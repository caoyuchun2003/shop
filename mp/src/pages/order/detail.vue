<template>
  <view class="page" v-if="order">
    <view class="status" :class="tone">
      <text class="label">{{ statusMap[order.status]?.label || order.status }}</text>
      <text class="hint">{{ statusMap[order.status]?.hint }}</text>
      <text class="oid">订单号 #{{ order.id }}</text>
    </view>

    <view class="card">
      <text class="title">自提信息</text>
      <text class="line">{{ order.pickup_point?.name }}</text>
      <text class="muted">{{ order.pickup_point?.address }}</text>
      <text class="muted">{{ order.buyer_name }} · {{ order.buyer_phone }}</text>
    </view>

    <view class="card">
      <text class="title">商品明细</text>
      <view v-for="it in order.items" :key="it.product_id" class="item">
        <text>{{ it.product_name }} × {{ it.qty }}</text>
        <text>¥{{ yuan(it.price_cents * it.qty) }}</text>
      </view>
      <view class="total">
        <text>实付</text>
        <text class="price">¥{{ yuan(order.total_cents) }}</text>
      </view>
    </view>

    <button
      v-if="order.status === 'pending_pay'"
      type="primary"
      :loading="busy"
      @click="pay"
    >
      模拟支付 ¥{{ yuan(order.total_cents) }}
    </button>
    <view v-else class="ok">支付演示完成。后台可核销为待自提 / 已完成。</view>
  </view>
  <view v-else class="muted center">{{ error || '加载中…' }}</view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { api, yuan } from '../../utils/api'

const order = ref(null)
const error = ref('')
const busy = ref(false)
let orderId = ''

const statusMap = {
  pending_pay: { label: '待支付', hint: '请完成模拟支付', tone: 'warn' },
  paid: { label: '已支付', hint: '等待商家备货', tone: 'ok' },
  ready: { label: '待自提', hint: '可前往自提点取货', tone: 'ok' },
  completed: { label: '已完成', hint: '感谢支持', tone: 'done' },
  cancelled: { label: '已取消', hint: '', tone: 'muted' },
}

const tone = computed(() => statusMap[order.value?.status]?.tone || 'muted')

onLoad(async (q) => {
  orderId = q.id
  try {
    order.value = await api.order(orderId)
  } catch (e) {
    error.value = e.message
  }
})

async function pay() {
  busy.value = true
  try {
    order.value = await api.mockPay(orderId)
    uni.showToast({ title: '支付成功', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    busy.value = false
  }
}
</script>

<style>
.page { padding: 24rpx; min-height: 100vh; background: #f3f5f8; }
.status { border-radius: 20rpx; padding: 28rpx; color: #fff; margin-bottom: 16rpx; }
.status.warn { background: linear-gradient(135deg, #f59e0b, #ea580c); }
.status.ok { background: linear-gradient(135deg, #0d9f6e, #087a55); }
.status.done, .status.muted { background: linear-gradient(135deg, #6b7280, #374151); }
.label { display: block; font-size: 36rpx; font-weight: 800; }
.hint { display: block; margin-top: 8rpx; opacity: 0.92; font-size: 26rpx; }
.oid { display: block; margin-top: 16rpx; font-size: 22rpx; opacity: 0.85; }
.card { background: #fff; border-radius: 20rpx; padding: 24rpx; margin-bottom: 16rpx; }
.title { display: block; font-weight: 800; margin-bottom: 12rpx; }
.line { display: block; font-weight: 700; }
.item { display: flex; justify-content: space-between; padding: 10rpx 0; border-bottom: 1px solid #f1f5f9; font-size: 26rpx; }
.total { display: flex; justify-content: space-between; margin-top: 16rpx; font-weight: 800; }
.price { color: #ff6b35; }
.ok { color: #087a55; font-size: 26rpx; line-height: 1.5; margin-top: 12rpx; }
.muted { color: #6b7280; font-size: 24rpx; display: block; margin-top: 6rpx; }
.center { text-align: center; padding: 120rpx 0; }
button { background: #0d9f6e; }
</style>
