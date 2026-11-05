from pathlib import Path

import pytest
from testes.suporte import (
    burst_de_cpu,
    burst_de_entrada_saida,
    conferir_se_os_tempos_das_cpus_fecham_o_makespan,
    gravar_carga,
    processo,
    rodar,
)

from simulador.cli import main
from simulador.saida import gravar_gantt_e_metricas


def test_rr_quantum_2_no_exemplo_sem_memoria(fixtures: Path) -> None:
    resultado = rodar(
        fixtures / "exemplo_7_1.json",
        algoritmo_de_escalonamento="rr",
        quantum=2,
        ignorar_memoria=True,
        custo_troca=1,
    )
    assert resultado.makespan == 16
    assert {p.pid: p.espera for p in resultado.processos} == {1: 8, 2: 9, 3: 4}
    assert {p.pid: p.resposta for p in resultado.processos} == {1: 0, 2: 3, 3: 4}
    assert {p.pid: p.turnaround for p in resultado.processos} == {1: 16, 2: 14, 3: 7}
    assert resultado.cpus[0].trocas == 6
    assert resultado.cpus[0].tempo_util == 10
    conferir_se_os_tempos_das_cpus_fecham_o_makespan(resultado)


def test_quantum_no_fim_com_fila_vazia_nao_cobra_troca(tmp_path: Path) -> None:
    caminho = tmp_path / "sozinho.json"
    gravar_carga(caminho, [processo(1, 0, [burst_de_cpu(5)])])
    resultado = rodar(
        caminho,
        algoritmo_de_escalonamento="rr",
        quantum=2,
        ignorar_memoria=True,
        custo_troca=1,
    )
    assert resultado.makespan == 6
    assert resultado.total_de_trocas_de_contexto() == 1
    assert resultado.cpus[0].tempo_util == 5
    assert resultado.cpus[0].tempo_troca == 1
    conferir_se_os_tempos_das_cpus_fecham_o_makespan(resultado)


def test_preempcao_ocorre_depois_da_chegada_no_mesmo_instante(tmp_path: Path) -> None:
    caminho = tmp_path / "ordem.json"
    gravar_carga(
        caminho,
        [
            processo(1, 0, [burst_de_cpu(4)]),
            processo(2, 2, [burst_de_cpu(2)]),
        ],
    )
    resultado = rodar(
        caminho,
        algoritmo_de_escalonamento="rr",
        quantum=2,
        ignorar_memoria=True,
        custo_troca=0,
    )
    termino = {p.pid: p.termino for p in resultado.processos}
    assert termino == {2: 4, 1: 6}
    conferir_se_os_tempos_das_cpus_fecham_o_makespan(resultado)


def test_retorno_de_es_na_mesma_cpu_ociosa_nao_cobra_troca(tmp_path: Path) -> None:
    caminho = tmp_path / "io.json"
    gravar_carga(
        caminho,
        [processo(1, 0, [burst_de_cpu(1), burst_de_entrada_saida(5), burst_de_cpu(1)])],
    )
    resultado = rodar(caminho, ignorar_memoria=True, custo_troca=1)
    assert resultado.makespan == 8
    assert resultado.total_de_trocas_de_contexto() == 1
    assert resultado.cpus[0].tempo_util == 2
    assert resultado.cpus[0].tempo_ocioso == 5
    conferir_se_os_tempos_das_cpus_fecham_o_makespan(resultado)


def test_chegada_e_retorno_no_mesmo_instante_entram_por_pid(tmp_path: Path) -> None:
    caminho = tmp_path / "pid.json"
    gravar_carga(
        caminho,
        [
            processo(3, 0, [burst_de_cpu(1), burst_de_entrada_saida(4), burst_de_cpu(1)]),
            processo(1, 5, [burst_de_cpu(1)]),
            processo(2, 5, [burst_de_cpu(1)], classe="longo"),
        ],
    )
    resultado = rodar(caminho, ignorar_memoria=True, custo_troca=0)
    termino = {p.pid: p.termino for p in resultado.processos}
    assert termino[1] == 6
    assert termino[2] == 7
    assert termino[3] == 8
    conferir_se_os_tempos_das_cpus_fecham_o_makespan(resultado)


def test_quatro_cpus_e_speedup(tmp_path: Path) -> None:
    caminho = tmp_path / "quatro.json"
    gravar_carga(caminho, [processo(pid, 0, [burst_de_cpu(5)]) for pid in range(1, 5)])
    uma = rodar(caminho, cpus=1, ignorar_memoria=True, custo_troca=1)
    _, metricas = gravar_gantt_e_metricas(uma, tmp_path)
    quatro = rodar(
        caminho,
        cpus=4,
        ignorar_memoria=True,
        custo_troca=1,
        arquivo_de_metricas_com_1_cpu=str(metricas),
    )
    assert uma.makespan == 24
    assert quatro.makespan == 6
    assert quatro.speedup == pytest.approx(4)
    assert quatro.eficiencia == pytest.approx(1)
    for nucleo in quatro.cpus:
        assert (nucleo.tempo_util, nucleo.tempo_troca, nucleo.tempo_ocioso) == (5, 1, 0)
    conferir_se_os_tempos_das_cpus_fecham_o_makespan(quatro)


def test_cli_rejeita_rr_sem_quantum(fixtures: Path, capsys: pytest.CaptureFixture[str]) -> None:
    codigo = main(
        [
            "--arquivo",
            str(fixtures / "exemplo_7_1.json"),
            "--cpus",
            "1",
            "--sched",
            "rr",
            "--subst",
            "fifo",
            "--ignorar-memoria",
            "--saida",
            "resultados",
        ]
    )
    assert codigo == 2
    assert "quantum" in capsys.readouterr().err
