const API_BASE = (import.meta.env.VITE_API_URL || 'https://2jng249qsad2r.cfc-execute.bj.baidubce.com').replace(/\/$/, '')
const SID_KEY = 'shop_sid'

function sessionId() {
  let sid = uni.getStorageSync(SID_KEY)
  if (!sid) {
    sid = `mp_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`
    uni.setStorageSync(SID_KEY, sid)
  }
  return sid
}

export function yuan(cents) {
  return (Number(cents || 0) / 100).toFixed(2)
}

export function request({ url, method = 'GET', data }) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        'X-Session-Id': sessionId(),
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          const detail = res.data?.detail
          reject(new Error(typeof detail === 'string' ? detail : `请求失败 ${res.statusCode}`))
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '网络错误')),
    })
  })
}

export const api = {
  products: () => request({ url: '/api/products' }),
  product: (id) => request({ url: `/api/products/${id}` }),
  cart: () => request({ url: '/api/cart' }),
  addCart: (product_id, qty = 1) => request({ url: '/api/cart/items', method: 'POST', data: { product_id, qty } }),
  setCartQty: (id, qty) => request({ url: `/api/cart/items/${id}`, method: 'PATCH', data: { qty } }),
  delCart: (id) => request({ url: `/api/cart/items/${id}`, method: 'DELETE' }),
  pickups: () => request({ url: '/api/pickup-points' }),
  createOrder: (body) => request({ url: '/api/orders', method: 'POST', data: body }),
  orders: () => request({ url: '/api/orders' }),
  order: (id) => request({ url: `/api/orders/${id}` }),
  mockPay: (id) => request({ url: `/api/orders/${id}/mock-pay`, method: 'POST' }),
  cancelOrder: (id) => request({ url: `/api/orders/${id}/cancel`, method: 'POST' }),
}
