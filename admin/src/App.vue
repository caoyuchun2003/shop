<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { clearToken } from './auth'

const route = useRoute()
const router = useRouter()
const active = computed(() => route.path)
const isLogin = computed(() => route.path === '/login')

function logout() {
  clearToken()
  router.replace('/login')
}
</script>

<template>
  <router-view v-if="isLogin" />

  <el-container v-else class="layout">
    <el-aside width="232px" class="aside">
      <div class="brand">
        <div class="logo">邻</div>
        <div>
          <div class="brand-title">邻里小店</div>
          <div class="brand-sub">运营后台</div>
        </div>
      </div>

      <el-menu
        router
        :default-active="active"
        class="menu"
        background-color="transparent"
        text-color="#d1fae5"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/dashboard">
          <span class="menu-ico">📊</span>
          <span>运营看板</span>
        </el-menu-item>
        <el-menu-item index="/orders">
          <span class="menu-ico">📦</span>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/products">
          <span class="menu-ico">🛒</span>
          <span>商品管理</span>
        </el-menu-item>
        <el-menu-item index="/pickups">
          <span class="menu-ico">📍</span>
          <span>自提点</span>
        </el-menu-item>
      </el-menu>

      <div class="aside-foot">
        <div class="pill">模拟演示</div>
        <el-button class="logout" @click="logout">退出登录</el-button>
      </div>
    </el-aside>

    <el-container>
      <el-header class="topbar" height="64px">
        <div>
          <div class="top-title">阳光花园 · 今日团</div>
          <div class="top-sub">自提轻团购运营台</div>
        </div>
        <div class="top-right">
          <span class="live-dot" />
          <span>服务正常</span>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style>
@import './style.css';

.layout { height: 100%; min-height: 100vh; }

.aside {
  background: linear-gradient(180deg, #0b7d58 0%, #065f46 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  border-right: 0 !important;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 22px 18px 18px;
}

.logo {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.16);
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 18px;
}

.brand-title { font-weight: 800; font-size: 16px; }
.brand-sub { font-size: 12px; opacity: 0.8; margin-top: 2px; }

.menu {
  border-right: 0 !important;
  padding: 8px 10px;
  flex: 1;
}

.menu .el-menu-item {
  border-radius: 12px;
  margin-bottom: 6px;
  height: 46px;
  line-height: 46px;
}

.menu .el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.16) !important;
  font-weight: 700;
}

.menu-ico { margin-right: 8px; }

.aside-foot {
  padding: 16px 18px 22px;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
}

.pill {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  margin-bottom: 12px;
}

.logout {
  width: 100%;
  background: rgba(255, 255, 255, 0.12) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: #fff !important;
}

.topbar {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.top-title { font-weight: 800; font-size: 15px; }
.top-sub { font-size: 12px; color: var(--muted); margin-top: 2px; }

.top-right {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--brand-dark);
  font-weight: 700;
  background: var(--brand-soft);
  padding: 8px 12px;
  border-radius: 999px;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--brand);
  box-shadow: 0 0 0 4px rgba(13, 159, 110, 0.18);
}

.main {
  padding: 22px 24px 32px;
  background: var(--bg);
}

.el-table {
  --el-table-header-bg-color: #f8fafc;
  --el-table-row-hover-bg-color: #f0fdf8;
}

.el-table th.el-table__cell {
  font-weight: 700;
  color: #374151;
}
</style>
