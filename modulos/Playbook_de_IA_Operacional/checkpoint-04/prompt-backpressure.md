# Prompt Parametrizável: Análise de Estratégia de Backpressure

Você é um arquiteto de sistemas na Aegis. Sua tarefa é analisar um cenário de sobrecarga no Relay (barramento de eventos) e comparar múltiplas abordagens de backpressure, pesando prós e contras antes de recomendar uma solução.

## Cenário
{{cenario_relay}}

## Restrições e SLAs
- Alerting do Sentinel não pode atrasar mais que 60s (SLA com cliente)
- Ingestão do Forge pode atrasar até 15min sem violar SLA
- Orçamento de infra do trimestre já está 8% acima do previsto
- Perda de telemetry é inaceitável (histórico de perda no barramento antigo)

## Abordagens a Comparar

### 1. Priorização de Tráfego (Priority Queues)
Dar prioridade ao Sentinel (alerting em tempo real) na frente do Forge (ingestão que pode esperar até 15min).

### 2. Dead-Letter Queue (DLQ)
Guardar o que não foi processado numa fila separada para reprocessar depois, mantendo a fila principal limpa.

### 3. Particionamento por Cliente (Tenant Isolation)
Dividir o Relay por cliente, para que um cliente barulhento não atrapalhe os outros (multi-tenancy explícito).

### 4. Auto-scaling de Consumidores
Aumentar automaticamente o número de consumidores quando a carga sobe (horizontal scaling reativo).

## Seu Raciocínio

Para cada abordagem, analise:

### Critérios de Avaliação
1. **Aderência aos SLAs**: A solução respeita o SLA de 60s para Sentinel e 15min para Forge?
2. **Custo**: A solução exige infra adicional? Impacto no orçamento já 8% acima?
3. **Risco de perda de dados**: A solução pode resultar em perda de telemetry em algum cenário?
4. **Complexidade de implementação**: Quanto esforço de engenharia é necessário?
5. **Reversibilidade**: Se a solução não funcionar, é fácil voltar atrás?
6. **Escalabilidade futura**: A solução escala para picos maiores que o observado (320k msgs/s)?

### Processo de Comparação
1. Liste os prós de cada abordagem
2. Liste os contras de cada abordagem
3. Avalie cada abordagem contra os 6 critérios acima
4. Identifique combinações possíveis (ex: priorização + DLQ)
5. Descarte abordagens que violam restrições críticas (ex: perda de dados)
6. Ordene as abordagens restantes por custo-benefício
7. Recomende a melhor abordagem (ou combinação) com justificativa detalhada

## Formato de Saída

Apresente sua análise no seguinte formato:

### ABORDAGEM 1: [Nome da abordagem]
**Prós**:
- [pró 1]
- [pró 2]

**Contras**:
- [contra 1]
- [contra 2]

**Avaliação por critério**:
- SLAs: [atende/não atende/explicação]
- Custo: [baixo/médio/alto e por quê]
- Risco de perda: [baixo/médio/alto e por quê]
- Complexidade: [baixa/média/alta e por quê]
- Reversibilidade: [fácil/médio/difícil e por quê]
- Escalabilidade: [boa/média/ruim e por quê]

[Repita para cada abordagem]

### COMBINAÇÕES POSSÍVEIS
[Se houver combinações de abordagens que façam sentido, descreva aqui. Se não, indique "Nenhuma combinação recomendada".]

### ABORDAGENS DESCARTADAS
[Liste abordagens que violam restrições críticas (ex: perda de dados) e explique por que foram descartadas.]

### RECOMENDAÇÃO FINAL
**Abordagem recomendada**: [nome da abordagem ou combinação]

**Justificativa**:
[2-3 parágrafos explicando por que esta é a melhor escolha. Cite explicitamente os critérios que pesaram mais na decisão e como as alternativas foram piores nesses critérios.]

**Plano de implementação (alto nível)**:
1. [passo 1]
2. [passo 2]
3. [passo 3]

**Riscos e mitigações**:
- [risco 1]: [mitigação]
- [risco 2]: [mitigação]

## Instruções Adicionais
- Não pule para recomendação - mostre o trabalho de comparação.
- Seja específico ao avaliar custo: "requer X instâncias adicionais de tipo Y, custo estimado de $Z/mês".
- Seja honesto sobre trade-offs: toda solução tem prós e contras.
- Se mais de uma abordagem for defensável, discuta as duas e justifique sua escolha.
- A recomendação deve ser algo que o time pode implementar com esforço razoável (não um rewrite completo).

---

Agora, analise o cenário fornecido e produza a comparação de abordagens conforme acima.
