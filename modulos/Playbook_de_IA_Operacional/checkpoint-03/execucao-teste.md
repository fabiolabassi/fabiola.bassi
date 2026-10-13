# Checkpoint 03 - Execução e Resultados

## Prompt Parametrizável
Ver arquivo: `prompt-causa-raiz.md`

## Parâmetros
- `{{config_cerebro}}`: Configuração do cluster Elasticsearch
- `{{metricas_cerebro}}`: Métricas das últimas 2 horas
- `{{logs_cerebro}}`: Logs do nó cobrindo a janela do problema

## Artefatos Fornecidos

### Artefato 1 - Configuração (cerebro.yaml)
```yaml
cerebro:
  shards: 12
  replicas_per_shard: 1
  jvm_heap: 8g
  refresh_interval: 1s
  reindex_job:
    schedule: "0 2 * * *"     # roda todo dia às 02:00
    avg_duration_min: 90      # normalmente termina ~03:30
  query_cache:
    enabled: true
    size_mb: 512
```

### Artefato 2 - Métricas (08h-10h)
```
timestamp              search_p99_ms   indexed_docs_per_s   heap_used_pct   cache_hit_pct
2026-05-13 08:00 UTC   850             4200                 61              74
2026-05-13 08:30 UTC   1100            4100                 68              71
2026-05-13 09:00 UTC   2300            9800                 79              58
2026-05-13 09:30 UTC   4100            11200                88              41
2026-05-13 10:00 UTC   6700            12400                94              29
```

### Artefato 3 - Logs (trecho 08h-10h)
```
[2026-05-13T08:02:11,540][INFO ][o.e.t.LoggingTaskListener              ][cerebro-node-3] reindex task [88123] (scheduled 02:00) progress, created [3.8M]/[10M] docs (38%)
[2026-05-13T08:14:33,019][WARN ][o.e.m.j.JvmGcMonitorService            ][cerebro-node-3] [gc][young] duration [620ms], collections [1] in [10s], heap [4.9gb]->[3.1gb]/[8gb]
[2026-05-13T08:41:07,222][INFO ][o.e.i.IndexingMemoryController         ][cerebro-node-3] now throttling indexing for shard [logs-2026.05][7]: segment writing can't keep up
[2026-05-13T09:03:55,810][WARN ][o.e.t.ThreadPool                       ][cerebro-node-3] write thread pool queue at [150/200]
[2026-05-13T09:12:48,402][WARN ][o.e.m.j.JvmGcMonitorService            ][cerebro-node-3] [gc][old] duration [1.1s], collections [2] in [60s], heap [6.3gb]->[5.9gb]/[8gb]
[2026-05-13T09:20:02,118][INFO ][o.e.t.LoggingTaskListener              ][cerebro-node-3] reindex task [88123] (scheduled 02:00) progress, created [4.0M]/[10M] docs (40%)
[2026-05-13T09:31:17,653][WARN ][o.e.i.b.HierarchyCircuitBreakerService ][cerebro-node-3] [parent] usage [6.9gb/8gb] (86%), approaching limit
[2026-05-13T09:44:29,901][WARN ][o.e.s.SearchService                    ][cerebro-node-3] slow query on shard [logs-2026.05][7] took [2380ms]
[2026-05-13T09:51:08,377][WARN ][o.e.t.ThreadPool                       ][cerebro-node-3] write thread pool queue at [188/200]
[2026-05-13T09:58:41,102][WARN ][o.e.t.ThreadPool                       ][cerebro-node-3] write thread pool queue full [200/200], rejecting bulk — EsRejectedExecutionException
[2026-05-13T09:58:43,210][WARN ][o.e.m.j.JvmGcMonitorService            ][cerebro-node-3] [gc][old] duration [1.8s], collections [4] in [60s], heap [7.6gb]->[7.4gb]/[8gb]
[2026-05-13T09:58:44,005][INFO ][o.e.t.LoggingTaskListener              ][cerebro-node-3] reindex task [88123] (scheduled 02:00) still running, created [4.1M]/[10M] docs (41%), ETA unknown
[2026-05-13T09:58:45,889][WARN ][o.e.i.IndexingMemoryController         ][cerebro-node-3] indexing buffer above limit, throttling shard [logs-2026.05][7]
[2026-05-13T09:58:46,330][DEBUG][o.e.s.query.QueryPhase                 ][cerebro-node-3] shard [logs-2026.05][7] search took [5031ms] (timeout [5000ms])
[2026-05-13T09:58:46,512][ERROR][o.e.s.SearchService                    ][cerebro-node-3] search returned partial results: 11/12 shards succeeded
[2026-05-13T09:58:46,701][WARN ][o.e.i.b.HierarchyCircuitBreakerService ][cerebro-node-3] [parent] circuit breaker tripped, usage [7.7gb/8gb] (96%) over limit
[2026-05-13T09:58:47,001][WARN ][o.e.i.cache.query.IndicesQueryCache    ][cerebro-node-3] query cache eviction rate spiking, hit_ratio dropped to 0.29
[2026-05-13T10:01:12,778][ERROR][o.e.s.SearchService                    ][cerebro-node-3] CircuitBreakingException: [parent] Data too large, would be [7.9gb/8gb]
[2026-05-13T10:03:39,255][WARN ][o.e.t.ThreadPool                       ][cerebro-node-3] write thread pool rejected [1284] bulk requests in last 5min
[2026-05-13T10:05:50,640][ERROR][o.e.s.SearchService                    ][cerebro-node-3] all shards failed for index [logs-2026.05] on 3 of last 20 queries
```

## Execução

**Modelo usado**: Claude Sonnet 4 (Anthropic)
**Justificativa**: Tarefa de raciocínio complexo exigindo correlação de múltiplas fontes de dados e distinção entre causa e consequência. Claude Sonnet 4 tem excelente desempenho em raciocínio técnico (maior que GPT-4o-mini) com custo moderado (~$3/1M input tokens). Privacidade: logs contêm hostname "cerebro-node-3" (genérico) e nome de índice "logs-2026.05" (padrão temporal) - não há dados sensíveis. Pode enviar para modelo externo sem sanitização.

**Output esperado**:

### ANÁLISE CRONOLÓGICA
Às 08:02, o job de reindexação agendado para 02:00 estava apenas em 38% (3.8M de 10M docs), já com 6h de atraso em relação ao esperado (deveria ter terminado ~03:30). Às 08:14, o primeiro warning de GC aparece com heap em 4.9GB. Às 08:41, o IndexingMemoryController começa a throttling o shard 7 porque segment writing não consegue acompanhar. Entre 08:00 e 09:00, search_p99 sobe de 850ms para 2300ms, indexed_docs_per_s mais que dobra (4200→9800), heap_used sobe de 61% para 79%, e cache_hit cai de 74% para 58%.

Às 09:03, a fila de write thread pool atinge 150/200. Às 09:12, GC old duration sobe para 1.1s com heap em 6.3GB. Às 09:20, a reindexação está apenas em 40% (4.0M de 10M) - progrediu apenas 0.2M em 18 minutos. Às 09:31, circuit breaker atinge 86% do heap. Às 09:44, primeira slow query de 2380ms aparece. Às 09:51, fila de write thread pool atinge 188/200.

Às 09:58:41, a fila fica cheia (200/200) e começa a rejeitar bulk requests. Heap atinge 7.6GB. Às 09:58:44, reindexação está em 41% (4.1M de 10M) - quase sem progresso em 38 minutos. Às 09:58:46, search estoura timeout de 5s e retorna resultados parciais (11/12 shards). Circuit breaker dispara aos 96% do heap (7.7GB). Cache hit ratio cai para 0.29. Às 10:01, CircuitBreakingException é lançada diretamente. Às 10:05, 3 das últimas 20 queries falharam completamente (all shards failed).

### CORRELAÇÃO ENTRE ARTEFATOS
**Configuração + Métricas**: O jvm_heap de 8GB na configuração é o teto absoluto. As métricas mostram heap_used_pct crescendo de 61% às 08h para 94% às 10h, indicando aproximação do limite. O cache de 512MB não é suficiente para a carga, evidenciado pela queda de cache_hit_pct de 74% para 29%.

**Configuração + Logs**: O schedule "0 2 * * *" deveria terminar em ~90min (avg_duration_min: 90), ou seja ~03:30. Os logs mostram que às 10:00 ainda estava em 41%, indicando que o job está travado ou muito lento. O refresh_interval de 1s está gerando muita pressão de indexação.

**Métricas + Logs**: O crescimento de indexed_docs_per_s (4200→12400) correlaciona com os logs de throttling e rejeição de bulk requests. A queda de cache_hit_pct (74%→29%) correlaciona com o log de "query cache eviction rate spiking" às 09:58:47. O aumento de search_p99_ms (850→6700) correlaciona com os logs de slow query (2380ms às 09:44), timeout (5031ms às 09:58:46) e CircuitBreakingException (10:01).

### DIFERENCIAÇÃO CAUSA vs CONSEQUÊNCIA
**Causa-raiz**: O job de reindexação agendado para 02:00 não está progredindo adequadamente. Deveria terminar ~03:30, mas às 10:00 ainda estava em 41% (4.1M de 10M docs). Isso cria write thrashing contínuo que compete com queries por recursos.

**Consequências**:
- Cache hit caindo (de 74% para 29%) é efeito do heap saturado forçando evictions frequentes, não causa.
- Circuit breaker disparando (96% heap) é efeito do heap sendo saturado pelo write thrashing, não causa.
- ThreadPool rejeitando bulks (EsRejectedExecutionException) é efeito da fila encher por saturação, não causa.
- Search timeouts e resultados parciais são efeitos do circuit bloqueando operações, não causa.
- Aumento de indexed_docs_per_s (4200→12400) é efeito do sistema tentando compensar atraso, não causa primária.

### CAUSA-RAIZ IDENTIFICADA
A causa-raiz da degradação é o job de reindexação agendado para 02:00 que não está progredindo adequadamente. A configuração indica que o job tem duração média de 90min (terminando ~03:30), mas os logs mostram que às 10:00 (8h depois do schedule) ainda estava em apenas 41% (4.1M de 10M docs). Entre 09:20 e 09:58, progrediu apenas 0.1M docs em 38 minutos - praticamente travado.

Este write thrashing contínuo (evidenciado pelos logs de IndexingMemoryController throttling, ThreadPool rejeitando bulks, e indexed_docs_per_s crescendo descontroladamente) saturou o heap de 8GB (atingiu 96% às 09:58). A saturação do heap causou:
1. Aumento de pressão de GC (durations de 1.1s a 1.8s em old gen)
2. Evictions agressivas no query cache (hit ratio caiu de 74% para 29%)
3. Circuit breaker disparando e bloqueando operações
4. Search timeouts e resultados parciais

Evidências que suportam:
- Config: avg_duration_min: 90 indicando baseline de 90min, mas logs mostram 8h de execução
- Logs: progresso de reindexação de 38% (08:02) para 41% (09:58) - quase estagnado
- Métricas: heap_used_pct de 61%→94% correlacionando com logs de GC warnings
- Logs: write thread pool queue cheia (200/200) rejeitando bulks às 09:58:41
- Logs: circuit breaker trip aos 96% heap às 09:58:46

O job de reindexação travado é o evento primário que desencadeou a cascata. Se o job fosse interrompido ou agendado para horário de menor carga, o heap não saturaria e as buscas continuariam normais.

### AÇÃO RECOMENDADA
Interromper imediatamente o job de reindexação [88123] para liberar recursos de heap e parar o write thrashing. Monitorar heap_used_pct e search_p99_ms para confirmar recuperação. Em seguida:
1. Investigar por que o job está progredindo tão lentamente (possível lock no shard 7, volume de dados maior que esperado, ou problema de I/O)
2. Ajustar o schedule da reindexação para horário de menor carga (ex: madrugada)
3. Considerar aumentar jvm_heap se o volume de dados cresceu desde a configuração original
4. Revisar refresh_interval de 1s para um valor maior se aplicações não necessitam de latência tão baixa

### INCERTEZAS E LIMITAÇÕES
Os artefatos não permitem determinar com certeza POR QUE o job de reindexação está progredindo tão lentamente. Possíveis causas não verificáveis com os dados fornecidos:
- Lock ou contention no shard 7 específico (logs mencionam throttling neste shard)
- Volume de dados maior que o baseline de 10M docs usado no avg_duration_min
- Problema de I/O no storage subjacente
- Contenção com outras operações de indexação em horário comercial

---

## Curadoria

### Técnica/Framework escolhido
- **Chain of Thought Estruturado**: Dividi o raciocínio em 6 passos explícitos (ler config, analisar métricas, correlacionar logs, distinguir causa/consequência, chegar à causa-raiz, propor ação). Isso guia o modelo passo a passo.
- **Role Prompting**: Defini o modelo como "engenheiro de dados sênior com expertise em Elasticsearch" para alinhar o contexto técnico.
- **Requisito de Evidência**: Exigi que o modelo cite trechos específicos dos logs e correlações entre artefatos, reduzindo alucinação.

### Refinamentos feitos
1. **Iteração 1**: Prompt inicial não enfatizava a distinção entre causa e consequência. Adicionei seção específica "Distinguir causa de consequência" com exemplos.
2. **Iteração 2**: O modelo estava listando problemas sem construir narrativa cronológica. Adicionei seção "Análise Cronológica" exigindo horários específicos.
3. **Iteração 3**: O modelo não estava citando evidências dos 3 artefatos. Adicionei instrução explícita de "Cite trechos específicos dos logs quando relevante" e seção "Correlação Entre Artefatos".
4. **Iteração 4**: Adicionei seção "Incertezas e Limitações" para incentivar honestidade epistêmica - o modelo deve admitir o que não sabe.

### Sanitização de dados
Os artefatos contêm:
- Nome de nó: "cerebro-node-3" (genérico, padrão de cluster)
- Nome de índice: "logs-2026.05" (padrão temporal, não sensível)
- Task ID: "88123" (identificador interno)
- Timestamps específicos (não sensíveis)
- **Decisão**: Não há dados sensíveis (no tenant, hostname interno real, dados de cliente). Pode enviar para modelo externo sem sanitização adicional.

### Avaliação final
O prompt satisfaz os requisitos:
- Parametrizável (recebe {{config_cerebro}}, {{metricas_cerebro}}, {{logs_cerebro}})
- Correlaciona os 3 artefatos para chegar à causa-raiz
- Distingue causa de consequência (não lista apenas sintomas)
- Cita evidências específicas dos artefatos
- Propõe ação proporcional ao diagnóstico
- Reconhece incertezas e limitações
- Saída estruturada e legível
