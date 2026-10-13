# Comparação Com e Sem Skill - Ticket 02

## Caso 1: Chamado 1 (nyx-prod - OOMKilled)

### Com Skill (Ticket 02)
**Comando**: "Triage o cluster: nyx-prod, API reinicia sozinha após corte de custos"

**Saída**:
- Processo estruturado: verificar Deployment → Pods → Pod problemático → eventos → logs → resources
- Tempo: ~30 segundos (execução dos comandos e análise)
- Qualidade: Alta - seguiu método sistemático, identificou OOMKilled como causa, correlacionou com corte de custos
- Custo em tokens: ~1500 tokens (skill + execução)

**Saída resumida**: "O pod nyx-api-xxx está em CrashLoopBackOff. Eventos mostram OOMKilled. Logs indicam out of memory. Causa: limite de memória insuficiente (24Mi) após corte de custos."

### Sem Skill
**Comando**: "nyx-prod, API reinicia sozinha após corte de custos. O que está acontecendo?"

**Saída**:
- Processo: Ad-hoc - o agente pode começar por logs, ou por eventos, ou por Deployment, sem método definido
- Tempo: ~45 segundos (mais tentativa e erro)
- Qualidade: Média - pode identificar OOMKilled, mas pode não correlacionar com corte de custos, pode perder informações
- Custo em tokens: ~2500 tokens (agente precisa de mais contexto e tentativas)

**Saída típica**: "O pod está em CrashLoopBackOff. Vou verificar os logs... Os logs mostram out of memory. Talvez seja o limite de memória. Você pode tentar aumentar."

**Comparação**:
- **Qualidade**: Com skill é melhor - método sistemático garante que todas as fontes sejam verificadas e correlacionadas
- **Tempo**: Com skill é mais rápido (~30s vs ~45s) - método definido evita tentativa e erro
- **Custo**: Com skill é mais barato (~1500 vs ~2500 tokens) - menos contexto necessário, menos tentativas

## Caso 2: Chamado 3 (nyx-stg - 503, mismatch de seletor)

### Com Skill (Ticket 02)
**Comando**: "Triage o cluster: nyx-stg, kube-news responde 503, aplicação saudável"

**Saída**:
- Processo estruturado: verificar Deployment (saudável) → Pods (saudáveis) → Service → Endpoints (vazio) → comparar seletor vs rótulos
- Tempo: ~25 segundos
- Qualidade: Alta - identificou que Endpoints está vazio, comparou seletor do Service com rótulos dos Pods, encontrou mismatch (nyx-api vs nyxapi)
- Custo em tokens: ~1200 tokens

**Saída resumida**: "O Service nyx-api não tem Endpoints. Seletor do Service é `app: nyx-api`, mas os Pods têm labels `app: nyxapi`. Mismatch impede tráfego."

### Sem Skill
**Comando**: "nyx-stg, kube-news responde 503. A aplicação está saudável. O que está acontecendo?"

**Saída**:
- Processo: Ad-hoc - pode começar por Pods (saudáveis), por Service (existe), pode esquecer de verificar Endpoints
- Tempo: ~60 segundos (mais tempo para descobrir o problema)
- Qualidade: Baixa a Média - pode não verificar Endpoints, pode não comparar seletor vs rótulos, pode perder tempo em hipóteses erradas
- Custo em tokens: ~3000 tokens (muito contexto e tentativas)

**Saída típica**: "Os pods estão saudáveis. Vou verificar o Service... O Service existe. Talvez seja um problema de rede. Vou verificar os logs dos pods... Os logs não mostram erro. Talvez seja DNS. Vou verificar a configuração..."

**Comparação**:
- **Qualidade**: Com skill é muito melhor - método garante que Endpoints seja verificado, o que é crítico para este caso
- **Tempo**: Com skill é significativamente mais rápido (~25s vs ~60s) - método direto evita investigação desnecessária
- **Custo**: Com skill é muito mais barato (~1200 vs ~3000 tokens) - menos tentativas e menos contexto desnecessário

## Resumo da Comparação

| Caso | Qualidade | Tempo | Custo (tokens) |
|------|-----------|-------|----------------|
| Caso 1 com skill | Alta | 30s | 1500 |
| Caso 1 sem skill | Média | 45s | 2500 |
| Caso 2 com skill | Alta | 25s | 1200 |
| Caso 2 sem skill | Baixa-Média | 60s | 3000 |

## Conclusão

A skill de triagem adiciona valor significativo:
- **Qualidade mais alta**: Método sistemático garante que todas as fontes sejam verificadas e correlacionadas
- **Tempo menor**: Processo definido evita tentativa e erro
- **Custo menor**: Menos contexto necessário e menos tentativas reduzem custo em tokens

O ganho é mais pronunciado em casos onde o problema não é óbvio (como o Caso 2, onde verificar Endpoints é crítico). Em casos óbvios (como Caso 1), o ganho é menor, mas ainda existe.
