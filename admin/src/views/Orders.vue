<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const rows = ref([])
const loading = ref(false)
const filter = ref('all')

const statusMeta = {
  pending_pay: { label: '待支付', type: 'warning' },
  paid: { label: '已支付', type: 'primary' },
  ready: { label: '待自提', type: 'success' },
  completed: { label: '已完成', type: 'info' },
  cancelled: { label: '已取消', type: 'danger' },
}

const filters = [
  { key: 'all', label: '全部' },
  { key: 'paid', label: '待备货' },
  { key: 'ready', label: '待自提' },
  { key: 'completed', label: '已完成' },
  { key: 'pending_pay', label: '待支付' },
]

const filtered = computed(() => {
  if (filter.value === 'all') return rows.value
  return rows.value.filter((r) => r.status === filter.value)
})

const stats = computed(() => {
  const list = rows.value
  return {
    total: list.length,
    paid: list.filter((r) => r.status === 'paid').length,
    ready: list.filter((r) => r.status === 'ready').length,
    amount: list
      .filter((r) => ['paid', 'ready', 'completed'].includes(r.status))
      .reduce((n, r) => n + r.total_cents, 0),
  }
})

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/admin/orders')
    rows.value = data
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  } finally {
    loading.value = false
  }
}

async function setStatus(row, status) {
  try {
    await api.post(`/api/admin/orders/${row.id}/status`, { status })
    ElMessage.success(status === 'ready' ? '已标为待自提' : '核销完成')
    await load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  }
}

function yuan(cents) {
  return (cents / 100).toFixed(2)
}

function timeText(iso) {
  if (!iso) return '-'
  try {
    return new Date(iso).toLocaleString('zh-CN', { hour12: false })
  } catch {
    return iso
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h2>订单管理</h2>
        <p>处理支付后的备货、自提与核销</p>
      </div>
      <el-button type="primary" @click="load">刷新订单</el-button>
    </div>

    <div class="stats">
      <div class="stat gray">
        <div class="label">全部订单</div>
        <div class="value">{{ stats.total }}</div>
      </div>
      <div class="stat blue">
        <div class="label">待备货</div>
        <div class="value">{{ stats.paid }}</div>
      </div>
      <div class="stat green">
        <div class="label">待自提</div>
        <div class="value">{{ stats.ready }}</div>
      </div>
      <div class="stat orange">
        <div class="label">已收金额</div>
        <div class="value" style="font-size: 24px">¥{{ yuan(stats.amount) }}</div>
      </div>
    </div>

    <div class="filters">
      <button
        v-for="f in filters"
        :key="f.key"
        class="filter-chip"
        :class="{ active: filter === f.key }"
        @click="filter = f.key"
      >
        {{ f.label }}
      </button>
    </div>

    <div class="panel">
      <div class="panel-body">
        <el-table :data="filtered" v-loading="loading" stripe empty-text="暂无订单">
          <el-table-column label="订单" width="92">
            <template #default="{ row }">
              <div class="oid">#{{ row.id }}</div>
              <div class="muted">{{ timeText(row.created_at) }}</div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <el-tag :type="statusMeta[row.status]?.type || 'info'" effect="light" round>
                {{ statusMeta[row.status]?.label || row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="金额" width="100">
            <template #default="{ row }">
              <span class="money">¥{{ yuan(row.total_cents) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="买家" min-width="140">
            <template #default="{ row }">
              <div class="buyer">{{ row.buyer_name }}</div>
              <div class="muted">{{ row.buyer_phone }}</div>
            </template>
          </el-table-column>
          <el-table-column label="自提点" min-width="160">
            <template #default="{ row }">
              <div>{{ row.pickup_point?.name || '-' }}</div>
              <div class="muted">{{ row.pickup_point?.address }}</div>
            </template>
          </el-table-column>
          <el-table-column label="商品" min-width="180">
            <template #default="{ row }">
              <div v-for="it in row.items" :key="it.product_id" class="item-line">
                {{ it.product_name }} × {{ it.qty }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="row.status === 'paid'"
                size="small"
                type="primary"
                @click="setStatus(row, 'ready')"
              >
                标为待自提
              </el-button>
              <el-button
                v-else-if="row.status === 'ready'"
                size="small"
                type="success"
                @click="setStatus(row, 'completed')"
              >
                核销完成
              </el-button>
              <span v-else class="muted">—</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.oid { font-weight: 800; }
.muted { color: var(--muted); font-size: 12px; margin-top: 4px; line-height: 1.35; }
.money { color: #ea580c; font-weight: 800; font-size: 15px; }
.buyer { font-weight: 700; }
.item-line { font-size: 13px; line-height: 1.5; }
</style>
