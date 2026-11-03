from pathlib import Path

import pytest
from testes.suporte import conferir_se_os_tempos_das_cpus_fecham_o_makespan, espera_por_pid, rodar


def test_fcfs_fila_depois_dos_faults(fixtures: Path) -> None:
    resultado = rodar(
        fixtures / "exemplo_7_3.json",
        custo_troca=0,
        tempo_fault=20,
        quadros=8,
    )
    assert resultado.makespan == 29
    assert espera_por_pid(resultado) == {1: 0, 2: 4, 3: 7}
    assert resultado.espera_media() == pytest.approx(11 / 3)
    assert resultado.page_faults == 3
    assert resultado.cpus[0].tempo_util == 9
    conferir_se_os_tempos_das_cpus_fecham_o_makespan(resultado)


def test_sjf_escolhe_o_burst_restante(fixtures: Path) -> None:
    resultado = rodar(
        fixtures / "exemplo_7_3.json",
        algoritmo_de_escalonamento="sjf",
        custo_troca=0,
        tempo_fault=20,
        quadros=8,
    )
    assert resultado.makespan == 29
    assert espera_por_pid(resultado) == {1: 5, 2: 2, 3: 0}
    assert resultado.espera_media() == pytest.approx(7 / 3)
    assert {p.pid: p.turnaround for p in resultado.processos} == {1: 29, 2: 25, 3: 22}
    conferir_se_os_tempos_das_cpus_fecham_o_makespan(resultado)
