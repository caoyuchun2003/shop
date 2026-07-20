# 邻里小店 · uni-app 微信小程序壳

与 `mini/` H5 共用同一套 FastAPI 后端（默认走 CFC HTTPS）。

## 本地运行

```bash
cd mp
npm install
npm run dev:mp-weixin
```

用**微信开发者工具**打开目录：

`mp/dist/dev/mp-weixin`

- AppID 可留空（测试号 / 游客模式）
- `manifest.json` 已设 `urlCheck: false`，便于直连 CFC
- 会话靠 `X-Session-Id`（本地 storage），跨端与 H5 一致

自定义 API：

```bash
VITE_API_URL=http://127.0.0.1:8020 npm run dev:mp-weixin
```

## 构建

```bash
npm run build:mp-weixin
# 产物：mp/dist/build/mp-weixin
```

## 页面

| 页面 | 说明 |
| --- | --- |
| 首页 | 商品列表 / 加购 / 进详情 |
| 购物车 | 改数量 / 删除 / 去结算 |
| 确认订单 | 选自提点 + 联系人 |
| 订单列表 | 状态筛选 / 取消待支付 |
| 订单详情 | 模拟支付 |

企业主体与微信支付进件到位后，可替换 `mock-pay` 为真实 `wx.requestPayment`。
