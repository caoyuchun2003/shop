/**
 * Record demo: H5 order → mock pay → admin fulfill
 */
const { chromium } = require('playwright')
const path = require('path')
const fs = require('fs')

const OUT = path.resolve(__dirname, '../docs/demo')
const H5 = process.env.DEMO_H5 || 'http://127.0.0.1:5173/'
const ADMIN = process.env.DEMO_ADMIN || 'http://127.0.0.1:5174/'

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

async function main() {
  fs.mkdirSync(OUT, { recursive: true })
  for (const f of fs.readdirSync(OUT)) {
    if (f.endsWith('.webm') || f.endsWith('.mp4')) fs.unlinkSync(path.join(OUT, f))
  }

  // --- H5 ---
  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2,
    recordVideo: { dir: OUT, size: { width: 390, height: 844 } },
    locale: 'zh-CN',
  })
  const page = await context.newPage()

  await page.goto(H5, { waitUntil: 'domcontentloaded', timeout: 60000 })
  await page.locator('button.add:not([disabled])').first().waitFor({ timeout: 30000 })
  await sleep(1000)

  await page.locator('button.add:not([disabled])').first().click()
  await sleep(1000)

  await page.locator('a.fab').click()
  await sleep(1000)

  await page.getByRole('button', { name: '去结算' }).click()
  await sleep(1000)

  await page.getByPlaceholder('怎么称呼您').fill('演示用户')
  await page.getByPlaceholder('用于取货通知').fill('13800138000')
  await sleep(500)
  await page.getByRole('button', { name: '提交订单' }).click()
  await page.waitForURL(/\/orders\/\d+/, { timeout: 30000 })
  await sleep(1200)

  await page.getByRole('button', { name: /模拟支付/ }).click()
  await sleep(2000)
  console.log('H5 paid:', page.url())

  await context.close()
  await browser.close()

  let vids = fs.readdirSync(OUT).filter((f) => f.endsWith('.webm'))
  if (!vids.length) throw new Error('no H5 video')
  fs.renameSync(path.join(OUT, vids[0]), path.join(OUT, '01-h5-order-pay.webm'))

  // --- Admin ---
  const browser2 = await chromium.launch({ headless: true })
  const context2 = await browser2.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: OUT, size: { width: 1280, height: 720 } },
    locale: 'zh-CN',
  })
  const admin = await context2.newPage()
  await admin.goto(ADMIN + 'login', { waitUntil: 'domcontentloaded', timeout: 60000 })
  await sleep(800)

  if (await admin.getByPlaceholder('请输入 X-Admin-Token').count()) {
    await admin.getByPlaceholder('请输入 X-Admin-Token').fill('dev-admin')
    await admin.getByRole('button', { name: '进入后台' }).click()
    await sleep(1500)
  }

  await admin.goto(ADMIN + 'orders', { waitUntil: 'domcontentloaded', timeout: 60000 })
  await sleep(2000)

  const readyBtn = admin.getByRole('button', { name: '标为待自提' }).first()
  if (await readyBtn.count()) {
    await readyBtn.click()
    await sleep(1500)
  } else {
    console.warn('no 标为待自提 button — maybe already fulfilled')
  }

  const doneBtn = admin.getByRole('button', { name: '核销完成' }).first()
  if (await doneBtn.count()) {
    await doneBtn.click()
    await sleep(1500)
  }

  await sleep(800)
  await context2.close()
  await browser2.close()

  vids = fs.readdirSync(OUT).filter((f) => f.endsWith('.webm') && f !== '01-h5-order-pay.webm')
  if (!vids.length) throw new Error('no admin video')
  fs.renameSync(path.join(OUT, vids[0]), path.join(OUT, '02-admin-fulfill.webm'))

  console.log('OK →', OUT)
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
