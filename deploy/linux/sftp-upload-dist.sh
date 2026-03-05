#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <user> <host> [identity_file]"
  exit 1
fi

USER_NAME="$1"
HOST_NAME="$2"
IDENTITY_FILE="${3:-}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
REMOTE_DIST_DIR="/opt/lab-ecosystem/dist"

if [[ ! -d "$DIST_DIR" ]]; then
  echo "Missing local dist directory: $DIST_DIR"
  echo "Run pnpm build on your local machine first."
  exit 1
fi

TMP_BATCH="$(mktemp)"
cat > "$TMP_BATCH" <<EOF
mkdir /opt/lab-ecosystem
mkdir $REMOTE_DIST_DIR
put -r $DIST_DIR/* $REMOTE_DIST_DIR/
ls $REMOTE_DIST_DIR
bye
EOF

if [[ -n "$IDENTITY_FILE" ]]; then
  sftp -i "$IDENTITY_FILE" -b "$TMP_BATCH" "$USER_NAME@$HOST_NAME"
else
  sftp -b "$TMP_BATCH" "$USER_NAME@$HOST_NAME"
fi

rm -f "$TMP_BATCH"
echo "Frontend dist upload completed: $REMOTE_DIST_DIR"
