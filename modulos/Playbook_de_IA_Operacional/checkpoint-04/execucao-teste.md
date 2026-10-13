# Checkpoint 04 - Execução e Resultados

## Prompt Parametrizável
Ver arquivo: `prompt-backpressure.md`

## Parâmetros
- `{{cenario_relay}}`: Descrição do estado atual do Relay + restrições do time

## Cenário Fornecido

**Relay (barramento de eventos)**:
- throughput sustentado: 180k msgs/s
- pico observado no incidente da semana passada: 320k msgs/s por 25min
- retenção atual: 4h
- consumidores: Forge (ingestão), Sentinel (alerting em tempo real)

**Restrições do time**:
- alerting do Sentinel não pode atrasar mais que 60s (SLA com cliente)
- ingestão do Forge pode atrasar até 15min sem violar SLA
- orçamento de infra do trimestre já está 8% acima do previsto
- Steve Rogers lembra que o barramento antigo perdia mensagens sob pico, e perda de telemetry é inaceitável para um produto de observabilidade

## Execução

**Modelo usado**: Claude Sonnet 4 (Anthropic)
**Justificativa**: Tarefa de análise comparativa exigindo raciocínio sobre trade-offs (custo, complexidade, risco, SLAs). Claude Sonnet 4 tem excelente desempenho em raciocínio de decisão com múltiplos critérios. Custo moderado (~$3/1M input tokens) é aceitável para a complexidade da tarefa. Privacidade: dados são genéricos (throughput, SLAs) - não há informações sensíveis. Pode enviar para modelo externo.

**Output esperado**:

### ABORDAGEM 1: Priorização de Tráfego (Priority Queues)
**Prós**:
- Implementação relativamente simples (fila única com múltiplas prioridades)
- Garante que Sentinel (crítico) sempre tem precedência sobre Forge (pode esperar)
- Baixo custo adicional (mudança lógica, não infra nova)
- Fácil de testar e monitorar

**Contras**:
- Forge pode ficar muito atrasado se o pico for prolongado (viola 15min em cenários extremos)
- Não resolve o problema de capacidade global - se tudo estourar, nada é processado
- Requer mudança no código de consumidores para respeitar prioridade
- Se a prioridade for mal configurada, pode causar starvation do Forge

**Avaliação por critério**:
- SLAs: Atende parcialmente. Sentinel sempre tem prioridade, mas Forge pode exceder 15min em picos prolongados.
- Custo: Baixo. Mudança de software, sem infra adicional.
- Risco de perda: Baixo. Fila continua com retenção de 4h, nada é descartado.
- Complexidade: Média. Requer mudança em Relay e consumidores, mas conceito é bem conhecido.
- Reversibilidade: Fácil. Pode voltar a fila FIFO simples com rollback de código.
- Escalabilidade: Média. Não aumenta capacidade total, apenas distribui melhor o que existe.

### ABORDAGEM 2: Dead-Letter Queue (DLQ)
**Prós**:
- Permite que a fila principal continue fluindo enquanto excesso é separado
- DLQ pode ser reprocessada posteriormente sem perda de dados
- Isola problemas de "bad tenants" ou eventos problemáticos
- Padrão bem estabelecido em sistemas de mensageria

**Contras**:
- Adiciona complexidade significativa (duas filas, lógica de reprocessamento)
- Requer infra adicional para DLQ (armazenamento extra)
- Reprocessamento pode gerar pico secundário se não for bem controlado
- Custo aumenta com retenção (DLQ também precisa de armazenamento)
- Se DLQ crescer demais, pode virar problema em si

**Avaliação por critério**:
- SLAs: Atende. Fila principal continua processando normalmente, DLQ é assíncrona.
- Custo: Médio. Requer infra adicional para DLQ (estimativa: +20% custo de Relay atual).
- Risco de perda: Baixo. DLQ retém tudo, nada é descartado.
- Complexidade: Alta. Requer implementação de DLQ, monitoramento, lógica de reprocessamento.
- Reversibilidade: Média. Uma vez implementado, remover DLQ requer migração de dados.
- Escalabilidade: Boa. DLQ absorve picos, mas requer capacidade de reprocessamento.

### ABORDAGEM 3: Particionamento por Cliente (Tenant Isolation)
**Prós**:
- Isola completamente clientes barulhentos de afetar outros
- Permite aplicar limites por cliente (rate limiting per-tenant)
- Facilita billing e chargeback (cada cliente tem seu uso claro)
- Se um cliente explode, só ele sofre - outros continuam normais

**Contras**:
- Complexidade muito alta (mudança arquitetural significativa)
- Requer infra multiplicada (múltiplas filas/partições por cliente)
- Custo escala com número de clientes (não é linear)
- Difficult forecasting de capacidade (cada cliente tem padrão diferente)
- Requer descoberta dinâmica de clientes e roteamento

**Avaliação por critério**:
- SLAs: Atende bem. Clientes normais não são afetados por clientes barulhentos.
- Custo: Alto. Infra multiplica por número de clientes ativos (estimativa: +50-100% custo atual).
- Risco de perda: Baixo. Isolamento impede que um cliente afete outros, mas o cliente afetado pode ter perda se sua fila estourar.
- Complexidade: Muito alta. Mudança arquitetural major, requer meses de trabalho.
- Reversibilidade: Difícil. Uma vez particionado, voltar a monolito é praticamente impossível.
- Escalabilidade: Excelente se bem implementado, mas custo é proibitivo.

### ABORDAGEM 4: Auto-scaling de Consumidores
**Prós**:
- Responde automaticamente a picos de carga
- Não requer priorização manual ou particionamento
- Escala horizontal conforme necessário
- Pode ser desligado quando não há pico (economia em horários normais)

**Contras**:
- Latência de scaling (pode levar minutos para novos consumidores estarem prontos)
- Custo aumenta proporcionalmente ao pico (se pico for 320k, escala para isso mesmo se for breve)
- Orçamento já está 8% acima - auto-scaling pode exceder ainda mais
- Requer infra com capacidade de scale rápido (ex: Kubernetes HPA, mas nodes precisam estar disponíveis)
- Se nodes não estiverem disponíveis, auto-scaling não funciona (cluster pode estar no limite)

**Avaliação por critério**:
- SLAs: Atende se cluster tiver capacidade. Se nodes estiverem no limite, auto-scaling falha.
- Custo: Alto/Escalável. Custo acompanha pico - no incidente de 25min a 320k msgs/s, custo triplicaria momentaneamente.
- Risco de perda: Médio. Se auto-scaling falhar (sem nodes), fila pode estourar.
- Complexidade: Média. HPA e autoscaling são padrão, mas requer monitoramento e tuning.
- Reversibilidade: Fácil. Pode desabilitar auto-scaling e voltar a capacidade fixa.
- Escalabilidade: Boa se infra subjacente permitir. Limitada por disponibilidade de nodes.

### COMBINAÇÕES POSSÍVEIS
**Priorização + Auto-scaling limitado**: Implementar priority queues para garantir que Sentinel sempre tem precedência, e auto-scaling com teto de custo (ex: não escalar além de 200k msgs/s para controlar orçamento). Pico acima disso é absorvido pela fila de retenção de 4h e reprocessado depois.

**Priorização + DLQ**: Priority queues para garantir SLA do Sentinel, e DLQ para capturar excesso que não cabe na fila principal. DLQ é reprocessada quando carga normaliza.

### ABORDAGENS DESCARTADAS
**Particionamento por Cliente (Tenant Isolation)**: Descartada por custo proibitivo (+50-100% infra) e complexidade muito alta (mudança arquitetural major). O orçamento já está 8% acima do previsto, e o time não tem meses para implementar isolamento completo. O problema (pico de 320k por 25min) é temporário, não estrutural - isolamento por cliente é overengineering para este caso.

### RECOMENDAÇÃO FINAL
**Abordagem recomendada**: Priorização de Tráfego (Priority Queues) + Auto-scaling limitado

**Justificativa**:
A combinação de priority queues com auto-scaling limitado oferece o melhor equilíbrio entre aderência aos SLAs, custo e complexidade. Priority queues garantem que o Sentinel (SLA de 60s) sempre tem precedência sobre o Forge (SLA de 15min), endereçando a restrição mais crítica. Auto-scaling com teto de custo (ex: escalar até 250k msgs/s, não 320k) permite responder a picos moderados sem estourar o orçamento já pressionado. O pico de 320k msgs/s no incidente anterior durou apenas 25min - o excesso acima do teto seria absorvido pela fila de retenção de 4h e reprocessado quando carga normaliza, sem perda de dados.

Esta combinação tem custo baixo (mudança de software, infra mínima adicional), complexidade média (priority queues são padrão, auto-scaling é HPA nativo do Kubernetes), e é facilmente reversível. Alternativas como particionamento por cliente têm custo e complexidade proibitivos para o orçamento e timeframe. DLQ isolado adiciona complexidade sem ganho claro se já temos fila de retenção de 4h - o excesso pode ficar na fila principal até ser processado.

**Plano de implementação (alto nível)**:
1. Implementar priority queues no Relay (duas filas: alta prioridade para Sentinel, baixa para Forge)
2. Configurar HPA (Horizontal Pod Autoscaler) para consumidores com teto de custo (ex: máximo de 25 réplicas vs 10 atuais)
3. Adicionar métricas de monitoramento: tamanho de cada fila de prioridade, latência de cada consumidor, custo em tempo real
4. Testar em staging com carga simulada de pico (320k msgs/s por 30min)
5. Rollout gradativo em produção, começando com 10% do tráfego

**Riscos e mitigações**:
- **Risco**: Auto-scaling pode não ter nodes disponíveis se cluster estiver no limite. **Mitigação**: Configurar cluster autoscaler para garantir nodes de reserva, ou aceitar que pico acima do teto ficará na fila de retenção.
- **Risco**: Priority queues podem causar starvation do Forge se pico for prolongado. **Mitigação**: Monitorar tempo de espera do Forge e ajustar dinamicamente a proporção de prioridade (ex: 70/30 em normal, 90/10 em pico).
- **Risco**: Custo de auto-scaling pode exceder orçamento se picos forem frequentes. **Mitigação**: Teto de custo rígido com alerta se atingido, revisão de orçamento no próximo trimestre.

---

## Curadoria

### Técnica/Framework escolhido
- **Análise Comparativa Estruturada**: Forcei o modelo a listar prós/contras de cada abordagem e avaliar em 6 critérios explícitos antes de recomendar. Isso evita resposta apressada e garante que trade-offs sejam considerados.
- **Requisito de Justificativa Detalhada**: Exigi que a recomendação explique por que as alternativas foram piores nos critérios que pesaram mais.
- **Role Prompting**: Defini o modelo como "arquiteto de sistemas" para alinhar o nível de decisão.

### Refinamentos feitos
1. **Iteração 1**: Prompt inicial não especificava critérios de avaliação. O modelo estava usando critérios vagos. Adicionei 6 critérios explícitos (SLAs, custo, risco de perda, complexidade, reversibilidade, escalabilidade).
2. **Iteração 2**: O modelo não estava avaliando custo especificamente. Adicionei instrução "Seja específico ao avaliar custo: requer X instâncias adicionais de tipo Y, custo estimado de $Z/mês".
3. **Iteração 3**: O modelo estava ignorando combinações de abordagens. Adicionei seção "Combinações Possíveis" para incentivar pensamento sintético.
4. **Iteração 4**: Adicionei seção "Abordagens Descartadas" para forçar o modelo a justificar por que não escolheu certas opções (ex: particionamento por cliente).

### Sanitização de dados
O cenário contém:
- Métricas de throughput (180k, 320k msgs/s) - não sensíveis
- SLAs (60s, 15min) - não sensíveis
- Orçamento (8% acima) - não sensível
- Nomes de sistemas genéricos (Relay, Forge, Sentinel)
- **Decisão**: Não há dados sensíveis. Pode enviar para modelo externo sem sanitização.

### Avaliação final
O prompt satisfaz os requisitos:
- ✓ Parametrizável (recebe {{cenario_relay}})
- ✓ Compara múltiplas abordagens (4 abordagens listadas)
- ✓ Pesa prós e contras de cada uma
- ✓ Avalia contra restrições (SLAs, custo, perda de dados)
- ✓ Não cuspe resposta única - mostra processo de decisão
- ✓ Inclui análise de combinações
- ✓ Justifica abordagens descartadas
- ✓ Recomenda com justificativa detalhada
