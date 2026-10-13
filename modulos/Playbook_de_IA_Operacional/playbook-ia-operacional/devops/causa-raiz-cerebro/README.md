---
nome: Análise de Causa-raiz de Degradação
descricao: Analisa config, métricas e logs do Cerebro para identificar causa-raiz de degradação de busca
versao: 1.0.0
tags: [elasticsearch, causa-raiz, debug, performance]
inputs:
  - nome: config_cerebro
    descricao: Arquivo de configuração do cluster Elasticsearch (cerebro.yaml)
  - nome: metricas_cerebro
    descricao: Métricas do Cerebro nas últimas 2 horas (search_p99, indexed_docs, heap, cache)
  - nome: logs_cerebro
    descricao: Logs de um nó do Cerebro cobrindo a janela do problema
---

# Análise de Causa-raiz de Degradação

## Objetivo
Prompt para análise de causa-raiz de degradação no sistema de busca Cerebro (Elasticsearch). Recebe três artefatos (configuração, métricas e logs) e correlaciona as informações para identificar a causa-raiz, distinguindo entre causa e consequência, e recomenda ação proporcional ao diagnóstico.

## Quando Usar
- Quando o Cerebro apresenta degradação de performance (latência alta, resultados incompletos)
- Para investigação pós-incidente do Cerebro
- Para documentação de RCA (Root Cause Analysis)
- Quando há necessidade de entender interações entre configuração, métricas e logs

## Exemplo de Uso

### Entrada (resumida)
**Config**: jvm_heap: 8g, reindex_job schedule: "0 2 * * *", avg_duration_min: 90
**Métricas**: search_p99 subiu de 850ms às 08h para 6700ms às 10h, heap_used de 61% para 94%
**Logs**: reindex task em 41% às 10h (deveria terminar ~03:30), circuit breaker disparou aos 96% heap

### Saída Esperada (resumida)
```
### CAUSA-RAIZ IDENTIFICADA
O job de reindexação agendado para 02:00 não está progredindo adequadamente. Deveria terminar ~03:30, mas às 10:00 ainda estava em 41%. Este write thrashing contínuo saturou o heap de 8GB, causando evictions agressivas no cache, circuit breaker disparando e timeouts de busca.

### AÇÃO RECOMENDADA
Interromper imediatamente o job de reindexação para liberar recursos de heap. Monitorar heap_used_pct e search_p99_ms para confirmar recuperação. Em seguida investigar por que o job está progredindo tão lentamente e ajustar schedule ou heap.
```

## Limitações
- Requer que os três artefatos sejam fornecidos completos e cobrindo a mesma janela temporal
- Assume familiaridade com Elasticsearch (heap, GC, circuit breaker, shards)
- A análise depende da qualidade dos logs - se faltarem eventos críticos, a causa-raiz pode não ser identificável
- Não substitui investigação mais profunda com ferramentas de profiling ou análise de heap dump
- Específico para Cerebro/Elasticsearch - não é genérico para outros sistemas de busca

## Técnica Utilizada
- Chain of Thought Estruturado: 6 passos explícitos (ler config, analisar métricas, correlacionar logs, distinguir causa/consequência, chegar à causa-raiz, propor ação)
- Role Prompting: define o modelo como "engenheiro de dados sênior com expertise em Elasticsearch"
- Requisito de Evidência: exige citação de trechos específicos dos logs e correlações entre artefatos
- Honestidade Epistêmica: seção explícita para incertezas e limitações
