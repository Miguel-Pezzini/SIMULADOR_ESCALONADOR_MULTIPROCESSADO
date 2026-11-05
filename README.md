# Simulador de escalonamento multiprocessado

Simulador de tempo discreto com uma fila de prontos global, escalonadores FCFS, SJF não preemptivo e Round Robin, e paginação sob demanda com substituição FIFO ou LRU. O núcleo usa só a biblioteca padrão do Python 3.11+.

## Instalar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,experimentos]"
```

O extra `experimentos` traz o Matplotlib, usado só para os gráficos. O comando `simulador` não precisa dele.

## Executar

```bash
simulador \
  --arquivo dados/cenario_A_t0.json \
  --cpus 1 \
  --sched fcfs \
  --subst lru \
  --quadros 256
```

Também vale `python -m simulador` com os mesmos argumentos. A saída no terminal é o resumo da seção 9. O Gantt da janela 0 a 200 e o JSON de métricas vão para `resultados/`.

| Parâmetro | Valores | Impacto |
| --- | --- | --- |
| `--arquivo` | caminho do JSON, obrigatório | Define a carga: chegada, bursts de CPU com as páginas referenciadas e bursts de E/S. A classe (curto ou longo) aparece nas métricas, e nenhum escalonador a usa para escolher o próximo processo. |
| `--cpus` | `1` ou `4`, obrigatório | Número de CPUs que retiram processos da mesma fila de prontos, da de menor índice para a maior. Mais CPUs encurtam o makespan e disputam os mesmos quadros. |
| `--sched` | `fcfs`, `sjf` ou `rr`, obrigatório | Decide quem executa. FCFS tira a cabeça da fila e não preempta. SJF escolhe o menor pedaço que ainda falta do burst de CPU atual; no empate, fica quem entrou antes na fila; também não preempta. RR tira a cabeça e preempta quando o quantum acaba e há outro processo pronto. |
| `--quantum` | inteiro ≥ 1; obrigatório no RR e proibido nos outros | Fatia de tempo útil do Round Robin. Troca de contexto e page fault não consomem quantum. No fim da fatia, com alguém na fila, o processo vai para o fim e o próximo despacho pode pagar troca. Com a fila vazia, a fatia renova sem troca. Quantum menor gera mais preempções e trocas; quantum maior se aproxima do FCFS. |
| `--subst` | `fifo` ou `lru`, obrigatório | Política de substituição quando a memória está ligada e não há quadro livre. FIFO expulsa a página carregada há mais tempo que não esteja protegida nem em uso por uma CPU. LRU expulsa a menos recentemente usada nessas mesmas condições. Isso muda quais referências faltam. Com `--ignorar-memoria`, o valor é aceito e não altera a rodada. |
| `--quadros` | inteiro ≥ 1, padrão 256 | Quadros da memória física, compartilhados por todas as CPUs. Menos quadros aumentam os page faults. Com `--ignorar-memoria`, o valor é aceito e não altera a rodada. |
| `--custo-troca` | inteiro ≥ 0, padrão 1 | Unidades em que a CPU fica em troca, sem executar e sem consultar página, quando o processo despachado é diferente do último daquela CPU. O primeiro despacho também paga. Zero elimina esse custo. O mesmo processo que volta à mesma CPU, sem outro no meio, não paga. A renovação de quantum com fila vazia também não paga. |
| `--tempo-fault` | inteiro ≥ 1, padrão 20 | Tempo em que o processo fica bloqueado depois de um page fault, com página carregada ou sem vítima disponível. Esse intervalo não entra na espera, que só conta o tempo na fila de prontos. Aumenta turnaround e makespan. Sem vítima, a nova tentativa depois desse tempo conta o fault uma única vez. |
| `--ignorar-memoria` | flag, desligada por padrão | Desliga a paginação. Cada referência executa na hora e não há page fault. Usada no exemplo sem memória. |
| `--referencia-1cpu` | caminho de um JSON de métricas, opcional | Não altera o escalonamento. Depois da rodada, compara o makespan com o da execução de 1 CPU e preenche speedup e eficiência. Sem esse arquivo, os dois campos ficam vazios. |
| `--saida` | diretório, padrão `resultados` | Não altera o escalonamento. É o diretório do Gantt de 0 a 200 e do JSON de métricas. O nome do arquivo embute a carga, o escalonador, o quantum, as CPUs, a substituição, os quadros, o custo de troca e o tempo de fault. |

Speedup e eficiência comparam duas rodadas. Grave a de 1 CPU e aponte o JSON na de 4 CPUs:

```bash
simulador --arquivo dados/cenario_A_t0.json --cpus 4 --sched rr --quantum 10 \
  --subst lru --referencia-1cpu resultados/cenario_A_t0_rr_q10_cpu1_lru_f256_t1_pf20.json
```

O nome exato do JSON aparece na linha `metricas:` da rodada de 1 CPU.

## Exemplos do enunciado

```bash
simulador --arquivo testes/fixtures/exemplo_7_1.json --cpus 1 --sched fcfs \
  --subst fifo --custo-troca 1 --ignorar-memoria --saida /tmp/ex71

simulador --arquivo testes/fixtures/exemplo_7_2.json --cpus 1 --sched fcfs \
  --subst lru --quadros 16 --custo-troca 0 --tempo-fault 5 --saida /tmp/ex72

simulador --arquivo testes/fixtures/exemplo_7_3.json --cpus 1 --sched sjf \
  --subst lru --quadros 8 --custo-troca 0 --tempo-fault 20 --saida /tmp/ex73
```

## Experimentos

```bash
make experimentos
```

São 28 execuções base (cenários A e B, 1 e 4 CPUs, FCFS, SJF e RR com quantum 2, 5, 10, 20 e 50, LRU, 256 quadros) e mais 4 execuções FIFO para comparar com a LRU correspondente. O enunciado nomeia os quantums 2, 10 e 50 e fecha a conta em sete variações; 5 e 20 completam essa conta.

O comando grava `resultados/metricas.csv` (métricas obrigatórias, inclusive utilização, ociosidade e trocas por CPU), os Gantt, os gráficos em `resultados/graficos/`, o texto em `experimentos/analise.md` e o relatório em `relatorio/relatorio.docx`.

## Qualidade do código

```bash
make qualidade
```

O mesmo, sem o make:

```bash
ruff check src testes experimentos
ruff format --check src testes experimentos
mypy src
pytest --cov=simulador --cov-report=term-missing --cov-fail-under=85
```

Ruff cobre lint e formato. O mypy roda em modo estrito sobre `src/simulador`. O pytest cobre os exemplos numéricos das seções 7.1, 7.2 e 7.3, a renovação de quantum, a ordem de chegada e retorno no mesmo instante, o retorno de E/S sem troca indevida e a contagem única do fault sem vítima. A cobertura mínima do pacote é 85%.

## Modelo, em uma página

O tempo é inteiro. Em cada instante entram na fila, em ordem de pid, as chegadas e os retornos de E/S e de page fault; depois o processo que estourou o quantum vai para o fim; só então as CPUs livres despacham, da de menor índice para a maior. Bloqueados não formam fila.

A troca de contexto custa `--custo-troca` quando o processo despachado é diferente do último que aquela CPU executou, inclusive no primeiro despacho. O mesmo processo que continua com a fila vazia no fim do quantum não paga. O quantum conta só tempo útil.

A página é o par (pid, número). Ela entra num quadro na detecção do fault, protegida até o acerto da repetição. Sem vítima livre, o processo tenta de novo depois de `--tempo-fault` e esse fault conta uma vez. No término, os quadros do processo são liberados.

A fila de prontos é um `deque`: FCFS e RR entram e saem em O(1). O SJF varre a fila (no máximo 1000) e escolhe o menor pedaço que falta do burst de CPU atual; empate fica com quem entrou antes. A classe do processo não entra na decisão. A memória usa um dicionário `(pid, página) → quadro` para o acerto em O(1), um `deque` para o FIFO e um `OrderedDict` para o LRU.
