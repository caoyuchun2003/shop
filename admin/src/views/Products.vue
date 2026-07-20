<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const rows = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const creating = ref(false)

const form = reactive({
  name: '',
  desc: '',
  price_yuan: 9.9,
  stock: 50,
  on_sale: true,
})

const stats = computed(() => ({
  total: rows.value.length,
  onSale: rows.value.filter((r) => r.on_sale).length,
  low: rows.value.filter((r) => r.stock < 10).length,
}))

function resetForm() {
  form.name = ''
  form.desc = ''
  form.price_yuan = 9.9
  form.stock = 50
  form.on_sale = true
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

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
    const { data } = await api.patch(`/api/admin/products/${row.id}`, {
      name: row.name.trim(),
      desc: row.desc || '',
      price_cents: cents,
      stock: row.stock,
      on_sale: !!row.on_sale,
    })
    Object.assign(row, data, { price_yuan: Number((data.price_cents / 100).toFixed(2)) })
    ElMessage.success('已保存')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  }
}

async function createProduct() {
  const cents = Math.round(Number(form.price_yuan) * 100)
  if (!form.name.trim()) {
    ElMessage.warning('请填写商品名称')
    return
  }
  if (!(cents > 0)) {
    ElMessage.warning('价格需大于 0')
    return
  }
  creating.value = true
  try {
    await api.post('/api/admin/products', {
      name: form.name.trim(),
      desc: form.desc.trim(),
      price_cents: cents,
      stock: form.stock,
      on_sale: !!form.on_sale,
    })
    ElMessage.success('商品已添加')
    dialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  } finally {
    creating.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h2>商品管理</h2>
        <p>添加商品，调整价格、库存与上下架</p>
      </div>
      <div class="actions">
        <el-button @click="load">刷新</el-button>
        <el-button type="primary" @click="openCreate">添加商品</el-button>
      </div>
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
        <el-table :data="rows" v-loading="loading" stripe empty-text="暂无商品，点击右上角添加">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column label="商品" min-width="240">
            <template #default="{ row }">
              <el-input v-model="row.name" size="default" placeholder="商品名称" />
              <el-input
                v-model="row.desc"
                class="desc-input"
                type="textarea"
                :rows="2"
                placeholder="商品简介"
              />
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

    <el-dialog v-model="dialogVisible" title="添加商品" width="480px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="商品名称" required>
          <el-input v-model="form.name" placeholder="例如：红颜草莓 1 斤" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="form.desc" type="textarea" :rows="3" placeholder="一两句卖点描述" />
        </el-form-item>
        <div class="form-row">
          <el-form-item label="售价（元）" required>
            <el-input-number
              v-model="form.price_yuan"
              :min="0.01"
              :step="0.1"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="库存" required>
            <el-input-number v-model="form.stock" :min="0" controls-position="right" />
          </el-form-item>
        </div>
        <el-form-item label="上架销售">
          <el-switch v-model="form.on_sale" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="createProduct">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.actions { display: flex; gap: 8px; }
.desc-input { margin-top: 8px; }
.warn {
  margin-top: 4px;
  color: #ea580c;
  font-size: 12px;
  font-weight: 700;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
</style>
