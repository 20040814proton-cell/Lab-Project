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

SITE_HOST="$(get_env "CADDY_SITE_HOST")"

if [[ -z "$SITE_HOST" || "$SITE_HOST" == "example.com" ]]; then
  echo "CADDY_SITE_HOST is not configured in deploy/.env.prod"
  exit 1
fi

echo "Checking docker and compose availability..."
docker version >/dev/null
docker compose version >/dev/null

echo "Validating compose configuration..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" config >/dev/null

echo "Checking local port usage..."
if ss -ltn | grep -qE ':(80|443)\s'; then
  echo "Warning: port 80 or 443 is already in use."
else
  echo "Ports 80 and 443 are free."
fi

if [[ -d /srv/lab-static ]]; then
  echo "Static root exists: /srv/lab-static"
else
  echo "Warning: /srv/lab-static does not exist yet. Create it before deployment."
fi

echo "Checking DNS resolution for $SITE_HOST ..."
if command -v getent >/dev/null 2>&1; then
  getent hosts "$SITE_HOST" || echo "Warning: DNS lookup failed for $SITE_HOST"
else
  echo "Warning: getent command not found, skip DNS check."
fi

echo "Current running services (if any):"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps || true

echo "check-prod completed."
