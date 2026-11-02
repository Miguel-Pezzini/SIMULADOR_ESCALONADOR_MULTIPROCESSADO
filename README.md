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

Argumentos: `--arquivo`, `--cpus` (1 ou 4), `--sched` (`fcfs`, `sjf`, `rr`), `--quantum` (obrigatório no RR), `--subst` (`fifo` ou `lru`), `--quadros` (padrão 256), `--custo-troca` (padrão 1), `--log`.

Dois argumentos extras reproduzem o enunciado sem editar código: `--tempo-fault` (padrão 20; o exemplo 7.2 usa 5) e `--ignorar-memoria` (o exemplo 7.1 não tem paginação).

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

O comando grava `resultados/metricas.csv`, os Gantt, os gráficos em `resultados/graficos/` e o texto em `experimentos/analise.md`.

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
