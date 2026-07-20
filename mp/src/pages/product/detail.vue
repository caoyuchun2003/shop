<template>
  <view class="page" v-if="product">
    <image v-if="product.cover_url" class="cover" :src="product.cover_url" mode="aspectFill" />
    <view v-else class="cover placeholder">🛒</view>
    <view class="card">
      <text class="name">{{ product.name }}</text>
      <text class="desc">{{ product.desc }}</text>
      <view class="meta">
        <text class="price">¥{{ yuan(product.price_cents) }}</text>
        <text class="muted">库存 {{ product.stock }}</text>
      </view>
      <view class="qty-row">
        <text>数量</text>
        <view class="ops">
          <view class="btn" @click="qty = Math.max(1, qty - 1)">−</view>
          <text>{{ qty }}</text>
          <view class="btn" @click="qty = Math.min(99, qty + 1)">+</view>
        </view>
      </view>
      <button type="primary" :disabled="busy || product.stock < 1" @click="add">
        {{ product.stock < 1 ? '售罄' : '加入购物车' }}
      </button>
    </view>
  </view>
  <view v-else class="muted center">{{ error || '加载中…' }}</view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { api, yuan } from '../../utils/api'

const product = ref(null)
const error = ref('')
const qty = ref(1)
const busy = ref(false)

onLoad(async (q) => {
  try {
    product.value = await api.product(q.id)
  } catch (e) {
    error.value = e.message
  }
})

async function add() {
  busy.value = true
  try {
    await api.addCart(product.value.id, qty.value)
    uni.showToast({ title: '已加入', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    busy.value = false
  }
}
</script>

<style>
.page { min-height: 100vh; background: #f3f5f8; padding-bottom: 40rpx; }
.cover { width: 100%; height: 480rpx; background: #eef2f7; }
.placeholder { display: flex; align-items: center; justify-content: center; font-size: 96rpx; }
.card { margin: 24rpx; background: #fff; border-radius: 20rpx; padding: 28rpx; }
.name { display: block; font-size: 36rpx; font-weight: 800; }
.desc { display: block; margin-top: 12rpx; color: #6b7280; font-size: 26rpx; line-height: 1.5; }
.meta { display: flex; justify-content: space-between; margin: 24rpx 0; }
.price { color: #ff6b35; font-size: 40rpx; font-weight: 800; }
.qty-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24rpx; font-weight: 700; }
.ops { display: flex; align-items: center; gap: 20rpx; }
.btn {
  width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #e8f8f1; color: #087a55;
  text-align: center; line-height: 56rpx; font-weight: 800;
}
.muted { color: #6b7280; }
.center { text-align: center; padding: 120rpx 0; }
</style>
