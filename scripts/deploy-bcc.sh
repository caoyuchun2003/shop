#!/usr/bin/env bash
# 同步后端到 BCC、构建镜像、启动容器、更新 nginx
set -euo pipefail

HOST="${SHOP_HOST:-root@180.76.180.105}"
REMOTE_DIR="${SHOP_REMOTE_DIR:-/opt/shop}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo ">>> sync server -> $HOST:$REMOTE_DIR"
ssh -o BatchMode=yes -o ConnectTimeout=20 "$HOST" "mkdir -p $REMOTE_DIR/server $REMOTE_DIR/html/mini $REMOTE_DIR/html/admin"
rsync -az --delete \
  --exclude venv --exclude __pycache__ --exclude .pytest_cache --exclude 'data/*.db' \
  "$ROOT/server/" "$HOST:$REMOTE_DIR/server/"

echo ">>> build & run container"
ssh -o BatchMode=yes "$HOST" bash -s <<EOF
set -euo pipefail
cd $REMOTE_DIR/server
podman build -t localhost/shop:latest .
podman stop shop 2>/dev/null || true
podman rm shop 2>/dev/null || true
mkdir -p $REMOTE_DIR/data
podman run -d --name shop --restart=always \
  -p 8020:8020 \
  -e ADMIN_TOKEN=\${ADMIN_TOKEN:-dev-admin} \
  -v $REMOTE_DIR/data:/app/data \
  localhost/shop:latest
sleep 2
curl -sf http://127.0.0.1:8020/health
echo
EOF

echo ">>> ensure nginx /shop-api/ + static paths"
ssh -o BatchMode=yes "$HOST" bash -s <<'EOF'
set -euo pipefail
CONF=/opt/nginx/conf/conf.d/default.conf
if ! grep -q 'location /shop-api/' "$CONF"; then
  python3 - <<'PY'
from pathlib import Path
p = Path("/opt/nginx/conf/conf.d/default.conf")
text = p.read_text()
block = """
    # 邻里小店 API (podman :8020)
    location /shop-api/ {
        proxy_pass http://10.88.0.1:8020/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Session-Id $http_x_session_id;
        proxy_set_header X-Admin-Token $http_x_admin_token;
        proxy_buffering off;
        proxy_read_timeout 30s;
    }

    location = /shop {
        return 301 /shop/;
    }

    location /shop/ {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /shop/index.html;
    }

    location = /shop-admin {
        return 301 /shop-admin/;
    }

    location /shop-admin/ {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /shop-admin/index.html;
    }

"""
needle = "    # video-agent FastAPI"
if needle not in text:
    raise SystemExit("nginx marker not found")
p.write_text(text.replace(needle, block + needle, 1))
print("nginx conf patched")
PY
  podman exec nginx nginx -t
  podman exec nginx nginx -s reload
else
  echo "nginx already has /shop-api/"
fi
EOF

echo "BCC API ready: http://180.76.180.105/shop-api/health"
