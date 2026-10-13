# Playbook de IA Operacional - Aegis

## Visão Geral

Este projeto é o resultado do desafio "Operação contínua na Aegis", onde foi construído um playbook de IA operacional para a empresa fictícia Aegis de observabilidade. O playbook consiste em uma biblioteca de prompts parametrizáveis, versionados e testados, que o time de engenharia pode usar para tarefas de SRE e operação.

## Estrutura do Repositório

```
playbook-ia-operacional/
├── devops/                           # Categoria DevOps
│   ├── triagem-de-pods/              # CP01: Triagem de pods Kubernetes
│   ├── nota-de-triagem/              # CP02: Notas de triagem padronizadas
│   ├── causa-raiz-cerebro/           # CP03: Análise de causa-raiz de degradação
│   ├── backpressure-relay/           # CP04: Análise de estratégia de backpressure
│   ├── migracao-forge-diagnostico/   # CP05-1: Diagnóstico do estado atual
│   ├── migracao-forge-planejamento/  # CP05-2: Planejamento da migração
│   ├── migracao-forge-execucao/     # CP05-3: Plano executável
│   └── networkpolicy-sentinel/       # CP06: Endurecimento de NetworkPolicy
├── .github/workflows/
│   └── prompt-tests.yml              # CP10: Pipeline de testes
└── README.md
```

## Checkpoints Completos

### Checkpoint 01: Triagem de Pods
- **Prompt**: Analisa snapshot de cluster Kubernetes (get pods, describe, logs) e identifica pods problemáticos com causa provável e ação recomendada
- **Técnica**: Few-shot learning + Chain of thought + Role prompting
- **Teste**: promptfooconfig.yaml com 3 casos (OOMKilled, ImagePullBackOff/Pending, saudável)

### Checkpoint 02: Nota de Triagem
- **Prompt**: Transforma alertas crus em notas de triagem padronizadas com 5 campos (ALERTA, IMPACTO, HIPÓTESE INICIAL, AÇÃO IMEDIATA, ESCALAR PARA)
- **Técnica**: Few-shot learning com exemplos de formato
- **Teste**: promptfooconfig.yaml com 3 alertas crus

### Checkpoint 03: Causa-raiz do Cerebro
- **Prompt**: Analisa config, métricas e logs do Cerebro para identificar causa-raiz de degradação de busca
- **Técnica**: Chain of thought estruturado + Honestidade epistêmica
- **Teste**: promptfooconfig.yaml com LLM-as-judge (rubrica de 4 critérios, corte ≥ 6)

### Checkpoint 04: Backpressure do Relay
- **Prompt**: Compara múltiplas abordagens de backpressure (priority queues, DLQ, tenant isolation, auto-scaling) e recomenda a melhor
- **Técnica**: Análise comparativa estruturada + Trade-off analysis
- **Teste**: Não aplicável (saída aberta, requer julgamento humano)

### Checkpoint 05: Migração do Forge
- **Prompts**: Cadeia de 3 prompts encadeados
  1. Diagnóstico do estado atual
  2. Planejamento da migração
  3. Plano executável e reversível
- **Técnica**: Prompt chaining + Progressive disclosure
- **Teste**: Não aplicável (saída aberta, requer julgamento humano)

### Checkpoint 06: NetworkPolicy do Sentinel
- **Prompt**: Corrige manifesto permissivo de NetworkPolicy e transforma em política default-deny com regras explícitas
- **Técnica**: Iterative refinement (3 iterações de verificação e refino)
- **Teste**: promptfooconfig.yaml com 1 caso (manifesto permissivo)

### Checkpoint 07: Biblioteca vira Código
- **Entrega**: 8 prompts migrados para formato do template prompt-registry
- **Estrutura**: Cada prompt tem prompt.md (frontmatter + texto) e README.md (documentação)
- **Versionamento**: Todos iniciados em 1.0.0, commits semânticos com escopo `feat(devops)`

### Checkpoint 08: Testes Determinísticos
- **Entrega**: promptfooconfig.yaml para 3 prompts de saída estruturada
- **Asserts**: Contains, regex, not-contains, is-json, javascript, latency (≤5s), cost (≤$0.01)
- **Providers**: GPT-4o-mini + Claude 3.5 Sonnet

### Checkpoint 09: Gate de Qualidade com LLM-as-Judge
- **Entrega**: promptfooconfig.yaml para causa-raiz com juiz LLM
- **Rubrica**: 4 critérios (0-2 pontos cada), total 0-8, corte ≥ 6
- **Calibração**: Juiz calibrado contra pontuação humana (diferença ≤ 1 ponto)

### Checkpoint 10: Pipeline em Produção Contínua
- **Entrega**: GitHub Actions workflow (.github/workflows/prompt-tests.yml)
- **Trigger**: pull_request + push para main
- **Gate**: Falha se qualquer teste falhar (incluindo LLM-as-judge)
- **Comentário**: Resultados postados automaticamente no PR

## Como Usar o Playbook

### Para Engenheiros

1. Navegue até a categoria `devops/`
2. Escolha o prompt desejado (ex: `triagem-de-pods`)
3. Leia o `README.md` para entender objetivo, quando usar e limitações
4. Copie o conteúdo do `prompt.md`
5. Substitua os placeholders `{{variavel}}` pelos valores reais
6. Cole no modelo de IA (chat, playground ou API)

### Para Manutenção

1. Para mudar um prompt: edite `prompt.md` e `README.md` (mantenha frontmatter idêntico)
2. Para adicionar um prompt: siga o template (prompt.md + README.md com frontmatter)
3. Para testar: rode `promptfoo eval -c devops/<prompt>/promptfooconfig.yaml`
4. Para versionar: incremente o campo `versao` no frontmatter (semver)
5. Para commit: use semantic commit `feat(devops): descrição da mudança`

## Configuração do Pipeline

### Secrets Necessários

Configure estes secrets no repositório GitHub (Settings → Secrets and variables → Actions):
- `OPENAI_API_KEY`: Chave da API da OpenAI
- `ANTHROPIC_API_KEY`: Chave da API da Anthropic

### Execução Local dos Testes

```bash
# Instalar promptfoo
npm install -g promptfoo

# Rodar testes de um prompt específico
promptfoo eval -c devops/triagem-de-pods/promptfooconfig.yaml

# Rodar todos os testes
promptfoo eval -c devops/*/promptfooconfig.yaml
```

## Decisões de Design

### Gate de Falha
O build falha se qualquer teste falhar (incluindo LLM-as-judge). Isso garante que nenhuma regressão entre no repositório.

### Corte do Juiz LLM
Nota ≥ 6 de 8 máximo, com nenhum critério zerado. Este corte é conservador o suficiente para evitar falsos positivos frequentes, mas flexível para permitir melhorias.

### Providers
Dois providers (GPT-4o-mini + Claude 3.5 Sonnet) para garantir que o prompt funciona independentemente do modelo.

### Execução
Suíte inteira roda a cada PR e push, independentemente de quais prompts foram alterados. Simplicidade e garantia de integridade global.

## Aprendizados

1. **Meta-prompting é poderoso**: Em vez de escrever prompts na mão, direcionar a IA para gerar e refinar prompts produz resultados melhores mais rápido.

2. **Parametrização é essencial**: Todo prompt deve ser parametrizável para ser reusável. Placeholders `{{variavel}}` permitem que qualquer pessoa use o mesmo prompt com dados diferentes.

3. **Testes são obrigatórios**: Prompt sem teste é prompt em que ninguém confia. Testes determinísticos (asserts) + LLM-as-judge (julgamento) cobrem diferentes tipos de saída.

4. **Tratar prompt como código**: Versionamento, commits semânticos, pipeline de CI/CD - prompt deve ser tratado com o mesmo rigor que código de produção.

5. **Iteração é normal**: O primeiro prompt raramente é perfeito. Processos de verificação e refino (como no CP06) são essenciais para qualidade.

## Próximos Passos

O playbook está funcional e pronto para uso. Possíveis expansões futuras:

- Adicionar mais prompts à categoria DevOps (ex: diagnóstico de Redis, análise de logs de aplicação)
- Criar novas categorias (ex: desenvolvimento, produtividade)
- Adicionar mais prompts de saída estruturada com testes determinísticos
- Adicionar LLM-as-judge para prompts de saída aberta (backpressure, migração)
- Expandir a suíte de testes com mais casos de borda

## Licença

Este projeto faz parte do material da pós-graduação em AIOps e Inteligência Artificial com Engenharia Cloud (pos.veronez.io/pos-aiops).
