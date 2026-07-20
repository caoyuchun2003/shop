<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const props = defineProps({ id: { type: [String, Number], required: true } })
const order = ref(null)
const busy = ref(false)
const err = ref('')

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
  const { data } = await api.get(`/api/orders/${props.id}`)
  order.value = data
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
  <div v-if="order" class="order fade-in">
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
    <p v-else class="ok">演示完成。商家可在后台将订单标记为「待自提 / 已完成」。</p>
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
.ok { color: var(--brand-dark); font-size: 13px; margin: 0; line-height: 1.5; }
button { width: 100%; }
</style>
