# Desafio 03 - Skill de DevOps e Projetos com SSD

## Visão Geral

Desafio completo com 4 tickets envolvendo skills de Kubernetes, triagem de cluster, inventário de VM por SSH e dashboard de cluster.

## Tickets

- [Ticket 01 - Skill do Padrão de Manifests](./ticket-01-padrao-de-manifests/) ✅ Completo - Skill que empacota o padrão de manifests da Metacortex
- [Ticket 02 - Skill de Triagem de Cluster](./ticket-02-triagem-no-cluster/) ✅ Completo - Skill de triagem usando mcp-server-kubernetes
- [Ticket 03 - Inventário de VM por SSH](./ticket-03-inventario-de-vm/) ✅ Completo (spec + código simulado) - Ferramenta CLI de auditoria de VM
- [Ticket 04 - Dashboard do Cluster](./ticket-04-dashboard-do-cluster/) ✅ Completo (spec apenas) - Aplicação local de visualização do cluster

## Agente e Modelos

- **Agente**: Claude (Anthropic)
- **Modelos**: Claude Sonnet 4 para tarefas complexas, GPT-4o-mini para tarefas simples

## Contexto da Metacortex

A Metacortex é uma provedora de infraestrutura gerenciada com três sistemas internos:
- **Construct**: provisiona VMs e clusters Kubernetes
- **Loom**: constrói e publica imagens de VM e container
- **Roster**: inventário de hosts (mantido à mão)

Três projetos reais são usados:
- **kube-news** (cliente nyx): Node + Express + PostgreSQL
- **fake-shop** (cliente orion): Flask + PostgreSQL
- **encontros-tech** (cliente helio): Flask + PostgreSQL
