# Checkpoint 05 - Execução e Resultados da Cadeia

## Cadeia de Prompts
1. **Prompt 1**: Diagnóstico do estado atual (`prompt-1-diagnostico.md`)
2. **Prompt 2**: Planejamento da migração (`prompt-2-planejamento.md`)
3. **Prompt 3**: Plano executável e reversível (`prompt-3-execucao.md`)

## Cenário Fornecido (Entrada do Prompt 1)

**Forge hoje**:
- ingestão: um job em cron acorda a cada 60min (o "forge-batch-ingest")
- transformação: 14 etapas de processamento encadeadas (em Spark), ~40min no total
- destino: grava em tabelas no data warehouse, particionadas por hora
- ponto frágil: se um lote falha, o próximo acumula o dobro de volume
- quem depende do Forge: Sentinel (lê as tabelas agregadas), Cerebro (indexa os eventos transformados) e os relatórios de billing da Pepper (rodam de madrugada)

**O que a migração precisa garantir**:
- consumir do Relay continuamente, processando em pequenos blocos no lugar do lote de 1h
- manter quem depende do Forge funcionando durante a transição
- nada de virada única (big-bang): a migração tem que ir em passos e poder voltar atrás

## Execução da Cadeia

**Modelo usado**: Claude Sonnet 4 (Anthropic) para os 3 prompts
**Justificativa**: Tarefa de planejamento complexo exigindo raciocínio de arquitetura, dependências e coordenação. Claude Sonnet 4 tem excelente desempenho em raciocínio técnico estruturado. Custo moderado (~$3/1M input tokens) é aceitável dado que são 3 chamadas sequenciais. Privacidade: dados são genéricos (estrutura do pipeline, nomes de sistemas) - não há informações sensíveis. Pode enviar para modelo externo.

---

### Output do Prompt 1: Diagnóstico

### ARQUITETURA ATUAL
O Forge opera como um pipeline batch clássico:
1. **Ingestão**: Job cron "forge-batch-ingest" acorda a cada 60min e lê tudo que acumulou no Relay desde o ciclo anterior
2. **Transformação**: 14 etapas encadeadas em Spark processam os dados brutos (~40min total)
3. **Destino**: Resultados são gravados em tabelas do data warehouse, particionadas por hora para otimizar queries

As 14 etapas de transformação são altamente acopladas - cada etapa depende da saída da anterior completar antes de começar. Se uma etapa falhar, o job inteiro falha e o lote não é gravado. O particionamento por hora no destino sugere que o design foi otimizado para batch, não para streaming.

### RISCOS DA MIGRAÇÃO
- **Alta severidade**: Perda de dados durante a transição. Se mudarmos para event-driven sem garantir que todos os eventos do Relay são consumidos, eventos podem ser descartados se o Relay tiver retenção limitada.
- **Alta severidade**: Falha no modelo contínuo pode não ser detectável imediatamente. No batch, um job falhado é óbvio (nada sai). No event-driven, degradação parcial (10% de eventos perdidos) pode passar despercebida.
- **Média severidade**: As 14 etapas de Spark podem não se adaptar a processamento incremental. Algumas etapas podem depender de ter "todos os dados da hora" para funcionar (ex: agregações, deduplicação).
- **Média severidade**: Dependências (Sentinel, Cerebro, billing) podem não tolerar latência diferente. Se o event-driven entregar dados com latência de 1s em vez de 60min, dashboards podem ficar inconsistentes.
- **Baixa severidade**: Infra atual pode não suportar throughput contínuo. O batch de 40min sugere que a infra foi dimensionada para picos de 1.5h de trabalho a cada hora, não para trabalho constante.

### DEPENDÊNCIAS EXTERNAS
- **Sentinel**: Lê tabelas agregadas do Forge para dashboards de observabilidade. No modelo event-driven, precisaria consumir eventos individuais ou usar views materializadas que são atualizadas continuamente. Pode exigir mudança no Sentinel.
- **Cerebro**: Indexa eventos transformados do Forge. No modelo event-driven, pode indexar em tempo real em vez de em lote, o que pode ser benéfico (buscas mais frescas) mas pode exigir ajuste de throughput.
- **Billing (Pepper)**: Relatórios rodam de madrugada e lêem tabelas agregadas do Forge. O modelo event-driven pode ser transparente se as tabelas continuarem sendo atualizadas (só que mais frequentemente), mas pode haver impacto se os relatórios esperam consistência de snapshot end-of-hour.

### CAPACIDADE E PERFORMANCE
O batch de 60min com 40min de processamento sugere que o volume por hora é significativo (~40min de trabalho Spark a cada hora). A infra atual provavelmente foi dimensionada para isso - clusters Spark que ficam ociosos 20min de cada hora e trabalham 40min. Para throughput contínuo, a infra precisaria trabalhar os 60min constantemente, o que pode exigir:
- Aumento de capacidade (mais workers Spark)
- Reconfiguração de jobs Spark para otimizar throughput contínuo (ex: reduzir shuffle, aumentar paralelismo)
- Revisão de custos - trabalhar constantemente pode custar mais que trabalhar em bursts

O particionamento por hora no destino é compatível com event-driven (partições podem ser criadas incrementalmente), mas pode exigir ajuste para evitar muitos arquivos pequenos (se eventos chegarem um por um em vez de em lote).

### PONTO FRÁGIL: ACÚMULO DE LOTE
O ponto frágil "se um lote falha, o próximo acumula o dobro de volume" indica que o design atual não tem mecanismo de backpressure ou buffering resiliente. Se o job das 10:00 falha, os dados das 10:00 ficam no Relay (ou em algum buffer) e o job das 11:00 tenta processar dados das 10:00 + 11:00 = 2x volume. Isso causa:
- Custo dobrado de processamento (Spark trabalha o dobro)
- Latência dobrada (job demora 80min em vez de 40min)
- Risco de falha em cascata (se 2x volume estoura capacidade, o job das 11:00 também falha, acumulando 3x volume para as 12:00)

Isso sugere que o Relay não tem retenção infinita - se lotes acumularem demais, dados podem ser perdidos. O modelo event-driven mitiga isso processando continuamente, mas apenas se o throughput contínuo for suficiente para o volume médio.

### GAPS DE CONHECIMENTO
- Volume exato de dados por hora (GB ou número de eventos) - necessário para dimensionar infra contínua
- Retenção atual do Relay (quanto tempo os dados ficam no Relay antes de serem descartados) - crítico para garantir que não haverá perda durante transição
- SLAs de dependências (Sentinel, Cerebro, billing) - que latência é aceitável para cada um?
- Janela de manutenção disponível - a migração pode ser feita online ou precisa de downtime?
- Capacidade orçamentária para infra adicional - o orçamento permite aumentar infra para throughput contínuo?

### CONCLUSÃO DO DIAGNÓSTICO
O Forge atual é um pipeline batch monolítico com 14 etapas acopladas em Spark, dimensionado para processar 1h de dados a cada 60min. O maior risco da migração é garantir que nenhum dado seja perdido durante a transição, dado que o design atual acumula volume em caso de falha. Dependências externas (Sentinel, Cerebro, billing) exigem coordenação cuidadosa para continuar funcionando durante a migração. A infra atual pode precisar de ajuste para suportar throughput contínuo em vez de bursts. A migração deve ser incremental com cada etapa sendo reversível para mitigar riscos.

---

### Output do Prompt 2: Planejamento (usando diagnóstico acima)

### ESTRATÉGIA DE TRANSIÇÃO
Abordagem: **Paralelo gradual com dual-write**

A estratégia é rodar batch e event-driven em paralelo por um período, com o Relay fazendo dual-write (envia eventos tanto para o job batch quanto para o novo consumidor event-driven). Isso permite:
- Validar que o event-driven produz os mesmos resultados que o batch
- Manter dependências funcionando (elas continuam lendo do batch)
- Ter rollback imediato (basta parar o event-driven e continuar com batch)
- Comparar outputs lado a lado para garantir consistência

Após validação completa (ex: 1 semana), mudar as dependências para consumir do event-driven e desligar o batch gradualmente.

### ETAPAS DA MIGRAÇÃO

**Etapa 1: Adicionar consumer event-driven ao Relay**
- **Objetivo**: Criar um novo consumidor do Relay que processa eventos continuamente, sem afetar o batch existente
- **Dependências**: Nenhuma - é aditivo ao Relay
- **Risco**: Baixo - batch continua funcionando normalmente
- **Reversibilidade**: Fácil - basta parar o novo consumer
- **Critérios de sucesso**: Consumer event-driven está consumindo eventos, Relay não degradou, batch continua funcionando

**Etapa 2: Implementar transformação incremental em Spark**
- **Objetivo**: Adaptar as 14 etapas de Spark para processar eventos em pequenos blocos (ex: janelas de 1min) em vez de lote de 1h
- **Dependências**: Etapa 1 completa (consumer event-driven existe)
- **Risco**: Alto - algumas etapas podem não funcionar com dados incrementais (ex: agregações que requerem todos os dados da hora)
- **Reversibilidade**: Média - pode voltar ao código batch anterior, mas exige rollback de código
- **Critérios de sucesso**: Cada etapa processa dados incrementais corretamente, outputs são idênticos ao batch para o mesmo período

**Etapa 3: Dual-write para validação**
- **Objetivo**: Rodar batch e event-driven em paralelo por X dias, comparando outputs para garantir consistência
- **Dependências**: Etapa 2 completa (transformação incremental funciona)
- **Risco**: Médio - se houver divergência, pode ser difícil identificar a causa
- **Reversibilidade**: Fácil - parar event-driven e continuar com batch
- **Critérios de sucesso**: Outputs event-driven e batch são idênticos (ou diferença explicável e aceitável) por 7 dias consecutivos

**Etapa 4: Criar views materializadas para dependências**
- **Objetivo**: Criar views/indices que expõem os dados event-driven no formato que dependências esperam (tabelas agregadas para Sentinel, índices para Cerebro)
- **Dependências**: Etapa 3 completa (event-driven validado)
- **Risco**: Médio - views podem ter performance diferente das tabelas batch
- **Reversibilidade**: Fácil - dependências podem voltar a ler das tabelas batch
- **Critérios de sucesso**: Dependências podem consumir das views sem degradação de performance

**Etapa 5: Migrar Cerebro para event-driven**
- **Objetivo**: Mudar Cerebro para consumir do event-driven em vez de ler tabelas batch
- **Dependências**: Etapa 4 completa (views materializadas existem)
- **Risco**: Baixo - Cerebro pode se beneficiar de latência menor
- **Reversibilidade**: Fácil - voltar Cerebro para ler tabelas batch
- **Critérios de sucesso**: Cerebro indexa dados corretamente, latência de busca não piorou (ou melhorou)

**Etapa 6: Migrar Sentinel para event-driven**
- **Objetivo**: Mudar Sentinel para consumir do event-driven em vez de ler tabelas batch
- **Dependências**: Etapa 5 completa (Cerebro migrado com sucesso)
- **Risco**: Médio - Sentinel é crítico para operação
- **Reversibilidade**: Fácil - voltar Sentinel para ler tabelas batch
- **Critérios de sucesso**: Sentinel dashboards funcionam corretamente, latência de alertas não piorou

**Etapa 7: Migrar billing para event-driven**
- **Objetivo**: Mudar relatórios de billing para ler do event-driven
- **Dependências**: Etapa 6 completa (Sentinel migrado com sucesso)
- **Risco**: Baixo - billing roda de madrugada, há janela para correção
- **Reversibilidade**: Fácil - voltar billing para ler tabelas batch
- **Critérios de sucesso**: Relatórios de billing produzem os mesmos valores que antes

**Etapa 8: Desligar batch**
- **Objetivo**: Parar o job batch e o dual-write do Relay
- **Dependências**: Etapa 7 completa (todas dependências migradas)
- **Risco**: Baixo - se houver problema, pode reativar batch rapidamente
- **Reversibilidade**: Fácil - reativar job batch e dual-write
- **Critérios de sucesso**: Tudo continua funcionando sem batch, custo de infra reduziu (batch desligado)

### GAPS DO PLANEJAMENTO
- Duração do período de dual-write (7 dias? 30 dias?) - depende da tolerância a risco do time
- Se alguma etapa de Spark não funcionar com dados incrementais, qual é o plano B? (pode ser necessário reescrever essa etapa)
- Orçamento para infra adicional durante dual-write (rodar batch + event-drive em paralelo dobra custo temporariamente)

### RISCOS CRÍTICOS DA MIGRAÇÃO
- **Risco**: Alguma das 14 etapas de Spark não funciona com dados incrementais (ex: requer windowing completo da hora). **Mitigação**: Identificar essas etapas cedo na Etapa 2 e reescrevê-las se necessário.
- **Risco**: Divergência entre batch e event-driven não é detectada imediatamente. **Mitigação**: Automatizar comparação de outputs com alertas se diferença > 0.1%.
- **Risco**: Infra não suporta throughput contínuo + batch em paralelo. **Mitigação**: Aumentar infra temporariamente durante dual-write, aceitar custo adicional.
- **Risco**: Dependência (ex: Sentinel) tem problema com event-driven e precisa voltar rapidamente. **Mitigação**: Ter rollback script pronto e testado para cada dependência.

### CONCLUSÃO DO PLANEJAMENTO
A migração será feita em 8 etapas incrementais, começando com um consumer event-driven aditivo ao Relay e terminando com o desligamento do batch. A estratégia de dual-write permite validação completa antes de mudar dependências. Cada etapa é reversível, mitigando riscos. O maior desafio técnico é adaptar as 14 etapas de Spark para processamento incremental - algumas etapas podem precisar de reescrita. O planejamento assume que o orçamento permite infra adicional durante o período de dual-write (batch + event-driven em paralelo).

---

### Output do Prompt 3: Plano Executável (usando planejamento acima)

### ESTRATÉGIA DE ROLLBACK GERAL
Cada etapa tem um rollback individual específico. Além disso, existe um **rollback global de emergência**: se múltiplas etapas falharem simultaneamente ou se houver perda de dados, o plano é:
1. Parar todos os consumers event-driven
2. Reativar o job batch forge-batch-ingest (se estiver desligado)
3. Reconfigurar Relay para não enviar para event-driven (se dual-write estiver ativo)
4. Notificar stakeholders via Slack #incidentes
5. Investigar causa em ambiente de staging

Este rollback global deve levar menos de 15 minutos e foi testado em staging.

### PLANO EXECUTÁVEL

**Etapa 1: Adicionar consumer event-driven ao Relay**

**Ações específicas**:
1. Criar novo deployment Kubernetes `forge-event-driven-consumer` no namespace `forge-prod`
2. Configurar consumer para ler do topic `relay-events` do Relay
3. Implementar buffer local no consumer (ex: Kafka local) para garantir que eventos não sejam perdidos se transformação falhar
4. Adicionar métricas de monitoramento: `forge_event_consumer_lag`, `forge_event_consumer_throughput`, `forge_event_consumer_errors`
5. Deploy em staging e testar com carga simulada (1h de volume em 10min)
6. Deploy em produção com 10% do tráfego inicial (usando feature flag)
7. Monitorar por 24h, se estável aumentar para 100% do tráfego

**Duração estimada**: 3 dias (1 dia desenvolvimento, 1 dia staging, 1 dia rollout gradativo)

**Responsáveis**: Engenharia de dados (Bruce Banner), SRE (Sam Wilson)

**Critérios de sucesso**:
- Métrica 1: `forge_event_consumer_lag` < 1000 eventos - medir por 24h
- Métrica 2: `forge_event_consumer_errors` = 0 - medir por 24h
- Métrica 3: Job batch `forge-batch-ingest` continua funcionando normalmente - verificar por 24h

**Rollback plan**:
- **Trigger de rollback**: `forge_event_consumer_errors` > 10 em 5min OU Relay latency aumenta > 20%
- **Ação de rollback**: `kubectl delete deployment forge-event-driven-consumer -n forge-prod`
- **Duração do rollback**: 2 minutos
- **Verificação pós-rollback**: Verificar que Relay latency voltou ao normal e batch continua funcionando

**Riscos desta etapa**:
- Consumer event-driven consome recursos do Relay e degrada performance: mitigação - começar com 10% do tráfego e monitorar
- Buffer local pode estourar se transformação falhar: mitigação - configurar alerta se buffer > 80% capacidade

---

**Etapa 2: Implementar transformação incremental em Spark**

**Ações específicas**:
1. Criar branch `feature/spark-incremental` no repositório do Forge
2. Para cada uma das 14 etapas de Spark:
   a. Analisar se a etapa pode funcionar com dados incrementais
   b. Se sim, adaptar para processar janelas de 1min em vez de lote de 1h
   c. Se não, documentar como reescrever (ex: mudar de aggregação em lote para stream aggregation)
3. Implementar versão incremental das etapas adaptadas
4. Adicionar testes unitários para cada etapa incremental com dados de exemplo
5. Deploy em staging e rodar com 1h de dados históricos, comparar output com batch
6. Se outputs idênticos, marcar etapa como validada

**Duração estimada**: 2 semanas (dependendo de quantas etapas precisam de reescrita)

**Responsáveis**: Engenharia de dados (Bruce Banner)

**Critérios de sucesso**:
- Métrica 1: Todas as 14 etapas têm versão incremental implementada
- Métrica 2: Outputs incrementais são idênticos aos outputs batch (diferença < 0.01%) - testar em staging
- Métrica 3: Performance incremental não é significativamente pior que batch (< 20% slower)

**Rollback plan**:
- **Trigger de rollback**: Qualquer etapa não pode ser adaptada para incremental OU outputs diferem > 0.1%
- **Ação de rollback**: Fechar branch `feature/spark-incremental`, continuar com código batch atual
- **Duração do rollback**: Imediato (não deployou em produção ainda)
- **Verificação pós-rollback**: N/A (rollback é apenas não prosseguir)

**Riscos desta etapa**:
- Algumas etapas não funcionam com dados incrementais: mitigação - identificar cedo e reescrever usando stream aggregation
- Performance incremental é muito pior que batch: mitigação - otimizar Spark (aumentar particionamento, reduzir shuffle)

---

**Etapa 3: Dual-write para validação**

**Ações específicas**:
1. Modificar Relay para enviar eventos tanto para o job batch quanto para o consumer event-driven (dual-write)
2. Criar job de comparação que roda a cada hora e compara:
   - Tabelas batch vs tabelas event-driven (contagem de linhas, soma de métricas)
   - Se diferença > 0.1%, enviar alerta para Slack #forge-migration
3. Ativar dual-write em produção
4. Monitorar por 7 dias (pode estender para 30 dias se time for conservador)
5. Revisar alertas de comparação diariamente

**Duração estimada**: 7-30 dias (período de validação)

**Responsáveis**: Engenharia de dados (Bruce Banner), SRE (Sam Wilson)

**Critérios de sucesso**:
- Métrica 1: Diferença entre batch e event-driven < 0.1% - medir por 7 dias consecutivos
- Métrica 2: Zero alertas críticos de comparação - medir por 7 dias
- Métrica 3: Relay não degradou (latência < baseline + 10%) - medir por 7 dias

**Rollback plan**:
- **Trigger de rollback**: Diferença > 1% OU Relay degradou > 20% OU perda de dados detectada
- **Ação de rollback**: Reconfigurar Relay para parar dual-write (enviar apenas para batch)
- **Duração do rollback**: 5 minutos (config change + reload)
- **Verificação pós-rollback**: Verificar que Relay latency voltou ao normal

**Riscos desta etapa**:
- Dual-write dobra custo de infra (batch + event-driven): mitigação - aceitar custo temporário, justificar como investimento em migração
- Divergência não é detectada: mitigação - automação de comparação com múltiplas métricas (contagem, soma, min, max)

---

**Etapa 4: Criar views materializadas para dependências**

**Ações específicas**:
1. Criar views materializadas no data warehouse que agregam dados event-driven no mesmo formato das tabelas batch
2. Para Sentinel: view que replica tabelas agregadas que o Sentinel lê hoje
3. Para Cerebro: view que expõe eventos transformados no formato que Cerebro indexa
4. Para billing: view que replica tabelas de faturamento
5. Testar cada view em staging comparando queries com tabelas batch
6. Deploy em produção

**Duração estimada**: 1 semana

**Responsáveis**: Engenharia de dados (Bruce Banner)

**Critérios de sucesso**:
- Métrica 1: Views retornam os mesmos dados que tabelas batch (query checksum idêntico)
- Métrica 2: Latência de queries nas views não é > 2x latência de tabelas batch
- Métrica 3: Views são atualizadas em < 5min após novos dados chegarem

**Rollback plan**:
- **Trigger de rollback**: Views têm performance ruim (> 5x latência batch) OU retornam dados incorretos
- **Ação de rollback**: Drop views, dependências continuam lendo tabelas batch
- **Duração do rollback**: 5 minutos
- **Verificação pós-rollback**: Verificar que dependências continuam funcionando

**Riscos desta etapa**:
- Views têm performance pior que tabelas batch: mitigação - otimizar views (indexes, particionamento)
- Views não são atualizadas em tempo real: mitigação - configurar refresh schedule (ex: a cada 1min)

---

**Etapa 5: Migrar Cerebro para event-driven**

**Ações específicas**:
1. Atualizar configuração do Cerebro para ler da view materializada event-driven em vez da tabela batch
2. Deploy em staging, testar indexação com dados event-driven
3. Deploy em produção
4. Monitorar latência de busca e throughput de indexação por 24h

**Duração estimada**: 2 dias

**Responsáveis**: Engenharia de dados (Bruce Banner), Time do Cerebro

**Critérios de sucesso**:
- Métrica 1: Cerebro indexa dados corretamente (contagem de documentos indexados = esperado)
- Métrica 2: Latência de busca p99 não piorou (ou melhorou)
- Métrica 3: Zero erros de indexação por 24h

**Rollback plan**:
- **Trigger de rollback**: Latência de busca p99 aumentou > 50% OU erros de indexação > 10/hora
- **Ação de rollback**: Reverter configuração do Cerebro para ler tabela batch
- **Duração do rollback**: 10 minutos (config change + reload)
- **Verificação pós-rollback**: Verificar que latência de busca voltou ao normal

**Riscos desta etapa**:
- Cerebro tem performance pior com event-driven: mitigação - se pior, investigar otimização da view
- Cerebro não indexa dados corretamente: mitigação - rollback imediato, investigar bug na view

---

**Etapa 6: Migrar Sentinel para event-driven**

**Ações específicas**:
1. Atualizar configuração do Sentinel para ler da view materializada event-driven em vez da tabela batch
2. Deploy em staging, testar dashboards com dados event-driven
3. Deploy em produção com 10% dos tenants inicialmente
4. Monitorar dashboards e alertas por 24h
5. Se estável, aumentar para 50%, depois 100%

**Duração estimada**: 3 dias (rollout gradativo)

**Responsáveis**: Engenharia de dados (Bruce Banner), Time do Sentinel, SRE (Sam Wilson)

**Critérios de sucesso**:
- Métrica 1: Dashboards do Sentinel mostram dados corretos (validação manual)
- Métrica 2: Latência de alertas não piorou (ou melhorou)
- Métrica 3: Zero erros de consulta por 24h

**Rollback plan**:
- **Trigger de rollback**: Dashboards incorretos OU latência de alertas aumentou > 30% OU erros > 5/hora
- **Ação de rollback**: Reverter configuração do Sentinel para ler tabela batch
- **Duração do rollback**: 5 minutos (config change)
- **Verificação pós-rollback**: Verificar que dashboards voltaram ao normal

**Riscos desta etapa**:
- Sentinel é crítico, qualquer problema afeta operação: mitigação - rollout gradativo (10% → 50% → 100%)
- Latência diferente pode causar inconsistência em dashboards: mitigação - testar extensivamente em staging

---

**Etapa 7: Migrar billing para event-driven**

**Ações específicas**:
1. Atualizar job de billing para ler da view materializada event-driven
2. Rodar job de billing em staging com dados event-driven, comparar valores com batch
3. Agendar próximo job de billing em produção usando event-driven (job roda de madrugada)
4. Comparar resultados com batch anterior
5. Se idênticos, confirmar migração

**Duração estimada**: 1 dia (job roda de madrugada)

**Responsáveis**: Engenharia de dados (Bruce Banner), Financeiro (Pepper)

**Critérios de sucesso**:
- Métrica 1: Relatório de billing produz os mesmos valores que batch (diferença < $0.01)
- Métrica 2: Job de billing completa em tempo habitual
- Métrica 3: Zero erros

**Rollback plan**:
- **Trigger de rollback**: Valores de billing diferem > $1 OU job falha
- **Ação de rollback**: Reconfigurar job de billing para ler tabela batch, rerun job
- **Duração do rollback**: 30 minutos (rerun job)
- **Verificação pós-rollback**: Verificar que valores batem com batch anterior

**Riscos desta etapa**:
- Billing é crítico para negócio: mitigação - rodar de madrugada quando há janela para correção
- Valores incorretos podem ter impacto financeiro: mitigação - comparação rigorosa com batch antes de aceitar

---

**Etapa 8: Desligar batch**

**Ações específicas**:
1. Verificar que todas as dependências estão consumindo de event-driven há pelo menos 7 dias sem problemas
2. Parar job cron `forge-batch-ingest`
3. Remover dual-write do Relay (enviar apenas para event-driven)
4. Remover tabelas batch obsoletas (após backup)
5. Reduzir infra se aplicável (parar clusters Spark usados apenas para batch)

**Duração estimada**: 1 dia

**Responsáveis**: Engenharia de dados (Bruce Banner), SRE (Sam Wilson)

**Critérios de sucesso**:
- Métrica 1: Todas as dependências continuam funcionando sem batch
- Métrica 2: Custo de infra reduziu (batch desligado)
- Métrica 3: Zero erros por 7 dias após desligamento

**Rollback plan**:
- **Trigger de rollback**: Qualquer dependência falha após desligamento
- **Ação de rollback**: Reativar job batch e dual-write do Relay
- **Duração do rollback**: 15 minutos
- **Verificação pós-rollback**: Verificar que dependências voltaram ao normal

**Riscos desta etapa**:
- Alguma dependência tinha problema silencioso com event-driven: mitigação - monitoramento extensivo por 7 dias antes de desligar batch
- Infra event-driven não suporta carga sozinha: mitigação - manter clusters Spark extras por 30 dias após desligamento como safety net

---

### COMUNICAÇÃO E COORDENAÇÃO
- **Stakeholders a notificar**: Tony Stark (CTO), Pepper Potts (CEO), Carol Danvers (Head of Product), Sam Wilson (SRE), Bruce Banner (Engenharia de Dados)
- **Canal de comunicação**: Slack #forge-migration (público para time) + email semanal para stakeholders
- **Frequência de atualização**: Update no Slack a cada etapa concluída, email semanal resumindo progresso
- **Critérios para abortar a migração**: Perda de dados detectada OU múltiplas etapas falharem consecutivamente OR custo de infra exceder orçamento em > 20%

### MÉTRICAS DE MONITORAMENTO
- `forge_event_consumer_lag` - alerta se > 10k eventos
- `forge_event_consumer_throughput` - alerta se < 90% do esperado
- `forge_event_consumer_errors` - alerta se > 5/hora
- `forge_batch_vs_event_diff` - alerta se diferença > 0.5%
- `relay_latency` - alerta se > baseline + 20%
- `spark_job_duration` - alerta se > 2x baseline
- `sentinel_query_latency` - alerta se > baseline + 30%
- `cerebro_search_latency` - alerta se > baseline + 30%

### SUPORTES DE CONTINGÊNCIA
- **Se a migração falhar na etapa X**: Reverter à etapa X-1 e investigar causa em staging. Não prosseguir até causa ser identificada e mitigada.
- **Se o rollback falhar**: Ativar rollback global de emergência (parar tudo, reativar batch, notificar stakeholders).
- **Se houver perda de dados**: Parar migração imediatamente, investigar Relay logs para identificar período de perda, notificar stakeholders afetados, considerar compensação se for cliente externo.

### CRONOGRAMA RESUMIDO
- Etapa 1: Semana 1 (3 dias)
- Etapa 2: Semanas 2-3 (2 semanas)
- Etapa 3: Semanas 4-6 (3 semanas validação)
- Etapa 4: Semana 7 (1 semana)
- Etapa 5: Semana 8 (2 dias)
- Etapa 6: Semana 9 (3 dias)
- Etapa 7: Semana 10 (1 dia)
- Etapa 8: Semana 11 (1 dia)
- Conclusão: Semana 11 (total ~11 semanas)

---

## Curadoria

### Técnica/Framework escolhido
- **Encadeamento de Prompts (Prompt Chaining)**: Dividi a migração em 3 prompts sequenciais, cada um usando a saída do anterior. Isso evita um prompt monolítico que seria raso e genérico.
- **Progressive Disclosure**: Prompt 1 foca em diagnóstico, Prompt 2 em planejamento, Prompt 3 em execução. Cada prompt adiciona complexidade gradualmente.
- **Role Prompting**: Defini o modelo como "arquiteto de dados sênior" em todos os prompts para manter consistência de contexto.

### Por que encadear em vez de um prompt único?
Um prompt único tentando cobrir diagnóstico + planejamento + execução seria:
- Muito longo (alta chance de o modelo perder detalhes)
- Raso (cada aspecto teria menos profundidade)
- Difícil de iterar (se o planejamento estiver ruim, teria que refazer tudo)
- Mais propenso a alucinação (mais contexto para o modelo gerar inconsistências)

Com encadeamento:
- Cada prompt tem foco claro e tamanho gerenciável
- A saída de um prompt valida a entrada do próximo
- É possível iterar em um elo sem refazer toda a cadeia
- O modelo "pensa" em etapas, refletindo o processo humano real

### Refinamentos feitos
1. **Iteração 1**: Prompt 1 inicial não tinha seção "Gaps de Conhecimento". Adicionei para que o modelo identificasse o que não sabe, permitindo que prompts posteriores façam suposições explícitas.
2. **Iteração 2**: Prompt 2 não enfatizava reversibilidade. Adicionei instrução "A reversibilidade não é opcional" e exigir rollback plan para cada etapa.
3. **Iteração 3**: Prompt 3 não era específico o suficiente nas ações. Adicionei instrução "Seja específico nas ações - 'fazer X' é vago, 'rodar kubectl apply' é específico".
4. **Iteração 4**: Adicionei seção "Estratégia de Rollback Geral" no Prompt 3 para fornecer um safety net além dos rollbacks individuais.

### Sanitização de dados
O cenário contém:
- Estrutura do pipeline (14 etapas Spark, job cron) - não sensível
- Nomes de sistemas genéricos (Forge, Sentinel, Cerebro) - não sensível
- Nomes de pessoas fictícias (Bruce Banner, Pepper, Sam) - não sensível
- **Decisão**: Não há dados sensíveis. Pode enviar para modelo externo sem sanitização.

### Avaliação final
A cadeia satisfaz os requisitos:
- ✓ Cada prompt é parametrizável (recebe saída do anterior)
- ✓ A migração é quebrada em etapas (não big-bang)
- ✓ Cada etapa é reversível
- ✓ Quem depende do Forge continua funcionando durante transição
- ✓ O plano é executável (ações específicas, métricas, rollback)
- ✓ O raciocínio é progressivo (diagnóstico → planejamento → execução)
