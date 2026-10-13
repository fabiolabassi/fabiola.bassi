# Proposta - Ticket 04: Dashboard do Cluster

## Resumo
Proposta de aplicação local (dashboard) que mostra o estado do cluster Kubernetes para encurtar os primeiros minutos de triagem.

## Problema
Toda triagem começa com a mesma sequência de comandos no terminal (kubectl get pods, describe, logs, etc.). Isso é repetitivo e consome tempo valioso.

## Solução Proposta
Aplicação local que:
- Lê kubeconfig da máquina
- Mostra Namespaces, Pods, Deployments, Services, Events
- Permite filtro por namespace e busca por nome
- Trata falhas de ambiente (cluster não responde, credencial expirada, permissão negada)
- É apenas leitura

## Escopo Inicial (MVP)
- Contexto corrente do kubeconfig (não multicluster)
- 5 recursos: Namespaces, Pods, Deployments, Services, Events
- Filtro por namespace
- Busca por nome
- Refresh manual
- Tratamento de 3 cenários de falha

## Fora do Escopo (Futuro)
- Multicluster (troca de contexto por fora)
- Operações de escrita (apply, delete, scale)
- Graficos/métricas
- Logs de pods
- ConfigMaps, Secrets, Ingress
- StatefulSets, DaemonSets, Jobs

## Tecnologia
- Python 3.10+ com Streamlit para UI
- kubernetes/python-client para API do Kubernetes
- EndpointSlice para verificação de endpoints

## Aceitação
- Lista namespaces
- Mostra pods com estado, restarts, motivo de falha
- Mostra deployments com réplicas prontas vs desejadas
- Mostra services e se têm endpoint
- Mostra events recentes
- Filtro por namespace funciona
- Busca por nome funciona
- Trata cluster não responde
- Trata credencial expirada
- Trata permissão negada
