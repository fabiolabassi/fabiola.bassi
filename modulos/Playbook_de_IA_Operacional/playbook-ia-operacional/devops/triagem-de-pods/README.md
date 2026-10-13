---
nome: Triagem de Pods Kubernetes
descricao: Analisa snapshot de cluster Kubernetes e identifica pods problemáticos com causa provável e ação recomendada
versao: 1.0.0
tags: [kubernetes, sre, triagem, debug]
inputs:
  - nome: snapshot_cluster
    descricao: Snapshot completo do cluster contendo kubectl get pods, describe e logs
---

# Triagem de Pods Kubernetes

## Objetivo
Prompt para triagem rápida e confiável da saúde de pods em um cluster Kubernetes. Recebe um snapshot contendo `kubectl get pods`, `kubectl describe` e `kubectl logs`, e retorna uma análise estruturada identificando pods problemáticos, suas causas prováveis e ações recomendadas para o plantonista.

## Quando Usar
- Durante incidentes ou plantões para diagnosticar problemas em clusters Kubernetes
- Quando múltiplos pods estão em estado não-Running e é necessário priorizar ações
- Para documentação de incidentes (triagem inicial)
- Para treinamento de novos SREs no padrão de diagnóstico

## Exemplo de Uso

### Entrada
```
$ kubectl get pods -n sentinel-prod
NAME                            READY   STATUS             RESTARTS       AGE
sentinel-api-7d9c8b6f4-2xk9p    1/1     Running            0              6d
sentinel-api-7d9c8b6f4-h4m2t    0/1     CrashLoopBackOff   14 (90s ago)   42m
$ kubectl describe pod sentinel-api-7d9c8b6f4-h4m2t -n sentinel-prod
    State:          Waiting
      Reason:       CrashLoopBackOff
    Last State:     Terminated
      Reason:       OOMKilled
      Exit Code:    137
    Limits:         memory: 512Mi
$ kubectl logs sentinel-api-7d9c8b6f4-h4m2t -n sentinel-prod --previous
2026-05-13 10:15:12 [FATAL] [runtime] out of memory, shutting down process
```

### Saída Esperada
```
### PODS PROBLEMÁTICOS
**Nome do Pod**: sentinel-api-7d9c8b6f4-h4m2t
- **Status**: CrashLoopBackOff (14 restarts em 42m)
- **Causa Provável**: OOMKilled - o pod está sendo terminado por falta de memória. Os logs mostram heap chegando ao limite antes do FATAL "out of memory".
- **Ação Recomendada**: Aumentar o limite de memória do pod de 512Mi para 768Mi ou investigar memory leak.

### RESUMO DA SITUAÇÃO
Um pod do sentinel-api está em CrashLoopBackOff devido a OOMKilled, afetando a disponibilidade do serviço.

### AÇÕES PRIORITÁRIAS
1. Aumentar memory limit do sentinel-api deployment de 512Mi para 768Mi
2. Monitorar heap usage após o ajuste
```

## Limitações
- Requer que o snapshot seja coletado por alguém com acesso ao cluster - o prompt não busca dados externamente
- Assume familiaridade básica com terminologia Kubernetes (STATUS, RESTARTS, eventos)
- Não substitui investigação mais profunda - é uma triagem inicial rápida
- Depende da qualidade e completude do snapshot fornecido (se faltarem logs ou describe, a análise fica limitada)
- Não lida com problemas de nível de nó (node failures, network issues) - foca em problemas de pod específicos

## Técnica Utilizada
- Few-Shot Learning: exemplos de casos comuns (OOMKilled, ImagePullBackOff, Pending, saudável)
- Chain of Thought: raciocínio estruturado em 6 passos (verificar status, examinar eventos, analisar logs, correlacionar, investigar restarts, identificar motivo)
- Role Prompting: define o modelo como "engenheiro SRE com expertise em diagnósticos de clusters Kubernetes"
