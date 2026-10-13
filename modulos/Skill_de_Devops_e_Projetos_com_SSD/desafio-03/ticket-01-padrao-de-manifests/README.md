# Ticket 01 - Skill do Padrão de Manifests

## Objetivo
Empacotar o padrão de manifests da Metacortex em uma skill que pode:
- **Modo escrita**: Gerar manifests novos já dentro do padrão
- **Modo conferência**: Apontar violações em manifest existentes

## Artefatos

- [skill-manifests.md](./skill-manifests.md) - A skill completa
- [trivy-check.sh](./trivy-check.sh) - Script para verificar o que Trivy já cobre
- [gerar-manifests-kube-news.yaml](./gerar-manifests-kube-news.yaml) - Manifests gerados do kube-news
- [conferencia-manifesto-barrado.md](./conferencia-manifesto-barrado.md) - Resultado da conferência

## Entregue

### 1. A skill completa
- Corpo da skill
- Scripts de verificação de regras mecânicas
- Instruções para regras que exigem ler o projeto

### 2. Origem da skill
- De qual fluxo nasceu
- Como foi produzida
- Com qual ferramenta

### 3. Saída real das duas execuções
- Manifests gerados de um dos 3 projetos
- Resultado da conferência do manifesto barrado

### 4. Curadoria
- Linha entre script e instrução (regra por regra)
- O que Trivy já cobria
- O que ficou no corpo vs arquivo consultado
- O que não foi empacotado e por quê
- Permissões que a skill pede

## Padrão de Manifests (Resumo)

### Bloco 1 - Identidade e Nomenclatura
- Namespace: `{cliente}-{ambiente}` (dev, stg, prod)
- 4 rótulos obrigatórios: app.kubernetes.io/name, instance, part-of, managed-by
- Seletor deve casar com rótulos do pod

### Bloco 2 - Resiliência
- requests e limits obrigatórios
- readinessProbe e livenessProbe obrigatórios
- replicas >= 2 em prod
- Estratégia de RollingUpdate em prod
- PodDisruptionBudget recomendado em prod
- terminationGracePeriodSeconds compatível

### Bloco 3 - Segurança
- Tag :latest proibida
- securityContext obrigatório (runAsNonRoot, readOnlyRootFilesystem, etc.)
- Segredo em texto puro proibido
- automountServiceAccountToken: false quando não fala com API
- ServiceAccount dedicada
- hostNetwork, hostPID, privileged proibidos
- Imagem só de registry interno

## Status
✅ Completo
