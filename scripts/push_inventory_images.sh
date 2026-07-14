#!/usr/bin/env bash
set -euo pipefail

REGISTRY="docker.io"

ACCOUNT="maxxonair"
# ACCOUNT="inventorycontainer"

LOCAL_IMAGES=(
  "localhost/inventoryserver:latest"
  "localhost/inventoryapp:latest"
)

REMOTE_IMAGES=(
  "docker.io/${ACCOUNT}/inventoryserver:latest"
  "docker.io/${ACCOUNT}/inventoryapp:latest"
)

echo "Logging in to $REGISTRY..."
podman login "$REGISTRY"

for i in "${!LOCAL_IMAGES[@]}"; do
  local_ref="${LOCAL_IMAGES[$i]}"
  remote_ref="${REMOTE_IMAGES[$i]}"

  echo ""
  echo "Tagging:  $local_ref → $remote_ref"
  podman tag "$local_ref" "$remote_ref"

  echo "Pushing:  $remote_ref"
  podman push "$remote_ref"
done

echo ""
echo "Done. All images pushed successfully."