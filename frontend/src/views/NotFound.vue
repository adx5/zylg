<!-- frontend/src/views/NotFound.vue —— 全局路由兜底，避免未注册路径白屏 -->
<template>
  <div class="nf-page">
    <div class="nf-code">404</div>
    <h2 class="nf-title">页面不存在或已下线</h2>
    <p class="nf-desc">链接可能有误，或该功能尚未开放</p>

    <div class="nf-actions">
      <button class="nf-btn primary" @click="goHome">返回首页</button>
      <button class="nf-btn" @click="$router.back()">返回上一页</button>
    </div>

    <p class="nf-path">当前路径：{{ $route.fullPath }}</p>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  const role = localStorage.getItem('activeRole')
  const map = {
    merchant: '/merchant/dash',
    provider: '/provider/hall',
    hq_ops: '/admin/dash',
    city_gov: '/admin/dash',
    city_ops: '/admin/dash'
  }
  router.push(map[role] || '/worker/home')
}
</script>

<style scoped>
.nf-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 30px;
  background: var(--bg, #eef1f5);
  text-align: center;
}
.nf-code { font-size: 64px; font-weight: 900; color: var(--brand, #1677ff); opacity: 0.25; letter-spacing: 4px; }
.nf-title { font-size: 20px; font-weight: 800; color: var(--text, #1d2531); margin-top: 8px; }
.nf-desc { font-size: 14px; color: #7b8797; margin-top: 10px; }

.nf-actions { display: flex; gap: 12px; margin-top: 28px; }
.nf-btn {
  height: 46px;
  padding: 0 26px;
  border-radius: 999px;
  border: 1px solid #e5e9f0;
  background: #fff;
  color: #4a5565;
  font-size: 15px;
  font-weight: 700;
}
.nf-btn.primary { background: var(--brand, #1677ff); border-color: var(--brand, #1677ff); color: #fff; }

.nf-path { margin-top: 32px; font-size: 12px; color: #b9c2cc; word-break: break-all; }
</style>
