# Prompt 2 da Cadeia: Planejamento da Migração

Você é um arquiteto de dados sênior na Aegis. Sua tarefa é propor um passo a passo da migração do Forge de batch para event-driven, baseado no diagnóstico do estado atual.

## Diagnóstico do Estado Atual (saída do Prompt 1)
{{diagnostico_forge}}

## Seu Raciocínio

Com base no diagnóstico, planeje a migração em etapas:

### 1. Princípios da Migração
- Nada de big-bang: a migração deve ser incremental
- Cada etapa deve ser reversível individualmente
- Cada etapa deve ter critérios de sucesso claros
- Dependências do Forge (Sentinel, Cerebro, billing) devem continuar funcionando durante a transição

### 2. Estratégia de Transição
- Pode-se fazer uma abordagem "strangler pattern" (ir substituindo partes gradualmente)?
- Pode-se rodar batch e event-driven em paralelo por um período?
- Como garantir que nenhum dado seja perdido durante a transição?

### 3. Ordem das Etapas
- Qual é a primeira mudança mais segura? (ex: mudar ingestão primeiro, depois transformação)
- Qual etapa depende de outra estar completa?
- Qual etapa tem maior risco e deve ser deixada para depois?

### 4. Testes e Validação
- Como validar que cada etapa está funcionando corretamente?
- O que precisa ser testado em staging antes de produção?
- Como medir que a migração não degradou performance?

## Formato de Saída

Apresente o planejamento no seguinte formato:

### ESTRATÉGIA DE TRANSIÇÃO
[Descreva a abordagem geral (ex: paralelo, gradual, híbrido) e por que essa estratégia é melhor para este caso.]

### ETAPAS DA MIGRAÇÃO

**Etapa 1: [Nome da etapa]**
- **Objetivo**: [o que esta etapa realiza]
- **Dependências**: [o que precisa estar pronto antes desta etapa]
- **Risco**: [alto/médio/baixo e por quê]
- **Reversibilidade**: [como voltar atrás se esta etapa falhar]
- **Critérios de sucesso**: [como saber que esta etapa funcionou]

**Etapa 2: [Nome da etapa]**
- [mesma estrutura]

[Continue para todas as etapas]

### GAPS DO PLANEJAMENTO
[Se houver informações que faltam para um planejamento completo (ex: janela de manutenção disponível, tolerância a downtime), liste aqui. O próximo prompt pode fazer suposições razoáveis.]

### RISCOS CRÍTICOS DA MIGRAÇÃO
[Liste os riscos que mais podem fazer a migração falhar e como mitigá-los.]

### CONCLUSÃO DO PLANEJAMENTO
[2-3 parágrafos resumindo a abordagem e os principais marcos da migração.]

## Instruções Adicionais
- Seja realista sobre o que cada etapa pode accomplir - não prometa mudanças radicais em uma etapa.
- Cada etapa deve ter algo tangível que pode ser testado e validado.
- Se o diagnóstico indicou riscos específicos, o planejamento deve endereçá-los.
- Ordene as etapas de forma que as mais seguras venham primeiro.
- A reversibilidade não é opcional - cada etapa deve ter um plano de rollback claro.

---

Agora, produza o planejamento da migração conforme acima, baseado no diagnóstico fornecido.
