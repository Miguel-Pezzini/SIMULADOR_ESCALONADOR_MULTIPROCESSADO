# Análise dos experimentos

Cada número abaixo sai de `resultados/metricas.csv`, gerado por `experimentos/rodar.py`.
A base tem 28 execuções: cenários A e B, 1 e 4 CPUs, FCFS, SJF e Round Robin
com quantum 2, 5, 10, 20 e 50, substituição LRU e 256 quadros.
O enunciado nomeia os quantums 2, 10 e 50 e fecha a conta em sete variações;
os quantums 5 e 20 completam essa conta e desenham a curva do quantum.
Outras quatro execuções trocam a LRU pela FIFO, nas mesmas condições de carga,
escalonador e número de CPUs. Custo de troca 1 e page fault de 20 em todas.

Speedup é makespan com 1 CPU dividido pelo makespan com 4 CPUs,
no mesmo escalonador, quantum e memória. Eficiência é esse speedup dividido por 4.
A espera conta só o tempo na fila de prontos. E/S e page fault ficam de fora.

## Cenário A

| Escalonador | Q | CPUs | Memória | Espera média | Espera máx | Turnaround | Resposta | Makespan | Trocas | Faults | Taxa | Speedup | Eficiência |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FCFS | — | 1 | LRU | 36216,01 | 70919 | 37036,32 | 499,50 | 74823 | 38520 | 16935 | 0,3185 | — | — |
| FCFS | — | 4 | LRU | 8592,76 | 15152 | 9422,15 | 124,50 | 18982 | 38952 | 16889 | 0,3179 | 3,9418 | 0,9854 |
| RR | 2 | 1 | LRU | 39053,24 | 81559 | 39882,26 | 499,50 | 85703 | 49464 | 16929 | 0,3184 | — | — |
| RR | 2 | 4 | LRU | 9901,07 | 18126 | 10778,04 | 124,50 | 22128 | 51434 | 16934 | 0,3185 | 3,8731 | 0,9683 |
| RR | 5 | 1 | LRU | 36334,37 | 73273 | 37154,74 | 499,50 | 77267 | 41028 | 16800 | 0,3167 | — | — |
| RR | 5 | 4 | LRU | 8613,38 | 15695 | 9443,59 | 124,50 | 19556 | 41355 | 16832 | 0,3172 | 3,9511 | 0,9878 |
| RR | 10 | 1 | LRU | 36255,58 | 71628 | 37076,86 | 499,50 | 75587 | 39348 | 16942 | 0,3186 | — | — |
| RR | 10 | 4 | LRU | 8600,99 | 15257 | 9430,84 | 124,50 | 19164 | 39702 | 16875 | 0,3177 | 3,9442 | 0,9861 |
| RR | 20 | 1 | LRU | 36232,20 | 71067 | 37052,66 | 499,50 | 74940 | 38701 | 16933 | 0,3185 | — | — |
| RR | 20 | 4 | LRU | 8595,11 | 15134 | 9424,62 | 124,50 | 19011 | 39091 | 16888 | 0,3179 | 3,9419 | 0,9855 |
| RR | 50 | 1 | LRU | 36220,69 | 70911 | 37041,36 | 499,50 | 74820 | 38550 | 16951 | 0,3187 | — | — |
| RR | 50 | 4 | LRU | 8592,38 | 15110 | 9422,11 | 124,50 | 18987 | 38976 | 16905 | 0,3181 | 3,9406 | 0,9851 |
| SJF | — | 1 | LRU | 14508,09 | 45746 | 14738,07 | 7098,35 | 46873 | 10409 | 7408 | 0,1697 | — | — |
| SJF | — | 4 | LRU | 3581,90 | 11147 | 3840,96 | 1742,07 | 12481 | 11785 | 8784 | 0,1951 | 3,7555 | 0,9389 |
| FCFS | — | 1 | FIFO | 36236,97 | 71165 | 37069,00 | 499,50 | 75333 | 39081 | 17493 | 0,3256 | — | — |
| RR | 10 | 4 | FIFO | 8559,17 | 15062 | 9401,43 | 124,50 | 19302 | 40220 | 17554 | 0,3263 | — | — |

## Cenário B

| Escalonador | Q | CPUs | Memória | Espera média | Espera máx | Turnaround | Resposta | Makespan | Trocas | Faults | Taxa | Speedup | Eficiência |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FCFS | — | 1 | LRU | 30458,54 | 66686 | 31207,12 | 694,33 | 71355 | 35107 | 16912 | 0,3182 | — | — |
| FCFS | — | 4 | LRU | 343,95 | 4040 | 572,09 | 33,23 | 11953 | 10323 | 7338 | 0,1684 | 5,9696 | 1,4924 |
| RR | 2 | 1 | LRU | 33323,09 | 75598 | 34076,73 | 691,14 | 82189 | 45946 | 16721 | 0,3157 | — | — |
| RR | 2 | 4 | LRU | 651,43 | 8527 | 960,25 | 26,95 | 15772 | 26307 | 10573 | 0,2259 | 5,2111 | 1,3028 |
| RR | 5 | 1 | LRU | 31294,92 | 67996 | 32052,81 | 694,97 | 74275 | 38032 | 16777 | 0,3165 | — | — |
| RR | 5 | 4 | LRU | 314,69 | 5341 | 539,52 | 23,17 | 12733 | 13676 | 7005 | 0,1620 | 5,8333 | 1,4583 |
| RR | 10 | 1 | LRU | 30490,06 | 66476 | 31238,94 | 694,33 | 72133 | 35890 | 16888 | 0,3179 | — | — |
| RR | 10 | 4 | LRU | 268,16 | 4095 | 480,96 | 24,30 | 11949 | 10766 | 6549 | 0,1531 | 6,0367 | 1,5092 |
| RR | 20 | 1 | LRU | 30466,30 | 66106 | 31215,07 | 694,33 | 71519 | 35272 | 16913 | 0,3182 | — | — |
| RR | 20 | 4 | LRU | 284,35 | 3752 | 498,29 | 27,46 | 11728 | 10046 | 6642 | 0,1549 | 6,0981 | 1,5245 |
| RR | 50 | 1 | LRU | 30458,45 | 66137 | 31207,15 | 694,33 | 71367 | 35124 | 16917 | 0,3183 | — | — |
| RR | 50 | 4 | LRU | 296,67 | 3690 | 508,32 | 29,68 | 11623 | 9624 | 6549 | 0,1531 | 6,1402 | 1,5350 |
| SJF | — | 1 | LRU | 9246,40 | 43129 | 9465,26 | 3709,61 | 46316 | 9881 | 6877 | 0,1595 | — | — |
| SJF | — | 4 | LRU | 96,42 | 5608 | 284,36 | 17,43 | 11960 | 8401 | 5424 | 0,1302 | 3,8726 | 0,9681 |
| RR | 2 | 4 | FIFO | 642,93 | 8367 | 960,67 | 26,64 | 15879 | 26744 | 10997 | 0,2328 | — | — |
| SJF | — | 1 | FIFO | 9290,13 | 43251 | 9510,08 | 3727,01 | 46462 | 9928 | 6929 | 0,1605 | — | — |

## Espera, resposta e justiça

No cenário A com 1 CPU e LRU, a espera média foi 36216,01 no FCFS, 14508,09 no SJF e 36255,58 no RR com quantum 10. A resposta média foi 499,50, 7098,35 e 499,50, nessa mesma ordem. A espera máxima do FCFS chegou a 70919 (pid 877).

No cenário A com 4 CPUs e LRU, a espera média foi 8592,76 no FCFS, 3581,90 no SJF e 8600,99 no RR com quantum 10. A resposta média foi 124,50, 1742,07 e 124,50, nessa mesma ordem. A espera máxima do FCFS chegou a 15152 (pid 947).

No cenário B com 1 CPU e LRU, a espera média foi 30458,54 no FCFS, 9246,40 no SJF e 30490,06 no RR com quantum 10. A resposta média foi 694,33, 3709,61 e 694,33, nessa mesma ordem. A espera máxima do FCFS chegou a 66686 (pid 64).

No cenário B com 4 CPUs e LRU, a espera média foi 343,95 no FCFS, 96,42 no SJF e 268,16 no RR com quantum 10. A resposta média foi 33,23, 17,43 e 24,30, nessa mesma ordem. A espera máxima do FCFS chegou a 4040 (pid 465).

No cenário A com 1 CPU, o SJF separa as classes: espera média 13601,92 nos curtos e 35703,51 nos longos. No RR com quantum 10 as duas sobem, para 34860,89 e 68877,61. O SJF baixa a média dos dois grupos porque despacha o menor burst restante e, com isso, também reduz page faults: os curtos terminam, devolvem os quadros, e a memória não fica ocupada pelo conjunto inteiro ao mesmo tempo. Os longos continuam atrás dos curtos. A razão longo/curto é maior no SJF do que no RR, então a média melhora e a justiça relativa piora. A resposta média do SJF nesse caso é 7098,35, bem acima dos 499,50 do RR, porque o longo espera mais para receber a CPU pela primeira vez.

## Efeito do quantum

A comparação usa o cenário A com 1 CPU e LRU, do quantum 2 ao quantum 50. Nesse cenário a resposta média não muda com o quantum. O efeito aparece na espera, nas trocas e no makespan, e no cenário B com 4 CPUs também na taxa de faults. O gráfico `resultados/graficos/quantum.png` mostra os quatro pares.

Com quantum 2, a resposta média foi 499,50 e houve 49464 trocas de contexto. Com quantum 50, a resposta foi 499,50 e as trocas caíram para 38550. A espera média foi de 39053,24 para 36220,69. O FCFS na mesma máquina teve espera 36216,01, resposta 499,50 e 38520 trocas.

No cenário A todos chegam em t = 0 e a primeira referência de cada processo causa page fault. Com custo de troca 1, o simulador despacha um processo por unidade de tempo só para descobrir o fault, em ordem de pid, antes de qualquer quantum se cumprir. Por isso FCFS e RR, em qualquer quantum, têm a mesma resposta média (499,50). O quantum aparece depois: quantum 2 gera 49464 trocas e espera 39053,24; quantum 50 cai para 38550 trocas e espera 36220,69, colado no FCFS (38520 trocas, espera 36216,01). Quantum maior segura o processo na CPU, reduz preempção e se aproxima do FCFS.

## Speedup

No cenário A, o FCFS levou o makespan de 74823 com 1 CPU para 18982 com 4 CPUs. Speedup 3,9418, eficiência 0,9854.
No cenário A, o SJF levou o makespan de 46873 com 1 CPU para 12481 com 4 CPUs. Speedup 3,7555, eficiência 0,9389.
No cenário A, o RR com quantum 2 levou o makespan de 85703 com 1 CPU para 22128 com 4 CPUs. Speedup 3,8731, eficiência 0,9683.
No cenário A, o RR com quantum 10 levou o makespan de 75587 com 1 CPU para 19164 com 4 CPUs. Speedup 3,9442, eficiência 0,9861.
No cenário A, o RR com quantum 50 levou o makespan de 74820 com 1 CPU para 18987 com 4 CPUs. Speedup 3,9406, eficiência 0,9851.

No cenário B, o FCFS levou o makespan de 71355 com 1 CPU para 11953 com 4 CPUs. Speedup 5,9696, eficiência 1,4924.
No cenário B, o SJF levou o makespan de 46316 com 1 CPU para 11960 com 4 CPUs. Speedup 3,8726, eficiência 0,9681.
No cenário B, o RR com quantum 2 levou o makespan de 82189 com 1 CPU para 15772 com 4 CPUs. Speedup 5,2111, eficiência 1,3028.
No cenário B, o RR com quantum 10 levou o makespan de 72133 com 1 CPU para 11949 com 4 CPUs. Speedup 6,0367, eficiência 1,5092.
No cenário B, o RR com quantum 50 levou o makespan de 71367 com 1 CPU para 11623 com 4 CPUs. Speedup 6,1402, eficiência 1,5350.

No cenário A a eficiência fica entre 0,93 e 0,99: perto de 4, sem chegar lá. Cada processo usa um núcleo por vez, a troca ocupa a CPU sem avançar referência, e os 256 quadros são os mesmos da máquina de 1 CPU. No cenário B o speedup do FCFS e do RR passa de 4. Com 1 CPU esses escalonadores geram cerca de 16,9 mil faults; com 4 CPUs, e chegadas espalhadas até t = 9534, o makespan fica perto de 12.000 e os faults caem para a faixa de 6.549 a 10.573. Menos page faults significam menos trabalho extra, e o speedup ultrapassa o número de núcleos. O SJF no cenário B já tinha 6.877 faults com 1 CPU, então o speedup fica em 3,8726, abaixo de 4. Eficiência acima de 1, aqui, é efeito da memória, não de um núcleo a mais.

## FIFO e LRU

Cenário A, FCFS com 1 CPU: LRU teve 16935 page faults (taxa 0,3185) e FIFO teve 17493 (taxa 0,3256). O makespan foi 74823 na LRU e 75333 na FIFO.
Cenário A, RR com quantum 10 e 4 CPUs: LRU teve 16875 page faults (taxa 0,3177) e FIFO teve 17554 (taxa 0,3263). O makespan foi 19164 na LRU e 19302 na FIFO.
Cenário B, SJF com 1 CPU: LRU teve 6877 page faults (taxa 0,1595) e FIFO teve 6929 (taxa 0,1605). O makespan foi 46316 na LRU e 46462 na FIFO.
Cenário B, RR com quantum 2 e 4 CPUs: LRU teve 10573 page faults (taxa 0,2259) e FIFO teve 10997 (taxa 0,2328). O makespan foi 15772 na LRU e 15879 na FIFO.

No FCFS com LRU e 1 CPU, a taxa de faults do cenário A foi 0,3185 (16935 faults) e a do cenário B foi 0,3182 (16912 faults): com um núcleo só, a fila enorme mantém os dois cenários no mesmo regime de substituição. Com 4 CPUs a diferença aparece. O cenário A continua em 0,3179 (16889 faults), porque os 1000 processos estão vivos desde t = 0. O cenário B cai para 0,1684 (7338 faults): as chegadas vão até t = 9534 e a máquina de 4 CPUs dá conta da carga sem empilhar todo mundo na memória. Nas quatro comparações acima, a LRU teve menos faults e makespan menor que a FIFO. A diferença é de algumas centenas de faults, não de uma ordem de grandeza: com 256 quadros e mil processos, as duas políticas falham muito, e a LRU só aproveita a localidade que ainda cabe.

## Comboio, inanição e thrashing

Efeito comboio, cenário A, 1 CPU, FCFS, LRU: a espera máxima foi 70919 no pid 877 e a espera média foi 36216,01. Todos chegam juntos e a fila anda na ordem de entrada. Um processo curto que fica atrás de um longo espera o burst inteiro, mais os faults que acontecem no meio. A média e o máximo se afastam porque a posição na fila, e não o tamanho do serviço, decide a espera.

Inanição relativa, cenário A, 1 CPU, SJF, LRU: espera média dos curtos 13601,92, dos longos 35703,51. No RR com quantum 10 os curtos esperaram 34860,89 e os longos 68877,61. O SJF reduz a espera absoluta das duas classes e, ao mesmo tempo, aumenta a razão entre longo e curto. O longo perde a decisão sempre que um curto volta de E/S ou de page fault com um burst menor. O RR reparte a CPU e aproxima as classes, com espera absoluta maior para as duas, porque não esvazia a fila pelos curtos.

Thrashing, no sentido de disputa forte por quadro: a taxa de faults do FCFS com 1 CPU no cenário A foi 0,3185, com 16935 faults para 36239 acertos (uma referência bem-sucedida por unidade de CPU). Cada fault tira o processo da CPU por 20 unidades e a página fica protegida até o acerto. Com a memória cheia, a próxima referência de outro processo expulsa uma página que logo será pedida de novo. O cenário B com 4 CPUs, citado na seção FIFO e LRU, reduz essa pressão: a taxa do FCFS cai de 0,3179 no cenário A para 0,1684 no B. Com 1 CPU os dois cenários ficam na mesma taxa, perto de 0,32, porque a fila longa segura todo mundo no sistema. O simulador não tem fila de disco: os faults andam em paralelo, então o tempo perdido é menor do que seria num disco único.

## Limitações do modelo

O SJF lê o campo `cpu` do burst que ainda falta. No sistema real esse valor não está disponível e precisaria ser estimado; a vantagem medida aqui é um teto.

A classe (`curto` ou `longo`) é só rótulo de análise. Nenhum escalonador a consulta.

Não há fila de disco. Processos em page fault ou em E/S esperam em paralelo, cada um com o próprio instante de retorno. Um disco real serializaria parte desses acessos.

O custo do fault é fixo (20) e o da troca de contexto também (1, nesta bateria). O quantum não inclui a troca: só o tempo em que a CPU avança uma referência.

A substituição é global. A página em trânsito fica protegida até o acerto, e a página que uma CPU já decidiu executar naquele instante não é vítima.

Cada processo usa um núcleo por vez. O speedup mede paralelismo entre processos, não dentro de um processo. A mesma carga e os mesmos 256 quadros rodam em 1 e em 4 CPUs, então a comparação de speedup é válida e a disputa de memória muda junto com o hardware.

## Gantt

A janela de 0 a 200 do cenário A com FCFS e LRU está em
`resultados/graficos/gantt_A_fcfs_cpu1.png` e
`resultados/graficos/gantt_A_fcfs_cpu4.png`.
Os CSV de todas as execuções ficam em `resultados/`, no formato `cpu,inicio,fim,evento`.
`TROCA` é a troca de contexto, `OCIOSA` é CPU sem processo, `P<pid>` é execução útil.

Os outros gráficos são `resultados/graficos/espera_media.png` (espera média por escalonador),
`resultados/graficos/quantum.png` (espera, resposta e trocas contra o quantum do RR)
e `resultados/graficos/speedup.png` (speedup por escalonador).

