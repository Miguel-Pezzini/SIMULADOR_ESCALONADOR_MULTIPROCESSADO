"""Resumo padronizado, Gantt da janela 0 a 200 e log de estados."""

from __future__ import annotations

import json
from pathlib import Path

from simulador.metricas import Resultado

JANELA_GANTT = 200


def nome_execucao(resultado: Resultado) -> str:
    params = resultado.parametros
    arquivo = Path(params.arquivo).stem
    quantum = f"q{params.quantum}" if params.quantum is not None else "q-"
    memoria = "semmem" if params.ignorar_memoria else f"{params.subst}_f{params.quadros}"
    return (
        f"{arquivo}_{params.sched}_{quantum}_cpu{params.cpus}_"
        f"{memoria}_t{params.custo_troca}_pf{params.tempo_fault}"
    )


def recortar_gantt(
    intervalos: list[tuple[int, int, str]],
    limite: int = JANELA_GANTT,
) -> list[tuple[int, int, str]]:
    recorte: list[tuple[int, int, str]] = []
    for inicio, fim, evento in intervalos:
        a = max(inicio, 0)
        b = min(fim, limite)
        if a >= b:
            continue
        if recorte and recorte[-1][2] == evento and recorte[-1][1] == a:
            ini, _, ev = recorte[-1]
            recorte[-1] = (ini, b, ev)
        else:
            recorte.append((a, b, evento))
    return recorte


def formatar_resumo(resultado: Resultado) -> str:
    params = resultado.parametros
    linhas = [
        "=== Parâmetros ===",
        f"arquivo: {params.arquivo}",
        f"cpus: {params.cpus}",
        f"escalonador: {params.sched}",
        f"quantum: {params.quantum if params.quantum is not None else '-'}",
        f"substituicao: {params.subst}",
        f"quadros: {params.quadros}",
        f"custo_troca: {params.custo_troca}",
        f"tempo_fault: {params.tempo_fault}",
        f"ignorar_memoria: {'sim' if params.ignorar_memoria else 'nao'}",
        "",
        "=== Métricas globais ===",
        f"espera_media: {resultado.espera_media():.2f}",
        f"espera_max: {resultado.espera_max()}",
        f"turnaround_medio: {resultado.turnaround_medio():.2f}",
        f"resposta_media: {resultado.resposta_media():.2f}",
        f"makespan: {resultado.makespan}",
        f"trocas_contexto: {resultado.trocas_total()}",
        f"page_faults: {resultado.page_faults}",
        f"taxa_faults: {resultado.taxa_faults():.4f}",
        f"speedup: {_fmt_opcional(resultado.speedup)}",
        f"eficiencia: {_fmt_opcional(resultado.eficiencia)}",
        "",
        "=== Por classe ===",
        "classe espera_media turnaround_medio resposta_media",
    ]
    for classe in ("curto", "longo"):
        espera = resultado.media_classe(classe, "espera")
        turno = resultado.media_classe(classe, "turnaround")
        resposta = resultado.media_classe(classe, "resposta")
        if espera is None or turno is None or resposta is None:
            continue
        linhas.append(f"{classe} {espera:.2f} {turno:.2f} {resposta:.2f}")
    linhas.extend(
        [
            "",
            "=== Por CPU ===",
            (
                "cpu tempo_util tempo_troca tempo_ocioso trocas "
                "util_pct troca_pct ocioso_pct utilizacao_pct"
            ),
        ]
    )
    for cpu in resultado.cpus:
        linhas.append(
            _linha_cpu(
                resultado.makespan,
                cpu.indice,
                cpu.tempo_util,
                cpu.tempo_troca,
                cpu.tempo_ocioso,
                cpu.trocas,
            )
        )
    return "\n".join(linhas) + "\n"


def imprimir(resultado: Resultado) -> None:
    print(formatar_resumo(resultado), end="")


def gravar(resultado: Resultado, diretorio: Path) -> tuple[Path, Path]:
    diretorio.mkdir(parents=True, exist_ok=True)
    base = diretorio / nome_execucao(resultado)
    gantt = base.with_name(base.name + "_gantt.csv")
    metricas = base.with_suffix(".json")
    gantt.write_text(_gantt_csv(resultado), encoding="utf-8")
    metricas.write_text(json.dumps(para_json(resultado), indent=2), encoding="utf-8")
    if resultado.parametros.log:
        log = base.with_name(base.name + "_log.txt")
        log.write_text("\n".join(resultado.log) + ("\n" if resultado.log else ""), encoding="utf-8")
    return gantt, metricas


def para_json(resultado: Resultado) -> dict[str, object]:
    params = resultado.parametros
    return {
        "arquivo": params.arquivo,
        "cpus": params.cpus,
        "sched": params.sched,
        "quantum": params.quantum,
        "subst": params.subst,
        "quadros": params.quadros,
        "custo_troca": params.custo_troca,
        "tempo_fault": params.tempo_fault,
        "ignorar_memoria": params.ignorar_memoria,
        "espera_media": resultado.espera_media(),
        "espera_max": resultado.espera_max(),
        "espera_max_pid": resultado.espera_max_pid(),
        "turnaround_medio": resultado.turnaround_medio(),
        "resposta_media": resultado.resposta_media(),
        "makespan": resultado.makespan,
        "trocas_contexto": resultado.trocas_total(),
        "page_faults": resultado.page_faults,
        "acertos": resultado.acertos,
        "taxa_faults": resultado.taxa_faults(),
        "speedup": resultado.speedup,
        "eficiencia": resultado.eficiencia,
        "espera_curto": resultado.media_classe("curto", "espera"),
        "espera_longo": resultado.media_classe("longo", "espera"),
        "turnaround_curto": resultado.media_classe("curto", "turnaround"),
        "turnaround_longo": resultado.media_classe("longo", "turnaround"),
        "resposta_curto": resultado.media_classe("curto", "resposta"),
        "resposta_longo": resultado.media_classe("longo", "resposta"),
        "por_cpu": [
            {
                "indice": cpu.indice,
                "tempo_util": cpu.tempo_util,
                "tempo_troca": cpu.tempo_troca,
                "tempo_ocioso": cpu.tempo_ocioso,
                "trocas": cpu.trocas,
                "utilizacao": cpu.utilizacao(resultado.makespan),
            }
            for cpu in resultado.cpus
        ],
    }


def _gantt_csv(resultado: Resultado) -> str:
    linhas = ["cpu,inicio,fim,evento"]
    for cpu in resultado.cpus:
        for inicio, fim, evento in recortar_gantt(cpu.gantt):
            linhas.append(f"{cpu.indice},{inicio},{fim},{evento}")
    return "\n".join(linhas) + "\n"


def _linha_cpu(
    makespan: int,
    indice: int,
    util: int,
    troca: int,
    ocioso: int,
    trocas: int,
) -> str:
    def pct(parte: int) -> float:
        if makespan == 0:
            return 0.0
        return 100.0 * parte / makespan

    utilizacao = 0.0 if makespan == 0 else 100.0 * (util + troca) / makespan
    return (
        f"{indice} {util} {troca} {ocioso} {trocas} "
        f"{pct(util):.2f} {pct(troca):.2f} {pct(ocioso):.2f} {utilizacao:.2f}"
    )


def _fmt_opcional(valor: float | None) -> str:
    if valor is None:
        return "-"
    return f"{valor:.4f}"
