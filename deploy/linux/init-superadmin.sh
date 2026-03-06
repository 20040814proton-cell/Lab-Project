#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/docker/docker-compose.prod.yml"
ENV_FILE="$ROOT_DIR/deploy/.env.prod"

USERNAME="${1:-superadmin}"
PASSWORD="${2:-123456}"
DISPLAY_NAME="${3:-System Administrator}"
RESET_FLAG="${4:-}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE"
  exit 1
fi

CMD=(python /app/scripts/init_superadmin.py --username "$USERNAME" --password "$PASSWORD" --name "$DISPLAY_NAME")
if [[ "$RESET_FLAG" == "--reset-if-exists" ]]; then
  CMD+=(--reset-if-exists)
fi

cd "$ROOT_DIR"

if [[ $# -lt 2 ]]; then
  echo "No username/password provided."
  echo "Using defaults: username=superadmin password=123456"
fi

echo "Running superadmin initializer inside backend container..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T backend "${CMD[@]}"
echo "Done."
