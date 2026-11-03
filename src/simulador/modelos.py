"""Tipos do simulador.

O campo ``classe`` existe só para a análise. Nenhum escalonador lê esse rótulo
para escolher quem executa.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Estado(Enum):
    NOVO = "novo"
    PRONTO = "pronto"
    EXECUTANDO = "executando"
    BLOQUEADO = "bloqueado"
    TERMINADO = "terminado"


class ModoCpu(Enum):
    LIVRE = "livre"
    TROCA = "troca"
    EXECUTANDO = "executando"


@dataclass(frozen=True, slots=True)
class BurstCPU:
    duracao_de_cpu: int
    paginas_referenciadas_no_burst: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class BurstES:
    duracao_de_entrada_saida: int


Burst = BurstCPU | BurstES


@dataclass(eq=False, slots=True)
class Processo:
    pid: int
    chegada: int
    classe: str
    paginas: int
    bursts: tuple[Burst, ...]
    indice_do_burst_atual: int = 0
    unidades_de_cpu_ja_executadas: int = 0
    estado: Estado = Estado.NOVO
    espera: int = 0
    instante_em_que_entrou_na_fila_de_prontos: int | None = None
    ordem_de_entrada_na_fila_de_prontos: int = 0
    instante_do_primeiro_despacho: int | None = None
    instante_de_termino: int | None = None
    instante_de_retorno_do_bloqueio: int | None = None
    motivo_bloqueio: str | None = None
    falta_de_pagina_ja_contabilizada: bool = False

    def burst_cpu_atual(self) -> BurstCPU:
        burst = self.bursts[self.indice_do_burst_atual]
        if not isinstance(burst, BurstCPU):
            raise RuntimeError(f"processo {self.pid} não está em burst de CPU")
        return burst

    def unidades_de_cpu_restantes_no_burst(self) -> int:
        burst_de_cpu = self.burst_cpu_atual()
        return burst_de_cpu.duracao_de_cpu - self.unidades_de_cpu_ja_executadas

    def pagina_referenciada_na_unidade_atual(self) -> int:
        burst_de_cpu = self.burst_cpu_atual()
        return burst_de_cpu.paginas_referenciadas_no_burst[self.unidades_de_cpu_ja_executadas]


@dataclass(eq=False)
class Cpu:
    indice: int
    modo: ModoCpu = ModoCpu.LIVRE
    processo: Processo | None = None
    unidades_restantes_da_troca_de_contexto: int = 0
    unidades_restantes_do_quantum: int = 0
    pid_do_ultimo_processo_nesta_cpu: int | None = None
    executou_unidade_de_cpu: bool = False
    tempo_util: int = 0
    tempo_troca: int = 0
    tempo_ocioso: int = 0
    trocas: int = 0
    gantt: list[tuple[int, int, str]] = field(default_factory=list)

    def marcar(self, inicio: int, fim: int, evento: str) -> None:
        if inicio >= fim:
            return
        if self.gantt and self.gantt[-1][2] == evento and self.gantt[-1][1] == inicio:
            inicio_anterior, _, rotulo = self.gantt[-1]
            self.gantt[-1] = (inicio_anterior, fim, rotulo)
            return
        self.gantt.append((inicio, fim, evento))


@dataclass(frozen=True, slots=True)
class Parametros:
    arquivo: str
    cpus: int
    algoritmo_de_escalonamento: str
    quantum: int | None
    algoritmo_de_substituicao_de_pagina: str
    quadros: int
    custo_troca: int = 1
    tempo_fault: int = 20
    ignorar_memoria: bool = False
    log: bool = False
    arquivo_de_metricas_com_1_cpu: str | None = None
    saida: str | None = None

    def __post_init__(self) -> None:
        if self.cpus not in (1, 4):
            raise ValueError("--cpus aceita apenas 1 ou 4")
        if self.algoritmo_de_escalonamento not in ("fcfs", "sjf", "rr"):
            raise ValueError("--sched aceita fcfs, sjf ou rr")
        if self.algoritmo_de_substituicao_de_pagina not in ("fifo", "lru"):
            raise ValueError("--subst aceita fifo ou lru")
        if self.quadros < 1:
            raise ValueError("--quadros deve ser pelo menos 1")
        if self.custo_troca < 0:
            raise ValueError("--custo-troca não pode ser negativo")
        if self.tempo_fault < 1:
            raise ValueError("--tempo-fault deve ser pelo menos 1")
        if self.algoritmo_de_escalonamento == "rr":
            if self.quantum is None or self.quantum < 1:
                raise ValueError("--quantum é obrigatório no RR e deve ser pelo menos 1")
        elif self.quantum is not None:
            raise ValueError("--quantum só é usado com --sched rr")
