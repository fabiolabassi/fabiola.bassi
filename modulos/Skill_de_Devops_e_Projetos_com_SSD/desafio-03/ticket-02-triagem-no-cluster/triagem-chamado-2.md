# Triagem do Chamado 2 - orion-stg

## Sintoma Relatado
"orion-stg, a loja do fake-shop parou depois de uma publicação do Loom. A tag nova foi anunciada no release e o deploy foi aplicado, mas o pod nunca foi substituído."

## Ambiente Aplicado
Arquivo: `chamado-2-orion-stg.yaml` (Deployment de PostgreSQL + web, Services)

## Processo de Triagem

### Passo 1: Verificar Deployment
```
kubectl get deployment orion-web -n orion-stg
```
**Resultado**: Deployment tem 3 réplicas desejadas, 3 réplicas totais, mas 3 unavailableReplicas.

### Passo 2: Ver Pods
```
kubectl get pods -n orion-stg
```
**Resultado**:
- orion-web-xxx: Running, mas com idade antiga (subiu há horas, não minutos)
- orion-postgres: Running

### Passo 3: Ver Pods mais detalhadamente
```
kubectl get pods -n orion-stg -o wide
```
**Resultado**: Todos os pods orion-web têm a mesma imagem antiga (v1.14.2 mencionada no manifesto, mas não a tag nova do release).

### Passo 4: Ver Eventos do Deployment
```
kubectl describe deployment orion-web -n orion-stg
```
**Resultado**: Não há eventos recentes de rollout. O Deployment não criou ReplicaSet novo.

### Passo 5: Ver Imagem no Manifesto vs Pods
```
kubectl get deployment orion-web -n orion-stg -o yaml | grep image
```
**Resultado do manifesto**: image: fabricioveronez/fake-shop:v1.14.2

**Resultado dos pods**: Todos os pods estão rodando v1.14.2 (mesma versão do manifesto).

### Passo 6: Verificar se há tag nova disponível
```
kubectl get deployment orion-web -n orion-stg -o yaml | grep image:
```
**Resultado**: O manifesto ainda aponta para v1.14.2.

### Passo 7: Comparar com release anunciado
**Informação do sintoma**: O release anunciou uma tag nova, mas o manifesto não foi atualizado.

### Passo 8: Verificar se houve tentativa de atualização
```
kubectl rollout history deployment/orion-web -n orion-stg
```
**Resultado**: Apenas uma revisão (a inicial). Não há rollout recente.

## Causa Identificada
**Causa raiz**: O manifesto do Deployment não foi atualizado com a nova tag de imagem. O release anunciou uma tag nova do Loom, mas o deploy aplicado (kubectl apply) usou o manifesto antigo que ainda aponta para v1.14.2. O Deployment não criou ReplicaSet novo, então os pods nunca foram substituídos. A aplicação continua rodando a versão antiga, que pode ter um problema ou a "nova versão" anunciada pode não ter sido realmente implantada.

**Correlação**: Release anunciou tag nova → deploy foi aplicado mas com manifesto antigo → Deployment não criou ReplicaSet novo → pods nunca substituídos → aplicação continua em versão antiga.

## Próximo Passo (Sem Aplicar Correção)
Atualizar o manifesto do Deployment com a nova tag de imagem e aplicar kubectl apply. Verificar se a tag nova existe no registry do Loom. Se não existir, o problema é no processo de release do Loom, não no deploy.

## Status da Triagem
**CAUSA IDENTIFICADA** - Manifesto não atualizado com nova tag de imagem, pods nunca substituídos
