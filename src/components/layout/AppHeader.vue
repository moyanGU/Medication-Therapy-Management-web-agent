<template>
  <header class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo和标题 -->
        <div class="flex items-center">
          <router-link to="/" class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 9.172V5L8 4z"></path>
              </svg>
            </div>
            <span class="text-xl font-bold text-gray-900">MTM-用药助手</span>
          </router-link>
        </div>

        <!-- 导航菜单 (桌面端) -->
        <nav class="hidden md:flex space-x-8" v-if="isAuthenticated">
          <router-link
            to="/dashboard"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/dashboard' }"
          >
            仪表板
          </router-link>
          <router-link
            to="/medicines"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/medicines' }"
          >
            药品管理
          </router-link>
          <router-link
            to="/records"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/records' }"
          >
            用药记录
          </router-link>
          <router-link
            to="/reminders"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/reminders' }"
          >
            用药提醒
          </router-link>
          <router-link
            to="/plans"
            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/plans' }"
          >
            用药计划
          </router-link>
        </nav>

        <!-- 用户菜单 -->
        <div class="flex items-center space-x-4">
          <!-- 通知图标 -->
          <button
            v-if="isAuthenticated"
            class="relative p-2 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-full"
            @click="toggleNotifications"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM10.5 3.75a6 6 0 0 1 6 6v2.25l2.25 2.25v.75H2.25v-.75L4.5 12V9.75a6 6 0 0 1 6-6z"></path>
            </svg>
            <!-- 通知小红点 -->
            <span v-if="hasUnreadNotifications" class="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white"></span>
          </button>

          <!-- 用户头像和菜单 -->
          <div v-if="isAuthenticated" class="relative">
            <button
              @click="toggleUserMenu"
              class="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
              <span class="hidden md:block text-sm font-medium text-gray-700">{{ userName || '用户' }}</span>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </button>

            <!-- 用户下拉菜单 -->
            <div
              v-if="showUserMenu"
              class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200"
              @click.stop
            >
              <router-link
                to="/settings"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                @click="showUserMenu = false"
              >
                个人设置
              </router-link>
              <router-link
                to="/medical-records"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                @click="showUserMenu = false"
              >
                就医记录
              </router-link>
              <hr class="my-1">
              <button
                @click="handleLogout"
                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                退出登录
              </button>
            </div>
          </div>

          <!-- 登录/注册按钮 (未登录时) -->
          <div v-else class="flex items-center space-x-3">
            <router-link
              to="/login"
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
            >
              登录
            </router-link>
            <router-link
              to="/register"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              注册
            </router-link>
          </div>

          <!-- 移动端菜单按钮 -->
          <button
            v-if="isAuthenticated"
            @click="toggleMobileMenu"
            class="md:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- 移动端导航菜单 -->
      <div v-if="showMobileMenu && isAuthenticated" class="md:hidden border-t border-gray-200 pt-4 pb-3">
        <div class="space-y-1">
          <router-link
            to="/dashboard"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/dashboard' }"
            @click="showMobileMenu = false"
          >
            仪表板
          </router-link>
          <router-link
            to="/medicines"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/medicines' }"
            @click="showMobileMenu = false"
          >
            药品管理
          </router-link>
          <router-link
            to="/records"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/records' }"
            @click="showMobileMenu = false"
          >
            用药记录
          </router-link>
          <router-link
            to="/reminders"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/reminders' }"
            @click="showMobileMenu = false"
          >
            用药提醒
          </router-link>
          <router-link
            to="/plans"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            :class="{ 'text-blue-600 bg-blue-50': $route.path === '/plans' }"
            @click="showMobileMenu = false"
          >
            用药计划
          </router-link>
        </div>
      </div>
    </div>

    <!-- 通知面板 -->
    <div
      v-if="showNotifications"
      class="absolute top-16 right-4 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
      @click.stop
    >
      <div class="p-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">通知</h3>
      </div>
      <div class="max-h-96 overflow-y-auto">
        <div v-if="notifications.length === 0" class="p-4 text-center text-gray-500">
          暂无通知
        </div>
        <div v-else>
          <div
            v-for="notification in notifications"
            :key="notification.id"
            class="p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
            @click="markAsRead(notification.id)"
          >
            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0">
                <div class="w-2 h-2 bg-blue-500 rounded-full mt-2" v-if="!notification.read"></div>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">{{ notification.title }}</p>
                <p class="text-sm text-gray-600 mt-1">{{ notification.message }}</p>
                <p class="text-xs text-gray-400 mt-2">{{ formatTime(notification.createdAt) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
// 新增：服务与类型
import { reminderService, type Reminder } from '@/services/reminderService'
import { medicineApi } from '@/api/medicine'
import type { Medicine } from '@/types/medicine'

/**
 * 应用头部组件
 * 包含导航菜单、用户信息、通知等功能
 */

const { isAuthenticated, user, logout } = useAuth()

// 组件状态
const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const showNotifications = ref(false)

// 计算属性
const userName = computed(() => user.value?.username || '')

// 通知项类型与数据
interface NotificationItem {
  id: string
  title: string
  message: string
  read: boolean
  createdAt: string
}

// 从各来源抓取通知
const loadingNotifications = ref(false)
const fetchNotifications = async () => {
  if (!isAuthenticated.value) return
  try {
    loadingNotifications.value = true
    // Option A: 6个月有效期 = 180 天
    const SIX_MONTHS_DAYS = 180

    const results = await Promise.allSettled([
      reminderService.getTodayReminders(),
      medicineApi.getExpiredMedicines(),
      // 低库存
      medicineApi.getLowStockMedicines(),
      // 获取药品列表，前端计算 180 天内到期并生成通知；同时稳健解析后端响应的双层 data 结构，增加关键日志。
      medicineApi.getMedicines({ page_size: 1000, ordering: 'expiry_date' })
    ])

    const now = new Date().toISOString()
    const tmp: NotificationItem[] = []

    // 工具：稳健提取列表数据（兼容 {success,data: T} 与 {success,data:{results:[]}} 等）
    const pickArray = (resp: any): any[] => {
      const d = resp?.data ?? resp
      if (Array.isArray(d)) return d
      if (Array.isArray(d?.results)) return d.results
      if (Array.isArray(d?.data)) return d.data
      if (Array.isArray(d?.data?.results)) return d.data.results
      return []
    }

    // 工具：计算距今天的天数（正数表示还有N天，负数表示已过期N天）
    const daysUntil = (iso?: string | null) => {
      if (!iso) return Number.NaN
      const end = new Date(iso)
      if (isNaN(end.getTime())) return Number.NaN
      const nowDate = new Date()
      const diffMs = end.getTime() - nowDate.getTime()
      return Math.ceil(diffMs / (1000 * 60 * 60 * 24))
    }

    // 今日用药提醒
    {
      const r = results[0]
      if (r.status === 'fulfilled' && r.value?.success) {
        const list = pickArray(r.value) as Reminder[]
        console.log('🔔 [通知] 今日提醒数:', list.length)
        list.forEach((rem, idx) => {
          const time = rem.reminder_time?.slice(0,5) || ''
          const medName = rem.medicine?.name || '药品'
          const dose = rem.dosage ? `${rem.dosage}${unitLabel(rem.dosage_unit)}` : ''
          tmp.push({
            id: `rem-${rem.id}-${idx}`,
            title: '用药提醒',
            message: `今天${time} 服用 ${medName}${dose ? ` · ${dose}` : ''}`,
            read: false,
            createdAt: rem.last_reminded_at || now
          })
        })
      }
    }

    // 已过期药品
    {
      const r = results[1]
      if (r.status === 'fulfilled' && r.value?.success) {
        const list = pickArray(r.value) as Medicine[]
        console.log('🔔 [通知] 已过期药品数:', list.length)
        list.forEach((m, idx) => {
          tmp.push({
            id: `exp-${m.id}-${idx}`,
            title: '药品过期提醒',
            message: `${m.name} 已过期${m.expiry_date ? `（有效期：${formatDateYMD(m.expiry_date)}）` : ''}`,
            read: false,
            createdAt: now
          })
        })
      }
    }

    // 库存不足药品
    {
      const r = results[2]
      if (r.status === 'fulfilled' && r.value?.success) {
        const list = pickArray(r.value) as Medicine[]
        console.log('🔔 [通知] 库存不足药品数:', list.length)
        list.forEach((m, idx) => {
          tmp.push({
            id: `low-${m.id}-${idx}`,
            title: '库存不足提醒',
            message: `${m.name} 库存不足（当前${m.quantity}），请尽快补购`,
            read: false,
            createdAt: now
          })
        })
      }
    }

    // 6个月有效期提醒（Option A：days=180，由前端基于 expiry_date 计算）
    {
      const r = results[3]
      if (r.status === 'fulfilled' && r.value?.success) {
        const raw = pickArray(r.value) as Medicine[]
        // 过滤出 0..180 天内到期的药品
        const list = raw.filter(m => {
          const d = daysUntil(m.expiry_date || null)
          return Number.isFinite(d) && d >= 0 && d <= SIX_MONTHS_DAYS
        })
        console.log('🔔 [通知] 6个月内到期药品数:', list.length)
        list.forEach((m, idx) => {
          const d = daysUntil(m.expiry_date || null)
          const suffix = Number.isFinite(d) ? `（约${d}天后过期）` : ''
          tmp.push({
            id: `val6m-${m.id}-${idx}`,
            title: '6个月有效期提醒',
            message: `${m.name} ${suffix}`,
            read: false,
            createdAt: now
          })
        })
      }
    }

    // 按时间/重要性可排序（简单按创建时间降序）
    notifications.value = tmp.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
  } catch (e) {
    // 失败不打断UI，仅记录
    console.error('[通知] 获取失败:', e)
  } finally {
    loadingNotifications.value = false
  }
}

/**
 * 切换用户菜单
 */
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  showNotifications.value = false
}

/**
 * 切换移动端菜单
 */
const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
  showUserMenu.value = false
  showNotifications.value = false
}

/**
 * 切换通知面板（打开时拉取最新数据）
 */
const toggleNotifications = async () => {
  const next = !showNotifications.value
  showNotifications.value = next
  showUserMenu.value = false
  if (next) {
    await fetchNotifications()
  }
}

/**
 * 处理登出
 */
const handleLogout = async () => {
  await logout()
  showUserMenu.value = false
}

/**
 * 标记通知为已读
 */
const markAsRead = (id: string | number) => {
  const nid = String(id)
  const notification = notifications.value.find(n => n.id === nid)
  if (notification) {
    notification.read = true
  }
}

/**
 * 格式化时间
 */
const formatTime = (timeString: string) => {
  const time = new Date(timeString)
  const now = new Date()
  const diff = now.getTime() - time.getTime()
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return `${Math.floor(diff / 86400000)}天前`
  }
}

/**
 * 点击外部关闭菜单
 */
const handleClickOutside = (event: Event) => {
  const target = event.target as Element
  if (!target.closest('.relative')) {
    showUserMenu.value = false
    showNotifications.value = false
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>