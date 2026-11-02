"""Tipos do simulador.

O campo ``classe`` existe só para a análise. Nenhum escalonador lê esse rótulo
para escolher quem executa.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class Estado(Enum):
    NOVO = "novo"
    PRONTO = "pronto"
    EXECUTANDO = "executando"
    BLOQUEADO = "bloqueado"
    TERMINADO = "terminado"


class ModoCpu(Enum):
    LIVRE = "livre"
    TROCA = "troca"
    EXEC = "exec"


Subst = Literal["fifo", "lru"]
Escalonador = Literal["fcfs", "sjf", "rr"]


@dataclass(frozen=True, slots=True)
class BurstCPU:
    cpu: int
    refs: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class BurstES:
    es: int


Burst = BurstCPU | BurstES


@dataclass(eq=False, slots=True)
class Processo:
    pid: int
    chegada: int
    classe: str
    paginas: int
    bursts: tuple[Burst, ...]
    indice_burst: int = 0
    unidades_feitas: int = 0
    estado: Estado = Estado.NOVO
    espera: int = 0
    pronto_desde: int | None = None
    entrada_seq: int = 0
    primeiro_despacho: int | None = None
    termino: int | None = None
    retorno: int | None = None
    motivo_bloqueio: str | None = None
    falta_ja_contada: bool = False

    def burst_cpu_atual(self) -> BurstCPU:
        burst = self.bursts[self.indice_burst]
        if not isinstance(burst, BurstCPU):
            raise RuntimeError(f"processo {self.pid} não está em burst de CPU")
        return burst

    def burst_restante(self) -> int:
        return self.burst_cpu_atual().cpu - self.unidades_feitas

    def ref_atual(self) -> int:
        return self.burst_cpu_atual().refs[self.unidades_feitas]


@dataclass(eq=False)
class Cpu:
    indice: int
    modo: ModoCpu = ModoCpu.LIVRE
    processo: Processo | None = None
    troca_restante: int = 0
    quantum_restante: int = 0
    ultimo_pid: int | None = None
    concluiu_unidade: bool = False
    tempo_util: int = 0
    tempo_troca: int = 0
    tempo_ocioso: int = 0
    trocas: int = 0
    gantt: list[tuple[int, int, str]] = field(default_factory=list)

    def marcar(self, inicio: int, fim: int, evento: str) -> None:
        if inicio >= fim:
            return
        if self.gantt and self.gantt[-1][2] == evento and self.gantt[-1][1] == inicio:
            ini, _, ev = self.gantt[-1]
            self.gantt[-1] = (ini, fim, ev)
            return
        self.gantt.append((inicio, fim, evento))


@dataclass(frozen=True, slots=True)
class Parametros:
    arquivo: str
    cpus: int
    sched: str
    quantum: int | None
    subst: str
    quadros: int
    custo_troca: int = 1
    tempo_fault: int = 20
    ignorar_memoria: bool = False
    log: bool = False
    referencia_1cpu: str | None = None
    saida: str | None = None

    def __post_init__(self) -> None:
        if self.cpus not in (1, 4):
            raise ValueError("--cpus aceita apenas 1 ou 4")
        if self.sched not in ("fcfs", "sjf", "rr"):
            raise ValueError("--sched aceita fcfs, sjf ou rr")
        if self.subst not in ("fifo", "lru"):
            raise ValueError("--subst aceita fifo ou lru")
        if self.quadros < 1:
            raise ValueError("--quadros deve ser pelo menos 1")
        if self.custo_troca < 0:
            raise ValueError("--custo-troca não pode ser negativo")
        if self.tempo_fault < 1:
            raise ValueError("--tempo-fault deve ser pelo menos 1")
        if self.sched == "rr":
            if self.quantum is None or self.quantum < 1:
                raise ValueError("--quantum é obrigatório no RR e deve ser pelo menos 1")
        elif self.quantum is not None:
            raise ValueError("--quantum só é usado com --sched rr")
