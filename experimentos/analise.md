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
Utilização de uma CPU é (tempo útil + tempo de troca) dividido pelo makespan.
A coluna Utilização é a média dessas frações, em porcentagem.
Ocioso é a soma do tempo em que a CPU não tinha processo.
A tabela de utilização abre as mesmas parcelas em cada núcleo, com as trocas cobradas nele.

## Cenário A

| Escalonador | Q | CPUs | Memória | Espera média | Espera máx | Turnaround | Resposta | Makespan | Trocas | Faults | Taxa | Speedup | Eficiência | Utilização | Ocioso |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FCFS | — | 1 | LRU | 36216,01 | 70919 | 37036,32 | 499,50 | 74823 | 38520 | 16935 | 0,3185 | — | — | 99,91 | 64 |
| FCFS | — | 4 | LRU | 8592,76 | 15152 | 9422,15 | 124,50 | 18982 | 38952 | 16889 | 0,3179 | 3,9418 | 0,9854 | 99,03 | 737 |
| RR | 2 | 1 | LRU | 39053,24 | 81559 | 39882,26 | 499,50 | 85703 | 49464 | 16929 | 0,3184 | — | — | 100,00 | 0 |
| RR | 2 | 4 | LRU | 9901,07 | 18126 | 10778,04 | 124,50 | 22128 | 51434 | 16934 | 0,3185 | 3,8731 | 0,9683 | 99,05 | 839 |
| RR | 5 | 1 | LRU | 36334,37 | 73273 | 37154,74 | 499,50 | 77267 | 41028 | 16800 | 0,3167 | — | — | 100,00 | 0 |
| RR | 5 | 4 | LRU | 8613,38 | 15695 | 9443,59 | 124,50 | 19556 | 41355 | 16832 | 0,3172 | 3,9511 | 0,9878 | 99,19 | 630 |
| RR | 10 | 1 | LRU | 36255,58 | 71628 | 37076,86 | 499,50 | 75587 | 39348 | 16942 | 0,3186 | — | — | 100,00 | 0 |
| RR | 10 | 4 | LRU | 8600,99 | 15257 | 9430,84 | 124,50 | 19164 | 39702 | 16875 | 0,3177 | 3,9442 | 0,9861 | 99,07 | 715 |
| RR | 20 | 1 | LRU | 36232,20 | 71067 | 37052,66 | 499,50 | 74940 | 38701 | 16933 | 0,3185 | — | — | 100,00 | 0 |
| RR | 20 | 4 | LRU | 8595,11 | 15134 | 9424,62 | 124,50 | 19011 | 39091 | 16888 | 0,3179 | 3,9419 | 0,9855 | 99,06 | 714 |
| RR | 50 | 1 | LRU | 36220,69 | 70911 | 37041,36 | 499,50 | 74820 | 38550 | 16951 | 0,3187 | — | — | 99,96 | 31 |
| RR | 50 | 4 | LRU | 8592,38 | 15110 | 9422,11 | 124,50 | 18987 | 38976 | 16905 | 0,3181 | 3,9406 | 0,9851 | 99,03 | 733 |
| SJF | — | 1 | LRU | 14508,09 | 45746 | 14738,07 | 7098,35 | 46873 | 10409 | 7408 | 0,1697 | — | — | 99,52 | 225 |
| SJF | — | 4 | LRU | 3581,90 | 11147 | 3840,96 | 1742,07 | 12481 | 11785 | 8784 | 0,1951 | 3,7555 | 0,9389 | 96,19 | 1900 |
| FCFS | — | 1 | FIFO | 36236,97 | 71165 | 37069,00 | 499,50 | 75333 | 39081 | 17493 | 0,3256 | — | — | 99,98 | 13 |
| RR | 10 | 4 | FIFO | 8559,17 | 15062 | 9401,43 | 124,50 | 19302 | 40220 | 17554 | 0,3263 | — | — | 99,03 | 749 |

## Cenário B

| Escalonador | Q | CPUs | Memória | Espera média | Espera máx | Turnaround | Resposta | Makespan | Trocas | Faults | Taxa | Speedup | Eficiência | Utilização | Ocioso |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FCFS | — | 1 | LRU | 30458,54 | 66686 | 31207,12 | 694,33 | 71355 | 35107 | 16912 | 0,3182 | — | — | 99,99 | 9 |
| FCFS | — | 4 | LRU | 343,95 | 4040 | 572,09 | 33,23 | 11953 | 10323 | 7338 | 0,1684 | 5,9696 | 1,4924 | 97,39 | 1250 |
| RR | 2 | 1 | LRU | 33323,09 | 75598 | 34076,73 | 691,14 | 82189 | 45946 | 16721 | 0,3157 | — | — | 100,00 | 4 |
| RR | 2 | 4 | LRU | 651,43 | 8527 | 960,25 | 26,95 | 15772 | 26307 | 10573 | 0,2259 | 5,2111 | 1,3028 | 99,14 | 542 |
| RR | 5 | 1 | LRU | 31294,92 | 67996 | 32052,81 | 694,97 | 74275 | 38032 | 16777 | 0,3165 | — | — | 99,99 | 4 |
| RR | 5 | 4 | LRU | 314,69 | 5341 | 539,52 | 23,17 | 12733 | 13676 | 7005 | 0,1620 | 5,8333 | 1,4583 | 98,00 | 1017 |
| RR | 10 | 1 | LRU | 30490,06 | 66476 | 31238,94 | 694,33 | 72133 | 35890 | 16888 | 0,3179 | — | — | 99,99 | 4 |
| RR | 10 | 4 | LRU | 268,16 | 4095 | 480,96 | 24,30 | 11949 | 10766 | 6549 | 0,1531 | 6,0367 | 1,5092 | 98,35 | 791 |
| RR | 20 | 1 | LRU | 30466,30 | 66106 | 31215,07 | 694,33 | 71519 | 35272 | 16913 | 0,3182 | — | — | 99,99 | 8 |
| RR | 20 | 4 | LRU | 284,35 | 3752 | 498,29 | 27,46 | 11728 | 10046 | 6642 | 0,1549 | 6,0981 | 1,5245 | 98,66 | 627 |
| RR | 50 | 1 | LRU | 30458,45 | 66137 | 31207,15 | 694,33 | 71367 | 35124 | 16917 | 0,3183 | — | — | 99,99 | 4 |
| RR | 50 | 4 | LRU | 296,67 | 3690 | 508,32 | 29,68 | 11623 | 9624 | 6549 | 0,1531 | 6,1402 | 1,5350 | 98,65 | 629 |
| SJF | — | 1 | LRU | 9246,40 | 43129 | 9465,26 | 3709,61 | 46316 | 9881 | 6877 | 0,1595 | — | — | 99,58 | 196 |
| SJF | — | 4 | LRU | 96,42 | 5608 | 284,36 | 17,43 | 11960 | 8401 | 5424 | 0,1302 | 3,8726 | 0,9681 | 93,31 | 3200 |
| RR | 2 | 4 | FIFO | 642,93 | 8367 | 960,67 | 26,64 | 15879 | 26744 | 10997 | 0,2328 | — | — | 99,16 | 533 |
| SJF | — | 1 | FIFO | 9290,13 | 43251 | 9510,08 | 3727,01 | 46462 | 9928 | 6929 | 0,1605 | — | — | 99,37 | 295 |

## Utilização, ociosidade e trocas por CPU

Cada linha é um núcleo de uma execução. Utilização está em porcentagem.

| Cenário | Escalonador | Q | Memória | CPU | Útil | Troca | Ocioso | Trocas | Utilização |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | FCFS | — | LRU | 0 | 36239 | 38520 | 64 | 38520 | 99,91 |
| A | FCFS | — | LRU | 0 | 9134 | 9758 | 90 | 9758 | 99,53 |
| A | FCFS | — | LRU | 1 | 9127 | 9752 | 103 | 9752 | 99,46 |
| A | FCFS | — | LRU | 2 | 9021 | 9734 | 227 | 9734 | 98,80 |
| A | FCFS | — | LRU | 3 | 8957 | 9708 | 317 | 9708 | 98,33 |
| A | RR | 2 | LRU | 0 | 36239 | 49464 | 0 | 49464 | 100,00 |
| A | RR | 2 | LRU | 0 | 9140 | 12869 | 119 | 12869 | 99,46 |
| A | RR | 2 | LRU | 1 | 9130 | 12862 | 136 | 12862 | 99,39 |
| A | RR | 2 | LRU | 2 | 9069 | 12815 | 244 | 12815 | 98,90 |
| A | RR | 2 | LRU | 3 | 8900 | 12888 | 340 | 12888 | 98,46 |
| A | RR | 5 | LRU | 0 | 36239 | 41028 | 0 | 41028 | 100,00 |
| A | RR | 5 | LRU | 0 | 9171 | 10320 | 65 | 10320 | 99,67 |
| A | RR | 5 | LRU | 1 | 9022 | 10363 | 171 | 10363 | 99,13 |
| A | RR | 5 | LRU | 2 | 9047 | 10373 | 136 | 10373 | 99,30 |
| A | RR | 5 | LRU | 3 | 8999 | 10299 | 258 | 10299 | 98,68 |
| A | RR | 10 | LRU | 0 | 36239 | 39348 | 0 | 39348 | 100,00 |
| A | RR | 10 | LRU | 0 | 9094 | 9934 | 136 | 9934 | 99,29 |
| A | RR | 10 | LRU | 1 | 9015 | 9941 | 208 | 9941 | 98,91 |
| A | RR | 10 | LRU | 2 | 9161 | 9943 | 60 | 9943 | 99,69 |
| A | RR | 10 | LRU | 3 | 8969 | 9884 | 311 | 9884 | 98,38 |
| A | RR | 20 | LRU | 0 | 36239 | 38701 | 0 | 38701 | 100,00 |
| A | RR | 20 | LRU | 0 | 9132 | 9787 | 92 | 9787 | 99,52 |
| A | RR | 20 | LRU | 1 | 9073 | 9788 | 150 | 9788 | 99,21 |
| A | RR | 20 | LRU | 2 | 9109 | 9750 | 152 | 9750 | 99,20 |
| A | RR | 20 | LRU | 3 | 8925 | 9766 | 320 | 9766 | 98,32 |
| A | RR | 50 | LRU | 0 | 36239 | 38550 | 31 | 38550 | 99,96 |
| A | RR | 50 | LRU | 0 | 9146 | 9773 | 68 | 9773 | 99,64 |
| A | RR | 50 | LRU | 1 | 9092 | 9774 | 121 | 9774 | 99,36 |
| A | RR | 50 | LRU | 2 | 9042 | 9694 | 251 | 9694 | 98,68 |
| A | RR | 50 | LRU | 3 | 8959 | 9735 | 293 | 9735 | 98,46 |
| A | SJF | — | LRU | 0 | 36239 | 10409 | 225 | 10409 | 99,52 |
| A | SJF | — | LRU | 0 | 9418 | 2886 | 177 | 2886 | 98,58 |
| A | SJF | — | LRU | 1 | 9153 | 2957 | 371 | 2957 | 97,03 |
| A | SJF | — | LRU | 2 | 9093 | 2950 | 438 | 2950 | 96,49 |
| A | SJF | — | LRU | 3 | 8575 | 2992 | 914 | 2992 | 92,68 |
| A | FCFS | — | FIFO | 0 | 36239 | 39081 | 13 | 39081 | 99,98 |
| A | RR | 10 | FIFO | 0 | 9085 | 10064 | 153 | 10064 | 99,21 |
| A | RR | 10 | FIFO | 1 | 9036 | 10091 | 175 | 10091 | 99,09 |
| A | RR | 10 | FIFO | 2 | 9149 | 10041 | 112 | 10041 | 99,42 |
| A | RR | 10 | FIFO | 3 | 8969 | 10024 | 309 | 10024 | 98,40 |
| B | FCFS | — | LRU | 0 | 36239 | 35107 | 9 | 35107 | 99,99 |
| B | FCFS | — | LRU | 0 | 9011 | 2594 | 348 | 2594 | 97,09 |
| B | FCFS | — | LRU | 1 | 9047 | 2577 | 329 | 2577 | 97,25 |
| B | FCFS | — | LRU | 2 | 9203 | 2565 | 185 | 2565 | 98,45 |
| B | FCFS | — | LRU | 3 | 8978 | 2587 | 388 | 2587 | 96,75 |
| B | RR | 2 | LRU | 0 | 36239 | 45946 | 4 | 45946 | 100,00 |
| B | RR | 2 | LRU | 0 | 9141 | 6592 | 39 | 6592 | 99,75 |
| B | RR | 2 | LRU | 1 | 9046 | 6585 | 141 | 6585 | 99,11 |
| B | RR | 2 | LRU | 2 | 9143 | 6550 | 79 | 6550 | 99,50 |
| B | RR | 2 | LRU | 3 | 8909 | 6580 | 283 | 6580 | 98,21 |
| B | RR | 5 | LRU | 0 | 36239 | 38032 | 4 | 38032 | 99,99 |
| B | RR | 5 | LRU | 0 | 9205 | 3453 | 75 | 3453 | 99,41 |
| B | RR | 5 | LRU | 1 | 9076 | 3367 | 290 | 3367 | 97,72 |
| B | RR | 5 | LRU | 2 | 9089 | 3427 | 217 | 3427 | 98,30 |
| B | RR | 5 | LRU | 3 | 8869 | 3429 | 435 | 3429 | 96,58 |
| B | RR | 10 | LRU | 0 | 36239 | 35890 | 4 | 35890 | 99,99 |
| B | RR | 10 | LRU | 0 | 9190 | 2713 | 46 | 2713 | 99,62 |
| B | RR | 10 | LRU | 1 | 8891 | 2733 | 325 | 2733 | 97,28 |
| B | RR | 10 | LRU | 2 | 9047 | 2656 | 246 | 2656 | 97,94 |
| B | RR | 10 | LRU | 3 | 9111 | 2664 | 174 | 2664 | 98,54 |
| B | RR | 20 | LRU | 0 | 36239 | 35272 | 8 | 35272 | 99,99 |
| B | RR | 20 | LRU | 0 | 9139 | 2545 | 44 | 2545 | 99,62 |
| B | RR | 20 | LRU | 1 | 9025 | 2486 | 217 | 2486 | 98,15 |
| B | RR | 20 | LRU | 2 | 9128 | 2482 | 118 | 2482 | 98,99 |
| B | RR | 20 | LRU | 3 | 8947 | 2533 | 248 | 2533 | 97,89 |
| B | RR | 50 | LRU | 0 | 36239 | 35124 | 4 | 35124 | 99,99 |
| B | RR | 50 | LRU | 0 | 9095 | 2399 | 129 | 2399 | 98,89 |
| B | RR | 50 | LRU | 1 | 9198 | 2338 | 87 | 2338 | 99,25 |
| B | RR | 50 | LRU | 2 | 9088 | 2404 | 131 | 2404 | 98,87 |
| B | RR | 50 | LRU | 3 | 8858 | 2483 | 282 | 2483 | 97,57 |
| B | SJF | — | LRU | 0 | 36239 | 9881 | 196 | 9881 | 99,58 |
| B | SJF | — | LRU | 0 | 9392 | 2352 | 216 | 2352 | 98,19 |
| B | SJF | — | LRU | 1 | 8722 | 2357 | 881 | 2357 | 92,63 |
| B | SJF | — | LRU | 2 | 8978 | 2039 | 943 | 2039 | 92,12 |
| B | SJF | — | LRU | 3 | 9147 | 1653 | 1160 | 1653 | 90,30 |
| B | RR | 2 | FIFO | 0 | 9123 | 6712 | 44 | 6712 | 99,72 |
| B | RR | 2 | FIFO | 1 | 9133 | 6681 | 65 | 6681 | 99,59 |
| B | RR | 2 | FIFO | 2 | 9056 | 6697 | 126 | 6697 | 99,21 |
| B | RR | 2 | FIFO | 3 | 8927 | 6654 | 298 | 6654 | 98,12 |
| B | SJF | — | FIFO | 0 | 36239 | 9928 | 295 | 9928 | 99,37 |

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

No cenário A a eficiência fica entre 0,94 e 0,99: perto de 4, sem chegar lá. Cada processo usa um núcleo por vez, a troca ocupa a CPU sem avançar referência, e os 256 quadros são os mesmos da máquina de 1 CPU. No FCFS com LRU, a CPU única ficou com utilização 99,91% (útil 36239, troca 38520, ocioso 64). Com 4 CPUs a utilização média foi 99,03% e o ocioso somado foi 737. A folga entre o núcleo mais ocupado e o menos ocupado foi 1,20 pontos percentuais. No cenário B o speedup do FCFS e do RR passa de 4. Com 1 CPU esses escalonadores geram cerca de 16,9 mil faults; com 4 CPUs, e chegadas espalhadas até t = 9534, os faults caem para a faixa de 6549 a 10573. No FCFS com 4 CPUs a utilização média continua em 97,39% (ocioso somado 1250, trocas por CPU 2594, 2577, 2565 e 2587). Os núcleos não ficam parados. O speedup acima de 4 vem do trabalho extra que a máquina de 1 CPU paga em faults e trocas, e que a de 4 CPUs evita. O SJF no cenário B já tinha 6877 faults com 1 CPU, então o speedup fica em 3,8726, abaixo de 4. Eficiência acima de 1, aqui, é efeito da memória, não de um núcleo a mais.

## FIFO e LRU

Cenário A, FCFS com 1 CPU: LRU teve 16935 page faults (taxa 0,3185) e FIFO teve 17493 (taxa 0,3256). O makespan foi 74823 na LRU e 75333 na FIFO.
Cenário A, RR com quantum 10 e 4 CPUs: LRU teve 16875 page faults (taxa 0,3177) e FIFO teve 17554 (taxa 0,3263). O makespan foi 19164 na LRU e 19302 na FIFO.
Cenário B, SJF com 1 CPU: LRU teve 6877 page faults (taxa 0,1595) e FIFO teve 6929 (taxa 0,1605). O makespan foi 46316 na LRU e 46462 na FIFO.
Cenário B, RR com quantum 2 e 4 CPUs: LRU teve 10573 page faults (taxa 0,2259) e FIFO teve 10997 (taxa 0,2328). O makespan foi 15772 na LRU e 15879 na FIFO.

No FCFS com LRU e 1 CPU, a taxa de faults do cenário A foi 0,3185 (16935 faults) e a do cenário B foi 0,3182 (16912 faults): com um núcleo só, a fila enorme mantém os dois cenários no mesmo regime de substituição. Com 4 CPUs a diferença aparece. O cenário A continua em 0,3179 (16889 faults), porque os 1000 processos estão vivos desde t = 0. O cenário B cai para 0,1684 (7338 faults): as chegadas vão até t = 9534 e a máquina de 4 CPUs dá conta da carga sem empilhar todo mundo na memória. Nas quatro comparações acima, a LRU teve menos faults e makespan menor que a FIFO. A diferença é de algumas centenas de faults, não de uma ordem de grandeza: com 256 quadros e mil processos, as duas políticas falham muito, e a LRU só aproveita a localidade que ainda cabe.

## Comboio, inanição e thrashing

Efeito comboio, cenário A, 1 CPU, FCFS, LRU: a espera máxima foi 70919 no pid 877 e a espera média foi 36216,01. Todos chegam juntos e a fila anda na ordem de entrada. Um processo curto que fica atrás de um longo espera o burst inteiro, mais os faults que acontecem no meio. A média e o máximo se afastam porque a posição na fila, e não o tamanho do serviço, decide a espera.

Inanição relativa, cenário A, 1 CPU, SJF, LRU: espera média dos curtos 13601,92, dos longos 35703,51. No RR com quantum 10 os curtos esperaram 34860,89 e os longos 68877,61. O SJF reduz a espera absoluta das duas classes e, ao mesmo tempo, aumenta a razão entre longo e curto. O longo perde a decisão sempre que um curto volta de E/S ou de page fault com um burst menor. O RR reparte a CPU e aproxima as classes, com espera absoluta maior para as duas, porque não esvazia a fila pelos curtos.

A taxa de faults alta não deixa a CPU ociosa. No FCFS com LRU e 1 CPU no cenário A, a taxa foi 0,3185, com 16935 faults para 36239 acertos. O mesmo núcleo teve utilização 99,91%: útil 36239, troca 38520 e ocioso 64, no makespan 74823. Cada fault tira o processo da CPU por 20 unidades e a página fica protegida até o acerto. Outro processo pronto ocupa o núcleo na hora. Com a memória cheia, a próxima referência expulsa uma página que logo será pedida de novo. Isso é pressão de memória. Não é thrashing no sentido de o processador parar à espera do disco, porque a utilização fica colada em 100%. No cenário A com 4 CPUs a taxa do FCFS continua 0,3179 e a utilização média é 99,03%. No cenário B com 1 CPU a taxa é 0,3182 e a utilização é 99,99%. Com 4 CPUs a taxa cai para 0,1684 e a utilização média fica em 97,39%, com ocioso somado 1250. A fila longa, com 1 CPU, segura os dois cenários na mesma taxa, perto de 0,32. O simulador não tem fila de disco: os faults andam em paralelo, então o tempo perdido é menor do que seria num disco único, e a CPU não espera.

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

