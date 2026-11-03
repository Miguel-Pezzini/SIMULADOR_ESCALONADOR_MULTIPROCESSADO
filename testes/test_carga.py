from pathlib import Path

import pytest
from testes.suporte import burst_de_cpu, gravar_carga, processo

from simulador.carga import carregar_processos


def test_carrega_cenario_pequeno(fixtures: Path) -> None:
    processos = carregar_processos(fixtures / "exemplo_7_1.json")
    assert [p.pid for p in processos] == [1, 2, 3]
    assert processos[2].chegada == 2
    assert processos[0].unidades_de_cpu_restantes_no_burst() == 5


def test_rejeita_pid_duplicado(tmp_path: Path) -> None:
    caminho = tmp_path / "dup.json"
    gravar_carga(
        caminho,
        [processo(1, 0, [burst_de_cpu(1)]), processo(1, 0, [burst_de_cpu(1)])],
    )
    with pytest.raises(ValueError, match="duplicado"):
        carregar_processos(caminho)


def test_rejeita_refs_curtas(tmp_path: Path) -> None:
    caminho = tmp_path / "refs.json"
    gravar_carga(caminho, [processo(1, 0, [burst_de_cpu(2, paginas_referenciadas=[0])])])
    with pytest.raises(ValueError, match="refs"):
        carregar_processos(caminho)


def test_rejeita_arquivo_ausente(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="não encontrado"):
        carregar_processos(tmp_path / "nao_existe.json")


def test_rejeita_json_quebrado(tmp_path: Path) -> None:
    caminho = tmp_path / "quebrado.json"
    caminho.write_text("{", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON inválido"):
        carregar_processos(caminho)
