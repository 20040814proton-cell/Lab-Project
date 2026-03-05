#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/docker/docker-compose.prod.yml"
ENV_FILE="$ROOT_DIR/deploy/.env.prod"
RESTART_CADDY="${1:-}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE"
  exit 1
fi

echo "SAFETY RED LINE:"
echo "  NEVER use docker compose down -v"
echo "  NEVER remove production docker volumes"

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
HTTP_HOST_HEADER="$SITE_HOST"
if [[ "$SITE_HOST" =~ ^: ]]; then
  HTTP_HOST_HEADER=""
fi

cd "$ROOT_DIR"

docker image inspect lab-backend:rollback >/dev/null 2>&1 || {
  echo "Missing rollback image: lab-backend:rollback"
  exit 1
}

docker tag lab-backend:rollback lab-backend:latest >/dev/null
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --no-build --force-recreate backend

if [[ "$RESTART_CADDY" == "--restart-caddy" ]]; then
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d caddy
fi

if ! wait_http_ok "http://127.0.0.1/healthz" "$HTTP_HOST_HEADER"; then
  echo "Rollback finished but healthz is still failing."
  exit 1
fi

if ! wait_http_ok "http://127.0.0.1/readyz" "$HTTP_HOST_HEADER"; then
  echo "Rollback finished but readyz is still failing."
  exit 1
fi

docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
echo "Backend rollback succeeded."
