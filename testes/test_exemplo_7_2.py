from pathlib import Path

from testes.suporte import conferir_se_os_tempos_das_cpus_fecham_o_makespan, espera_por_pid, rodar

from simulador.saida import recortar_gantt


def test_faults_nao_entram_na_espera(fixtures: Path) -> None:
    resultado = rodar(
        fixtures / "exemplo_7_2.json",
        custo_troca=0,
        tempo_fault=5,
        quadros=16,
    )
    assert resultado.makespan == 13
    assert espera_por_pid(resultado) == {1: 0, 2: 0, 3: 0}
    assert {p.pid: p.turnaround for p in resultado.processos} == {1: 12, 2: 12, 3: 6}
    assert resultado.page_faults == 5
    assert resultado.acertos == 5
    cpu = resultado.cpus[0]
    assert (cpu.tempo_util, cpu.tempo_troca, cpu.tempo_ocioso) == (5, 0, 8)
    assert recortar_gantt(cpu.gantt) == [
        (0, 5, "OCIOSA"),
        (5, 6, "P1"),
        (6, 7, "P2"),
        (7, 8, "P3"),
        (8, 11, "OCIOSA"),
        (11, 12, "P1"),
        (12, 13, "P2"),
    ]
    conferir_se_os_tempos_das_cpus_fecham_o_makespan(resultado)
