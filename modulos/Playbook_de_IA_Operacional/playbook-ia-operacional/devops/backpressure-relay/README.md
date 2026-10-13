---
nome: Análise de Estratégia de Backpressure
descricao: Compara múltiplas abordagens de backpressure para o Relay, pesando prós e contras antes de recomendar
versao: 1.0.0
tags: [backpressure, arquitetura, decisao, trade-offs]
inputs:
  - nome: cenario_relay
    descricao: Descrição do estado atual do Relay mais restrições de SLA, custo e requisitos
---

# Análise de Estratégia de Backpressure

## Objetivo
Prompt para análise comparativa de estratégias de backpressure no Relay (barramento de eventos). Compara múltiplas abordagens (priority queues, DLQ, tenant isolation, auto-scaling) avaliando prós, contras e critérios como SLAs, custo, risco de perda de dados, complexidade, reversibilidade e escalabilidade, antes de recomendar uma solução.

## Quando Usar
- Quando o Relay está sofrendo sobrecarga e é necessário definir uma estratégia de backpressure
- Para decisões arquiteturais sobre como lidar com picos de carga no barramento
- Para documentação de trade-offs em arquitetura de sistemas distribuídos
- Para alinhar time de engenharia em uma abordagem comum

## Exemplo de Uso

### Entrada (resumida)
**Estado atual**: throughput sustentado 180k msgs/s, pico 320k msgs/s por 25min, retenção 4h
**Restrições**: Sentinel SLA 60s, Forge SLA 15min, orçamento 8% acima, perda inaceitável

### Saída Esperada (resumida)
```
### RECOMENDAÇÃO FINAL
**Abordagem recomendada**: Priorização de Tráfego + Auto-scaling limitado

**Justificativa**: Priority queues garantem que Sentinel (SLA 60s) sempre tem precedência sobre Forge (SLA 15min). Auto-scaling com teto de custo responde a picos moderados sem estourar orçamento. Pico acima do teto é absorvido pela fila de retenção de 4h e reprocessado depois.

**Plano de implementação**:
1. Implementar priority queues no Relay (duas filas: alta para Sentinel, baixa para Forge)
2. Configurar HPA com teto de custo (ex: máximo 25 réplicas)
3. Adicionar métricas de monitoramento
```

## Limitações
- Foca em 4 abordagens específicas - pode haver outras abordagens não consideradas
- Assume familiaridade com conceitos de sistemas distribuídos (backpressure, DLQ, multi-tenancy)
- A análise depende da qualidade e completude do cenário fornecido
- As estimativas de custo são aproximadas e dependem do provedor de infra
- Não considera aspectos de implementação técnica detalhada (ex: tecnologia específica de fila)

## Técnica Utilizada
- Análise Comparativa Estruturada: força avaliação em 6 critérios explícitos antes de recomendar
- Role Prompting: define o modelo como "arquiteto de sistemas"
- Requisito de Justificativa Detalhada: exige explicação de por que alternativas foram piores
- Trade-off Analysis: exige listagem de prós e contras de cada abordagem
