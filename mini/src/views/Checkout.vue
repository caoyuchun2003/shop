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
  <div class="checkout fade-in">
    <h2 class="page-title">确认订单</h2>
    <p class="page-sub">填写自提信息，提交后可模拟支付</p>

    <div class="card steps">
      <div class="step done"><span>1</span> 选商品</div>
      <div class="step active"><span>2</span> 填信息</div>
      <div class="step"><span>3</span> 支付</div>
    </div>

    <div class="card form-card">
      <h3>自提信息</h3>
      <label class="field">
        <span>自提点</span>
        <select v-model.number="form.pickup_point_id">
          <option v-for="p in points" :key="p.id" :value="p.id">{{ p.name }} — {{ p.address }}</option>
        </select>
      </label>
      <label class="field">
        <span>联系人</span>
        <input v-model="form.buyer_name" placeholder="怎么称呼您" />
      </label>
      <label class="field">
        <span>手机号</span>
        <input v-model="form.buyer_phone" type="tel" placeholder="用于取货通知" />
      </label>
      <p v-if="err" class="err">{{ err }}</p>
      <button :disabled="busy" @click="submit">{{ busy ? '提交中…' : '提交订单' }}</button>
    </div>
  </div>
</template>

<style scoped>
.checkout { padding-top: 6px; }

.steps {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;
  padding: 12px;
}

.step {
  text-align: center;
  font-size: 12px;
  color: var(--muted);
  font-weight: 600;
}

.step span {
  display: inline-grid;
  place-items: center;
  width: 22px;
  height: 22px;
  border-radius: 999px;
  background: #eef2f7;
  color: #6b7280;
  font-size: 11px;
  margin-right: 4px;
}

.step.done { color: var(--brand-dark); }
.step.done span { background: var(--brand-soft); color: var(--brand-dark); }
.step.active { color: var(--text); font-weight: 800; }
.step.active span { background: var(--brand); color: #fff; }

.form-card h3 { margin: 0 0 12px; font-size: 16px; }
.err { color: #dc2626; font-size: 13px; margin: 0 0 10px; }
button { width: 100%; }
</style>
