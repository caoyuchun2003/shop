<template>
  <view class="page">
    <view class="banner">
      <text class="banner-tag">今日特惠</text>
      <text class="banner-title">邻居拼团 · 新鲜直达</text>
      <text class="banner-sub">社区自提 · 模拟支付演示</text>
    </view>

    <view v-if="loading" class="muted center">加载中…</view>
    <view v-else-if="error" class="muted center">{{ error }}</view>

    <view v-else class="grid">
      <view v-for="p in products" :key="p.id" class="card" @click="goDetail(p.id)">
        <image v-if="p.cover_url" class="cover" :src="p.cover_url" mode="aspectFill" />
        <view v-else class="cover placeholder">🛒</view>
        <view class="body">
          <text class="name">{{ p.name }}</text>
          <text class="desc">{{ p.desc }}</text>
          <view class="foot">
            <text class="price">¥{{ yuan(p.price_cents) }}</text>
            <view class="add" @click.stop="add(p)">+</view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { onShow } from '@dcloudio/uni-app'
import { ref } from 'vue'
import { api, yuan } from '../../utils/api'

const products = ref([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    products.value = await api.products()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function goDetail(id) {
  uni.navigateTo({ url: `/pages/product/detail?id=${id}` })
}

async function add(p) {
  try {
    await api.addCart(p.id, 1)
    uni.showToast({ title: '已加入购物车', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onShow(load)
</script>

<style>
.page { padding: 24rpx; background: #f3f5f8; min-height: 100vh; }
.banner {
  background: linear-gradient(135deg, #0d9f6e, #065f46);
  color: #fff;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
}
.banner-tag { font-size: 22rpx; opacity: 0.9; }
.banner-title { display: block; font-size: 34rpx; font-weight: 700; margin-top: 10rpx; }
.banner-sub { display: block; font-size: 24rpx; opacity: 0.85; margin-top: 8rpx; }
.grid { display: flex; flex-wrap: wrap; justify-content: space-between; }
.card {
  width: 48%;
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(15,23,42,0.06);
}
.cover { width: 100%; height: 220rpx; background: #eef2f7; }
.placeholder { display: flex; align-items: center; justify-content: center; font-size: 64rpx; }
.body { padding: 16rpx; }
.name { font-size: 28rpx; font-weight: 700; color: #1c2434; }
.desc {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #6b7280;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.foot { display: flex; justify-content: space-between; align-items: center; margin-top: 16rpx; }
.price { color: #ff6b35; font-weight: 800; font-size: 30rpx; }
.add {
  width: 56rpx; height: 56rpx; border-radius: 16rpx;
  background: #0d9f6e; color: #fff; text-align: center; line-height: 56rpx; font-size: 36rpx; font-weight: 700;
}
.muted { color: #6b7280; font-size: 26rpx; }
.center { text-align: center; padding: 80rpx 0; }
</style>
