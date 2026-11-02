"""Memória física paginada, compartilhada, com substituição global FIFO ou LRU.

Uma página é o par (pid, número). A página carregada por um page fault fica
protegida até o processo repetir a referência e acertar. Quadros em uso por
uma CPU neste instante também não são vítimas: a referência já foi concedida.
"""

from __future__ import annotations

from collections import OrderedDict, deque
from enum import Enum


class Acesso(Enum):
    ACERTO = "acerto"
    CARREGADA = "carregada"
    SEM_VITIMA = "sem_vitima"


class Memoria:
    def __init__(self, quadros: int, subst: str) -> None:
        if quadros < 1:
            raise ValueError("quadros deve ser pelo menos 1")
        if subst not in ("fifo", "lru"):
            raise ValueError("substituição deve ser fifo ou lru")
        self.quadros = quadros
        self.subst = subst
        self._conteudo: list[tuple[int, int] | None] = [None] * quadros
        self._quadro_de: dict[tuple[int, int], int] = {}
        self._protegidas: set[tuple[int, int]] = set()
        self._em_uso: set[tuple[int, int]] = set()
        self._fifo: deque[tuple[int, int]] = deque()
        self._lru: OrderedDict[tuple[int, int], None] = OrderedDict()
        self.acertos = 0

    def ocupados(self) -> int:
        return len(self._quadro_de)

    def residente(self, pid: int, pagina: int) -> bool:
        return (pid, pagina) in self._quadro_de

    def soltar_em_uso(self) -> None:
        self._em_uso.clear()

    def acessar(self, pid: int, pagina: int) -> Acesso:
        chave = (pid, pagina)
        if chave in self._quadro_de:
            self._protegidas.discard(chave)
            self._tocar(chave)
            self._em_uso.add(chave)
            self.acertos += 1
            return Acesso.ACERTO
        if not self._alocar(chave):
            return Acesso.SEM_VITIMA
        return Acesso.CARREGADA

    def liberar_processo(self, pid: int) -> None:
        for chave in [chave for chave in self._quadro_de if chave[0] == pid]:
            self._remover(chave)

    def _alocar(self, chave: tuple[int, int]) -> bool:
        indice = self._quadro_livre()
        if indice is None:
            vitima = self._escolher_vitima()
            if vitima is None:
                return False
            self._remover(vitima)
            indice = self._quadro_livre()
            if indice is None:
                raise RuntimeError("quadro liberado não ficou disponível")
        self._conteudo[indice] = chave
        self._quadro_de[chave] = indice
        self._protegidas.add(chave)
        if self.subst == "fifo":
            self._fifo.append(chave)
        else:
            self._lru[chave] = None
        return True

    def _escolher_vitima(self) -> tuple[int, int] | None:
        ordem = list(self._fifo) if self.subst == "fifo" else list(self._lru)
        for chave in ordem:
            if chave in self._protegidas or chave in self._em_uso:
                continue
            return chave
        return None

    def _quadro_livre(self) -> int | None:
        for indice, conteudo in enumerate(self._conteudo):
            if conteudo is None:
                return indice
        return None

    def _tocar(self, chave: tuple[int, int]) -> None:
        if self.subst == "lru":
            self._lru.move_to_end(chave)

    def _remover(self, chave: tuple[int, int]) -> None:
        indice = self._quadro_de.pop(chave)
        self._conteudo[indice] = None
        self._protegidas.discard(chave)
        self._em_uso.discard(chave)
        if self.subst == "fifo":
            self._fifo.remove(chave)
        else:
            del self._lru[chave]
