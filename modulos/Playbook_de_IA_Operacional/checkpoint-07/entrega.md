# Checkpoint 07 - Entrega

## Repositório Baseado no Template
Repositório criado a partir do template `prompt-registry`: https://github.com/fabricioveronez/prompt-registry

**Local**: `modulos/Playbook_de_IA_Operacional/playbook-ia-operacional/`

O repositório foi clonado, o .git foi removido (para ser um novo repositório independente), e a estrutura foi mantida conforme o template.

## Prompts Migrados (Checkpoints 01-06)

Todos os 6 prompts dos Checkpoints 01-06 foram migrados para o formato do template:

1. **triagem-de-pods** (CP01) - `devops/triagem-de-pods/`
2. **nota-de-triagem** (CP02) - `devops/nota-de-triagem/`
3. **causa-raiz-cerebro** (CP03) - `devops/causa-raiz-cerebro/`
4. **backpressure-relay** (CP04) - `devops/backpressure-relay/`
5. **migracao-forge-diagnostico** (CP05 - prompt 1) - `devops/migracao-forge-diagnostico/`
6. **migracao-forge-planejamento** (CP05 - prompt 2) - `devops/migracao-forge-planejamento/`
7. **migracao-forge-execucao** (CP05 - prompt 3) - `devops/migracao-forge-execucao/`
8. **networkpolicy-sentinel** (CP06) - `devops/networkpolicy-sentinel/`

Nota: O Checkpoint 05 (migração do Forge) tinha uma cadeia de 3 prompts, então foram criadas 3 pastas separadas (uma para cada prompt da cadeia).

## Estrutura de Cada Prompt

Cada prompt segue a estrutura do template:

```
devops/<nome-do-prompt>/
  prompt.md          # Frontmatter + texto do prompt com {{placeholders}}
  README.md          # Mesmo frontmatter + documentação humana
```

### Exemplo Completo: triagem-de-pods

**prompt.md**:
```yaml
---
nome: Triagem de Pods Kubernetes
descricao: Analisa snapshot de cluster Kubernetes e identifica pods problemáticos com causa provável e ação recomendada
versao: 1.0.0
tags: [kubernetes, sre, triagem, debug]
inputs:
  - nome: snapshot_cluster
    descricao: Snapshot completo do cluster contendo kubectl get pods, describe e logs
---

Você é um engenheiro SRE com expertise em diagnósticos de clusters Kubernetes...
[resto do prompt com {{snapshot_cluster}}]
```

**README.md**:
```yaml
---
nome: Triagem de Pods Kubernetes
descricao: Analisa snapshot de cluster Kubernetes e identifica pods problemáticos com causa provável e ação recomendada
versao: 1.0.0
tags: [kubernetes, sre, triagem, debug]
inputs:
  - nome: snapshot_cluster
    descricao: Snapshot completo do cluster contendo kubectl get pods, describe e logs
---

# Triagem de Pods Kubernetes

## Objetivo
Prompt para triagem rápida e confiável da saúde de pods em um cluster Kubernetes...

## Quando Usar
- Durante incidentes ou plantões para diagnosticar problemas em clusters Kubernetes
...

## Exemplo de Uso
[entrada e saída esperada]

## Limitações
[limitações conhecidas]

## Técnica Utilizada
- Few-Shot Learning
- Chain of Thought
- Role Prompting
```

## Como Mapeei o Playbook nas Convenções do Template

### 1. Categorias
- Todos os prompts do playbook caem naturalmente na categoria **devops/**, pois são voltados a operação de sistemas (Kubernetes, SRE, data pipelines, segurança)
- Não criei nova categoria - usei a existente `devops/` do template
- O escopo de `devops/` no template já cobre: "Pipelines de CI/CD, containers, orquestração, infraestrutura como código, observabilidade, SRE e segurança operacional"

### 2. Nomenclatura de Pastas
- Segui a regra: nomear pelo **resultado**, não pela técnica
- Exemplos:
  - `triagem-de-pods` (resultado) ✓ vs `chain-of-thought-pods` (técnica) ✗
  - `nota-de-triagem` (resultado) ✓ vs `few-shot-triagem` (técnica) ✗
  - `backpressure-relay` (resultado) ✓ vs `comparacao-approaches` (técnica) ✗
- Usei kebab-case conforme o template

### 3. Frontmatter
- Campo `nome`: título humano em pt-BR, capitalizado (ex: "Triagem de Pods Kubernetes")
- Campo `descricao`: uma linha descrevendo o objetivo
- Campo `versao`: todos iniciaram em `1.0.0` (semver)
- Campo `tags`: 2-5 termos em pt-BR, formato inline
- Campo `inputs`: lista com um item por `{{placeholder}}` do prompt, com `nome` (sem {{}}) e `descricao`
- Frontmatter é **idêntico** em `prompt.md` e `README.md`

### 4. Separação prompt.md × README.md
- `prompt.md`: contém apenas frontmatter + texto do prompt com placeholders `{{variavel}}`
- `README.md`: contém o mesmo frontmatter + documentação humana (objetivo, quando usar, exemplo, limitações, técnica utilizada)
- O texto do prompt é **autocontido** - não referencia o README nem outros arquivos

### 5. Placeholders
- Usam formato `{{nome_variavel}}` conforme o template
- Aparecem listados no campo `inputs` do frontmatter
- Correspondência 1:1 entre placeholders no corpo do prompt e itens em `inputs`

### 6. Documentação
- Atualizei o `README.md` da categoria `devops/` com a lista de todos os 8 prompts
- Atualizei o `README.md` da raiz com a lista de prompts na categoria DevOps
- Cada `README.md` de prompt tem: objetivo, quando usar, exemplo de uso, limitações, técnica utilizada

### 7. Versionamento
- Todos os prompts iniciaram na versão `1.0.0`
- Futuras mudanças seguirão semver:
  - MAJOR: mudança breaking (ex: mudar formato de saída)
  - MINOR: nova funcionalidade ou input
  - PATCH: correção de bug ou melhoria de texto
- Commits seguirão semantic commit com escopo na categoria: `feat(devops): adiciona prompt de triagem de pods`

## Observações Específicas

### Cadeia de Prompts (Checkpoint 05)
O Checkpoint 05 tinha uma cadeia de 3 prompts encadeados. Para seguir a convenção do template (um prompt por pasta), criei 3 pastas separadas:
- `migracao-forge-diagnostico` (prompt 1)
- `migracao-forge-planejamento` (prompt 2)
- `migracao-forge-execucao` (prompt 3)

Cada README documenta que é parte de uma cadeia e explica a ordem de uso.

### Linguagem
- Todos os prompts e documentação estão em **português (pt-BR)** conforme o template
- Isso está alinhado com o contexto do desafio (empresa Aegis fictícia brasileira)

### Conformidade com CLAUDE.md
O repositório segue todas as regras do `CLAUDE.md` do template:
- ✓ Estrutura obrigatória (categoria/prompt/prompt.md + README.md)
- ✓ Frontmatter padrão com todos os campos obrigatórios
- ✓ Placeholders em formato {{nome_variavel}}
- ✓ Documentação mantida atualizada (READMEs de categoria e raiz)
- ✓ Nomenclatura pelo resultado, não pela técnica
- ✓ Texto do prompt autocontido

## Próximos Passos (Checkpoints 08-10)
- CP08: Adicionar testes promptfoo para prompts de saída estruturada
- CP09: Adicionar LLM-as-judge para prompt de causa-raiz
- CP10: Criar pipeline GitHub Actions para rodar testes a cada mudança
