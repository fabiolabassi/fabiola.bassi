# Tarefas - Ticket 03: Inventário e Drift de VM por SSH

## Tarefa 1: Estrutura do Projeto
- [x] Criar diretório do ticket
- [x] Criar PRD.md
- [x] Criar TRD.md
- [x] Criar ADR-001 (linguagem e SSH)
- [x] Criar baseline.yaml
- [x] Criar requirements.txt

## Tarefa 2: Implementação Principal
- [x] Criar auditor-vm.py com estrutura básica
- [x] Implementar carregar_baseline()
- [x] Implementar conectar_ssh()
- [x] Implementar executar_comando()
- [x] Implementar coletar_identificacao()
- [x] Implementar coletar_so()
- [x] Implementar coletar_kernel()
- [x] Implementar coletar_servicos()
- [x] Implementar coletar_swap()
- [x] Implementar coletar_portas()
- [x] Implementar coletar_chaves_ssh()
- [x] Implementar coletar_ssh_root()
- [x] Implementar coletar_ntp()
- [x] Implementar validar_conformidade()
- [x] Implementar gerar_json()
- [x] Implementar gerar_markdown()
- [x] Implementar main()

## Tarefa 3: Testes e Validação
- [ ] Testar contra host real Linux (simulado)
- [ ] Validar saída JSON
- [ ] Validar saída Markdown
- [ ] Testar host inalcançável
- [ ] Testar idempotência

## Tarefa 4: Documentação
- [x] Criar openspec/proposta.md
- [x] Criar openspec/tarefas.md
- [x] Criar openspec/specs.md
- [ ] Criar evidencia-execucao.md
- [ ] Criar origem-e-curadoria.md

## Tarefa 5: Arquivamento
- [ ] Mover documentos não utilizados para arquivo/
- [ ] Atualizar README.md do ticket
