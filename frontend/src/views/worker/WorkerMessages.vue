<!-- frontend/src/views/worker/WorkerMessages.vue —— 求职者消息中心 -->
<template>
  <div class="msg-page">
    <header class="msg-nav">
      <button class="msg-back" @click="$router.back()">‹</button>
      <span class="msg-title">消息中心</span>
      <button class="msg-read-all" :disabled="!unread" @click="readAll">全部已读</button>
    </header>

    <div v-if="loading" class="msg-tip">加载中…</div>

    <template v-else>
      <article
        v-for="m in list"
        :key="m.id"
        :class="['msg-card', { unread: !m.is_read }]"
        @click="openItem(m)"
      >
        <div class="msg-head">
          <span class="msg-dot" v-if="!m.is_read"></span>
          <h3 class="msg-name">{{ m.title }}</h3>
          <span class="msg-time">{{ formatTime(m.created_at) }}</span>
        </div>
        <p class="msg-body">{{ m.content }}</p>
      </article>

      <p v-if="!list.length" class="msg-tip">
        暂无消息。报名、面试邀请、录用和结单通知都会出现在这里。
      </p>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const list = ref([])
const loading = ref(true)
const unread = ref(0)

function formatTime(t) {
  if (!t) return ''
  return String(t).replace('T', ' ').slice(0, 16)
}

async function load() {
  loading.value = true
  try {
    const res = await api.get('/notifications/list')
    list.value = res.data || []
  } catch (err) {
    list.value = []
  }
  try {
    const c = await api.get('/notifications/unread-count')
    unread.value = c.data?.count || 0
  } catch (err) {
    unread.value = 0
  }
  loading.value = false
}

async function openItem(m) {
  if (m.is_read) return
  try {
    await api.put(`/notifications/read/${m.id}`)
    m.is_read = true
    unread.value = Math.max(0, unread.value - 1)
  } catch (err) {}
}

async function readAll() {
  try {
    await api.put('/notifications/read-all')
    list.value = list.value.map((m) => ({ ...m, is_read: true }))
    unread.value = 0
    window.$toast && window.$toast('全部已读')
  } catch (err) {
    window.$toast && window.$toast('操作失败')
  }
}

onMounted(load)
</script>

<style scoped>
.msg-page { min-height: 100vh; background: var(--bg, #eef1f5); padding-bottom: 30px; }

.msg-nav {
  position: sticky;
  top: 0;
  z-index: 10;
  height: 52px;
  background: #fff;
  display: flex;
  align-items: center;
  padding: 0 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}
.msg-back { border: none; background: none; font-size: 28px; width: 40px; text-align: left; color: #333; padding-bottom: 4px; }
.msg-title { flex: 1; text-align: center; font-size: 18px; font-weight: 800; color: var(--text, #111); }
.msg-read-all {
  border: none;
  background: none;
  font-size: 13px;
  color: var(--brand, #1677ff);
  font-weight: 700;
  width: 68px;
  text-align: right;
}
.msg-read-all:disabled { color: #b9c2cc; }

.msg-card {
  background: #fff;
  border-radius: 14px;
  padding: 16px 18px;
  margin: 12px 20px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}
.msg-card.unread { border-left: 3px solid var(--brand, #1677ff); }

.msg-head { display: flex; align-items: center; gap: 8px; }
.msg-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--price, #ff7a1a); flex-shrink: 0; }
.msg-name { flex: 1; font-size: 16px; font-weight: 800; color: var(--text, #111); }
.msg-time { font-size: 12px; color: #9aa6b5; flex-shrink: 0; }
.msg-body { font-size: 14px; color: #5a6675; line-height: 1.65; margin-top: 8px; }

.msg-tip { text-align: center; font-size: 14px; color: #9aa6b5; padding: 40px 30px; line-height: 1.7; }
</style>
