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
PUBLIC_IMAGES_DIR="$ROOT_DIR/public/images"
PHOTOS_DIR="$ROOT_DIR/photos"
DEMO_DIR="$ROOT_DIR/demo"

if [[ ! -d "$PUBLIC_IMAGES_DIR" ]]; then
  echo "Missing local directory: $PUBLIC_IMAGES_DIR"
  exit 1
fi
if [[ ! -d "$PHOTOS_DIR" ]]; then
  echo "Missing local directory: $PHOTOS_DIR"
  exit 1
fi
if [[ ! -d "$DEMO_DIR" ]]; then
  echo "Missing local directory: $DEMO_DIR"
  exit 1
fi

TMP_BATCH="$(mktemp)"
cat > "$TMP_BATCH" <<EOF
mkdir /srv/lab-static
mkdir /srv/lab-static/images
mkdir /srv/lab-static/photos
mkdir /srv/lab-static/demo
put -r $PUBLIC_IMAGES_DIR/* /srv/lab-static/images/
put -r $PHOTOS_DIR/* /srv/lab-static/photos/
put -r $DEMO_DIR/* /srv/lab-static/demo/
ls /srv/lab-static
bye
EOF

if [[ -n "$IDENTITY_FILE" ]]; then
  sftp -i "$IDENTITY_FILE" -b "$TMP_BATCH" "$USER_NAME@$HOST_NAME"
else
  sftp -b "$TMP_BATCH" "$USER_NAME@$HOST_NAME"
fi

rm -f "$TMP_BATCH"
echo "SFTP static upload completed."
