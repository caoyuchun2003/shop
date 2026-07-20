#!/usr/bin/env bash
# 注入 BACKEND_URL / ALLOW_ORIGIN 后 bsam package + deploy
set -euo pipefail

export PATH="${HOME}/Library/Python/3.9/bin:${HOME}/.local/bin:${PATH}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v bsam >/dev/null 2>&1; then
  echo "未找到 bsam。先: pip3 install --user bce-sam-cli"
  exit 1
fi

: "${BACKEND_URL:?请 export BACKEND_URL=http://IP/shop-api}"
ALLOW_ORIGIN="${ALLOW_ORIGIN:-https://shop.yuchuntest.com}"

BASE_TEMPLATE="${ROOT}/template.yaml"
DEPLOY_TEMPLATE="${ROOT}/template.deploy.yaml"
trap 'rm -f "$DEPLOY_TEMPLATE"' EXIT

python3 - "$BASE_TEMPLATE" "$DEPLOY_TEMPLATE" <<'PY'
import os, re, sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()

def esc(v: str) -> str:
    return v.replace("'", "''")

vars_block = (
    "        Variables:\n"
    f"          BACKEND_URL: '{esc(os.environ['BACKEND_URL'])}'\n"
    f"          ALLOW_ORIGIN: '{esc(os.environ['ALLOW_ORIGIN'])}'\n"
)

text2, n = re.subn(
    r"        Variables:\n(?:(?:          .*\n))+",
    vars_block,
    text,
    count=1,
)
if n != 1:
    raise SystemExit(f"failed to inject Variables block (matches={n})")
open(dst, "w", encoding="utf-8").write(text2)
print("已生成 template.deploy.yaml")
PY

echo ">>> bsam package"
bsam package -t "$DEPLOY_TEMPLATE"
echo ">>> bsam deploy"
bsam deploy -t "$DEPLOY_TEMPLATE"
rm -f "$ROOT"/*.zip "$ROOT"/src/*.zip
echo "部署完成。"
