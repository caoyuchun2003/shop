<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const rows = ref([])
const loading = ref(false)

const statusMap = {
  pending_pay: '待支付',
  paid: '已支付',
  ready: '待自提',
  completed: '已完成',
  cancelled: '已取消',
}

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
  await api.post(`/api/admin/orders/${row.id}/status`, { status })
  ElMessage.success('已更新')
  load()
}

function yuan(cents) {
  return (cents / 100).toFixed(2)
}

onMounted(load)
</script>

<template>
  <div>
    <div class="bar">
      <h2>订单</h2>
      <el-button @click="load">刷新</el-button>
    </div>
    <el-table :data="rows" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">{{ statusMap[row.status] || row.status }}</template>
      </el-table-column>
      <el-table-column label="金额" width="100">
        <template #default="{ row }">¥{{ yuan(row.total_cents) }}</template>
      </el-table-column>
      <el-table-column label="买家">
        <template #default="{ row }">{{ row.buyer_name }} / {{ row.buyer_phone }}</template>
      </el-table-column>
      <el-table-column label="自提点">
        <template #default="{ row }">{{ row.pickup_point?.name }}</template>
      </el-table-column>
      <el-table-column label="商品">
        <template #default="{ row }">
          <div v-for="it in row.items" :key="it.product_id">
            {{ it.product_name }} × {{ it.qty }}
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button v-if="row.status === 'paid'" size="small" type="primary" @click="setStatus(row, 'ready')">
            标为待自提
          </el-button>
          <el-button v-if="row.status === 'ready'" size="small" type="success" @click="setStatus(row, 'completed')">
            核销完成
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
h2 { margin: 0; font-size: 18px; }
</style>
