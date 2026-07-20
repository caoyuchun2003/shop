<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const products = ref([])
const toast = ref('')

function yuan(c) {
  return (c / 100).toFixed(2)
}

function tip(msg) {
  toast.value = msg
  setTimeout(() => { toast.value = '' }, 2000)
}

async function load() {
  const { data } = await api.get('/api/products')
  products.value = data
}

async function add(p) {
  await api.post('/api/cart/items', { product_id: p.id, qty: 1 })
  tip(`已加入：${p.name}`)
}

onMounted(load)
</script>

<template>
  <div>
    <div v-for="p in products" :key="p.id" class="card item">
      <div class="info">
        <div class="name">{{ p.name }}</div>
        <div class="muted">{{ p.desc }}</div>
        <div class="row">
          <span class="price">¥{{ yuan(p.price_cents) }}</span>
          <span class="muted">库存 {{ p.stock }}</span>
        </div>
      </div>
      <button @click="add(p)">加购</button>
    </div>
    <button class="secondary go" @click="router.push('/cart')">去购物车</button>
    <div v-if="toast" class="toast">{{ toast }}</div>
  </div>
</template>

<style scoped>
.item { display: flex; gap: 12px; align-items: center; justify-content: space-between; }
.info { flex: 1; min-width: 0; }
.name { font-weight: 600; margin-bottom: 4px; }
.row { display: flex; gap: 12px; align-items: baseline; margin-top: 8px; }
.go { width: 100%; margin-top: 8px; }
.toast {
  position: fixed; left: 50%; bottom: 88px; transform: translateX(-50%);
  background: #111; color: #fff; padding: 8px 14px; border-radius: 999px; font-size: 13px;
}
</style>
