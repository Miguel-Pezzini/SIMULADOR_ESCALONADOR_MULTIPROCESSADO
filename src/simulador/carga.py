"""Leitura e validação da carga em JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from simulador.modelos import Burst, BurstCPU, BurstES, Processo


def carregar(caminho: Path) -> list[Processo]:
    try:
        bruto = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"arquivo não encontrado: {caminho}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido em {caminho}: {exc}") from exc
    if not isinstance(bruto, list):
        raise ValueError("o JSON deve ser uma lista de processos")

    processos: list[Processo] = []
    vistos: set[int] = set()
    for indice, item in enumerate(bruto):
        if not isinstance(item, dict):
            raise ValueError(f"processo na posição {indice} não é um objeto")
        processo = _processo(cast(dict[str, object], item))
        if processo.pid in vistos:
            raise ValueError(f"pid duplicado: {processo.pid}")
        vistos.add(processo.pid)
        processos.append(processo)
    return processos


def _processo(item: dict[str, object]) -> Processo:
    pid = _inteiro(item, "pid")
    chegada = _inteiro(item, "chegada")
    classe = item.get("classe")
    paginas = _inteiro(item, "paginas")
    if not isinstance(classe, str) or not classe:
        raise ValueError(f"processo {pid}: classe ausente")
    if paginas < 1:
        raise ValueError(f"processo {pid}: paginas deve ser pelo menos 1")
    bursts_brutos = item.get("bursts")
    if not isinstance(bursts_brutos, list) or not bursts_brutos:
        raise ValueError(f"processo {pid}: bursts vazio")

    bursts: list[Burst] = []
    for etapa in bursts_brutos:
        if not isinstance(etapa, dict):
            raise ValueError(f"processo {pid}: etapa inválida em bursts")
        bursts.append(_burst(pid, paginas, cast(dict[str, object], etapa)))
    if not isinstance(bursts[0], BurstCPU) or not isinstance(bursts[-1], BurstCPU):
        raise ValueError(f"processo {pid}: a vida começa e termina com burst de CPU")
    for indice in range(len(bursts) - 1):
        if isinstance(bursts[indice], type(bursts[indice + 1])):
            raise ValueError(f"processo {pid}: bursts de CPU e E/S devem alternar")
    return Processo(
        pid=pid,
        chegada=chegada,
        classe=classe,
        paginas=paginas,
        bursts=tuple(bursts),
    )


def _burst(pid: int, paginas: int, etapa: dict[str, object]) -> Burst:
    if "cpu" in etapa:
        cpu = etapa["cpu"]
        refs = etapa.get("refs")
        if not isinstance(cpu, int) or isinstance(cpu, bool) or cpu < 1:
            raise ValueError(f"processo {pid}: cpu inválido")
        if not isinstance(refs, list) or len(refs) != cpu:
            raise ValueError(f"processo {pid}: refs deve ter exatamente {cpu} páginas")
        paginas_ref: list[int] = []
        for ref in refs:
            if not isinstance(ref, int) or isinstance(ref, bool) or not 0 <= ref < paginas:
                raise ValueError(f"processo {pid}: referência fora do intervalo de páginas")
            paginas_ref.append(ref)
        return BurstCPU(cpu=cpu, refs=tuple(paginas_ref))
    if "es" in etapa:
        es = etapa["es"]
        if not isinstance(es, int) or isinstance(es, bool) or es < 1:
            raise ValueError(f"processo {pid}: es inválido")
        return BurstES(es=es)
    raise ValueError(f"processo {pid}: etapa sem cpu nem es")


def _inteiro(item: dict[str, object], campo: str) -> int:
    valor = item.get(campo)
    if not isinstance(valor, int) or isinstance(valor, bool) or valor < 0:
        raise ValueError(f"campo {campo} deve ser um inteiro >= 0")
    return valor
