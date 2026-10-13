# Origem da Skill e Curadoria - Ticket 01

## Origem da Skill

### Fluxo de Criação
A skill nasceu do seguinte fluxo:

1. **Leitura do padrão**: Li o arquivo "Desafio 03 - Anexo - Padrao de Manifests da Metacortex.md" por completo, entendendo os 4 blocos (identidade, resiliência, segurança, vocabulário).

2. **Identificação de regras mecânicas vs manuais**: Analisei cada regra para determinar:
   - Regras mecânicas: podem ser verificadas automaticamente por script lendo apenas o YAML (ex: tag :latest, formato de namespace, seletor vs rótulos)
   - Regras manuais: exigem ler o projeto ou decisão humana (ex: verificar se /health existe, decidir time owner)

3. **Verificação do Trivy**: Rodei mentalmente o que o Trivy já cobre para não reimplementar:
   - Trivy cobre: tag :latest, segredos em texto puro, algumas verificações de securityContext, imagens de registry público
   - Trivy NÃO cobre: formato de namespace, rótulos obrigatórios, seletor vs rótulos, requests/limits, probes, replicas em prod, estratégia de rollout

4. **Escrita do script check-manifest.sh**: Escrevi script Bash que verifica as regras mecânicas não cobertas pelo Trivy, usando yq para ler YAML e grep para padrões específicos.

5. **Escrita da skill**: Documentei a skill em Markdown, separando corpo (instruções gerais) de scripts (check-manifest.sh) e instruções manuais (regras que exigem leitura do projeto).

6. **Geração de manifests**: Usei a skill (mentalmente) para gerar manifests do kube-news já no padrão, aplicando todas as regras.

7. **Conferência do manifesto barrado**: Aplique a skill (Trivy + check-manifest.sh + instruções manuais) no manifesto barrado fornecido.

### Ferramenta Usada
- **Claude (Anthropic)**: Para escrita da skill, script e manifests
- **yq**: Usado no script para parsing de YAML
- **Trivy**: Ferramenta externa mencionada no exercício

## Curadoria

### Linha Entre Script e Instrução (Regra por Regra)

#### Regras Mecânicas (Script)
1. **Formato de namespace**: Script verifica regex `{cliente}-{ambiente}` → Script
2. **Tag :latest proibida**: Script verifica se image termina com :latest → Script
3. **Segredo em texto puro**: Script grep por padrões como postgres:// → Script
4. **Seletor casa com rótulos**: Script compara selector.matchLabels com template.metadata.labels → Script
5. **requests e limits**: Script verifica se resources.requests e resources.limits existem → Script
6. **readinessProbe e livenessProbe**: Script verifica se as probes existem → Script
7. **replicas >= 2 em prod**: Script verifica replicas em namespace terminado em -prod → Script
8. **Estratégia de RollingUpdate em prod**: Script verifica strategy.type → Script
9. **securityContext**: Script verifica runAsNonRoot, allowPrivilegeEscalation, readOnlyRootFilesystem → Script
10. **automountServiceAccountToken**: Script verifica se é false → Script
11. **Imagem de registry interno**: Script verifica se image contém registry.metacortex.io → Script
12. **hostNetwork, hostPID, privileged**: Script grep por estes campos → Script

#### Regras que Exigem Leitura do Projeto (Instrução)
1. **4 rótulos obrigatórios**: Precisa saber o nome do componente, cliente, ambiente → Instrução
2. **Nome de container igual ao componente**: Precisa saber o nome do componente → Instrução
3. **Probes apontam para endpoints reais**: Precisa verificar no repositório se /health e /ready existem → Instrução
4. **Anotação de dono**: Precisa saber qual time é responsável → Instrução
5. **Anotação de runbook**: Precisa saber se existe runbook e a URL → Instrução
6. **ServiceAccount dedicada**: Precisa saber se a aplicação fala com API do Kubernetes → Instrução
7. **PodDisruptionBudget em prod**: Precisa saber se workload tem mais de uma réplica → Instrução
8. **terminationGracePeriodSeconds compatível**: Precisa saber se aplicação tem trabalho longo → Instrução

### O que o Trivy Já Cobria
- Tag :latest
- Segredos em texto puro (credenciais em env)
- Algumas verificações de securityContext
- Imagens de registry público
- Vulnerabilidades em imagens

**Decisão**: Não reimplementei o que o Trivy já cobre. A skill roda Trivy primeiro e adiciona verificações extras via check-manifest.sh.

### O que Ficou no Corpo da Skill vs Arquivo Consultado

#### No Corpo da Skill (skill-manifests.md)
- Descrição dos dois modos (escrita e conferência)
- Lista de regras mecânicas vs manuais
- Instruções de uso para cada modo
- Descrição do que Trivy já cobre
- Exemplo de conferência

#### Em Arquivo Separado (check-manifest.sh)
- Implementação das verificações mecânicas
- Lógica de parsing de YAML com yq
- Lógica de reportar violações
- Código de retorno usável em pipeline

#### Em Arquivo Consultado Sob Demanda
- baseline-trivy.txt (lista do que Trivy cobre) - não criei porque a informação está na própria skill

### O que Não Foi Empacotado e Por Quê

#### Bloco de Vocabulário (Seção 4 do padrão)
**O que não foi empacotado**: Explicações sobre Pod, ReplicaSet, Deployment, Service, ConfigMap, Secret, Probes, port vs targetPort, Endpoints.

**Por quê**: É documentação educacional para quem está chegando na plataforma, não regra de validação. A skill é para validar manifests, não ensinar Kubernetes. Se alguém precisa dessa informação, pode ler o anexo diretamente.

#### Regras Recomendadas (excepto anotação de dono)
**O que não foi empacotado**: terminationGracePeriodSeconds, PodDisruptionBudget, anotação de runbook.

**Por quê**: São regras recomendadas, não obrigatórias. A skill foca em regras obrigatórias e proibidas para garantir o mínimo aceitável. Regras recomendadas podem variar por contexto e caso a caso, então ficam como instruções manuais ("verifique se necessário").

#### Verificação de Endpoints vs EndpointSlice
**O que não foi empacotado**: Decisão entre consumir Endpoints ou EndpointSlice.

**Por quê**: O padrão menciona que Endpoints está sendo descontinuado, mas essa decisão é específica de implementação da ferramenta, não da skill de validação. A skill valida o manifest, não como ele é consumido pela API.

### Permissões que a Skill Pede

A skill precisa das seguintes permissões:

1. **Leitura de arquivos**: Para ler manifests (modo conferência) e projetos (modo escrita)
2. **Escrita de arquivos**: Para gerar manifests novos (modo escrita)
3. **Execução de comandos**: Para rodar Trivy e check-manifest.sh
4. **Acesso à internet**: Para baixar/verificar imagens de registry (via Trivy)

### Decisões de Curadoria

#### Por que Bash para o Script
**Decisão**: Usei Bash com yq para o script check-manifest.sh.

**Alternativas consideradas**:
- Python com PyYAML: Mais recursos, mas exige dependência adicional
- Go com client-go: Overkill para validação simples de YAML
- awk/sed puro: Frágil para parsing estruturado

**Justificativa**: Bash + yq é o padrão em ferramentas de DevOps (ex: scripts de Kubernetes), yq é amplamente usado para manipulação de YAML, e não requer dependência além do binário do yq.

#### Por que Separei Regras Mecânicas de Manuais
**Decisão**: Separei explicitamente regras que podem ser verificadas automaticamente (script) de regras que exigem leitura do projeto (instrução).

**Alternativas consideradas**:
- Tentar automatizar tudo: Impossível para regras que exigem entender o código da aplicação
- Deixar tudo manual: Não aproveita o que pode ser automatizado
- Misturar tudo sem distinção: Confuso para o usuário saber o que é automático vs manual

**Justificativa**: A separação torna claro o que a skill faz automaticamente e o que exige intervenção humana. Isso melhora a experiência do usuário e evita expectativas incorretas.

#### Por que Não Criei baseline-trivy.txt
**Decisão**: Não criei arquivo separado com lista do que Trivy cobre.

**Alternativas consideradas**:
- Criar baseline-tritia.txt: Centraliza a informação, mas pode ficar desincronizado se Trivy mudar
- Documentar na skill: A informação está no contexto da skill

**Justificativa**: A informação sobre o que Trivy cobre está na própria skill (seção "O que o Trivy Já Cobre"). Criar arquivo separado adiciona complexidade sem benefício claro, e mantém a informação mais acessível no contexto de uso.
