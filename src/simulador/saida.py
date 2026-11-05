"""Resumo padronizado e Gantt da janela 0 a 200."""

from __future__ import annotations

import json
from pathlib import Path

from simulador.metricas import Resultado

JANELA_GANTT = 200


def nome_dos_arquivos_desta_execucao(resultado: Resultado) -> str:
    parametros = resultado.parametros
    arquivo = Path(parametros.arquivo).stem
    quantum = f"q{parametros.quantum}" if parametros.quantum is not None else "q-"
    if parametros.ignorar_memoria:
        trecho_de_memoria_no_nome = "semmem"
    else:
        trecho_de_memoria_no_nome = (
            f"{parametros.algoritmo_de_substituicao_de_pagina}_f{parametros.quadros}"
        )
    return (
        f"{arquivo}_{parametros.algoritmo_de_escalonamento}_{quantum}_cpu{parametros.cpus}_"
        f"{trecho_de_memoria_no_nome}_t{parametros.custo_troca}_pf{parametros.tempo_fault}"
    )


def recortar_gantt(
    intervalos: list[tuple[int, int, str]],
    instante_final_da_janela: int = JANELA_GANTT,
) -> list[tuple[int, int, str]]:
    intervalos_recortados: list[tuple[int, int, str]] = []
    for inicio, fim, evento in intervalos:
        inicio_visivel_na_janela = max(inicio, 0)
        fim_visivel_na_janela = min(fim, instante_final_da_janela)
        if inicio_visivel_na_janela >= fim_visivel_na_janela:
            continue
        cabe_no_intervalo_anterior = (
            intervalos_recortados
            and intervalos_recortados[-1][2] == evento
            and intervalos_recortados[-1][1] == inicio_visivel_na_janela
        )
        if cabe_no_intervalo_anterior:
            inicio_anterior, _, rotulo = intervalos_recortados[-1]
            intervalos_recortados[-1] = (inicio_anterior, fim_visivel_na_janela, rotulo)
        else:
            intervalos_recortados.append((inicio_visivel_na_janela, fim_visivel_na_janela, evento))
    return intervalos_recortados


def formatar_resumo(resultado: Resultado) -> str:
    parametros = resultado.parametros
    linhas = [
        "=== Parâmetros ===",
        f"arquivo: {parametros.arquivo}",
        f"cpus: {parametros.cpus}",
        f"escalonador: {parametros.algoritmo_de_escalonamento}",
        f"quantum: {parametros.quantum if parametros.quantum is not None else '-'}",
        f"substituicao: {parametros.algoritmo_de_substituicao_de_pagina}",
        f"quadros: {parametros.quadros}",
        f"custo_troca: {parametros.custo_troca}",
        f"tempo_fault: {parametros.tempo_fault}",
        f"ignorar_memoria: {'sim' if parametros.ignorar_memoria else 'nao'}",
        "",
        "=== Métricas globais ===",
        f"espera_media: {resultado.espera_media():.2f}",
        f"espera_max: {resultado.espera_max()}",
        f"turnaround_medio: {resultado.turnaround_medio():.2f}",
        f"resposta_media: {resultado.resposta_media():.2f}",
        f"makespan: {resultado.makespan}",
        f"trocas_contexto: {resultado.total_de_trocas_de_contexto()}",
        f"page_faults: {resultado.page_faults}",
        f"taxa_faults: {resultado.taxa_de_faltas_de_pagina():.4f}",
        f"speedup: {_formatar_opcional(resultado.speedup)}",
        f"eficiencia: {_formatar_opcional(resultado.eficiencia)}",
        "",
        "=== Por classe ===",
        "classe espera_media turnaround_medio resposta_media",
    ]
    for classe in ("curto", "longo"):
        espera = resultado.media_do_campo_na_classe(classe, "espera")
        turnaround_da_classe = resultado.media_do_campo_na_classe(classe, "turnaround")
        resposta = resultado.media_do_campo_na_classe(classe, "resposta")
        if espera is None or turnaround_da_classe is None or resposta is None:
            continue
        linhas.append(f"{classe} {espera:.2f} {turnaround_da_classe:.2f} {resposta:.2f}")
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


def imprimir_resumo(resultado: Resultado) -> None:
    print(formatar_resumo(resultado), end="")


def gravar_gantt_e_metricas(resultado: Resultado, diretorio: Path) -> tuple[Path, Path]:
    diretorio.mkdir(parents=True, exist_ok=True)
    base = diretorio / nome_dos_arquivos_desta_execucao(resultado)
    gantt = base.with_name(base.name + "_gantt.csv")
    metricas = base.with_suffix(".json")
    gantt.write_text(_gantt_csv(resultado), encoding="utf-8")
    metricas.write_text(
        json.dumps(resultado_para_dicionario(resultado), indent=2),
        encoding="utf-8",
    )
    return gantt, metricas


def resultado_para_dicionario(resultado: Resultado) -> dict[str, object]:
    parametros = resultado.parametros
    return {
        "arquivo": parametros.arquivo,
        "cpus": parametros.cpus,
        "sched": parametros.algoritmo_de_escalonamento,
        "quantum": parametros.quantum,
        "subst": parametros.algoritmo_de_substituicao_de_pagina,
        "quadros": parametros.quadros,
        "custo_troca": parametros.custo_troca,
        "tempo_fault": parametros.tempo_fault,
        "ignorar_memoria": parametros.ignorar_memoria,
        "espera_media": resultado.espera_media(),
        "espera_max": resultado.espera_max(),
        "espera_max_pid": resultado.espera_max_pid(),
        "turnaround_medio": resultado.turnaround_medio(),
        "resposta_media": resultado.resposta_media(),
        "makespan": resultado.makespan,
        "trocas_contexto": resultado.total_de_trocas_de_contexto(),
        "page_faults": resultado.page_faults,
        "acertos": resultado.acertos,
        "taxa_faults": resultado.taxa_de_faltas_de_pagina(),
        "speedup": resultado.speedup,
        "eficiencia": resultado.eficiencia,
        "espera_curto": resultado.media_do_campo_na_classe("curto", "espera"),
        "espera_longo": resultado.media_do_campo_na_classe("longo", "espera"),
        "turnaround_curto": resultado.media_do_campo_na_classe("curto", "turnaround"),
        "turnaround_longo": resultado.media_do_campo_na_classe("longo", "turnaround"),
        "resposta_curto": resultado.media_do_campo_na_classe("curto", "resposta"),
        "resposta_longo": resultado.media_do_campo_na_classe("longo", "resposta"),
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
    tempo_util: int,
    tempo_de_troca: int,
    tempo_ocioso: int,
    trocas: int,
) -> str:
    def percentual(parte: int) -> float:
        if makespan == 0:
            return 0.0
        return 100.0 * parte / makespan

    utilizacao = 0.0 if makespan == 0 else 100.0 * (tempo_util + tempo_de_troca) / makespan
    return (
        f"{indice} {tempo_util} {tempo_de_troca} {tempo_ocioso} {trocas} "
        f"{percentual(tempo_util):.2f} {percentual(tempo_de_troca):.2f} "
        f"{percentual(tempo_ocioso):.2f} {utilizacao:.2f}"
    )


def _formatar_opcional(valor: float | None) -> str:
    if valor is None:
        return "-"
    return f"{valor:.4f}"
