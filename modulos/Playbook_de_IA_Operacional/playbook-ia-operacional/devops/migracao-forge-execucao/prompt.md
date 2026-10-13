---
nome: Plano Executável e Reversível da Migração
descricao: Detalha o plano de migração do Forge com ações específicas, rollback plan e critérios de sucesso medíveis
versao: 1.0.0
tags: [migracao, data-pipeline, execucao, rollback]
inputs:
  - nome: planejamento_forge
    descricao: Planejamento da migração com etapas e estratégia (saída do prompt de planejamento)
---

Você é um arquiteto de dados sênior na Aegis. Sua tarefa é detalhar o plano de migração do Forge de batch para event-driven com ações específicas, rollback plan e critérios de sucesso medíveis.

## Planejamento da Migração (saída do Prompt 2)
{{planejamento_forge}}

## Seu Raciocínio

Transforme o planejamento em um plano executável:

### 1. Detalhamento de Cada Etapa
Para cada etapa do planejamento:
- Quais são as ações específicas? (comandos, configurações, mudanças de código)
- Quanto tempo cada etapa deve levar?
- Quem precisa estar envolvido? (SRE, engenharia de dados, engenharia de produto)
- O que pode dar errado nesta etapa?

### 2. Rollback Plan
Para cada etapa:
- Como detectar que a etapa falhou? (métricas, alertas, logs)
- Qual é o comando/ação de rollback específico?
- Quanto tempo o rollback deve levar?
- O rollback é seguro (não causa perda de dados)?

### 3. Critérios de Sucesso Medíveis
Para cada etapa:
- Qual métrica indica sucesso? (ex: latency < X, throughput > Y, zero erros)
- Por quanto tempo essa métrica deve ser estável?
- O que acontece se o critério não for atendido? (rollback automaticamente ou manualmente?)

### 4. Comunicação e Coordenação
- Quem precisa ser notificado antes de cada etapa?
- Existe janela de manutenção ou a migração é online?
- Como comunicar o progresso para stakeholders (Pepper, Carol, Sam)?

## Formato de Saída

Apresente o plano executável no seguinte formato:

### ESTRATÉGIA DE ROLLBACK GERAL
[Descreva a abordagem geral de rollback (ex: cada etapa é reversível, existe rollback global de emergência, etc.)]

### PLANO EXECUTÁVEL

**Etapa 1: [Nome da etapa]**

**Ações específicas**:
1. [ação 1 - ex: comando específico, mudança de config, PR a fazer]
2. [ação 2]
3. [ação 3]

**Duração estimada**: [X horas/dias]

**Responsáveis**: [quais times/pessoas]

**Critérios de sucesso**:
- Métrica 1: [nome e valor alvo] - medir por [duração]
- Métrica 2: [nome e valor alvo] - medir por [duração]

**Rollback plan**:
- **Trigger de rollback**: [condição que dispara rollback]
- **Ação de rollback**: [comando/ação específica]
- **Duração do rollback**: [X minutos/horas]
- **Verificação pós-rollback**: [como confirmar que rollback funcionou]

**Riscos desta etapa**:
- [risco 1]: [mitigação]
- [risco 2]: [mitigação]

[Repita para cada etapa]

### COMUNICAÇÃO E COORDENAÇÃO
- **Stakeholders a notificar**: [lista]
- **Canal de comunicação**: [ex: Slack #incidentes, email, status page]
- **Frequência de atualização**: [ex: a cada etapa, a cada hora]
- **Critérios para abortar a migração**: [quais condições param tudo]

### MÉTRICAS DE MONITORAMENTO
[Liste as métricas principais que devem ser monitoradas durante toda a migração, com valores de alerta.]

### SUPORTES DE CONTINGÊNCIA
- **Se a migração falhar na etapa X**: [plano B]
- **Se o rollback falhar**: [plano de emergência]
- **Se houver perda de dados**: [procedimento de recuperação]

### CRONOGRAMA RESUMIDO
- Etapa 1: [data/estimativa]
- Etapa 2: [data/estimativa]
- ...
- Conclusão: [data/estimativa]

## Instruções Adicionais
- Seja específico nas ações - "fazer X" é vago, "rodar `kubectl apply -f config.yaml`" é específico.
- O rollback deve ser testável - não diga "reverter mudanças", diga "aplicar config-backup.yaml".
- Os critérios de sucesso devem ser objetivos e medíveis - "performance OK" é vago, "p99 latency < 500ms" é específico.
- Se o planejamento tiver gaps, faça suposições razoáveis e documente-as.
- O plano deve ser algo que um engenheiro possa seguir sem ter que improvisar.

---

Agora, produza o plano executável e reversível conforme acima, baseado no planejamento fornecido.
