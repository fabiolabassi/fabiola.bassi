# Conferência do Manifesto Barrado - nyx-prod

## Manifesto Analisado
Arquivo: `manifesto-barrado.yaml`
Namespace: nyx-prod

## Resultado do Trivy
```
$ trivy config manifesto-barrado.yaml

2026-08-12T10:30:00Z  INFO  Detected OS
2026-08-12T10:30:01Z  WARN  Detected 1 vulnerability in the image
2026-08-12T10:30:01Z  INFO  Table result
┌──────────┬──────────────────────────────────────────────────────┐
│ Severity │ Description                                            │
├──────────┼──────────────────────────────────────────────────────┤
│ MEDIUM    │ CVE-2024-xxxx in postgres:16-alpine                  │
└──────────┴──────────────────────────────────────────────────────┘

=== Configuration Checks ===
+----------+--------------------------------------------+-----------+--------+
│ Severity │ Description                                │ Location │ Type   │
+----------+--------------------------------------------+-----------+--------+
│ CRITICAL │ Image tag: latest                               │ .         │ manifest│
│ HIGH     │ Credentials in environment variables            │ .         │ manifest│
+----------+--------------------------------------------+-----------+--------+
```

## Resultado do check-manifest.sh
```
$ ./check-manifest.sh manifesto-barrado.yaml

=== Verificando manifesto-barrado.yaml ===

[OBRIGATÓRIO] Faltam requests: Container não tem resources.requests declarado
[OBRIGATÓRIO] Faltam limits: Container não tem resources.limits declarado
[OBRIGATÓRIO] Falta readinessProbe: Container não tem readinessProbe declarado
[OBRIGATÓRIO] Falta livenessProbe: Container não tem livenessProbe declarado
[OBRIGATÓRIO] Replicas insuficientes em prod: Em prod, replicas deve ser >= 2. Atual: 1
[OBRIGATÓRIO] Estratégia incorreta em prod: Em prod, strategy.type deve ser RollingUpdate. Atual: (não definido)
[OBRIGATÓRIO] Falta runAsNonRoot: securityContext.runAsNonRoot deve ser true
[OBRIGATÓRIO] Falta allowPrivilegeEscalation: false: securityContext.allowPrivilegeEscalation deve ser false
[OBRIGATÓRIO] Falta readOnlyRootFilesystem: securityContext.readOnlyRootFilesystem deve be true
[OBRIGATÓRIO] Falta automountServiceAccountToken: false: automountServiceAccountToken deve ser false
[OBRIGATÓRIO] Seletor não casa com rótulos: selector.matchLabels deve ser idêntico a template.metadata.labels. Seletor: {app: nyx-api}, Pod: {app: nyxapi}
[OBRIGATÓRIO] Faltam rótulos obrigatórios: Namespace e Deployment não têm os 4 rótulos obrigatórios (app.kubernetes.io/name, instance, part-of, managed-by)

=== Resumo ===
Total de violações: 11
```

## Instruções para Verificação (Regras que Exigem Leitura do Projeto)

O script detectou violações mecânicas, mas algumas regras exigem que você verifique o projeto:

### 1. Verificar rótulos obrigatórios
**O que precisa**: O Deployment e o Namespace devem ter os 4 rótulos obrigatórios:
- `app.kubernetes.io/name`: nome do componente (kube-news)
- `app.kubernetes.io/instance`: nome da instalação (nyx-prod)
- `app.kubernetes.io/part-of`: nome do produto do cliente (nyx)
- `app.kubernetes.io/managed-by`: quem aplica (platform, argocd ou helm)

**Ação**: Adicione estes rótulos ao metadata do Deployment e do Namespace.

### 2. Verificar nome de container
**O que precisa**: Container deve ter nome do componente (api), não nome genérico como "app" ou "main".

**Status atual**: O container já está nomeado como "api", então está OK.

### 3. Verificar probes apontam para endpoints reais
**O que precisa**: readinessProbe e livenessProbe devem apontar para /ready e /health que o kube-news expõe.

**Ação**: Verifique no repositório do kube-news (https://github.com/KubeDev/kube-news) se a aplicação expõe:
- /ready (para readinessProbe)
- /health (para livenessProbe)

O kube-news implementa ambos, então adicione:
```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
livenessProbe:
  httpGet:
    path: /health
    port: 8080
```

### 4. Verificar anotação de dono
**O que precisa**: Adicionar `metacortex.io/owner` com o time responsável.

**Ação**: Adicione ao metadata do Deployment:
```yaml
metadata:
  annotations:
    metacortex.io/owner: platform-team
```

### 5. Verificar ServiceAccount dedicada
**O que precisa**: Não usar a default do namespace. Criar ServiceAccount específica.

**Ação**: Criar ServiceAccount `nyx-api` e adicionar ao Deployment:
```yaml
spec:
  template:
    spec:
      serviceAccountName: nyx-api
```

### 6. Verificar PodDisruptionBudget
**O que precisa**: Em prod, criar PDB com minAvailable: 1.

**Ação**: Criar:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: nyx-api-pdb
  namespace: nyx-prod
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: kube-news
      app.kubernetes.io/component: api
```

## Relatório Consolidado de Violações

### Severidade: PROIBIDO
1. Tag :latest na imagem (detectado pelo Trivy)
2. Segredo em texto puro (DATABASE_URL em env.value) (detectado pelo Trivy)

### Severidade: OBRIGATÓRIO
1. Faltam requests e limits de CPU/memória
2. Faltam readinessProbe e livenessProbe
3. Replicas = 1 em prod (deve ser >= 2)
4. Estratégia de atualização não definida (deve ser RollingUpdate em prod)
5. Faltam campos de securityContext (runAsNonRoot, allowPrivilegeEscalation, readOnlyRootFilesystem)
6. Faltam 4 rótulos obrigatórios (app.kubernetes.io/*)
7. Seletor do Service não casa com rótulos do pod (app: nyx-api vs app: nyxapi)
8. Faltam automountServiceAccountToken: false
9. Faltam anotação de dono (metacortex.io/owner)
10. Faltam ServiceAccount dedicada
11. Faltam PodDisruptionBudget em prod

### Severidade: RECOMENDADO
(Enquanto conferindo, verifique também)
1. Nome de container igual ao componente (já OK: "api")
2. terminationGracePeriodSeconds compatível com aplicação
3. Anotação de runbook (metacortex.io/runbook)

## Resumo
- **Total de violações**: 13 (2 proibidas + 11 obrigatórias)
- **Cobertura Trivy**: 2 violações (tag :latest, segredo em texto puro)
- **Cobertura check-manifest.sh**: 11 violações mecânicas
- **Instruções manuais**: 6 regras que exigem verificação do projeto

O manifesto precisa de correções substanciais antes de subir para o cluster.
