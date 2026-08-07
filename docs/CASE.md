# 邻里小店 · 案例说明

| 项 | 内容 |
| --- | --- |
| 场景 | 社区自提轻团购（非美团级商城） |
| 演示地址 | 用户端 https://shop.yuchuntest.com/ · 后台 https://shop.yuchuntest.com/admin/ |
| 案例页（对外甩） | https://yuchuntest.com/cases/shop.html |
| 演示视频 | 案例页内嵌；仓库 [`demo/`](demo/)（`.webm` / `shop-demo.mp4`）与关键截图 |
| 演示脚本 | [`DEMO-SCRIPT.md`](DEMO-SCRIPT.md) |
| 微信预览 | [`mp/PREVIEW.md`](../mp/PREVIEW.md) |
| 演示账号 | 后台令牌 `dev-admin` |
| 工期参考 | 骨架 + 支付闭环约 1～2 周；视觉与运营台打磨约再 3～5 天 |
| 技术栈 | Vue 3 · FastAPI · SQLite · Element Plus · uni-app（微信壳）· 百度 CFC 网关 · BCC 容器 · GitHub Pages |
| 支付说明 | **模拟支付演示桩**；接单可替换为微信支付 |

## 功能清单

**用户端 H5**（`mini/`）
- 商品列表（封面 / 分类 / 加购）
- 购物车（改数量 / 删除）
- 选自提点下单
- 模拟支付
- 我的订单（状态筛选 / 取消待支付）

**微信小程序壳**（`mp/` · uni-app）
- 与 H5 共用 API：首页 / 详情 / 购物车 / 下单 / 模拟支付 / 订单
- 微信开发者工具预览；正式上架需企业主体 AppID

**管理后台**
- 令牌登录
- 运营看板
- 订单核销（待自提 / 完成）
- 商品增改删、上下架、库存、封面 URL
- 自提点增改删

## 状态流转

`pending_pay` → 模拟支付 → `paid` → 后台备货 → `ready` → 核销 → `completed`

## 明确未做（防范围膨胀）

分销、复杂优惠券、真实微信进件、完整退款仲裁、多店铺。uni-app 微信壳已提供（`mp/`，开发者工具预览；正式发布需企业主体 AppID）。

## 接单话术一句

「轻量社区团购：用户下单 + 模拟支付 + 后台核销，一套可演示的小程序/H5 业务闭环；真实微信登录支付可在企业主体到位后接入。」
