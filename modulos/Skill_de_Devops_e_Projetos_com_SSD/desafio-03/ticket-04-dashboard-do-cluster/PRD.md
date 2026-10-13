# PRD - Product Requirements Document
## Ticket 04 - Dashboard do Cluster

## 1. Visão Geral

### 1.1 Problema
Toda triagem começa com a mesma sequência de seis a dez comandos no terminal para montar o retrato de um namespace. Isso é repetitivo e consome tempo valioso nos primeiros minutos de cada chamado.

### 1.2 Solução Proposta
Aplicação local que mostra o retrato do namespace na tela, usando o kubeconfig da máquina de quem opera. Não substitui o terminal, mas encurta os primeiros minutos de cada chamado.

### 1.3 Objetivos
- Mostrar Namespaces, Pods, Deployments, Services e Events do cluster
- Filtro por namespace e busca por nome
- Tratar falhas de ambiente (cluster não responde, credencial expirada, permissão negada)
- Ser apenas leitura (não aplica correções)

## 2. Stakeholders

### 2.1 Primários
- **Trinity (SRE)**: Precisa de visibilidade rápida do cluster durante triagem
- **Morpheus (Engenharia)**: Precisa monitorar workloads em produção

### 2.2 Secundários
- **Nick Fury (Operações)**: Precisa visibilidade do estado do cluster

## 3. Requisitos Funcionais

### 3.1 Entrada
A aplicação lê o contexto corrente do kubeconfig da máquina:
- Cluster do contexto corrente
- Namespace do contexto corrente (ou todos se não especificado)

### 3.2 O que Mostrar (Mínimo)

#### 3.2.1 Namespaces
- Lista de todos os namespaces do cluster
- Filtro por nome

#### 3.2.2 Pods
- Nome do pod
- Estado (Running, Pending, Failed, etc.)
- Contagem de reinícios
- Motivo quando em falha (ex: CrashLoopBackOff, OOMKilled)
- Filtro por namespace e busca por nome

#### 3.2.3 Deployments
- Nome do deployment
- Réplicas prontas vs desejadas
- Status (Available, Progressing, etc.)
- Filtro por namespace e busca por nome

#### 3.2.4 Services
- Nome do service
- Tipo (ClusterIP, NodePort)
- Se tem endpoint (sim/não)
- Portas (port e targetPort)
- Filtro por namespace e busca por nome

#### 3.2.5 Events
- Tipo (Normal, Warning)
- Reason
- Message
- Timestamp
- Objeto envolvido
- Filtro por namespace selecionado

### 3.3 Navegação
- Seleção de namespace para filtrar pods, deployments, services, events
- Busca por nome em cada seção
- Refresh manual

### 3.4 Comportamento de Falha

#### 3.4.1 Contexto apontando para cluster que não responde
- Mostrar mensagem de erro amigável
- Não travar a aplicação
- Opção de tentar reconectar

#### 3.4.2 Credencial expirada
- Mostrar mensagem de erro indicando credencial expirada
- Instruções para renovar credencial

#### 3.4.3 Permissão negada
- Mostrar que um tipo de recurso não pode ser acessado
- Outros recursos continuam acessíveis
- Indicar qual permissão está faltando

## 4. Requisitos Não-Funcionais

### 4.1 Performance
- Carregar namespaces em < 5 segundos
- Carregar pods de um namespace em < 3 segundos
- Atualização manual (refresh) em < 3 segundos

### 4.2 Usabilidade
- Interface intuitiva para plantonistas
- Filtros funcionais
- Mensagens de erro claras

### 4.3 Manutenibilidade
- Código bem documentado
- Fácil de adicionar novos recursos
- Fácil de adaptar para novos clusters

## 5. Exclusões (Out of Scope)

- Multicluster (ler apenas contexto corrente do kubeconfig)
- Troca de contexto por dentro da aplicação (troca por fora)
- Operações de escrita (apply, delete, scale)
- Graficos ou métricas (apenas estado dos objetos)
- Logs de pods (apenas estado e eventos)
- Detalhes avançados de objetos (apenas o essencial)

## 6. Critérios de Aceite

### 6.1 Critérios de Pronto
1. Lista namespaces do cluster
2. Mostra pods com estado, restarts e motivo de falha
3. Mostra deployments com réplicas prontas vs desejadas
4. Mostra services e se têm endpoint
5. Mostra events recentes do namespace selecionado
6. Filtro por namespace funciona
7. Busca por nome funciona
8. Trata cluster que não responde sem travar
9. Trata credencial expirada com mensagem clara
10. Trata permissão negada sem quebrar os outros recursos

## 7. Histórico de Revisões

| Versão | Data | Autor | Mudanças |
|--------|------|-------|---------|
| 1.0 | 2026-08-12 | [Nome] | Versão inicial |
