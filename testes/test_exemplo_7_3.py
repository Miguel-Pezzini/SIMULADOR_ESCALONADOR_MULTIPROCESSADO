from pathlib import Path

import pytest
from testes.suporte import fecha_makespan, por_pid, rodar


def test_fcfs_fila_depois_dos_faults(fixtures: Path) -> None:
    resultado = rodar(
        fixtures / "exemplo_7_3.json",
        custo_troca=0,
        tempo_fault=20,
        quadros=8,
    )
    assert resultado.makespan == 29
    assert por_pid(resultado) == {1: 0, 2: 4, 3: 7}
    assert resultado.espera_media() == pytest.approx(11 / 3)
    assert resultado.page_faults == 3
    assert resultado.cpus[0].tempo_util == 9
    fecha_makespan(resultado)


def test_sjf_escolhe_o_burst_restante(fixtures: Path) -> None:
    resultado = rodar(
        fixtures / "exemplo_7_3.json",
        sched="sjf",
        custo_troca=0,
        tempo_fault=20,
        quadros=8,
    )
    assert resultado.makespan == 29
    assert por_pid(resultado) == {1: 5, 2: 2, 3: 0}
    assert resultado.espera_media() == pytest.approx(7 / 3)
    assert {p.pid: p.turnaround for p in resultado.processos} == {1: 29, 2: 25, 3: 22}
    fecha_makespan(resultado)
