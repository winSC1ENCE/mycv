#!/usr/bin/env bash
# Nightly Postgres backup for mycv.
# Invoked by mycv-backup.service / mycv-backup.timer — see docs/deployment.md.

set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-/opt/mycv/docker-compose.prod.yml}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/mycv}"
POSTGRES_USER="${POSTGRES_USER:-mycv}"
POSTGRES_DB="${POSTGRES_DB:-mycv}"
RETAIN_DAYS="${RETAIN_DAYS:-14}"

STAMP=$(date -u +%Y%m%d-%H%M%S)
DEST="${BACKUP_DIR}/mycv-${STAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "[backup] Starting dump → ${DEST}"
docker compose -f "${COMPOSE_FILE}" exec -T db \
    pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" \
    | gzip -9 > "${DEST}"

echo "[backup] Removing backups older than ${RETAIN_DAYS} days"
find "${BACKUP_DIR}" -name "mycv-*.sql.gz" -mtime +"${RETAIN_DAYS}" -delete

echo "[backup] Done. Size: $(du -sh "${DEST}" | cut -f1)"
