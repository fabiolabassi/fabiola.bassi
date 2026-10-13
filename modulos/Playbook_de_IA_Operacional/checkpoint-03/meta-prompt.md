# Meta-prompting para Checkpoint 03 - Causa-raiz do Cerebro

## Objetivo
Criar um prompt parametrizável que recebe 3 artefatos (config, métricas, logs) e determina a causa-raiz da degradação, não apenas sintomas.

## Estratégia
- Usar Chain of Thought estruturado para guiar o raciocínio
- Enfatizar correlação entre os 3 artefatos
- Ensinar o modelo a distinguir causa de consequência
- Requer raciocínio temporal (08h→10h de degradação)

## Entradas (Parâmetros)
- {{config_cerebro}}: arquivo cerebro.yaml com configuração do cluster Elasticsearch
- {{metricas_cerebro}}: métricas das últimas 2h (timestamp, search_p99_ms, indexed_docs_per_s, heap_used_pct, cache_hit_pct)
- {{logs_cerebro}}: logs de um nó cobrindo a janela do problema

## Causa-raiz esperada (baseada nos artefatos)
- Reindexação agendada às 02:00 deveria terminar ~03:30
- Às 10:00 ainda estava em 41% (4.1M de 10M docs)
- Isso saturou o heap (8GB teto) com write thrashing
- Levou a circuit breaker, timeouts de busca e queda do cache
- Resultado: buscas lentas e resultados incompletos

## Saída esperada
Análise estruturada com:
- Causa-raiz identificada
- Evidências dos 3 artefatos que suportam a conclusão
- Diferenciação clara entre causa e consequência
- Ação recomendada proporcional ao diagnóstico
