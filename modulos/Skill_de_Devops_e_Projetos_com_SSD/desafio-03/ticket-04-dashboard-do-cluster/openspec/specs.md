# Specs - Ticket 04: Dashboard do Cluster

## Especificação Técnica

### Estrutura da Aplicação

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

### Funções Principais

#### 1. Conexão com Cluster
```python
def load_kube_config():
    """
    Carrega contexto corrente do kubeconfig.
    Retorna cliente configurado ou None se falhar.
    """
    try:
        config.load_kube_config()
        return client.CoreV1Api(), client.AppsV1Api()
    except Exception as e:
        return None
```

#### 2. Listar Namespaces
```python
def list_namespaces(core_v1):
    """
    Lista todos os namespaces do cluster.
    Retorna lista de strings (nomes dos namespaces).
    """
    try:
        ns_list = core_v1.list_namespace()
        return [ns.metadata.name for ns in ns_list.items]
    except ApiException as e:
        mostrar_erro(f"Erro ao listar namespaces: {e}")
        return []
```

#### 3. Listar Pods
```python
def list_pods(core_v1, namespace):
    """
    Lista pods do namespace.
    Retorna lista de dicts com:
    - name: nome do pod
    - status: estado (Running, Pending, Failed, etc.)
    - restarts: contagem de reinícios
    - reason: motivo quando em falha (ex: CrashLoopBackOff)
    """
    try:
        pod_list = core_v1.list_namespaced_pod(namespace)
        pods = []
        for pod in pod_list.items:
            status = pod.status.phase
            restarts = sum(c.restart_count for c in pod.status.container_statuses or [])
            reason = None
            if pod.status.container_statuses:
                for cs in pod.status.container_statuses:
                    if cs.state.waiting:
                        reason = cs.state.waiting.reason
                    elif cs.state.terminated:
                        reason = cs.state.terminated.reason
            pods.append({
                "name": pod.metadata.name,
                "status": status,
                "restarts": restarts,
                "reason": reason
            })
        return pods
    except ApiException as e:
        if e.status == 403:
            mostrar_erro(f"Permissão negada para pods em {namespace}")
        else:
            mostrar_erro(f"Erro ao listar pods: {e}")
        return []
```

#### 4. Listar Deployments
```python
def list_deployments(apps_v1, namespace):
    """
    Lista deployments do namespace.
    Retorna lista de dicts com:
    - name: nome do deployment
    - ready: réplicas prontas
    - desired: réplicas desejadas
    - status: status (Available, Progressing, etc.)
    """
    try:
        deploy_list = apps_v1.list_namespaced_deployment(namespace)
        deployments = []
        for deploy in deploy_list.items:
            ready = deploy.status.ready_replicas or 0
            desired = deploy.spec.replicas or 0
            status = "Available"
            for cond in deploy.status.conditions or []:
                if cond.type == "Available" and cond.status != "True":
                    status = cond.reason or "NotAvailable"
            deployments.append({
                "name": deploy.metadata.name,
                "ready": ready,
                "desired": desired,
                "status": status
            })
        return deployments
    except ApiException as e:
        if e.status == 403:
            mostrar_erro(f"Permissão negada para deployments em {namespace}")
        else:
            mostrar_erro(f"Erro ao listar deployments: {e}")
        return []
```

#### 5. Listar Services
```python
def list_services(core_v1, namespace):
    """
    Lista services do namespace.
    Retorna lista de dicts com:
    - name: nome do service
    - type: tipo (ClusterIP, NodePort)
    - has_endpoint: tem endpoint (sim/não)
    - ports: lista de portas (port, targetPort)
    """
    try:
        svc_list = core_v1.list_namespaced_service(namespace)
        services = []
        for svc in svc_list.items:
            # Verificar se tem endpoint usando EndpointSlice
            has_endpoint = check_endpoint(core_v1, namespace, svc.metadata.name)
            ports = []
            for port in svc.spec.ports or []:
                ports.append({
                    "port": port.port,
                    "targetPort": port.target_port
                })
            services.append({
                "name": svc.metadata.name,
                "type": svc.spec.type,
                "has_endpoint": has_endpoint,
                "ports": ports
            })
        return services
    except ApiException as e:
        if e.status == 403:
            mostrar_erro(f"Permissão negada para services em {namespace}")
        else:
            mostrar_erro(f"Erro ao listar services: {e}")
        return []

def check_endpoint(core_v1, namespace, service_name):
    """
    Verifica se service tem endpoint usando EndpointSlice.
    Retorna True se tem, False se não.
    """
    try:
        endpoint_slices = core_v1.list_namespaced_endpoint_slice(namespace)
        for es in endpoint_slices.items:
            if es.metadata.labels.get("kubernetes.io/service-name") == service_name:
                if es.endpoints:
                    for endpoint in es.endpoints:
                        if endpoint.addresses:
                            return True
        return False
    except ApiException:
        return False
```

#### 6. Listar Events
```python
def list_events(core_v1, namespace):
    """
    Lista events do namespace (última hora).
    Retorna lista de dicts com:
    - type: Normal ou Warning
    - reason: motivo
    - message: mensagem
    - timestamp: quando ocorreu
    - object: objeto envolvido
    """
    try:
        event_list = core_v1.list_namespaced_event(namespace)
        events = []
        for event in event_list.items:
            events.append({
                "type": event.type,
                "reason": event.reason,
                "message": event.message,
                "timestamp": event.last_timestamp,
                "object": f"{event.involved_object.kind}/{event.involved_object.name}"
            })
        # Filtrar última hora
        uma_hora_atras = datetime.now() - timedelta(hours=1)
        events = [e for e in events if e["timestamp"] >= uma_hora_atras]
        return events
    except ApiException as e:
        if e.status == 403:
            mostrar_erro(f"Permissão negada para events em {namespace}")
        else:
            mostrar_erro(f"Erro ao listar events: {e}")
        return []
```

### Layout da UI

#### Sidebar
- Seleção de namespace (dropdown)
- Busca por nome (input)

#### Área Principal
- Abas: Namespaces, Pods, Deployments, Services, Events
- Cada aba mostra tabela do recurso correspondente
- Botão "Refresh" em cada aba

### Tratamento de Erros

#### Cluster Não Responde
```python
try:
    core_v1, apps_v1 = load_kube_config()
    core_v1.list_namespace()
except ApiException as e:
    if e.status == 503:
        st.error("Cluster não responde. Tente novamente mais tarde.")
```

#### Credencial Expirada
```python
try:
    core_v1.list_namespace()
except ApiException as e:
    if e.status == 401:
        st.error("Credencial expirada. Renove a credencial e recarregue.")
```

#### Permissão Negada
```python
try:
    pods = list_pods(core_v1, namespace)
except ApiException as e:
    if e.status == 403:
        st.warning(f"Permissão negada para pods em {namespace}")
        # Continuar mostrando outros recursos
```

### Dependências
```
streamlit>=1.28.0
kubernetes>=28.0.0
```

### Execução
```bash
streamlit run dashboard/app.py
```
