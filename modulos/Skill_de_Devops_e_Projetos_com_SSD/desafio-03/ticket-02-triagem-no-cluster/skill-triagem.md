# Skill: Triagem de Cluster

## Descrição
Skill de triagem de cluster Kubernetes que define um método único para plantonistas começarem a investigar um alerta, usando mcp-server-kubernetes em modo não destrutivo.

## Método de Triagem

### Por Onde Começar
A partir do sintoma relatado ("está fora do ar", "pod não sobe", "service não entrega tráfego"), começar pelo que está mais próximo da superfície:

1. **Se o sintoma menciona um recurso específico** (ex: "o pod X não sobe"): Comece por esse recurso
2. **Se o sintoma é genérico** (ex: "está fora do ar"): Comece pelo Deployment que está em 0/ready
3. **Se o sintoma menciona Service** (ex: "service não tem endpoint"): Comece pelo Service e verifique se tem Endpoints

### Ordem para Descer as Camadas
Quando um recurso está em estado problemático, desça as camadas nesta ordem:

1. **Pod**: Ver status, restarts, motivo de falha
2. **Eventos do Pod**: Ler eventos para entender o fluxo
3. **Logs do Pod**: Ler logs para identificar erros específicos
4. **Deployment**: Ver replicas prontas vs desejadas
5. **Service**: Ver se o Service tem Endpoints
6. **Namespace**: Ver se há problemas no namespace (quota, NetworkPolicy)

### Quando Cruzar Duas Fontes vs Aprofundar numa Só
- **Cruzar quando**: O sintoma sugere correlação entre recursos (ex: "Service não entrega, mas pods estão saudáveis" → cruze Service + Endpoints)
- **Aprofundar quando**: Um recurso tem múltiplos sintomas (ex: Pod com CrashLoopBackOff → aprofunde eventos + logs)

### Quando Parar
A triagem PARA quando:
- A causa raiz for identificada (ex: "OOMKilled por falta de memória")
- O componente que está quebrado for apontado (ex: "Deployment está em 0/ready porque pods não conseguem subir")
- Um próximo passo claro de ação for definido (ex: "aumentar memory limit")

A triagem NÃO aplica correções, mesmo que o agente tenha permissão. É só leitura.

## Passos Específicos por Sintoma

### Sintoma: Pod em CrashLoopBackOff
1. Ver status do Pod (kubectl get pod)
2. Ver eventos do Pod (kubectl describe pod)
3. Ver logs do container (kubectl logs --previous)
4. Identificar causa (OOMKilled, exit code, erro no log)
5. PARAR - causa identificada

### Sintoma: Pod em Pending
1. Ver status do Pod
2. Ver eventos do Pod (kubectl describe pod)
3. Identificar motivo (FailedScheduling, Insufficient cpu, Insufficient memory)
4. PARAR - causa identificada

### Sintoma: Deployment em 0/ready
1. Ver status do Deployment (kubectl get deployment)
2. Ver Pods do Deployment (kubectl get pods -l app=...)
3. Para cada Pod problemático, seguir "Pod em CrashLoopBackOff" ou "Pod em Pending"
4. PARAR - causa identificada

### Sintoma: Service não tem endpoint
1. Ver Endpoints do Service (kubectl get endpoints)
2. Se Endpoints vazio: verificar se seletor do Service casa com rótulos dos Pods
3. Ver Pods no namespace (kubectl get pods)
4. Comparar seletor vs rótulos
5. PARAR - causa identificada (mismatch de seletor)

### Sintoma: Aplicação responde 503
1. Ver Deployment (está 0/ready?)
2. Se Deployment OK: verificar Service
3. Se Service OK: verificar Pods (estão saudáveis?)
4. Ver logs dos Pods (há erro?)
5. PARAR - causa identificada

## Limite Absoluto
A triagem **SÓ LÊ o cluster**. Nenhuma correção é aplicada, nem quando o agente tem permissão para isso. Se o agente tentar aplicar correção, a skill deve interromper.

## Ferramenta
- **mcp-server-kubernetes**: Acesso ao cluster Kubernetes em modo não destrutivo
- **kubectl**: Comandos específicos quando necessário

## Exemplo de Uso

**Entrada**: "o pod do nyx-prod não sobe"

**Processo da skill**:
1. Identificar namespace: nyx-prod
2. Listar pods no namespace (kubectl get pods -n nyx-prod)
3. Identificar pod problemático pelo status
4. Ver eventos do pod (kubectl describe pod)
5. Ver logs do pod (kubectl logs)
6. Apontar causa e PARAR

**Saída**: "O pod nyx-api-xxx está em CrashLoopBackOff. Eventos mostram OOMKilled. Logs indicam out of memory. Causa: limite de memória insuficiente."

## Como Usar

**Uso**: "Triage o cluster para [sintoma]"

**Entrada**: Sintoma relatado pelo plantonista

**Saída**: Diagnóstico estruturado com:
- O que foi verificado (em ordem)
- O que foi encontrado
- Causa identificada
- Próximo passo (sem aplicar correção)

## Permissões
A skill precisa de:
- Acesso ao cluster via mcp-server-kubernetes
- Permissões de leitura no cluster (get, list, describe)
- **NÃO** permissões de escrita (apply, delete, scale, edit)

## Garantia de Modo Não Destrutivo
A skill usa mcp-server-kubernetes em modo não destrutivo, o que significa:
- Apenas operações de leitura (get, list, describe)
- Nenhuma operação de escrita
- Se o agente tentar executar comando de escrita, a skill interrompe
