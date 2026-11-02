"""Relatório do trabalho, em DOCX, preenchido com as métricas da rodada."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.document import Document as Documento
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.section import Section
from docx.shared import Cm, Pt, RGBColor
from docx.table import Table, _Cell

RAIZ = Path(__file__).resolve().parents[1]
FIGURAS = (
    "espera_media.png",
    "quantum.png",
    "speedup.png",
    "gantt_A_fcfs_cpu1.png",
    "gantt_A_fcfs_cpu4.png",
)
LARGURAS_RESUMO = (
    3.0,
    1.1,
    1.3,
    1.7,
    2.3,
    2.0,
    2.3,
    2.0,
    2.1,
    1.8,
    1.7,
    1.6,
    1.9,
    2.2,
)
CABECALHO_RESUMO = (
    "Escalonador",
    "Q",
    "CPUs",
    "Memória",
    "Espera média",
    "Espera máx.",
    "Turnaround",
    "Resposta",
    "Makespan",
    "Trocas",
    "Faults",
    "Taxa",
    "Speedup",
    "Eficiência",
)


def main() -> None:
    linhas = _carregar(RAIZ / "resultados" / "metricas.csv")
    figuras = _garantir_graficos(RAIZ)
    doc = Document()
    _propriedades(doc)
    _estilos(doc)
    _capa(doc)
    corpo = doc.add_section(WD_SECTION.NEW_PAGE)
    _retrato(corpo)
    _cabecalho(corpo)
    _introducao(doc)
    _modelo(doc)
    _implementacao(doc)
    _validacao(doc)
    _experimentos(doc)
    paisagem = doc.add_section(WD_SECTION.NEW_PAGE)
    _paisagem(paisagem)
    _cabecalho(paisagem)
    _tabelas(doc, linhas)
    figuras_secao = doc.add_section(WD_SECTION.NEW_PAGE)
    _retrato(figuras_secao)
    _cabecalho(figuras_secao)
    _figuras(doc, figuras)
    _discussao(doc, linhas)
    _conclusao(doc, linhas)
    _limitacoes(doc)
    _referencias(doc)
    destino = RAIZ / "relatorio" / "relatorio.docx"
    destino.parent.mkdir(parents=True, exist_ok=True)
    doc.save(destino)
    print(f"relatorio: {destino}")


def _propriedades(doc: Documento) -> None:
    nucleo = doc.core_properties
    nucleo.title = "Simulador de escalonamento multiprocessado com paginação sob demanda"
    nucleo.author = "Miguel Pezzini Kuhr; Davi Barros; Cauã"
    nucleo.subject = "Sistemas Operacionais — UNIVALI"
    nucleo.category = "Relatório"
    nucleo.language = "pt-BR"


def _estilos(doc: Documento) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    _fonte_elemento(normal.element.get_or_add_rPr())
    for nome, tamanho in (("Heading 1", 14), ("Heading 2", 12)):
        estilo = doc.styles[nome]
        estilo.font.name = "Times New Roman"
        estilo.font.size = Pt(tamanho)
        estilo.font.bold = True
        estilo.font.italic = False
        estilo.font.color.rgb = RGBColor(0, 0, 0)
        _fonte_elemento(estilo.element.get_or_add_rPr())


def _fonte_elemento(rpr: OxmlElement) -> None:
    fontes = rpr.find(qn("w:rFonts"))
    if fontes is None:
        fontes = OxmlElement("w:rFonts")
        rpr.append(fontes)
    for atributo in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fontes.set(qn(atributo), "Times New Roman")
    idioma = rpr.find(qn("w:lang"))
    if idioma is None:
        idioma = OxmlElement("w:lang")
        rpr.append(idioma)
    idioma.set(qn("w:val"), "pt-BR")


def _fonte(run: object, tamanho: int, *, negrito: bool = False, italico: bool = False) -> None:
    run.font.name = "Times New Roman"  # type: ignore[attr-defined]
    run.font.size = Pt(tamanho)  # type: ignore[attr-defined]
    run.bold = negrito  # type: ignore[attr-defined]
    run.italic = italico  # type: ignore[attr-defined]
    run.font.color.rgb = RGBColor(0, 0, 0)  # type: ignore[attr-defined]
    elemento = run._r  # type: ignore[attr-defined]
    rpr = elemento.get_or_add_rPr()
    _fonte_elemento(rpr)


def _retrato(secao: Section) -> None:
    secao.orientation = WD_ORIENT.PORTRAIT
    secao.page_width = Cm(21.0)
    secao.page_height = Cm(29.7)
    secao.top_margin = Cm(2.5)
    secao.bottom_margin = Cm(2.0)
    secao.left_margin = Cm(2.5)
    secao.right_margin = Cm(2.5)


def _paisagem(secao: Section) -> None:
    secao.orientation = WD_ORIENT.LANDSCAPE
    secao.page_width = Cm(29.7)
    secao.page_height = Cm(21.0)
    secao.top_margin = Cm(1.5)
    secao.bottom_margin = Cm(1.5)
    secao.left_margin = Cm(1.2)
    secao.right_margin = Cm(1.2)


def _cabecalho(secao: Section) -> None:
    cabecalho = secao.header
    cabecalho.is_linked_to_previous = False
    paragrafo = cabecalho.paragraphs[0]
    paragrafo.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    paragrafo.paragraph_format.space_after = Pt(2)
    trecho = paragrafo.add_run("Sistemas Operacionais — UNIVALI")
    _fonte(trecho, 10)
    rodape = secao.footer
    rodape.is_linked_to_previous = False
    linha = rodape.paragraphs[0]
    linha.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _numero_pagina(linha)


def _numero_pagina(paragrafo: object) -> None:
    inicio = paragrafo.add_run()  # type: ignore[attr-defined]
    campo_inicio = OxmlElement("w:fldChar")
    campo_inicio.set(qn("w:fldCharType"), "begin")
    inicio._r.append(campo_inicio)
    instrucao = paragrafo.add_run()  # type: ignore[attr-defined]
    texto = OxmlElement("w:instrText")
    texto.set(qn("xml:space"), "preserve")
    texto.text = " PAGE "
    instrucao._r.append(texto)
    fim = paragrafo.add_run()  # type: ignore[attr-defined]
    campo_fim = OxmlElement("w:fldChar")
    campo_fim.set(qn("w:fldCharType"), "end")
    fim._r.append(campo_fim)
    for trecho in (inicio, instrucao, fim):
        _fonte(trecho, 10)


def _centro(
    doc: Documento,
    texto: str,
    tamanho: int,
    *,
    negrito: bool = False,
    antes: int = 0,
    depois: int = 0,
) -> None:
    paragrafo = doc.add_paragraph()
    paragrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragrafo.paragraph_format.space_before = Pt(antes)
    paragrafo.paragraph_format.space_after = Pt(depois)
    paragrafo.paragraph_format.line_spacing = 1.0
    paragrafo.paragraph_format.first_line_indent = Cm(0)
    if texto:
        trecho = paragrafo.add_run(texto)
        _fonte(trecho, tamanho, negrito=negrito)


def _titulo(doc: Documento, texto: str, nivel: int = 1) -> None:
    titulo = doc.add_heading(texto, level=nivel)
    titulo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    titulo.paragraph_format.first_line_indent = Cm(0)
    titulo.paragraph_format.space_before = Pt(16 if nivel == 1 else 12)
    titulo.paragraph_format.space_after = Pt(6)
    titulo.paragraph_format.line_spacing = 1.15
    for trecho in titulo.runs:
        _fonte(trecho, 14 if nivel == 1 else 12, negrito=True)


def _p(doc: Documento, *partes: str) -> None:
    paragrafo = doc.add_paragraph()
    paragrafo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragrafo.paragraph_format.line_spacing = 1.5
    paragrafo.paragraph_format.space_after = Pt(8)
    paragrafo.paragraph_format.space_before = Pt(0)
    paragrafo.paragraph_format.first_line_indent = Cm(1.25)
    trecho = paragrafo.add_run(" ".join(partes))
    _fonte(trecho, 12)


def _legenda(doc: Documento, texto: str) -> None:
    paragrafo = doc.add_paragraph()
    paragrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragrafo.paragraph_format.first_line_indent = Cm(0)
    paragrafo.paragraph_format.space_before = Pt(10)
    paragrafo.paragraph_format.space_after = Pt(4)
    paragrafo.paragraph_format.line_spacing = 1.0
    trecho = paragrafo.add_run(texto)
    _fonte(trecho, 10, italico=True)


def _capa(doc: Documento) -> None:
    secao = doc.sections[0]
    _retrato(secao)
    secao.header.is_linked_to_previous = False
    secao.footer.is_linked_to_previous = False
    secao.different_first_page_header_footer = False
    for _ in range(3):
        _centro(doc, "", 12)
    _centro(doc, "UNIVERSIDADE DO VALE DO ITAJAÍ", 14, negrito=True, depois=2)
    _centro(doc, "CIÊNCIA DA COMPUTAÇÃO", 12, negrito=True, depois=18)
    _centro(doc, "SISTEMAS OPERACIONAIS", 12, negrito=True, depois=2)
    _centro(doc, "Prof. Michael Douglas", 12, depois=28)
    _centro(doc, "SIMULADOR DE ESCALONAMENTO MULTIPROCESSADO", 16, negrito=True)
    _centro(doc, "COM PAGINAÇÃO SOB DEMANDA", 16, negrito=True, depois=28)
    _centro(doc, "Miguel Pezzini Kuhr", 12, depois=2)
    _centro(doc, "Davi Barros", 12, depois=2)
    _centro(doc, "Cauã", 12, depois=28)
    _centro(doc, "Itajaí", 12, depois=2)
    _centro(doc, "3 de novembro de 2026", 12)


def _introducao(doc: Documento) -> None:
    _titulo(doc, "1 Introdução")
    _p(
        doc,
        "Escalonamento de CPU e gerenciamento de memória costumam ser estudados em separado.",
        "No sistema, os dois se encontram a cada page fault: o processo sai da CPU,",
        "o núcleo volta para a fila de prontos e a política de escalonamento escolhe",
        "quem entra. Essa escolha muda quais páginas permanecem residentes",
        "e, com isso, muda os faults seguintes.",
    )
    _p(
        doc,
        "Este relatório descreve um simulador de tempo discreto que recebe uma carga",
        "de 1000 processos e mede FCFS, SJF não preemptivo e Round Robin",
        "em máquinas de 1 e de 4 CPUs. A memória é paginada sob demanda,",
        "com substituição global FIFO ou LRU.",
        "Os números da análise saem das 32 execuções gravadas em resultados/metricas.csv.",
    )
    _p(
        doc,
        "O objetivo geral é desenvolver o simulador integrado à paginação sob demanda",
        "e analisar, com os dados coletados, o comportamento dos algoritmos",
        "em duas cargas e em dois hardwares.",
        "Os objetivos específicos são implementar os três escalonadores com quantum variável;",
        "simular 1 e 4 CPUs sobre uma única fila de prontos;",
        "simular page fault com FIFO e LRU; contabilizar a troca de contexto;",
        "registrar prontos, executando, bloqueados e terminados;",
        "calcular as métricas de espera, resposta, turnaround, makespan, speedup,",
        "eficiência, trocas e faults; produzir o diagrama de Gantt da janela de 0 a 200;",
        "procurar injustiça, inanição, efeito comboio e thrashing;",
        "e explicitar as limitações do modelo.",
    )


def _modelo(doc: Documento) -> None:
    _titulo(doc, "2 Modelo")
    _p(
        doc,
        "O tempo é inteiro e começa em 0. Cada processo está em um destes estados:",
        "novo, enquanto a chegada ainda não ocorreu; pronto, na fila de prontos;",
        "executando, em uma CPU, inclusive durante a troca de contexto que o precede;",
        "bloqueado, em E/S ou na resolução de um page fault; terminado,",
        "quando o último burst de CPU acabou.",
        "Bloqueados não formam fila. Cada um espera o próprio instante de retorno,",
        "em paralelo. A espera medida é só o tempo na fila de prontos.",
    )
    _p(
        doc,
        "Há uma única fila de prontos, compartilhada pelas CPUs.",
        "Quando várias CPUs ficam livres no mesmo instante, a de menor índice despacha primeiro.",
        "O processo deixa a fila no instante do despacho, inclusive se a CPU ainda vai gastar",
        "a troca de contexto. No mesmo instante t a ordem é fixa:",
        "primeiro entram as chegadas e os retornos de E/S e de page fault, em ordem de pid;",
        "depois o processo que estourou o quantum vai para o fim da fila;",
        "só então ocorrem os despachos.",
    )
    _p(
        doc,
        "O FCFS atende na ordem de entrada na fila.",
        "O SJF, quando uma CPU fica livre, escolhe o processo pronto cujo pedaço restante",
        "do burst de CPU atual é o menor. Empate fica com quem entrou antes na fila.",
        "Uma vez despachado, o processo não sai da CPU porque chegou outro menor.",
        "O Round Robin usa uma fila circular e um quantum Q.",
        "No fim do quantum, se há outro processo pronto, o atual vai para o fim",
        "e a troca é cobrada.",
        "Se a fila está vazia, o mesmo processo continua, o quantum é renovado e não há custo.",
        "Se o burst acaba antes do quantum, a CPU é liberada na hora.",
        "Um page fault no meio do quantum interrompe a execução e o restante do quantum se perde:",
        "no retorno, o processo entra na fila e recebe quantum inteiro ao ser despachado de novo.",
    )
    _p(
        doc,
        "A troca de contexto custa uma unidade de tempo quando o processo despachado",
        "é diferente do último que aquela CPU executou.",
        "O primeiro despacho de cada CPU também paga.",
        "Durante a troca a CPU está ocupada e nenhuma referência avança.",
        "O custo é o argumento custo-troca, com padrão 1.",
        "Cada CPU acumula tempo útil, tempo de troca e tempo ocioso.",
        "A soma das três parcelas fecha o makespan.",
        "O quantum conta só tempo útil.",
    )
    _p(
        doc,
        "A memória física tem N quadros globais, com padrão 256.",
        "Uma página é o par (pid, número da página).",
        "A página 0 de um processo e a página 0 de outro são páginas diferentes.",
        "A memória começa vazia. A página existe desde o início;",
        "o fault é o tempo de trazê-la para um quadro.",
        "Cada unidade de CPU consome a próxima referência da lista refs.",
        "No acerto, a execução segue. No fault, o processo fica bloqueado pelo tempo de fault,",
        "com padrão 20, e a unidade de CPU daquela referência não é consumida na detecção.",
        "A página entra num quadro na detecção e fica protegida até o acerto da repetição.",
        "A página que uma CPU já decidiu executar naquele instante também não é vítima.",
        "Sem quadro livre, a substituição é global.",
        "Se todos os quadros estão protegidos, o processo tenta de novo depois do tempo de fault",
        "e esse fault conta uma vez.",
        "FIFO escolhe a página carregada há mais tempo. LRU escolhe a de referência mais antiga.",
        "Durante a E/S as páginas permanecem na memória e podem ser vítimas.",
        "No término, os quadros do processo são liberados.",
        "A troca de contexto não altera a memória.",
    )
    _titulo(doc, "2.1 Métricas", 2)
    _p(
        doc,
        "As definições são as da seção 10 do enunciado.",
        "Speedup e eficiência só existem na execução de 4 CPUs,",
        "porque comparam o makespan dessa execução com o da execução irmã de 1 CPU,",
        "no mesmo escalonador, quantum e memória.",
    )
    _legenda(doc, "Tabela 1 — Definição das métricas obrigatórias.")
    _tabela(
        doc,
        ["Métrica", "Definição"],
        [
            ["Espera", "Tempo na fila de prontos. E/S e page fault ficam de fora. Média e máximo."],
            ["Turnaround", "Instante de término menos o instante de chegada. Média."],
            ["Resposta", "Instante do primeiro despacho menos o instante de chegada. Média."],
            ["Makespan", "Instante em que o último processo termina."],
            ["Speedup", "Makespan com 1 CPU dividido pelo makespan com 4 CPUs."],
            ["Eficiência", "Speedup dividido por 4. O valor 1 esgota o ganho ideal."],
            ["Trocas", "Número de vezes em que o custo de troca foi cobrado."],
            ["Page faults", "Ocorrências. A taxa é faults dividido por faults mais acertos."],
            ["Utilização", "(tempo útil + tempo de troca) dividido pelo makespan, por CPU."],
        ],
        [4.0, 12.0],
    )


def _implementacao(doc: Documento) -> None:
    _titulo(doc, "3 Implementação")
    _p(
        doc,
        "O núcleo está em Python 3.11 e usa só a biblioteca padrão,",
        "para o professor executar o comando simulador sem instalar bibliotecas de gráfico.",
        "Arquivo, número de CPUs, escalonador, quantum, política de substituição,",
        "quantidade de quadros, custo da troca, tempo de fault e a opção de ignorar a memória",
        "entram pela linha de comando. Mudar um parâmetro não exige editar o código.",
        "O Matplotlib entra apenas na geração das figuras deste relatório.",
    )
    _p(
        doc,
        "A fila de prontos é um deque. FCFS e Round Robin retiram a cabeça em tempo constante.",
        "O SJF percorre a fila, de no máximo 1000 processos, e escolhe o menor burst restante.",
        "O número de sequência da entrada na fila desempata, então quem chegou antes ganha",
        "sem uma segunda varredura. A classe curto ou longo não entra na chave.",
        "Com mil processos, a varredura do SJF cabe folgada no tempo de uma execução.",
    )
    _p(
        doc,
        "A memória guarda um dicionário de (pid, página) para o índice do quadro.",
        "O acerto consulta esse dicionário em tempo constante, o que importa",
        "porque há uma referência por unidade de CPU e a carga soma 36.239 referências.",
        "Um deque registra a ordem de carga do FIFO: a vítima é a primeira página da esquerda",
        "que não está protegida nem em uso naquele instante.",
        "Um OrderedDict registra o LRU. Cada acerto move a página para o fim;",
        "a vítima é a primeira chave que ainda pode sair.",
        "Inserir no fim e mover para o fim são operações constantes,",
        "então a política não precisa varrer os 256 quadros a cada referência.",
        "O conjunto de páginas protegidas e o conjunto de páginas em uso neste instante",
        "impedem que a vítima seja a página recém-carregada ou a página que outra CPU",
        "já decidiu executar.",
    )
    _p(
        doc,
        "Ao final de cada execução o simulador grava o resumo da seção 9,",
        "o JSON de métricas e o Gantt da janela de 0 a 200, no formato cpu, início, fim, evento.",
        "A opção de log registra, a cada mudança de estado, o evento, a fila de prontos,",
        "os bloqueados com o instante de retorno, o processo em cada CPU",
        "e a quantidade de quadros ocupados.",
    )


def _validacao(doc: Documento) -> None:
    _titulo(doc, "4 Validação")
    _p(
        doc,
        "Antes da carga de 1000 processos, o simulador foi conferido nos três exemplos",
        "numéricos do enunciado. Os testes automatizados reproduzem os valores abaixo.",
    )
    _titulo(doc, "4.1 Exemplo sem memória", 2)
    _p(
        doc,
        "O exemplo 7.1 usa 1 CPU, FCFS, custo de troca 1 e ignora a paginação.",
        "P1 chega em 0 com burst 5, P2 chega em 0 com burst 3 e P3 chega em 2 com burst 2.",
        "O Gantt é troca de 0 a 1, P1 de 1 a 6, troca de 6 a 7, P2 de 7 a 10,",
        "troca de 10 a 11 e P3 de 11 a 13.",
        "A CPU acumula 10 de tempo útil, 3 de troca e 0 de ocioso. O makespan é 13.",
        "A espera média é (0 + 6 + 8) / 3 = 4,67. O turnaround médio é 9.",
        "A utilização é (10 + 3) / 13 = 100%.",
    )
    _legenda(doc, "Tabela 2 — Exemplo 7.1 com FCFS, 1 CPU, troca 1 e sem memória.")
    _tabela(
        doc,
        ["Processo", "Espera", "Resposta", "Turnaround"],
        [
            ["P1", "0", "0", "6"],
            ["P2", "6", "6", "10"],
            ["P3", "8", "8", "11"],
        ],
        [4.0, 4.0, 4.0, 4.0],
    )
    _p(
        doc,
        "O mesmo exemplo com SJF troca a ordem: P2, P3 e P1.",
        "As esperas ficam 7, 0 e 2, os turnarounds ficam 13, 4 e 5, e o makespan continua 13.",
        "P2 e P3, menores, passam na frente de P1, que já estava pronto em t = 0",
        "e por isso paga a espera do próprio burst mais longo.",
        "Com Round Robin e quantum 2, as esperas ficam 8, 9 e 4, as respostas ficam 0, 3 e 4,",
        "os turnarounds ficam 16, 14 e 7, há 6 trocas e o makespan sobe para 16.",
        "O tempo útil permanece 10. As trocas extras explicam o makespan maior.",
    )
    _titulo(doc, "4.2 Page fault com fila quase vazia", 2)
    _p(
        doc,
        "O exemplo 7.2 usa 1 CPU, FCFS, troca 0, fault de 5 e memória grande o bastante",
        "para nenhuma página ser retirada. P1, P2 e P3 sofrem fault nas primeiras referências",
        "e ficam bloqueados em paralelo. A espera dos três é 0.",
        "Os turnarounds são 12, 12 e 6. O makespan é 13.",
        "Há 5 page faults e 5 acertos. A CPU tem 5 de tempo útil, 0 de troca e 8 de ocioso:",
        "com todos bloqueados, a fila quase não se forma.",
        "As 20 unidades do exemplo didático da seção 5.5, e as 5 daqui,",
        "não entram na espera, porque o processo estava bloqueado.",
    )
    _titulo(doc, "4.3 Fila depois dos faults", 2)
    _p(
        doc,
        "O exemplo 7.3 usa 1 CPU, troca 0, fault de 20 e 8 quadros.",
        "P1, P2 e P3 chegam em t = 0, dão fault juntos e voltam juntos em t = 20.",
        "A partir daí a fila existe. O makespan dos dois escalonadores é 29 e há 3 faults.",
        "As 20 unidades de bloqueio continuam fora da espera.",
    )
    _legenda(doc, "Tabela 3 — Exemplo 7.3 depois do retorno dos faults, em t = 20.")
    _tabela(
        doc,
        ["Escalonador", "Ordem", "Espera P1 / P2 / P3", "Espera média"],
        [
            ["FCFS", "P1, P2, P3", "0 / 4 / 7", "3,67"],
            ["SJF", "P3, P2, P1", "5 / 2 / 0", "2,33"],
        ],
        [3.5, 3.5, 5.0, 4.0],
    )


def _experimentos(doc: Documento) -> None:
    _titulo(doc, "5 Experimentos")
    _p(
        doc,
        "Cada cenário tem 1000 processos, 959 curtos e 41 longos,",
        "36.239 unidades de CPU e 34.816 unidades de E/S.",
        "A classe é rótulo de análise. O escalonador não a consulta.",
        "No cenário A todos chegam em t = 0.",
        "No cenário B as chegadas vão de t = 2 a t = 9534,",
        "com carga média próxima de 95% da capacidade de 4 CPUs.",
        "O mesmo arquivo roda em 1 e em 4 CPUs. A máquina, e não o arquivo,",
        "define núcleos, quadros e escalonador. Essa identidade da carga",
        "é o que torna o speedup comparável.",
    )
    _p(
        doc,
        "A bateria de base tem 28 execuções: dois cenários, 1 e 4 CPUs,",
        "FCFS, SJF e Round Robin com quantum 2, 5, 10, 20 e 50,",
        "substituição LRU e 256 quadros.",
        "O enunciado nomeia os quantums 2, 10 e 50 e fecha a conta em sete variações",
        "por cenário e por número de CPUs. Os quantums 5 e 20 completam a curva.",
        "Outras quatro execuções trocam a LRU pela FIFO, nas mesmas condições de carga,",
        "escalonador e CPUs: cenário A com FCFS e 1 CPU;",
        "cenário A com RR de quantum 10 e 4 CPUs;",
        "cenário B com SJF e 1 CPU;",
        "cenário B com RR de quantum 2 e 4 CPUs.",
        "A escolha cruza cenário, política de CPU e número de núcleos.",
        "Em todas as 32 execuções o custo de troca é 1 e o page fault dura 20.",
    )


def _tabelas(doc: Documento, linhas: list[dict[str, object]]) -> None:
    _titulo(doc, "6 Resultados")
    _p(
        doc,
        "Cada linha é uma execução. O traço indica métrica que não se aplica:",
        "quantum no FCFS e no SJF, e speedup na execução de 1 CPU,",
        "que é a base da divisão. As quatro últimas linhas de cada tabela são as comparações FIFO.",
    )
    for indice, cenario in enumerate(("A", "B"), start=4):
        _legenda(doc, f"Tabela {indice} — Métricas do cenário {cenario}.")
        corpo = [_linha_tabela(linha) for linha in _grupo(linhas, cenario)]
        _tabela(doc, list(CABECALHO_RESUMO), corpo, list(LARGURAS_RESUMO), fonte=8)


def _figuras(doc: Documento, pasta: Path) -> None:
    _titulo(doc, "6.1 Figuras", 2)
    _p(
        doc,
        "As três primeiras figuras reúnem a bateria LRU.",
        "A linha tracejada do speedup marca o valor 4, ganho ideal de quatro núcleos",
        "quando o trabalho e a memória se comportam como na máquina de 1 CPU.",
        "Os dois Gantt mostram a janela de 0 a 200 do cenário A com FCFS e LRU.",
        "O makespan dessa carga passa de 70.000 com 1 CPU, então a janela inteira",
        "não caberia numa figura legível. TROCA é a troca de contexto,",
        "OCIOSA é CPU sem processo e o rótulo P seguido do pid é execução útil.",
        "Nessa janela a faixa sai inteira em TROCA, nas quatro CPUs e na CPU única.",
        "Todos chegam em t = 0. Cada despacho paga uma unidade de troca,",
        "a primeira referência causa page fault e o processo sai antes de executar",
        "uma unidade útil. Com mil processos na fila, as primeiras 200 unidades",
        "só descobrem faults. A execução útil começa depois dessa janela.",
    )
    pares = (
        (
            "espera_media.png",
            "Figura 1 — Espera média por escalonador, com LRU e 256 quadros.",
        ),
        (
            "quantum.png",
            "Figura 2 — Espera, resposta e trocas de contexto contra o quantum do Round Robin.",
        ),
        (
            "speedup.png",
            "Figura 3 — Speedup de 4 CPUs sobre 1 CPU, no mesmo escalonador, quantum e memória.",
        ),
        (
            "gantt_A_fcfs_cpu1.png",
            "Figura 4 — Gantt de 0 a 200 no cenário A, FCFS, LRU e 1 CPU. "
            "A faixa é só troca de contexto: cada despacho descobre um page fault.",
        ),
        (
            "gantt_A_fcfs_cpu4.png",
            "Figura 5 — Gantt de 0 a 200 no cenário A, FCFS, LRU e 4 CPUs. "
            "As quatro faixas repetem a troca de contexto da Figura 4, em paralelo.",
        ),
    )
    for nome, legenda in pares:
        paragrafo = doc.add_paragraph()
        paragrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragrafo.paragraph_format.first_line_indent = Cm(0)
        paragrafo.paragraph_format.space_before = Pt(8)
        paragrafo.paragraph_format.space_after = Pt(2)
        paragrafo.add_run().add_picture(str(pasta / nome), width=Cm(15.5))
        _legenda(doc, legenda)


def _discussao(doc: Documento, linhas: list[dict[str, object]]) -> None:
    _titulo(doc, "7 Discussão")
    _espera(doc, linhas)
    _quantum(doc, linhas)
    _speedup(doc, linhas)
    _memoria(doc, linhas)
    _fenomenos(doc, linhas)


def _espera(doc: Documento, linhas: list[dict[str, object]]) -> None:
    _titulo(doc, "7.1 Espera, resposta e justiça", 2)
    for cenario, cpus in (("A", 1), ("A", 4), ("B", 1), ("B", 4)):
        fcfs = _buscar(linhas, cenario, "fcfs", None, cpus)
        sjf = _buscar(linhas, cenario, "sjf", None, cpus)
        rr = _buscar(linhas, cenario, "rr", 10, cpus)
        maquina = "1 CPU" if cpus == 1 else "4 CPUs"
        _p(
            doc,
            f"No cenário {cenario} com {maquina} e LRU, a espera média foi",
            f"{_br(_num(fcfs, 'espera_media'))} no FCFS,",
            f"{_br(_num(sjf, 'espera_media'))} no SJF",
            f"e {_br(_num(rr, 'espera_media'))} no RR com quantum 10.",
            "A resposta média, na mesma ordem, foi",
            f"{_br(_num(fcfs, 'resposta_media'))},",
            f"{_br(_num(sjf, 'resposta_media'))}",
            f"e {_br(_num(rr, 'resposta_media'))}.",
            f"A espera máxima do FCFS chegou a {_inteiro(fcfs, 'espera_max')}",
            f"(pid {_inteiro(fcfs, 'espera_max_pid')}).",
        )
    sjf = _buscar(linhas, "A", "sjf", None, 1)
    rr = _buscar(linhas, "A", "rr", 10, 1)
    razao_sjf = _num(sjf, "espera_longo") / _num(sjf, "espera_curto")
    razao_rr = _num(rr, "espera_longo") / _num(rr, "espera_curto")
    _p(
        doc,
        "No cenário A com 1 CPU, o SJF separa as classes.",
        f"A espera média dos curtos foi {_br(_num(sjf, 'espera_curto'))}",
        f"e a dos longos foi {_br(_num(sjf, 'espera_longo'))},",
        f"razão longo/curto de {_br(razao_sjf)}.",
        f"No RR com quantum 10 as duas sobem, para {_br(_num(rr, 'espera_curto'))}",
        f"e {_br(_num(rr, 'espera_longo'))},",
        f"razão de {_br(razao_rr)}.",
        "O SJF baixa a média dos dois grupos porque despacha o menor burst restante",
        "e, com isso, também reduz page faults: os curtos terminam, devolvem os quadros,",
        "e a memória deixa de guardar o conjunto inteiro ao mesmo tempo.",
        "Os longos continuam atrás dos curtos.",
        "A razão longo/curto é maior no SJF do que no RR,",
        "então a média melhora e a justiça relativa piora.",
        f"A resposta média do SJF nesse caso é {_br(_num(sjf, 'resposta_media'))},",
        f"acima dos {_br(_num(rr, 'resposta_media'))} do RR,",
        "porque o processo longo espera mais para receber a CPU pela primeira vez.",
    )


def _quantum(doc: Documento, linhas: list[dict[str, object]]) -> None:
    _titulo(doc, "7.2 Efeito do quantum", 2)
    curto_q = _buscar(linhas, "A", "rr", 2, 1)
    longo_q = _buscar(linhas, "A", "rr", 50, 1)
    fcfs = _buscar(linhas, "A", "fcfs", None, 1)
    _p(
        doc,
        "A comparação usa o cenário A com 1 CPU e LRU, do quantum 2 ao quantum 50,",
        "como na Figura 2. Nesse cenário a resposta média não muda com o quantum.",
        "O efeito aparece na espera, nas trocas e no makespan.",
        "No cenário B com 4 CPUs o quantum também mexe na taxa de faults.",
    )
    _p(
        doc,
        f"Com quantum 2, a resposta média foi {_br(_num(curto_q, 'resposta_media'))}",
        f"e houve {_inteiro(curto_q, 'trocas_contexto')} trocas de contexto.",
        f"Com quantum 50, a resposta foi {_br(_num(longo_q, 'resposta_media'))}",
        f"e as trocas caíram para {_inteiro(longo_q, 'trocas_contexto')}.",
        f"A espera média foi de {_br(_num(curto_q, 'espera_media'))}",
        f"para {_br(_num(longo_q, 'espera_media'))}.",
        f"O FCFS na mesma máquina teve espera {_br(_num(fcfs, 'espera_media'))},",
        f"resposta {_br(_num(fcfs, 'resposta_media'))}",
        f"e {_inteiro(fcfs, 'trocas_contexto')} trocas.",
    )
    _p(
        doc,
        "No cenário A todos chegam em t = 0 e a primeira referência de cada processo",
        "causa page fault. Com custo de troca 1, o simulador despacha um processo",
        "por unidade de tempo só para descobrir o fault, em ordem de pid,",
        "antes de qualquer quantum se cumprir.",
        "Por isso FCFS e RR, em qualquer quantum, têm a mesma resposta média",
        f"({_br(_num(curto_q, 'resposta_media'))}).",
        f"O quantum aparece depois: quantum 2 gera {_inteiro(curto_q, 'trocas_contexto')}",
        f"trocas e espera {_br(_num(curto_q, 'espera_media'))};",
        f"quantum 50 cai para {_inteiro(longo_q, 'trocas_contexto')} trocas",
        f"e espera {_br(_num(longo_q, 'espera_media'))},",
        f"colado no FCFS ({_inteiro(fcfs, 'trocas_contexto')} trocas,",
        f"espera {_br(_num(fcfs, 'espera_media'))}).",
        "Quantum maior segura o processo na CPU, reduz a preempção e se aproxima do FCFS.",
    )


def _speedup(doc: Documento, linhas: list[dict[str, object]]) -> None:
    _titulo(doc, "7.3 Speedup", 2)
    for cenario in ("A", "B"):
        for sched, quantum, rotulo in (
            ("fcfs", None, "FCFS"),
            ("sjf", None, "SJF"),
            ("rr", 2, "RR com quantum 2"),
            ("rr", 10, "RR com quantum 10"),
            ("rr", 50, "RR com quantum 50"),
        ):
            quatro = _buscar(linhas, cenario, sched, quantum, 4)
            uma = _buscar(linhas, cenario, sched, quantum, 1)
            _p(
                doc,
                f"No cenário {cenario}, o {rotulo} levou o makespan",
                f"de {_inteiro(uma, 'makespan')} com 1 CPU",
                f"para {_inteiro(quatro, 'makespan')} com 4 CPUs.",
                f"Speedup {_br(_opc(quatro, 'speedup'), 4)},",
                f"eficiência {_br(_opc(quatro, 'eficiencia'), 4)}.",
            )
    a_ef = [
        _num(linha, "eficiencia")
        for linha in linhas
        if linha["cenario"] == "A" and linha["cpus"] == 4 and linha["subst"] == "lru"
    ]
    faults_b4 = [
        _inteiro(linha, "page_faults")
        for linha in linhas
        if linha["cenario"] == "B"
        and linha["cpus"] == 4
        and linha["subst"] == "lru"
        and linha["sched"] in {"fcfs", "rr"}
    ]
    sjf_b = _buscar(linhas, "B", "sjf", None, 1)
    _p(
        doc,
        f"No cenário A a eficiência fica entre {_br(min(a_ef), 2)} e {_br(max(a_ef), 2)}:",
        "perto de 4, sem chegar lá. Cada processo usa um núcleo por vez,",
        "a troca ocupa a CPU sem avançar referência,",
        "e os 256 quadros são os mesmos da máquina de 1 CPU.",
        "No cenário B o speedup do FCFS e do RR passa de 4.",
        "Com 1 CPU esses escalonadores geram cerca de 16,9 mil faults.",
        "Com 4 CPUs, e chegadas espalhadas de t = 2 a t = 9534,",
        f"os faults do FCFS e do RR caem para a faixa de {min(faults_b4)} a {max(faults_b4)}.",
        "Menos page faults significam menos trabalho extra,",
        "e o speedup ultrapassa o número de núcleos.",
        f"O SJF no cenário B já tinha {_inteiro(sjf_b, 'page_faults')} faults com 1 CPU,",
        f"então o speedup fica em {_br(_opc(_buscar(linhas, 'B', 'sjf', None, 4), 'speedup'), 4)},",
        "abaixo de 4. Eficiência acima de 1, aqui, é efeito da memória.",
    )


def _memoria(doc: Documento, linhas: list[dict[str, object]]) -> None:
    _titulo(doc, "7.4 FIFO e LRU", 2)
    comparacoes = (
        ("A", "fcfs", None, 1, "FCFS com 1 CPU"),
        ("A", "rr", 10, 4, "RR com quantum 10 e 4 CPUs"),
        ("B", "sjf", None, 1, "SJF com 1 CPU"),
        ("B", "rr", 2, 4, "RR com quantum 2 e 4 CPUs"),
    )
    for cenario, sched, quantum, cpus, rotulo in comparacoes:
        lru = _buscar(linhas, cenario, sched, quantum, cpus, "lru")
        fifo = _buscar(linhas, cenario, sched, quantum, cpus, "fifo")
        _p(
            doc,
            f"Cenário {cenario}, {rotulo}: a LRU teve {_inteiro(lru, 'page_faults')} page faults",
            f"(taxa {_br(_num(lru, 'taxa_faults'), 4)})",
            f"e a FIFO teve {_inteiro(fifo, 'page_faults')}",
            f"(taxa {_br(_num(fifo, 'taxa_faults'), 4)}).",
            f"O makespan foi {_inteiro(lru, 'makespan')} na LRU",
            f"e {_inteiro(fifo, 'makespan')} na FIFO.",
        )
    a1 = _buscar(linhas, "A", "fcfs", None, 1)
    b1 = _buscar(linhas, "B", "fcfs", None, 1)
    a4 = _buscar(linhas, "A", "fcfs", None, 4)
    b4 = _buscar(linhas, "B", "fcfs", None, 4)
    _p(
        doc,
        "No FCFS com LRU e 1 CPU, a taxa de faults do cenário A foi",
        f"{_br(_num(a1, 'taxa_faults'), 4)} ({_inteiro(a1, 'page_faults')} faults)",
        f"e a do cenário B foi {_br(_num(b1, 'taxa_faults'), 4)}",
        f"({_inteiro(b1, 'page_faults')} faults).",
        "Com um núcleo só, a fila enorme mantém os dois cenários no mesmo regime de substituição.",
        "Com 4 CPUs a diferença aparece. O cenário A continua em",
        f"{_br(_num(a4, 'taxa_faults'), 4)}",
        f"({_inteiro(a4, 'page_faults')} faults),",
        "porque os 1000 processos estão vivos desde t = 0.",
        f"O cenário B cai para {_br(_num(b4, 'taxa_faults'), 4)}",
        f"({_inteiro(b4, 'page_faults')} faults):",
        "as chegadas vão de t = 2 a t = 9534 e a máquina de 4 CPUs dá conta da carga",
        "sem empilhar todo mundo na memória.",
        "Nas quatro comparações acima, a LRU teve menos faults e makespan menor que a FIFO.",
        "A diferença é de algumas centenas de faults.",
        "Com 256 quadros e mil processos, as duas políticas falham muito,",
        "e a LRU só aproveita a localidade que ainda cabe.",
    )


def _fenomenos(doc: Documento, linhas: list[dict[str, object]]) -> None:
    _titulo(doc, "7.5 Comboio, inanição e thrashing", 2)
    fcfs = _buscar(linhas, "A", "fcfs", None, 1)
    sjf = _buscar(linhas, "A", "sjf", None, 1)
    rr = _buscar(linhas, "A", "rr", 10, 1)
    a4 = _buscar(linhas, "A", "fcfs", None, 4)
    b4 = _buscar(linhas, "B", "fcfs", None, 4)
    taxa = _num(fcfs, "taxa_faults")
    faults = _inteiro(fcfs, "page_faults")
    acertos = faults * (1.0 - taxa) / taxa
    _p(
        doc,
        "Efeito comboio, cenário A, 1 CPU, FCFS, LRU: a espera máxima foi",
        f"{_inteiro(fcfs, 'espera_max')} no pid {_inteiro(fcfs, 'espera_max_pid')}",
        f"e a espera média foi {_br(_num(fcfs, 'espera_media'))}.",
        "Todos chegam juntos e a fila anda na ordem de entrada.",
        "Um processo curto que fica atrás de um longo espera o burst inteiro,",
        "mais os faults que acontecem no meio.",
        "A média e o máximo se afastam porque a posição na fila decide a espera.",
        "O tamanho do serviço entra quando gera faults no meio do caminho.",
    )
    _p(
        doc,
        "Inanição relativa, cenário A, 1 CPU, SJF, LRU: espera média dos curtos",
        f"{_br(_num(sjf, 'espera_curto'))}, dos longos {_br(_num(sjf, 'espera_longo'))}.",
        f"No RR com quantum 10 os curtos esperaram {_br(_num(rr, 'espera_curto'))}",
        f"e os longos {_br(_num(rr, 'espera_longo'))}.",
        "O SJF reduz a espera absoluta das duas classes e, ao mesmo tempo,",
        "aumenta a razão entre longo e curto.",
        "O longo perde a decisão sempre que um curto volta de E/S ou de page fault",
        "com um burst menor.",
        "O RR reparte a CPU e aproxima as classes, com espera absoluta maior para as duas,",
        "porque não esvazia a fila pelos curtos.",
    )
    _p(
        doc,
        "Thrashing, no sentido de disputa forte por quadro: a taxa de faults",
        f"do FCFS com 1 CPU no cenário A foi {_br(taxa, 4)},",
        f"com {faults} faults para {acertos:.0f} acertos.",
        "Há uma referência bem-sucedida por unidade de CPU, e a carga tem 36.239 delas.",
        "Cada fault tira o processo da CPU por 20 unidades e a página fica protegida até o acerto.",
        "Com a memória cheia, a próxima referência de outro processo expulsa uma página",
        "que logo será pedida de novo.",
        "O cenário B com 4 CPUs reduz essa pressão: a taxa do FCFS cai",
        f"de {_br(_num(a4, 'taxa_faults'), 4)} no cenário A",
        f"para {_br(_num(b4, 'taxa_faults'), 4)} no B.",
        "Com 1 CPU os dois cenários ficam na mesma taxa, perto de 0,32,",
        "porque a fila longa segura todo mundo no sistema.",
        "O simulador não tem fila de disco: os faults andam em paralelo,",
        "então o tempo perdido é menor do que seria num disco único.",
    )


def _conclusao(doc: Documento, linhas: list[dict[str, object]]) -> None:
    _titulo(doc, "8 Conclusão")
    sjf = _buscar(linhas, "A", "sjf", None, 1)
    fcfs = _buscar(linhas, "A", "fcfs", None, 1)
    rr = _buscar(linhas, "A", "rr", 10, 1)
    a_ef = [
        _num(linha, "eficiencia")
        for linha in linhas
        if linha["cenario"] == "A" and linha["cpus"] == 4 and linha["subst"] == "lru"
    ]
    _p(
        doc,
        "O simulador reproduz os exemplos numéricos do enunciado",
        "e executa as 32 configurações com fila global e paginação sob demanda.",
        "No cenário A, com os 1000 processos vivos desde t = 0,",
        "os 256 quadros permanecem saturados nas duas máquinas.",
        f"A espera média do SJF com 1 CPU foi {_br(_num(sjf, 'espera_media'))},",
        f"contra {_br(_num(fcfs, 'espera_media'))} no FCFS",
        f"e {_br(_num(rr, 'espera_media'))} no RR com quantum 10.",
        "A mesma política aumenta a razão entre a espera dos longos e a dos curtos",
        "e atrasa a primeira resposta.",
        "O Round Robin com quantum pequeno multiplica as trocas;",
        "com quantum 50, espera, trocas e makespan se aproximam do FCFS.",
        "A resposta média do FCFS e do RR não muda com o quantum,",
        "porque a primeira referência de cada processo causa page fault",
        "antes de o quantum se cumprir.",
        f"A eficiência no cenário A fica entre {_br(min(a_ef), 2)} e {_br(max(a_ef), 2)}.",
    )
    _p(
        doc,
        "No cenário B, as chegadas espaçadas e as 4 CPUs reduzem a disputa por quadro.",
        "O speedup do FCFS e do RR ultrapassa 4 porque a máquina de 4 CPUs",
        "gera bem menos page faults do que a de 1 CPU.",
        "O SJF já reduzia os faults com um núcleo só, e o speedup permanece abaixo de 4.",
        "Nas quatro comparações, a LRU teve menos faults e makespan menor que a FIFO.",
        "A diferença é de algumas centenas de faults.",
        "O efeito comboio aparece na espera máxima do FCFS.",
        "A inanição relativa aparece na distância entre curtos e longos no SJF.",
        "A taxa de faults perto de 0,32 no cenário A, com um núcleo,",
        "descreve a disputa forte por quadro.",
    )


def _limitacoes(doc: Documento) -> None:
    _titulo(doc, "9 Limitações")
    _p(
        doc,
        "O SJF lê o campo cpu do burst que ainda falta.",
        "No sistema real esse valor precisaria ser estimado.",
        "A vantagem medida aqui é um teto, obtido com informação que o escalonador real não tem.",
    )
    _p(
        doc,
        "A classe curto ou longo é rótulo de análise.",
        "Nenhum escalonador a consulta para decidir quem roda.",
    )
    _p(
        doc,
        "Não há fila de disco. Processos em page fault ou em E/S esperam em paralelo,",
        "cada um com o próprio instante de retorno.",
        "Um disco real serializaria parte desses acessos e aumentaria o makespan",
        "nos trechos em que muitos faults coincidem.",
    )
    _p(
        doc,
        "O custo do fault é fixo em 20 e o da troca de contexto é fixo em 1 nesta bateria.",
        "O quantum não inclui a troca: só o tempo em que a CPU avança uma referência.",
    )
    _p(
        doc,
        "A substituição é global. A página em trânsito fica protegida até o acerto,",
        "e a página que uma CPU já decidiu executar naquele instante não é vítima.",
    )
    _p(
        doc,
        "Cada processo usa um núcleo por vez.",
        "O speedup mede paralelismo entre processos, não dentro de um processo.",
        "A mesma carga e os mesmos 256 quadros rodam em 1 e em 4 CPUs,",
        "então a comparação de speedup é válida e a disputa de memória muda junto com o hardware.",
        "Eficiência acima de 1 no cenário B vem dessa mudança de memória,",
        "e some se a leitura tratar o speedup como ganho puro de núcleo.",
    )


def _referencias(doc: Documento) -> None:
    _titulo(doc, "Referências")
    for texto in (
        "SILBERSCHATZ, Abraham; GALVIN, Peter B.; GAGNE, Greg. Operating System Concepts. Wiley.",
        "TANENBAUM, Andrew S.; BOS, Herbert. Modern Operating Systems. Pearson.",
        "UNIVERSIDADE DO VALE DO ITAJAÍ. Simulador de escalonamento multiprocessado "
        "com paginação sob demanda. Trabalho da disciplina de Sistemas Operacionais. Itajaí, 2026.",
    ):
        paragrafo = doc.add_paragraph()
        paragrafo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragrafo.paragraph_format.line_spacing = 1.5
        paragrafo.paragraph_format.space_after = Pt(8)
        paragrafo.paragraph_format.first_line_indent = Cm(0)
        paragrafo.paragraph_format.left_indent = Cm(1.25)
        trecho = paragrafo.add_run(texto)
        _fonte(trecho, 12)


def _tabela(
    doc: Documento,
    cabecalho: list[str],
    linhas: list[list[str]],
    larguras: list[float],
    fonte: int = 11,
) -> Table:
    tabela = doc.add_table(rows=1, cols=len(cabecalho))
    tabela.style = "Table Grid"
    tabela.autofit = False
    tabela.allow_autofit = False
    _layout_fixo(tabela, larguras)
    for celula, texto, largura in zip(tabela.rows[0].cells, cabecalho, larguras, strict=True):
        _preencher(celula, texto, largura, negrito=True, tamanho=fonte, cabecalho=True)
    _repetir_cabecalho(tabela.rows[0])
    for valores in linhas:
        linha = tabela.add_row()
        for celula, texto, largura in zip(linha.cells, valores, larguras, strict=True):
            _preencher(celula, texto, largura, tamanho=fonte)
    return tabela


def _dxa(centimetros: float) -> int:
    return int(Cm(centimetros).twips)


def _layout_fixo(tabela: Table, larguras: list[float]) -> None:
    tbl = tabela._tbl
    tbl_pr = tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tbl_pr.append(layout)
    total = sum(_dxa(largura) for largura in larguras)
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(total))
    tbl_w.set(qn("w:type"), "dxa")
    grade = tbl.find(qn("w:tblGrid"))
    if grade is None:
        grade = OxmlElement("w:tblGrid")
        tbl_pr.addnext(grade)
    for filho in list(grade):
        grade.remove(filho)
    for largura in larguras:
        coluna = OxmlElement("w:gridCol")
        coluna.set(qn("w:w"), str(_dxa(largura)))
        grade.append(coluna)


def _preencher(
    celula: _Cell,
    texto: str,
    largura: float,
    *,
    negrito: bool = False,
    tamanho: int = 11,
    cabecalho: bool = False,
) -> None:
    celula.width = Cm(largura)
    celula.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    celula.text = ""
    paragrafo = celula.paragraphs[0]
    paragrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragrafo.paragraph_format.space_before = Pt(1)
    paragrafo.paragraph_format.space_after = Pt(1)
    paragrafo.paragraph_format.line_spacing = 1.0
    paragrafo.paragraph_format.first_line_indent = Cm(0)
    trecho = paragrafo.add_run(texto)
    _fonte(trecho, tamanho, negrito=negrito or cabecalho)
    if cabecalho:
        _sombrear(celula, "D9E2F3")


def _sombrear(celula: _Cell, cor: str) -> None:
    propriedades = celula._tc.get_or_add_tcPr()
    sombra = OxmlElement("w:shd")
    sombra.set(qn("w:val"), "clear")
    sombra.set(qn("w:fill"), cor)
    propriedades.append(sombra)


def _repetir_cabecalho(linha: object) -> None:
    tr_pr = linha._tr.get_or_add_trPr()  # type: ignore[attr-defined]
    marca = OxmlElement("w:tblHeader")
    tr_pr.append(marca)


def _linha_tabela(linha: dict[str, object]) -> list[str]:
    quantum = linha["quantum"]
    return [
        str(linha["sched"]).upper(),
        "—" if quantum == "" else str(quantum),
        str(linha["cpus"]),
        str(linha["subst"]).upper(),
        _br(_num(linha, "espera_media")),
        str(_inteiro(linha, "espera_max")),
        _br(_num(linha, "turnaround_medio")),
        _br(_num(linha, "resposta_media")),
        str(_inteiro(linha, "makespan")),
        str(_inteiro(linha, "trocas_contexto")),
        str(_inteiro(linha, "page_faults")),
        _br(_num(linha, "taxa_faults"), 4),
        _br_opc(_opc(linha, "speedup"), 4),
        _br_opc(_opc(linha, "eficiencia"), 4),
    ]


def _grupo(linhas: list[dict[str, object]], cenario: str) -> list[dict[str, object]]:
    grupo = [linha for linha in linhas if linha["cenario"] == cenario]
    grupo.sort(
        key=lambda linha: (
            0 if linha["subst"] == "lru" else 1,
            str(linha["sched"]),
            _quantum_ordem(linha),
            int(str(linha["cpus"])),
        )
    )
    return grupo


def _buscar(
    linhas: list[dict[str, object]],
    cenario: str,
    sched: str,
    quantum: int | None,
    cpus: int,
    subst: str = "lru",
) -> dict[str, object]:
    alvo: object = "" if quantum is None else quantum
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


def _inteiro(linha: dict[str, object], campo: str) -> int:
    return int(_num(linha, campo))


def _opc(linha: dict[str, object], campo: str) -> float | None:
    valor = linha[campo]
    if valor is None or valor == "":
        return None
    return _num(linha, campo)


def _br(valor: float | None, casas: int = 2) -> str:
    if valor is None:
        return "—"
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


def _carregar(caminho: Path) -> list[dict[str, object]]:
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


def _garantir_graficos(raiz: Path) -> Path:
    pasta = raiz / "resultados" / "graficos"
    if all((pasta / nome).is_file() for nome in FIGURAS):
        return pasta
    subprocess.run([sys.executable, str(raiz / "experimentos" / "graficos.py")], check=True)
    faltando = [nome for nome in FIGURAS if not (pasta / nome).is_file()]
    if faltando:
        faltas = ", ".join(faltando)
        raise FileNotFoundError(f"gráficos ausentes: {faltas}")
    return pasta


if __name__ == "__main__":
    main()
