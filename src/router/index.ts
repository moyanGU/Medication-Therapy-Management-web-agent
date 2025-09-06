import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 导入页面组件
import HomePage from '@/pages/HomePage.vue'
import WelcomePage from '../pages/WelcomePage.vue'
import LoginPage from '../pages/LoginPage.vue'
import Login from '../pages/Login.vue'
import RegisterPage from '../pages/RegisterPage.vue'
import Register from '../pages/Register.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import MedicinesPage from '../pages/MedicinesPage.vue'
import RecordsPage from '../pages/RecordsPage.vue'
import RemindersPage from '../pages/RemindersPage.vue'
import PlansPage from '../pages/PlansPage.vue'
import MedicalRecordsPage from '../pages/MedicalRecordsPage.vue'
import RecordStatsPage from '../pages/RecordStatsPage.vue'
import SettingsPage from '../pages/SettingsPage.vue'

// 提醒相关页面
import ReminderList from '@/pages/reminders/ReminderList.vue'
import ReminderForm from '@/pages/reminders/ReminderForm.vue'
import ReminderDetail from '@/pages/reminders/ReminderDetail.vue'

// 病历管理相关页面
import MedicalRecords from '@/pages/MedicalRecords.vue'
import MedicalRecordForm from '@/pages/MedicalRecordForm.vue'
import MedicalRecordDetail from '@/pages/MedicalRecordDetail.vue'
import MedicalRecordStatistics from '@/pages/MedicalRecordStatistics.vue'

/**
 * 路由配置
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { requiresAuth: false }
  },
  {
    path: '/welcome',
    name: 'Welcome',
    component: WelcomePage,
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/medicines',
    name: 'Medicines',
    component: MedicinesPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/medicines/:id',
    name: 'MedicineDetail',
    component: () => import('@/pages/MedicineDetailPage.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/records',
    name: 'Records',
    component: RecordsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/records/stats',
    name: 'RecordStats',
    component: RecordStatsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/reminders',
    name: 'Reminders',
    component: ReminderList,
    meta: { requiresAuth: true }
  },
  {
    path: '/reminders/create',
    name: 'ReminderCreate',
    component: ReminderForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/reminders/:id',
    name: 'ReminderDetail',
    component: ReminderDetail,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/reminders/:id/edit',
    name: 'ReminderEdit',
    component: ReminderForm,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/plans',
    name: 'Plans',
    component: PlansPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/medical-records',
    name: 'MedicalRecords',
    component: MedicalRecords,
    meta: { requiresAuth: true }
  },
  {
    path: '/medical-records/create',
    name: 'MedicalRecordCreate',
    component: MedicalRecordForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/medical-records/:id',
    name: 'MedicalRecordDetail',
    component: MedicalRecordDetail,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/medical-records/:id/edit',
    name: 'MedicalRecordEdit',
    component: MedicalRecordForm,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/medical-records/statistics',
    name: 'MedicalRecordStatistics',
    component: MedicalRecordStatistics,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
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
  }
})

// 路由守卫 - 检查认证状态
router.beforeEach(async (to, from, next) => {
  console.log('🔵 [Router] === Route Guard Started ===')
  console.log('🔵 [Router] Navigation from:', from.path, 'to:', to.path)
  console.log('🔵 [Router] Route name:', to.name)
  console.log('🔵 [Router] Route params:', to.params)
  console.log('🔵 [Router] Route query:', to.query)
  
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)
  
  console.log('🔵 [Router] Auth store state:', {
    isAuthenticated: authStore.isAuthenticated,
    hasAccessToken: !!authStore.accessToken,
    hasRefreshToken: !!authStore.refreshToken,
    user: authStore.user
  })
  console.log('🔵 [Router] localStorage tokens:', {
    accessToken: !!localStorage.getItem('access_token'),
    refreshToken: !!localStorage.getItem('refresh_token'),
    userInfo: !!localStorage.getItem('user_info')
  })
  console.log('🔵 [Router] Route requirements:', {
    requiresAuth,
    requiresGuest
  })
  
  // 如果是从登录页跳转，给一个小延迟确保认证状态已更新
  if (from.path === '/login' && authStore.isAuthenticated) {
    console.log('🔵 [Router] 从登录页跳转，等待认证状态更新')
    await new Promise(resolve => setTimeout(resolve, 50))
    console.log('🔵 [Router] 认证状态更新完成')
  }
  
  console.log('🔵 [Router] 路由守卫检查:', {
    to: to.path,
    from: from.path,
    requiresAuth,
    requiresGuest,
    isAuthenticated: authStore.isAuthenticated
  })
  
  // 如果需要认证但未登录
  if (requiresAuth && !authStore.isAuthenticated) {
    console.log('🔴 [Router] 需要认证但未登录，重定向到登录页')
    console.log('🔴 [Router] 重定向参数:', {
      path: '/login',
      query: { redirect: to.fullPath }
    })
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
    return
  }
  
  // 如果需要访客状态但已登录
  if (requiresGuest && authStore.isAuthenticated) {
    console.log('🟡 [Router] 已登录用户访问访客页面，重定向到仪表板')
    next('/dashboard')
    return
  }
  
  // 如果访问根路径且已登录，重定向到仪表板
  if (to.path === '/' && authStore.isAuthenticated) {
    console.log('🟡 [Router] 已登录用户访问根路径，重定向到仪表板')
    next('/dashboard')
    return
  }
  
  // 其他情况正常通过
  console.log('🟢 [Router] 路由守卫检查通过，允许导航')
  console.log('🔵 [Router] === Route Guard Completed ===')
  next()
})

/**
 * 全局后置钩子
 * 处理页面标题等
 */
router.afterEach((to) => {
  // 设置页面标题
  const baseTitle = '用药提醒助手'
  const pageTitle = getPageTitle(to.name as string)
  document.title = pageTitle ? `${pageTitle} - ${baseTitle}` : baseTitle
})

/**
 * 获取页面标题
 */
function getPageTitle(routeName: string): string {
  const titleMap: Record<string, string> = {
    Home: '首页',
    Welcome: '欢迎',
    Login: '登录',
    Register: '注册',
    Dashboard: '仪表板',
    Medicines: '药品管理',
    Records: '用药记录',
    RecordStats: '用药统计',
    Reminders: '用药提醒',
    ReminderCreate: '新建提醒',
    ReminderDetail: '提醒详情',
    ReminderEdit: '编辑提醒',
    Plans: '用药计划',
    MedicalRecords: '病历管理',
    MedicalRecordCreate: '新增病历',
    MedicalRecordDetail: '病历详情',
    MedicalRecordEdit: '编辑病历',
    MedicalRecordStatistics: '病历统计',
    Settings: '设置'
  }
  
  return titleMap[routeName] || ''
}

export default router
