#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/docker/docker-compose.prod.yml"
ENV_FILE="$ROOT_DIR/deploy/.env.prod"

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

SITE_HOST="$(get_env "CADDY_SITE_HOST")"
if [[ -z "$SITE_HOST" ]]; then
  echo "CADDY_SITE_HOST is not configured."
  exit 1
fi

DIST_HOST_DIR="/opt/lab-ecosystem/dist"

echo "Checking docker and compose availability..."
docker version >/dev/null
docker compose version >/dev/null

echo "Validating compose configuration..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" config >/dev/null

if grep -q "Dockerfile.frontend" "$COMPOSE_FILE"; then
  echo "Error: compose still contains frontend build config. Server-side frontend build is forbidden."
  exit 1
fi

echo "Checking Caddy + backend routes in Caddyfile..."
grep -q "handle /api/*" "$ROOT_DIR/deploy/docker/Caddyfile.prod"
grep -q "handle /static/*" "$ROOT_DIR/deploy/docker/Caddyfile.prod"
grep -q "try_files {path} /index.html" "$ROOT_DIR/deploy/docker/Caddyfile.prod"

if [[ -d "$DIST_HOST_DIR" ]]; then
  echo "Frontend dist directory exists: $DIST_HOST_DIR"
else
  echo "Warning: $DIST_HOST_DIR does not exist yet."
fi

if [[ -d /srv/lab-static ]]; then
  echo "External static directory exists: /srv/lab-static"
else
  echo "Warning: /srv/lab-static does not exist yet."
fi

echo "Checking local port usage..."
if ss -ltn | grep -qE ':(80|443)\s'; then
  echo "Warning: port 80 or 443 is already in use."
else
  echo "Ports 80 and 443 are free."
fi

echo "Checking dns resolution for $SITE_HOST ..."
if [[ "$SITE_HOST" =~ ^: ]]; then
  echo "CADDY_SITE_HOST is port-only mode ($SITE_HOST), skip dns check."
elif command -v getent >/dev/null 2>&1; then
  getent hosts "$SITE_HOST" || echo "Warning: DNS lookup failed for $SITE_HOST"
else
  echo "Warning: getent command not found, skip dns check."
fi

echo "Current running services (if any):"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps || true

echo "check-prod completed."
