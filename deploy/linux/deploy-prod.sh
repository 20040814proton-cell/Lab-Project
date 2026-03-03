#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/docker/docker-compose.prod.yml"
ENV_FILE="$ROOT_DIR/deploy/.env.prod"

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

wait_http_ok() {
  local url="$1"
  local host="${2:-}"
  local retries="${3:-40}"
  local delay="${4:-2}"

  for ((i = 1; i <= retries; i++)); do
    if [[ -n "$host" ]]; then
      if curl -fsS -H "Host: $host" "$url" >/dev/null 2>&1; then
        return 0
      fi
    else
      if curl -fsS "$url" >/dev/null 2>&1; then
        return 0
      fi
    fi
    sleep "$delay"
  done

  return 1
}

SITE_HOST="$(get_env "CADDY_SITE_HOST")"
if [[ -z "$SITE_HOST" || "$SITE_HOST" == "example.com" ]]; then
  echo "CADDY_SITE_HOST is not configured in deploy/.env.prod"
  exit 1
fi

cd "$ROOT_DIR"

docker version >/dev/null
docker compose version >/dev/null
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" config >/dev/null

if docker image inspect lab-backend:latest >/dev/null 2>&1; then
  docker tag lab-backend:latest lab-backend:rollback >/dev/null
fi
if docker image inspect lab-frontend-caddy:latest >/dev/null 2>&1; then
  docker tag lab-frontend-caddy:latest lab-frontend-caddy:rollback >/dev/null
fi

docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build

if ! wait_http_ok "http://127.0.0.1/healthz" "$SITE_HOST"; then
  echo "healthz check failed, triggering rollback..."
  "$ROOT_DIR/deploy/linux/rollback.sh"
  exit 1
fi

if ! wait_http_ok "http://127.0.0.1/readyz" "$SITE_HOST"; then
  echo "readyz check failed, triggering rollback..."
  "$ROOT_DIR/deploy/linux/rollback.sh"
  exit 1
fi

docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
echo "Production deployment succeeded for $SITE_HOST"
