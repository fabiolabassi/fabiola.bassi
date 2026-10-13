# Specs - Ticket 03: Inventário e Drift de VM por SSH

## Especificação Técnica

### Coleta de Dados

#### 1. Identificação
- **Método**: `hostname` para hostname, datetime local para timestamp
- **Saída**: `{"hostname": "...", "coletado_em": "ISO8601Z"}`

#### 2. Sistema Operacional
- **Método**: `cat /etc/os-release`
- **Saída**: `{"distribuicao": "ubuntu", "versao": "22.04.4"}`
- **Validação**: Comparar distribuicao e versao_minima com baseline

#### 3. Kernel
- **Método**: `uname -r`
- **Saída**: `{"versao": "5.15.0-118-generic"}`
- **Validação**: Comparar versao_minima com baseline

#### 4. Serviços
- **Método**: `systemctl list-units --type=service --state=running`
- **Saída**: `[{"nome": "ssh.service", "tipo": "service"}]`
- **Validação**: Verificar se serviços ativos esperados estão rodando, serviços proibidos não estão

#### 5. Swap
- **Método**: `swapon --show`
- **Saída**: `{"habilitado": true, "tamanho": "4G"}` ou `{"habilitado": false}`
- **Validação**: Comparar habilitado com baseline

#### 6. Portas em Escuta
- **Método**: `ss -tulpn`
- **Saída**: `[{"porta": 22, "bind": "0.0.0.0", "processo": "sshd"}]`
- **Validação**: Verificar se portas públicas permitidas estão OK, portas internas só em rede interna

#### 7. Chaves SSH
- **Método**: `cat ~/.ssh/authorized_keys`
- **Saída**: `{"quantidade": 3, "chaves": [{"identificacao": "platform@metacortex-platform"}]}`
- **Validação**: Verificar se todas as chaves foram emitidas pela plataforma

#### 8. SSH Root
- **Método**: `grep PermitRootLogin /etc/ssh/sshd_config`
- **Saída**: `{"login_de_root": false}`
- **Validação**: Comparar login_de_root com baseline

#### 9. NTP
- **Método**: `timedatectl status`
- **Saída**: `{"sincronizado": true, "mecanismo": "systemd-timesyncd"}`
- **Validação**: Comparar sincronizado com baseline

### Validação de Conformidade

Para cada regra do baseline:
1. Extrair valor esperado
2. Comparar com valor encontrado
3. Atribuir veredito:
   - `conforme`: valor encontrado == valor esperado
   - `desvio`: valor encontrado != valor esperado
   - `nao_verificado`: valor não pôde ser coletado
4. Se desvio, adicionar severidade do baseline

### Formato de Saída

#### JSON
```json
{
  "host": {"endereco": "...", "hostname": "...", "coletado_em": "..."},
  "inventario": { ... },
  "conformidade": [ ... ],
  "resumo": {"conforme": N, "desvio": N, "nao_verificado": N, "por_severidade": {...}}
}
```

#### Markdown
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
[lista]
```

### Códigos de Saída
- 0: Host conforme (nenhum desvio)
- 1: Host com desvios
- 2: Host inalcançável (erro de conexão SSH)
- 3: Erro de validação (baseline inválido)

### Tratamento de Erros
- Erro de conexão SSH: Mensagem amigável, código 2
- Erro de comando: Reportar como "nao_verificado" para regra específica
- Erro de baseline: Mensagem de erro, código 3
