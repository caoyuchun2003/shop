<template>
  <view class="page">
    <view class="chips">
      <view
        v-for="f in filters"
        :key="f.key"
        class="chip"
        :class="{ active: filter === f.key }"
        @click="filter = f.key"
      >{{ f.label }}</view>
    </view>

    <view v-if="loading" class="muted center">加载中…</view>
    <view v-else-if="!filtered.length" class="empty">暂无订单</view>

    <view
      v-for="o in filtered"
      :key="o.id"
      class="card"
      @click="goDetail(o.id)"
    >
      <view class="top">
        <text class="oid">#{{ o.id }}</text>
        <text class="tag">{{ statusMap[o.status] || o.status }}</text>
      </view>
      <view v-for="it in o.items" :key="it.product_id" class="item">
        {{ it.product_name }} × {{ it.qty }}
      </view>
      <view class="bottom">
        <text class="muted">{{ o.pickup_point?.name }}</text>
        <text class="price">¥{{ yuan(o.total_cents) }}</text>
      </view>
      <view v-if="o.status === 'pending_pay'" class="actions" @click.stop>
        <button size="mini" @click="cancel(o)">取消</button>
        <button size="mini" type="primary" @click="goDetail(o.id)">去支付</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { api, yuan } from '../../utils/api'

const orders = ref([])
const loading = ref(true)
const filter = ref('all')

const statusMap = {
  pending_pay: '待支付',
  paid: '已支付',
  ready: '待自提',
  completed: '已完成',
  cancelled: '已取消',
}

const filters = [
  { key: 'all', label: '全部' },
  { key: 'pending_pay', label: '待支付' },
  { key: 'paid', label: '已支付' },
  { key: 'ready', label: '待自提' },
  { key: 'completed', label: '已完成' },
]

const filtered = computed(() => {
  if (filter.value === 'all') return orders.value
  return orders.value.filter((o) => o.status === filter.value)
})

async function load() {
  loading.value = true
  try {
    orders.value = await api.orders()
  } catch (e) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    loading.value = false
  }
}

function goDetail(id) {
  uni.navigateTo({ url: `/pages/order/detail?id=${id}` })
}

async function cancel(o) {
  try {
    await api.cancelOrder(o.id)
    uni.showToast({ title: '已取消', icon: 'success' })
    await load()
  } catch (e) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onShow(load)
</script>

<style>
.page { padding: 24rpx; min-height: 100vh; background: #f3f5f8; }
.chips { display: flex; flex-wrap: wrap; gap: 12rpx; margin-bottom: 16rpx; }
.chip {
  padding: 10rpx 20rpx; border-radius: 999rpx; background: #fff; color: #6b7280;
  font-size: 24rpx; border: 1px solid #e8ecf1;
}
.chip.active { background: #0d9f6e; color: #fff; border-color: transparent; }
.card { background: #fff; border-radius: 20rpx; padding: 24rpx; margin-bottom: 16rpx; }
.top { display: flex; justify-content: space-between; margin-bottom: 12rpx; }
.oid { font-weight: 800; }
.tag { color: #087a55; font-size: 24rpx; font-weight: 700; }
.item { font-size: 26rpx; color: #374151; line-height: 1.6; }
.bottom { display: flex; justify-content: space-between; margin-top: 12rpx; }
.price { color: #ff6b35; font-weight: 800; }
.actions { display: flex; justify-content: flex-end; gap: 12rpx; margin-top: 16rpx; }
.muted { color: #6b7280; font-size: 24rpx; }
.center, .empty { text-align: center; padding: 80rpx 0; color: #6b7280; }
</style>
