# TRD - Technical Requirements Document
## Ticket 04 - Dashboard do Cluster

## 1. Decisões de Arquitetura

### 1.1 Linguagem e Stack
**Decisão**: Python 3.10+ com Streamlit para UI

**Alternativas consideradas**:
- **Go com servidor HTTP + HTML/JS**: Vantagem: Binário único, performance superior. Desvantagem: Curva de aprendizado mais íngreme para time de infraestrutura, desenvolvimento de UI mais complexo.
- **JavaScript (React/Next.js)**: Vantagem: Ecossistema maduro de componentes UI. Desvantagem: Curva de aprendizado para time de infraestrutura, requer bundler/compilação.
- **Python com Dash**: Vantagem: Similar ao Streamlit. Desvantagem: Menos popular para dashboards simples.

**Justificativa**: Python é linguagem que time de infraestrutura já conhece (usado em Ticket 03). Streamlit é framework Python para dashboards que requer pouco código para UI, ideal para MVP. Time de infraestrutura pode manter facilmente.

### 1.2 Como Falar com API do Kubernetes
**Decisão**: Usar cliente oficial Python (kubernetes/python-client)

**Alternativas consideradas**:
- **kubectl como subprocesso**: Vantagem: Usa kubectl que time já conhece. Desvantagem: Parsing de saída YAML é frágil, performance pior, não há tipagem.
- **HTTP direto com apiserver**: Vantagem: Máximo controle. Desvantagem: Precisa implementar autenticação, contexto, tipagem, complexo.

**Justificativa**: Cliente oficial Python abstrai autenticação, contexto, tipagem e retry. É mantido pelo time do Kubernetes, maduro e estável. Parsing de objetos é nativo (objetos Python em vez de strings YAML).

### 1.3 Como Manter Tela Atualizada
**Decisão**: Consulta sob demanda (refresh manual)

**Alternativas consideradas**:
- **Consulta em intervalo fixo (polling)**: Vantagem: Tela sempre atualizada. Desvantagem: Carga constante no apiserver, desperdício se ninguém está olhando.
- **Observação de mudanças (watch)**: Vantagem: Reativo, carga mínima. Desvantagem: Complexidade de implementação (gerenciar streams, reconexões), estado local complexo.

**Justificativa**: Consulta sob demanda é mais simples de implementar e não impõe carga no apiserver. Para ferramenta de triagem (plantão), refresh manual é suficiente - plantonista clica refresh quando precisa.

### 1.4 Fonte dos Endpoints
**Decisão**: EndpointSlice (Endpoints está sendo descontinuado)

**Alternativas consideradas**:
- **Endpoints**: Vantagem: Simples, amplamente usado. Desvantagem: Est sendo descontinuado pelo Kubernetes.
- **EndpointSlice**: Vantagem: Futuro do Kubernetes, escalável. Desvantagem: Sintaxe diferente.

**Justificativa**: O exercício menciona que Endpoints está sendo descontinuado. EndpointSlice é o futuro e continuará funcionando. Implementar com EndpointSlice desde o início evita migração no futuro.

### 1.5 Recorte da Primeira Fatia
**Decisão**: MVP inclui apenas o essencial: Namespaces, Pods, Deployments, Services, Events

**O que entra na primeira spec**:
- Namespaces (lista)
- Pods (estado, restarts, motivo de falha)
- Deployments (réplicas prontas vs desejadas)
- Services (tipo, tem endpoint, portas)
- Events (filtro por namespace)
- Filtro por namespace
- Busca por nome
- Tratamento de falhas (cluster não responde, credencial expirada, permissão negada)

**O que fica para depois**:
- Graficos/métricas
- Logs de pods
- Detalhes avançados de objetos
- ConfigMaps e Secrets
- Ingress
- StatefulSets, DaemonSets, Jobs
- CronJobs

**Justificativa**: PRD especifica "mínimo" e os 5 recursos listados são o essencial para triagem. Adicionar mais recursos estende o escopo sem valor claro para MVP. Fica para iterações futuras.

## 2. Detalhamento Técnico

### 2.1 Estrutura do Código
```
dashboard/
├── app.py              # Aplicação Streamlit principal
├── k8s_client.py       # Wrapper para cliente Kubernetes
├── views/
│   ├── namespaces.py   # View de namespaces
│   ├── pods.py         # View de pods
│   ├── deployments.py  # View de deployments
│   ├── services.py     # View de services
│   └── events.py       # View de events
└── requirements.txt    # Dependências Python
```

### 2.2 Dependências
```
streamlit>=1.28.0
kubernetes>=28.0.0
```

### 2.3 Funções Principais

#### 2.3.1 Conexão com Cluster
```python
def load_kube_config():
    # Carrega contexto corrente do kubeconfig
    # Retorna cliente configurado
```

#### 2.3.2 Listar Namespaces
```python
def list_namespaces(client):
    # Listar todos os namespaces
    # Retornar lista de objetos Namespace
```

#### 2.3.3 Listar Pods
```python
def list_pods(client, namespace):
    # Listar pods do namespace
    # Extrair estado, restarts, motivo de falha
    # Retornar lista com estado formatado
```

#### 2.3.4 Listar Deployments
```python
def list_deployments(client, namespace):
    # Listar deployments do namespace
    # Extrair réplicas prontas vs desejadas
    # Retornar lista com status formatado
```

#### 2.3.5 Listar Services
```pytho
def list_services(client, namespace):
    # Listar services do namespace
    # Listar endpointSlices para verificar se tem endpoint
    # Retornar lista com status de endpoint
```

#### 2.3.6 Listar Events
```python
def list_events(client, namespace):
    # Listar events do namespace
    # Filtrar eventos recentes (última hora)
    # Retornar lista formatada
```

### 2.4 Tratamento de Erros

#### 2.4.1 Cluster Não Responde
```python
try:
    client.list_namespace()
except ApiException as e:
    if e.status == 503:
        mostrar_erro("Cluster não responde. Tente novamente mais tarde.")
```

#### 2.4.2 Credencial Expirada
```python
try:
    client.list_namespace()
except ApiException as e:
    if e.status == 401:
        mostrar_erro("Credencial expirada. Renove a credencial e recarregue.")
```

#### 2.4.3 Permissão Negada
```python
try:
    client.list_pods(namespace)
except ApiException as e:
    if e.status == 403:
        mostrar_erro(f"Permissão negada para pods em {namespace}")
        # Continuar mostrando outros recursos
```

## 3. Decisões de Implementação

### 3.1 Layout da UI
**Decisão**: Sidebar com seleção de namespace, área principal com abas para cada recurso

**Alternativas consideradas**:
- **Uma página longa com tudo**: Vantagem: Simples. Desvantagem: Scroll excessivo, difícil de usar.
- **Modal para cada recurso**: Vantagem: Foco. Desvantagem: Muitos cliques, workflow lento.

**Justificativa**: Sidebar + abas é padrão em dashboards Kubernetes (ex: Lens, Rancher). É familiar para plantonistas e eficiente.

### 3.2 Refresh Automático vs Manual
**Decisão**: Refresh manual com botão

**Alternativas consideradas**:
- **Refresh automático a cada X segundos**: Vantagem: Tela sempre atualizada. Desvantagem: Carga no apiserver, pode ser perturbador.
- **Refresh automático apenas quando aba é visível**: Vantagem: Carga menor. Desvantagem: Complexidade adicional.

**Justificativa**: Refresh manual dá controle ao plantonista. Para triagem, o plantonista sabe quando precisa de dados atualizados.

### 3.3 Mostrar EndpointSlice vs Endpoints
**Decisão**: Internamente usar EndpointSlice, mas mostrar "Endpoint" na UI

**Alternativas consideradas**:
- **Mostrar "EndpointSlice"**: Vantagem: Preciso. Desvantagem: Confuso para usuários não familiarizados.
- **Mostrar "Endpoints"**: Vantagem: Familiar. Desvantagem: Impreciso.

**Justificativa**: Mostrar "Endpoint" na UI é mais claro para usuários. Internamente usar EndpointSlice é correto tecnicamente.

## 4. Segurança

### 4.1 Apenas Leitura
- Aplicação não expõe botões de apply, delete, scale
- Cliente Kubernetes é usado apenas para operações de leitura (get, list)

### 4.2 Credenciais
- Usa kubeconfig local (já existente na máquina)
- Não armazena credenciais adicionais
- Segurança herdada do kubeconfig do usuário

## 5. Testes

### 5.1 Testes Unitários
- Teste de parsing de estado de Pod
- Teste de parsing de status de Deployment
- Teste de verificação de endpoint

### 5.2 Testes de Integração
- Teste contra cluster real (se disponível)
- Teste de cluster não responde
- Teste de credencial expirada
- Teste de permissão negada

## 6. Manutenibilidade

### 6.1 Adicionando Novo Recurso
1. Criar nova view em views/
2. Adicionar aba na UI
3. Adicionar função de listagem em k8s_client.py
4. Adicionar filtro e busca

### 6.2 Adicionando Novo Cluster
- Nenhuma mudança necessária
- Usuário troca contexto do kubeconfig por fora
- Aplicação lê contexto corrente automaticamente
