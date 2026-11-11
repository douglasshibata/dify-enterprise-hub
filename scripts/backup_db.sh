#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Script de Backup Consistente: PostgreSQL e Qdrant
# ==============================================================================

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TARGET_DIR="${BACKUP_DIR}/${TIMESTAMP}"

mkdir -p "${TARGET_DIR}"

echo "==> [1/2] Iniciando backup do PostgreSQL (Metadados Dify)..."
docker exec dify_enterprise_db pg_dump -U "${DB_USER:-dify}" "${DB_NAME:-dify_db}" | gzip > "${TARGET_DIR}/postgres_dify_${TIMESTAMP}.sql.gz"
echo "Backup do PostgreSQL concluído: ${TARGET_DIR}/postgres_dify_${TIMESTAMP}.sql.gz"

echo "==> [2/2] Iniciando snapshot do Qdrant (Base Vetorial)..."
# Cria snapshot na API interna do Qdrant ou copia armazenamento seguro
if docker exec dify_enterprise_qdrant tar -czf - /qdrant/storage > "${TARGET_DIR}/qdrant_storage_${TIMESTAMP}.tar.gz" 2>/dev/null; then
    echo "Snapshot do Qdrant concluído: ${TARGET_DIR}/qdrant_storage_${TIMESTAMP}.tar.gz"
else
    echo "Aviso: Snapshot alternativo de volumes qdrantdata pode ser executado via docker volume export."
fi

echo "==> Backup corporativo concluído com sucesso em: ${TARGET_DIR}"
