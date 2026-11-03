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
from simulador.saida import gravar_gantt_e_metricas  # noqa: E402

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
    "tempo_util",
    "tempo_troca",
    "tempo_ocioso",
    "utilizacao_media",
    *(
        nome
        for indice in range(4)
        for nome in (
            f"cpu{indice}_util",
            f"cpu{indice}_troca",
            f"cpu{indice}_ocioso",
            f"cpu{indice}_trocas",
            f"cpu{indice}_utilizacao",
        )
    ),
)


def main() -> None:
    PASTA.mkdir(parents=True, exist_ok=True)
    arquivos_de_metricas_com_1_cpu: dict[tuple[str, str, int | None, str], Path] = {}
    linhas: list[dict[str, object]] = []
    for cenario, arquivo in CENARIOS:
        for algoritmo_de_escalonamento, quantum in VARIANTES:
            for cpus in (1, 4):
                linhas.append(
                    _executar(
                        cenario,
                        arquivo,
                        algoritmo_de_escalonamento,
                        quantum,
                        cpus,
                        "lru",
                        arquivos_de_metricas_com_1_cpu,
                    )
                )
    for cenario, algoritmo_de_escalonamento, quantum, cpus in EXTRAS_FIFO:
        arquivo = dict(CENARIOS)[cenario]
        linhas.append(
            _executar(
                cenario,
                arquivo,
                algoritmo_de_escalonamento,
                quantum,
                cpus,
                "fifo",
                arquivos_de_metricas_com_1_cpu,
            )
        )
    _gravar_csv(linhas)
    escrever_analise(linhas, RAIZ / "experimentos" / "analise.md")
    print(f"metricas: {PASTA / 'metricas.csv'}")
    print(f"analise: {RAIZ / 'experimentos' / 'analise.md'}")


def _executar(
    cenario: str,
    arquivo: Path,
    algoritmo_de_escalonamento: str,
    quantum: int | None,
    cpus: int,
    algoritmo_de_substituicao_de_pagina: str,
    arquivos_de_metricas_com_1_cpu: dict[tuple[str, str, int | None, str], Path],
) -> dict[str, object]:
    arquivo_de_metricas_com_1_cpu = None
    if cpus == 4:
        chave = (
            cenario,
            algoritmo_de_escalonamento,
            quantum,
            algoritmo_de_substituicao_de_pagina,
        )
        rodada_com_1_cpu = arquivos_de_metricas_com_1_cpu.get(chave)
        if rodada_com_1_cpu is not None:
            arquivo_de_metricas_com_1_cpu = str(rodada_com_1_cpu)
    resultado = simular(
        Parametros(
            arquivo=str(arquivo),
            cpus=cpus,
            algoritmo_de_escalonamento=algoritmo_de_escalonamento,
            quantum=quantum,
            algoritmo_de_substituicao_de_pagina=algoritmo_de_substituicao_de_pagina,
            quadros=256,
            custo_troca=1,
            tempo_fault=20,
            arquivo_de_metricas_com_1_cpu=arquivo_de_metricas_com_1_cpu,
            saida=str(PASTA),
        )
    )
    for cpu in resultado.cpus:
        soma = cpu.tempo_util + cpu.tempo_troca + cpu.tempo_ocioso
        if soma != resultado.makespan:
            raise RuntimeError(
                f"CPU {cpu.indice} não fecha o makespan ({soma} != {resultado.makespan})"
            )
    _, metricas = gravar_gantt_e_metricas(resultado, PASTA)
    if cpus == 1:
        arquivos_de_metricas_com_1_cpu[
            (cenario, algoritmo_de_escalonamento, quantum, algoritmo_de_substituicao_de_pagina)
        ] = metricas
    linha = _linha(cenario, resultado)
    quantum_txt = "-" if quantum is None else str(quantum)
    print(
        f"{cenario} {algoritmo_de_escalonamento} q={quantum_txt} cpu={cpus} "
        f"{algoritmo_de_substituicao_de_pagina} "
        f"makespan={resultado.makespan} espera={resultado.espera_media():.2f} "
        f"faults={resultado.page_faults}",
        flush=True,
    )
    return linha


def _linha(cenario: str, resultado: Resultado) -> dict[str, object]:
    params = resultado.parametros
    return {
        "cenario": cenario,
        "sched": params.algoritmo_de_escalonamento,
        "quantum": "" if params.quantum is None else params.quantum,
        "cpus": params.cpus,
        "subst": params.algoritmo_de_substituicao_de_pagina,
        "espera_media": resultado.espera_media(),
        "espera_max": resultado.espera_max(),
        "espera_max_pid": resultado.espera_max_pid(),
        "turnaround_medio": resultado.turnaround_medio(),
        "resposta_media": resultado.resposta_media(),
        "makespan": resultado.makespan,
        "trocas_contexto": resultado.total_de_trocas_de_contexto(),
        "page_faults": resultado.page_faults,
        "taxa_faults": resultado.taxa_de_faltas_de_pagina(),
        "speedup": resultado.speedup,
        "eficiencia": resultado.eficiencia,
        "espera_curto": resultado.media_do_campo_na_classe("curto", "espera"),
        "espera_longo": resultado.media_do_campo_na_classe("longo", "espera"),
        "turnaround_curto": resultado.media_do_campo_na_classe("curto", "turnaround"),
        "turnaround_longo": resultado.media_do_campo_na_classe("longo", "turnaround"),
        "resposta_curto": resultado.media_do_campo_na_classe("curto", "resposta"),
        "resposta_longo": resultado.media_do_campo_na_classe("longo", "resposta"),
        **_parcelas_das_cpus(resultado),
    }


def _parcelas_das_cpus(resultado: Resultado) -> dict[str, object]:
    makespan = resultado.makespan
    campos: dict[str, object] = {
        "tempo_util": sum(cpu.tempo_util for cpu in resultado.cpus),
        "tempo_troca": sum(cpu.tempo_troca for cpu in resultado.cpus),
        "tempo_ocioso": sum(cpu.tempo_ocioso for cpu in resultado.cpus),
        "utilizacao_media": sum(cpu.utilizacao(makespan) for cpu in resultado.cpus)
        / len(resultado.cpus),
    }
    for indice in range(4):
        if indice < len(resultado.cpus):
            cpu = resultado.cpus[indice]
            campos[f"cpu{indice}_util"] = cpu.tempo_util
            campos[f"cpu{indice}_troca"] = cpu.tempo_troca
            campos[f"cpu{indice}_ocioso"] = cpu.tempo_ocioso
            campos[f"cpu{indice}_trocas"] = cpu.trocas
            campos[f"cpu{indice}_utilizacao"] = cpu.utilizacao(makespan)
        else:
            campos[f"cpu{indice}_util"] = ""
            campos[f"cpu{indice}_troca"] = ""
            campos[f"cpu{indice}_ocioso"] = ""
            campos[f"cpu{indice}_trocas"] = ""
            campos[f"cpu{indice}_utilizacao"] = ""
    return campos


def _gravar_csv(linhas: list[dict[str, object]]) -> None:
    with (PASTA / "metricas.csv").open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    main()
