<!-- frontend/src/views/merchant/MerchantResumes.vue (B端公共人才库：真实数据 + 灰色扁平头像) -->
<template>
  <div class="talent-page">
    <div class="header">
      <h2>平台人才库</h2>
      <div class="search-bar">
        <input type="text" v-model="keyword" placeholder="搜索意向岗位，如：普工、保洁" @keyup.enter="load" />
        <button @click="load">搜索</button>
      </div>
      <div class="filter-tags">
        <span v-for="tag in filters" :key="tag" @click="pickTag(tag)">{{ tag }}</span>
      </div>
    </div>

    <div class="list">
      <div class="card" v-for="item in displayList" :key="item.id" @click="openDetail(item)">
        <div class="info-left">
          <div class="user-title">
            <UserAvatar :src="item.avatar" :size="40" />
            <div class="basic">
              <h3>
                {{ item.name }}
                <span v-if="item.age" class="tag">{{ item.age }}岁</span>
                <span v-if="item.education" class="tag">{{ item.education }}</span>
              </h3>
              <div class="intent">{{ item.job_intent || '暂无意向填写' }} | 期望: {{ item.salary || '面议' }}</div>
            </div>
          </div>

          <div class="meta-tags">
            <span class="active-time today">已实名</span>
            <span class="cloud-tag" v-if="isFav(item)">⭐ 已入简历库</span>
          </div>
        </div>

        <div class="action-right">
          <button class="btn-call" @click.stop="handleCall(item)">📞 沟通</button>
          <button class="btn-favorite" :class="{ 'is-fav': isFav(item) }" @click.stop="toggleFavorite(item)">
            {{ isFav(item) ? '已收藏' : '⭐ 收藏' }}
          </button>
        </div>
      </div>

      <p v-if="!loading && !displayList.length" class="empty">
        人才库暂无符合条件的求职者<br />
        <span class="empty-sub">（仅展示已实名求职者，清理测试数据后为空属正常）</span>
      </p>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="showDetail" class="modal-overlay" @click.self="showDetail = false">
      <div class="modal-content">
        <h3>人才详情</h3>
        <div class="detail-info">
          <p><strong>姓名：</strong>{{ currentResume.name }}</p>
          <p v-if="currentResume.age"><strong>年龄：</strong>{{ currentResume.age }}岁</p>
          <p><strong>学历：</strong>{{ currentResume.education || '未填写' }}</p>
          <p><strong>意向岗位：</strong>{{ currentResume.job_intent || '未填写' }}</p>
          <p><strong>期望薪资：</strong>{{ currentResume.salary || '面议' }}</p>
          <p><strong>手机号：</strong>{{ currentResume.phone }}</p>
        </div>
        <div class="modal-btns">
          <button class="btn-call" @click="handleCall(currentResume)">📞 电话沟通</button>
          <button class="btn-close" @click="showDetail = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import UserAvatar from '../../components/UserAvatar.vue'

const keyword = ref('')
const filters = ['附近优先', '普工', '叉车工', '保安', '保洁', '日结', '全部']
const talents = ref([])
const loading = ref(true)

const showDetail = ref(false)
const currentResume = ref({})
const isVerified = ref(false)

// 收藏存本地（避免为演示数据加表；后续可迁移到企业简历库）
const FAV_KEY = 'merchant_talent_favs'
const favIds = ref(JSON.parse(localStorage.getItem(FAV_KEY) || '[]'))
const isFav = (item) => favIds.value.includes(item.id)

const maskName = (name) => {
  if (!name) return '求职者'
  return name.length <= 1 ? name : name[0] + '**'
}

async function load() {
  loading.value = true
  try {
    const res = await api.get('/user/talents', { params: keyword.value ? { keyword: keyword.value } : {} })
    const rows = res.data || []
    talents.value = rows.map((u) => {
      const b = u.resume_data?.basic || {}
      return {
        id: u.id,
        name: maskName(u.real_name || b.name),
        avatar: '',
        age: b.age || '',
        education: b.education || '',
        job_intent: b.expected_position || b.skills || '',
        salary: b.expected_salary || '',
        phone: u.phone,
        raw_name: u.real_name || b.name || ''
      }
    })
  } catch (err) {
    talents.value = []
    window.$toast && window.$toast(err.response?.data?.detail || '人才库加载失败')
  }
  loading.value = false
}

const displayList = computed(() => {
  if (!keyword.value) return talents.value
  const k = keyword.value.trim()
  return talents.value.filter(
    (t) => (t.job_intent || '').includes(k) || (t.name || '').includes(k)
  )
})

function pickTag(tag) {
  keyword.value = tag === '全部' || tag === '附近优先' ? '' : tag
}

onMounted(async () => {
  try {
    const res = await api.get('/merchant/info')
    isVerified.value = res.data?.status === 'active'
  } catch (err) {}

  await load()
})

const openDetail = (item) => {
  currentResume.value = item
  showDetail.value = true
}

function toggleFavorite(item) {
  if (!isVerified.value) return window.$toast && window.$toast('请先完成企业备案认证')
  const i = favIds.value.indexOf(item.id)
  if (i >= 0) favIds.value.splice(i, 1)
  else favIds.value.push(item.id)
  localStorage.setItem(FAV_KEY, JSON.stringify(favIds.value))
  window.$toast && window.$toast(i < 0 ? '已存入企业简历库' : '已从简历库移除')
}

async function handleCall(item) {
  if (!isVerified.value) {
    return window.$toast && window.$toast('您的企业尚未通过备案，无法查看联系方式')
  }
  try {
    // 取完整号码会写审计日志（谁、何时、看了谁）
    const res = await api.post(`/user/talents/${item.id}/contact`, { reason: '人才库沟通' })
    const phone = res.data?.phone
    if (phone) window.location.href = `tel:${phone}`
  } catch (err) {
    window.$toast && window.$toast(err.response?.data?.detail || '获取联系方式失败')
  }
}
</script>

<style scoped>
.talent-page { min-height: 100vh; background: #f5f7fa; }
.header { background: #fff; padding: 16px; position: sticky; top: 0; z-index: 10; border-bottom: 1px solid #f0f2f5; }
.header h2 { font-size: 18px; color: #1f2937; margin-bottom: 12px; }
.search-bar { display: flex; gap: 8px; }
.search-bar input { flex: 1; height: 38px; border: 1px solid #e5e7eb; border-radius: 6px; padding: 0 12px; font-size: 14px; outline: none; }
.search-bar button { width: 70px; height: 38px; background: #2563eb; color: #fff; border: none; border-radius: 6px; font-weight: bold; font-size: 14px; }
.filter-tags { display: flex; gap: 8px; margin-top: 12px; overflow-x: auto; padding-bottom: 2px; }
.filter-tags span { flex-shrink: 0; padding: 5px 12px; background: #f3f4f6; border-radius: 14px; font-size: 13px; color: #4b5563; cursor: pointer; }

.list { padding: 12px 16px; }
.card { background: #fff; border-radius: 12px; padding: 14px; margin-bottom: 12px; display: flex; justify-content: space-between; gap: 10px; }
.info-left { flex: 1; min-width: 0; }
.user-title { display: flex; gap: 10px; align-items: flex-start; }
.basic h3 { font-size: 16px; color: #1f2937; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.tag { font-size: 12px; background: #f3f4f6; color: #6b7280; padding: 2px 6px; border-radius: 4px; font-weight: normal; }
.intent { font-size: 13px; color: #4b5563; margin-top: 6px; }
.meta-tags { display: flex; gap: 10px; margin-top: 10px; font-size: 12px; color: #9ca3af; }
.active-time.today { color: #10b981; }
.cloud-tag { color: #f59e0b; }

.action-right { display: flex; flex-direction: column; gap: 8px; flex-shrink: 0; }
.btn-call { background: #2563eb; color: #fff; border: none; padding: 8px 12px; border-radius: 6px; font-size: 13px; font-weight: bold; }
.btn-favorite { background: #fff; color: #4b5563; border: 1px solid #e5e7eb; padding: 8px 12px; border-radius: 6px; font-size: 13px; }
.btn-favorite.is-fav { border-color: #fcd34d; color: #f59e0b; background: #fffbeb; }

.empty { text-align: center; color: #9ca3af; font-size: 14px; padding: 60px 20px; line-height: 1.9; }
.empty-sub { font-size: 12px; color: #c4ccd6; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.45); display: flex; align-items: center; justify-content: center; z-index: 99; }
.modal-content { background: #fff; width: 82%; max-width: 340px; border-radius: 14px; padding: 20px; }
.modal-content h3 { font-size: 17px; margin-bottom: 14px; color: #1f2937; }
.detail-info p { font-size: 14px; color: #4b5563; margin-bottom: 8px; }
.modal-btns { display: flex; gap: 10px; margin-top: 16px; }
.modal-btns .btn-call { flex: 1; }
.btn-close { flex: 1; background: #f3f4f6; color: #4b5563; border: none; border-radius: 6px; font-size: 14px; }
</style>
