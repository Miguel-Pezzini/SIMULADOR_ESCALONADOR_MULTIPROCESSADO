"""Atalho para montar uma execução de teste."""

from __future__ import annotations

import json
from pathlib import Path

from simulador.metricas import Resultado
from simulador.modelos import Parametros
from simulador.nucleo import simular


def burst_de_cpu(
    duracao_de_cpu: int,
    paginas_referenciadas: list[int] | None = None,
) -> dict[str, object]:
    if paginas_referenciadas is None:
        paginas_referenciadas = [0] * duracao_de_cpu
    return {"cpu": duracao_de_cpu, "refs": paginas_referenciadas}


def burst_de_entrada_saida(duracao_de_entrada_saida: int) -> dict[str, object]:
    return {"es": duracao_de_entrada_saida}


def processo(
    pid: int,
    chegada: int,
    bursts: list[dict[str, object]],
    *,
    classe: str = "curto",
    paginas: int = 1,
) -> dict[str, object]:
    return {
        "pid": pid,
        "chegada": chegada,
        "classe": classe,
        "paginas": paginas,
        "bursts": bursts,
    }


def gravar_carga(caminho: Path, processos: list[dict[str, object]]) -> None:
    caminho.write_text(json.dumps(processos), encoding="utf-8")


def rodar(
    arquivo: Path,
    *,
    cpus: int = 1,
    algoritmo_de_escalonamento: str = "fcfs",
    quantum: int | None = None,
    algoritmo_de_substituicao_de_pagina: str = "fifo",
    quadros: int = 32,
    custo_troca: int = 1,
    tempo_fault: int = 20,
    ignorar_memoria: bool = False,
    log: bool = False,
    arquivo_de_metricas_com_1_cpu: str | None = None,
    saida: str | None = None,
) -> Resultado:
    return simular(
        Parametros(
            arquivo=str(arquivo),
            cpus=cpus,
            algoritmo_de_escalonamento=algoritmo_de_escalonamento,
            quantum=quantum,
            algoritmo_de_substituicao_de_pagina=algoritmo_de_substituicao_de_pagina,
            quadros=quadros,
            custo_troca=custo_troca,
            tempo_fault=tempo_fault,
            ignorar_memoria=ignorar_memoria,
            log=log,
            arquivo_de_metricas_com_1_cpu=arquivo_de_metricas_com_1_cpu,
            saida=saida,
        )
    )


def espera_por_pid(resultado: Resultado) -> dict[int, int]:
    return {processo.pid: processo.espera for processo in resultado.processos}


def conferir_se_os_tempos_das_cpus_fecham_o_makespan(resultado: Resultado) -> None:
    for cpu in resultado.cpus:
        soma = cpu.tempo_util + cpu.tempo_troca + cpu.tempo_ocioso
        assert soma == resultado.makespan
