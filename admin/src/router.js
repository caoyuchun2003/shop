import { createRouter, createWebHistory } from 'vue-router'
import Orders from './views/Orders.vue'
import Products from './views/Products.vue'

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/orders' },
    { path: '/orders', component: Orders },
    { path: '/products', component: Products },
  ],
})
