<template>
  <view class="page">
    <view class="card">
      <text class="title">自提信息</text>
      <picker :range="pickupNames" @change="onPickup">
        <view class="field">自提点：{{ pickupNames[pickupIndex] || '请选择' }}</view>
      </picker>
      <input class="input" v-model="buyer_name" placeholder="联系人姓名" />
      <input class="input" v-model="buyer_phone" type="number" placeholder="手机号" />
      <button type="primary" :loading="busy" @click="submit">提交订单</button>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { api } from '../../utils/api'

const points = ref([])
const pickupIndex = ref(0)
const buyer_name = ref('')
const buyer_phone = ref('')
const busy = ref(false)

const pickupNames = computed(() => points.value.map((p) => `${p.name}（${p.address}）`))

onLoad(async () => {
  try {
    points.value = await api.pickups()
  } catch (e) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
})

function onPickup(e) {
  pickupIndex.value = Number(e.detail.value)
}

async function submit() {
  if (!buyer_name.value.trim() || !buyer_phone.value.trim()) {
    uni.showToast({ title: '请填写姓名和手机号', icon: 'none' })
    return
  }
  if (!points.value.length) {
    uni.showToast({ title: '暂无自提点', icon: 'none' })
    return
  }
  busy.value = true
  try {
    const order = await api.createOrder({
      pickup_point_id: points.value[pickupIndex.value].id,
      buyer_name: buyer_name.value.trim(),
      buyer_phone: buyer_phone.value.trim(),
    })
    uni.redirectTo({ url: `/pages/order/detail?id=${order.id}` })
  } catch (e) {
    uni.showToast({ title: e.message, icon: 'none' })
  } finally {
    busy.value = false
  }
}
</script>

<style>
.page { padding: 24rpx; min-height: 100vh; background: #f3f5f8; }
.card { background: #fff; border-radius: 20rpx; padding: 28rpx; }
.title { display: block; font-size: 32rpx; font-weight: 800; margin-bottom: 20rpx; }
.field { padding: 22rpx 0; border-bottom: 1px solid #eef2f7; color: #374151; }
.input {
  margin-top: 20rpx; padding: 22rpx; background: #f8fafc; border-radius: 14rpx; font-size: 28rpx;
}
button { margin-top: 32rpx; background: #0d9f6e; }
</style>
