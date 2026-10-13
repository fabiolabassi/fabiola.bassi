---
nome: Planejamento da Migração do Forge
descricao: Propõe um passo a passo da migração do Forge de batch para event-driven baseado no diagnóstico, com etapas reversíveis
versao: 1.0.0
tags: [migracao, data-pipeline, planejamento, reversibilidade]
inputs:
  - nome: diagnostico_forge
    descricao: Diagnóstico do estado atual do Forge (saída do prompt de diagnóstico)
---

# Planejamento da Migração do Forge

## Objetivo
Segundo prompt de uma cadeia de 3 prompts para planejar a migração do Forge de batch para event-driven. Este prompt foca no planejamento da migração em etapas incrementais e reversíveis, baseado no diagnóstico do estado atual.

## Quando Usar
- Como segundo passo após o diagnóstico do estado atual do Forge
- Para planejar migrações complexas que não podem ser big-bang
- Para documentar a estratégia de transição (paralelo, gradual, híbrido)
- Como entrada para o prompt de execução (terceiro prompt da cadeia)

## Exemplo de Uso

### Entrada (resumida - diagnóstico)
Arquitetura: pipeline batch monolítico com 14 etapas acopladas
Riscos: perda de dados, falha não detectável, etapas podem não funcionar com dados incrementais
Dependências: Sentinel, Cerebro, billing precisam continuar funcionando

### Saída Esperada (resumida)
```
### ESTRATÉGIA DE TRANSIÇÃO
Abordagem: Paralelo gradual com dual-write. Rodar batch e event-driven em paralelo por um período, com o Relay fazendo dual-write. Isso permite validar que o event-driven produz os mesmos resultados que o batch antes de mudar dependências.

### ETAPAS DA MIGRAÇÃO

**Etapa 1: Adicionar consumer event-driven ao Relay**
- Objetivo: Criar novo consumidor que processa eventos continuamente
- Dependências: Nenhuma - é aditivo
- Risco: Baixo - batch continua funcionando
- Reversibilidade: Fácil - basta parar o consumer
- Critérios de sucesso: Consumer consumindo, Relay não degradou

**Etapa 2: Implementar transformação incremental em Spark**
- Objetivo: Adaptar 14 etapas para processar janelas de 1min
- Dependências: Etapa 1 completa
- Risco: Alto - algumas etapas podem não funcionar
- Reversibilidade: Média - exige rollback de código
- Critérios de sucesso: Outputs idênticos ao batch

[continua com 6-8 etapas]
```

## Limitações
- É o segundo de uma cadeia de 3 prompts - depende da saída do prompt de diagnóstico
- Assume familiaridade com estratégias de migração (strangler pattern, dual-write, blue-green)
- A qualidade do planejamento depende da qualidade do diagnóstico fornecido
- Não detalha implementação técnica - apenas plano de alto nível
- Específico para o contexto do Forge da Aegis - não é genérico para qualquer pipeline

## Técnica Utilizada
- Chain of Thought (parte da cadeia): segundo passo de 3 prompts sequenciais
- Role Prompting: define o modelo como "arquiteto de dados sênior"
- Estratégia Incremental: exige que cada etapa seja reversível individualmente
- Princípios de Migração: nada de big-bang, cada etapa com critérios de sucesso claros

## Uso em Cadeia
Este prompt é o **segundo de uma cadeia de 3 prompts**:
1. **Diagnóstico**: analisa estado atual, identifica riscos e dependências
2. **Planejamento** (este prompt): propõe etapas da migração em ordem lógica, com reversibilidade
3. **Execução**: detalha plano executável com ações específicas, rollback plan e critérios de sucesso

A saída do prompt de diagnóstico deve ser usada como entrada neste prompt. A saída deste prompt deve ser usada como entrada no prompt de execução.
