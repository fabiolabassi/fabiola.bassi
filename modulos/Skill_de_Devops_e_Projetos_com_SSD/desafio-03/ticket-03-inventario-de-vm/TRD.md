# TRD - Technical Requirements Document
## Ticket 03 - Inventário e Drift de VM por SSH

## 1. Decisões de Arquitetura

### 1.1 Linguagem e Stack
**Decisão**: Python 3.10+ com Paramiko para SSH

**Alternativas consideradas**:
- **Go com golang.org/x/crypto**: Vantagem: binário único, sem dependência de runtime. Desvantagem: Mais verboso para manipulação de YAML/JSON, curva de aprendizado mais íngreme para time de infraestrutura.
- **Ruby com Net::SSH**: Vantagem: Ecossistema DevOps maduro (Chef, Puppet). Desvantagem: Menos popular atualmente, dependência de Ruby runtime.

**Justificativa**: Python é amplamente usado em automação de infraestrutura (Ansible, Terraform providers), time de infraestrutura da Metacortex provavelmente já conhece. Paramiko é a biblioteca padrão para SSH em Python, madura e estável. Mais fácil de manter por time de infraestrutura.

### 1.2 Comunicação com Host Remoto
**Decisão**: Usar Paramiko com autenticação por chave privada

**Alternativas consideradas**:
- **kubectl-style (wrapper SSH)**: Vantagem: Interface familiar. Desvantagem: Dependência de binário externo, mais frágil, menos controle sobre erros.
- **HTTP direto com apiserver**: Não aplicável - VMs não têm apiserver do Kubernetes.

**Justificativa**: Paramiko é biblioteca pura Python, não depende de binários externos, dá controle total sobre conexão SSH, tratamento de erros e timeout. Permite execução de comandos remotos e captura de saída de forma robusta.

### 1.3 Coleta de Dados: Quando Dado Não Pode Ser Coletado
**Decisão**: Reportar como "nao_verificado" com motivo, não abortar execução

**Alternativas consideradas**:
- **Abortar execução inteira**: Vantagem: Evita relatório parcial. Desvantagem: Perde todos os outros dados que foram coletados com sucesso.
- **Tentar escalar privilégio**: Vantagem: Pode coletar todos os dados. Desvantagem: Requer configuração de sudo, pode não funcionar em todos os ambientes, aumenta complexidade e risco.

**Justificativa**: Reportar como "nao_verificado" é mais útil - o relatório ainda mostra o que foi possível coletar, e o motivo fica claro. O usuário pode investigar manualmente ou executar novamente com usuário privilegiado. Abortar desperdiçaria tudo.

### 1.4 Formato de Saída
**Decisão**: Gerar JSON e Markdown na mesma execução

**Alternativas consideradas**:
- **Apenas JSON**: Vantagem: Mais simples. Desvantagem: Não legível por humanos no terminal.
- **Apenas Markdown**: Vantagem: Legível. Desvantagem: Difícil de processar automaticamente pelo Roster.
- **Dois comandos separados**: Vantagem: Flexibilidade. Desvantagem: Dobra a latência e custo de conexão SSH.

**Justificativa**: Gerar ambos na mesma execução evita dupla conexão SSH (latência e custo). Os dados são os mesmos, só mudam a formatação. JSON serve para Roster, Markdown para leitura humana no plantão.

## 2. Detalhamento Técnico

### 2.1 Estrutura do Código
```
auditor-vm.py              # Script principal
baseline.yaml             # Baseline do parque (configuração)
requirements.txt           # Dependências Python
```

### 2.2 Dependências
```
paramiko>=2.12.0
pyyaml>=6.0
```

### 2.3 Funções Principais

#### 2.3.1 Coleta de Identificação
```python
def coletar_identificacao(ssh_client):
    # hostname
    # timestamp
```

#### 2.3.2 Coleta de SO
```python
def coletar_so(ssh_client):
    # cat /etc/os-release
    #解析 lsb_release / os-release
```

#### 2.3.3 Coleta de Kernel
```python
def coletar_kernel(ssh_client):
    # uname -r
```

#### 2.3.4 Coleta de Serviços
```python
def coletar_servicos(ssh_client):
    # systemctl list-units --type=service --state=running
    # systemctl list-units --type=socket --state=listening
```

#### 2.3.5 Coleta de Swap
```python
def coletar_swap(ssh_client):
    # /proc/meminfo ou swapon --show
```

#### 2.3.6 Coleta de Portas
```python
def coletar_portas(ssh_client):
    # ss -tulpn
```

#### 2.3.7 Coleta de Chaves SSH
```python
def coletar_chaves_ssh(ssh_client):
    # cat ~/.ssh/authorized_keys
    # analizar cada chave (ssh-keygen -l -f)
```

#### 2.3.8 Coleta de SSH Root
```python
def coletar_ssh_root(ssh_client):
    # grep PermitRootLogin /etc/ssh/sshd_config
    # systemctl is-enabled sshd
```

#### 2.3.9 Coleta de NTP
```python
def coletar_ntp(ssh_client):
    # timedatectl status
    # ou chronyc tracking
```

### 2.4 Validação de Conformidade
```python
def validar_conformidade(inventario, baseline):
    # Para cada regra do baseline:
    # - Comparar esperado vs encontrado
    # - Atribuir veredito (conforme, desvio, nao_verificado)
    # - Se desvio, adicionar severidade do baseline
```

### 2.5 Geração de Saída
```python
def gerar_json(dados, conformidade):
    # Converter para JSON
    # Incluir host, inventario, conformidade, resumo

def gerar_markdown(dados, conformidade):
    # Formatar como tabela Markdown
    # Incluir desvios, não verificados, conforme
```

## 3. Decisões de Implementação

### 3.1 Tratamento de Erros
**Decisão**: Capturar exceções do Paramiko e retornar mensagem amigável

**Alternativas consideradas**:
- **Propagar exceção**: Vantagem: Verdadeiro. Desvantagem: Stack trace confuso para usuário.
- **Logar exception e continuar**: Vantagem: Mais dados. Desvantagem: Polui saída.

**Justificativa**: Capturar exceção e retornar mensagem amigável melhora usabilidade. O stack trace pode ser útil para debug, mas polui a saída normal. Em modo debug, pode logar.

### 3.2 Timeout de Conexão
**Decisão**: Timeout de 10 segundos para conexão SSH, 30 segundos para execução de comando

**Alternativas consideradas**:
- **Sem timeout**: Vantagem: Simples. Desvantagem: Pode travar indefinidamente.
- **Timeout curto (5s)**: Vantagem: Rápido. Desvantagem: Pode falhar em hosts lentos.

**Justificativa**: 10s para conexão é razoável para redes corporativas. 30s para comando permite tempo suficiente para comandos como `systemctl list-units`. Se host está muito lento, 30s ainda é aceitável sem travar.

### 3.3 Detecção de Chaves da Plataforma
**Decisão**: Verificar se chave tem comentário "platform@metacortex-platform" ou usar ssh-keygen -l para fingerprint e comparar com fingerprints conhecidos

**Alternativas consideradas**:
- **Verificar apenas comentário**: Vantagem: Simples. Desvantagem: Comentário pode não existir ou estar incorreto.
- **Verificar fingerprint**: Vantagem: Mais confiável. Desvantagem: Requer banco de dados de fingerprints.

**Justificativa**: Verificar comentário é simples e funciona para chaves emitidas pela plataforma com processo padronizado. Se o comentário não existir, reportar como "nao_verificado" ou "não foi possível determinar". Implementar banco de fingerprints seria overkill para MVP.

### 3.4 Detecção de Portas
**Decisão**: Usar `ss -tulpn` (socket statistics) para obter portas, bind address e processo

**Alternativas consideradas**:
- **netstat**: Vantagem: Mais comum. Desvantagem: "netstat é deprecado, use ss".
- **lsof**: Vantagem: Mais informações. Desvantagem: Pode não estar instalado.

**Justificativa**: `ss` é o substituto moderno de `netstat`, está disponível na maioria das distribuições Linux modernas, e fornece tudo necessário (porta, bind, processo).

## 4. Estrutura do Baseline

### 4.1 Formato YAML
```yaml
versao: 1
aplica_a: vms-do-parque
esperado:
  so:
    distribuicao: ubuntu
    versao_minima: "22.04"
  kernel:
    versao_minima: "6.5"
  servicos:
    ativos: [ssh, containerd, node_exporter, chrony]
    proibidos: [telnet.socket, rpcbind.socket]
  swap:
    habilitado: false
  portas_em_escuta:
    publicas_permitidas: [22]
    somente_rede_interna: [9100]
  chaves_ssh:
    emitidas_por: metacortex-platform
  ssh:
    login_de_root: false
  ntp:
    sincronizado: true
severidade:
  critico: [swap.habilitado, chaves_ssh.emitidas_por,
            portas_em_escuta.publicas_permitidas, portas_em_escuta.somente_rede_interna]
  alto: [servicos.ativos, servicos.proibidos, ssh.login_de_root,
         so.distribuicao, so.versao_minima]
  medio: [kernel.versao_minima, ntp.sincronizado]
```

### 4.2 Validação de Tipo
Na leitura do baseline, validar:
- versao: inteiro
- aplica_a: string
- esperado.so.distribuicao: string (ubuntu, debian, etc.)
- esperado.so.versao_minima: string (ex: "22.04")
- esperado.kernel.versao_minima: string (ex: "6.5")
- esperado.servicos.ativos: lista de strings
- esperado.servicos.proibidos: lista de strings
- esperado.swap.habilitado: booleano
- esperado.portas_em_escuta.publicas_permitidas: lista de inteiros
- esperado.portas_em_escuta.somente_rede_interna: lista de inteiros
- esperado.chaves_ssh.emitidas_por: string
- esperado.ssh.login_de_root: booleano
- esperado.ntp.sincronizado: booleano
- severidade: dicionário com listas

## 5. Código de Saída

### 5.1 Código de Retorno
- 0: Host conforme (nenhum desvio)
- 1: Host com desvios
- 2: Host inalcançável (erro de conexão SSH)
- 3: Erro de validação (baseline inválido)

## 6. Segurança

### 6.1 Proteção de Credencial
- Chave privada nunca é logada
- Chave privada nunca aparece em mensagem de erro
- Chave privada é passada como argumento de linha de comando (não em arquivo de configuração)

### 6.2 Sanitização de Saída
- Chave privada não aparece em JSON nem Markdown
- Outros dados sensíveis (se houver) não são incluídos na saída

## 7. Testes

### 7.1 Testes Unitários
- Teste de parsing de baseline
- Teste de validação de conformidade (mock de inventário)
- Teste de geração de JSON e Markdown

### 7.2 Testes de Integração
- Teste contra VM real (se disponível)
- Teste de host inalcançável (endereço inválido)

## 8. Manutenibilidade

### 8.1 Adicionando Nova Regra ao Baseline
1. Adicionar campo em `esperado`
2. Adicionar regra em `severidade` (critico, alto ou medio)
3. Adicionar lógica de validação em `validar_conformidade`

### 8.2 Adicionando Nova Verificação
1. Criar nova função `coletar_<dado>(ssh_client)`
2. Chamar função em `main`
3. Adicionar validação em `validar_conformidade`
