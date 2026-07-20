import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn } from './auth'
import Login from './views/Login.vue'
import Dashboard from './views/Dashboard.vue'
import Orders from './views/Orders.vue'
import Products from './views/Products.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/login', component: Login, meta: { public: true } },
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: Dashboard },
    { path: '/orders', component: Orders },
    { path: '/products', component: Products },
  ],
})

router.beforeEach((to) => {
  if (to.meta.public) return true
  if (!isLoggedIn()) return { path: '/login', query: { redirect: to.fullPath } }
  return true
})

export default router
