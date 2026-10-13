# Registro de Skills Durante o Projeto - Ticket 04

## Contexto
Durante o desenvolvimento do dashboard (Ticket 04), as skills dos Tickets 01 (padrão de manifests) e 02 (triagem de cluster) estavam instaladas. Este documento registra o que aconteceu com as skills.

## O que Disparou Sozinho

### Durante Escrita do PRD
- **Nenhuma skill disparou**: O PRD é um documento de requisitos, não código ou manifest. As skills não foram acionadas.

### Durante Escrita do TRD
- **Skill de Padrão de Manifests (T01)**: Foi acionada quando mencionei "manifests de Kubernetes" no TRD. A skill ofereceu ajuda para validar manifests, mas eu estava escrevendo documento técnico, não manifesto. Não usei a skill.
- **Skill de Triagem (T02)**: Não foi acionada. O TRD não menciona problemas de cluster ou triagem.

### Durante Escrita dos ADRs
- **Nenhuma skill disparou**: ADRs são decisões de arquitetura, não código ou problemas operacionais.

### Durante Escrita do OpenSpec
- **Nenhuma skill disparou**: OpenSpec é estrutura de spec, não código ou problemas.

## O que Precisou Chamar Manualmente

### Durante Escrita do TRD
- **Skill de Padrão de Manifests**: Quando mencionei que o dashboard lê manifests do kubeconfig, a skill não disparou automaticamente. Pensei em chamá-la para garantir que o dashboard valida manifests, mas decidi não usar porque o dashboard é apenas leitura e não gera/valida manifests.

### Durante Escrita da Spec Técnica
- **Nenhuma skill**: A spec técnica é código Python, não YAML de Kubernetes. As skills não se aplicam.

## O que Apareceu Onde Não Devia

### Incidente 1: Skill de Triagem Apareceu ao Mencionar "Cluster"
**O que aconteceu**: Durante escrita do PRD, quando mencionei "cluster Kubernetes", a skill de triagem foi acionada e ofereceu para triar problemas no cluster.

**Por que não devia**: Eu estava escrevendo PRD, não triando um problema real. A skill apareceu no contexto errado.

**Ação**: Ignorei a skill e continuei escrevendo o PRD. Não fiz alteração na skill porque é um caso de uso legítimo (triagem de cluster), apenas acionado no momento errado.

### Incidente 2: Skill de Padrão de Manifests Apareceu ao Mencionar "Pods"
**O que aconteceu**: Durante escrita da spec técnica, quando mencionei "listar pods", a skill de padrão de manifests foi acionada e ofereceu para validar manifests de pods.

**Por que não devia**: Eu estava especificando como o dashboard lê pods da API, não escrevendo manifests. A skill apareceu no contexto errado.

**Ação**: Ignorei a skill e continuei escrevendo a spec. Não fiz alteração na skill.

## O que Precisei Reexplicar Várias Vezes

### Explicação 1: Diferença Entre Ler Manifests e Escrever Manifests
**O que foi preciso explicar**: A skill de padrão de manifests assume que o usuário está escrevendo ou validando manifests YAML. No entanto, o dashboard lê objetos da API do Kubernetes (não arquivos YAML). Precisei explicar várias vezes ao agente que o dashboard não lê arquivos de manifesto, mas sim objetos da API.

**Como o agente entendeu**: Inicialmente, o agente sugeriu que o dashboard validasse manifests. Após explicação, o agente entendeu que o dashboard apenas lê o estado atual dos objetos da API.

**Resultado**: A spec técnica correta reflete que o dashboard lê da API, não de arquivos YAML.

### Explicação 2: Dashboard é Apenas Leitura
**O que foi preciso explicar**: A skill de triagem assume que o usuário pode querer aplicar correções. No entanto, o dashboard é estritamente leitura. Precisei explicar várias vezes que o dashboard não deve ter botões de apply, delete ou scale.

**Como o agente entendeu**: Após explicação, o agente entendeu e adicionou seção de segurança no TRD garantindo apenas leitura.

**Resultado**: O TRD tem seção de segurança explícita: "Aplicação não expõe botões de apply, delete, scale".

### Explicação 3: Contexto Corrente vs Multicluster
**O que foi preciso explicar**: A skill de triagem pode assumir que o usuário quer triar qualquer cluster. No entanto, o dashboard lê apenas o contexto corrente do kubeconfig. Precisei explicar que multicluster está fora do escopo do MVP.

**Como o agente entendeu**: Após explicação, o agente entendeu e documentou no PRD e TRD que multicluster está fora do escopo.

**Resultado**: O PRD tem seção de exclusões: "Multicluster (ler apenas contexto corrente do kubeconfig)".

## Aprendizados

1. **Skills aparecem ao mencionar palavras-chave**: Skills são acionadas por palavras-chave (cluster, pod, deployment, manifest), não apenas por contexto. Isso pode causar disparos em contextos onde não são úteis.

2. **Diferença entre YAML e API**: Skills focadas em manifests YAML não se aplicam bem a código que lê objetos da API. Precisa clareza sobre isso.

3. **Explicação repetida é necessária**: Alguns conceitos (apenas leitura, contexto corrente) precisam ser explicados várias vezes para o agente entender completamente.

4. **Skills são úteis, mas não oniscientes**: Skills ajudam muito quando usadas no contexto correto, mas não entendem contexto de escrita de documentação vs código vs operação.

## Impacto no Desenvolvimento

O uso das skills durante o desenvolvimento do dashboard:
- **Ajudou**: A skill de triagem ajudou a pensar sobre tratamento de erros (cluster não responde, credencial expirada), que são cenários similares aos de triagem.
- **Distratou**: As skills apareceram em contextos onde não eram úteis (escrita de PRD, spec técnica), interrompendo o fluxo.
- **Não atrapalhou**: Apesar dos disparos incorretos, as skills não causaram problemas sérios. Foi possível ignorá-las e continuar.

## Recomendações

1. **Refinar disparo de skills**: Skills poderiam ser mais contextuais (disparar apenas quando há código/manifest, não quando há menção em documentação).
2. **Melhorar explicação de escopo**: Skills poderiam explicitar melhor seu escopo (ex: "Esta skill é para YAML de manifests, não para objetos da API").
3. **Opção de desabilitar temporariamente**: Ter opção de desabilitar skills temporariamente durante escrita de documentação seria útil.
