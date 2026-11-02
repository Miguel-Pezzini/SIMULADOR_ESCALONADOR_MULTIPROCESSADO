"""Atalho para montar uma execução de teste."""

from __future__ import annotations

import json
from pathlib import Path

from simulador.metricas import Resultado
from simulador.modelos import Parametros
from simulador.nucleo import simular


def burst_cpu(duracao: int, refs: list[int] | None = None) -> dict[str, object]:
    return {"cpu": duracao, "refs": [0] * duracao if refs is None else refs}


def es(duracao: int) -> dict[str, object]:
    return {"es": duracao}


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
    sched: str = "fcfs",
    quantum: int | None = None,
    subst: str = "fifo",
    quadros: int = 32,
    custo_troca: int = 1,
    tempo_fault: int = 20,
    ignorar_memoria: bool = False,
    log: bool = False,
    referencia_1cpu: str | None = None,
    saida: str | None = None,
) -> Resultado:
    return simular(
        Parametros(
            arquivo=str(arquivo),
            cpus=cpus,
            sched=sched,
            quantum=quantum,
            subst=subst,
            quadros=quadros,
            custo_troca=custo_troca,
            tempo_fault=tempo_fault,
            ignorar_memoria=ignorar_memoria,
            log=log,
            referencia_1cpu=referencia_1cpu,
            saida=saida,
        )
    )


def por_pid(resultado: Resultado) -> dict[int, int]:
    return {proc.pid: proc.espera for proc in resultado.processos}


def fecha_makespan(resultado: Resultado) -> None:
    for cpu in resultado.cpus:
        soma = cpu.tempo_util + cpu.tempo_troca + cpu.tempo_ocioso
        assert soma == resultado.makespan
