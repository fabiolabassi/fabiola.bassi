#!/bin/bash
# Script para verificar regras mecânicas do padrão de manifests da Metacortex
# Uso: ./check-manifest.sh <caminho-do-manifest.yaml>

MANIFEST_FILE=$1

if [ -z "$MANIFEST_FILE" ]; then
  echo "Uso: $0 <caminho-do-manifest.yaml>"
  exit 1
fi

if [ ! -f "$MANIFEST_FILE" ]; then
  echo "Erro: Arquivo $MANIFEST_FILE não encontrado"
  exit 1
fi

echo "=== Verificando $MANIFEST_FILE ==="
echo ""

VIOLATIONS=0

# Função para relatar violação
report_violation() {
  local severity=$1
  local rule=$2
  local message=$3

  echo "[$severity] $rule: $message"
  VIOLATIONS=$((VIOLATIONS + 1))
}

# Verificar formato de namespace
NAMESPACE=$(yq eval '.metadata.namespace' "$MANIFEST_FILE")
if [[ ! "$NAMESPACE" =~ ^[a-z]+-(dev|stg|prod)$ ]]; then
  report_violation "OBRIGATÓRIO" "Formato de namespace" "Namespace deve ser {cliente}-{ambiente} (dev, stg, prod). Atual: $NAMESPACE"
fi

# Verificar tag :latest
IMAGE=$(yq eval '.spec.template.spec.containers[0].image' "$MANIFEST_FILE" 2>/dev/null)
if [[ "$IMAGE" =~ :latest$ ]]; then
  report_violation "PROIBIDO" "Tag :latest" "Imagem não pode usar tag :latest. Atual: $IMAGE"
fi

# Verificar segredo em texto puro
if grep -q "value:.*postgres://" "$MANIFEST_FILE" 2>/dev/null; then
  report_violation "PROIBIDO" "Segredo em texto puro" "Credencial de banco em texto puro encontrado. Use secretKeyRef."
fi

# Verificar seletor casa com rótulos do pod
SELECTOR=$(yq eval '.spec.selector.matchLabels' "$MANIFEST_FILE" 2>/dev/null)
POD_LABELS=$(yq eval '.spec.template.metadata.labels' "$MANIFEST_FILE" 2>/dev/null)

if [ "$SELECTOR" != "$POD_LABELS" ]; then
  report_violation "OBRIGATÓRIO" "Seletor não casa com rótulos" "selector.matchLabels deve ser idêntico a template.metadata.labels. Seletor: $SELECTOR, Pod: $POD_LABELS"
fi

# Verificar requests e limits
REQUESTS=$(yq eval '.spec.template.spec.containers[0].resources.requests' "$MANIFEST_FILE" 2>/dev/null)
LIMITS=$(yq eval '.spec.template.spec.containers[0].resources.limits' "$MANIFEST_FILE" 2>/dev/null)

if [ "$REQUESTS" = "null" ] || [ -z "$REQUESTS" ]; then
  report_violation "OBRIGATÓRIO" "Faltam requests" "Container não tem resources.requests declarado"
fi

if [ "$LIMITS" = "null" ] || [ -z "$LIMITS" ]; then
  report_violation "OBRIGATÓRIO" "Faltam limits" "Container não tem resources.limits declarado"
fi

# Verificar probes
READINESS=$(yq eval '.spec.template.spec.containers[0].readinessProbe' "$MANIFEST_FILE" 2>/dev/null)
LIVENESS=$(yq eval '.spec.template.spec.containers[0].livenessProbe' "$MANIFEST_FILE" 2>/dev/null)

if [ "$READINESS" = "null" ] || [ -z "$READINESS" ]; then
  report_violation "OBRIGATÓRIO" "Falta readinessProbe" "Container não tem readinessProbe declarado"
fi

if [ "$LIVENESS" = "null" ] || [ -z "$LIVENESS" ]; then
  report_violation "OBRIGATÓRIO" "Falta livenessProbe" "Container não tem livenessProbe declarado"
fi

# Verificar replicas >= 2 em prod
REPLICAS=$(yq eval '.spec.replicas' "$MANIFEST_FILE" 2>/dev/null)
if [[ "$NAMESPACE" =~ -prod$ ]] && [ "$REPLICAS" -lt 2 ]; then
  report_violation "OBRIGATÓRIO" "Replicas insuficientes em prod" "Em prod, replicas deve ser >= 2. Atual: $REPLICAS"
fi

# Verificar estratégia de RollingUpdate em prod
STRATEGY=$(yq eval '.spec.strategy.type' "$MANIFEST_FILE" 2>/dev/null)
if [[ "$NAMESPACE" =~ -prod$ ]] && [ "$STRATEGY" != "RollingUpdate" ]; then
  report_violation "OBRIGATÓRIO" "Estratégia incorreta em prod" "Em prod, strategy.type deve ser RollingUpdate. Atual: $STRATEGY"
fi

# Verificar securityContext
RUN_AS_NON_ROOT=$(yq eval '.spec.template.spec.containers[0].securityContext.runAsNonRoot' "$MANIFEST_FILE" 2>/dev/null)
ALLOW_PRIVILEGE_ESCALATION=$(yq eval '.spec.template.spec.containers[0].securityContext.allowPrivilegeEscalation' "$MANIFEST_FILE" 2>/dev/null)
READ_ONLY_ROOT=$(yq eval '.spec.template.spec.containers[0].securityContext.readOnlyRootFilesystem' "$MANIFEST_FILE" 2>/dev/null)

if [ "$RUN_AS_NON_ROOT" != "true" ]; then
  report_violation "OBRIGATÓRIO" "Falta runAsNonRoot" "securityContext.runAsNonRoot deve ser true"
fi

if [ "$ALLOW_PRIVILEGE_ESCALATION" != "false" ]; then
  report_violation "OBRIGATÓRIO" "Falta allowPrivilegeEscalation: false" "securityContext.allowPrivilegeEscalation deve ser false"
fi

if [ "$READ_ONLY_ROOT" != "true" ]; then
  report_violation "OBRIGATÓRIO" "Falta readOnlyRootFilesystem" "securityContext.readOnlyRootFilesystem deve ser true"
fi

# Verificar automountServiceAccountToken
AUTOMOUNT=$(yq eval '.spec.template.spec.automountServiceAccountToken' "$MANIFEST_FILE" 2>/dev/null)
if [ "$AUTOMOUNT" != "false" ]; then
  report_violation "OBRIGATÓRIO" "Falta automountServiceAccountToken: false" "automountServiceAccountToken deve ser false quando não fala com API"
fi

# Verificar imagem de registry interno
if [[ ! "$IMAGE" =~ registry\.metacortex\.io ]]; then
  report_violation "OBRIGATÓRIO" "Imagem de registry externo" "Imagem deve apontar para registry.metacortex.io. Atual: $IMAGE"
fi

# Verificar campos proibidos
if grep -q "hostNetwork: true" "$MANIFEST_FILE" 2>/dev/null; then
  report_violation "PROIBIDO" "hostNetwork proibido" "hostNetwork: true não é permitido"
fi

if grep -q "hostPID: true" "$MANIFEST_FILE" 2>/dev/null; then
  report_violation "PROIBIDO" "hostPID proibido" "hostPID: true não é permitido"
fi

if grep -q "privileged: true" "$MANIFEST_FILE" 2>/dev/null; then
  report_violation "PROIBIDO" "privileged proibido" "privileged: true não é permitido"
fi

echo ""
echo "=== Resumo ==="
if [ $VIOLATIONS -eq 0 ]; then
  echo "Nenhuma violação encontrada nas regras mecânicas."
else
  echo "Total de violações: $VIOLATIONS"
fi

exit $VIOLATIONS
