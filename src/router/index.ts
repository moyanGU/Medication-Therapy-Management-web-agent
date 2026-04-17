import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
// 新增：导入语音播报与页面用途元数据工具
import { speak, isSpeechSupported } from '@/composables/useSpeech'
// 使用相对路径以避免某些环境下别名解析异常
import { getPageTitle, getPagePurpose } from '../utils/pageMeta'

const isDebug = import.meta.env.MODE !== 'production'
const log = (...args: any[]) => {
  if (isDebug) console.log(...args)
}
const warn = (message: string, error?: unknown) => {
  if (isDebug && error !== undefined) {
    console.warn(message, error)
    return
  }
  console.warn(message)
}

const HomePage = () => import('@/pages/HomePage.vue')
const WelcomePage = () => import('@/pages/WelcomePage.vue')
const Login = () => import('@/pages/Login.vue')
const Register = () => import('@/pages/Register.vue')
const DashboardPage = () => import('@/pages/DashboardPage.vue')
const MtmServiceCasesPage = () => import('@/pages/MtmServiceCasesPage.vue')
const MtmServiceCaseDetailPage = () => import('@/pages/MtmServiceCaseDetailPage.vue')
const MtmInterviewFormPage = () => import('@/pages/MtmInterviewFormPage.vue')
const MtmAssessmentFormPage = () => import('@/pages/MtmAssessmentFormPage.vue')
const MedicinesPage = () => import('@/pages/MedicinesPage.vue')
const RecordsPage = () => import('@/pages/RecordsPage.vue')
const PlansPage = () => import('@/pages/PlansPage.vue')
const RecordStatsPage = () => import('@/pages/RecordStatsPage.vue')
const SettingsPage = () => import('@/pages/SettingsPage.vue')

// 提醒相关页面
const ReminderList = () => import('@/pages/reminders/ReminderList.vue')
const ReminderForm = () => import('@/pages/reminders/ReminderForm.vue')
const ReminderDetail = () => import('@/pages/reminders/ReminderDetail.vue')

// 病历管理相关页面
const MedicalRecords = () => import('@/pages/MedicalRecords.vue')
const MedicalRecordForm = () => import('@/pages/MedicalRecordForm.vue')
const MedicalRecordDetail = () => import('@/pages/MedicalRecordDetail.vue')
const MedicalRecordStatistics = () => import('@/pages/MedicalRecordStatistics.vue')

/**
 * 路由配置
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { requiresAuth: false },
  },
  {
    path: '/welcome',
    name: 'Welcome',
    component: WelcomePage,
    meta: { requiresAuth: false },
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { requiresGuest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { requiresGuest: true },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/mtm/service-cases',
    name: 'MtmServiceCases',
    component: MtmServiceCasesPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/mtm/service-cases/:id',
    name: 'MtmServiceCaseDetail',
    component: MtmServiceCaseDetailPage,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/mtm/service-cases/:id/interview',
    name: 'MtmInterviewForm',
    component: MtmInterviewFormPage,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/mtm/service-cases/:id/assessment',
    name: 'MtmAssessmentForm',
    component: MtmAssessmentFormPage,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/mtm/service-cases/:id/plan',
    name: 'MtmPlanForm',
    component: () => import('@/pages/MtmPlanFormPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/mtm/service-cases/:caseId/follow-ups/:followUpId',
    name: 'MtmFollowUpForm',
    component: () => import('@/pages/MtmFollowUpFormPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/medicines',
    name: 'Medicines',
    component: MedicinesPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/medicines/:id',
    name: 'MedicineDetail',
    component: () => import('@/pages/MedicineDetailPage.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/records',
    name: 'Records',
    component: RecordsPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/records/stats',
    name: 'RecordStats',
    component: RecordStatsPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/reminders',
    name: 'Reminders',
    component: ReminderList,
    meta: { requiresAuth: true },
  },
  {
    path: '/reminders/create',
    name: 'ReminderCreate',
    component: ReminderForm,
    meta: { requiresAuth: true },
  },
  {
    path: '/reminders/:id',
    name: 'ReminderDetail',
    component: ReminderDetail,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/reminders/:id/edit',
    name: 'ReminderEdit',
    component: ReminderForm,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/plans',
    name: 'Plans',
    component: PlansPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/medical-records',
    name: 'MedicalRecords',
    component: MedicalRecords,
    meta: { requiresAuth: true },
  },
  {
    path: '/medical-records/create',
    name: 'MedicalRecordCreate',
    component: MedicalRecordForm,
    meta: { requiresAuth: true },
  },
  {
    path: '/medical-records/:id',
    name: 'MedicalRecordDetail',
    component: MedicalRecordDetail,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/medical-records/:id/edit',
    name: 'MedicalRecordEdit',
    component: MedicalRecordForm,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/medical-records/statistics',
    name: 'MedicalRecordStatistics',
    component: MedicalRecordStatistics,
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/',
  },
]

/**
 * 创建路由实例
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// 路由守卫 - 检查认证状态
router.beforeEach(async (to, from, next) => {
  log('🔵 [Router] === Route Guard Started ===')
  log('🔵 [Router] Navigation from:', from.path, 'to:', to.path)
  log('🔵 [Router] Route name:', to.name)
  log('🔵 [Router] Route params:', to.params)
  log('🔵 [Router] Route query:', to.query)

  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)
  const hasPersistedAccessToken = !!localStorage.getItem('access_token')

  if (authStore.isAuthenticated && !hasPersistedAccessToken) {
    warn('🟡 [Router] 发现内存态已登录但本地令牌缺失，自动清理认证状态')
    authStore.clearTokens()
  }

  log('🔵 [Router] Auth store state:', {
    isAuthenticated: authStore.isAuthenticated,
    hasAccessToken: !!authStore.accessToken,
    hasRefreshToken: !!authStore.refreshToken,
    hasUser: !!authStore.user,
  })
  log('🔵 [Router] localStorage tokens:', {
    accessToken: !!localStorage.getItem('access_token'),
    refreshToken: !!localStorage.getItem('refresh_token'),
    userInfo: !!localStorage.getItem('user_info'),
  })
  log('🔵 [Router] Route requirements:', {
    requiresAuth,
    requiresGuest,
  })

  // 如果是从登录页跳转，给一个小延迟确保认证状态已更新
  if (from.path === '/login' && authStore.isAuthenticated) {
    log('🔵 [Router] 从登录页跳转，等待认证状态更新')
    await new Promise(resolve => setTimeout(resolve, 50))
    log('🔵 [Router] 认证状态更新完成')
  }

  log('🔵 [Router] 路由守卫检查:', {
    to: to.path,
    from: from.path,
    requiresAuth,
    requiresGuest,
    isAuthenticated: authStore.isAuthenticated,
  })

  // 如果需要认证但未登录
  if (requiresAuth && !authStore.isAuthenticated) {
    log('🔴 [Router] 需要认证但未登录，重定向到登录页')
    log('🔴 [Router] 重定向参数:', {
      path: '/login',
      query: { redirect: to.fullPath },
    })
    next({
      path: '/login',
      query: { redirect: to.fullPath },
    })
    return
  }

  // 如果需要访客状态但已登录
  if (requiresGuest && authStore.isAuthenticated) {
    log('🟡 [Router] 已登录用户访问访客页面，重定向到仪表板')
    next('/dashboard')
    return
  }

  // 如果访问根路径且已登录，重定向到仪表板
  if (to.path === '/' && authStore.isAuthenticated) {
    log('🟡 [Router] 已登录用户访问根路径，重定向到仪表板')
    next('/dashboard')
    return
  }

  // 其他情况正常通过
  log('🟢 [Router] 路由守卫检查通过，允许导航')
  log('🔵 [Router] === Route Guard Completed ===')
  next()
})

/**
 * 全局后置钩子
 * 处理页面标题等
 */
// 语音播报去重控制：避免同一路由短时间内重复播报
let lastSpokenRouteName: string | null = null
let lastSpokenTime = 0

router.afterEach(to => {
  // 设置页面标题
  const baseTitle = '用药提醒助手'
  const pageTitle = getPageTitle(String(to.name || ''))
  document.title = pageTitle ? `${pageTitle} - ${baseTitle}` : baseTitle

  // 页面主要作用语音播报
  try {
    const now = Date.now()
    const routeName = String(to.name || '')
    const purpose = getPagePurpose(routeName)

    // 条件：浏览器支持 + 已开启语音播报（由 useSpeech 内部控制）
    if (isSpeechSupported.value && purpose) {
      // 避免同一路由在15秒内重复播报
      const isSameRoute = lastSpokenRouteName === routeName
      const withinCooldown = now - lastSpokenTime < 15000
      if (isSameRoute && withinCooldown) {
        log(
          '[Router][Speech] 路由未变化或在冷却时间内，跳过页面用途播报'
        )
        return
      }

      const text = `当前页面：${pageTitle || baseTitle}。主要作用：${purpose}。`
      log('[Router][Speech] 页面用途播报:', {
        routeName,
        pageTitle,
        purpose,
      })
      speak(text, {
        rate: 0.8,
        category: 'route',
        priority: 'low',
        dedupeWindowMs: 15000,
        maxSegmentLength: 36,
      })
      lastSpokenRouteName = routeName
      lastSpokenTime = now
    }
  } catch (e) {
    warn('[Router][Speech] 页面用途播报失败', e)
  }
})

/**
 * 获取页面标题
 */
// 注意：标题与用途映射已移动到 utils/pageMeta 以避免重复与保证一致性

export default router
