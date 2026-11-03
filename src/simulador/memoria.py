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
    PAGINA_CARREGADA = "pagina_carregada"
    SEM_QUADRO_DISPONIVEL = "sem_quadro_disponivel"


class Memoria:
    def __init__(self, quadros: int, algoritmo_de_substituicao_de_pagina: str) -> None:
        if quadros < 1:
            raise ValueError("quadros deve ser pelo menos 1")
        if algoritmo_de_substituicao_de_pagina not in ("fifo", "lru"):
            raise ValueError("substituição deve ser fifo ou lru")
        self.quadros = quadros
        self.algoritmo_de_substituicao_de_pagina = algoritmo_de_substituicao_de_pagina
        self.pagina_de_cada_quadro: list[tuple[int, int] | None] = [None] * quadros
        self.quadro_da_pagina: dict[tuple[int, int], int] = {}
        self.paginas_protegidas_ate_o_acerto: set[tuple[int, int]] = set()
        self.paginas_em_uso_por_uma_cpu: set[tuple[int, int]] = set()
        self.ordem_de_carregamento_das_paginas: deque[tuple[int, int]] = deque()
        self.ordem_de_uso_das_paginas: OrderedDict[tuple[int, int], None] = OrderedDict()
        self.acertos = 0

    def quantidade_de_quadros_ocupados(self) -> int:
        return len(self.quadro_da_pagina)

    def pagina_esta_carregada(self, pid: int, pagina: int) -> bool:
        return (pid, pagina) in self.quadro_da_pagina

    def liberar_paginas_em_uso_por_uma_cpu(self) -> None:
        self.paginas_em_uso_por_uma_cpu.clear()

    def acessar_pagina(self, pid: int, pagina: int) -> Acesso:
        identidade_da_pagina = (pid, pagina)
        if identidade_da_pagina in self.quadro_da_pagina:
            self.paginas_protegidas_ate_o_acerto.discard(identidade_da_pagina)
            self._marcar_pagina_como_recentemente_usada(identidade_da_pagina)
            self.paginas_em_uso_por_uma_cpu.add(identidade_da_pagina)
            self.acertos += 1
            return Acesso.ACERTO
        if not self._alocar(identidade_da_pagina):
            return Acesso.SEM_QUADRO_DISPONIVEL
        return Acesso.PAGINA_CARREGADA

    def liberar_quadros_do_processo(self, pid: int) -> None:
        for identidade_da_pagina in [
            identidade for identidade in self.quadro_da_pagina if identidade[0] == pid
        ]:
            self._remover(identidade_da_pagina)

    def _alocar(self, identidade_da_pagina: tuple[int, int]) -> bool:
        indice = self._quadro_livre()
        if indice is None:
            vitima = self._escolher_vitima()
            if vitima is None:
                return False
            self._remover(vitima)
            indice = self._quadro_livre()
            if indice is None:
                raise RuntimeError("quadro liberado não ficou disponível")
        self.pagina_de_cada_quadro[indice] = identidade_da_pagina
        self.quadro_da_pagina[identidade_da_pagina] = indice
        self.paginas_protegidas_ate_o_acerto.add(identidade_da_pagina)
        if self.algoritmo_de_substituicao_de_pagina == "fifo":
            self.ordem_de_carregamento_das_paginas.append(identidade_da_pagina)
        else:
            self.ordem_de_uso_das_paginas[identidade_da_pagina] = None
        return True

    def _escolher_vitima(self) -> tuple[int, int] | None:
        if self.algoritmo_de_substituicao_de_pagina == "fifo":
            ordem = list(self.ordem_de_carregamento_das_paginas)
        else:
            ordem = list(self.ordem_de_uso_das_paginas)
        for identidade_da_pagina in ordem:
            if identidade_da_pagina in self.paginas_protegidas_ate_o_acerto:
                continue
            if identidade_da_pagina in self.paginas_em_uso_por_uma_cpu:
                continue
            return identidade_da_pagina
        return None

    def _quadro_livre(self) -> int | None:
        for indice, pagina in enumerate(self.pagina_de_cada_quadro):
            if pagina is None:
                return indice
        return None

    def _marcar_pagina_como_recentemente_usada(self, identidade_da_pagina: tuple[int, int]) -> None:
        if self.algoritmo_de_substituicao_de_pagina == "lru":
            self.ordem_de_uso_das_paginas.move_to_end(identidade_da_pagina)

    def _remover(self, identidade_da_pagina: tuple[int, int]) -> None:
        indice = self.quadro_da_pagina.pop(identidade_da_pagina)
        self.pagina_de_cada_quadro[indice] = None
        self.paginas_protegidas_ate_o_acerto.discard(identidade_da_pagina)
        self.paginas_em_uso_por_uma_cpu.discard(identidade_da_pagina)
        if self.algoritmo_de_substituicao_de_pagina == "fifo":
            self.ordem_de_carregamento_das_paginas.remove(identidade_da_pagina)
        else:
            del self.ordem_de_uso_das_paginas[identidade_da_pagina]
