#!/usr/bin/env bash
# 构建用户端 + 后台，可选同步到 BCC 静态目录
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API_URL="${VITE_API_URL:-}"
HOST="${SHOP_HOST:-root@180.76.180.105}"

cd "$ROOT/mini"
VITE_BASE=/ VITE_API_URL="$API_URL" npm run build

cd "$ROOT/admin"
VITE_BASE=/admin/ VITE_API_URL="$API_URL" npm run build

rm -rf "$ROOT/dist-pages"
mkdir -p "$ROOT/dist-pages/admin"
cp -R "$ROOT/mini/dist/." "$ROOT/dist-pages/"
cp -R "$ROOT/admin/dist/." "$ROOT/dist-pages/admin/"

# BCC 路径版（相对同源 /shop-api）
cd "$ROOT/mini"
VITE_BASE=/shop/ VITE_API_URL=/shop-api npm run build
cd "$ROOT/admin"
VITE_BASE=/shop-admin/ VITE_API_URL=/shop-api npm run build

if [[ "${SYNC_BCC_STATIC:-0}" == "1" ]]; then
  ssh -o BatchMode=yes "$HOST" "mkdir -p /opt/nginx/html/shop /opt/nginx/html/shop-admin"
  rsync -az --delete "$ROOT/mini/dist/" "$HOST:/opt/nginx/html/shop/"
  rsync -az --delete "$ROOT/admin/dist/" "$HOST:/opt/nginx/html/shop-admin/"
  echo "synced BCC static /shop/ /shop-admin/"
fi

echo "Pages bundle: $ROOT/dist-pages"
echo "BCC mini dist: $ROOT/mini/dist  admin: $ROOT/admin/dist"
