<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const rows = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const saving = ref(false)

const form = reactive({ name: '', address: '' })

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/admin/pickup-points')
    rows.value = data
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.name = ''
  form.address = ''
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  form.name = row.name
  form.address = row.address
  dialogVisible.value = true
}

async function save() {
  if (!form.name.trim() || !form.address.trim()) {
    ElMessage.warning('请填写名称和地址')
    return
  }
  saving.value = true
  try {
    const body = { name: form.name.trim(), address: form.address.trim() }
    if (editingId.value) {
      await api.patch(`/api/admin/pickup-points/${editingId.value}`, body)
      ElMessage.success('已更新')
    } else {
      await api.post('/api/admin/pickup-points', body)
      ElMessage.success('已添加')
    }
    dialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message)
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(`删除自提点「${row.name}」？`, '确认删除', { type: 'warning' })
    await api.delete(`/api/admin/pickup-points/${row.id}`)
    ElMessage.success('已删除')
    await load()
  } catch (e) {
    if (e === 'cancel' || e === 'close') return
    ElMessage.error(e.response?.data?.detail || e.message)
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h2>自提点</h2>
        <p>配置用户下单时可选择的取货地点</p>
      </div>
      <div class="actions">
        <el-button @click="load">刷新</el-button>
        <el-button type="primary" @click="openCreate">添加自提点</el-button>
      </div>
    </div>

    <div class="panel">
      <div class="panel-body">
        <el-table :data="rows" v-loading="loading" stripe empty-text="暂无自提点">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="name" label="名称" min-width="160" />
          <el-table-column prop="address" label="地址" min-width="240" />
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="openEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="remove(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑自提点' : '添加自提点'"
      width="460px"
      destroy-on-close
    >
      <el-form label-position="top">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="例如：阳光花园东门驿站" />
        </el-form-item>
        <el-form-item label="地址" required>
          <el-input v-model="form.address" type="textarea" :rows="2" placeholder="详细地址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.actions { display: flex; gap: 8px; }
</style>
