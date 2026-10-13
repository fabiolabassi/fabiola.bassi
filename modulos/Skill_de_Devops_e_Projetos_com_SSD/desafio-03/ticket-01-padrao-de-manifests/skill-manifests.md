# Skill: Padrão de Manifests da Metacortex

## Descrição
Skill que verifica e gera manifests de Kubernetes conforme o padrão da Metacortex, separando regras mecânicas (script) de regras que exigem leitura do projeto (instrução).

## Modos de Uso

### Modo Conferência
Verifica se um manifesto existente viola o padrão da casa.

**Uso**: "Confira este manifesto contra o padrão da Metacortex"

**Entrada**: Caminho do arquivo YAML do manifesto

**Saída**: Lista de violações encontradas, separadas por severidade (proibido, obrigatório, recomendado)

### Modo Escrita
Gera manifests novos já dentro do padrão a partir de um projeto.

**Uso**: "Gera os manifests do projeto [nome] seguindo o padrão da Metacortex"

**Entrada**: Caminho do diretório do projeto (kube-news, fake-shop ou encontros-tech)

**Saída**: Manifests completos (Deployment, Service, ConfigMap, Secret) já no padrão

## Regras Verificadas

### Regras Mecânicas (Script)
Estas regras são verificadas pelo script sem precisar ler o projeto:

1. **Formato de namespace**: Deve ser `{cliente}-{ambiente}` (nyx-prod, orion-stg, helio-dev)
2. **Tag :latest proibida**: Imagem não pode usar :latest
3. **Segredo em texto puro proibido**: env.value não pode ter credencial, deve usar secretKeyRef
4. **Seletor casa com rótulos do pod**: selector.matchLabels deve ser idêntico a template.metadata.labels
5. **requests e limits obrigatórios**: Todo container deve ter resources.requests e resources.limits
6. **readinessProbe e livenessProbe obrigatórias**: Todo container deve ter as duas probes
7. **replicas >= 2 em prod**: Em namespace terminado em -prod, replicas deve ser >= 2
8. **Estratégia de RollingUpdate em prod**: Em prod, deve ter strategy.type: RollingUpdate
9. **securityContext obrigatório**: runAsNonRoot, allowPrivilegeEscalation, readOnlyRootFilesystem, drop ALL
10. **automountServiceAccountToken: false**: Quando não fala com API
11. **Imagem de registry interno**: image deve apontar para registry.metacortex.io
12. **hostNetwork, hostPID, privileged proibidos**: Não pode ter esses campos

### Regras que Exigem Leitura do Projeto (Instrução)
Estas regras precisam do usuário verificar o projeto:

1. **4 rótulos obrigatórios**: app.kubernetes.io/name, instance, part-of, managed-by
2. **Nome de container igual ao componente**: Container deve ter nome do componente (api, worker, scheduler)
3. **Probes apontam para endpoints reais**: readinessProbe e livenessProbe devem apontar para /health e /ready que a aplicação expõe
4. **Anotação de dono**: metacortex.io/owner com time responsável
5. **Anotação de runbook**: metacortex.io/runbook com URL do procedimento de plantão
6. **ServiceAccount dedicada**: Não usar default, criar ServiceAccount específica
7. **PodDisruptionBudget em prod**: Criar PDB com minAvailable: 1
8. **terminationGracePeriodSeconds compatível**: Se aplicação precisa de mais tempo para drenar, declarar

## O que o Trivy Já Cobre

Rodar `trivy config manifests/` cobre:
- Tag :latest
- Segredos em texto puro
- securityContext (parcialmente)
- Imagens de registry público

O que Trivy NÃO cobre (precisa da skill):
- Formato de namespace
- Rótulos obrigatórios
- Seletor casando com rótulos
- requests/limits
- Probes
- replicas >= 2 em prod
- Estratégia de RollingUpdate
- PodDisruptionBudget
- ServiceAccount dedicada
- terminationGracePeriodSeconds

## Arquivos de Apoio

- `check-manifest.sh`: Script que verifica regras mecânicas
- `baseline-trivy.txt`: Lista do que Trivy já cobre (para não reimplementar)

## Como Usar

### Conferir um manifesto
1. O usuário fornece o caminho do manifesto
2. A skill roda Trivy primeiro
3. A skill roda check-manifest.sh para regras mecânicas
4. A skill instrui o usuário a verificar regras que exigem leitura do projeto
5. A skill consolida todas as violações em um relatório

### Gerar manifests de um projeto
1. O usuário fornece o caminho do projeto
2. A skill lê o projeto para entender:
   - Nome do componente (ex: api, web)
   - Portas do container
   - Endpoints de saúde (/health, /ready)
   - Dependências de banco
3. A skill gera Deployment com todos os campos obrigatórios
4. A skill gera Service com seletor correto
5. A skill gera ConfigMap para config não sensível
6. A skill instrui sobre Secret para credenciais (não gera valor em texto puro)
7. A skill aplica as regras mecânicas automaticamente

## Permissões
A skill precisa de:
- Leitura de arquivos do sistema (para ler manifests e projetos)
- Execução de comandos (para rodar Trivy e check-manifest.sh)
- Escrita de arquivos (para gerar manifests no modo escrita)

## Exemplo de Conferência

**Entrada**: Manifesto barrado do nyx-prod

**Processo**:
1. Trivy detecta: tag :latest, segredo em texto puro
2. check-manifest.sh detecta: replicas = 1 (deveria ser >= 2 em prod), faltam requests/limits, faltam probes, faltam rótulos obrigatórios, seletor não casa (app: nyx-api vs app: nyxapi)
3. Instrução: Verificar no projeto kube-news se há endpoints /health e /ready

**Saída**: Relatório consolidado de todas as violações
