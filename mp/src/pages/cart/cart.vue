<template>
  <view class="page">
    <view v-if="loading" class="muted center">加载中…</view>
    <view v-else-if="!cart.items.length" class="empty">
      <text class="empty-title">购物车是空的</text>
      <button size="mini" @click="goHome">去逛逛</button>
    </view>
    <view v-else>
      <view v-for="it in cart.items" :key="it.id" class="row card">
        <image v-if="it.cover_url" class="thumb" :src="it.cover_url" mode="aspectFill" />
        <view v-else class="thumb placeholder">🛒</view>
        <view class="info">
          <text class="name">{{ it.name }}</text>
          <text class="muted">¥{{ yuan(it.price_cents) }}</text>
          <view class="ops">
            <view class="btn" @click="setQty(it, it.qty - 1)">−</view>
            <text class="qty">{{ it.qty }}</text>
            <view class="btn" @click="setQty(it, it.qty + 1)">+</view>
            <text class="del" @click="remove(it)">删除</text>
          </view>
        </view>
        <text class="line">¥{{ yuan(it.line_cents) }}</text>
      </view>
      <view class="bar card">
        <text>合计 <text class="price">¥{{ yuan(cart.total_cents) }}</text></text>
        <button type="primary" size="mini" @click="goCheckout">去结算</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app'
import { ref } from 'vue'
import { api, yuan } from '../../utils/api'

const cart = ref({ items: [], total_cents: 0 })
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    cart.value = await api.cart()
  } catch (e) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    loading.value = false
  }
}

async function setQty(it, qty) {
  try {
    await api.setCartQty(it.id, qty)
    await load()
  } catch (e) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

async function remove(it) {
  try {
    await api.delCart(it.id)
    await load()
  } catch (e) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

function goHome() {
  uni.switchTab({ url: '/pages/index/index' })
}

function goCheckout() {
  uni.navigateTo({ url: '/pages/checkout/checkout' })
}

onShow(load)
</script>

<style>
.page { padding: 24rpx; min-height: 100vh; background: #f3f5f8; }
.card { background: #fff; border-radius: 20rpx; padding: 20rpx; margin-bottom: 16rpx; }
.row { display: flex; align-items: center; gap: 16rpx; }
.thumb { width: 100rpx; height: 100rpx; border-radius: 16rpx; background: #eef2f7; }
.placeholder { display: flex; align-items: center; justify-content: center; }
.info { flex: 1; }
.name { display: block; font-weight: 700; font-size: 28rpx; }
.ops { display: flex; align-items: center; gap: 12rpx; margin-top: 12rpx; }
.btn {
  width: 48rpx; height: 48rpx; border-radius: 12rpx; background: #e8f8f1; color: #087a55;
  text-align: center; line-height: 48rpx; font-weight: 800;
}
.qty { min-width: 32rpx; text-align: center; font-weight: 700; }
.del { color: #dc2626; font-size: 24rpx; margin-left: 8rpx; }
.line { color: #ff6b35; font-weight: 800; }
.bar { display: flex; justify-content: space-between; align-items: center; }
.price { color: #ff6b35; font-weight: 800; }
.empty { text-align: center; padding: 120rpx 0; }
.empty-title { display: block; margin-bottom: 20rpx; color: #6b7280; }
.muted { color: #6b7280; font-size: 24rpx; }
.center { text-align: center; padding: 80rpx 0; }
</style>
