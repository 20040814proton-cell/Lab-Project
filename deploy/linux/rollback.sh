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
    if curl -fsS -H "Host: $host" "$url" >/dev/null 2>&1; then
      return 0
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

docker image inspect lab-backend:rollback >/dev/null 2>&1 || { echo "Missing rollback image: lab-backend:rollback"; exit 1; }
docker image inspect lab-frontend-caddy:rollback >/dev/null 2>&1 || { echo "Missing rollback image: lab-frontend-caddy:rollback"; exit 1; }

docker tag lab-backend:rollback lab-backend:latest >/dev/null
docker tag lab-frontend-caddy:rollback lab-frontend-caddy:latest >/dev/null

docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --no-build --force-recreate

if ! wait_http_ok "http://127.0.0.1/healthz" "$SITE_HOST"; then
  echo "Rollback finished but healthz is still failing."
  exit 1
fi

if ! wait_http_ok "http://127.0.0.1/readyz" "$SITE_HOST"; then
  echo "Rollback finished but readyz is still failing."
  exit 1
fi

docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
echo "Rollback succeeded."
