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

# Endurecimento de NetworkPolicy

## Objetivo
Prompt para correção e endurecimento de manifestos de NetworkPolicy permissivos no Kubernetes. Transforma políticas allow-all em políticas default-deny com regras explícitas de ingress e egress, seguindo o padrão de segurança da Aegis e usando labels e ports corretos do mapa de serviços.

## Quando Usar
- Ao revisar NetworkPolicies permissivas que foram barradas por segurança
- Para criar políticas de rede seguindo o princípio de least privilege
- Para documentar e padronizar políticas de rede entre namespaces
- Como parte de um processo de hardening de segurança do cluster

## Exemplo de Uso

### Entrada (resumida)
**Manifesto permissivo**: podSelector: {}, ingress: - {}, egress: - {}
**Regras**: pods só aceitam Relay + API gateway, só fazem saída para Forge (5432) + Cerebro (9200) + DNS
**Mapa**: Sentinel (app=sentinel), Relay (app=relay), API gateway (app=api-gateway), Forge (app=forge, 5432), Cerebro (app=cerebro, 9200), DNS (k8s-app=kube-dns, 53)

### Saída Esperada (resumida)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: sentinel-network-policy
  namespace: sentinel-prod
spec:
  podSelector:
    matchLabels:
      app: sentinel
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchNames:
              - relay-prod
          podSelector:
            matchLabels:
              app: relay
      # Permite tráfego de entrada do Relay para consumo de eventos de telemetry
  egress:
    - to:
        - namespaceSelector:
            matchNames:
              - forge-prod
          podSelector:
            matchLabels:
              app: forge
      ports:
        - protocol: TCP
          port: 5432
      # Permite saída para Forge (warehouse Postgres) na porta 5432
```

## Limitações
- Assume familiaridade com Kubernetes NetworkPolicy e conceitos de default-deny
- Requer que o mapa de serviços seja completo e correto (labels e ports)
- O prompt gera uma única política - em casos complexos pode ser necessário múltiplas políticas
- Específico para o padrão de segurança da Aegis - pode não se aplicar a outras organizações
- Não valida o YAML gerado - deve ser aplicado e testado no cluster

## Técnica Utilizada
- Role Prompting: define o modelo como "engenheiro de segurança sênior"
- Precisão Técnica: exige uso exato de labels e ports fornecidos no mapa
- Constraint Specification: proíbe allow-all (- {}), exige comentários em todas as regras
- Default-Deny Pattern: ensina o padrão de bloquear tudo por padrão e liberar só o necessário

## Processo de Verificação
Este prompt foi desenvolvido com um processo de verificação e refino em 3 iterações:
- **v1**: Primeira versão gerada
- **v2**: Correção após crítica (namespaceSelector correto, política default-deny separada)
- **v3**: Versão final aprovada (namespaceSelector com matchNames, política única)

Em produção, recomenda-se seguir processo similar: gerar, criticar como revisor de segurança, refinar.
