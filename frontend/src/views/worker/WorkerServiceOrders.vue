<!-- frontend/src/views/worker/WorkerServiceOrders.vue —— C端：我的同城服务订单 -->
<template>
  <div class="so-page">
    <header class="so-nav">
      <button class="so-back" @click="$router.back()">‹</button>
      <span class="so-title">同城服务订单</span>
      <button class="so-more" @click="$router.push('/worker/service')">去预约</button>
    </header>

    <div v-if="loading" class="so-tip">加载中…</div>

    <template v-else>
      <article v-for="o in list" :key="o.id" class="so-card">
        <div class="so-head">
          <h3 class="so-name">{{ o.title }}</h3>
          <span :class="['so-status', statusClass(o.status)]">{{ statusText(o.status) }}</span>
        </div>
        <p class="so-meta">
          <span v-if="o.price">￥{{ o.price }}</span>
          <span v-if="o.address"> · {{ o.address }}</span>
        </p>
        <p class="so-time">下单时间：{{ o.created_at || '—' }}</p>
      </article>

      <p v-if="!list.length" class="so-tip">
        还没有服务订单。去「同城」找师傅，预约后订单会出现在这里。
      </p>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const list = ref([])
const loading = ref(true)

const STATUS = {
  pending: { text: '待接单', cls: 'warn' },
  accepted: { text: '已接单', cls: 'info' },
  finished: { text: '已完成', cls: 'ok' },
  cancelled: { text: '已取消', cls: 'muted' },
  reviewed: { text: '已评价', cls: 'ok' }
}

const statusText = (s) => STATUS[s]?.text || s || '—'
const statusClass = (s) => STATUS[s]?.cls || 'muted'

async function load() {
  loading.value = true
  try {
    const res = await api.get('/services/orders/my')
    list.value = res.data || []
  } catch (err) {
    list.value = []
  }
  loading.value = false
}

onMounted(load)
</script>

<style scoped>
.so-page { min-height: 100vh; background: var(--bg, #eef1f5); padding-bottom: 30px; }

.so-nav {
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
.so-back { border: none; background: none; font-size: 28px; width: 40px; text-align: left; color: #333; padding-bottom: 4px; }
.so-title { flex: 1; text-align: center; font-size: 18px; font-weight: 800; color: var(--text, #111); }
.so-more { width: 60px; text-align: right; border: none; background: none; font-size: 13px; font-weight: 700; color: var(--brand, #1677ff); }

.so-card { background: #fff; border-radius: 14px; padding: 16px 18px; margin: 12px 20px 0; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04); }
.so-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.so-name { font-size: 17px; font-weight: 800; color: var(--text, #111); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.so-status { font-size: 12px; font-weight: 800; padding: 3px 10px; border-radius: 6px; flex-shrink: 0; }
.so-status.warn { background: #fff1e6; color: #ff7a1a; }
.so-status.info { background: #e8f1ff; color: #1677ff; }
.so-status.ok { background: #e8f8ee; color: #12a150; }
.so-status.muted { background: #f0f2f5; color: #7b8797; }

.so-meta { font-size: 15px; font-weight: 700; color: var(--price, #ff7a1a); margin-top: 8px; }
.so-time { font-size: 12px; color: #9aa6b5; margin-top: 6px; }

.so-tip { text-align: center; font-size: 14px; color: #9aa6b5; padding: 40px 30px; line-height: 1.7; }
</style>
