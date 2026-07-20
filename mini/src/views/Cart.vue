<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { productEmoji, productGradient } from '../lib/productArt'

const router = useRouter()
const cart = ref({ items: [], total_cents: 0 })
const loading = ref(true)

function yuan(c) {
  return (c / 100).toFixed(2)
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/cart')
    cart.value = data
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="cart-page fade-in">
    <h2 class="page-title">购物车</h2>
    <p class="page-sub">确认商品后填写自提信息并下单</p>

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
          <div class="thumb" :style="{ background: productGradient(it.product_id) }">
            {{ productEmoji(it.name) }}
          </div>
          <div class="info">
            <div class="name">{{ it.name }}</div>
            <div class="muted">单价 ¥{{ yuan(it.price_cents) }}</div>
            <div class="qty">× {{ it.qty }}</div>
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
}

.name { font-weight: 700; font-size: 15px; margin-bottom: 4px; }
.qty { margin-top: 6px; font-size: 13px; color: var(--brand-dark); font-weight: 700; }
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
