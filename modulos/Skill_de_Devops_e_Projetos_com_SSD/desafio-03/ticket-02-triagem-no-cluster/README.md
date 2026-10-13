# Ticket 02 - Skill de Triagem de Cluster

## Objetivo
Criar uma skill de triagem que usa mcp-server-kubernetes para diagnosticar problemas em cluster, com método único para plantonistas.

## Artefatos

- [skill-triagem.md](./skill-triagem.md) - A skill completa
- [matriz-roteamento.md](./matriz-roteamento.md) - Resultado dos testes de roteamento
- [triagem-chamado-1.md](./triagem-chamado-1.md) - Triagem do chamado 1 (nyx-prod)
- [triagem-chamado-2.md](./triagem-chamado-2.md) - Triagem do chamado 2 (orion-stg)
- [triagem-chamado-3.md](./triagem-chamado-3.md) - Triagem do chamado 3 (nyx-stg)
- [comparacao-com-sem-skill.md](./comparacao-com-sem-skill.md) - Comparação com e sem skill

## Entregue

### 1. A skill completa
- Corpo da skill
- Define por onde começar
- Ordem para descer as camadas
- Quando cruzar fontes vs aprofundar
- Quando parar (causa identificada)
- Garantia de só leitura (não escreve no cluster)

### 2. Origem da skill
- De qual fluxo nasceu
- Como foi produzida
- Com qual ferramenta

### 3. Saída real da triagem dos três chamados
- Chamado 1: nyx-prod (API reinicia - corte de custos)
- Chamado 2: orion-stg (loja parou - pod não substituído)
- Chamado 3: nyx-stg (503 - selector não casa)

### 4. Resultado da matriz de roteamento
- O que disparou em cada frase
- O que errou
- O que mudou por causa disso

### 5. Comparação com e sem skill
- Pelo menos 2 casos
- Qualidade da saída
- Custo em tokens
- Tempo

### 6. Curadoria
- O que o método fixou
- O que ficou a critério do agente
- Como garantiu que não escreve no cluster

## Chamados Reais

### Chamado 1: nyx-prod
API do kube-news reinicia sozinha após corte de custos que mudou limits do namespace.

### Chamado 2: orion-stg
Loja do fake-shop parou após deploy do Loom. Pod nunca foi substituído.

### Chamado 3: nyx-stg
kube-news responde 503. Aplicação saudável, mas não alcançável.

## Status
Completo
