# Matriz de Roteamento - Ticket 02

## Objetivo
Testar qual skill dispara para cada frase, com as skills dos Tickets 01 (padrão de manifests) e 02 (triagem de cluster) instaladas.

## Frases Testadas

### 1. "o pod do nyx-prod não sobe"
**Resultado**: Disparou skill de triagem (Ticket 02)
**Correto**: Sim, é sobre um pod com problema

### 2. "por que esse deployment está 0/3"
**Resultado**: Disparou skill de triagem (Ticket 02)
**Correto**: Sim, é sobre deployment com problema

### 3. "o service do nyx-stg não tem endpoint"
**Resultado**: Disparou skill de triagem (Ticket 02)
**Correto**: Sim, é sobre service com problema

### 4. "revisa esse deployment antes de eu subir"
**Resultado**: Disparou skill de padrão de manifests (Ticket 01)
**Correto**: Sim, é sobre validar manifest antes de subir

### 5. "esse manifesto está no padrão da casa?"
**Resultado**: Disparou skill de padrão de manifests (Ticket 01)
**Correto**: Sim, é sobre verificar padrão

### 6. "cria um Deployment novo do zero pra mim"
**Resultado**: Disparou skill de triagem (Ticket 02)
**Errado**: Deveria disparar nenhuma skill - criação de deployment não é triagem nem conferência de padrão

**Ação tomada**: Nenhuma. A frase está fora do escopo das duas skills. As skills são para triagem (ler e diagnosticar) e conferência (validar), não para criação.

### 7. "esse manifesto não sobe no cluster"
**Resultado**: Disparou skill de triagem (Ticket 02)
**Parcialmente correto**: Pode ser um problema de manifest (skill 01) ou um problema de cluster após aplicar (skill 02). O agente escolheu triagem, que é razoável se o manifesto já foi aplicado.

**Ação tomada**: Nenhuma. Ambas as skills poderiam ser úteis aqui, mas triagem é um ponto de partida razoável.

### 8. "o Service do nyx não está entregando tráfego"
**Resultado**: Disparou skill de triagem (Ticket 02)
**Correto**: Sim, é sobre service com problema

### 9. "o que é um DaemonSet?"
**Resultado**: Nenhuma skill disparou
**Correto**: É uma pergunta educacional, fora do escopo das duas skills

**Ação tomada**: Nenhuma. A resposta deve vir de documentação ou explicação direta, não de skill de triagem ou conferência.

### 10. "provisiona uma VM nova no Construct pro cliente orion"
**Resultado**: Nenhuma skill disparou
**Correto**: É sobre o Construct (sistema de provisionamento), fora do escopo das skills de Kubernetes

**Ação tomada**: Nenhuma. Isso exigiria uma skill diferente, não as existentes.

## Resumo da Matriz

|| Frase | Skill Disparada | Correto? | Ação |
||-------|----------------|----------|------|
|| "o pod do nyx-prod não sobe" | Triagem (T02) | Sim | Nenhuma |
|| "por que esse deployment está 0/3" | Triagem (T02) | Sim | Nenhuma |
|| "o service do nyx-stg não tem endpoint" | Triagem (T02) | Sim | Nenhuma |
|| "revisa esse deployment antes de eu subir" | Padrão de manifests (T01) | Sim | Nenhuma |
|| "esse manifesto está no padrão da casa?" | Padrão de manifests (T01) | Sim | Nenhuma |
|| "cria um Deployment novo do zero pra mim" | Triagem (T02) | Não | Nenhuma - fora de escopo |
|| "esse manifesto não sobe no cluster" | Triagem (T02) | Parcial | Aceitável - triagem é ponto de partida razoável |
|| "o Service do nyx não está entregando tráfego" | Triagem (T02) | Sim | Nenhuma |
|| "o que é um DaemonSet?" | Nenhuma | Sim | Nenhuma - fora de escopo |
|| "provisiona uma VM nova no Construct" | Nenhuma | Sim | Nenhuma - fora de escopo |

## Mudanças Feitas

### Mudança 1: Descrição da Skill de Triagem
**O que mudou**: Adicionei no início da skill: "Esta skill é para triagem e diagnóstico de problemas existentes, não para criação de recursos."

**Por quê**: Para evitar que a skill dispare para frases como "cria um Deployment novo", que estão fora do escopo.

### Mudança 2: Descrição da Skill de Padrão de Manifests
**O que mudou**: Adicionei: "Esta skill é para validação e conferência de manifests, não para criação de recursos."

**Por quê**: Para reforçar o escopo e evitar confusão com criação.

### Mudança 3: Nenhuma
Para as frases que estão fora do escopo ("o que é um DaemonSet?", "provisiona uma VM"), nenhuma skill disparou, que é o comportamento correto. Nenhuma mudança foi necessária.

## Aprendizados

1. **Ambiguidade natural**: Algumas frases podem ser interpretadas por mais de uma skill (ex: "esse manifesto não sobe no cluster" pode ser triagem ou conferência). Isso é aceitável - o importante é que a skill escolhida consiga resolver o problema.

2. **Frases fora do escopo**: Frases sobre criação ("cria Deployment novo") ou conceitos educacionais ("o que é DaemonSet") não devem disparar nenhuma skill. Se dispararem, precisa ajustar a descrição da skill.

3. **Nome de recursos**: As skills identificam bem quando um nome de recurso específico é mencionado (pod, deployment, service). Isso funciona bem.

4. **Frases mal formuladas**: O exercício menciona que algumas frases podem estar mal formuladas. "cria um Deployment novo do zero pra mim" é um exemplo - a ação implícita é criação, mas a frase é uma solicitação. Nesse caso, nenhuma skill deveria disparar, mas a skill de triagem foi acionada. Ajustei a descrição da skill para incluir "não para criação".
