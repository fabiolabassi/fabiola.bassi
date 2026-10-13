# Proposta - Ticket 03: Inventário e Drift de VM por SSH

## Resumo
Proposta de ferramenta CLI para auditar VMs por SSH e comparar com baseline do parque da Metacortex.

## Problema
O Roster (inventário do parque) é mantido à mão e está desatualizado. Há hosts que mudaram de papel, agentes não registrados, chaves SSH obsoletas. Ninguém sabe quantas VMs estão fora do padrão.

## Solução Proposta
Ferramenta de linha de comando que:
- Conecta por SSH a uma VM
- Coleta dados de SO, kernel, serviços, swap, portas, chaves SSH, SSH root, NTP
- Compara com baseline do parque
- Gera relatório em JSON (para Roster) e Markdown (para plantonistas)
- É apenas leitura (não corrige nada)

## Escopo Inicial (MVP)
- Suporta Ubuntu 22.04+
- Valida contra baseline.yaml fornecido
- Um host por execução
- Saída em stdout (JSON e Markdown)
- Código de saída usável em pipeline

## Fora do Escopo (Futuro)
- Multithreading (múltiplos hosts em paralelo)
- Suporte a outros SO (Debian, CentOS)
- Integração em tempo real com Roster
- Correção automática de desvios
- Inventário de containers/Kubernetes

## Tecnologia
- Python 3.10+ com Paramiko para SSH
- YAML para baseline
- JSON + Markdown para saída

## Aceitação
- Host conforme sai sem desvios
- Host com desvios sai com cada desvio classificado por severidade
- Dado não coletado aparece como "nao_verificado"
- Host inalcançável falha com mensagem clara (código != 0)
- Chave privada não aparece na saída
- Idempotente (segunda execução = mesmo resultado)
