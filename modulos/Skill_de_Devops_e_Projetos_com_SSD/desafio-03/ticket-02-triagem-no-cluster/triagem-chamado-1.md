# Triagem do Chamado 1 - nyx-prod

## Sintoma Relatado
"nyx-prod, a API do kube-news reinicia sozinha. O problema apareceu depois de um corte de custos que mudou os limites de recurso do namespace inteiro de uma vez."

## Ambiente Aplicado
Arquivo: `chamado-1-nyx-prod.yaml` (Deployment de PostgreSQL + API, Services)

## Processo de Triagem

### Passo 1: Verificar Deployment
```
kubectl get deployment nyx-api -n nyx-prod
```
**Resultado**: Deployment tem 2 réplicas desejadas, mas nenhuma pronta (unavailableReplicas: 2)

### Passo 2: Ver Pods
```
kubectl get pods -n nyx-prod
```
**Resultado**:
- nyx-api-xxx: CrashLoopBackOff, 17 restarts
- nyx-postgres: Running

### Passo 3: Ver Pod Problemático (nyx-api)
```
kubectl describe pod nyx-api-xxx -n nyx-prod
```
**Resultado - Estado**:
- State: Waiting
- Reason: CrashLoopBackOff
- Last State: Terminated
- Reason: OOMKilled
- Exit Code: 137

**Resultado - Events**:
- Warning BackOff: "Back-off restarting failed container api"

### Passo 4: Ver Logs do Pod
```
kubectl logs nyx-api-xxx -n nyx-prod --previous
```
**Resultado**: Logs mostram aplicação inicializando, mas logo em seguida há "out of memory" antes do shutdown.

### Passo 5: Ver Resources do Container
```
kubectl describe pod nyx-api-xxx -n nyx-prod | grep -A 5 "Limits:"
```
**Resultado**:
- Limits: memory: 24Mi
- Requests: memory: 16Mi

## Causa Identificada
**Causa raiz**: O container da API tem limite de memória de apenas 24Mi, que é insuficiente para a aplicação. O corte de custos reduziu os limits do namespace inteiro, e 24Mi não é suficiente para a aplicação rodar. O container é terminado com OOMKilled (exit code 137) e entra em CrashLoopBackOff.

**Correlação**: O problema apareceu após corte de custos que mudou limits do namespace → limits de memória foram reduzidos drasticamente (para 24Mi) → aplicação não cabe em 24Mi → OOMKilled → CrashLoopBackOff.

## Próximo Passo (Sem Aplicar Correção)
Aumentar o memory limit do container da API para um valor adequado (ex: 256Mi ou 512Mi) no Deployment. Verificar no projeto kube-news qual é o consumo de memória típico em regime e definir limit entre 1.5x e 2x desse valor.

## Status da Triagem
✅ **CAUSA IDENTIFICADA** - OOMKilled por limite de memória insuficiente após corte de custos
