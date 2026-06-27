#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Load project-level environment variables.
if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
else
  echo ".env file not found. Create one from .env.example before deploying."
  exit 1
fi

: "${ALIYUN_USER:?Missing ALIYUN_USER}"
: "${ALIYUN_PASSWORD:?Missing ALIYUN_PASSWORD}"
: "${ALIYUN_REGISTRY:?Missing ALIYUN_REGISTRY}"
: "${ALIYUN_NAMESPACE:?Missing ALIYUN_NAMESPACE}"

BACKEND_IMAGE="${ALIYUN_BACKEND_IMAGE:-newsense-backend}"
FRONTEND_IMAGE="${ALIYUN_FRONTEND_IMAGE:-newsense-frontend}"
BACKEND_TAG="${ALIYUN_REGISTRY}/${ALIYUN_NAMESPACE}/${BACKEND_IMAGE}:latest"
FRONTEND_TAG="${ALIYUN_REGISTRY}/${ALIYUN_NAMESPACE}/${FRONTEND_IMAGE}:latest"

docker login --username="$ALIYUN_USER" --password="$ALIYUN_PASSWORD" "$ALIYUN_REGISTRY"

docker build -t "$BACKEND_IMAGE" "$ROOT_DIR/apps"
docker build -t "$FRONTEND_IMAGE" "$ROOT_DIR/apps/frontend"

docker tag "$BACKEND_IMAGE" "$BACKEND_TAG"
docker tag "$FRONTEND_IMAGE" "$FRONTEND_TAG"

docker push "$BACKEND_TAG"
docker push "$FRONTEND_TAG"

echo "Images pushed to ${ALIYUN_REGISTRY}/${ALIYUN_NAMESPACE}."