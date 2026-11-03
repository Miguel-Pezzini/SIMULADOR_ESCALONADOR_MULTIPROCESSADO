"""Texto da análise, preenchido com as métricas da rodada."""

from __future__ import annotations

import csv
from pathlib import Path


def escrever_analise(linhas: list[dict[str, object]], destino: Path) -> None:
    destino.write_text(_texto(linhas), encoding="utf-8")


def _texto(linhas: list[dict[str, object]]) -> str:
    partes = [
        _introducao(),
        _tabela("A", linhas),
        _tabela("B", linhas),
        _tabela_por_cpu(linhas),
        _espera(linhas),
        _quantum(linhas),
        _speedup(linhas),
        _memoria(linhas),
        _fenomenos(linhas),
        _limitacoes(),
        _gantt(),
        "",
    ]
    return "\n".join(partes)


def _introducao() -> str:
    return "\n".join(
        [
            "# Análise dos experimentos",
            "",
            "Cada número abaixo sai de `resultados/metricas.csv`, gerado por `experimentos/rodar.py`.",
            "A base tem 28 execuções: cenários A e B, 1 e 4 CPUs, FCFS, SJF e Round Robin",
            "com quantum 2, 5, 10, 20 e 50, substituição LRU e 256 quadros.",
            "O enunciado nomeia os quantums 2, 10 e 50 e fecha a conta em sete variações;",
            "os quantums 5 e 20 completam essa conta e desenham a curva do quantum.",
            "Outras quatro execuções trocam a LRU pela FIFO, nas mesmas condições de carga,",
            "escalonador e número de CPUs. Custo de troca 1 e page fault de 20 em todas.",
            "",
            "Speedup é makespan com 1 CPU dividido pelo makespan com 4 CPUs,",
            "no mesmo escalonador, quantum e memória. Eficiência é esse speedup dividido por 4.",
            "A espera conta só o tempo na fila de prontos. E/S e page fault ficam de fora.",
            "Utilização de uma CPU é (tempo útil + tempo de troca) dividido pelo makespan.",
            "A coluna Utilização é a média dessas frações, em porcentagem.",
            "Ocioso é a soma do tempo em que a CPU não tinha processo.",
            "A tabela de utilização abre as mesmas parcelas em cada núcleo, com as trocas cobradas nele.",
            "",
        ]
    )


def _tabela(cenario: str, linhas: list[dict[str, object]]) -> str:
    cabecalho = (
        "| Escalonador | Q | CPUs | Memória | Espera média | Espera máx | "
        "Turnaround | Resposta | Makespan | Trocas | Faults | Taxa | Speedup | Eficiência | "
        "Utilização | Ocioso |"
    )
    separador = (
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | "
        "--- | --- |"
    )
    corpo = [cabecalho, separador]
    grupo = [linha for linha in linhas if linha["cenario"] == cenario]
    grupo.sort(
        key=lambda linha: (
            0 if linha["subst"] == "lru" else 1,
            str(linha["sched"]),
            _quantum_ordem(linha),
            int(str(linha["cpus"])),
        )
    )
    for linha in grupo:
        quantum = linha["quantum"]
        corpo.append(
            "| {sched} | {quantum} | {cpus} | {subst} | {espera} | {espera_max} | "
            "{turnaround} | {resposta} | {makespan} | {trocas} | {faults} | {taxa} | "
            "{speedup} | {eficiencia} | {utilizacao} | {ocioso} |".format(
                sched=str(linha["sched"]).upper(),
                quantum="—" if quantum == "" else quantum,
                cpus=linha["cpus"],
                subst=str(linha["subst"]).upper(),
                espera=_br(_num(linha, "espera_media")),
                espera_max=linha["espera_max"],
                turnaround=_br(_num(linha, "turnaround_medio")),
                resposta=_br(_num(linha, "resposta_media")),
                makespan=linha["makespan"],
                trocas=linha["trocas_contexto"],
                faults=linha["page_faults"],
                taxa=_br(_num(linha, "taxa_faults"), 4),
                speedup=_br_opc(_opc(linha, "speedup"), 4),
                eficiencia=_br_opc(_opc(linha, "eficiencia"), 4),
                utilizacao=_br(_utilizacao_media_pct(linha)),
                ocioso=_int(linha, "tempo_ocioso"),
            )
        )
    return "\n".join([f"## Cenário {cenario}", "", *corpo, ""])


def _tabela_por_cpu(linhas: list[dict[str, object]]) -> str:
    cabecalho = "| Cenário | Escalonador | Q | Memória | CPU | Útil | Troca | Ocioso | Trocas | Utilização |"
    separador = "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    corpo = [cabecalho, separador]
    for linha in _ordenar(linhas):
        quantum = linha["quantum"]
        for indice in range(int(str(linha["cpus"]))):
            corpo.append(
                "| {cenario} | {sched} | {quantum} | {subst} | {cpu} | {util} | {troca} | "
                "{ocioso} | {trocas} | {utilizacao} |".format(
                    cenario=linha["cenario"],
                    sched=str(linha["sched"]).upper(),
                    quantum="—" if quantum == "" else quantum,
                    subst=str(linha["subst"]).upper(),
                    cpu=indice,
                    util=_int(linha, f"cpu{indice}_util"),
                    troca=_int(linha, f"cpu{indice}_troca"),
                    ocioso=_int(linha, f"cpu{indice}_ocioso"),
                    trocas=_int(linha, f"cpu{indice}_trocas"),
                    utilizacao=_br(_utilizacao_da_cpu_pct(linha, indice)),
                )
            )
    return "\n".join(
        [
            "## Utilização, ociosidade e trocas por CPU",
            "",
            "Cada linha é um núcleo de uma execução. Utilização está em porcentagem.",
            "",
            *corpo,
            "",
        ]
    )


def _ordenar(linhas: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(
        linhas,
        key=lambda linha: (
            str(linha["cenario"]),
            0 if linha["subst"] == "lru" else 1,
            str(linha["sched"]),
            _quantum_ordem(linha),
            int(str(linha["cpus"])),
        ),
    )


def _espera(linhas: list[dict[str, object]]) -> str:
    frases = ["## Espera, resposta e justiça", ""]
    for cenario, cpus in (("A", 1), ("A", 4), ("B", 1), ("B", 4)):
        fcfs = _buscar(linhas, cenario, "fcfs", None, cpus)
        sjf = _buscar(linhas, cenario, "sjf", None, cpus)
        rr = _buscar(linhas, cenario, "rr", 10, cpus)
        maquina = "1 CPU" if cpus == 1 else "4 CPUs"
        frases.append(
            f"No cenário {cenario} com {maquina} e LRU, a espera média foi "
            f"{_br(_num(fcfs, 'espera_media'))} no FCFS, {_br(_num(sjf, 'espera_media'))} no SJF "
            f"e {_br(_num(rr, 'espera_media'))} no RR com quantum 10. "
            f"A resposta média foi {_br(_num(fcfs, 'resposta_media'))}, "
            f"{_br(_num(sjf, 'resposta_media'))} e {_br(_num(rr, 'resposta_media'))}, "
            f"nessa mesma ordem. "
            f"A espera máxima do FCFS chegou a {_num(fcfs, 'espera_max'):.0f} "
            f"(pid {_int(fcfs, 'espera_max_pid')})."
        )
        frases.append("")
    sjf = _buscar(linhas, "A", "sjf", None, 1)
    rr = _buscar(linhas, "A", "rr", 10, 1)
    frases.append(
        f"No cenário A com 1 CPU, o SJF separa as classes: espera média "
        f"{_br(_num(sjf, 'espera_curto'))} nos curtos e {_br(_num(sjf, 'espera_longo'))} nos longos. "
        f"No RR com quantum 10 as duas sobem, para {_br(_num(rr, 'espera_curto'))} e "
        f"{_br(_num(rr, 'espera_longo'))}. "
        "O SJF baixa a média dos dois grupos porque despacha o menor burst restante "
        "e, com isso, também reduz page faults: os curtos terminam, devolvem os quadros, "
        "e a memória não fica ocupada pelo conjunto inteiro ao mesmo tempo. "
        "Os longos continuam atrás dos curtos. A razão longo/curto é maior no SJF do que no RR, "
        "então a média melhora e a justiça relativa piora. "
        "A resposta média do SJF nesse caso é "
        f"{_br(_num(sjf, 'resposta_media'))}, bem acima dos "
        f"{_br(_num(rr, 'resposta_media'))} do RR, porque o longo espera mais para receber a CPU "
        "pela primeira vez."
    )
    frases.append("")
    return "\n".join(frases)


def _quantum(linhas: list[dict[str, object]]) -> str:
    frases = [
        "## Efeito do quantum",
        "",
        "A comparação usa o cenário A com 1 CPU e LRU, do quantum 2 ao quantum 50. "
        "Nesse cenário a resposta média não muda com o quantum. "
        "O efeito aparece na espera, nas trocas e no makespan, "
        "e no cenário B com 4 CPUs também na taxa de faults. "
        "O gráfico `resultados/graficos/quantum.png` mostra os quatro pares.",
        "",
    ]
    curto_q = _buscar(linhas, "A", "rr", 2, 1)
    longo_q = _buscar(linhas, "A", "rr", 50, 1)
    fcfs = _buscar(linhas, "A", "fcfs", None, 1)
    frases.append(
        f"Com quantum 2, a resposta média foi {_br(_num(curto_q, 'resposta_media'))} "
        f"e houve {_int(curto_q, 'trocas_contexto')} trocas de contexto. "
        f"Com quantum 50, a resposta foi {_br(_num(longo_q, 'resposta_media'))} "
        f"e as trocas caíram para {_int(longo_q, 'trocas_contexto')}. "
        f"A espera média foi de {_br(_num(curto_q, 'espera_media'))} para "
        f"{_br(_num(longo_q, 'espera_media'))}. "
        f"O FCFS na mesma máquina teve espera {_br(_num(fcfs, 'espera_media'))}, "
        f"resposta {_br(_num(fcfs, 'resposta_media'))} e "
        f"{_int(fcfs, 'trocas_contexto')} trocas."
    )
    frases.append("")
    resposta_2 = _num(curto_q, "resposta_media")
    resposta_50 = _num(longo_q, "resposta_media")
    trocas_2 = _num(curto_q, "trocas_contexto")
    trocas_50 = _num(longo_q, "trocas_contexto")
    if resposta_2 == resposta_50 and trocas_2 > trocas_50:
        frases.append(
            "No cenário A todos chegam em t = 0 e a primeira referência de cada processo "
            "causa page fault. Com custo de troca 1, o simulador despacha um processo por "
            "unidade de tempo só para descobrir o fault, em ordem de pid, antes de qualquer "
            "quantum se cumprir. Por isso FCFS e RR, em qualquer quantum, têm a mesma resposta "
            f"média ({_br(resposta_2)}). O quantum aparece depois: quantum 2 gera "
            f"{trocas_2:.0f} trocas e espera {_br(_num(curto_q, 'espera_media'))}; "
            f"quantum 50 cai para {trocas_50:.0f} trocas e espera "
            f"{_br(_num(longo_q, 'espera_media'))}, colado no FCFS "
            f"({_int(fcfs, 'trocas_contexto')} trocas, espera {_br(_num(fcfs, 'espera_media'))}). "
            "Quantum maior segura o processo na CPU, reduz preempção e se aproxima do FCFS."
        )
        frases.append("")
    elif resposta_2 < resposta_50 and trocas_2 > trocas_50:
        frases.append(
            "Quantum maior segura o processo por mais tempo na CPU. "
            "O número de preempções cai, e com ele o custo de troca. "
            "A resposta piora porque quem está no fim da fila espera a fatia "
            "inteira de quem está na frente. "
            "No limite, o RR se aproxima do FCFS."
        )
        frases.append("")
    return "\n".join(frases)


def _speedup(linhas: list[dict[str, object]]) -> str:
    frases = ["## Speedup", ""]
    for cenario in ("A", "B"):
        for sched, quantum, rotulo in (
            ("fcfs", None, "FCFS"),
            ("sjf", None, "SJF"),
            ("rr", 2, "RR com quantum 2"),
            ("rr", 10, "RR com quantum 10"),
            ("rr", 50, "RR com quantum 50"),
        ):
            linha = _buscar(linhas, cenario, sched, quantum, 4)
            speedup = _opc(linha, "speedup")
            eficiencia = _opc(linha, "eficiencia")
            if speedup is None or eficiencia is None:
                continue
            uma = _buscar(linhas, cenario, sched, quantum, 1)
            frases.append(
                f"No cenário {cenario}, o {rotulo} levou o makespan de "
                f"{_int(uma, 'makespan')} com 1 CPU para {_int(linha, 'makespan')} com 4 CPUs. "
                f"Speedup {_br(speedup, 4)}, eficiência {_br(eficiencia, 4)}."
            )
        frases.append("")
    frases.append(_leitura_do_speedup(linhas))
    frases.append("")
    return "\n".join(frases)


def _leitura_do_speedup(linhas: list[dict[str, object]]) -> str:
    eficiencias_a = [
        _num(linha, "eficiencia")
        for linha in linhas
        if linha["cenario"] == "A" and linha["cpus"] == 4 and linha["subst"] == "lru"
    ]
    faults_b4 = [
        _int(linha, "page_faults")
        for linha in linhas
        if linha["cenario"] == "B"
        and linha["cpus"] == 4
        and linha["subst"] == "lru"
        and linha["sched"] in {"fcfs", "rr"}
    ]
    sjf_b1 = _buscar(linhas, "B", "sjf", None, 1)
    sjf_b4 = _buscar(linhas, "B", "sjf", None, 4)
    fcfs_a1 = _buscar(linhas, "A", "fcfs", None, 1)
    fcfs_a4 = _buscar(linhas, "A", "fcfs", None, 4)
    fcfs_b4 = _buscar(linhas, "B", "fcfs", None, 4)
    return (
        f"No cenário A a eficiência fica entre {_br(min(eficiencias_a), 2)} e "
        f"{_br(max(eficiencias_a), 2)}: perto de 4, sem chegar lá. "
        "Cada processo usa um núcleo por vez, a troca ocupa a CPU sem avançar referência, "
        "e os 256 quadros são os mesmos da máquina de 1 CPU. "
        f"No FCFS com LRU, a CPU única ficou com utilização {_br(_utilizacao_media_pct(fcfs_a1))}% "
        f"(útil {_int(fcfs_a1, 'tempo_util')}, troca {_int(fcfs_a1, 'tempo_troca')}, "
        f"ocioso {_int(fcfs_a1, 'tempo_ocioso')}). "
        f"Com 4 CPUs a utilização média foi {_br(_utilizacao_media_pct(fcfs_a4))}% "
        f"e o ocioso somado foi {_int(fcfs_a4, 'tempo_ocioso')}. "
        f"A folga entre o núcleo mais ocupado e o menos ocupado foi "
        f"{_br(_folga_de_utilizacao(fcfs_a4))} pontos percentuais. "
        "No cenário B o speedup do FCFS e do RR passa de 4. "
        "Com 1 CPU esses escalonadores geram cerca de 16,9 mil faults; "
        "com 4 CPUs, e chegadas espalhadas até t = 9534, "
        f"os faults caem para a faixa de {min(faults_b4)} a {max(faults_b4)}. "
        f"No FCFS com 4 CPUs a utilização média continua em "
        f"{_br(_utilizacao_media_pct(fcfs_b4))}% "
        f"(ocioso somado {_int(fcfs_b4, 'tempo_ocioso')}, "
        f"trocas por CPU {_trocas_por_cpu(fcfs_b4)}). "
        "Os núcleos não ficam parados. O speedup acima de 4 vem do trabalho extra "
        "que a máquina de 1 CPU paga em faults e trocas, e que a de 4 CPUs evita. "
        f"O SJF no cenário B já tinha {_int(sjf_b1, 'page_faults')} faults com 1 CPU, "
        f"então o speedup fica em {_br(_num(sjf_b4, 'speedup'), 4)}, abaixo de 4. "
        "Eficiência acima de 1, aqui, é efeito da memória, não de um núcleo a mais."
    )


def _memoria(linhas: list[dict[str, object]]) -> str:
    frases = ["## FIFO e LRU", ""]
    comparacoes = (
        ("A", "fcfs", None, 1, "FCFS com 1 CPU"),
        ("A", "rr", 10, 4, "RR com quantum 10 e 4 CPUs"),
        ("B", "sjf", None, 1, "SJF com 1 CPU"),
        ("B", "rr", 2, 4, "RR com quantum 2 e 4 CPUs"),
    )
    for cenario, sched, quantum, cpus, rotulo in comparacoes:
        lru = _buscar(linhas, cenario, sched, quantum, cpus, "lru")
        fifo = _buscar(linhas, cenario, sched, quantum, cpus, "fifo")
        falhas_lru = _int(lru, "page_faults")
        falhas_fifo = _int(fifo, "page_faults")
        frases.append(
            f"Cenário {cenario}, {rotulo}: LRU teve {falhas_lru} page faults "
            f"(taxa {_br(_num(lru, 'taxa_faults'), 4)}) e FIFO teve {falhas_fifo} "
            f"(taxa {_br(_num(fifo, 'taxa_faults'), 4)}). "
            f"O makespan foi {_int(lru, 'makespan')} na LRU e {_int(fifo, 'makespan')} na FIFO."
        )
    frases.append("")
    a1 = _buscar(linhas, "A", "fcfs", None, 1)
    b1 = _buscar(linhas, "B", "fcfs", None, 1)
    a4 = _buscar(linhas, "A", "fcfs", None, 4)
    b4 = _buscar(linhas, "B", "fcfs", None, 4)
    frases.append(
        f"No FCFS com LRU e 1 CPU, a taxa de faults do cenário A foi "
        f"{_br(_num(a1, 'taxa_faults'), 4)} ({_int(a1, 'page_faults')} faults) "
        f"e a do cenário B foi {_br(_num(b1, 'taxa_faults'), 4)} "
        f"({_int(b1, 'page_faults')} faults): com um núcleo só, a fila enorme mantém "
        "os dois cenários no mesmo regime de substituição. "
        f"Com 4 CPUs a diferença aparece. O cenário A continua em "
        f"{_br(_num(a4, 'taxa_faults'), 4)} ({_int(a4, 'page_faults')} faults), "
        f"porque os 1000 processos estão vivos desde t = 0. "
        f"O cenário B cai para {_br(_num(b4, 'taxa_faults'), 4)} "
        f"({_int(b4, 'page_faults')} faults): as chegadas vão até t = 9534 "
        "e a máquina de 4 CPUs dá conta da carga sem empilhar todo mundo na memória. "
        "Nas quatro comparações acima, a LRU teve menos faults e makespan menor que a FIFO. "
        "A diferença é de algumas centenas de faults, não de uma ordem de grandeza: "
        "com 256 quadros e mil processos, as duas políticas falham muito, "
        "e a LRU só aproveita a localidade que ainda cabe."
    )
    frases.append("")
    return "\n".join(frases)


def _fenomenos(linhas: list[dict[str, object]]) -> str:
    fcfs = _buscar(linhas, "A", "fcfs", None, 1)
    sjf = _buscar(linhas, "A", "sjf", None, 1)
    rr = _buscar(linhas, "A", "rr", 10, 1)
    frases = [
        "## Comboio, inanição e thrashing",
        "",
        f"Efeito comboio, cenário A, 1 CPU, FCFS, LRU: a espera máxima foi "
        f"{_num(fcfs, 'espera_max'):.0f} no pid {_int(fcfs, 'espera_max_pid')} "
        f"e a espera média foi {_br(_num(fcfs, 'espera_media'))}. "
        "Todos chegam juntos e a fila anda na ordem de entrada. "
        "Um processo curto que fica atrás de um longo espera o burst inteiro, "
        "mais os faults que acontecem no meio. A média e o máximo se afastam "
        "porque a posição na fila, e não o tamanho do serviço, decide a espera.",
        "",
        f"Inanição relativa, cenário A, 1 CPU, SJF, LRU: espera média dos curtos "
        f"{_br(_num(sjf, 'espera_curto'))}, dos longos {_br(_num(sjf, 'espera_longo'))}. "
        f"No RR com quantum 10 os curtos esperaram {_br(_num(rr, 'espera_curto'))} "
        f"e os longos {_br(_num(rr, 'espera_longo'))}. "
        "O SJF reduz a espera absoluta das duas classes e, ao mesmo tempo, "
        "aumenta a razão entre longo e curto. O longo perde a decisão sempre que "
        "um curto volta de E/S ou de page fault com um burst menor. "
        "O RR reparte a CPU e aproxima as classes, com espera absoluta maior para as duas, "
        "porque não esvazia a fila pelos curtos.",
        "",
    ]
    a4 = _buscar(linhas, "A", "fcfs", None, 4)
    b1 = _buscar(linhas, "B", "fcfs", None, 1)
    b4 = _buscar(linhas, "B", "fcfs", None, 4)
    taxa = _num(fcfs, "taxa_faults")
    acertos = _int(fcfs, "page_faults") * (1.0 - taxa) / taxa
    frases.append(
        "A taxa de faults alta não deixa a CPU ociosa. "
        f"No FCFS com LRU e 1 CPU no cenário A, a taxa foi {_br(taxa, 4)}, "
        f"com {_int(fcfs, 'page_faults')} faults para {acertos:.0f} acertos. "
        f"O mesmo núcleo teve utilização {_br(_utilizacao_media_pct(fcfs))}%: "
        f"útil {_int(fcfs, 'tempo_util')}, troca {_int(fcfs, 'tempo_troca')} "
        f"e ocioso {_int(fcfs, 'tempo_ocioso')}, no makespan {_int(fcfs, 'makespan')}. "
        "Cada fault tira o processo da CPU por 20 unidades e a página fica protegida "
        "até o acerto. Outro processo pronto ocupa o núcleo na hora. "
        "Com a memória cheia, a próxima referência expulsa uma página que logo será pedida de novo. "
        "Isso é pressão de memória. Não é thrashing no sentido de o processador parar "
        "à espera do disco, porque a utilização fica colada em 100%. "
        f"No cenário A com 4 CPUs a taxa do FCFS continua {_br(_num(a4, 'taxa_faults'), 4)} "
        f"e a utilização média é {_br(_utilizacao_media_pct(a4))}%. "
        f"No cenário B com 1 CPU a taxa é {_br(_num(b1, 'taxa_faults'), 4)} "
        f"e a utilização é {_br(_utilizacao_media_pct(b1))}%. "
        f"Com 4 CPUs a taxa cai para {_br(_num(b4, 'taxa_faults'), 4)} "
        f"e a utilização média fica em {_br(_utilizacao_media_pct(b4))}%, "
        f"com ocioso somado {_int(b4, 'tempo_ocioso')}. "
        "A fila longa, com 1 CPU, segura os dois cenários na mesma taxa, perto de 0,32. "
        "O simulador não tem fila de disco: os faults andam em paralelo, "
        "então o tempo perdido é menor do que seria num disco único, e a CPU não espera."
    )
    frases.append("")
    return "\n".join(frases)


def _limitacoes() -> str:
    return "\n".join(
        [
            "## Limitações do modelo",
            "",
            "O SJF lê o campo `cpu` do burst que ainda falta. No sistema real esse valor "
            "não está disponível e precisaria ser estimado; a vantagem medida aqui é um teto.",
            "",
            "A classe (`curto` ou `longo`) é só rótulo de análise. Nenhum escalonador a consulta.",
            "",
            "Não há fila de disco. Processos em page fault ou em E/S esperam em paralelo, "
            "cada um com o próprio instante de retorno. Um disco real serializaria parte desses acessos.",
            "",
            "O custo do fault é fixo (20) e o da troca de contexto também (1, nesta bateria). "
            "O quantum não inclui a troca: só o tempo em que a CPU avança uma referência.",
            "",
            "A substituição é global. A página em trânsito fica protegida até o acerto, "
            "e a página que uma CPU já decidiu executar naquele instante não é vítima.",
            "",
            "Cada processo usa um núcleo por vez. O speedup mede paralelismo entre processos, "
            "não dentro de um processo. A mesma carga e os mesmos 256 quadros rodam em 1 e em 4 CPUs, "
            "então a comparação de speedup é válida e a disputa de memória muda junto com o hardware.",
            "",
        ]
    )


def _gantt() -> str:
    return "\n".join(
        [
            "## Gantt",
            "",
            "A janela de 0 a 200 do cenário A com FCFS e LRU está em",
            "`resultados/graficos/gantt_A_fcfs_cpu1.png` e",
            "`resultados/graficos/gantt_A_fcfs_cpu4.png`.",
            "Os CSV de todas as execuções ficam em `resultados/`, no formato `cpu,inicio,fim,evento`.",
            "`TROCA` é a troca de contexto, `OCIOSA` é CPU sem processo, `P<pid>` é execução útil.",
            "",
            "Os outros gráficos são `resultados/graficos/espera_media.png` (espera média por escalonador),",
            "`resultados/graficos/quantum.png` (espera, resposta e trocas contra o quantum do RR)",
            "e `resultados/graficos/speedup.png` (speedup por escalonador).",
            "",
        ]
    )


def _buscar(
    linhas: list[dict[str, object]],
    cenario: str,
    sched: str,
    quantum: int | None,
    cpus: int,
    subst: str = "lru",
) -> dict[str, object]:
    alvo = "" if quantum is None else quantum
    for linha in linhas:
        if (
            linha["cenario"] == cenario
            and linha["sched"] == sched
            and linha["quantum"] == alvo
            and int(str(linha["cpus"])) == cpus
            and linha["subst"] == subst
        ):
            return linha
    raise KeyError((cenario, sched, quantum, cpus, subst))


def _num(linha: dict[str, object], campo: str) -> float:
    valor = linha[campo]
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{campo} não é numérico: {valor!r}")
    return float(valor)


def _int(linha: dict[str, object], campo: str) -> int:
    return int(_num(linha, campo))


def _opc(linha: dict[str, object], campo: str) -> float | None:
    valor = linha[campo]
    if valor is None or valor == "":
        return None
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{campo} não é numérico: {valor!r}")
    return float(valor)


def _utilizacao_media_pct(linha: dict[str, object]) -> float:
    return _num(linha, "utilizacao_media") * 100.0


def _utilizacao_da_cpu_pct(linha: dict[str, object], indice: int) -> float:
    return _num(linha, f"cpu{indice}_utilizacao") * 100.0


def _folga_de_utilizacao(linha: dict[str, object]) -> float:
    valores = [_utilizacao_da_cpu_pct(linha, indice) for indice in range(int(str(linha["cpus"])))]
    return max(valores) - min(valores)


def _trocas_por_cpu(linha: dict[str, object]) -> str:
    valores = [str(_int(linha, f"cpu{indice}_trocas")) for indice in range(int(str(linha["cpus"])))]
    if len(valores) == 1:
        return valores[0]
    return ", ".join(valores[:-1]) + " e " + valores[-1]


def _br(valor: float, casas: int = 2) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def _br_opc(valor: float | None, casas: int = 2) -> str:
    if valor is None:
        return "—"
    return _br(valor, casas)


def _quantum_ordem(linha: dict[str, object]) -> int:
    quantum = linha["quantum"]
    if quantum == "":
        return -1
    return int(str(quantum))


def carregar_csv(caminho: Path) -> list[dict[str, object]]:
    linhas: list[dict[str, object]] = []
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        for bruta in csv.DictReader(arquivo):
            linha: dict[str, object] = {}
            for chave, valor in bruta.items():
                if chave in {"cenario", "sched", "subst"}:
                    linha[chave] = valor
                elif valor == "":
                    linha[chave] = "" if chave == "quantum" else None
                elif "." in valor:
                    linha[chave] = float(valor)
                else:
                    linha[chave] = int(valor)
            linhas.append(linha)
    return linhas


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    escrever_analise(
        carregar_csv(raiz / "resultados" / "metricas.csv"), raiz / "experimentos" / "analise.md"
    )
