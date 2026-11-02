"""Políticas da fila de prontos.

FCFS e RR retiram a cabeça da fila. SJF escolhe o menor pedaço que ainda falta
do burst de CPU atual; empate fica com quem entrou antes na fila. A classe do
processo não entra na decisão.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from simulador.modelos import Processo


class Politica(Protocol):
    def escolher(self, fila: Sequence[Processo]) -> Processo | None: ...


class FCFS:
    def escolher(self, fila: Sequence[Processo]) -> Processo | None:
        if not fila:
            return None
        return fila[0]


class SJF:
    def escolher(self, fila: Sequence[Processo]) -> Processo | None:
        if not fila:
            return None
        return min(fila, key=lambda proc: (proc.burst_restante(), proc.entrada_seq))


class RR:
    def escolher(self, fila: Sequence[Processo]) -> Processo | None:
        if not fila:
            return None
        return fila[0]


def criar_politica(nome: str) -> Politica:
    if nome == "fcfs":
        return FCFS()
    if nome == "sjf":
        return SJF()
    if nome == "rr":
        return RR()
    raise ValueError(f"escalonador desconhecido: {nome}")
