#!/usr/bin/env bash
set -euo pipefail

# Move to infra directory (this script resides here)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure docker and compose available
if ! command -v docker &>/dev/null; then
  echo "Docker is not installed or not in PATH" >&2
  exit 1
fi
if ! docker compose version &>/dev/null; then
  if ! command -v docker-compose &>/dev/null; then
    echo "docker compose / docker-compose not found" >&2
    exit 1
  fi
fi

# Build and up
if docker compose version &>/dev/null; then
  docker compose pull || true
  docker compose build --no-cache
  docker compose up -d
else
  docker-compose pull || true
  docker-compose build --no-cache
  docker-compose up -d
fi

echo "\nServices are up. Useful commands:"
echo "  docker compose logs -f app"
echo "  docker compose logs -f nginx"
echo "  open http://localhost (via Nginx) or http://localhost:8000 (direct app)"