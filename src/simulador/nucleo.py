"""Laço de tempo discreto.

Em cada instante t, nesta ordem:
1. chegadas e retornos de E/S e de page fault entram no fim da fila, em ordem de pid;
2. quem estourou o quantum vai para o fim da fila (se a fila estava vazia, segue sem troca);
3. as CPUs livres despacham da menor para a maior. Com custo de troca 0, a
   referência é tentada na hora: um fault libera a CPU e o próximo processo
   ainda é despachado em t.

O quantum conta só tempo útil. A troca de contexto não consome quantum.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

from simulador.carga import carregar
from simulador.memoria import Acesso, Memoria
from simulador.metricas import (
    CpuMetrica,
    ProcessoMetrica,
    Resultado,
    aplicar_referencia,
)
from simulador.modelos import (
    BurstES,
    Cpu,
    Estado,
    ModoCpu,
    Parametros,
    Processo,
)
from simulador.politicas import Politica, criar_politica


class Simulador:
    def __init__(self, parametros: Parametros, processos: list[Processo]) -> None:
        self.parametros = parametros
        self.processos = processos
        self.por_pid = {proc.pid: proc for proc in processos}
        self.ordem = sorted(processos, key=lambda proc: (proc.chegada, proc.pid))
        self.prox_chegada = 0
        self.fila: deque[Processo] = deque()
        self.bloqueados: dict[int, int] = {}
        self.cpus = [Cpu(indice=i) for i in range(parametros.cpus)]
        self.politica: Politica = criar_politica(parametros.sched)
        self.memoria = Memoria(parametros.quadros, parametros.subst)
        self.n_faults = 0
        self.seq = 0
        self.log: list[str] = []
        self._limite = self._calcular_limite()

    def executar(self) -> Resultado:
        t = 0
        while True:
            if t > self._limite:
                raise RuntimeError(f"simulação excedeu o limite de tempo ({self._limite})")
            self._processar_instante(t)
            if all(proc.estado is Estado.TERMINADO for proc in self.processos):
                return self._resultado(t)
            if self._tudo_ocioso():
                proximo = self._proximo_evento(t)
                if proximo is None:
                    raise RuntimeError("simulação parada com processos ativos e sem eventos")
                for cpu in self.cpus:
                    cpu.tempo_ocioso += proximo - t
                    cpu.marcar(t, proximo, "OCIOSA")
                t = proximo
                continue
            self._avancar(t)
            t += 1

    def _processar_instante(self, t: int) -> None:
        if not self.parametros.ignorar_memoria:
            self.memoria.soltar_em_uso()
        for entrada in self._coletar_entradas(t):
            self._enfileirar(entrada[0], t)
            self._registrar(t, entrada[1], entrada[0].pid)
        for cpu in self.cpus:
            if cpu.modo is ModoCpu.TROCA and cpu.troca_restante == 0:
                self._tentar_referencia(cpu, t)
            elif cpu.modo is ModoCpu.EXEC and cpu.concluiu_unidade:
                cpu.concluiu_unidade = False
                self._apos_unidade(cpu, t)
        self._despachar(t)
        if self.fila and all(cpu.modo is ModoCpu.LIVRE for cpu in self.cpus):
            raise RuntimeError("fila de prontos não vazia com todas as CPUs livres")

    def _coletar_entradas(self, t: int) -> list[tuple[Processo, str]]:
        entrantes: list[tuple[Processo, str]] = []
        while self.prox_chegada < len(self.ordem):
            proc = self.ordem[self.prox_chegada]
            if proc.chegada > t:
                break
            if proc.chegada < t:
                raise RuntimeError(f"chegada do processo {proc.pid} foi pulada")
            self.prox_chegada += 1
            entrantes.append((proc, "CHEGADA"))
        retornos = [pid for pid, quando in self.bloqueados.items() if quando == t]
        for pid in retornos:
            del self.bloqueados[pid]
            proc = self.por_pid[pid]
            evento = "RETORNO_FALTA" if proc.motivo_bloqueio == "falta" else "RETORNO_ES"
            entrantes.append((proc, evento))
        entrantes.sort(key=lambda item: item[0].pid)
        return entrantes

    def _enfileirar(self, proc: Processo, t: int) -> None:
        self.seq += 1
        proc.estado = Estado.PRONTO
        proc.pronto_desde = t
        proc.entrada_seq = self.seq
        proc.retorno = None
        self.fila.append(proc)

    def _apos_unidade(self, cpu: Cpu, t: int) -> None:
        proc = cpu.processo
        if proc is None:
            raise RuntimeError("CPU em execução sem processo")
        burst = proc.burst_cpu_atual()
        if proc.unidades_feitas == burst.cpu:
            self._fim_de_burst_cpu(cpu, proc, t)
            return
        if self.parametros.quantum is not None and cpu.quantum_restante == 0:
            if not self.fila:
                cpu.quantum_restante = self.parametros.quantum
                self._registrar(t, "RENOVACAO_QUANTUM", proc.pid)
                self._tentar_referencia(cpu, t)
                return
            cpu.modo = ModoCpu.LIVRE
            cpu.processo = None
            self._enfileirar(proc, t)
            self._registrar(t, "PREEMPCAO", proc.pid)
            return
        self._tentar_referencia(cpu, t)

    def _fim_de_burst_cpu(self, cpu: Cpu, proc: Processo, t: int) -> None:
        proc.indice_burst += 1
        proc.unidades_feitas = 0
        cpu.modo = ModoCpu.LIVRE
        cpu.processo = None
        if proc.indice_burst >= len(proc.bursts):
            proc.estado = Estado.TERMINADO
            proc.termino = t
            proc.motivo_bloqueio = None
            if not self.parametros.ignorar_memoria:
                self.memoria.liberar_processo(proc.pid)
            self._registrar(t, "TERMINO", proc.pid)
            return
        burst = proc.bursts[proc.indice_burst]
        if not isinstance(burst, BurstES):
            raise RuntimeError(f"processo {proc.pid} deveria entrar em E/S")
        proc.indice_burst += 1
        self._bloquear(proc, t, "es", burst.es)
        self._registrar(t, "INICIO_ES", proc.pid)

    def _despachar(self, t: int) -> None:
        while True:
            despachou = False
            for cpu in self.cpus:
                if cpu.modo is not ModoCpu.LIVRE:
                    continue
                if not self.fila:
                    break
                proc = self.politica.escolher(self.fila)
                if proc is None:
                    break
                self.fila.remove(proc)
                self._ocupar(cpu, proc, t)
                despachou = True
            if not despachou:
                break

    def _ocupar(self, cpu: Cpu, proc: Processo, t: int) -> None:
        if proc.primeiro_despacho is None:
            proc.primeiro_despacho = t
        if proc.pronto_desde is not None:
            proc.espera += t - proc.pronto_desde
            proc.pronto_desde = None
        proc.estado = Estado.EXECUTANDO
        anterior = cpu.ultimo_pid
        cpu.processo = proc
        cpu.ultimo_pid = proc.pid
        cpu.concluiu_unidade = False
        if self.parametros.quantum is not None:
            cpu.quantum_restante = self.parametros.quantum
        self._registrar(t, "DESPACHO", proc.pid)
        if anterior != proc.pid and self.parametros.custo_troca > 0:
            cpu.modo = ModoCpu.TROCA
            cpu.troca_restante = self.parametros.custo_troca
            cpu.trocas += 1
            return
        self._tentar_referencia(cpu, t)

    def _tentar_referencia(self, cpu: Cpu, t: int) -> None:
        proc = cpu.processo
        if proc is None:
            raise RuntimeError("referência sem processo na CPU")
        if self.parametros.ignorar_memoria:
            cpu.modo = ModoCpu.EXEC
            return
        acesso = self.memoria.acessar(proc.pid, proc.ref_atual())
        if acesso is Acesso.ACERTO:
            proc.falta_ja_contada = False
            cpu.modo = ModoCpu.EXEC
            return
        if acesso is Acesso.CARREGADA:
            if not proc.falta_ja_contada:
                self.n_faults += 1
            proc.falta_ja_contada = False
            evento = "PAGE_FAULT"
        else:
            if not proc.falta_ja_contada:
                self.n_faults += 1
                proc.falta_ja_contada = True
            evento = "SEM_VITIMA"
        cpu.modo = ModoCpu.LIVRE
        cpu.processo = None
        self._bloquear(proc, t, "falta", self.parametros.tempo_fault)
        self._registrar(t, evento, proc.pid)

    def _bloquear(self, proc: Processo, t: int, motivo: str, duracao: int) -> None:
        proc.estado = Estado.BLOQUEADO
        proc.motivo_bloqueio = motivo
        proc.retorno = t + duracao
        proc.pronto_desde = None
        self.bloqueados[proc.pid] = proc.retorno

    def _avancar(self, t: int) -> None:
        for cpu in self.cpus:
            if cpu.modo is ModoCpu.TROCA:
                cpu.tempo_troca += 1
                cpu.troca_restante -= 1
                cpu.marcar(t, t + 1, "TROCA")
            elif cpu.modo is ModoCpu.EXEC:
                proc = cpu.processo
                if proc is None:
                    raise RuntimeError("CPU executando sem processo")
                cpu.tempo_util += 1
                proc.unidades_feitas += 1
                if self.parametros.quantum is not None:
                    cpu.quantum_restante -= 1
                cpu.concluiu_unidade = True
                cpu.marcar(t, t + 1, f"P{proc.pid}")
            else:
                cpu.tempo_ocioso += 1
                cpu.marcar(t, t + 1, "OCIOSA")

    def _tudo_ocioso(self) -> bool:
        return not self.fila and all(cpu.modo is ModoCpu.LIVRE for cpu in self.cpus)

    def _proximo_evento(self, t: int) -> int | None:
        candidatos: list[int] = []
        if self.prox_chegada < len(self.ordem):
            candidatos.append(self.ordem[self.prox_chegada].chegada)
        if self.bloqueados:
            candidatos.append(min(self.bloqueados.values()))
        futuros = [quando for quando in candidatos if quando > t]
        if not futuros:
            return None
        return min(futuros)

    def _registrar(self, t: int, evento: str, pid: int | None) -> None:
        if not self.parametros.log:
            return
        fila = ",".join(str(proc.pid) for proc in self.fila) or "-"
        bloqueados = ",".join(
            f"{pid_b}:{quando}" for pid_b, quando in sorted(self.bloqueados.items())
        )
        if not bloqueados:
            bloqueados = "-"
        cpus = ",".join(
            f"{cpu.indice}:{'-' if cpu.processo is None else cpu.processo.pid}" for cpu in self.cpus
        )
        pid_txt = "-" if pid is None else str(pid)
        quadros = 0 if self.parametros.ignorar_memoria else self.memoria.ocupados()
        self.log.append(
            f"t={t} evento={evento} pid={pid_txt} fila=[{fila}] "
            f"bloqueados=[{bloqueados}] cpus=[{cpus}] quadros={quadros}"
        )

    def _resultado(self, makespan: int) -> Resultado:
        processos: list[ProcessoMetrica] = []
        for proc in self.processos:
            if proc.termino is None or proc.primeiro_despacho is None:
                raise RuntimeError(f"processo {proc.pid} terminou sem despacho")
            processos.append(
                ProcessoMetrica(
                    pid=proc.pid,
                    classe=proc.classe,
                    chegada=proc.chegada,
                    termino=proc.termino,
                    espera=proc.espera,
                    resposta=proc.primeiro_despacho - proc.chegada,
                    turnaround=proc.termino - proc.chegada,
                )
            )
        if self.parametros.ignorar_memoria:
            acertos = sum(cpu.tempo_util for cpu in self.cpus)
            faults = 0
        else:
            acertos = self.memoria.acertos
            faults = self.n_faults
        return Resultado(
            parametros=self.parametros,
            processos=processos,
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
            page_faults=faults,
            acertos=acertos,
            makespan=makespan,
            log=list(self.log),
        )

    def _calcular_limite(self) -> int:
        cpu = 0
        es = 0
        for proc in self.processos:
            for burst in proc.bursts:
                if isinstance(burst, BurstES):
                    es += burst.es
                else:
                    cpu += burst.cpu
        chegada = max((proc.chegada for proc in self.processos), default=0)
        return chegada + (cpu + es + cpu * self.parametros.tempo_fault) * 5 + 10


def simular(parametros: Parametros) -> Resultado:
    processos = carregar(Path(parametros.arquivo))
    resultado = Simulador(parametros, processos).executar()
    if parametros.referencia_1cpu is not None:
        aplicar_referencia(resultado, Path(parametros.referencia_1cpu))
    return resultado
