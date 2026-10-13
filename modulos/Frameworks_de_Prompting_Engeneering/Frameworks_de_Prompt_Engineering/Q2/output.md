#!/usr/bin/env bash
# =============================================================================
# ledger-backup.sh
# Descrição : Backup diário do banco ledger_prod para S3 com retenção 30 dias
# Uso       : bash ledger-backup.sh
# Cron      : 0 2 * * * /usr/local/bin/ledger-backup.sh >> /var/log/ledger-backup.log 2>&1
# =============================================================================
set -euo pipefail
 
DB_HOST="ledger-db.internal.hvt.io"
DB_PORT="5432"
DB_NAME="ledger_prod"
DB_USER="backup_user"
S3_BUCKET="hvt-ledger-backups"
S3_REGION="us-east-1"
BACKUP_DIR="/var/backups/ledger"
LOG_FILE="/var/log/ledger-backup.log"
RETENTION_DAYS=30
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
FILENAME="ledger_prod_${TIMESTAMP}.sql.gz"
LOCAL_PATH="${BACKUP_DIR}/${FILENAME}"
 
log() { echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] $*" | tee -a "${LOG_FILE}"; }
die() { log "ERROR: $*"; exit 1; }
 
cleanup() {
  [[ -f "${LOCAL_PATH}" ]] && rm -f "${LOCAL_PATH}" && log "Temp removido"
}
trap cleanup EXIT
 
# Validar dependências
for cmd in pg_dump gzip aws; do
  command -v "${cmd}" >/dev/null 2>&1 || die "Dependência ausente: ${cmd}"
done
 
# Verificar PGPASSWORD
[[ -n "${PGPASSWORD:-}" ]] || die "PGPASSWORD não está definida"
 
mkdir -p "${BACKUP_DIR}"
log "Iniciando backup de ${DB_NAME}"
 
# Dump + compactação em pipeline
PGPASSWORD="${PGPASSWORD}" pg_dump \
  --host="${DB_HOST}" --port="${DB_PORT}" \
  --username="${DB_USER}" --no-password \
  --format=plain "${DB_NAME}" | gzip -9 > "${LOCAL_PATH}" \
  || die "Falha no pg_dump/gzip"
 
DUMP_SIZE=$(du -sh "${LOCAL_PATH}" | cut -f1)
log "Dump concluído. Tamanho: ${DUMP_SIZE}"
 
# Upload para S3
aws s3 cp "${LOCAL_PATH}" "s3://${S3_BUCKET}/backups/${FILENAME}" \
  --region "${S3_REGION}" --storage-class STANDARD_IA \
  || die "Falha no upload S3"

# Retenção: remover objetos mais antigos que 30 dias
CUTOFF=$(date -u -d "${RETENTION_DAYS} days ago" +"%Y-%m-%dT%H:%M:%SZ")
aws s3 ls "s3://${S3_BUCKET}/backups/" --region "${S3_REGION}" \
  | awk '{print $4}' | while read -r obj; do
    OBJ_DATE=$(echo "${obj}" | grep -oP '\d{8}_\d{6}' \
      | sed 's/\(....\)\(..\)\(..\)_\(..\)\(..\)\(..\)/\1-\2-\3T\4:\5:\6Z/')
    if [[ "${OBJ_DATE}" < "${CUTOFF}" ]]; then
      aws s3 rm "s3://${S3_BUCKET}/backups/${obj}" --region "${S3_REGION}"
    fi
  done
 
rm -f "${LOCAL_PATH}"
trap - EXIT
log "Backup finalizado com sucesso: ${FILENAME}"
exit 0