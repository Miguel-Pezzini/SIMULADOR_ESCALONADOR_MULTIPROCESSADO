"""Laço de tempo discreto.

Em cada instante, nesta ordem:
1. chegadas e retornos de E/S e de page fault entram no fim da fila, em ordem de pid;
2. quem estourou o quantum vai para o fim da fila (se a fila estava vazia, segue sem troca);
3. as CPUs livres despacham da menor para a maior. Com custo de troca 0, a
   referência é tentada na hora: um fault libera a CPU e o próximo processo
   ainda é despachado nesse instante.

O quantum conta só tempo útil. A troca de contexto não consome quantum.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

from simulador.carga import carregar_processos
from simulador.escalonadores import (
    EscalonadorDaFilaDeProntos,
    criar_escalonador_da_fila_de_prontos,
)
from simulador.memoria import Acesso, Memoria
from simulador.metricas import (
    CpuMetrica,
    ProcessoMetrica,
    Resultado,
    calcular_speedup_e_eficiencia,
)
from simulador.modelos import (
    BurstES,
    Cpu,
    Estado,
    ModoCpu,
    Parametros,
    Processo,
)


class Simulador:
    def __init__(self, parametros: Parametros, processos: list[Processo]) -> None:
        self.parametros = parametros
        self.processos = processos
        self.processo_por_pid = {processo.pid: processo for processo in processos}
        self.processos_ordenados_por_chegada = sorted(
            processos, key=lambda processo: (processo.chegada, processo.pid)
        )
        self.indice_da_proxima_chegada_de_processo = 0
        self.fila_de_prontos: deque[Processo] = deque()
        self.instante_de_retorno_por_pid_bloqueado: dict[int, int] = {}
        self.cpus = [Cpu(indice=i) for i in range(parametros.cpus)]
        self.escalonador_da_fila_de_prontos: EscalonadorDaFilaDeProntos = (
            criar_escalonador_da_fila_de_prontos(parametros.algoritmo_de_escalonamento)
        )
        self.memoria = Memoria(
            parametros.quadros,
            parametros.algoritmo_de_substituicao_de_pagina,
        )
        self.quantidade_de_faltas_de_pagina = 0
        self.contador_de_entradas_na_fila_de_prontos = 0
        self.log: list[str] = []
        self.instante_limite_de_seguranca = self._calcular_instante_limite_de_seguranca()

    def executar(self) -> Resultado:
        instante = 0
        while True:
            if instante > self.instante_limite_de_seguranca:
                raise RuntimeError(
                    "simulação excedeu o instante limite de segurança "
                    f"({self.instante_limite_de_seguranca})"
                )
            self._processar_instante(instante)
            if all(processo.estado is Estado.TERMINADO for processo in self.processos):
                return self._montar_resultado(instante)
            if self._fila_de_prontos_vazia_e_cpus_livres():
                proximo = self._instante_do_proximo_evento(instante)
                if proximo is None:
                    raise RuntimeError("simulação parada com processos ativos e sem eventos")
                for cpu in self.cpus:
                    cpu.tempo_ocioso += proximo - instante
                    cpu.marcar(instante, proximo, "OCIOSA")
                instante = proximo
                continue
            self._avancar_um_instante(instante)
            instante += 1

    def _processar_instante(self, instante: int) -> None:
        if not self.parametros.ignorar_memoria:
            self.memoria.liberar_paginas_em_uso_por_uma_cpu()
        for entrada in self._processos_que_entram_na_fila_de_prontos(instante):
            self._colocar_processo_na_fila_de_prontos(entrada[0], instante)
            self._registrar_evento_no_log(instante, entrada[1], entrada[0].pid)
        for cpu in self.cpus:
            if cpu.modo is ModoCpu.TROCA and cpu.unidades_restantes_da_troca_de_contexto == 0:
                self._consultar_pagina_na_memoria(cpu, instante)
            elif cpu.modo is ModoCpu.EXECUTANDO and cpu.executou_unidade_de_cpu:
                cpu.executou_unidade_de_cpu = False
                self._reagir_ao_fim_da_unidade_de_cpu(cpu, instante)
        self._despachar_processos_nas_cpus_livres(instante)
        if self.fila_de_prontos and all(cpu.modo is ModoCpu.LIVRE for cpu in self.cpus):
            raise RuntimeError("fila de prontos não vazia com todas as CPUs livres")

    def _processos_que_entram_na_fila_de_prontos(self, instante: int) -> list[tuple[Processo, str]]:
        processos_que_entram: list[tuple[Processo, str]] = []
        ordenados = self.processos_ordenados_por_chegada
        while self.indice_da_proxima_chegada_de_processo < len(ordenados):
            processo = ordenados[self.indice_da_proxima_chegada_de_processo]
            if processo.chegada > instante:
                break
            if processo.chegada < instante:
                raise RuntimeError(f"chegada do processo {processo.pid} foi pulada")
            self.indice_da_proxima_chegada_de_processo += 1
            processos_que_entram.append((processo, "CHEGADA"))
        pids_que_retornam = [
            pid
            for pid, quando in self.instante_de_retorno_por_pid_bloqueado.items()
            if quando == instante
        ]
        for pid in pids_que_retornam:
            del self.instante_de_retorno_por_pid_bloqueado[pid]
            processo = self.processo_por_pid[pid]
            if processo.motivo_bloqueio == "falta_de_pagina":
                evento = "RETORNO_FALTA"
            else:
                evento = "RETORNO_ES"
            processos_que_entram.append((processo, evento))
        processos_que_entram.sort(key=lambda item: item[0].pid)
        return processos_que_entram

    def _colocar_processo_na_fila_de_prontos(self, processo: Processo, instante: int) -> None:
        self.contador_de_entradas_na_fila_de_prontos += 1
        processo.estado = Estado.PRONTO
        processo.instante_em_que_entrou_na_fila_de_prontos = instante
        processo.ordem_de_entrada_na_fila_de_prontos = self.contador_de_entradas_na_fila_de_prontos
        processo.instante_de_retorno_do_bloqueio = None
        self.fila_de_prontos.append(processo)

    def _reagir_ao_fim_da_unidade_de_cpu(self, cpu: Cpu, instante: int) -> None:
        processo = cpu.processo
        if processo is None:
            raise RuntimeError("CPU em execução sem processo")
        burst_de_cpu = processo.burst_cpu_atual()
        if processo.unidades_de_cpu_ja_executadas == burst_de_cpu.duracao_de_cpu:
            self._fim_de_burst_cpu(cpu, processo, instante)
            return
        if self.parametros.quantum is not None and cpu.unidades_restantes_do_quantum == 0:
            if not self.fila_de_prontos:
                cpu.unidades_restantes_do_quantum = self.parametros.quantum
                self._registrar_evento_no_log(instante, "RENOVACAO_QUANTUM", processo.pid)
                self._consultar_pagina_na_memoria(cpu, instante)
                return
            cpu.modo = ModoCpu.LIVRE
            cpu.processo = None
            self._colocar_processo_na_fila_de_prontos(processo, instante)
            self._registrar_evento_no_log(instante, "PREEMPCAO", processo.pid)
            return
        self._consultar_pagina_na_memoria(cpu, instante)

    def _fim_de_burst_cpu(self, cpu: Cpu, processo: Processo, instante: int) -> None:
        processo.indice_do_burst_atual += 1
        processo.unidades_de_cpu_ja_executadas = 0
        cpu.modo = ModoCpu.LIVRE
        cpu.processo = None
        if processo.indice_do_burst_atual >= len(processo.bursts):
            processo.estado = Estado.TERMINADO
            processo.instante_de_termino = instante
            processo.motivo_bloqueio = None
            if not self.parametros.ignorar_memoria:
                self.memoria.liberar_quadros_do_processo(processo.pid)
            self._registrar_evento_no_log(instante, "TERMINO", processo.pid)
            return
        burst = processo.bursts[processo.indice_do_burst_atual]
        if not isinstance(burst, BurstES):
            raise RuntimeError(f"processo {processo.pid} deveria entrar em E/S")
        processo.indice_do_burst_atual += 1
        self._bloquear_processo(processo, instante, "entrada_saida", burst.duracao_de_entrada_saida)
        self._registrar_evento_no_log(instante, "INICIO_ES", processo.pid)

    def _despachar_processos_nas_cpus_livres(self, instante: int) -> None:
        while True:
            despachou_algum_processo = False
            for cpu in self.cpus:
                if cpu.modo is not ModoCpu.LIVRE:
                    continue
                if not self.fila_de_prontos:
                    break
                processo = self.escalonador_da_fila_de_prontos.escolher_proximo_processo(
                    self.fila_de_prontos
                )
                if processo is None:
                    break
                self.fila_de_prontos.remove(processo)
                self._colocar_processo_em_execucao(cpu, processo, instante)
                despachou_algum_processo = True
            if not despachou_algum_processo:
                break

    def _colocar_processo_em_execucao(self, cpu: Cpu, processo: Processo, instante: int) -> None:
        if processo.instante_do_primeiro_despacho is None:
            processo.instante_do_primeiro_despacho = instante
        if processo.instante_em_que_entrou_na_fila_de_prontos is not None:
            processo.espera += instante - processo.instante_em_que_entrou_na_fila_de_prontos
            processo.instante_em_que_entrou_na_fila_de_prontos = None
        processo.estado = Estado.EXECUTANDO
        pid_do_processo_anterior = cpu.pid_do_ultimo_processo_nesta_cpu
        cpu.processo = processo
        cpu.pid_do_ultimo_processo_nesta_cpu = processo.pid
        cpu.executou_unidade_de_cpu = False
        if self.parametros.quantum is not None:
            cpu.unidades_restantes_do_quantum = self.parametros.quantum
        self._registrar_evento_no_log(instante, "DESPACHO", processo.pid)
        if pid_do_processo_anterior != processo.pid and self.parametros.custo_troca > 0:
            cpu.modo = ModoCpu.TROCA
            cpu.unidades_restantes_da_troca_de_contexto = self.parametros.custo_troca
            cpu.trocas += 1
            return
        self._consultar_pagina_na_memoria(cpu, instante)

    def _consultar_pagina_na_memoria(self, cpu: Cpu, instante: int) -> None:
        processo = cpu.processo
        if processo is None:
            raise RuntimeError("referência sem processo na CPU")
        if self.parametros.ignorar_memoria:
            cpu.modo = ModoCpu.EXECUTANDO
            return
        resultado_do_acesso = self.memoria.acessar_pagina(
            processo.pid,
            processo.pagina_referenciada_na_unidade_atual(),
        )
        if resultado_do_acesso is Acesso.ACERTO:
            processo.falta_de_pagina_ja_contabilizada = False
            cpu.modo = ModoCpu.EXECUTANDO
            return
        if resultado_do_acesso is Acesso.PAGINA_CARREGADA:
            if not processo.falta_de_pagina_ja_contabilizada:
                self.quantidade_de_faltas_de_pagina += 1
            processo.falta_de_pagina_ja_contabilizada = False
            evento = "PAGE_FAULT"
        else:
            if not processo.falta_de_pagina_ja_contabilizada:
                self.quantidade_de_faltas_de_pagina += 1
                processo.falta_de_pagina_ja_contabilizada = True
            evento = "SEM_VITIMA"
        cpu.modo = ModoCpu.LIVRE
        cpu.processo = None
        self._bloquear_processo(
            processo,
            instante,
            "falta_de_pagina",
            self.parametros.tempo_fault,
        )
        self._registrar_evento_no_log(instante, evento, processo.pid)

    def _bloquear_processo(
        self,
        processo: Processo,
        instante: int,
        motivo: str,
        duracao: int,
    ) -> None:
        processo.estado = Estado.BLOQUEADO
        processo.motivo_bloqueio = motivo
        processo.instante_de_retorno_do_bloqueio = instante + duracao
        processo.instante_em_que_entrou_na_fila_de_prontos = None
        self.instante_de_retorno_por_pid_bloqueado[processo.pid] = (
            processo.instante_de_retorno_do_bloqueio
        )

    def _avancar_um_instante(self, instante: int) -> None:
        for cpu in self.cpus:
            if cpu.modo is ModoCpu.TROCA:
                cpu.tempo_troca += 1
                cpu.unidades_restantes_da_troca_de_contexto -= 1
                cpu.marcar(instante, instante + 1, "TROCA")
            elif cpu.modo is ModoCpu.EXECUTANDO:
                processo = cpu.processo
                if processo is None:
                    raise RuntimeError("CPU executando sem processo")
                cpu.tempo_util += 1
                processo.unidades_de_cpu_ja_executadas += 1
                if self.parametros.quantum is not None:
                    cpu.unidades_restantes_do_quantum -= 1
                cpu.executou_unidade_de_cpu = True
                cpu.marcar(instante, instante + 1, f"P{processo.pid}")
            else:
                cpu.tempo_ocioso += 1
                cpu.marcar(instante, instante + 1, "OCIOSA")

    def _fila_de_prontos_vazia_e_cpus_livres(self) -> bool:
        return not self.fila_de_prontos and all(cpu.modo is ModoCpu.LIVRE for cpu in self.cpus)

    def _instante_do_proximo_evento(self, instante: int) -> int | None:
        instantes_candidatos: list[int] = []
        ordenados = self.processos_ordenados_por_chegada
        if self.indice_da_proxima_chegada_de_processo < len(ordenados):
            indice = self.indice_da_proxima_chegada_de_processo
            instantes_candidatos.append(ordenados[indice].chegada)
        if self.instante_de_retorno_por_pid_bloqueado:
            instantes_candidatos.append(min(self.instante_de_retorno_por_pid_bloqueado.values()))
        instantes_futuros = [quando for quando in instantes_candidatos if quando > instante]
        if not instantes_futuros:
            return None
        return min(instantes_futuros)

    def _registrar_evento_no_log(self, instante: int, evento: str, pid: int | None) -> None:
        if not self.parametros.log:
            return
        pids_na_fila = ",".join(str(processo.pid) for processo in self.fila_de_prontos) or "-"
        texto_dos_bloqueados = ",".join(
            f"{pid_bloqueado}:{quando}"
            for pid_bloqueado, quando in sorted(self.instante_de_retorno_por_pid_bloqueado.items())
        )
        if not texto_dos_bloqueados:
            texto_dos_bloqueados = "-"
        texto_das_cpus = ",".join(
            f"{cpu.indice}:{'-' if cpu.processo is None else cpu.processo.pid}" for cpu in self.cpus
        )
        pid_txt = "-" if pid is None else str(pid)
        if self.parametros.ignorar_memoria:
            quadros_ocupados = 0
        else:
            quadros_ocupados = self.memoria.quantidade_de_quadros_ocupados()
        self.log.append(
            f"t={instante} evento={evento} pid={pid_txt} fila=[{pids_na_fila}] "
            f"bloqueados=[{texto_dos_bloqueados}] cpus=[{texto_das_cpus}] "
            f"quadros={quadros_ocupados}"
        )

    def _montar_resultado(self, instante_final: int) -> Resultado:
        metricas_dos_processos: list[ProcessoMetrica] = []
        for processo in self.processos:
            if (
                processo.instante_de_termino is None
                or processo.instante_do_primeiro_despacho is None
            ):
                raise RuntimeError(f"processo {processo.pid} terminou sem despacho")
            metricas_dos_processos.append(
                ProcessoMetrica(
                    pid=processo.pid,
                    classe=processo.classe,
                    chegada=processo.chegada,
                    termino=processo.instante_de_termino,
                    espera=processo.espera,
                    resposta=processo.instante_do_primeiro_despacho - processo.chegada,
                    turnaround=processo.instante_de_termino - processo.chegada,
                )
            )
        if self.parametros.ignorar_memoria:
            acertos = sum(cpu.tempo_util for cpu in self.cpus)
            faltas_de_pagina = 0
        else:
            acertos = self.memoria.acertos
            faltas_de_pagina = self.quantidade_de_faltas_de_pagina
        return Resultado(
            parametros=self.parametros,
            processos=metricas_dos_processos,
            cpus=[
                CpuMetrica(
                    indice=cpu.indice,
                    tempo_util=cpu.tempo_util,
                    tempo_troca=cpu.tempo_troca,
                    tempo_ocioso=cpu.tempo_ocioso,
                    trocas=cpu.trocas,
                    gantt=list(cpu.gantt),
                )
                for cpu in self.cpus
            ],
            page_faults=faltas_de_pagina,
            acertos=acertos,
            makespan=instante_final,
            log=list(self.log),
        )

    def _calcular_instante_limite_de_seguranca(self) -> int:
        soma_duracao_de_cpu = 0
        soma_duracao_de_entrada_saida = 0
        for processo in self.processos:
            for burst in processo.bursts:
                if isinstance(burst, BurstES):
                    soma_duracao_de_entrada_saida += burst.duracao_de_entrada_saida
                else:
                    soma_duracao_de_cpu += burst.duracao_de_cpu
        chegada_mais_tardia = max((processo.chegada for processo in self.processos), default=0)
        folga_de_faltas = soma_duracao_de_cpu * self.parametros.tempo_fault
        trabalho = soma_duracao_de_cpu + soma_duracao_de_entrada_saida + folga_de_faltas
        return chegada_mais_tardia + trabalho * 5 + 10


def simular(parametros: Parametros) -> Resultado:
    processos = carregar_processos(Path(parametros.arquivo))
    resultado = Simulador(parametros, processos).executar()
    if parametros.arquivo_de_metricas_com_1_cpu is not None:
        calcular_speedup_e_eficiencia(resultado, Path(parametros.arquivo_de_metricas_com_1_cpu))
    return resultado
