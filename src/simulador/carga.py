"""Leitura e validação da carga em JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from simulador.modelos import Burst, BurstCPU, BurstES, Processo


def carregar_processos(caminho: Path) -> list[Processo]:
    try:
        conteudo_json = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"arquivo não encontrado: {caminho}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido em {caminho}: {exc}") from exc
    if not isinstance(conteudo_json, list):
        raise ValueError("o JSON deve ser uma lista de processos")

    processos: list[Processo] = []
    pids_ja_lidos: set[int] = set()
    for indice, item in enumerate(conteudo_json):
        if not isinstance(item, dict):
            raise ValueError(f"processo na posição {indice} não é um objeto")
        processo = _ler_processo(cast(dict[str, object], item))
        if processo.pid in pids_ja_lidos:
            raise ValueError(f"pid duplicado: {processo.pid}")
        pids_ja_lidos.add(processo.pid)
        processos.append(processo)
    return processos


def _ler_processo(item: dict[str, object]) -> Processo:
    pid = _ler_inteiro_nao_negativo(item, "pid")
    chegada = _ler_inteiro_nao_negativo(item, "chegada")
    classe = item.get("classe")
    paginas = _ler_inteiro_nao_negativo(item, "paginas")
    if not isinstance(classe, str) or not classe:
        raise ValueError(f"processo {pid}: classe ausente")
    if paginas < 1:
        raise ValueError(f"processo {pid}: paginas deve ser pelo menos 1")
    bursts_no_json = item.get("bursts")
    if not isinstance(bursts_no_json, list) or not bursts_no_json:
        raise ValueError(f"processo {pid}: bursts vazio")

    bursts: list[Burst] = []
    for descricao_do_burst in bursts_no_json:
        if not isinstance(descricao_do_burst, dict):
            raise ValueError(f"processo {pid}: etapa inválida em bursts")
        bursts.append(_ler_burst(pid, paginas, cast(dict[str, object], descricao_do_burst)))
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


def _ler_burst(pid: int, paginas: int, descricao_do_burst: dict[str, object]) -> Burst:
    if "cpu" in descricao_do_burst:
        duracao_de_cpu = descricao_do_burst["cpu"]
        paginas_no_json = descricao_do_burst.get("refs")
        if (
            not isinstance(duracao_de_cpu, int)
            or isinstance(duracao_de_cpu, bool)
            or duracao_de_cpu < 1
        ):
            raise ValueError(f"processo {pid}: cpu inválido")
        if not isinstance(paginas_no_json, list) or len(paginas_no_json) != duracao_de_cpu:
            raise ValueError(f"processo {pid}: refs deve ter exatamente {duracao_de_cpu} páginas")
        numeros_de_pagina: list[int] = []
        for numero_de_pagina in paginas_no_json:
            pagina_valida = (
                isinstance(numero_de_pagina, int)
                and not isinstance(numero_de_pagina, bool)
                and 0 <= numero_de_pagina < paginas
            )
            if not pagina_valida:
                raise ValueError(f"processo {pid}: referência fora do intervalo de páginas")
            numeros_de_pagina.append(numero_de_pagina)
        return BurstCPU(
            duracao_de_cpu=duracao_de_cpu,
            paginas_referenciadas_no_burst=tuple(numeros_de_pagina),
        )
    if "es" in descricao_do_burst:
        duracao_de_entrada_saida = descricao_do_burst["es"]
        if (
            not isinstance(duracao_de_entrada_saida, int)
            or isinstance(duracao_de_entrada_saida, bool)
            or duracao_de_entrada_saida < 1
        ):
            raise ValueError(f"processo {pid}: es inválido")
        return BurstES(duracao_de_entrada_saida=duracao_de_entrada_saida)
    raise ValueError(f"processo {pid}: etapa sem cpu nem es")


def _ler_inteiro_nao_negativo(item: dict[str, object], campo: str) -> int:
    valor = item.get(campo)
    if not isinstance(valor, int) or isinstance(valor, bool) or valor < 0:
        raise ValueError(f"campo {campo} deve ser um inteiro >= 0")
    return valor
