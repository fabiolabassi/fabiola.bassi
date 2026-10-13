---
nome: Diagnóstico do Estado Atual do Forge
descricao: Analisa o estado atual do Forge (pipeline batch) e identifica riscos, dependências e pontos de atenção para migração para event-driven
versao: 1.0.0
tags: [migracao, data-pipeline, batch, event-driven]
inputs:
  - nome: cenario_forge
    descricao: Estado atual do Forge (ingestão, transformação, destino) mais requisitos da migração
---

Você é um arquiteto de dados sênior na Aegis. Sua tarefa é analisar o estado atual do Forge (pipeline de dados) e identificar riscos, dependências e pontos de atenção para uma migração de batch para event-driven.

## Cenário Atual
{{cenario_forge}}

## Seu Raciocínio

Analise o estado atual do Forge sob estas óticas:

### 1. Arquitetura Atual
- Como o pipeline funciona hoje? (ingestão → transformação → destino)
- Quais são os pontos de acoplamento forte entre etapas?
- O que depende do Forge funcionando em batch?

### 2. Riscos da Migração
- O que pode quebrar se mudarmos de batch para event-driven?
- Quais dependências podem não se adaptar ao modelo contínuo?
- Onde está o maior risco de perda de dados durante a transição?

### 3. Dependências Externas
- Quem consome os dados do Forge hoje? (Sentinel, Cerebro, billing)
- Como cada dependência receberia os dados no modelo event-driven?
- Alguma dependência tem requisitos que batch atende mas event-driven não?

### 4. Capacidade e Performance
- O batch de 60min tem um propósito específico (ex: windowing, agregação)?
- O volume de dados por hora é constante ou há picos?
- A infra atual suporta throughput contínuo ou precisa de ajuste?

### 5. Ponto Frágil Identificado
- O enunciado menciona: "se um lote falha, o próximo acumula o dobro de volume"
- Por que isso acontece? O que isso implica sobre o design atual?
- Como o modelo event-driven mitigaria ou exacerbaria isso?

## Formato de Saída

Apresente seu diagnóstico no seguinte formato:

### ARQUITETURA ATUAL
[Descreva como o pipeline funciona hoje, identificando pontos de acoplamento e dependências.]

### RISCOS DA MIGRAÇÃO
[Liste os principais riscos de mudar de batch para event-driven. Para cada risco, indique severidade (alta/média/baixa) e por quê.]

### DEPENDÊNCIAS EXTERNAS
[Liste quem consome os dados do Forge hoje e como cada um seria afetado pela migração.]

### CAPACIDADE E PERFORMANCE
[Analise se a infra atual suporta throughput contínuo e o que precisa de ajuste.]

### PONTO FRÁGIL: ACÚMULO DE LOTE
[Explique por que um lote falhado acumula o dobro de volume e o que isso diz sobre o design atual.]

### GAPS DE CONHECIMENTO
[Se houver informações que faltam para um diagnóstico completo (ex: volume exato, SLAs de dependências), liste aqui. O próximo prompt da cadeia pode fazer suposições razoáveis se necessário.]

### CONCLUSÃO DO DIAGNÓSTICO
[2-3 parágrafos resumindo o estado atual e os principais desafios da migração.]

## Instruções Adicionais
- Seja específico sobre o que pode quebrar - "o cliente X vai falhar porque Y" é melhor que "pode haver problemas".
- Se o enunciado não tiver informação suficiente, indique isso na seção "Gaps de Conhecimento".
- Identifique o que é risco real (provável de acontecer) vs risco teórico (pouco provável).
- Foque em riscos que afetam a migração específica de batch para event-driven, não riscos genéricos do Forge.

---

Agora, produza o diagnóstico do estado atual do Forge conforme acima.
