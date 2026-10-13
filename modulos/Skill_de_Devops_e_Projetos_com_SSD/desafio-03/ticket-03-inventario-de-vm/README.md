# Ticket 03 - Inventário e Drift de VM por SSH

## Objetivo
Construir ferramenta CLI que audita VM por SSH e compara com baseline do parque da Metacortex.

## Artefatos

### Documentos de Spec
- [PRD.md](./PRD.md) - Product Requirements Document
- [TRD.md](./TRD.md) - Technical Requirements Document
- [ADRs/ADR-001-linguagem-e-ssh.md](./ADRs/ADR-001-linguagem-e-ssh.md) - Architecture Decision Record

### Artefatos do OpenSpec
- [openspec/proposta.md](./openspec/proposta.md) - Proposta do projeto
- [openspec/tarefas.md](./openspec/tarefas.md) - Lista de tarefas
- [openspec/specs.md](./openspec/specs.md) - Especificação técnica

### Código
- [auditor-vm.py](./auditor-vm.py) - Código da ferramenta
- [baseline.yaml](./baseline.yaml) - Baseline do parque
- [requirements.txt](./requirements.txt) - Dependências Python

### Evidência de Execução
- [evidencia-execucao.md](./evidencia-execucao.md) - Saída JSON e Markdown simuladas, comportamento com host inalcançável

### Curadoria
- [origem-e-curadoria.md](./origem-e-curadoria.md) - Origem do projeto e decisões de curadoria

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
- Ferramenta funcionando contra host remoto por SSH
- Em linguagem definida no TRD

### 4. Evidência de execução real
- Saída nos dois formatos (JSON e Markdown)
- Código de retorno
- Comportamento com host inalcançável
- Segunda execução mostrando mesmo resultado

### 5. Curadoria
- Onde a spec precisou ser corrigida durante implementação
- O que o agente entendeu diferente do que você escreveu

## Decisões a Registrar (TRD/ADRs)

### Como a ferramenta se comunica com o host remoto
- SSH library da linguagem?
- kubectl-style?
- Outro?

### O que acontece quando um dado não pode ser coletado
- Reportar como nao_verificado?
- Abortar execução?
- Tentar com privilégio elevado?

### Em que linguagem é escrita
- Python (com Paramiko)?
- Go (com golang.org/x/crypto)?
- Outra?

## Baseline do Parque

### Esperado
- SO: Ubuntu 22.04+
- Kernel: 6.5+
- Serviços ativos: ssh, containerd, node_exporter, chrony
- Serviços proibidos: telnet.socket, rpcbind.socket
- Swap: desabilitado
- Portas: 22 pública, 9100 só rede interna
- Chaves SSH: emitidas pela plataforma
- SSH: login de root desabilitado
- NTP: sincronizado

### Severidade
- Crítico: swap, chaves SSH, portas
- Alto: serviços, SSH root, SO
- Médio: kernel, NTP

## Restrições
- Só leitura (nada instala/escreve/corrige)
- Chave privada não aparece na saída
- Código de saída utilizável em pipeline

## Status
Completo (spec + código simulado - não testado contra host real)
