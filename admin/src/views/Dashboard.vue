<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const loading = ref(true)
const orders = ref([])
const products = ref([])

const statusMeta = {
  pending_pay: { label: '待支付', color: '#f59e0b' },
  paid: { label: '已支付', color: '#2563eb' },
  ready: { label: '待自提', color: '#0d9f6e' },
  completed: { label: '已完成', color: '#6b7280' },
  cancelled: { label: '已取消', color: '#ef4444' },
}

async function load() {
  loading.value = true
  try {
    const [o, p] = await Promise.all([
      api.get('/api/admin/orders'),
      api.get('/api/admin/products'),
    ])
    orders.value = o.data
    products.value = p.data
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  } finally {
    loading.value = false
  }
}

function yuan(cents) {
  return (cents / 100).toFixed(2)
}

const stats = computed(() => {
  const list = orders.value
  const paidLike = list.filter((r) => ['paid', 'ready', 'completed'].includes(r.status))
  return {
    orders: list.length,
    pending: list.filter((r) => r.status === 'paid').length,
    pickup: list.filter((r) => r.status === 'ready').length,
    revenue: paidLike.reduce((n, r) => n + r.total_cents, 0),
    products: products.value.length,
    onSale: products.value.filter((p) => p.on_sale).length,
    lowStock: products.value.filter((p) => p.stock < 10).length,
  }
})

const statusBars = computed(() => {
  const total = Math.max(orders.value.length, 1)
  return Object.keys(statusMeta).map((key) => {
    const count = orders.value.filter((o) => o.status === key).length
    return {
      key,
      ...statusMeta[key],
      count,
      pct: Math.round((count / total) * 100),
    }
  })
})

const recent = computed(() => orders.value.slice(0, 6))

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <div class="page-head">
      <div>
        <h2>运营看板</h2>
        <p>一眼看完今日订单与库存情况</p>
      </div>
      <div class="actions">
        <el-button @click="load">刷新数据</el-button>
        <el-button type="primary" @click="router.push('/orders')">去处理订单</el-button>
      </div>
    </div>

    <div class="stats">
      <div class="stat gray">
        <div class="label">订单总数</div>
        <div class="value">{{ stats.orders }}</div>
      </div>
      <div class="stat blue">
        <div class="label">待备货</div>
        <div class="value">{{ stats.pending }}</div>
      </div>
      <div class="stat green">
        <div class="label">待自提</div>
        <div class="value">{{ stats.pickup }}</div>
      </div>
      <div class="stat orange">
        <div class="label">已收金额</div>
        <div class="value" style="font-size: 24px">¥{{ yuan(stats.revenue) }}</div>
      </div>
    </div>

    <div class="grid">
      <section class="panel block">
        <div class="block-head">
          <h3>订单状态分布</h3>
          <span class="muted">共 {{ stats.orders }} 单</span>
        </div>
        <div class="bars">
          <div v-for="b in statusBars" :key="b.key" class="bar-row">
            <div class="bar-label">
              <span>{{ b.label }}</span>
              <strong>{{ b.count }}</strong>
            </div>
            <div class="track">
              <div class="fill" :style="{ width: b.pct + '%', background: b.color }" />
            </div>
          </div>
        </div>
      </section>

      <section class="panel block">
        <div class="block-head">
          <h3>商品概览</h3>
          <el-button text type="primary" @click="router.push('/products')">管理商品</el-button>
        </div>
        <div class="kpi-list">
          <div class="kpi">
            <span>在售商品</span>
            <strong>{{ stats.onSale }} / {{ stats.products }}</strong>
          </div>
          <div class="kpi warn">
            <span>低库存（&lt;10）</span>
            <strong>{{ stats.lowStock }}</strong>
          </div>
        </div>
        <div class="product-mini">
          <div v-for="p in products.slice(0, 4)" :key="p.id" class="p-row">
            <div>
              <div class="p-name">{{ p.name }}</div>
              <div class="muted">库存 {{ p.stock }} · {{ p.on_sale ? '在售' : '下架' }}</div>
            </div>
            <div class="money">¥{{ yuan(p.price_cents) }}</div>
          </div>
        </div>
      </section>
    </div>

    <section class="panel block" style="margin-top: 16px">
      <div class="block-head">
        <h3>最近订单</h3>
        <el-button text type="primary" @click="router.push('/orders')">查看全部</el-button>
      </div>
      <el-table :data="recent" empty-text="暂无订单" stripe>
        <el-table-column label="订单" width="90">
          <template #default="{ row }">#{{ row.id }}</template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag round effect="light">{{ statusMeta[row.status]?.label || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="买家">
          <template #default="{ row }">{{ row.buyer_name }} / {{ row.buyer_phone }}</template>
        </el-table-column>
        <el-table-column label="金额" width="110">
          <template #default="{ row }">
            <span class="money">¥{{ yuan(row.total_cents) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="自提点">
          <template #default="{ row }">{{ row.pickup_point?.name }}</template>
        </el-table-column>
      </el-table>
    </section>
  </div>
</template>

<style scoped>
.actions { display: flex; gap: 8px; }

.grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 16px;
}

.block { padding: 18px; }

.block-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.block-head h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
}

.muted { color: var(--muted); font-size: 12px; }

.bars { display: flex; flex-direction: column; gap: 12px; }

.bar-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 6px;
}

.track {
  height: 10px;
  border-radius: 999px;
  background: #eef2f7;
  overflow: hidden;
}

.fill {
  height: 100%;
  border-radius: 999px;
  min-width: 0;
  transition: width 0.35s ease;
}

.kpi-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 14px;
}

.kpi {
  background: var(--brand-soft);
  border-radius: 12px;
  padding: 12px;
}

.kpi span { display: block; font-size: 12px; color: var(--muted); }
.kpi strong { display: block; margin-top: 6px; font-size: 22px; font-weight: 800; color: var(--brand-dark); }
.kpi.warn { background: #fff7ed; }
.kpi.warn strong { color: #ea580c; }

.product-mini { display: flex; flex-direction: column; gap: 10px; }
.p-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-top: 1px dashed var(--line);
}
.p-name { font-weight: 700; font-size: 14px; }
.money { color: #ea580c; font-weight: 800; }

@media (max-width: 960px) {
  .grid { grid-template-columns: 1fr; }
}
</style>
