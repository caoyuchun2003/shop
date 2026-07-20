<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const props = defineProps({ id: { type: [String, Number], required: true } })
const order = ref(null)
const busy = ref(false)
const err = ref('')

const statusMap = {
  pending_pay: '待支付（模拟）',
  paid: '已支付',
  ready: '待自提',
  completed: '已完成',
  cancelled: '已取消',
}

function yuan(c) {
  return (c / 100).toFixed(2)
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
  <div v-if="order" class="card">
    <h3>订单 #{{ order.id }}</h3>
    <p>状态：<strong>{{ statusMap[order.status] || order.status }}</strong></p>
    <p class="muted">自提：{{ order.pickup_point?.name }}（{{ order.pickup_point?.address }}）</p>
    <div v-for="it in order.items" :key="it.product_id" class="line">
      <span>{{ it.product_name }} × {{ it.qty }}</span>
      <span>¥{{ yuan(it.price_cents * it.qty) }}</span>
    </div>
    <p class="total">合计 <span class="price">¥{{ yuan(order.total_cents) }}</span></p>
    <p v-if="err" class="err">{{ err }}</p>
    <button v-if="order.status === 'pending_pay'" :disabled="busy" @click="pay">
      {{ busy ? '支付中…' : '模拟支付' }}
    </button>
    <p v-else class="ok">支付演示完成。后台可将订单标为「待自提 / 核销」。 </p>
  </div>
</template>

<style scoped>
h3 { margin-top: 0; }
.line { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f3f4f6; }
.total { text-align: right; margin: 12px 0; }
.err { color: #dc2626; }
.ok { color: #16a34a; font-size: 14px; }
button { width: 100%; }
</style>
