<template>
  <header class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- PWA 更新横幅 -->
      <div v-if="showUpdateBanner" class="bg-blue-50 border-b border-blue-200 text-blue-800 text-sm px-4 py-2 flex justify-between items-center">
        <span>发现新版本，点击更新以应用最新功能。</span>
        <div class="space-x-2">
          <button @click="applyUpdate" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded">更新</button>
          <button @click="showUpdateBanner = false" class="text-blue-600 px-3 py-1">稍后</button>
        </div>
      </div>
      <!-- PWA 安装横幅（Android Chrome 等支持 beforeinstallprompt 的浏览器） -->
      <div v-if="showInstallBanner" class="bg-green-50 border-b border-green-200 text-green-800 text-sm px-4 py-2 flex justify-between items-center">
        <span>将 MTM-用药助手 安装到设备，获得类原生体验。</span>
        <div class="space-x-2">
          <button @click="triggerInstall" class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded">安装</button>
          <button @click="showInstallBanner = false" class="text-green-600 px-3 py-1">稍后</button>
        </div>
      </div>

      <!-- iOS 安装引导横幅（Safari 不支持 beforeinstallprompt） -->
      <div v-if="showIosInstallGuide" class="bg-amber-50 border-b border-amber-200 text-amber-800 text-sm px-4 py-2 flex justify-between items-start">
        <span>
          iPhone/iPad 安装指引：
          1) 使用 Safari 打开；
          2) 点击底部“分享”按钮；
          3) 选择“添加到主屏幕”；
          4) 添加后即可以独立应用方式使用。
        </span>
        <button @click="showIosInstallGuide = false" class="text-amber-700 px-3 py-1">知道了</button>
      </div>
      <div class="flex justify之间 items-center h-16">
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
          <!-- 老年人模式快速开关（所有用户可见） -->
          <button
            class="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center space-x-2"
            @click="handleToggleSenior"
            :aria-pressed="isSenior"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6M12 9v6M4 6h16M4 18h16" />
            </svg>
            <span class="text-sm font-medium">{{ isSenior ? '老年人模式：开' : '老年人模式：关' }}</span>
          </button>
          <!-- 语音播报开关（所有用户可见） -->
          <button
            class="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center space-x-2 disabled:opacity-50"
            :disabled="!isSpeechSupported"
            @click="handleToggleSpeech"
            :aria-pressed="isSpeechEnabled"
            :title="!isSpeechSupported ? '当前浏览器不支持语音播报' : ''"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5a1 1 0 011 1v2a6 6 0 016 6h2a1 1 0 110 2h-2a6 6 0 01-6 6v2a1 1 0 11-2 0v-2a6 6 0 01-6-6H3a1 1 0 110-2h2a6 6 0 016-6V6a1 1 0 011-1z" />
            </svg>
            <span class="text-sm font-medium">{{ isSpeechEnabled ? '语音播报：开' : '语音播报：关' }}</span>
          </button>
          <!-- 朗读当前页面标题（仅在开启时显示） -->
          <button
            v-if="isSpeechEnabled"
            class="px-2 py-1 rounded-md text-gray-700 bg-gray-100 hover:bg-gray-200 text-sm"
            @click="handleSpeakTitle"
            title="朗读当前页面标题"
          >朗读</button>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useTheme } from '@/composables/useTheme'
import useSpeech from '@/composables/useSpeech'
import { getPageTitle, getPagePurpose } from '@/utils/pageMeta'
// 新增：通知服务
import { getGlobalNotification } from '@/composables/useNotification'
// 新增：服务与类型
import { reminderService, type Reminder } from '@/services/reminderService'
import { medicineApi } from '@/api/medicine'
import type { Medicine } from '@/types/medicine'

/**
 * 应用头部组件
 * 包含导航菜单、用户信息、通知等功能
 */

const { isAuthenticated, user, logout } = useAuth()
const notificationService = getGlobalNotification()
// 主题与老年人模式
const { isSenior, toggleSenior } = useTheme()
// 语音播报
const { isSpeechEnabled, isSpeechSupported, toggleSpeech, speak } = useSpeech()

// 语音播报：到期提醒自动播报的定时器与去重集合
let speechReminderTimer: any = null
const spokenTodayKeys = new Set<string>()
let lastSpokenDateKey: string | null = null

/**
 * 映射用餐时机文字
 */
const mealTimingLabel = (timing?: string | null): string => {
  const map: Record<string, string> = {
    before_meal: '饭前',
    after_meal: '饭后',
    with_meal: '随餐',
    anytime: '任意时间',
  }
  if (!timing) return ''
  const k = String(timing).toLowerCase()
  return map[k] ?? ''
}

/**
 * 单位标签映射（与通知模块一致）
 */
const unitLabelSpeech = (unit?: string | null): string => {
  const map: Record<string, string> = {
    mg: 'mg',
    g: 'g',
    ml: 'ml',
    tablet: '片',
    capsule: '粒',
    drop: '滴',
    patch: '贴',
    puff: '喷',
  }
  if (!unit) return ''
  const key = String(unit).toLowerCase()
  return map[key] ?? unit
}

/**
 * 解析提醒时间为今天的具体时间
 */
const parseReminderTimeToday = (timeStr?: string): Date | null => {
  if (!timeStr) return null
  const now = new Date()
  const parts = timeStr.split(':').map(p => parseInt(p, 10))
  const h = parts[0] ?? 0
  const m = parts[1] ?? 0
  const s = parts[2] ?? 0
  const d = new Date(now)
  d.setHours(h, m, s, 0)
  return isNaN(d.getTime()) ? null : d
}

/**
 * 判断提醒在今天是否需要播报（时间窗口：[-1, +2] 分钟）
 */
const isDueNow = (rem: Reminder): boolean => {
  if (!rem.is_active) return false
  // 日期范围判断
  const today = new Date()
  const y = today.getFullYear()
  const m = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  const todayStr = `${y}-${m}-${day}`
  const sd = rem.start_date ? new Date(rem.start_date) : null
  const ed = rem.end_date ? new Date(rem.end_date) : null
  const td = new Date(todayStr)
  if (sd && sd > td) return false
  if (ed && ed < td) return false

  // 时间窗口判断
  const scheduled = parseReminderTimeToday(rem.reminder_time)
  if (!scheduled) return false
  const diffMs = scheduled.getTime() - today.getTime()
  const beforeWindowMs = -1 * 60 * 1000 // 提前1分钟
  const afterWindowMs = 2 * 60 * 1000   // 延后2分钟
  return diffMs >= beforeWindowMs && diffMs <= afterWindowMs
}

/**
 * 朗读单条提醒
 */
const speakReminder = (rem: Reminder) => {
  if (!isSpeechSupported.value || !isSpeechEnabled.value) return
  const medName = rem.medicine_name
    || (typeof rem.medicine === 'object' && rem.medicine ? (rem.medicine.name ?? '药品') : '药品')
  const dose = rem.dosage ? `${rem.dosage}${unitLabelSpeech(rem.dosage_unit)}` : ''
  const meal = mealTimingLabel(rem.meal_timing)
  const title = rem.title || '用药提醒'
  const parts = [
    `${title}：到吃药时间了`,
    medName ? `${medName}` : '',
    dose ? `${dose}` : '',
    meal ? `${meal}` : '',
  ].filter(Boolean)
  const text = parts.join('，')
  console.log('[Speech] 自动播报提醒:', text)
  speak(text, 0.8)
}

/**
 * 自动轮询并播报到期提醒（仅在页面可见且已登录时进行）
 */
const pollSpeakDueReminders = async () => {
  try {
    if (!isAuthenticated.value) return
    if (!isSpeechSupported.value || !isSpeechEnabled.value) return
    if (typeof document !== 'undefined' && document.visibilityState !== 'visible') return

    // 日期切换时清理去重集合
    const now = new Date()
    const y = now.getFullYear()
    const m = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    const todayKey = `${y}-${m}-${day}`
    if (lastSpokenDateKey !== todayKey) {
      spokenTodayKeys.clear()
      lastSpokenDateKey = todayKey
    }

    const resp = await reminderService.getTodayReminders()
    const list = Array.isArray(resp?.data) ? resp.data : (Array.isArray((resp as any)?.data?.data) ? (resp as any).data.data : [])
    if (!Array.isArray(list)) return

    list.forEach(rem => {
      if (!isDueNow(rem)) return
      const key = `${todayKey}_${rem.id}_${(rem.reminder_time || '').slice(0,5)}`
      if (spokenTodayKeys.has(key)) return
      spokenTodayKeys.add(key)
      speakReminder(rem)
    })
  } catch (e) {
    console.warn('[Speech] 轮询播报失败:', e)
  }
}

/**
 * 切换老年人模式并打印日志
 */
const handleToggleSenior = () => {
  console.log('[Header] 用户点击切换老年人模式, 当前状态 =', isSenior.value)
  toggleSenior()
}

/**
 * 切换语音播报
 */
const handleToggleSpeech = () => {
  if (!isSpeechSupported.value) {
    console.warn('[Header] 浏览器不支持 SpeechSynthesis')
    return
  }
  console.log('[Header] 用户点击切换语音播报, 当前状态 =', isSpeechEnabled.value)
  toggleSpeech()
}

/**
 * 朗读当前页面标题与主要作用
 * 说明：为满足老年用户的理解需求，除了页面标题，还播报当前页面的主要用途
 */
const route = useRoute()
const handleSpeakTitle = () => {
  if (!isSpeechSupported.value || !isSpeechEnabled.value) return
  const name = String(route.name || '')
  const title = getPageTitle(name) || (document.title || 'MTM-用药助手')
  const purpose = getPagePurpose(name)
  const text = purpose ? `当前页面：${title}。主要作用：${purpose}。` : `当前页面：${title}`
  speak(text, 0.8)
}

// 组件状态
const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const showNotifications = ref(false)

// 新增：PWA 横幅状态（Android 安装 + 通用更新提示）
const showUpdateBanner = ref(false)
const showInstallBanner = ref(false)
let deferredPrompt: any = null

// 新增：iOS 安装引导（Safari 不支持 beforeinstallprompt，只能通过“分享 -> 添加到主屏幕”）
const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent)
// iOS 已安装判断：iOS Safari 安装后 (navigator as any).standalone 为 true；其他浏览器可用 display-mode 媒体查询
const isStandalone = window.matchMedia('(display-mode: standalone)').matches || (navigator as any).standalone === true
const showIosInstallGuide = ref(false)

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

/**
 * 通知列表状态
 */
const notifications = ref<NotificationItem[]>([])

/**
 * 是否存在未读通知
 * 基于通知列表中 read 字段计算
 */
const hasUnreadNotifications = computed(() => notifications.value.some(n => !n.read))

// PWA 事件处理
function handleBeforeInstallPrompt(event: Event) {
  console.log('[PWA] beforeinstallprompt 触发')
  // 阻止自动弹窗，改为我们自定义横幅控制
  event.preventDefault()
  deferredPrompt = event as any
  showInstallBanner.value = true
}

function handleAppInstalled() {
  console.log('[PWA] appinstalled: 应用已安装')
  showInstallBanner.value = false
  deferredPrompt = null
  // 前台通知（如果权限允许）
  notificationService.showNotification('MTM-用药助手已安装', {
    body: '已添加到设备，支持离线使用',
    icon: '/favicon.svg',
  })
}

function handlePwaNeedRefresh() {
  console.log('[PWA] need-refresh: 显示更新横幅')
  showUpdateBanner.value = true
}

function applyUpdate() {
  const fn = (window as any).__pwa_update__
  if (typeof fn === 'function') {
    console.log('[PWA] 用户点击更新，执行 skipWaiting + reload')
    fn(true)
  } else {
    console.warn('[PWA] 更新函数不可用')
  }
  showUpdateBanner.value = false
}

function triggerInstall() {
  if (!deferredPrompt) {
    console.warn('[PWA] 暂无安装事件')
    return
  }
  ;(deferredPrompt as any).prompt()
  ;(deferredPrompt as any).userChoice?.then((choice: any) => {
    console.log('[PWA] 安装选择:', choice)
    deferredPrompt = null
    showInstallBanner.value = false
  })
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

    /**
     * 单位标签映射
     * 将后端返回或存储的单位代码转换为可读中文/符号
     */
    const unitLabel = (unit?: string | null): string => {
      const map: Record<string, string> = {
        mg: 'mg',
        g: 'g',
        ml: 'ml',
        tablet: '片',
        capsule: '粒',
        drop: '滴',
        patch: '贴',
        puff: '喷',
      }
      if (!unit) return ''
      const key = String(unit).toLowerCase()
      return map[key] ?? unit
    }

    /**
     * 格式化日期为 YYYY-MM-DD
     */
    const formatDateYMD = (d?: string | Date | null): string => {
      if (!d) return ''
      const date = typeof d === 'string' ? new Date(d) : d
      if (isNaN(date.getTime())) return ''
      const y = date.getFullYear()
      const m = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${y}-${m}-${day}`
    }

    // 今日用药提醒
    {
      const r = results[0]
      if (r.status === 'fulfilled' && r.value?.success) {
        const list = pickArray(r.value) as Reminder[]
        console.log('🔔 [通知] 今日提醒数:', list.length)
        list.forEach((rem, idx) => {
          const time = rem.reminder_time?.slice(0,5) || ''
          // medicine 可能是 number（ID）或对象，这里进行类型收窄，避免 TS 报错
          // 优先使用后端派生字段 medicine_name，其次再从对象中读取 name
          const medName = rem.medicine_name
            || (typeof rem.medicine === 'object' && rem.medicine ? (rem.medicine.name ?? '药品') : '药品')
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
  // 监听 PWA 事件
  window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt as EventListener)
  window.addEventListener('appinstalled', handleAppInstalled as EventListener)
  window.addEventListener('pwa:need-refresh', handlePwaNeedRefresh as EventListener)

  // iOS：在未安装且使用 Safari 的情况下，显示安装引导横幅
  const isSafariOnIOS = isIOS && /Safari/i.test(navigator.userAgent) && !/CriOS|FxiOS|EdgiOS/i.test(navigator.userAgent)
  if (isSafariOnIOS && !isStandalone) {
    console.log('[PWA][iOS] Safari 检测到未安装，显示引导横幅')
    showIosInstallGuide.value = true
  }

  // 初始化语音播报轮询（根据开关即时启动/停止）
  watch([isSpeechEnabled, isSpeechSupported, isAuthenticated], ([enabled, supported, authed]) => {
    // 停止已有定时器
    if (speechReminderTimer) {
      clearInterval(speechReminderTimer)
      speechReminderTimer = null
    }
    if (enabled && supported && authed) {
      console.log('[Speech] 启动到期提醒自动播报轮询（每60秒）')
      // 立即执行一次，然后每60秒轮询
      pollSpeakDueReminders()
      speechReminderTimer = setInterval(() => {
        pollSpeakDueReminders()
      }, 60000)
    } else {
      console.log('[Speech] 自动播报未启用或不支持，轮询已停止')
    }
  }, { immediate: true })
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt as EventListener)
  window.removeEventListener('appinstalled', handleAppInstalled as EventListener)
  window.removeEventListener('pwa:need-refresh', handlePwaNeedRefresh as EventListener)
  if (speechReminderTimer) {
    clearInterval(speechReminderTimer)
    speechReminderTimer = null
  }
})
</script>