<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const rows = ref([])
const loading = ref(false)

const stats = computed(() => ({
  total: rows.value.length,
  onSale: rows.value.filter((r) => r.on_sale).length,
  low: rows.value.filter((r) => r.stock < 10).length,
}))

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/admin/products')
    rows.value = data.map((p) => ({
      ...p,
      price_yuan: Number((p.price_cents / 100).toFixed(2)),
    }))
  } finally {
    loading.value = false
  }
}

async function save(row) {
  const cents = Math.round(Number(row.price_yuan) * 100)
  if (!row.name?.trim()) {
    ElMessage.warning('请填写商品名称')
    return
  }
  if (!(cents > 0)) {
    ElMessage.warning('价格需大于 0')
    return
  }
  try {
    await api.patch(`/api/admin/products/${row.id}`, {
      name: row.name.trim(),
      price_cents: cents,
      stock: row.stock,
      on_sale: !!row.on_sale,
    })
    row.price_cents = cents
    ElMessage.success('已保存')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h2>商品管理</h2>
        <p>调整价格、库存与上下架状态</p>
      </div>
      <el-button type="primary" @click="load">刷新商品</el-button>
    </div>

    <div class="stats">
      <div class="stat gray">
        <div class="label">商品数</div>
        <div class="value">{{ stats.total }}</div>
      </div>
      <div class="stat green">
        <div class="label">在售</div>
        <div class="value">{{ stats.onSale }}</div>
      </div>
      <div class="stat orange">
        <div class="label">低库存</div>
        <div class="value">{{ stats.low }}</div>
      </div>
      <div class="stat blue">
        <div class="label">说明</div>
        <div class="value" style="font-size: 14px; line-height: 1.4; font-weight: 700; padding-top: 8px">
          价格按元编辑
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-body">
        <el-table :data="rows" v-loading="loading" stripe empty-text="暂无商品">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column label="商品" min-width="220">
            <template #default="{ row }">
              <el-input v-model="row.name" size="default" placeholder="商品名称" />
              <div class="desc">{{ row.desc }}</div>
            </template>
          </el-table-column>
          <el-table-column label="售价（元）" width="160">
            <template #default="{ row }">
              <el-input-number
                v-model="row.price_yuan"
                :min="0.01"
                :step="0.1"
                :precision="2"
                size="default"
                controls-position="right"
              />
            </template>
          </el-table-column>
          <el-table-column label="库存" width="150">
            <template #default="{ row }">
              <el-input-number v-model="row.stock" :min="0" size="default" controls-position="right" />
              <div v-if="row.stock < 10" class="warn">库存偏低</div>
            </template>
          </el-table-column>
          <el-table-column label="上架" width="100">
            <template #default="{ row }">
              <el-switch v-model="row.on_sale" inline-prompt active-text="售" inactive-text="下" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="110" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" @click="save(row)">保存</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.desc {
  margin-top: 6px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.4;
}
.warn {
  margin-top: 4px;
  color: #ea580c;
  font-size: 12px;
  font-weight: 700;
}
</style>
