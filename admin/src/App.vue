<script setup>
</script>

<template>
  <el-container class="layout">
    <el-aside width="200px" class="aside">
      <div class="brand">邻里小店</div>
      <el-menu router :default-active="$route.path">
        <el-menu-item index="/orders">订单</el-menu-item>
        <el-menu-item index="/products">商品</el-menu-item>
      </el-menu>
    </el-aside>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<style>
html, body, #app { height: 100%; margin: 0; }
.layout { height: 100%; }
.aside { border-right: 1px solid #eee; background: #fafafa; }
.brand { padding: 20px 16px; font-weight: 700; font-size: 16px; }
</style>
