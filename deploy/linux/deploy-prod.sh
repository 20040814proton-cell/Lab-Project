#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/docker/docker-compose.prod.yml"
ENV_FILE="$ROOT_DIR/deploy/.env.prod"
WITH_CADDY="${1:-}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE"
  exit 1
fi

echo "SAFETY RED LINE:"
echo "  NEVER run docker compose down -v"
echo "  NEVER remove docker volumes for production"

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
if [[ -z "$SITE_HOST" ]]; then
  echo "CADDY_SITE_HOST is not configured in deploy/.env.prod"
  exit 1
fi

HTTP_HOST_HEADER="$SITE_HOST"
if [[ "$SITE_HOST" =~ ^: ]]; then
  HTTP_HOST_HEADER=""
fi

cd "$ROOT_DIR"

docker version >/dev/null
docker compose version >/dev/null
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" config >/dev/null

if grep -q "Dockerfile.frontend" "$COMPOSE_FILE"; then
  echo "Error: compose still contains frontend build config. Server-side frontend build is forbidden."
  exit 1
fi

if docker image inspect lab-backend:latest >/dev/null 2>&1; then
  docker tag lab-backend:latest lab-backend:rollback >/dev/null
fi

echo "Deploy backend (server-side build allowed)."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build backend

if [[ "$WITH_CADDY" == "--with-caddy" ]]; then
  echo "Reload caddy because config/static mapping changed."
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d caddy
elif [[ -z "$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps -q caddy)" ]]; then
  echo "Caddy is not running, start caddy service."
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d caddy
fi

if ! wait_http_ok "http://127.0.0.1/healthz" "$HTTP_HOST_HEADER"; then
  echo "healthz check failed, triggering backend rollback..."
  "$ROOT_DIR/deploy/linux/rollback.sh"
  exit 1
fi

if ! wait_http_ok "http://127.0.0.1/readyz" "$HTTP_HOST_HEADER"; then
  echo "readyz check failed, triggering backend rollback..."
  "$ROOT_DIR/deploy/linux/rollback.sh"
  exit 1
fi

docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
echo "Backend deployment succeeded."
echo "Reminder: frontend must be built on local machine and uploaded to /opt/lab-ecosystem/dist."
