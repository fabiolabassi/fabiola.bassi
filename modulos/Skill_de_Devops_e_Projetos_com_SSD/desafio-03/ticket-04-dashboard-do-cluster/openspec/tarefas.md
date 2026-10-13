# Tarefas - Ticket 04: Dashboard do Cluster

## Tarefa 1: Estrutura do Projeto
- [x] Criar diretório do ticket
- [x] Criar PRD.md
- [x] Criar TRD.md
- [x] Criar ADR-001 (linguagem e stack)
- [x] Criar ADR-002 (comunicação com K8s)
- [x] Criar openspec/proposta.md
- [x] Criar openspec/tarefas.md
- [x] Criar openspec/specs.md

## Tarefa 2: Implementação (MVP)
- [ ] Criar estrutura de diretórios (dashboard/, views/)
- [ ] Criar requirements.txt
- [ ] Implementar k8s_client.py (wrapper para cliente Kubernetes)
- [ ] Implementar app.py (aplicação Streamlit principal)
- [ ] Implementar views/namespaces.py
- [ ] Implementar views/pods.py
- [ ] Implementar views/deployments.py
- [ ] Implementar views/services.py
- [ ] Implementar views/events.py
- [ ] Implementar tratamento de erros (cluster não responde, credencial expirada, permissão negada)

## Tarefa 3: Testes e Validação
- [ ] Testar contra cluster real
- [ ] Validar filtro por namespace
- [ ] Validar busca por nome
- [ ] Testar cenário cluster não responde
- [ ] Testar cenário credencial expirada
- [ ] Testar cenário permissão negada

## Tarefa 4: Documentação
- [ ] Criar evidencia-execucao.md
- [ ] Criar registro-skills.md
- [ ] Criar origem-e-curadoria.md

## Tarefa 5: Arquivamento
- [ ] Mover documentos não utilizados para arquivo/
- [ ] Atualizar README.md do ticket
