"""Linha de comando do simulador."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from simulador.metricas import Resultado
from simulador.modelos import Parametros
from simulador.nucleo import simular
from simulador.saida import gravar_gantt_e_metricas, imprimir_resumo


def main(argv: list[str] | None = None) -> int:
    parser = _montar_argumentos()
    args = parser.parse_args(argv)
    quantum = args.quantum if args.sched == "rr" else None
    try:
        parametros = Parametros(
            arquivo=args.arquivo,
            cpus=args.cpus,
            algoritmo_de_escalonamento=args.sched,
            quantum=quantum,
            algoritmo_de_substituicao_de_pagina=args.subst,
            quadros=args.quadros,
            custo_troca=args.custo_troca,
            tempo_fault=args.tempo_fault,
            ignorar_memoria=args.ignorar_memoria,
            log=args.log,
            arquivo_de_metricas_com_1_cpu=args.referencia_1cpu,
            saida=args.saida,
        )
        resultado = simular(parametros)
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2
    _imprimir_resumo_e_gravar_arquivos(resultado)
    return 0


def _imprimir_resumo_e_gravar_arquivos(resultado: Resultado) -> None:
    imprimir_resumo(resultado)
    if resultado.parametros.saida is not None:
        gantt, metricas = gravar_gantt_e_metricas(resultado, Path(resultado.parametros.saida))
        print(f"gantt: {gantt}")
        print(f"metricas: {metricas}")


def _montar_argumentos() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="simulador",
        description="Simulador de escalonamento multiprocessado com paginação sob demanda.",
    )
    parser.add_argument("--arquivo", required=True, help="JSON com a carga de processos")
    parser.add_argument("--cpus", required=True, type=int, choices=(1, 4))
    parser.add_argument("--sched", required=True, choices=("fcfs", "sjf", "rr"))
    parser.add_argument("--quantum", type=int, help="fatia do Round Robin")
    parser.add_argument("--subst", required=True, choices=("fifo", "lru"))
    parser.add_argument("--quadros", type=int, default=256)
    parser.add_argument("--custo-troca", type=int, default=1)
    parser.add_argument(
        "--tempo-fault",
        type=int,
        default=20,
        help="duração do page fault (padrão 20)",
    )
    parser.add_argument(
        "--ignorar-memoria",
        action="store_true",
        help="desliga a paginação, para reproduzir o exemplo sem memória",
    )
    parser.add_argument("--log", action="store_true", help="grava o log de estados")
    parser.add_argument(
        "--referencia-1cpu",
        help="JSON de métricas da rodada com 1 CPU, para calcular speedup e eficiência",
    )
    parser.add_argument(
        "--saida",
        default="resultados",
        help="diretório do Gantt, das métricas e do log (padrão: resultados)",
    )
    return parser
