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
const logError = (message: string, error?: unknown) => {
  if (isDebug && error !== undefined) {
    console.error(message, error)
    return
  }
  console.error(message)
}

log('=== Application Starting ===')

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

log('=== Imports Loaded ===')

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

log('应用启动，各项服务初始化完成:', {
  isAuthenticated: authStore.isAuthenticated,
  hasUser: !!authStore.user,
  remindersTotal: reminderStore.totalReminders,
  remindersActive: reminderStore.totalActiveReminders,
  notificationSupported: notificationService.isSupported.value,
  notificationPermission: notificationService.permission.value,
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
      log(
        '[PWA][Storage] 使用量/配额:',
        usage,
        quota,
        `(${(((usage || 0) / (quota || 1)) * 100).toFixed(2)}%)`
      )
    }
    if ('caches' in window) {
      const cacheNames = await caches.keys()
      log('[PWA][Cache] 当前缓存列表:', cacheNames)
      for (const name of cacheNames) {
        const cache = await caches.open(name)
        const keys = await cache.keys()
        log(`[PWA][Cache] ${name} 条目数:`, keys.length)
      }
    }
  } catch (err) {
    warn('[PWA] 存储/缓存占用日志失败', err)
  }
}

// 注册 Service Worker，并提供更新提示
if ('serviceWorker' in navigator) {
  if (import.meta.env.PROD) {
    const updateSW = registerSW({
      immediate: true,
      onNeedRefresh() {
        log('[PWA] 有新版本可用，触发全局事件供 UI 展示更新横幅')
        ;(window as any).__pwa_update__ = updateSW
        window.dispatchEvent(new CustomEvent('pwa:need-refresh'))
      },
      onOfflineReady() {
        log('[PWA] 离线资源已就绪，可以在离线环境使用')
        logStorageAndCacheUsage()
        notificationService.requestPermission().then(p => {
          log('[PWA] 通知权限状态:', p)
        })
      },
      onRegisteredSW(swUrl, registration) {
        log('[PWA] SW 已注册:', swUrl, registration)
      },
      onRegisterError(error) {
        logError('[PWA] SW 注册失败', error)
      },
    })
  } else {
    ;(async () => {
      try {
        const registrations = await navigator.serviceWorker.getRegistrations()
        const staleRegistrations = registrations.filter(registration => {
          const scriptUrl = registration.active?.scriptURL || registration.scope
          return !scriptUrl.includes('/dev-sw.js')
        })
        await Promise.all(
          staleRegistrations.map(registration => registration.unregister())
        )
        if ('caches' in window) {
          const cacheNames = await caches.keys()
          const staleCacheNames = cacheNames.filter(
            name => !name.includes('vite-plugin-pwa')
          )
          await Promise.all(staleCacheNames.map(name => caches.delete(name)))
        }
        log('[PWA][DEV] 已清理历史 SW 与缓存', {
          registrationCount: staleRegistrations.length,
        })
        const registration = await navigator.serviceWorker.register(
          '/dev-sw.js?dev-sw',
          { type: 'module' }
        )
        log('[PWA][DEV] SW 已注册:', registration)
      } catch (error) {
        logError('[PWA][DEV] SW 清理或注册失败', error)
      }
    })()
  }
}

// 挂载应用
app.mount('#app')
