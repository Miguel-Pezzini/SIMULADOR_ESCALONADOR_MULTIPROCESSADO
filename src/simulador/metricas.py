"""Métricas de uma execução. Speedup exige a rodada irmã de 1 CPU."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from simulador.modelos import Parametros


@dataclass(slots=True)
class CpuMetrica:
    indice: int
    tempo_util: int
    tempo_troca: int
    tempo_ocioso: int
    trocas: int
    gantt: list[tuple[int, int, str]]

    def utilizacao(self, makespan: int) -> float:
        if makespan == 0:
            return 0.0
        return (self.tempo_util + self.tempo_troca) / makespan


@dataclass(slots=True)
class ProcessoMetrica:
    pid: int
    classe: str
    chegada: int
    termino: int
    espera: int
    resposta: int
    turnaround: int


@dataclass
class Resultado:
    parametros: Parametros
    processos: list[ProcessoMetrica]
    cpus: list[CpuMetrica]
    page_faults: int
    acertos: int
    makespan: int
    log: list[str]
    speedup: float | None = None
    eficiencia: float | None = None

    def espera_media(self) -> float:
        return _media([p.espera for p in self.processos])

    def espera_max(self) -> int:
        if not self.processos:
            return 0
        return max(p.espera for p in self.processos)

    def espera_max_pid(self) -> int | None:
        if not self.processos:
            return None
        return max(self.processos, key=lambda p: (p.espera, p.pid)).pid

    def turnaround_medio(self) -> float:
        return _media([p.turnaround for p in self.processos])

    def resposta_media(self) -> float:
        return _media([p.resposta for p in self.processos])

    def trocas_total(self) -> int:
        return sum(cpu.trocas for cpu in self.cpus)

    def taxa_faults(self) -> float:
        if self.parametros.ignorar_memoria:
            return 0.0
        total = self.page_faults + self.acertos
        if total == 0:
            return 0.0
        return self.page_faults / total

    def da_classe(self, classe: str) -> list[ProcessoMetrica]:
        return [p for p in self.processos if p.classe == classe]

    def media_classe(self, classe: str, campo: str) -> float | None:
        grupo = self.da_classe(classe)
        if not grupo:
            return None
        return _media([int(getattr(p, campo)) for p in grupo])


def aplicar_referencia(resultado: Resultado, caminho: Path) -> None:
    try:
        bruto = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"referência de 1 CPU não encontrada: {caminho}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"referência de 1 CPU inválida: {caminho}") from exc
    makespan = bruto.get("makespan") if isinstance(bruto, dict) else None
    if not isinstance(makespan, int):
        raise ValueError("referência de 1 CPU sem makespan inteiro")
    base = makespan
    if resultado.makespan == 0:
        raise ValueError("makespan zero impede o cálculo de speedup")
    resultado.speedup = base / resultado.makespan
    resultado.eficiencia = resultado.speedup / 4


def _media(valores: list[int]) -> float:
    if not valores:
        return 0.0
    return sum(valores) / len(valores)
