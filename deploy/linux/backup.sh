#!/usr/bin/env bash
set -euo pipefail

KEEP="${1:-7}"
if ! [[ "$KEEP" =~ ^[0-9]+$ ]]; then
  echo "Usage: $0 [keep_count]"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/docker/docker-compose.prod.yml"
ENV_FILE="$ROOT_DIR/deploy/.env.prod"
BACKUP_DIR="$ROOT_DIR/deploy/backups"

echo "SAFETY RED LINE:"
echo "  NEVER use docker compose down -v"
echo "  NEVER remove production docker volumes"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE"
  exit 1
fi

get_env() {
  local key="$1"
  local default="${2:-}"
  local value
  value="$(grep -E "^${key}=" "$ENV_FILE" | head -n1 | cut -d'=' -f2- || true)"
  if [[ -z "$value" ]]; then
    echo "$default"
  else
    echo "$value"
  fi
}

DB_NAME="$(get_env "LAB_MONGO_DB" "lab_ecosystem")"
mkdir -p "$BACKUP_DIR"

cd "$ROOT_DIR"

MONGO_ID="$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps -q mongo)"
if [[ -z "$MONGO_ID" ]]; then
  echo "Mongo container is not running."
  exit 1
fi

TS="$(date +%Y%m%d-%H%M%S)"
ARCHIVE_NAME="prod-${DB_NAME}-${TS}.archive.gz"
HOST_ARCHIVE_PATH="$BACKUP_DIR/$ARCHIVE_NAME"
CONTAINER_ARCHIVE_PATH="/tmp/$ARCHIVE_NAME"

docker exec "$MONGO_ID" sh -lc "mongodump --archive='$CONTAINER_ARCHIVE_PATH' --gzip --db '$DB_NAME'"
docker cp "$MONGO_ID:$CONTAINER_ARCHIVE_PATH" "$HOST_ARCHIVE_PATH"
docker exec "$MONGO_ID" sh -lc "rm -f '$CONTAINER_ARCHIVE_PATH'"

find "$BACKUP_DIR" -maxdepth 1 -type f -name "prod-*.archive.gz" -printf '%T@ %p\n' \
  | sort -nr \
  | tail -n +$((KEEP + 1)) \
  | cut -d' ' -f2- \
  | xargs -r rm -f

echo "Backup completed: $HOST_ARCHIVE_PATH"
