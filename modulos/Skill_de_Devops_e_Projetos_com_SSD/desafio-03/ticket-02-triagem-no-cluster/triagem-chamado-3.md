# Triagem do Chamado 3 - nyx-stg

## Sintoma Relatado
"nyx-stg, o kube-news responde 503 para quem chama de fora. A aplicação está de pé e saudável, e mesmo assim ninguém chega nela."

## Ambiente Aplicado
Arquivo: `chamado-3-nyx-stg.yaml` (Deployment de PostgreSQL + API, Services)

## Processo de Triagem

### Passo 1: Verificar Deployment
```
kubectl get deployment nyx-api -n nyx-stg
```
**Resultado**: Deployment tem 2 réplicas desejadas, 2 réplicas prontas, 0 unavailable. Deployment parece saudável.

### Passo 2: Ver Pods
```
kubectl get pods -n nyx-stg
```
**Resultado**:
- nyx-api-xxx: Running, 0 restarts
- nyx-api-yyy: Running, 0 restarts
- nyx-postgres: Running

Todos os pods estão Running com 0 restarts. Parecem saudáveis.

### Passo 3: Ver Service
```
kubectl get service nyx-api -n nyx-stg
```
**Resultado**: Service existe, tipo ClusterIP, porta 80 → targetPort 8080.

### Passo 4: Ver Endpoints do Service
```
kubectl get endpoints nyx-api -n nyx-stg
```
**Resultado**: O objeto Endpoints não traz o campo de endereços (ele não vem quando vazio).

**Diagnóstico**: O Service não tem Endpoints, o que significa que nenhum Pod está casando com o seletor do Service.

### Passo 5: Ver Seletor do Service
```
kubectl get service nyx-api -n nyx-stg -o yaml | grep -A 5 selector
```
**Resultado**:
```yaml
selector:
  app: nyx-api
```

### Passo 6: Ver Rótulos dos Pods
```
kubectl get pods -n nyx-stg -o yaml | grep -A 5 labels
```
**Resultado**:
```yaml
labels:
  app: nyxapi
```

### Passo 7: Comparar Seletor vs Rótulos
- Seletor do Service: `app: nyx-api`
- Rótulos dos Pods: `app: nyxapi`

**Mismatch**: Há um hífen de diferença. O Service procura pods com `app: nyx-api`, mas os pods têm `app: nyxapi`.

### Passo 8: Verificar Manifesto do Deployment
```
kubectl get deployment nyx-api -n nyx-stg -o yaml | grep -A 3 template.metadata.labels
```
**Resultado**: O template do Deployment define labels como `app: nyxapi`, que casam com os pods.

**Problema**: O seletor do Service foi definido como `app: nyx-api`, mas o Deployment define labels como `app: nyxapi`. Eles não casam.

## Causa Identificada
**Causa raiz**: Mismatch entre seletor do Service e rótulos do Pod. O Service `nyx-api` tem seletor `app: nyx-api`, mas o Deployment define labels `app: nyxapi` (sem hífen). Como resultado, o Service não encontra nenhum Pod que case com o seletor, os Endpoints ficam vazios, e o tráfego não é encaminhado para os Pods. A aplicação está saudável, mas inalcançável.

**Correlação**: Service criado com seletor errado (app: nyx-api) → Deployment define labels diferentes (app: nyxapi) → Service não encontra Pods → Endpoints vazios → tráfego não é encaminhado → 503 para quem chama de fora.

## Próximo Passo (Sem Aplicar Correção)
Corrigir o seletor do Service para `app: nyxapi` para casar com os rótulos dos Pods definidos no Deployment. Aplicar kubectl apply com o Service corrigido.

## Status da Triagem
**CAUSA IDENTIFICADA** - Mismatch de seletor do Service vs rótulos do Pod (nyx-api vs nyxapi)
