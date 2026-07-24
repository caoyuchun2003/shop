<script setup>
import { inject, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { productEmoji, productGradient } from '../lib/productArt'

const router = useRouter()
const refreshCart = inject('refreshCart', () => {})
const products = ref([])
const loading = ref(true)
const error = ref('')
const toast = ref('')
const activeCat = ref('全部')
const brokenCovers = ref(new Set())

function showCover(p) {
  return Boolean(p.cover_url) && !brokenCovers.value.has(p.id)
}

function markBrokenCover(p) {
  brokenCovers.value = new Set(brokenCovers.value).add(p.id)
}

const categories = ['全部', '生鲜', '蛋奶', '饮品']

const CAT_MAP = {
  红颜草莓: '生鲜',
  土鸡蛋: '蛋奶',
  现磨豆浆: '饮品',
}

function yuan(c) {
  return (c / 100).toFixed(2)
}

function categoryOf(name) {
  for (const [key, cat] of Object.entries(CAT_MAP)) {
    if (name.includes(key)) return cat
  }
  return '生鲜'
}

const filtered = () => {
  if (activeCat.value === '全部') return products.value
  return products.value.filter((p) => categoryOf(p.name) === activeCat.value)
}

function tip(msg) {
  toast.value = msg
  setTimeout(() => { toast.value = '' }, 2200)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/api/products')
    products.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || '商品加载失败，请检查网络后重试'
  } finally {
    loading.value = false
  }
}

async function add(p) {
  try {
    await api.post('/api/cart/items', { product_id: p.id, qty: 1 })
    await refreshCart()
    tip(`已加入购物车`)
  } catch (e) {
    tip(e.response?.data?.detail || '加购失败')
  }
}

onMounted(load)
</script>

<template>
  <div class="home fade-in">
    <section class="promo card">
      <div class="promo-text">
        <div class="promo-tag">今日特惠</div>
        <div class="promo-title">邻居拼团 · 新鲜直达</div>
        <div class="promo-sub">满 3 件享模拟支付演示价</div>
      </div>
      <div class="promo-art">🧺</div>
    </section>

    <div class="cats">
      <button
        v-for="c in categories"
        :key="c"
        class="cat"
        :class="{ active: activeCat === c }"
        @click="activeCat = c"
      >
        {{ c }}
      </button>
    </div>

    <div v-if="loading" class="grid">
      <div v-for="n in 4" :key="n" class="card sk-card">
        <div class="skeleton sk-img" />
        <div class="skeleton sk-line" />
        <div class="skeleton sk-line short" />
      </div>
    </div>

    <div v-else-if="error" class="card empty">
      <div class="empty-icon">⚠️</div>
      <p>{{ error }}</p>
      <button class="ghost" @click="load">重新加载</button>
    </div>

    <div v-else-if="!filtered().length" class="card empty">
      <div class="empty-icon">🛍️</div>
      <p>该分类暂无商品</p>
    </div>

    <div v-else class="grid">
      <article
        v-for="p in filtered()"
        :key="p.id"
        class="product card"
        @click="router.push(`/products/${p.id}`)"
      >
        <div
          class="cover"
          :style="showCover(p) ? {} : { background: productGradient(p.id) }"
        >
          <img
            v-if="showCover(p)"
            class="cover-img"
            :src="p.cover_url"
            :alt="p.name"
            loading="lazy"
            @error="markBrokenCover(p)"
          />
          <span v-else class="emoji">{{ productEmoji(p.name) }}</span>
          <span v-if="p.stock < 10" class="stock-tag">仅剩 {{ p.stock }}</span>
        </div>
        <div class="body">
          <h3 class="name">{{ p.name }}</h3>
          <p class="desc">{{ p.desc }}</p>
          <div class="foot">
            <div class="price"><small>¥</small>{{ yuan(p.price_cents) }}</div>
            <button class="add" :disabled="p.stock < 1" @click.stop="add(p)">
              {{ p.stock < 1 ? '售罄' : '+' }}
            </button>
          </div>
        </div>
      </article>
    </div>

    <transition name="toast">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </transition>
  </div>
</template>

<style scoped>
.home { padding-top: 4px; }

.promo {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #fff 0%, #f0fdf8 100%);
  border: 1px solid #d1fae5;
}

.promo-tag {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  color: var(--brand-dark);
  background: var(--brand-soft);
  padding: 3px 8px;
  border-radius: 999px;
  margin-bottom: 6px;
}

.promo-title { font-size: 16px; font-weight: 800; }
.promo-sub { font-size: 12px; color: var(--muted); margin-top: 4px; }
.promo-art { font-size: 42px; filter: drop-shadow(0 6px 10px rgba(0,0,0,.08)); }

.cats {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 2px 2px 12px;
  scrollbar-width: none;
}

.cats::-webkit-scrollbar { display: none; }

.cat {
  flex: 0 0 auto;
  padding: 8px 14px;
  border-radius: 999px;
  background: #fff;
  color: #6b7280;
  border: 1px solid var(--line);
  box-shadow: none;
  font-size: 13px;
  font-weight: 600;
}

.cat.active {
  background: var(--brand);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 6px 14px rgba(13, 159, 110, 0.25);
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.product {
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
}

.cover {
  position: relative;
  height: 108px;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: #f3f4f6;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.emoji { font-size: 44px; filter: drop-shadow(0 8px 12px rgba(0,0,0,.12)); }

.stock-tag {
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  background: rgba(17, 24, 39, 0.55);
  padding: 3px 7px;
  border-radius: 999px;
}

.body { padding: 10px 10px 12px; display: flex; flex-direction: column; flex: 1; }

.name {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.desc {
  margin: 4px 0 10px;
  font-size: 11px;
  color: var(--muted);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.add {
  width: 34px;
  height: 34px;
  padding: 0;
  border-radius: 12px;
  font-size: 20px;
  line-height: 1;
  display: grid;
  place-items: center;
}

.sk-card { padding: 10px; }
.sk-img { height: 100px; margin-bottom: 10px; }
.sk-line { height: 12px; margin-bottom: 8px; }
.sk-line.short { width: 60%; }

.empty {
  text-align: center;
  padding: 28px 16px;
  margin-top: 8px;
}

.empty-icon { font-size: 36px; margin-bottom: 8px; }
.empty p { color: var(--muted); margin: 0 0 14px; font-size: 14px; }

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
  white-space: nowrap;
}

.toast-enter-active, .toast-leave-active { transition: opacity 0.2s, transform 0.2s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translate(-50%, 8px); }
</style>
