from pathlib import Path

import pytest
from testes.suporte import fecha_makespan, por_pid, rodar

from simulador.cli import main
from simulador.saida import gravar, recortar_gantt


def test_fcfs_sem_memoria(fixtures: Path) -> None:
    resultado = rodar(fixtures / "exemplo_7_1.json", ignorar_memoria=True, custo_troca=1)
    assert resultado.makespan == 13
    assert por_pid(resultado) == {1: 0, 2: 6, 3: 8}
    assert {p.pid: p.turnaround for p in resultado.processos} == {1: 6, 2: 10, 3: 11}
    assert {p.pid: p.resposta for p in resultado.processos} == {1: 0, 2: 6, 3: 8}
    assert resultado.espera_media() == pytest.approx(14 / 3)
    assert resultado.turnaround_medio() == pytest.approx(9)
    cpu = resultado.cpus[0]
    assert (cpu.tempo_util, cpu.tempo_troca, cpu.tempo_ocioso, cpu.trocas) == (10, 3, 0, 3)
    assert cpu.gantt == [
        (0, 1, "TROCA"),
        (1, 6, "P1"),
        (6, 7, "TROCA"),
        (7, 10, "P2"),
        (10, 11, "TROCA"),
        (11, 13, "P3"),
    ]
    fecha_makespan(resultado)


def test_sjf_sem_memoria(fixtures: Path) -> None:
    resultado = rodar(
        fixtures / "exemplo_7_1.json",
        sched="sjf",
        ignorar_memoria=True,
        custo_troca=1,
    )
    assert resultado.makespan == 13
    assert por_pid(resultado) == {1: 7, 2: 0, 3: 2}
    assert {p.pid: p.turnaround for p in resultado.processos} == {1: 13, 2: 4, 3: 5}
    assert resultado.cpus[0].trocas == 3
    fecha_makespan(resultado)


def test_cli_grava_gantt_e_resumo(
    fixtures: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    codigo = main(
        [
            "--arquivo",
            str(fixtures / "exemplo_7_1.json"),
            "--cpus",
            "1",
            "--sched",
            "fcfs",
            "--subst",
            "lru",
            "--custo-troca",
            "1",
            "--ignorar-memoria",
            "--saida",
            str(tmp_path),
        ]
    )
    assert codigo == 0
    saida = capsys.readouterr().out
    assert "makespan: 13" in saida
    assert "espera_media: 4.67" in saida
    assert "trocas_contexto: 3" in saida
    gantts = list(tmp_path.glob("*_gantt.csv"))
    assert len(gantts) == 1
    texto = gantts[0].read_text(encoding="utf-8")
    assert texto.splitlines()[1] == "0,0,1,TROCA"
    assert "0,1,6,P1" in texto


def test_recorta_gantt_na_janela() -> None:
    recorte = recortar_gantt(
        [(0, 50, "P1"), (150, 250, "OCIOSA"), (200, 240, "P2"), (-4, 3, "TROCA")]
    )
    assert recorte == [(0, 50, "P1"), (150, 200, "OCIOSA"), (0, 3, "TROCA")]


def test_gravar_json_de_metricas(fixtures: Path, tmp_path: Path) -> None:
    resultado = rodar(fixtures / "exemplo_7_1.json", ignorar_memoria=True)
    _, metricas = gravar(resultado, tmp_path)
    assert metricas.exists()
    assert "makespan" in metricas.read_text(encoding="utf-8")
