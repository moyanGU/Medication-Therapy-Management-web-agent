console.log('=== Application Starting ===')

import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { pinia } from './stores'
import { useAuthStore } from './stores/auth'
import { useReminderStore } from './stores/reminder'
import { getGlobalNotification } from './composables/useNotification'

// PWA 注册与更新提示
import { registerSW } from 'virtual:pwa-register'

console.log('=== Imports Loaded ===')

// 创建Vue应用实例
const app = createApp(App)

// 使用Pinia状态管理
app.use(pinia)

// 使用路由
app.use(router)

// 初始化认证状态
const authStore = useAuthStore()
authStore.initializeAuth()

// 初始化提醒store
const reminderStore = useReminderStore()

// 初始化通知服务
const notificationService = getGlobalNotification()

console.log('应用启动，各项服务初始化完成:', {
  isAuthenticated: authStore.isAuthenticated,
  user: authStore.user,
  notificationSupported: notificationService.isSupported.value,
  notificationPermission: notificationService.permission.value
})

/**
 * 监控存储与缓存占用情况，便于后续容量治理
 * - 打印 storage(used/quota)
 * - 打印 caches 中缓存条目数量（按已知缓存名称）
 */
async function logStorageAndCacheUsage() {
  try {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      const { usage, quota } = await navigator.storage.estimate()
      console.log('[PWA][Storage] 使用量/配额:', usage, quota, `(${(((usage || 0) / (quota || 1)) * 100).toFixed(2)}%)`)
    }
    if ('caches' in window) {
      const cacheNames = await caches.keys()
      console.log('[PWA][Cache] 当前缓存列表:', cacheNames)
      for (const name of cacheNames) {
        const cache = await caches.open(name)
        const keys = await cache.keys()
        console.log(`[PWA][Cache] ${name} 条目数:`, keys.length)
      }
    }
  } catch (err) {
    console.warn('[PWA] 存储/缓存占用日志失败:', err)
  }
}

// 注册 Service Worker，并提供更新提示
const updateSW = registerSW({
  immediate: true,
  onNeedRefresh() {
    console.log('[PWA] 有新版本可用，触发全局事件供 UI 展示更新横幅')
    // 注入全局更新函数，供 UI 调用
    ;(window as any).__pwa_update__ = updateSW
    // 分发全局事件，AppHeader 监听后显示更新横幅
    window.dispatchEvent(new CustomEvent('pwa:need-refresh'))
  },
  onOfflineReady() {
    console.log('[PWA] 离线资源已就绪，可以在离线环境使用')
    // 离线就绪后记录一次占用情况
    logStorageAndCacheUsage()
    // 可选：提醒用户通知权限，便于后续安装/更新提示
    notificationService.requestPermission().then((p) => {
      console.log('[PWA] 通知权限状态:', p)
    })
  },
  onRegisteredSW(swUrl, registration) {
    console.log('[PWA] SW 已注册:', swUrl, registration)
  },
  onRegisterError(error) {
    console.error('[PWA] SW 注册失败:', error)
  }
})

// 挂载应用
app.mount('#app')
