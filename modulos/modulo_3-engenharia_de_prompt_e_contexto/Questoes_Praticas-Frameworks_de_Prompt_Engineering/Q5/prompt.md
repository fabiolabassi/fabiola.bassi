BEFORE:
O manifest Kubernetes abaixo foi escrito há 3 anos para o Chronos API gateway
Problemas críticos: réplica única, imagem :latest, secrets em plaintext, sem resources,
sem probes, container rodando como root, sem pdb nem rollingupdate configurado.
 
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chronos-api
  namespace: production
spec:
  replicas: 1
  selector:
    matchLabels:
      app: chronos-api
  template:
    metadata:
      labels:
        app: chronos-api
    spec:
      containers:
      - name: api
        image: chronos-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DB_PASSWORD
          value: "P@ssw0rd2023!"
        - name: JWT_SECRET
          value: "hvt-jwt-prod-secret"
 
AFTER:
Versão modernizada com:
- réplicas: 3 (alta disponibilidade)
- imagem versionada: chronos-api:v1.0.0
- secrets via secretKeyRef (Secret: chronos-api-secrets)
- resources: requests e limits para API Python/Flask
- liveness em get /healthz e readiness em GET /ready, porta 8080
- SecurityContext: runAsNonRoot: true, readOnlyRootFilesystem: true, allowPrivilegeEscalation: false, runAsUser: 1000
- RollingUpdate: maxSurge 1, maxUnavailable 0
- PodDisruptionBudget separado: minAvailable 2
 
BRIDGE:
Entregue dois manifests yml separados por "---:" o deployment modernizado e o pdb
Adicione comentários yaml explicando cada bloco adicionado
Entregue apenas yaml válido, sem texto ou markdown fora dos comentários inline