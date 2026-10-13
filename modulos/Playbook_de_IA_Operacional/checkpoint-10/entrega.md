# Checkpoint 10 - O Playbook em Produção Contínua

## Arquivo de Workflow do GitHub Actions

`.github/workflows/prompt-tests.yml`

### Estrutura
- Trigger: pull_request e push para branch main
- Job único: `prompt-tests` roda em ubuntu-latest
- Passos:
  1. Checkout do repositório
  2. Setup Node.js 20
  3. Install promptfoo via npm
  4. Roda testes para cada prompt com promptfooconfig.yaml
  5. Comenta resultados no PR (somente em PRs)
  6. Upload dos resultados como artifacts

### Segredos Necessários
- `OPENAI_API_KEY`: Chave da API da OpenAI
- `ANTHROPIC_API_KEY`: Chave da API da Anthropic

Estes segredos devem ser configurados no repositório GitHub em Settings → Secrets and variables → Actions.

## Estratégia de Gate (O que Falha o Build e Por Quê)

### Estratégia Escolhida: Falha Se Qualquer Teste Falhar

**Decisão**: O build falha se qualquer teste (determinístico ou LLM-as-judge) falhar.

**Justificativa**:
- O playbook é tratado como código de produção - qualquer regressão é inaceitável
- Testes determinísticos (asserts) são binários - se falharem, há um bug claro
- LLM-as-judge tem um corte ≥ 6, que é conservador o suficiente para evitar falsos positivos frequentes
- Se o LLM-as-judge flutuar ocasionalmente, isso é um sinal de que o prompt está instável e precisa de refinamento

### Alternativas Consideradas

#### Alternativa 1: Falha Apenas em Asserts Determinísticos, LLM-as-Judge é Apenas Informativo
**Descrição**: O build só falha se asserts determinísticos falharem. O LLM-as-judge roda e comentado no PR, mas não causa falha do build.

**Prós**:
- Elimina não-determinismo do juiz LLM do gate crítico
- Build é mais previsível - não flutua aleatoriamente
- Menos bloqueios por falsos positivos

**Contras**:
- Perda de qualidade no gate - prompts de saída aberta podem regredir sem serem barrados
- O juiz LLM se torna ornamental - se não bloqueia, por que rodar?
- Inconsistência - alguns prompts têm gate estrito, outros não

**Decisão**: Rejeitei esta alternativa porque o juiz LLM é crítico para prompts de saída aberta (causa-raiz, backpressure, migração). Sem o gate, esses prompts podem regredir sem serem detectados.

#### Alternativa 2: Falha em Qualquer Teste, Mas LLM-as-Judge Tem Corte Mais Alto (≥ 7)
**Descrição**: Igual à estratégia escolhida, mas o corte do LLM-as-judge é 7 em vez de 6.

**Prós**:
- Mais conservador - reduz falsos positivos de aprovação
- Maior confiança na qualidade de prompts aprovados

**Contras**:
- Mais falsos negativos - prompts bons podem flutuar entre 6 e 7 e serem rejeitados
- Não-determinismo do juiz LLM se torna mais problemático
- Pode bloquear melhorias legítimas que ainda não atingem 7

**Decisão**: Rejeitei esta alternativa porque o não-determinismo do juiz LLM tornaria o gate instável. Com corte 6, há margem para flutuação. Com corte 7, flutuações entre 6 e 7 causariam bloqueios frustrantes.

#### Alternativa 3: Falha em Qualquer Teste, Mas LLM-as-Judge Tem Duas Execuções e Média
**Descrição**: O juiz LLM roda 2 vezes e usa a média das notas. Se a média ≥ 6, passa.

**Prós**:
- Reduz não-determinismo - médias de múltiplas execuções são mais estáveis
- Mais robusto a flutuações aleatórias

**Contras**:
- Custo dobra - cada execução do juiz chama um modelo LLM adicional
- Latência aumenta - espera por 2 execuções em vez de 1
- Complexidade adicional no workflow

**Decisão**: Rejeitei esta alternativa por custo. Em um pipeline que roda a cada PR, dobrar o custo do juiz LLM pode ser proibitivo. A calibração do juiz (diferença ≤ 1 ponto) já é suficiente para estabilidade.

## Estratégia de Execução: Suíte Inteira vs Prompts Alterados

### Estratégia Escolhida: Rodar Suíte Inteira a Cada Mudança

**Decisão**: O pipeline roda todos os testes (todos os prompts) a cada PR e push, independentemente de quais prompts foram alterados.

**Justificativa**:
- Simplicidade - não precisa detectar quais prompts mudaram
- Garantia de que mudanças em um prompt não quebram outro (ex: mudança em frontmatter não afeta teste)
- Custo é aceitável - com 4 prompts testados, o custo total ainda é baixo (~$0.04 por execução)
- Tempo é aceitável - 4 prompts × 2 providers = 8 chamadas, ~20-30 segundos total

### Alternativas Consideradas

#### Alternativa 1: Rodar Apenas Prompts Alterados (Detecção de Diff)
**Descrição**: Detecta quais arquivos prompt.md mudaram no PR e roda apenas os testes correspondentes.

**Prós**:
- Custo menor - roda apenas o necessário
- Tempo menor - menos chamadas de API
- Mais escalável se o playbook crescer para 50+ prompts

**Contras**:
- Complexidade adicional - precisa implementar detecção de diff no workflow
- Pode perder regressões indiretas - mudança em uma pasta pode afetar outra
- Menos garantia de integridade global

**Decisão**: Rejeitei esta alternativa porque a complexidade adicional não vale a pena para o tamanho atual do playbook (8 prompts). Se o playbook crescer significativamente (20+ prompts), essa alternativa pode se tornar atraente.

#### Alternativa 2: Rodar Suíte Inteira, Mas Apenas em PRs (Não em Push para main)
**Descrição**: Roda todos os testes em PRs, mas não roda em push direto para main.

**Prós**:
- Economiza custo - não roda em merges que já foram validados em PR
- Reduz carga na CI

**Contras**:
- Push direto para main (sem PR) bypassa testes - risco de regressão
- Menos garantia de qualidade no branch principal
- Goles-se o propósito de testes contínuos

**Decisão**: Rejeitei esta alternativa porque compromete a garantia de qualidade. Push direto para main deve ser evitado (branch protection pode exigir PR), mas se acontecer, os testes devem rodar.

## Estratégia de Custo de Chamadas de Modelo

### Estratégia Escolhida: Dois Providers (GPT-4o-mini + Claude 3.5 Sonnet), Chaves em Secrets do Repositório

**Decisão**: Cada teste roda em 2 providers (GPT-4o-mini e Claude 3.5 Sonnet). As chaves de API são armazenadas como secrets do repositório GitHub.

**Justificativa**:
- **Diversidade de providers**: Garante que o prompt funciona independentemente do modelo
- **Custo aceitável**: GPT-4o-mini é barato (~$0.15/1M input), Claude 3.5 Sonnet é moderado (~$3/1M input). Com prompts curtos, custo total por execução é ~$0.04.
- **Segurança**: Secrets do GitHub são criptografados e expostos apenas ao workflow
- **Padrão**: Esta é a prática padrão para CI/CD com APIs externas

### Alternativas Consideradas

#### Alternativa 1: Apenas Um Provider (GPT-4o-mini)
**Descrição**: Roda testes apenas em GPT-4o-mini, o modelo mais barato.

**Prós**:
- Custo 50% menor - apenas um provider em vez de dois
- Latência menor - metade das chamadas
- Menos complexidade - menos uma chave de API

**Contras**:
- Menos garantia de robustez - prompt pode funcionar em GPT-4o-mini mas falhar em Claude
- Se o time usar Claude em produção, os testes não refletem o uso real
- Viés para um provedor específico

**Decisão**: Rejeitei esta alternativa porque a diversidade de providers é importante para garantir que o prompt é agnóstico ao modelo. O custo adicional de 50% (~$0.02 por execução) vale a garantia de robustez.

#### Alternativa 2: Self-Hosted Local LLM (Ollama)
**Descrição**: Roda um modelo local (ex: Llama 3) em um self-hosted runner do GitHub Actions, eliminando custo de API externa.

**Prós**:
- Custo zero de API - não paga por tokens
- Privacidade - dados não saem do ambiente
- Controle total - pode escolher qualquer modelo

**Contras**:
- Custo de infra - runner self-hosted precisa ser mantido
- Qualidade do modelo - modelos locais (Llama 3) podem ser inferiores a GPT-4o/Claude
- Latência - depende do hardware do runner
- Complexidade - precisa configurar e manter o runner

**Decisão**: Rejeitei esta alternativa por complexidade e qualidade. Configurar e manter um self-hosted runner é mais esforço que usar APIs gerenciadas. Modelos locais podem não ter a mesma qualidade que GPT-4o/Claude, comprometendo a validade dos testes.

#### Alternativa 3: Chaves em Variáveis de Ambiente do Time (Organização)
**Descrição**: Chaves de API são configuradas como secrets a nível de organização, compartilhadas entre múltiplos repositórios.

**Prós**:
- Reuso - mesma chave pode ser usada em múltiplos repositórios
- Centralização - gerenciamento em um lugar
- Menos configuração por repositório

**Contras**:
- Maior risco - se a chave vazia, afeta múltiplos repositórios
- Menos granularidade - não pode ter chaves diferentes por repositório
- Dependência de permissões de organização

**Decisão**: Rejeitei esta alternativa por segurança. Secrets a nível de repositório são mais seguros - cada repositório tem suas próprias chaves, limitando o blast radius de uma vazamento.

## Evidência de Execução

### Cenário de Sucesso
**Ação**: Um PR é aberto com uma melhoria no prompt de triagem-de-pods (ajuste no texto para melhor clareza).

**Resultado esperado**:
```
## Prompt Test Results

### nota-de-triagem: PASS (3/3)

### triagem-de-pods: PASS (3/3)

### networkpolicy-sentinel: PASS (1/1)

### causa-raiz-cerebro: PASS (1/1)

---
*Generated by promptfoo*
```

Workflow completa com status (green check). PR pode ser mergeado.

### Cenário de Falha Provocada
**Ação**: Um PR é aberto com uma mudança que quebra o prompt de nota-de-triagem (remoção da instrução de concisidade, fazendo o modelo gerar notas com mais de 8 linhas).

**Resultado esperado**:
```
## Prompt Test Results

### nota-de-triagem: FAIL (2/3)

**Failed tests:**
- Test: Alerta 1 (autoscaler hit max replicas)
  Error: Assert failed: javascript output.split('\n').length <= 8

### triagem-de-pods: PASS (3/3)

### networkpolicy-sentinel: PASS (1/1)

### causa-raiz-cerebro: PASS (1/1)

---
*Generated by promptfoo*
```

Workflow falha com status (red X). PR não pode ser mergeado até o teste ser corrigido.

## Resumo das Decisões de Design

| Decisão | Estratégia Escolhida | Alternativa Rejeitada | Justificativa |
|---------|---------------------|----------------------|---------------|
| Gate de falha | Falha se qualquer teste falhar (incluindo LLM-as-judge) | Falha apenas em asserts determinísticos | LLM-as-judge é crítico para prompts de saída aberta |
| Corte do juiz | ≥ 6 pontos | ≥ 7 pontos | Corte 6 tem margem para não-determinismo |
| Execução | Suíte inteira a cada mudança | Apenas prompts alterados | Simplicidade e garantia de integridade global |
| Trigger | PR + push para main | Apenas PR | Push direto deve ser validado |
| Providers | 2 providers (GPT-4o-mini + Claude) | 1 provider | Diversidade de modelos garante robustez |
| Chaves de API | Secrets do repositório | Secrets de organização | Segurança - menor blast radius |

## Conclusão

O pipeline está configurado para rodar automaticamente a cada PR e push, testando todos os prompts com asserts determinísticos e LLM-as-judge. O build falha se qualquer teste falhar, garantindo que nenhuma regressão entre no repositório. A estratégia de gate é conservadora o suficiente para evitar falsos positivos frequentes, mas flexível o suficiente para permitir melhorias legítimas. O custo é aceitável (~$0.04 por execução) e as chaves de API são armazenadas de forma segura no GitHub Secrets.

O playbook de IA operacional da Aegis agora é um ativo versionado, testado e tratado como código de produção, pronto para uso pelo time de engenharia.
