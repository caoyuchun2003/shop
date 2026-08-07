<script setup>
import { computed, onMounted, provide, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from './api'

const route = useRoute()
const cartCount = ref(0)
const cartTotal = ref(0)

async function refreshCart() {
  try {
    const { data } = await api.get('/api/cart')
    cartCount.value = data.items?.reduce((n, it) => n + it.qty, 0) || 0
    cartTotal.value = data.total_cents || 0
  } catch {
    cartCount.value = 0
    cartTotal.value = 0
  }
}

provide('refreshCart', refreshCart)

onMounted(refreshCart)
watch(() => route.path, refreshCart)

const showFab = computed(() => route.path === '/' && cartCount.value > 0)

function yuan(c) {
  return (c / 100).toFixed(2)
}
</script>

<template>
  <div class="shell">
    <header class="hero">
      <div class="hero-bg" />
      <div class="hero-inner">
        <div class="brand-row">
          <div class="logo">邻</div>
          <div>
            <h1 class="title">邻里小店</h1>
            <p class="tagline">阳光花园 · 今日团</p>
          </div>
          <span class="badge">模拟演示</span>
        </div>
        <div class="notice">
          <span class="notice-icon">📍</span>
          <div class="notice-body">
            <div class="notice-title">社区自提 · 次日 17:00 前可取</div>
            <div class="notice-sub">下单模拟支付后，可到运营后台演示核销</div>
            <a
              class="notice-link"
              href="https://shop.yuchuntest.com/admin/"
              target="_blank"
              rel="noopener"
            >运营后台演示 →</a>
          </div>
        </div>
      </div>
    </header>

    <main class="main">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <router-link v-if="showFab" to="/cart" class="fab">
      <span class="fab-icon">🛒</span>
      <span class="fab-text">去结算</span>
      <span class="fab-price">¥{{ yuan(cartTotal) }}</span>
      <span v-if="cartCount" class="fab-badge">{{ cartCount }}</span>
    </router-link>

    <nav class="tabbar">
      <router-link to="/" class="tab-item">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9.5 12 3l9 6.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1V9.5Z" fill="currentColor"/></svg>
        <span>首页</span>
      </router-link>
      <router-link to="/cart" class="tab-item">
        <span class="tab-icon-wrap">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4h-2l-1 2h2l3.6 7.59-1.35 2.44A2 2 0 0 0 10 19h9v-2h-8.42a.25.25 0 0 1-.22-.37L11 14h6.28a2 2 0 0 0 1.92-1.45L21 6H7.42l-.7-2Zm-1 16a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm10 0a2 2 0 1 0 .001 3.999A2 2 0 0 0 16 20Z" fill="currentColor"/></svg>
          <em v-if="cartCount" class="tab-badge">{{ cartCount > 99 ? '99+' : cartCount }}</em>
        </span>
        <span>购物车</span>
      </router-link>
      <router-link to="/orders" class="tab-item">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h10a2 2 0 0 1 2 2v16l-7-3-7 3V5a2 2 0 0 1 2-2Zm2 5v2h6V8H9Zm0 4v2h6v-2H9Z" fill="currentColor"/></svg>
        <span>订单</span>
      </router-link>
    </nav>
  </div>
</template>

<style scoped>
.shell {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  padding-bottom: calc(72px + var(--safe-bottom));
  position: relative;
}

.hero {
  position: relative;
  padding: 14px 16px 0;
}

.hero-bg {
  position: absolute;
  inset: 0 0 24px;
  background: linear-gradient(160deg, #0d9f6e 0%, #0b7d58 45%, #065f46 100%);
  border-radius: 0 0 28px 28px;
}

.hero-inner {
  position: relative;
  color: #fff;
  padding-bottom: 12px;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.18);
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 20px;
  backdrop-filter: blur(6px);
}

.title {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.tagline {
  margin: 2px 0 0;
  font-size: 12px;
  opacity: 0.88;
}

.badge {
  margin-left: auto;
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.22);
  white-space: nowrap;
}

.notice {
  margin-top: 14px;
  display: flex;
  gap: 10px;
  align-items: flex-start;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 14px;
  padding: 10px 12px;
  backdrop-filter: blur(8px);
}

.notice-icon { font-size: 18px; line-height: 1.2; }
.notice-body { min-width: 0; flex: 1; }
.notice-title { font-size: 13px; font-weight: 700; }
.notice-sub { font-size: 11px; opacity: 0.86; margin-top: 2px; }
.notice-link {
  display: inline-block;
  margin-top: 6px;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  text-decoration: underline;
  text-underline-offset: 2px;
  opacity: 0.95;
}

.main {
  padding: 0 14px 16px;
  margin-top: -8px;
  position: relative;
  z-index: 1;
}

.fab {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: calc(78px + var(--safe-bottom));
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px 10px 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
  color: #fff;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.28);
  max-width: calc(480px - 28px);
  width: max-content;
}

.fab-icon { font-size: 16px; }
.fab-text { font-size: 14px; font-weight: 700; }
.fab-price { font-size: 14px; font-weight: 800; color: #fbbf24; margin-left: 4px; }
.fab-badge {
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 999px;
  background: var(--accent);
  font-size: 11px;
  font-weight: 800;
  display: grid;
  place-items: center;
  font-style: normal;
}

.tabbar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 30;
  max-width: 480px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--line);
  padding-bottom: var(--safe-bottom);
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 0 10px;
  color: #9ca3af;
  font-size: 11px;
  font-weight: 600;
}

.tab-item svg { width: 22px; height: 22px; }

.tab-item.router-link-active { color: var(--brand-dark); }

.tab-icon-wrap { position: relative; display: inline-block; }

.tab-badge {
  position: absolute;
  top: -6px;
  right: -10px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 999px;
  background: var(--accent);
  color: #fff;
  font-size: 10px;
  font-weight: 800;
  display: grid;
  place-items: center;
  font-style: normal;
  border: 2px solid #fff;
}

.page-enter-active, .page-leave-active { transition: opacity 0.18s ease, transform 0.18s ease; }
.page-enter-from, .page-leave-to { opacity: 0; transform: translateY(6px); }
</style>
