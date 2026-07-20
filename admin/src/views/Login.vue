<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import { setToken } from '../auth'

const router = useRouter()
const token = ref('dev-admin')
const busy = ref(false)

async function login() {
  const value = token.value.trim()
  if (!value) {
    ElMessage.warning('请输入管理员令牌')
    return
  }
  busy.value = true
  try {
    setToken(value)
    await api.get('/api/admin/orders')
    ElMessage.success('登录成功')
    router.replace('/dashboard')
  } catch (e) {
    setToken('')
    ElMessage.error(e.response?.status === 401 ? '令牌无效' : (e.response?.data?.detail || e.message))
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="card">
      <div class="logo">邻</div>
      <h1>邻里小店后台</h1>
      <p class="sub">运营管理 · 模拟演示环境</p>

      <label class="field">
        <span>管理员令牌</span>
        <el-input
          v-model="token"
          type="password"
          show-password
          placeholder="请输入 X-Admin-Token"
          size="large"
          @keyup.enter="login"
        />
      </label>

      <el-button type="primary" size="large" class="btn" :loading="busy" @click="login">
        进入后台
      </el-button>

      <div class="hint">演示默认令牌：<code>dev-admin</code></div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(13, 159, 110, 0.18), transparent 40%),
    radial-gradient(circle at bottom left, rgba(234, 88, 12, 0.12), transparent 36%),
    linear-gradient(160deg, #f3f5f8 0%, #e8f8f1 100%);
}

.card {
  width: min(420px, 100%);
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 32px 28px 28px;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
  text-align: center;
}

.logo {
  width: 56px;
  height: 56px;
  margin: 0 auto 14px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-size: 24px;
  font-weight: 800;
  color: #fff;
  background: linear-gradient(135deg, #0d9f6e, #065f46);
  box-shadow: 0 10px 24px rgba(13, 159, 110, 0.3);
}

h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
}

.sub {
  margin: 8px 0 24px;
  color: var(--muted);
  font-size: 13px;
}

.field {
  display: block;
  text-align: left;
  margin-bottom: 16px;
}

.field span {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 700;
  color: #374151;
}

.btn {
  width: 100%;
  font-weight: 700;
}

.hint {
  margin-top: 16px;
  font-size: 12px;
  color: var(--muted);
}

code {
  background: var(--brand-soft);
  color: var(--brand-dark);
  padding: 2px 6px;
  border-radius: 6px;
  font-weight: 700;
}
</style>
