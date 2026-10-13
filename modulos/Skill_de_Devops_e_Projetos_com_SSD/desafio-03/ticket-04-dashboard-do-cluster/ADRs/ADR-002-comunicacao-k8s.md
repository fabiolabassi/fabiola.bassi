# ADR - Architecture Decision Record: Comunicação com API do Kubernetes

## Status
Aceito

## Contexto
O dashboard precisa falar com a API do Kubernetes para ler Namespaces, Pods, Deployments, Services e Events. Precisa escolher método de comunicação.

## Decisão
Usar cliente oficial Python (kubernetes/python-client).

## Drivers
- **Autenticação automática**: Cliente oficial lê kubeconfig e gerencia autenticação automaticamente
- **Tipagem**: Objetos Python em vez de strings YAML, mais seguro e fácil de usar
- **Manutenção**: Mantido pelo time do Kubernetes, atualizado com versões do Kubernetes
- **Abstração**: Abstrai retry, timeout, parsing de respostas

## Alternativas Consideradas

### A1: kubectl como Subprocesso
**Descrição**: Invocar binário kubectl como subprocesso e parsear saída YAML

**Prós**:
- Usa kubectl que time já conhece
- Comandos familiares para time de infraestrutura

**Contras**:
- Parsing de saída YAML é frágil (formato pode mudar)
- Performance pior (invocar subprocesso para cada comando)
- Não há tipagem (strings em vez de objetos)
- Erros são texto, não exceções estruturadas

**Decisão**: Rejeitado. Parsing de YAML é frágil e propenso a erros. Cliente oficial fornece objetos Python tipados, mais seguros e fáceis de usar.

### A2: HTTP Direto com Apiserver
**Descrição**: Fazer requisições HTTP diretas para apiserver do Kubernetes

**Prós**:
- Máximo controle sobre requisições
- Pode otimizar performance

**Contras**:
- Precisa implementar autenticação (token, cert, auth-provider)
- Precisa implementar parsing de respostas
- Precisa implementar retry e timeout
- Complexidade muito alta

**Decisão**: Rejeitado. Reimplementar autenticação, parsing, retry, timeout é trabalho desnecessário e propenso a erros. Cliente oficial já faz tudo isso.

## Consequências
- Aplicação usa kubernetes/python-client
- Autenticação é herdada do kubeconfig local
- Objetos são Python objects com campos tipados
- Erros são exceções ApiException estruturadas

## Referências
- kubernetes/python-client: https://github.com/kubernetes-client/python
