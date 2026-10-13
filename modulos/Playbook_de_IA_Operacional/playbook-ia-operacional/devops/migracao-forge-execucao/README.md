---
nome: Plano Executável e Reversível da Migração
descricao: Detalha o plano de migração do Forge com ações específicas, rollback plan e critérios de sucesso medíveis
versao: 1.0.0
tags: [migracao, data-pipeline, execucao, rollback]
inputs:
  - nome: planejamento_forge
    descricao: Planejamento da migração com etapas e estratégia (saída do prompt de planejamento)
---

# Plano Executável e Reversível da Migração

## Objetivo
Terceiro e último prompt de uma cadeia de 3 prompts para planejar a migração do Forge de batch para event-driven. Este prompt transforma o planejamento em um plano executável com ações específicas (comandos, configurações), rollback plan detalhado para cada etapa, critérios de sucesso medíveis e cronograma.

## Quando Usar
- Como terceiro e último passo após o planejamento da migração
- Para detalhar planos de migração em ações executáveis
- Para documentar rollback plans e critérios de sucesso
- Para criar cronogramas e planos de comunicação de migrações complexas

## Exemplo de Uso

### Entrada (resumida - planejamento)
Estratégia: Paralelo gradual com dual-write
Etapas: 1) Adicionar consumer event-driven, 2) Implementar transformação incremental, 3) Dual-write para validação, 4) Criar views materializadas, 5-7) Migrar dependências, 8) Desligar batch

### Saída Esperada (resumida)
```
### PLANO EXECUTÁVEL

**Etapa 1: Adicionar consumer event-driven ao Relay**

**Ações específicas**:
1. Criar deployment `forge-event-driven-consumer` no namespace `forge-prod`
2. Configurar consumer para ler do topic `relay-events`
3. Implementar buffer local
4. Adicionar métricas de monitoramento
5. Deploy em staging e testar
6. Deploy em produção com 10% do tráfego

**Duração estimada**: 3 dias

**Critérios de sucesso**:
- Métrica 1: `forge_event_consumer_lag` < 1000 eventos - medir por 24h
- Métrica 2: `forge_event_consumer_errors` = 0 - medir por 24h

**Rollback plan**:
- Trigger: `forge_event_consumer_errors` > 10 em 5min
- Ação: `kubectl delete deployment forge-event-driven-consumer`
- Duração: 2 minutos

[continua com 7-8 etapas detalhadas]

### CRONOGRAMA RESUMIDO
- Etapa 1: Semana 1 (3 dias)
- Etapa 2: Semanas 2-3 (2 semanas)
- ...
- Conclusão: Semana 11
```

## Limitações
- É o terceiro e último de uma cadeia de 3 prompts - depende da saída do prompt de planejamento
- Assume familiaridade com ferramentas específicas (Kubernetes, Spark, etc.) - comandos são exemplos
- A qualidade do plano depende da qualidade do planejamento fornecido
- Os comandos específicos podem variar dependendo do ambiente e ferramentas usadas
- Específico para o contexto do Forge da Aegis - não é genérico para qualquer pipeline

## Técnica Utilizada
- Chain of Thought (parte da cadeia): terceiro e último passo de 3 prompts sequenciais
- Role Prompting: define o modelo como "arquiteto de dados sênior"
- Especificidade Executável: exige comandos específicos, não descrições vagas
- Métricas Objetivas: critérios de sucesso devem ser medíveis (latency < X, throughput > Y)

## Uso em Cadeia
Este prompt é o **terceiro e último de uma cadeia de 3 prompts**:
1. **Diagnóstico**: analisa estado atual, identifica riscos e dependências
2. **Planejamento**: propõe etapas da migração em ordem lógica, com reversibilidade
3. **Execução** (este prompt): detalha plano executável com ações específicas, rollback plan e critérios de sucesso

A saída do prompt de planejamento deve ser usada como entrada neste prompt. A saída deste prompt é o plano final pronto para execução.
