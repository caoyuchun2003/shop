# 微信开发者工具 · 预览清单

`npm run build:mp-weixin` 已能产出可导入目录。按下面做一次即可录真机感画面。

## 一次性准备

1. 安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 本机已装 Node 18+

## 构建

```bash
cd mp
npm install          # 首次
npm run build:mp-weixin
```

开发热更新（改代码时用）：

```bash
npm run dev:mp-weixin
# 导入目录改为：mp/dist/dev/mp-weixin
```

## 导入项目

1. 打开微信开发者工具 → **导入项目**
2. 目录选：`mp/dist/build/mp-weixin`（或上面的 `dev` 目录）
3. AppID：**测试号** 或 游客模式（可留空，与 `manifest.json` 一致）
4. 后端默认走 CFC HTTPS（见 `src/utils/api.js`）；本地 API 时：

```bash
VITE_API_URL=http://127.0.0.1:8020 npm run build:mp-weixin
```

并在开发者工具勾选：**不校验合法域名**（`urlCheck: false` 已写入 manifest，正式上架前要配合法域名）。

## 走通闭环（约 2 分钟）

- [ ] 首页能拉到商品
- [ ] 加购 → 购物车数量正确
- [ ] 选自提点下单
- [ ] 订单详情「模拟支付」成功
- [ ] 订单列表能看到状态变化
- [ ]（可选）点工具栏 **真机预览**，扫码在手机上看同一流程

## 录屏建议

竖屏模拟器或真机预览，按 `docs/DEMO-SCRIPT.md` 前 60 秒流程走；可与 H5 片段剪到同一条演示视频。

## 常见问题

| 现象 | 处理 |
| --- | --- |
| 商品空白 / 网络错误 | 看控制台请求是否打到 CFC；本机防火墙；换 `VITE_API_URL` |
| 合法域名报错 | 详情 → 本地设置 → 不校验合法域名、web-view、TLS |
| 导入后白屏 | 确认选的是 `dist/build/mp-weixin` 不是 `mp/` 根目录 |
| 要正式上架 | 企业主体 AppID + 合法域名 HTTPS + 支付商户号（当前为演示桩） |
