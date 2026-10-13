# Runbook: High Memory Usage - Chronos API

## Contexto do Alerta

**Alerta:** [CRITICAL] High memory usage on Chronos API pods (>85% for 10min)

**Frequência:** Aproximadamente 4 vezes por semana  
**Tempo médio de resposta sem runbook:** 30 a 40 minutos

**Ambiente:**
- Cluster: EKS (Kubernetes)
- Namespace: production
- Réplicas atuais: 6
- HPA configurado: min 4 / max 12 / CPU target 70%
- Deploy: Argo CD (repositório hvt/chronos-api)
- Dependências: Ledger (PostgreSQL) e Reactor (SQS)
- Observabilidade: métricas em /metrics, logs no Beacon, dashboards no Grafana
- Ferramentas disponíveis: kubectl, aws cli, argocd cli
- Canal de comunicação: #oncall-chronos
- Escalação: @chronos-core (15min horário comercial, 30min fora)

## Diagnóstico Inicial

### Passo 1: Verificar status dos pods
**Comando:**
```bash
kubectl get pods -n production -l app=chronos-api
```

**Output normal:**
```
NAME                           READY   STATUS    RESTARTS   AGE
chronos-api-xxx-1              1/1     Running   0          2h
chronos-api-xxx-2              1/1     Running   0          2h
chronos-api-xxx-3              1/1     Running   0          2h
chronos-api-xxx-4              1/1     Running   0          2h
chronos-api-xxx-5              1/1     Running   0          2h
chronos-api-xxx-6              1/1     Running   0          2h
```

**Output anormal + ação:**
- Pods em estado `Pending`, `CrashLoopBackOff`, ou `OOMKilled`: Verificar eventos do pod (Passo 2)
- Menos de 4 pods running: Verificar HPA (Passo 3)

---

### Passo 2: Verificar consumo de memória por pod
**Comando:**
```bash
kubectl top pods -n production -l app=chronos-api
```

**Output normal:**
```
NAME                           CPU(cores)   MEMORY(bytes)
chronos-api-xxx-1              150m         256Mi
chronos-api-xxx-2              180m         280Mi
chronos-api-xxx-3              160m         240Mi
chronos-api-xxx-4              170m         260Mi
chronos-api-xxx-5              140m         230Mi
chronos-api-xxx-6              155m         250Mi
```

**Output anormal + ação:**
- Memória > 85% do limite (ex: > 435Mi se limite for 512Mi) em 2+ pods: Ir para Ações de Mitigação
- 1 pod com memória muito alta (>90%) enquanto outros normais: Verificar logs desse pod específico (Passo 4)

---

### Passo 3: Verificar comportamento do HPA
**Comando:**
```bash
kubectl get hpa chronos-api -n production
```

**Output normal:**
```
NAME          REFERENCE                      TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
chronos-api   Deployment/chronos-api        70%/70%         4         12        6          30d
```

**Output anormal + ação:**
- Replicas = 12 (máximo) e CPU target ainda alto: Escalar manualmente via Argo CD (Ação de Mitigação 2)
- Replicas < 4 (mínimo): Verificar cluster resources e node capacity

---

### Passo 4: Verificar logs de pods com alto consumo
**Comando:**
```bash
kubectl logs chronos-api-xxx-1 -n production --tail=100 --since=10m
```

**Output normal:**
```
[INFO] Request processed successfully
[INFO] Health check passed
[INFO] Metrics collection complete
```

**Output anormal + ação:**
- Erros de conexão com Ledger (PostgreSQL): Verificar status do banco de dados
- Erros de conexão com Reactor (SQS): Verificar fila SQS
- Mensagens de "out of memory" ou GC频繁: Escalar aumento de memória (Ação de Mitigação 3)
- Muitos erros 500: Verificar dashboards Grafana para padrões de tráfego

---

### Passo 5: Verificar métricas Prometheus
**Comando:**
```bash
kubectl port-forward svc/chronos-api 9090:8080 -n production
curl http://localhost:9090/metrics | grep -E "memory|heap|gc"
```

**Output normal:**
```
process_resident_memory_bytes 2.684e+08
jvm_memory_used_bytes{area="heap"} 1.5e+08
jvm_gc_pause_seconds_count 15
```

**Output anormal + ação:**
- heap_used > 80% de heap_max: Escalar aumento de memória (Ação de Mitigação 3)
- gc_pause_seconds_count aumentando rapidamente: Verificar memory leak no código (escalar para @chronos-core)

## Ações de Mitigação

### Ação 1: Restart manual dos pods com alto consumo (menos invasiva)
**Quando:** 1-2 pods com memória > 90%, outros normais

**Comando:**
```bash
kubectl delete pod chronos-api-xxx-1 -n production
```

**Expectativa:** Pod será recriado automaticamente pelo deployment controller, liberando memória

---

### Ação 2: Escalar réplicas via Argo CD (invasividade média)
**Quando:** 4+ pods com memória > 85%, HPA já no máximo (12 réplicas)

**Comando:**
```bash
argocd app get chronos-api
argocd app set chronos-api -p replicaCount=8
argocd app sync chronos-api
```

**Expectativa:** Deployment será atualizado para 8 réplicas, distribuindo carga

---

### Ação 3: Aumentar limite de memória (mais invasiva)
**Quando:** Todos os pods consistentemente > 85%, restart não resolve

**Passos:**
1. Fazer checkout do repositório hvt/chronos-api
2. Editar values.yaml ou deployment manifest
3. Aumentar `resources.limits.memory` de 512Mi para 768Mi ou 1Gi
4. Commit e push
5. Argo CD fará sync automático

**Comando git:**
```bash
git clone <repo-url>
cd chronos-api
# Editar deployment manifest
git add .
git commit -m "Increase memory limit to address high usage alerts"
git push
```

**Expectativa:** Pods serão recriados com novo limite de memória

## Critérios de Escalação

Escalar para @chronos-core em #oncall-chronos quando:

1. **Memória > 95% em mais de 4 pods** após tentar Ação 1 e Ação 2
2. **Replicas no máximo (12) e memória ainda > 85%** após 10 minutos
3. **Padrão de memory leak detectado** (GC frequentes, heap sempre crescente)
4. **Dependências externas afetadas** (Ledger ou Reactor com problemas)
5. **Tempo de diagnóstico > 25 minutos** sem resolução

**Template de mensagem:**
```
@chronos-core ESCALAÇÃO REQUIRED

Alerta: High memory usage on Chronos API pods
Situação: [descrever brevemente - ex: 6 pods com memória > 90%, HPA no máximo]
Ações tomadas: [listar ações tentadas - ex: Restart pods, escala para 8 replicas]
Tempo de diagnóstico: X minutos
Próximo passo aguardando: [ex: Aprovação para aumentar memory limit]
```

## Critério de Encerramento

Encerrar incidente quando:

1. **Todos os pods com memória < 75%** estável por 15 minutos
2. **Alerta não disparar** por 20 minutos
3. **Logs sem erros de memória** nos últimos 15 minutos
4. **HPA funcionando normalmente** (replicas entre 4-12, CPU target < 80%)
5. **Documentar no incident post-mortem:**
   - Causa raiz (se identificada)
   - Ações tomadas
   - Ações preventivas para futuro

**Comando final de verificação:**
```bash
kubectl top pods -n production -l app=chronos-api
kubectl get hpa chronos-api -n production
```