"""Escolha do próximo processo na fila de prontos.

FCFS e RR retiram a cabeça da fila. SJF escolhe o menor pedaço que ainda falta
do burst de CPU atual; empate fica com quem entrou antes na fila. A classe do
processo não entra na decisão.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from simulador.modelos import Processo


class EscalonadorDaFilaDeProntos(Protocol):
    def escolher_proximo_processo(self, fila_de_prontos: Sequence[Processo]) -> Processo | None: ...


class FCFS:
    def escolher_proximo_processo(self, fila_de_prontos: Sequence[Processo]) -> Processo | None:
        if not fila_de_prontos:
            return None
        return fila_de_prontos[0]


class SJF:
    def escolher_proximo_processo(self, fila_de_prontos: Sequence[Processo]) -> Processo | None:
        if not fila_de_prontos:
            return None
        return min(
            fila_de_prontos,
            key=lambda processo: (
                processo.unidades_de_cpu_restantes_no_burst(),
                processo.ordem_de_entrada_na_fila_de_prontos,
            ),
        )


class RR:
    def escolher_proximo_processo(self, fila_de_prontos: Sequence[Processo]) -> Processo | None:
        if not fila_de_prontos:
            return None
        return fila_de_prontos[0]


def criar_escalonador_da_fila_de_prontos(nome: str) -> EscalonadorDaFilaDeProntos:
    if nome == "fcfs":
        return FCFS()
    if nome == "sjf":
        return SJF()
    if nome == "rr":
        return RR()
    raise ValueError(f"escalonador desconhecido: {nome}")
