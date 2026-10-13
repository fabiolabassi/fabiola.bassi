---
nome: Endurecimento de NetworkPolicy
descricao: Corrige manifesto permissivo de NetworkPolicy e transforma em política default-deny com regras explícitas
versao: 1.0.0
tags: [kubernetes, networkpolicy, seguranca, hardening]
inputs:
  - nome: manifesto_permissivo
    descricao: NetworkPolicy permissivo a ser corrigida (com allow-all)
  - nome: regras_seguranca
    descricao: Padrão de segurança da Aegis (default-deny, regras de ingress/egress)
  - nome: mapa_servicos
    descricao: Labels e ports de cada serviço (Sentinel, Relay, API gateway, Forge, Cerebro, DNS)
---

Você é um engenheiro de segurança sênior na Aegis. Sua tarefa é corrigir um manifesto de NetworkPolicy permissivo e transformá-lo em uma política de rede segura seguindo os padrões da empresa.

## Manifesto Permissivo (a ser corrigido)
{{manifesto_permissivo}}

## Regras de Segurança da Aegis
{{regras_seguranca}}

## Mapa de Serviços (labels e ports)
{{mapa_servicos}}

## Seu Raciocínio

Siga este processo para corrigir o manifesto:

### 1. Analisar o manifesto permissivo
- Identifique o que está errado (ex: podSelector: {} aplica a todos, - {} libera tudo)
- Entenda qual namespace está sendo protegido
- Liste os riscos deste manifesto permissivo

### 2. Aplicar o padrão default-deny
- Crie uma política default-deny explícita para o namespace
- Esta política deve ter podSelector: {} e policyTypes mas NENHUMA regra de allow
- Isso bloqueia todo tráfego por padrão

### 3. Adicionar regras de ingress permitidas
- Use o mapa de serviços para identificar quais serviços podem falar com os pods do Sentinel
- Use os labels corretos (ex: app=relay, não invente labels)
- Especifique as portas corretas se aplicável
- Cada regra deve ter um comentário explicando qual fluxo legítimo ela libera

### 4. Adicionar regras de egress permitidas
- Use o mapa de serviços para identificar para onde os pods do Sentinel podem falar
- Use os labels corretos e as portas especificadas
- Inclua DNS (kube-dns) para resolução de nomes
- Cada regra deve ter um comentário explicando qual fluxo legítimo ela libera

### 5. Verificar a correção
- NÃO há regra allow-all (o manifesto não deve conter - {} em ingress ou egress)
- O podSelector está correto (app=sentinel para os pods do Sentinel)
- As regras de ingress correspondem ao esperado (Relay + API gateway)
- As regras de egress correspondem ao esperado (Forge + Cerebro + DNS)
- Toda regra tem comentário
- A política é default-deny (bloqueia tudo por padrão, libera só o necessário)

## Formato de Saída

Produza o manifesto YAML corrigido e endurecido:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: [nome da política]
  namespace: [namespace]
spec:
  podSelector:
    [seletor correto para pods do Sentinel]
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - [regra 1 de ingress]
      ports:
        - [portas se aplicável]
      # [comentário explicando o fluxo legítimo]
    - from:
        - [regra 2 de ingress]
      # [comentário explicando o fluxo legítimo]
  egress:
    - to:
        - [regra 1 de egress]
      ports:
        - [portas]
      # [comentário explicando o fluxo legítimo]
    - to:
        - [regra 2 de egress]
      ports:
        - [portas]
      # [comentário explicando o fluxo legítimo]
```

## Instruções Adicionais
- Use EXATAMENTE as labels fornecidas no mapa de serviços - não invente labels
- Use EXATAMENTE as ports fornecidas no mapa de serviços
- NÃO use - {} em nenhuma regra (isso é allow-all e é proibido)
- Cada regra DEVE ter um comentário começando com #
- O manifesto deve ser um único YAML válido (não múltiplos documentos separados por ---)
- O namespace deve ser o mesmo do manifesto permissivo original
- Se precisar de múltiplas políticas (ex: uma default-deny e uma com regras), combine em uma única política

---

Agora, produza o manifesto NetworkPolicy corrigido e endurecido conforme acima.
