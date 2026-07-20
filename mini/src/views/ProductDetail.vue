<script setup>
import { inject, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { productEmoji, productGradient } from '../lib/productArt'

const props = defineProps({ id: { type: [String, Number], required: true } })
const router = useRouter()
const refreshCart = inject('refreshCart', () => {})

const product = ref(null)
const loading = ref(true)
const err = ref('')
const qty = ref(1)
const busy = ref(false)
const toast = ref('')

function yuan(c) {
  return (c / 100).toFixed(2)
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    const { data } = await api.get(`/api/products/${props.id}`)
    product.value = data
    qty.value = 1
  } catch (e) {
    err.value = e.response?.data?.detail || '商品不存在或已下架'
  } finally {
    loading.value = false
  }
}

async function add() {
  if (!product.value) return
  busy.value = true
  try {
    await api.post('/api/cart/items', { product_id: product.value.id, qty: qty.value })
    await refreshCart()
    toast.value = '已加入购物车'
    setTimeout(() => { toast.value = '' }, 2000)
  } catch (e) {
    toast.value = e.response?.data?.detail || '加购失败'
    setTimeout(() => { toast.value = '' }, 2200)
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="detail fade-in">
    <button class="back ghost" @click="router.back()">← 返回</button>

    <div v-if="loading" class="card">
      <div class="skeleton" style="height: 220px; margin-bottom: 12px" />
      <div class="skeleton" style="height: 16px; width: 60%" />
    </div>

    <div v-else-if="err" class="card empty">
      <p>{{ err }}</p>
      <button class="ghost" @click="router.push('/')">回首页</button>
    </div>

    <template v-else-if="product">
      <div
        class="hero-cover card"
        :style="product.cover_url ? {} : { background: productGradient(product.id) }"
      >
        <img v-if="product.cover_url" :src="product.cover_url" :alt="product.name" />
        <span v-else class="emoji">{{ productEmoji(product.name) }}</span>
      </div>

      <div class="card body">
        <h2>{{ product.name }}</h2>
        <p class="desc">{{ product.desc || '新鲜直达，社区自提。' }}</p>
        <div class="meta">
          <span class="price"><small>¥</small>{{ yuan(product.price_cents) }}</span>
          <span class="muted">库存 {{ product.stock }}</span>
        </div>

        <div class="qty-row">
          <span>数量</span>
          <div class="ops">
            <button class="qty-btn" @click="qty = Math.max(1, qty - 1)">−</button>
            <strong>{{ qty }}</strong>
            <button class="qty-btn" @click="qty = Math.min(99, qty + 1)">+</button>
          </div>
        </div>

        <div class="btns">
          <button class="ghost" @click="router.push('/cart')">去购物车</button>
          <button :disabled="busy || product.stock < 1" @click="add">
            {{ product.stock < 1 ? '售罄' : (busy ? '加入中…' : '加入购物车') }}
          </button>
        </div>
      </div>
    </template>

    <div v-if="toast" class="toast">{{ toast }}</div>
  </div>
</template>

<style scoped>
.detail { padding-top: 4px; }
.back { margin-bottom: 10px; padding: 8px 12px; font-size: 13px; }

.hero-cover {
  height: 220px;
  padding: 0;
  overflow: hidden;
  display: grid;
  place-items: center;
  margin-bottom: 10px;
}
.hero-cover img { width: 100%; height: 100%; object-fit: cover; }
.emoji { font-size: 72px; }

.body h2 { margin: 0 0 8px; font-size: 20px; }
.desc { margin: 0 0 14px; color: var(--muted); font-size: 14px; line-height: 1.5; }
.meta { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 16px; }

.qty-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 700;
}
.ops { display: flex; align-items: center; gap: 12px; }
.qty-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 10px;
  background: var(--brand-soft);
  color: var(--brand-dark);
  box-shadow: none;
  font-size: 18px;
  font-weight: 800;
}

.btns { display: grid; grid-template-columns: 1fr 1.4fr; gap: 10px; }

.empty { text-align: center; padding: 28px 16px; }

.toast {
  position: fixed;
  left: 50%;
  bottom: calc(92px + var(--safe-bottom));
  transform: translateX(-50%);
  background: rgba(17, 24, 39, 0.92);
  color: #fff;
  padding: 10px 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  z-index: 40;
}
</style>
