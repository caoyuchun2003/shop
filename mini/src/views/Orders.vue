<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const orders = ref([])
const loading = ref(true)
const filter = ref('all')

const statusMap = {
  pending_pay: { label: '待支付', tone: 'warn' },
  paid: { label: '已支付', tone: 'ok' },
  ready: { label: '待自提', tone: 'ok' },
  completed: { label: '已完成', tone: 'done' },
  cancelled: { label: '已取消', tone: 'muted' },
}

const filters = [
  { key: 'all', label: '全部' },
  { key: 'pending_pay', label: '待支付' },
  { key: 'paid', label: '已支付' },
  { key: 'ready', label: '待自提' },
  { key: 'completed', label: '已完成' },
]

function yuan(c) {
  return (c / 100).toFixed(2)
}

function filtered() {
  if (filter.value === 'all') return orders.value
  return orders.value.filter((o) => o.status === filter.value)
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/orders')
    orders.value = data
  } finally {
    loading.value = false
  }
}

async function cancel(o) {
  if (!confirm(`取消订单 #${o.id}？`)) return
  try {
    await api.post(`/api/orders/${o.id}/cancel`)
    await load()
  } catch (e) {
    alert(e.response?.data?.detail || e.message)
  }
}

onMounted(load)
</script>

<template>
  <div class="orders-page fade-in">
    <h2 class="page-title">我的订单</h2>
    <p class="page-sub">查看状态，待支付可继续付款或取消</p>

    <div class="chips">
      <button
        v-for="f in filters"
        :key="f.key"
        class="chip"
        :class="{ active: filter === f.key }"
        @click="filter = f.key"
      >
        {{ f.label }}
      </button>
    </div>

    <div v-if="loading" class="card">
      <div class="skeleton" style="height: 88px; margin-bottom: 10px" />
      <div class="skeleton" style="height: 88px" />
    </div>

    <div v-else-if="!filtered().length" class="card empty">
      <div class="empty-art">📦</div>
      <h3>暂无订单</h3>
      <p>去首页加购几样邻居都在买的</p>
      <button class="ghost" @click="router.push('/')">去逛逛</button>
    </div>

    <div v-else class="list">
      <article
        v-for="o in filtered()"
        :key="o.id"
        class="card order"
        @click="router.push(`/orders/${o.id}`)"
      >
        <div class="top">
          <strong>#{{ o.id }}</strong>
          <span class="tag" :class="statusMap[o.status]?.tone">
            {{ statusMap[o.status]?.label || o.status }}
          </span>
        </div>
        <div class="items">
          <div v-for="it in o.items" :key="it.product_id">
            {{ it.product_name }} × {{ it.qty }}
          </div>
        </div>
        <div class="bottom">
          <span class="muted">{{ o.pickup_point?.name }}</span>
          <span class="price"><small>¥</small>{{ yuan(o.total_cents) }}</span>
        </div>
        <div v-if="o.status === 'pending_pay'" class="actions" @click.stop>
          <button class="ghost" @click="cancel(o)">取消</button>
          <button @click="router.push(`/orders/${o.id}`)">去支付</button>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.orders-page { padding-top: 6px; }

.chips {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 12px;
  scrollbar-width: none;
}
.chips::-webkit-scrollbar { display: none; }

.chip {
  flex: 0 0 auto;
  padding: 7px 12px;
  border-radius: 999px;
  background: #fff;
  color: #6b7280;
  border: 1px solid var(--line);
  box-shadow: none;
  font-size: 12px;
  font-weight: 700;
}
.chip.active {
  background: var(--brand);
  color: #fff;
  border-color: transparent;
}

.list { display: flex; flex-direction: column; gap: 10px; }

.order { cursor: pointer; }

.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.tag {
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
}
.tag.warn { background: #fff7ed; color: #c2410c; }
.tag.ok { background: var(--brand-soft); color: var(--brand-dark); }
.tag.done { background: #f3f4f6; color: #4b5563; }
.tag.muted { background: #f3f4f6; color: #9ca3af; }

.items { font-size: 13px; color: #374151; line-height: 1.5; }

.bottom {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-top: 10px;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: 8px;
  margin-top: 12px;
}

.empty {
  text-align: center;
  padding: 36px 20px;
}
.empty-art { font-size: 48px; margin-bottom: 8px; }
.empty h3 { margin: 0 0 6px; }
.empty p { margin: 0 0 16px; color: var(--muted); font-size: 13px; }
</style>
