"""Roda as 28 execuções base e as 4 comparações FIFO contra LRU."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from redigir import escrever_analise  # noqa: E402
from simulador.metricas import Resultado  # noqa: E402
from simulador.modelos import Parametros  # noqa: E402
from simulador.nucleo import simular  # noqa: E402
from simulador.saida import gravar  # noqa: E402

PASTA = RAIZ / "resultados"
QUANTUMS = (2, 5, 10, 20, 50)
VARIANTES = [("fcfs", None), ("sjf", None), *[("rr", quantum) for quantum in QUANTUMS]]
CENARIOS = (
    ("A", RAIZ / "dados" / "cenario_A_t0.json"),
    ("B", RAIZ / "dados" / "cenario_B_espacadas.json"),
)
EXTRAS_FIFO = (
    ("A", "fcfs", None, 1),
    ("A", "rr", 10, 4),
    ("B", "sjf", None, 1),
    ("B", "rr", 2, 4),
)
CAMPOS = (
    "cenario",
    "sched",
    "quantum",
    "cpus",
    "subst",
    "espera_media",
    "espera_max",
    "espera_max_pid",
    "turnaround_medio",
    "resposta_media",
    "makespan",
    "trocas_contexto",
    "page_faults",
    "taxa_faults",
    "speedup",
    "eficiencia",
    "espera_curto",
    "espera_longo",
    "turnaround_curto",
    "turnaround_longo",
    "resposta_curto",
    "resposta_longo",
)


def main() -> None:
    PASTA.mkdir(parents=True, exist_ok=True)
    referencias: dict[tuple[str, str, int | None, str], Path] = {}
    linhas: list[dict[str, object]] = []
    for cenario, arquivo in CENARIOS:
        for sched, quantum in VARIANTES:
            for cpus in (1, 4):
                linhas.append(_executar(cenario, arquivo, sched, quantum, cpus, "lru", referencias))
    for cenario, sched, quantum, cpus in EXTRAS_FIFO:
        arquivo = dict(CENARIOS)[cenario]
        linhas.append(_executar(cenario, arquivo, sched, quantum, cpus, "fifo", referencias))
    _gravar_csv(linhas)
    escrever_analise(linhas, RAIZ / "experimentos" / "analise.md")
    print(f"metricas: {PASTA / 'metricas.csv'}")
    print(f"analise: {RAIZ / 'experimentos' / 'analise.md'}")


def _executar(
    cenario: str,
    arquivo: Path,
    sched: str,
    quantum: int | None,
    cpus: int,
    subst: str,
    referencias: dict[tuple[str, str, int | None, str], Path],
) -> dict[str, object]:
    referencia = None
    if cpus == 4:
        anterior = referencias.get((cenario, sched, quantum, subst))
        if anterior is not None:
            referencia = str(anterior)
    resultado = simular(
        Parametros(
            arquivo=str(arquivo),
            cpus=cpus,
            sched=sched,
            quantum=quantum,
            subst=subst,
            quadros=256,
            custo_troca=1,
            tempo_fault=20,
            referencia_1cpu=referencia,
            saida=str(PASTA),
        )
    )
    for cpu in resultado.cpus:
        soma = cpu.tempo_util + cpu.tempo_troca + cpu.tempo_ocioso
        if soma != resultado.makespan:
            raise RuntimeError(
                f"CPU {cpu.indice} não fecha o makespan ({soma} != {resultado.makespan})"
            )
    _, metricas = gravar(resultado, PASTA)
    if cpus == 1:
        referencias[(cenario, sched, quantum, subst)] = metricas
    linha = _linha(cenario, resultado)
    quantum_txt = "-" if quantum is None else str(quantum)
    print(
        f"{cenario} {sched} q={quantum_txt} cpu={cpus} {subst} "
        f"makespan={resultado.makespan} espera={resultado.espera_media():.2f} "
        f"faults={resultado.page_faults}",
        flush=True,
    )
    return linha


def _linha(cenario: str, resultado: Resultado) -> dict[str, object]:
    params = resultado.parametros
    return {
        "cenario": cenario,
        "sched": params.sched,
        "quantum": "" if params.quantum is None else params.quantum,
        "cpus": params.cpus,
        "subst": params.subst,
        "espera_media": resultado.espera_media(),
        "espera_max": resultado.espera_max(),
        "espera_max_pid": resultado.espera_max_pid(),
        "turnaround_medio": resultado.turnaround_medio(),
        "resposta_media": resultado.resposta_media(),
        "makespan": resultado.makespan,
        "trocas_contexto": resultado.trocas_total(),
        "page_faults": resultado.page_faults,
        "taxa_faults": resultado.taxa_faults(),
        "speedup": resultado.speedup,
        "eficiencia": resultado.eficiencia,
        "espera_curto": resultado.media_classe("curto", "espera"),
        "espera_longo": resultado.media_classe("longo", "espera"),
        "turnaround_curto": resultado.media_classe("curto", "turnaround"),
        "turnaround_longo": resultado.media_classe("longo", "turnaround"),
        "resposta_curto": resultado.media_classe("curto", "resposta"),
        "resposta_longo": resultado.media_classe("longo", "resposta"),
    }


def _gravar_csv(linhas: list[dict[str, object]]) -> None:
    with (PASTA / "metricas.csv").open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    main()
