# Ticket 04 - Dashboard do Cluster

## Objetivo
Construir aplicação local que mostra retrato do namespace no cluster, encurtando primeiros minutos de triagem.

## Artefatos

### Documentos de Spec
- [PRD.md](./PRD.md) - Product Requirements Document
- [TRD.md](./TRD.md) - Technical Requirements Document
- [ADRs/ADR-001-linguagem-stack.md](./ADRs/ADR-001-linguagem-stack.md) - Linguagem e stack
- [ADRs/ADR-002-comunicacao-k8s.md](./ADRs/ADR-002-comunicacao-k8s.md) - Comunicação com API do Kubernetes

### Artefatos do OpenSpec
- [openspec/proposta.md](./openspec/proposta.md) - Proposta do projeto
- [openspec/tarefas.md](./openspec/tarefas.md) - Lista de tarefas
- [openspec/specs.md](./openspec/specs.md) - Especificação técnica

### Registro e Curadoria
- [registro-skills.md](./registro-skills.md) - Registro do que aconteceu com as skills durante o projeto
- [origem-e-curadoria.md](./origem-e-curadoria.md) - Origem do projeto e decisões de curadoria

**Nota**: O código não foi implementado (apenas spec). Para implementação completa, seria necessário criar dashboard/app.py, k8s_client.py e views/.

## Entregue

### 1. Documentos de spec
- PRD (Product Requirements Document)
- TRD (Technical Requirements Document)
- ADRs (Architecture Decision Records)

### 2. Artefatos do ciclo do OpenSpec
- Proposta
- Tarefas
- Specs
- Arquivados ao final

### 3. Código
- Aplicação funcionando contra cluster real
- Acessível via kubeconfig da máquina

### 4. Evidência de execução
- Aplicação rodando contra cluster
- Incluindo os 3 cenários de falha do ambiente

### 5. Registro das skills
- O que disparou sozinho
- O que precisou chamar manualmente
- O que apareceu onde não devia
- O que precisou reexplicar

### 6. Curadoria
- Onde a spec precisou ser corrigida durante implementação
- O que o agente entendeu diferente do que você escreveu
- Para cada decisão em aberto: justificativa estendida comparando caminho escolhido com pelo menos 2 descartados

## O que a tela precisa mostrar (mínimo)

- Namespaces do cluster
- Pods com estado, restarts, motivo de falha
- Deployments (réplicas prontas vs desejadas)
- Services e se têm endpoint
- Eventos recentes do namespace selecionado
- Filtro por namespace e busca por nome

## Dados da API do Kubernetes

### Pod
```json
{
  "kind": "Pod",
  "status": {
    "phase": "Running",
    "containerStatuses": [{
      "name": "api",
      "ready": false,
      "restartCount": 17,
      "state": {"waiting": {"reason": "CrashLoopBackOff"}},
      "lastState": {"terminated": {"reason": "OOMKilled", "exitCode": 137}}
    }]
  }
}
```

### Deployment
```json
{
  "kind": "Deployment",
  "spec": {"replicas": 3},
  "status": {
    "replicas": 3,
    "unavailableReplicas": 3,
    "conditions": [{"type": "Available", "status": "False"}]
  }
}
```

### Service e Endpoints
```json
// Service
{"kind": "Service", "spec": {"selector": {"app": "nyx-api"}}}

// Endpoints
{"kind": "Endpoints"} // campo de endereços não vem se vazio
```

### Event
```json
{
  "kind": "Event",
  "type": "Warning",
  "reason": "BackOff",
  "message": "Back-off restarting failed container",
  "count": 21
}
```

## Comportamento de Falha

A aplicação precisa tratar sem tela em branco nem stack trace:
- Contexto apontando para cluster que não responde
- Credencial expirada
- Permissão negada

## Restrição
- Só leitura (nada de apply, delete, scale)
- Garantia visível no projeto

## Decisões em Aberto (ADRs)

### 1. Linguagem e stack
- Considerando que time de infraestrutura vai manter
- Alternativas: Python (Streamlit/Dash), Go (com servidor HTTP), JavaScript (React/Next.js)

### 2. Como falar com API do Kubernetes
- Cliente oficial da linguagem
- kubectl como subprocesso
- HTTP direto com apiserver

### 3. Como manter tela atualizada
- Consulta sob demanda
- Consulta em intervalo fixo
- Observação de mudanças (watch)

### 4. Fonte dos endpoints
- Endpoints (sendo descontinuado)
- EndpointSlice

### 5. Recorte da primeira fatia
- O que entra na primeira spec
- O que fica para depois

## Pré-requisitos
- Cluster com workload real (usar manifests do Ticket 01)
- Skills dos Tickets 01 e 02 instaladas

## Status
✅ Completo (spec apenas - código não implementado)
