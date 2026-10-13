# Meta-prompting para Checkpoint 04 - Backpressure no Relay

## Objetivo
Criar um prompt parametrizável que recebe um cenário (estado + restrições) e faz a IA comparar múltiplas abordagens de backpressure, pesando prós e contras antes de recomendar.

## Estratégia
- Usar estrutura de análise comparativa (listar opções, comparar critérios, recomendar)
- Enfatizar trade-offs explícitos (custo, complexidade, risco)
- Pedir raciocínio em múltiplos critérios
- Não cuspir resposta única - mostrar o processo de decisão

## Entrada (Parâmetro)
- {{cenario_relay}}: Descrição do estado atual do Relay + restrições do time

## Abordagens em análise
1. Priorizar Sentinel (alerting) na frente do Forge (ingestão)
2. Dead-letter queue (fila separada para reprocessar depois)
3. Dividir Relay por cliente (isolar cliente barulhento)
4. Auto-scaling de consumidores (aumentar automaticamente)

## Critérios de decisão
- Respeitar SLAs (Sentinel: 60s, Forge: 15min)
- Custo (orçamento 8% acima do previsto)
- Não perder telemetry (Steve Rogers alertou sobre isso)
- Complexidade de implementação
- Reversibilidade da solução

## Saída esperada
Comparação estruturada das abordagens com:
- Prós e contras de cada uma
- Avaliação contra as restrições
- Recomendação final com justificativa
