# PRD - Product Requirements Document
## Ticket 03 - Inventário e Drift de VM por SSH

## 1. Visão Geral

### 1.1 Problema
O Roster, inventário do parque da Metacortex, é mantido à mão e está desatualizado. Há hosts que mudaram de papel, agentes instalados e nunca registrados, chaves SSH que ficaram para trás. Ninguém consegue dizer quantas VMs estão fora do padrão.

### 1.2 Solução Proposta
Ferramenta de linha de comando que audita uma VM por SSH e compara o que encontra com o baseline do parque. A ferramenta roda na máquina de quem opera (não no host auditado), recebe endereço, usuário e chave privada, conecta por SSH, coleta o estado real e compara com o baseline.

### 1.3 Objetivos
- Auditar VMs automaticamente contra baseline
- Identificar desvios (configuração fora do padrão)
- Gerar relatório em dois formatos (JSON para consumo automático, Markdown para leitura humana)
- Ser apenas leitura (não instala, escreve ou corrige nada no host)

## 2. Stakeholders

### 2.1 Primários
- **Trinity (SRE)**: Precisa de inventário atualizado para operação do parque
- **Morpheus (Engenharia)**: Precisa saber quais VMs estão fora do padrão para correção

### 2.2 Secundários
- **Nick Fury (Operações)**: Precisa de visibilidade do estado do parque

## 3. Requisitos Funcionais

### 3.1 Entrada
A ferramenta recebe:
- Endereço da VM (IP ou hostname)
- Usuário SSH
- Caminho da chave privada
- Opcional: caminho do baseline (se não fornecido, usa baseline.yaml padrão)

### 3.2 O que Coletar
A ferramenta coleta:

#### 3.2.1 Identificação
- Endereço usado na conexão
- Hostname reportado pelo host
- Instante da coleta (timestamp)

#### 3.2.2 Sistema Operacional
- Distribuição (ex: ubuntu)
- Versão (ex: 22.04.4)

#### 3.2.3 Kernel
- Versão em execução (ex: 5.15.0-118-generic)

#### 3.2.4 Serviços
- Serviços ativos (distinguindo service de socket)
- Serviços proibidos (telnet.socket, rpcbind.socket)

#### 3.2.5 Swap
- Se está habilitado
- Se habilitado, tamanho

#### 3.2.6 Portas em Escuta
- Número da porta
- Endereço de bind (0.0.0.0, 127.0.0.1, IP específico)
- Processo dono

#### 3.2.7 Chaves SSH Autorizadas
- Quantidade
- Identificação de cada uma (para saber se foram emitidas pela plataforma)

#### 3.2.8 SSH
- Login de root está habilitado ou desabilitado (configuração efetiva)

#### 3.2.9 NTP
- Se o relógio está sincronizado
- Mecanismo de sincronização (ex: systemd-timesyncd, chrony)

### 3.3 Saída
A ferramenta gera dois formatos a partir dos mesmos dados:

#### 3.3.1 JSON (para consumo automático pelo Roster)
```json
{
  "host": {"endereco": "...", "hostname": "...", "coletado_em": "..."},
  "inventario": { ... },
  "conformidade": [
    {"regra": "...", "esperado": "...", "encontrado": "...", "veredito": "...", "severidade": "..."}
  ],
  "resumo": {"conforme": N, "desvio": N, "nao_verificado": N, "por_severidade": {...}}
}
```

#### 3.3.2 Markdown (para leitura no terminal)
```markdown
# Inventário de [hostname] ([endereco])
Coletado em [timestamp] · baseline v[versão]

## Desvios
| Severidade | Regra | Esperado | Encontrado |
|---|---|---|---|
| ...

## Não verificado
| Regra | Motivo |
|---|---|
| ...

## Conforme
[lista de regras conformes]
```

### 3.4 Vereditos
Cada regra do baseline recebe um veredito:
- **conforme**: Valor encontrado é igual ao esperado
- **desvio**: Valor encontrado é diferente do esperado, acompanhado da severidade do baseline
- **nao_verificado**: O dado não pôde ser coletado (ex: usuário sem privilégio para verificar dado)

### 3.5 Comportamento com Host Inalcançável
Se o host não é alcançável (endereço errado, chave recusada, SSH fora do ar):
- A ferramenta falha com código de saída não-zero
- Mensagem de erro explica o que houve (sem stack trace)
- Não há confusão com host conforme

### 3.6 Idempotência
Duas execuções seguidas devolvem o mesmo veredito para cada regra. Só o instante da coleta muda.

## 4. Requisitos Não-Funcionais

### 4.1 Performance
- Execução completa em menos de 30 segundos para host em rede local
- Suporta até 100 hosts em paralelo (futuro)

### 4.2 Segurança
- Chave privada não aparece na saída, no log nem em mensagem de erro
- Credencial não é logada
- Conexão SSH usa apenas autenticação por chave

### 4.3 Usabilidade
- Saída JSON tem estrutura previsível para consumo por Roster
- Saída Markdown é legível no terminal
- Código de saída usável em pipeline (0 = conforme, != 0 = desvio ou erro)

### 4.4 Manutenibilidade
- Código bem documentado
- Fácil de adicionar novas regras ao baseline
- Fácil de adaptar para novos SO ou serviços

## 5. Exclusões (Out of Scope)

- Multithreading inicial (suporta apenas um host por execução)
- Interface gráfica (é CLI)
- Integração com Roster em tempo real (gera arquivo, Roster consome depois)
- Correção automática de desvios
- Inventário de containers ou Kubernetes (só VMs)
- Auditoria de serviços de aplicação (só serviços de infraestrutura)

## 6. Critérios de Aceite

### 6.1 Critérios de Pronto
1. Host conforme sai sem nenhum desvio
2. Host com desvios sai com cada desvio classificado pela severidade do baseline
3. Uma regra que não pôde ser verificada aparece como nao_verificado, separada de conforme
4. Host inalcançável falha com mensagem explicativa (sem stack trace), código != 0
5. Segunda execução devolve o mesmo resultado
6. Chave privada não aparece na saída

## 7. Histórico de Revisões

| Versão | Data | Autor | Mudanças |
|--------|------|-------|---------|
| 1.0 | 2026-08-12 | [Nome] | Versão inicial |
