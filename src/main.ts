console.log('=== Application Starting ===')

import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { pinia } from './stores'
import { useAuthStore } from './stores/auth'
import { useReminderStore } from './stores/reminder'
import { getGlobalNotification } from './composables/useNotification'

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

// 挂载应用
app.mount('#app')
