# Deployment modernizado — Chronos API
# Alterações: 3 réplicas, imagem versionada, secrets externos,
# resource limits, probes, securityContext não-root
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chronos-api
  namespace: production
  labels:
    app: chronos-api
spec:
  replicas: 3  # HA: era 1
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # zero downtime em deploys
  selector:
    matchLabels:
      app: chronos-api
  template:
    metadata:
      labels:
        app: chronos-api
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
      - name: api
        image: chronos-api:v1.0.0  # versionada, sem :latest
        ports:
        - containerPort: 8080
        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: chronos-api-secrets
              key: db-password
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: chronos-api-secrets
              key: jwt-secret
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
          failureThreshold: 3
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 20
          periodSeconds: 15
          failureThreshold: 3
        securityContext:
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
---
# PodDisruptionBudget — garante min 2 pods durante manutenções
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: chronos-api-pdb
  namespace: production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: chronos-api