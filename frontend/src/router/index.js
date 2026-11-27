// frontend/src/router/index.js (完整：新增积分明细路由)
import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/worker/home' },
  // 全局兜底：未注册路径不再白屏（BUG-07）
  { path: '/:pathMatch(.*)*', component: () => import('../views/NotFound.vue') },
  // 通用实名认证页：求职者与服务商共用（不再强制跳 /worker 导致身份校验踢人）
  { path: '/verify', component: () => import('../views/worker/WorkerVerify.vue'), meta: { requireAuth: true } },
    { path: '/login', component: () => import('../views/Login.vue') },

    {
      path: '/worker',
      component: () => import('../layout/WorkerLayout.vue'),
      meta: { role: 'worker' },
      children: [
        { path: 'home', component: () => import('../views/worker/WorkerHome.vue') },
        { path: 'long-term', component: () => import('../views/worker/WorkerLongTerm.vue') },
        { path: 'short-term', component: () => import('../views/worker/WorkerShortTerm.vue') },
        { path: 'find', component: () => import('../views/worker/WorkerFind.vue') },
        { path: 'job-detail/:id', component: () => import('../views/worker/JobDetail.vue') },
        { path: 'service', component: () => import('../views/worker/WorkerService.vue') },
        { path: 'service-detail/:id', component: () => import('../views/worker/ServiceDetail.vue') },
        { path: 'service-reviews/:id', component: () => import('../views/worker/ServiceReviews.vue') },
        { path: 'my-applies', component: () => import('../views/worker/WorkerMyApplies.vue'), meta: { requireAuth: true } },
        { path: 'favorites', component: () => import('../views/worker/WorkerFavorites.vue') },
        { path: 'messages', component: () => import('../views/worker/WorkerMessages.vue'), meta: { requireAuth: true } },
        { path: 'service-orders', component: () => import('../views/worker/WorkerServiceOrders.vue'), meta: { requireAuth: true } },
        { path: 'task', component: () => import('../views/worker/WorkerTask.vue'), meta: { requireAuth: true } },
        { path: 'exchange', component: () => import('../views/worker/WorkerExchange.vue'), meta: { requireAuth: true } },
        { path: 'mine', component: () => import('../views/worker/WorkerMine.vue'), meta: { requireAuth: true } },
        { path: 'resume', component: () => import('../views/worker/WorkerResume.vue'), meta: { requireAuth: true } },
        { path: 'verify', component: () => import('../views/worker/WorkerVerify.vue'), meta: { requireAuth: true } },
        { path: 'points', component: () => import('../views/worker/WorkerPoints.vue'), meta: { requireAuth: true } }
      ]
    },

    {
      path: '/merchant',
      component: () => import('../layout/MerchantLayout.vue'),
      meta: { role: 'merchant', requireAuth: true },
      children: [
        { path: 'dash', component: () => import('../views/merchant/MerchantDash.vue') },
        { path: 'job-list', component: () => import('../views/merchant/MerchantJobList.vue') },
        { path: 'talent-pool', component: () => import('../views/merchant/MerchantResumes.vue') },
        { path: 'received-resumes', component: () => import('../views/merchant/MerchantTalentPool.vue') },
        { path: 'interviews', component: () => import('../views/merchant/MerchantInterviewSchedule.vue') },
        { path: 'reviews', component: () => import('../views/merchant/MerchantSettlement.vue') },
        { path: 'messages', component: () => import('../views/merchant/MerchantMessages.vue') },
        { path: 'settings', component: () => import('../views/merchant/MerchantSettings.vue') },
        { path: 'mine', component: () => import('../views/merchant/MerchantMine.vue') },
        { path: 'company', component: () => import('../views/merchant/MerchantCompany.vue') }
      ]
    },
    { path: '/merchant/job-create', component: () => import('../views/merchant/MerchantJobs.vue'), meta: { role: 'merchant', requireAuth: true } },
    { path: '/merchant/info', component: () => import('../views/merchant/MerchantInfo.vue'), meta: { role: 'merchant', requireAuth: true } },
    { path: '/merchant/verify', component: () => import('../views/merchant/MerchantVerify.vue'), meta: { role: 'merchant', requireAuth: true } },

    {
      path: '/provider',
      component: () => import('../layout/ProviderLayout.vue'),
      meta: { role: 'provider', requireAuth: true },
      children: [
        { path: 'hall', component: () => import('../views/provider/ProviderHall.vue') },
        { path: 'services', component: () => import('../views/provider/ProviderServices.vue') },
        { path: 'publish', component: () => import('../views/provider/ProviderPublish.vue') },
        { path: 'verify', component: () => import('../views/provider/ProviderVerify.vue') },
        { path: 'homepage', component: () => import('../views/provider/ProviderHomepage.vue') },
        { path: 'settings', component: () => import('../views/provider/ProviderSettings.vue') },
        { path: 'mine', component: () => import('../views/provider/ProviderMine.vue') }
      ]
    },

    {
      path: '/admin',
      component: () => import('../layout/AdminLayout.vue'),
      // 🚨 管理端角色守卫：activeRole 为界面标识（agent/ops/gov），后端真实角色在 JWT 里
      meta: { requireAuth: true, roles: ['agent', 'ops', 'gov', 'hq_ops', 'hq_admin', 'city_ops', 'city_gov', 'city_admin'] },
      children: [
        { path: 'dash', component: () => import('../views/admin/AdminDash.vue') },
        { path: 'audit', component: () => import('../views/admin/AuditCenter.vue') },
        { path: 'risk', component: () => import('../views/admin/RiskControl.vue') },
        { path: 'gov', component: () => import('../views/admin/GovDashboard.vue') },
        { path: 'mine', component: () => import('../views/admin/AdminMine.vue') }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const activeRole = localStorage.getItem('activeRole')

  if (to.path === '/login') return next()
  const requireAuth = to.matched.some(record => record.meta.requireAuth)

  if (!token && requireAuth) {
    if (window.$toast) window.$toast('请先登录')
    window.location.hash = '#/login'
    return
  }

  if (token) {
    const requiredRole = to.matched.find(record => record.meta.role)?.meta.role
    const requiredRoles = to.matched.find(record => record.meta.roles)?.meta.roles

    const singleMismatch = requiredRole && requiredRole !== activeRole
    const multiMismatch = requiredRoles && !requiredRoles.includes(activeRole)

    if (singleMismatch || multiMismatch) {
      // 🚨 修复：身份不匹配时不再清空登录态（原来会把用户直接踢回登录页），
      //    改为友好提示并送回该身份自己的工作台。
      const ROLE_HOME = {
        worker: '/worker/home',
        merchant: '/merchant/dash',
        provider: '/provider/hall',
        hq_ops: '/admin/dash',
        hq_admin: '/admin/dash',
        city_ops: '/admin/dash',
        city_gov: '/admin/dash',
        city_admin: '/admin/dash',
        agent: '/admin/dash',
        ops: '/admin/dash',
        gov: '/admin/dash'
      }
      const home = ROLE_HOME[activeRole] || '/worker/home'
      if (window.$toast) window.$toast('该页面不属于当前身份，已返回你的工作台')
      if (to.path === home) return next()
      return next(home)
    }
  }
  next()
})

export default router