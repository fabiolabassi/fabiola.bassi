# Meta-prompting para Checkpoint 05 - Migração do Forge

## Objetivo
Criar uma cadeia de prompts encadeados para planejar a migração do Forge de batch para event-driven. Cada prompt usa a saída do anterior como entrada.

## Estratégia
- Quebrar a migração em etapas (não tentar resolver tudo de uma vez)
- Prompt 1: Diagnóstico do estado atual
- Prompt 2: Proposta de passo a passo da migração
- Prompt 3: Detalhamento do plano executável e reversível
- Cada prompt recebe a saída do anterior como contexto

## Entrada inicial (Parâmetro)
- {{cenario_forge}}: Estado atual do Forge + requisitos da migração

## Fluxo da cadeia
1. **Diagnóstico**: Analisa o estado atual, identifica riscos e dependências
2. **Planejamento**: Propõe etapas da migração em ordem lógica
3. **Execução**: Detalha cada etapa com ações específicas, rollback plan, critérios de sucesso

## Saída final
Plano de migração detalhado, executável e reversível
