<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const cart = ref({ items: [], total_cents: 0 })

function yuan(c) {
  return (c / 100).toFixed(2)
}

async function load() {
  const { data } = await api.get('/api/cart')
  cart.value = data
}

onMounted(load)
</script>

<template>
  <div>
    <div v-if="!cart.items.length" class="card muted">购物车是空的</div>
    <div v-for="it in cart.items" :key="it.id" class="card line">
      <div>
        <div class="name">{{ it.name }}</div>
        <div class="muted">¥{{ yuan(it.price_cents) }} × {{ it.qty }}</div>
      </div>
      <div class="price">¥{{ yuan(it.line_cents) }}</div>
    </div>
    <div v-if="cart.items.length" class="footer">
      <div>合计 <span class="price">¥{{ yuan(cart.total_cents) }}</span></div>
      <button @click="router.push('/checkout')">去结算</button>
    </div>
  </div>
</template>

<style scoped>
.line { display: flex; justify-content: space-between; align-items: center; }
.name { font-weight: 600; }
.footer {
  position: sticky; bottom: 64px;
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 12px 14px; border-radius: 14px; margin-top: 12px;
}
</style>
