<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const points = ref([])
const form = ref({ pickup_point_id: null, buyer_name: '', buyer_phone: '' })
const busy = ref(false)
const err = ref('')

onMounted(async () => {
  const { data } = await api.get('/api/pickup-points')
  points.value = data
  if (data.length) form.value.pickup_point_id = data[0].id
})

async function submit() {
  err.value = ''
  if (!form.value.buyer_name.trim() || !form.value.buyer_phone.trim()) {
    err.value = '请填写姓名和手机号'
    return
  }
  busy.value = true
  try {
    const { data } = await api.post('/api/orders', form.value)
    router.replace(`/orders/${data.id}`)
  } catch (e) {
    err.value = e.response?.data?.detail || e.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="card">
    <h3>填写自提信息</h3>
    <label class="field">
      <span>自提点</span>
      <select v-model.number="form.pickup_point_id">
        <option v-for="p in points" :key="p.id" :value="p.id">{{ p.name }} — {{ p.address }}</option>
      </select>
    </label>
    <label class="field">
      <span>姓名</span>
      <input v-model="form.buyer_name" placeholder="怎么称呼" />
    </label>
    <label class="field">
      <span>手机</span>
      <input v-model="form.buyer_phone" placeholder="用于取货通知" />
    </label>
    <p v-if="err" class="err">{{ err }}</p>
    <button :disabled="busy" @click="submit">{{ busy ? '提交中…' : '提交订单' }}</button>
  </div>
</template>

<style scoped>
h3 { margin: 0 0 12px; }
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; font-size: 14px; }
input, select {
  font: inherit; padding: 10px 12px; border: 1px solid #e5e7eb; border-radius: 10px; background: #fff;
}
.err { color: #dc2626; font-size: 13px; }
button { width: 100%; }
</style>
