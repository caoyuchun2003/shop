<script setup>
import { inject, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { productEmoji, productGradient } from '../lib/productArt'

const router = useRouter()
const refreshCart = inject('refreshCart', () => {})
const cart = ref({ items: [], total_cents: 0 })
const loading = ref(true)
const busyId = ref(null)

function yuan(c) {
  return (c / 100).toFixed(2)
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/cart')
    cart.value = data
    await refreshCart()
  } finally {
    loading.value = false
  }
}

async function setQty(it, qty) {
  busyId.value = it.id
  try {
    await api.patch(`/api/cart/items/${it.id}`, { qty })
    await load()
  } catch (e) {
    alert(e.response?.data?.detail || e.message)
  } finally {
    busyId.value = null
  }
}

async function remove(it) {
  busyId.value = it.id
  try {
    await api.delete(`/api/cart/items/${it.id}`)
    await load()
  } catch (e) {
    alert(e.response?.data?.detail || e.message)
  } finally {
    busyId.value = null
  }
}

onMounted(load)
</script>

<template>
  <div class="cart-page fade-in">
    <h2 class="page-title">购物车</h2>
    <p class="page-sub">可改数量、删除后再去结算</p>

    <div v-if="loading" class="card">
      <div class="skeleton" style="height: 72px; margin-bottom: 10px" />
      <div class="skeleton" style="height: 72px" />
    </div>

    <div v-else-if="!cart.items.length" class="card empty">
      <div class="empty-art">🛒</div>
      <h3>购物车还是空的</h3>
      <p>去首页挑点邻居都在买的生鲜吧</p>
      <button class="ghost" @click="router.push('/')">去逛逛</button>
    </div>

    <template v-else>
      <div class="list">
        <article v-for="it in cart.items" :key="it.id" class="card item">
          <div
            class="thumb"
            :style="it.cover_url ? {} : { background: productGradient(it.product_id) }"
          >
            <img v-if="it.cover_url" :src="it.cover_url" :alt="it.name" />
            <span v-else>{{ productEmoji(it.name) }}</span>
          </div>
          <div class="info">
            <div class="name">{{ it.name }}</div>
            <div class="muted">单价 ¥{{ yuan(it.price_cents) }}</div>
            <div class="ops">
              <button class="qty-btn" :disabled="busyId === it.id" @click="setQty(it, it.qty - 1)">−</button>
              <span class="qty-num">{{ it.qty }}</span>
              <button class="qty-btn" :disabled="busyId === it.id" @click="setQty(it, it.qty + 1)">+</button>
              <button class="rm" :disabled="busyId === it.id" @click="remove(it)">删除</button>
            </div>
          </div>
          <div class="line-price">¥{{ yuan(it.line_cents) }}</div>
        </article>
      </div>

      <div class="summary card">
        <div class="row"><span>商品件数</span><span>{{ cart.items.reduce((n, i) => n + i.qty, 0) }} 件</span></div>
        <div class="row total"><span>合计</span><span class="price"><small>¥</small>{{ yuan(cart.total_cents) }}</span></div>
        <button @click="router.push('/checkout')">去结算</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.cart-page { padding-top: 6px; }

.empty {
  text-align: center;
  padding: 36px 20px;
}

.empty-art { font-size: 48px; margin-bottom: 8px; }
.empty h3 { margin: 0 0 6px; font-size: 17px; }
.empty p { margin: 0 0 16px; color: var(--muted); font-size: 13px; }

.list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; }

.item {
  display: grid;
  grid-template-columns: 56px 1fr auto;
  gap: 12px;
  align-items: center;
}

.thumb {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 26px;
  overflow: hidden;
  background: #f3f4f6;
}

.thumb img { width: 100%; height: 100%; object-fit: cover; }

.name { font-weight: 700; font-size: 15px; margin-bottom: 4px; }

.ops {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.qty-btn {
  width: 28px;
  height: 28px;
  padding: 0;
  border-radius: 8px;
  background: var(--brand-soft);
  color: var(--brand-dark);
  box-shadow: none;
  font-size: 16px;
  font-weight: 800;
}

.qty-num { min-width: 18px; text-align: center; font-weight: 800; }

.rm {
  margin-left: 4px;
  padding: 4px 8px;
  font-size: 12px;
  background: #fff;
  color: #dc2626;
  border: 1px solid #fecaca;
  box-shadow: none;
}

.line-price { font-weight: 800; color: var(--accent); font-size: 16px; }

.summary .row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 14px;
  color: #4b5563;
}

.summary .total {
  margin: 4px 0 12px;
  padding-top: 10px;
  border-top: 1px dashed var(--line);
  font-weight: 700;
  color: var(--text);
}

.summary button { width: 100%; }
</style>
