# ADR - Architecture Decision Record: Linguagem e Comunicação SSH

## Status
Aceito

## Contexto
A ferramenta de inventário de VM precisa se comunicar com hosts remotos por SSH para coletar dados e comparar com o baseline. Precisa escolher linguagem e método de comunicação.

## Decisão
Usar Python 3.10+ com Paramiko para autenticação por chave privada.

## Drivers
- **Team de infraestrutura vai manter**: Python é amplamente usado em automação (Ansible, Terraform), curva de aprendizado menor
- **Padrão em DevOps**: A maioria das ferramentas de automação da Metacortex já usa Python
- **Biblioteca madura**: Paramiko é padrão de indústria para SSH em Python, estável e bem documentado
- **Autenticação por chave**: Único método seguro para automação, não requer interação humana
- **Sem dependência de binários externos**: Pure Python não precisa de kubectl ou outros wrappers

## Alternativas Consideradas

### A1: Go com golang.org/x/crypto
**Descrição**: Usar Go com biblioteca crypto para SSH

**Prós**:
- Binário único, sem dependência de runtime
- Performance superior em operações criptográficas
- Paralelismo nativo (goroutines)

**Contras**:
- Curva de aprendizado mais íngreme para time de infraestrutura
- Manipulação de YAML/JSON mais verbosa
- Menos ecossistema de ferramentas em Go em infraestrutura da Metacortex

**Decisão**: Rejeitado. O time de infraestrutura já usa Python para outras ferramentas. A performance não é crítica para este caso (não é um serviço de alta performance).

### A2: Ruby com Net::SSH
**Descrição**: Usar Ruby com biblioteca Net::SSH

**Prós**:
- Ecossistema DevOps maduro (Chef, Puppet)
- Gems maduros para automação

**Contras**:
- Menos popular atualmente
- Dependência de Ruby runtime
- Menos comunidade ativa em automação de infraestrutura

**Decisão**: Rejeitado. Ruby perdeu popularidade em automação de infraestrutura em favor de Python. O time provavelmente não tem expertise recente em Ruby.

### A3: Wrapper SSH (kubectl-style)
**Descrição**: Invocar binário ssh como subprocesso

**Prós**:
- Interface familiar para quem usa kubectl
- Sem dependência de biblioteca SSH

**Contras**:
- Dependência de binário externo (ssh)
- Mais frágil (binário pode não estar instalado ou versão diferente)
- Menos controle sobre conexão e erros
- Parsing de saída mais complexo

**Decisão**: Rejeitado. Biblioteca pura Python (Paramiko) dá mais controle, não depende de binários externos, e torna a ferramenta mais portável.

## Consequências
- Ferramenta requer Python 3.10+ e Paramiko instalados
- Código é interpretado, não compilado (sem binário único)
- Time de infraestrutura já conhece Python
- Facil de estender com novas verificações

## Referências
- Paramiko documentation: https://www.paramiko.org/
- Python SSH best practices: https://docs.paramiko.org/en/latest/
