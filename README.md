# 邻里小店（社区轻团购 Demo）

作品集项目：商品 → 购物车 → 下单 → **模拟支付** → 后台核销。

> 支付为演示桩，接单时可替换为微信支付。第一期用户端为 **H5**（后续可套 uni-app 出小程序）。

## 目录

| 目录 | 说明 | 本地端口 |
| --- | --- | --- |
| `server/` | FastAPI + SQLite | `8020` |
| `mini/` | 用户端 H5（Vue3） | `5173` |
| `admin/` | 管理后台（Vue3 + Element Plus） | `5174` |
| `cfc/` | 百度 CFC HTTPS 网关 | — |

## 本地启动

```bash
# 1) 后端
cd server
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
./venv/bin/uvicorn app.main:app --reload --port 8020

# 2) 用户端
cd mini && npm install && npm run dev

# 3) 后台
cd admin && npm install && npm run dev
```

- 用户端：http://127.0.0.1:5173/
- 后台：http://127.0.0.1:5174/ （登录令牌默认 `dev-admin`）

## 测试

```bash
cd server && ./venv/bin/pytest -v
```

## 部署

```bash
# BCC 后端 + nginx /shop-api/
./scripts/deploy-bcc.sh

# 静态（BCC 路径版）
SYNC_BCC_STATIC=1 VITE_API_URL=/shop-api ./scripts/build-web.sh

# CFC 网关（Pages 用 HTTPS）
export BACKEND_URL=http://180.76.180.105/shop-api
export ALLOW_ORIGIN=https://shop.yuchuntest.com
./cfc/scripts/deploy.sh
```

线上：

- 用户端：https://shop.yuchuntest.com/
- 后台：https://shop.yuchuntest.com/admin/ （登录令牌默认 `dev-admin`）
- API 网关：`https://2jng249qsad2r.cfc-execute.bj.baidubce.com`
- BCC 直连（备用）：http://180.76.180.105/shop/ · http://180.76.180.105/shop-admin/

## 状态流转

`pending_pay` →（模拟支付）→ `paid` →（后台）→ `ready` → `completed`
