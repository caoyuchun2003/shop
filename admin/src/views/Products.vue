<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const rows = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/admin/products')
    rows.value = data
  } finally {
    loading.value = false
  }
}

async function save(row) {
  await api.patch(`/api/admin/products/${row.id}`, {
    name: row.name,
    price_cents: row.price_cents,
    stock: row.stock,
    on_sale: row.on_sale,
  })
  ElMessage.success('已保存')
}

function yuan(cents) {
  return (cents / 100).toFixed(2)
}

onMounted(load)
</script>

<template>
  <div>
    <div class="bar">
      <h2>商品</h2>
      <el-button @click="load">刷新</el-button>
    </div>
    <el-table :data="rows" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="名称">
        <template #default="{ row }">
          <el-input v-model="row.name" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="价格(分)" width="140">
        <template #default="{ row }">
          <el-input-number v-model="row.price_cents" :min="1" size="small" />
          <div class="hint">≈ ¥{{ yuan(row.price_cents) }}</div>
        </template>
      </el-table-column>
      <el-table-column label="库存" width="140">
        <template #default="{ row }">
          <el-input-number v-model="row.stock" :min="0" size="small" />
        </template>
      </el-table-column>
      <el-table-column label="上架" width="90">
        <template #default="{ row }">
          <el-switch v-model="row.on_sale" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="save(row)">保存</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
h2 { margin: 0; font-size: 18px; }
.hint { font-size: 12px; color: #888; margin-top: 4px; }
</style>
