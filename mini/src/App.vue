<script setup>
</script>

<template>
  <div class="shell">
    <header class="top">
      <div class="title">邻里小店</div>
      <p class="sub">社区团购 · 模拟支付演示</p>
    </header>
    <main class="main">
      <router-view />
    </main>
    <nav class="tab">
      <router-link to="/">商品</router-link>
      <router-link to="/cart">购物车</router-link>
    </nav>
  </div>
</template>

<style scoped>
.shell { max-width: 480px; margin: 0 auto; min-height: 100vh; padding-bottom: 72px; }
.top { padding: 20px 16px 8px; }
.title { font-size: 22px; font-weight: 700; }
.sub { margin: 4px 0 0; color: #6b7280; font-size: 13px; }
.main { padding: 8px 16px 16px; }
.tab {
  position: fixed; left: 0; right: 0; bottom: 0;
  max-width: 480px; margin: 0 auto;
  display: grid; grid-template-columns: 1fr 1fr;
  background: #fff; border-top: 1px solid #eee;
}
.tab a { text-align: center; padding: 14px; font-size: 14px; }
.tab a.router-link-active { color: #16a34a; font-weight: 600; }
</style>
