"""Gráficos da seção 11 e o Gantt de 0 a 200 do cenário A com FCFS."""

from __future__ import annotations

import csv
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.container import BarContainer  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "resultados"
GRAFICOS = PASTA / "graficos"
ROTULOS = (
    ("fcfs", "", "FCFS"),
    ("sjf", "", "SJF"),
    ("rr", "2", "RR2"),
    ("rr", "5", "RR5"),
    ("rr", "10", "RR10"),
    ("rr", "20", "RR20"),
    ("rr", "50", "RR50"),
)


METRICAS = (
    ("espera_media", "Espera média", "espera_media.png", "tempo"),
    ("espera_max", "Espera máxima", "espera_max.png", "tempo"),
    ("turnaround_medio", "Turnaround médio", "turnaround.png", "tempo"),
    ("resposta_media", "Resposta média", "resposta.png", "tempo"),
    ("makespan", "Makespan", "makespan.png", "tempo"),
    ("page_faults", "Page faults", "page_faults.png", "contagem"),
    ("trocas_contexto", "Trocas de contexto", "trocas_contexto.png", "contagem"),
    ("taxa_faults", "Taxa de page faults", "taxa_faults.png", "taxa"),
)
COR_1_CPU = "#2563eb"
COR_4_CPUS = "#059669"


def main() -> None:
    linhas = _ler_csv(PASTA / "metricas.csv")
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    for campo, titulo, arquivo, tipo in METRICAS:
        _comparar(linhas, campo, titulo, arquivo, tipo)
    _quantum(linhas)
    _speedup(linhas)
    _gantt("cpu1")
    _gantt("cpu4")
    print(f"graficos: {GRAFICOS}")


def _ler_csv(caminho: Path) -> list[dict[str, str]]:
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def _base(linhas: list[dict[str, str]], cenario: str, cpus: str) -> list[dict[str, str]]:
    achados = []
    for algoritmo_de_escalonamento, quantum, _rotulo in ROTULOS:
        for linha in linhas:
            if (
                linha["cenario"] == cenario
                and linha["sched"] == algoritmo_de_escalonamento
                and linha["quantum"] == quantum
                and linha["cpus"] == cpus
                and linha["subst"] == "lru"
            ):
                achados.append(linha)
                break
    return achados


def _comparar(
    linhas: list[dict[str, str]],
    campo: str,
    titulo: str,
    arquivo: str,
    tipo: str,
) -> None:
    fig, eixos = plt.subplots(1, 2, figsize=(13.5, 6.2), sharey=False)
    posicoes = list(range(len(ROTULOS)))
    largura = 0.38
    for eixo, cenario in zip(eixos, ("A", "B"), strict=True):
        com_1_cpu = _base(linhas, cenario, "1")
        com_4_cpus = _base(linhas, cenario, "4")
        valores_1 = [_valor(linha[campo], tipo) for linha in com_1_cpu]
        valores_4 = [_valor(linha[campo], tipo) for linha in com_4_cpus]
        barras_1 = eixo.bar(
            [p - largura / 2 for p in posicoes],
            valores_1,
            width=largura,
            color=COR_1_CPU,
            label="1 CPU",
        )
        barras_4 = eixo.bar(
            [p + largura / 2 for p in posicoes],
            valores_4,
            width=largura,
            color=COR_4_CPUS,
            label="4 CPUs",
        )
        _rotular(eixo, barras_1, valores_1, tipo)
        _rotular(eixo, barras_4, valores_4, tipo)
        eixo.set_xticks(posicoes, [rotulo for _s, _q, rotulo in ROTULOS])
        eixo.set_title(f"Cenário {cenario}")
        eixo.set_ylabel(_unidade(titulo, tipo))
        eixo.set_ylim(0, max(valores_1 + valores_4) * 1.28)
        eixo.yaxis.grid(True, linestyle=":", linewidth=0.6, alpha=0.7)
        eixo.set_axisbelow(True)
        eixo.legend()
    fig.suptitle(f"{titulo} por escalonador (LRU, 256 quadros)")
    fig.tight_layout()
    fig.savefig(GRAFICOS / arquivo, dpi=140)
    plt.close(fig)


def _valor(texto: str, tipo: str) -> float:
    numero = float(texto)
    if tipo == "taxa":
        return numero * 100
    return numero


def _unidade(titulo: str, tipo: str) -> str:
    if tipo == "taxa":
        return "Taxa de page faults (%)"
    return titulo


def _rotular(eixo: Axes, barras: BarContainer, valores: list[float], tipo: str) -> None:
    for barra, valor in zip(barras, valores, strict=True):
        eixo.annotate(
            _texto(valor, tipo),
            xy=(barra.get_x() + barra.get_width() / 2, barra.get_height()),
            xytext=(0, 2),
            textcoords="offset points",
            ha="center",
            va="bottom",
            rotation=90,
            fontsize=7,
        )


def _texto(valor: float, tipo: str) -> str:
    if tipo == "taxa":
        return f"{valor:.1f}".replace(".", ",")
    if valor < 100:
        return f"{valor:.1f}".replace(".", ",")
    return f"{valor:.0f}"


def _quantum(linhas: list[dict[str, str]]) -> None:
    fig, eixos = plt.subplots(1, 3, figsize=(13, 4.2))
    series = (("A", "1"), ("A", "4"), ("B", "1"), ("B", "4"))
    campos = ("espera_media", "resposta_media", "trocas_contexto")
    titulos = ("Espera média", "Resposta média", "Trocas de contexto")
    for eixo, campo, titulo in zip(eixos, campos, titulos, strict=True):
        for cenario, cpus in series:
            pontos = []
            for quantum in ("2", "5", "10", "20", "50"):
                for linha in linhas:
                    if (
                        linha["cenario"] == cenario
                        and linha["sched"] == "rr"
                        and linha["quantum"] == quantum
                        and linha["cpus"] == cpus
                        and linha["subst"] == "lru"
                    ):
                        pontos.append(float(linha[campo]))
                        break
            eixo.plot([2, 5, 10, 20, 50], pontos, marker="o", label=f"{cenario}, {cpus} CPU")
        eixo.set_xlabel("Quantum")
        eixo.set_title(titulo)
        eixo.legend(fontsize=8)
    fig.suptitle("Efeito do quantum no Round Robin")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "quantum.png", dpi=140)
    plt.close(fig)


def _speedup(linhas: list[dict[str, str]]) -> None:
    fig, eixos = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for eixo, cenario in zip(eixos, ("A", "B"), strict=True):
        com_4_cpus = _base(linhas, cenario, "4")
        eixo.bar(range(len(com_4_cpus)), [float(linha["speedup"]) for linha in com_4_cpus])
        eixo.axhline(4, color="gray", linestyle="--", linewidth=1, label="ideal = 4")
        eixo.set_xticks(range(len(ROTULOS)), [rotulo for _s, _q, rotulo in ROTULOS])
        eixo.set_title(f"Cenário {cenario}")
        eixo.set_ylabel("Speedup")
        eixo.legend()
    fig.suptitle("Speedup de 4 CPUs sobre 1 CPU")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "speedup.png", dpi=140)
    plt.close(fig)


def _gantt(cpu_txt: str) -> None:
    caminho = next(PASTA.glob(f"cenario_A_t0_fcfs_q-_cpu{cpu_txt[-1]}_lru_f256_t1_pf20_gantt.csv"))
    faixas: dict[int, list[tuple[int, int, str]]] = {}
    for linha in caminho.read_text(encoding="utf-8").splitlines()[1:]:
        if not linha:
            continue
        cpu_s, inicio_s, fim_s, evento = linha.split(",")
        faixas.setdefault(int(cpu_s), []).append((int(inicio_s), int(fim_s), evento))
    fig, eixo = plt.subplots(figsize=(12, 1.6 + 0.7 * len(faixas)))
    for cpu, intervalos in faixas.items():
        for inicio, fim, evento in intervalos:
            eixo.barh(
                cpu,
                fim - inicio,
                left=inicio,
                height=0.55,
                color=_cor(evento),
                edgecolor="black",
                linewidth=0.2,
            )
            if fim - inicio >= 10 and evento not in {"TROCA", "OCIOSA"}:
                eixo.text((inicio + fim) / 2, cpu, evento, ha="center", va="center", fontsize=7)
    eixo.set_yticks(list(faixas), [f"CPU {cpu}" for cpu in faixas])
    eixo.set_xlim(0, 200)
    eixo.set_xlabel("Tempo")
    eixo.set_title(f"Gantt 0–200, cenário A, FCFS, LRU, {len(faixas)} CPU")
    eixo.legend(
        handles=[
            Patch(facecolor="#d97706", edgecolor="black", label="TROCA"),
            Patch(facecolor="#e5e7eb", edgecolor="black", label="OCIOSA"),
            Patch(facecolor="#2563eb", edgecolor="black", label="execução"),
        ],
        loc="upper right",
    )
    fig.tight_layout()
    fig.savefig(GRAFICOS / f"gantt_A_fcfs_{cpu_txt}.png", dpi=140)
    plt.close(fig)


def _cor(evento: str) -> str:
    if evento == "TROCA":
        return "#d97706"
    if evento == "OCIOSA":
        return "#e5e7eb"
    paleta = ("#2563eb", "#059669", "#7c3aed", "#db2777", "#0891b2", "#ca8a04", "#4f46e5")
    pid = int(evento[1:])
    return paleta[pid % len(paleta)]


if __name__ == "__main__":
    main()
