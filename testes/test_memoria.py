from pathlib import Path

from testes.suporte import burst_de_cpu, gravar_carga, processo, rodar

from simulador.memoria import Acesso, Memoria


def _carregar_e_acertar(memoria: Memoria, pid: int, pagina: int) -> None:
    assert memoria.acessar_pagina(pid, pagina) is Acesso.PAGINA_CARREGADA
    memoria.liberar_paginas_em_uso_por_uma_cpu()
    assert memoria.acessar_pagina(pid, pagina) is Acesso.ACERTO
    memoria.liberar_paginas_em_uso_por_uma_cpu()


def test_fifo_escolhe_a_pagina_mais_antiga() -> None:
    memoria = Memoria(3, "fifo")
    for pagina in (0, 1, 2):
        _carregar_e_acertar(memoria, 1, pagina)
    assert memoria.acessar_pagina(1, 0) is Acesso.ACERTO
    memoria.liberar_paginas_em_uso_por_uma_cpu()
    assert memoria.acessar_pagina(1, 1) is Acesso.ACERTO
    memoria.liberar_paginas_em_uso_por_uma_cpu()
    assert memoria.acessar_pagina(1, 3) is Acesso.PAGINA_CARREGADA
    assert not memoria.pagina_esta_carregada(1, 0)
    assert memoria.pagina_esta_carregada(1, 1)
    assert memoria.pagina_esta_carregada(1, 2)
    assert memoria.pagina_esta_carregada(1, 3)


def test_lru_escolhe_a_referencia_mais_antiga() -> None:
    memoria = Memoria(3, "lru")
    for pagina in (0, 1, 2):
        _carregar_e_acertar(memoria, 1, pagina)
    assert memoria.acessar_pagina(1, 0) is Acesso.ACERTO
    memoria.liberar_paginas_em_uso_por_uma_cpu()
    assert memoria.acessar_pagina(1, 1) is Acesso.ACERTO
    memoria.liberar_paginas_em_uso_por_uma_cpu()
    assert memoria.acessar_pagina(1, 3) is Acesso.PAGINA_CARREGADA
    assert memoria.pagina_esta_carregada(1, 0)
    assert memoria.pagina_esta_carregada(1, 1)
    assert not memoria.pagina_esta_carregada(1, 2)
    assert memoria.pagina_esta_carregada(1, 3)


def test_pagina_protegida_nao_e_vitima_e_em_uso_tambem_nao() -> None:
    memoria = Memoria(1, "lru")
    assert memoria.acessar_pagina(1, 0) is Acesso.PAGINA_CARREGADA
    assert memoria.acessar_pagina(2, 0) is Acesso.SEM_QUADRO_DISPONIVEL
    assert memoria.pagina_esta_carregada(1, 0)

    assert memoria.acessar_pagina(1, 0) is Acesso.ACERTO
    assert memoria.acessar_pagina(2, 0) is Acesso.SEM_QUADRO_DISPONIVEL
    memoria.liberar_paginas_em_uso_por_uma_cpu()
    assert memoria.acessar_pagina(2, 0) is Acesso.PAGINA_CARREGADA
    assert not memoria.pagina_esta_carregada(1, 0)

    memoria.liberar_quadros_do_processo(2)
    assert memoria.quantidade_de_quadros_ocupados() == 0
    assert memoria.acessar_pagina(1, 0) is Acesso.PAGINA_CARREGADA


def test_sem_vitima_conta_o_fault_uma_vez(tmp_path: Path) -> None:
    caminho = tmp_path / "apertado.json"
    gravar_carga(
        caminho,
        [processo(1, 0, [burst_de_cpu(1)]), processo(2, 0, [burst_de_cpu(1)])],
    )
    resultado = rodar(caminho, cpus=4, quadros=1, custo_troca=0, tempo_fault=20)
    assert resultado.page_faults == 2
    assert resultado.makespan == 61


def test_paginas_de_pids_diferentes_nao_se_confundem() -> None:
    memoria = Memoria(2, "fifo")
    assert memoria.acessar_pagina(1, 0) is Acesso.PAGINA_CARREGADA
    assert memoria.acessar_pagina(2, 0) is Acesso.PAGINA_CARREGADA
    assert memoria.pagina_esta_carregada(1, 0)
    assert memoria.pagina_esta_carregada(2, 0)
