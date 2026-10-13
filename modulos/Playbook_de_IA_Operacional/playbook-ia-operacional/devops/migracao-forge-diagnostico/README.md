---
nome: Diagnóstico do Estado Atual do Forge
descricao: Analisa o estado atual do Forge (pipeline batch) e identifica riscos, dependências e pontos de atenção para migração para event-driven
versao: 1.0.0
tags: [migracao, data-pipeline, batch, event-driven]
inputs:
  - nome: cenario_forge
    descricao: Estado atual do Forge (ingestão, transformação, destino) mais requisitos da migração
---

# Diagnóstico do Estado Atual do Forge

## Objetivo
Primeiro prompt de uma cadeia de 3 prompts para planejar a migração do Forge de batch para event-driven. Este prompt foca no diagnóstico do estado atual, identificando riscos, dependências externas, capacidade de infra e pontos frágeis do design atual que impactam a migração.

## Quando Usar
- Como primeiro passo ao planejar migração de pipelines batch para event-driven
- Para entender riscos e dependências antes de começar uma migração
- Para documentação do estado atual de um pipeline de dados
- Como entrada para o prompt de planejamento (segundo prompt da cadeia)

## Exemplo de Uso

### Entrada (resumida)
**Estado atual**: job cron a cada 60min, 14 etapas Spark em ~40min, destino particionado por hora, ponto frágil (lote falhado acumula dobro de volume)
**Dependências**: Sentinel (dashboards), Cerebro (indexação), billing (relatórios madrugada)
**Requisitos**: consumo contínuo, manter dependências funcionando, migração incremental e reversível

### Saída Esperada (resumida)
```
### ARQUITETURA ATUAL
Pipeline batch clássico: ingestão job cron → 14 etapas Spark acopladas → tabelas particionadas por hora.

### RISCOS DA MIGRAÇÃO
- Alta severidade: Perda de dados durante transição se Relay não tiver retenção suficiente
- Alta severidade: Falha no modelo contínuo pode não ser detectável imediatamente
- Média severidade: Algumas das 14 etapas podem não funcionar com dados incrementais

### DEPENDÊNCIAS EXTERNAS
- Sentinel: lê tabelas agregadas - pode precisar de views materializadas no modelo event-driven
- Cerebro: indexa eventos transformados - pode se beneficiar de latência menor
- Billing: relatórios madrugada - transparente se tabelas continuam sendo atualizadas

### CONCLUSÃO
O Forge é um pipeline batch monolítico com 14 etapas acopladas. O maior risco é garantir que nenhum dado seja perdido durante a transição, dado que o design atual acumula volume em caso de falha.
```

## Limitações
- É o primeiro de uma cadeia de 3 prompts - não deve ser usado isoladamente para migração completa
- Assume familiaridade com pipelines de dados, Spark e conceitos batch vs event-driven
- A qualidade do diagnóstico depende da quantidade de informação fornecida no cenário
- Não propõe soluções - apenas identifica problemas e riscos
- Específico para o contexto do Forge da Aegis - não é genérico para qualquer pipeline

## Técnica Utilizada
- Chain of Thought (parte da cadeia): primeiro passo de 3 prompts sequenciais
- Role Prompting: define o modelo como "arquiteto de dados sênior"
- Análise de Riscos: identifica severidade (alta/média/baixa) de cada risco
- Honestidade Epistêmica: seção "Gaps de Conhecimento" para o que não pode ser concluído

## Uso em Cadeia
Este prompt é o **primeiro de uma cadeia de 3 prompts**:
1. **Diagnóstico** (este prompt): analisa estado atual, identifica riscos e dependências
2. **Planejamento**: propõe etapas da migração em ordem lógica, com reversibilidade
3. **Execução**: detalha plano executável com ações específicas, rollback plan e critérios de sucesso

A saída deste prompt deve ser usada como entrada no prompt de planejamento.
