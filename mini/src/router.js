import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'
import Cart from './views/Cart.vue'
import Checkout from './views/Checkout.vue'
import Orders from './views/Orders.vue'
import OrderDetail from './views/OrderDetail.vue'
import ProductDetail from './views/ProductDetail.vue'

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: Home },
    { path: '/products/:id', component: ProductDetail, props: true },
    { path: '/cart', component: Cart },
    { path: '/checkout', component: Checkout },
    { path: '/orders', component: Orders },
    { path: '/orders/:id', component: OrderDetail, props: true },
  ],
})
