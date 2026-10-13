# Origem e Curadoria - Ticket 03

## Origem do Projeto

### Fluxo de Criação
O projeto nasceu do seguinte fluxo:

1. **Leitura do PRD**: Li o PRD criado anteriormente para entender o problema (Roster desatualizado) e a solução (ferramenta CLI de auditoria por SSH).

2. **Escrita do TRD**: Escrevi o TRD documentando as decisões técnicas:
   - Linguagem e stack (Python + Paramiko)
   - Comunicação com host remoto (SSH via Paramiko)
   - Coleta de dados (quando dado não pode ser coletado)
   - Formato de saída (JSON + Markdown)

3. **Criação de ADR**: Criei ADR-001 documentando a decisão de linguagem e comunicação SSH, com alternativas consideradas e justificativa.

4. **Ciclo do OpenSpec**: Criei proposta.md, tarefas.md e specs.md seguindo o ciclo do OpenSpec.

5. **Implementação**: Implementei auditor-vm.py com todas as funções de coleta e validação.

6. **Validação**: Criei evidencia-execucao.md com saídas simuladas (não tenho acesso a host real para execução).

### Ferramenta Usada
- **Claude (Anthropic)**: Para escrita de PRD, TRD, ADRs, specs e código Python
- **Python 3.10+**: Linguagem de implementação
- **Paramiko**: Biblioteca SSH

## Curadoria

### Onde a Spec Precisou Ser Corrigida Durante Implementação

#### Correção 1: Validação de Versão de SO
**O que estava na spec**: Comparação direta de strings (ex: "22.04.4" >= "22.04")

**O que o agente entendeu**: Usar comparação de versão Python (que pode não funcionar para strings com pontos)

**Correção**: Implementei comparação simplificada de string que funciona para Ubuntu 22.04+. Em uma implementação mais robusta, usaria `packaging.version` para comparação semântica de versão.

#### Correção 2: Coleta de Portas
**O que estava na spec**: Usar `ss -tulpn` e parsear saída

**O que o agente entendeu**: Parsing da saída do `ss` pode ser frágil se o formato mudar entre distribuições

**Correção**: Implementei parsing simplificado que assume formato padrão do `ss`. Em produção, poderia usar biblioteca Python para parsing ou validar com regex mais robusto.

#### Correção 3: Detecção de Chaves da Plataforma
**O que estava na spec**: Verificar comentário da chave (platform@metacortex-platform)

**O que o agente entendeu**: Comentário pode não existir ou estar incorreto

**Correção**: Implementei verificação de comentário com fallback para "desconhecida". Em produção, poderia usar `ssh-keygen -l` para fingerprint e comparar com banco de fingerprints conhecidos.

### O que o Agente Entendeu Diferente do que Eu Escrevi

#### Diferença 1: Função de Coleta de Serviços
**O que eu escrevi na spec**: "systemctl list-units --type=service --state=running"

**O que o agente implementou**: Também coleta sockets com "systemctl list-units --type=socket --state=listening"

**Diferença**: O agente adicionou coleta de sockets além de services. Isso é bom porque o baseline menciona telnet.socket e rpcbind.socket como proibidos, e esses são sockets, não services.

**Decisão**: Mantive a implementação do agente (melhor).

#### Diferença 2: Tratamento de Erro em Coleta
**O que eu escrevi na spec**: "Reportar como nao_verificado quando dado não puder ser coletado"

**O que o agente implementou**: Cada função de coleta tem try/except e retorna "nao_verificado" se falhar

**Diferença**: O agente implementou try/except em cada função individualmente, o que é mais granular do que eu havia especificado.

**Decisão**: Mantive a implementação do agente (mais robusta).

### Decisões de Curadoria

#### Por que Python em Vez de Go
**Decisão**: Python com Paramiko em vez de Go com golang.org/x/crypto

**Alternativas consideradas**:
- Go: Binário único, performance superior, mas curva de aprendizado mais íngreme para time de infraestrutura
- Ruby: Ecossistema DevOps maduro, mas menos popular atualmente

**Justificativa**: Python é amplamente usado em automação de infraestrutura (Ansible, Terraform providers). Time de infraestrutura provavelmente já conhece. Paramiko é biblioteca padrão e madura.

#### Por que Reportar como nao_verificado em Vez de Abortar
**Decisão**: Quando dado não pode ser coletado, reportar como "nao_verificado" em vez de abortar execução

**Alternativas consideradas**:
- Abortar execução: Evita relatório parcial, mas perde todos os outros dados
- Tentar escalar privilégio: Pode coletar todos os dados, mas requer configuração de sudo

**Justificativa**: Reportar como "nao_verificado" é mais útil - o relatório ainda mostra o que foi possível coletar. O usuário pode investigar manualmente ou executar novamente com usuário privilegiado.

#### Por que Gerar JSON e Markdown na Mesma Execução
**Decisão**: Gerar ambos na mesma execução em vez de ter dois comandos separados

**Alternativas consideradas**:
- Apenas JSON: Mais simples, mas não legível por humanos
- Apenas Markdown: Legível, mas difícil de processar automaticamente
- Dois comandos separados: Flexível, mas dobra latência e custo

**Justificativa**: Gerar ambos na mesma execução evita dupla conexão SSH (latência e custo). Os dados são os mesmos, só mudam a formatação.

#### Por que Não Implementar Multithreading Inicialmente
**Decisão**: MVP suporta apenas um host por execução

**Alternativas consideradas**:
- Multithreading desde o início: Mais eficiente para auditoria de vários hosts
- Multithreading futuro: Mais simples para MVP

**Justificativa**: Multithreading adiciona complexidade (gerenciamento de conexões SSH, sincronização, tratamento de erros paralelos). Para MVP, um host por execução é suficiente. Multithreading pode ser adicionado depois se necessário.

#### Por que Não Implementar Integração com Roster em Tempo Real
**Decisão**: Ferramenta gera arquivo JSON, Roster consome depois

**Alternativas consideradas**:
- Integração em tempo real: Roster consome diretamente da ferramenta
- Arquivo intermediário: Ferramenta gera arquivo, Roster consome

**Justificativa**: Integração em tempo real acopla os sistemas e adiciona complexidade. Arquivo intermediário desacopla e permite que Roster consuma quando quiser. Também permite uso da ferramenta independentemente do Roster.

### Limitações Conhecidas

1. **Comparação de versão simplificada**: Implementação atual usa comparação de string que pode não funcionar para todas as versões. Em produção, usar `packaging.version`.

2. **Parsing de ss frágil**: Parsing da saída do `ss` assume formato padrão. Pode quebrar se formato mudar.

3. **Detecção de chakes por comentário**: Verificação de comentário não é robusta. Em produção, usar fingerprint.

4. **Sem testes reais**: Como não tenho acesso a host real, a validação é simulada. Em produção, executar contra hosts reais.

5. **Sem multithreading**: Um host por execução. Auditoria de muitos hosts seria lenta.

### Próximos Passos (Se Fosse Continuar)

1. **Adicionar testes unitários**: Testar cada função de coleta com mocks
2. **Adicionar testes de integração**: Testar contra VM real
3. **Melhorar comparação de versão**: Usar `packaging.version`
4. **Adicionar multithreading**: Suportar múltiplos hosts em paralelo
5. **Melhorar detecção de chaves**: Usar fingerprint em vez de comentário
6. **Adicionar suporte a outros SO**: Debian, CentOS
7. **Integração com Roster**: API para consumo em tempo real
