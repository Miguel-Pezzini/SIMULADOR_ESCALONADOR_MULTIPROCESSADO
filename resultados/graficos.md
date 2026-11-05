# Gráficos

Comparação da bateria LRU com 256 quadros: cenários A e B, 1 e 4 CPUs, FCFS, SJF e Round Robin com quantum 2, 5, 10, 20 e 50. O valor de cada barra está no topo.

## Espera média

![Espera média por escalonador](graficos/espera_media.png)

## Espera máxima

![Espera máxima por escalonador](graficos/espera_max.png)

## Turnaround médio

![Turnaround médio por escalonador](graficos/turnaround.png)

## Resposta média

![Resposta média por escalonador](graficos/resposta.png)

## Makespan

![Makespan por escalonador](graficos/makespan.png)

## Page faults

![Page faults por escalonador](graficos/page_faults.png)

## Trocas de contexto

![Trocas de contexto por escalonador](graficos/trocas_contexto.png)

## Taxa de page faults

A taxa está em porcentagem.

![Taxa de page faults por escalonador](graficos/taxa_faults.png)

## Efeito do quantum

Espera média, resposta média e trocas de contexto do Round Robin, do quantum 2 ao 50.

![Efeito do quantum no Round Robin](graficos/quantum.png)

## Speedup

Speedup do makespan de 4 CPUs sobre a rodada irmã de 1 CPU. A linha tracejada marca o ganho ideal, 4.

![Speedup de 4 CPUs sobre 1 CPU](graficos/speedup.png)

## Gantt, cenário A, FCFS, 1 CPU

Janela de 0 a 200. TROCA é troca de contexto, OCIOSA é CPU sem processo e P seguido do pid é execução útil.

![Gantt 0–200, cenário A, FCFS, LRU, 1 CPU](graficos/gantt_A_fcfs_cpu1.png)

## Gantt, cenário A, FCFS, 4 CPUs

![Gantt 0–200, cenário A, FCFS, LRU, 4 CPUs](graficos/gantt_A_fcfs_cpu4.png)
