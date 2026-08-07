<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const props = defineProps({ id: { type: [String, Number], required: true } })
const order = ref(null)
const loading = ref(true)
const busy = ref(false)
const err = ref('')
const loadErr = ref('')

const ADMIN_URL = 'https://shop.yuchuntest.com/admin/'
const ADMIN_TOKEN = 'dev-admin'

const statusMap = {
  pending_pay: { label: '待支付', hint: '请完成模拟支付', tone: 'warn' },
  paid: { label: '已支付', hint: '等待商家备货', tone: 'ok' },
  ready: { label: '待自提', hint: '可前往自提点取货', tone: 'ok' },
  completed: { label: '已完成', hint: '感谢支持邻里小店', tone: 'done' },
  cancelled: { label: '已取消', hint: '', tone: 'muted' },
}

const steps = ['pending_pay', 'paid', 'ready', 'completed']

function yuan(c) {
  return (c / 100).toFixed(2)
}

function stepIndex(status) {
  const i = steps.indexOf(status)
  return i < 0 ? 0 : i
}

async function load() {
  loading.value = true
  loadErr.value = ''
  try {
    const { data } = await api.get(`/api/orders/${props.id}`)
    order.value = data
  } catch (e) {
    loadErr.value = e.response?.data?.detail || e.message || '订单加载失败'
  } finally {
    loading.value = false
  }
}

async function pay() {
  busy.value = true
  err.value = ''
  try {
    const { data } = await api.post(`/api/orders/${props.id}/mock-pay`)
    order.value = data
  } catch (e) {
    err.value = e.response?.data?.detail || e.message
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <div v-if="loading" class="order fade-in skeleton">
    <div class="card sk-block" />
    <div class="card sk-block short" />
    <p class="muted center">订单加载中…</p>
  </div>

  <div v-else-if="loadErr" class="order fade-in">
    <div class="card">
      <p class="err">{{ loadErr }}</p>
      <button @click="load">重新加载</button>
      <button class="secondary" style="width:100%;margin-top:10px" @click="router.push('/orders')">
        返回我的订单
      </button>
    </div>
  </div>

  <div v-else-if="order" class="order fade-in">
    <div class="status card" :class="statusMap[order.status]?.tone || 'muted'">
      <div class="status-label">{{ statusMap[order.status]?.label || order.status }}</div>
      <div class="status-hint">{{ statusMap[order.status]?.hint }}</div>
      <div class="status-id">订单号 #{{ order.id }}</div>
    </div>

    <div class="card timeline">
      <div v-for="(s, idx) in steps" :key="s" class="tl-item" :class="{ on: stepIndex(order.status) >= idx }">
        <div class="dot" />
        <div class="tl-text">{{ statusMap[s].label }}</div>
      </div>
    </div>

    <div class="card">
      <h3>自提信息</h3>
      <p class="pickup"><strong>{{ order.pickup_point?.name }}</strong></p>
      <p class="muted">{{ order.pickup_point?.address }}</p>
      <p class="muted buyer">{{ order.buyer_name }} · {{ order.buyer_phone }}</p>
    </div>

    <div class="card">
      <h3>商品明细</h3>
      <div v-for="it in order.items" :key="it.product_id" class="line">
        <span>{{ it.product_name }} × {{ it.qty }}</span>
        <span>¥{{ yuan(it.price_cents * it.qty) }}</span>
      </div>
      <div class="total">
        <span>实付</span>
        <span class="price"><small>¥</small>{{ yuan(order.total_cents) }}</span>
      </div>
    </div>

    <p v-if="err" class="err">{{ err }}</p>
    <button v-if="order.status === 'pending_pay'" :disabled="busy" @click="pay">
      {{ busy ? '支付中…' : '模拟支付 ¥' + yuan(order.total_cents) }}
    </button>

    <div v-if="order.status !== 'pending_pay' && order.status !== 'cancelled'" class="card demo-next">
      <h3>继续演示 · 商家后台</h3>
      <p class="demo-copy">用户端已支付。打开运营后台，把本单标成「待自提」再「核销完成」，走完闭环。</p>
      <ol class="demo-steps">
        <li>打开后台，令牌填 <code>{{ ADMIN_TOKEN }}</code></li>
        <li>找到订单 #{{ order.id }} → 标待自提 → 核销完成</li>
      </ol>
      <a class="admin-cta" :href="ADMIN_URL" target="_blank" rel="noopener">打开管理后台 →</a>
    </div>

    <button class="secondary" style="width:100%;margin-top:10px" @click="router.push('/orders')">
      返回我的订单
    </button>
  </div>
</template>

<style scoped>
.order { padding-top: 6px; display: flex; flex-direction: column; gap: 10px; }

.status { padding: 16px; color: #fff; }
.status.warn { background: linear-gradient(135deg, #f59e0b, #ea580c); }
.status.ok { background: linear-gradient(135deg, #0d9f6e, #087a55); }
.status.done { background: linear-gradient(135deg, #4b5563, #111827); }
.status.muted { background: linear-gradient(135deg, #9ca3af, #6b7280); }

.status-label { font-size: 20px; font-weight: 800; }
.status-hint { margin-top: 4px; font-size: 13px; opacity: 0.92; }
.status-id { margin-top: 10px; font-size: 12px; opacity: 0.85; }

.timeline {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  padding: 12px 10px;
}

.tl-item { text-align: center; opacity: 0.35; }
.tl-item.on { opacity: 1; }

.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #d1d5db;
  margin: 0 auto 6px;
}

.tl-item.on .dot { background: var(--brand); box-shadow: 0 0 0 4px var(--brand-soft); }
.tl-text { font-size: 11px; font-weight: 700; color: #4b5563; }

h3 { margin: 0 0 10px; font-size: 15px; }
.pickup { margin: 0 0 4px; }
.buyer { margin-top: 8px; }

.line {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 14px;
}

.total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-top: 12px;
  font-weight: 700;
}

.err { color: #dc2626; font-size: 13px; margin: 0; }
.center { text-align: center; margin: 8px 0 0; }
button { width: 100%; }

.skeleton .sk-block {
  height: 88px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s ease infinite;
}
.skeleton .sk-block.short { height: 56px; }
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.demo-next h3 { margin-bottom: 8px; }
.demo-copy { margin: 0; font-size: 13px; color: #4b5563; line-height: 1.55; }
.demo-steps {
  margin: 10px 0 14px;
  padding-left: 18px;
  font-size: 13px;
  color: #374151;
  line-height: 1.6;
}
.demo-steps code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  background: #ecfdf5;
  color: #047857;
  padding: 1px 6px;
  border-radius: 6px;
}
.admin-cta {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  background: linear-gradient(135deg, #0d9f6e, #087a55);
  color: #fff;
  font-weight: 700;
  font-size: 14px;
  text-decoration: none;
}
</style>
