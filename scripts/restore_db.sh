#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Script de Disaster Recovery: Restauração de PostgreSQL e Qdrant
# Uso: ./scripts/restore_db.sh <caminho_para_pasta_de_backup_ou_arquivo_sql.gz>
# ==============================================================================

if [ -z "${1:-}" ]; then
    echo "Erro: Informe o caminho do arquivo de backup do PostgreSQL (.sql.gz) ou diretório."
    echo "Exemplo: ./scripts/restore_db.sh ./backups/20250101_120000/postgres_dify_20250101_120000.sql.gz"
    exit 1
fi

BACKUP_TARGET="$1"

if [ -d "${BACKUP_TARGET}" ]; then
    SQL_FILE=$(ls "${BACKUP_TARGET}"/postgres_dify_*.sql.gz 2>/dev/null | head -n 1)
else
    SQL_FILE="${BACKUP_TARGET}"
fi

if [ ! -f "${SQL_FILE}" ]; then
    echo "Erro: Arquivo de backup não encontrado em: ${SQL_FILE}"
    exit 1
fi

echo "==> [1/2] Restaurando base PostgreSQL a partir de: ${SQL_FILE}..."
gunzip -c "${SQL_FILE}" | docker exec -i dify_enterprise_db psql -U "${DB_USER:-dify}" -d "${DB_NAME:-dify_db}"
echo "Restauração do PostgreSQL concluída com sucesso."

echo "==> [2/2] Para restauração do Qdrant, descompacte os dados no volume qdrantdata e reinicie o serviço."
echo "docker compose restart qdrant"
echo "==> Recuperação de desastre finalizada com sucesso."
