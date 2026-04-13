<template>
  <aside
    class="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0"
    :class="{
      'translate-x-0': isOpen,
      '-translate-x-full': !isOpen,
    }"
  >
    <!-- 侧边栏头部 -->
    <div
      class="flex items-center justify-between h-16 px-6 border-b border-gray-200"
    >
      <div class="flex items-center space-x-3">
        <div
          class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center"
        >
          <svg
            class="w-5 h-5 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 9.172V5L8 4z"
            ></path>
          </svg>
        </div>
        <span class="text-lg font-semibold text-gray-900">MTM-用药助手</span>
      </div>

      <!-- 关闭按钮 (移动端) -->
      <button
        @click="$emit('close')"
        class="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
      >
        <svg
          class="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          ></path>
        </svg>
      </button>
    </div>

    <!-- 导航菜单 -->
    <nav class="mt-6 px-3">
      <div class="space-y-1">
        <!-- 仪表板 -->
        <router-link
          to="/dashboard"
          class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
          :class="
            isActive('/dashboard')
              ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          "
          @click="$emit('navigate')"
        >
          <svg
            class="mr-3 h-5 w-5"
            :class="
              isActive('/dashboard')
                ? 'text-blue-500'
                : 'text-gray-400 group-hover:text-gray-500'
            "
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"
            ></path>
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6a2 2 0 01-2 2H10a2 2 0 01-2-2V5z"
            ></path>
          </svg>
          仪表板
        </router-link>

        <!-- 药品管理 -->
        <router-link
          to="/medicines"
          class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
          :class="
            isActive('/medicines')
              ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          "
          @click="$emit('navigate')"
        >
          <svg
            class="mr-3 h-5 w-5"
            :class="
              isActive('/medicines')
                ? 'text-blue-500'
                : 'text-gray-400 group-hover:text-gray-500'
            "
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 9.172V5L8 4z"
            ></path>
          </svg>
          药品管理
        </router-link>

        <!-- 用药记录 -->
        <router-link
          to="/records"
          class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
          :class="
            isActive('/records')
              ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          "
          @click="$emit('navigate')"
        >
          <svg
            class="mr-3 h-5 w-5"
            :class="
              isActive('/records')
                ? 'text-blue-500'
                : 'text-gray-400 group-hover:text-gray-500'
            "
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
            ></path>
          </svg>
          用药记录
        </router-link>

        <!-- 用药提醒 -->
        <router-link
          to="/reminders"
          class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
          :class="
            isActive('/reminders')
              ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          "
          @click="$emit('navigate')"
        >
          <svg
            class="mr-3 h-5 w-5"
            :class="
              isActive('/reminders')
                ? 'text-blue-500'
                : 'text-gray-400 group-hover:text-gray-500'
            "
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 17h5l-5 5v-5zM10.5 3.75a6 6 0 0 1 6 6v2.25l2.25 2.25v.75H2.25v-.75L4.5 12V9.75a6 6 0 0 1 6-6z"
            ></path>
          </svg>
          用药提醒
          <span
            v-if="reminderCount > 0"
            class="ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
          >
            {{ reminderCount }}
          </span>
        </router-link>

        <!-- 用药计划 -->
        <router-link
          to="/plans"
          class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
          :class="
            isActive('/plans')
              ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          "
          @click="$emit('navigate')"
        >
          <svg
            class="mr-3 h-5 w-5"
            :class="
              isActive('/plans')
                ? 'text-blue-500'
                : 'text-gray-400 group-hover:text-gray-500'
            "
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            ></path>
          </svg>
          用药计划
        </router-link>

        <!-- 分割线 -->
        <div class="border-t border-gray-200 my-4"></div>

        <!-- 就医记录 -->
        <router-link
          to="/medical-records"
          class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
          :class="
            isActive('/medical-records')
              ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          "
          @click="$emit('navigate')"
        >
          <svg
            class="mr-3 h-5 w-5"
            :class="
              isActive('/medical-records')
                ? 'text-blue-500'
                : 'text-gray-400 group-hover:text-gray-500'
            "
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            ></path>
          </svg>
          就医记录
        </router-link>

        <!-- 个人设置 -->
        <router-link
          to="/settings"
          class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
          :class="
            isActive('/settings')
              ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          "
          @click="$emit('navigate')"
        >
          <svg
            class="mr-3 h-5 w-5"
            :class="
              isActive('/settings')
                ? 'text-blue-500'
                : 'text-gray-400 group-hover:text-gray-500'
            "
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            ></path>
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            ></path>
          </svg>
          个人设置
        </router-link>
      </div>
    </nav>

    <!-- 侧边栏底部 -->
    <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
      <!-- 用户信息 -->
      <div class="flex items-center space-x-3 mb-3">
        <div
          class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center"
        >
          <svg
            class="w-5 h-5 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            ></path>
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">
            {{ userName || '用户' }}
          </p>
          <p class="text-xs text-gray-500 truncate">
            {{ userEmail || '未设置邮箱' }}
          </p>
        </div>
      </div>

      <!-- 登出按钮 -->
      <button
        @click="handleLogout"
        class="w-full flex items-center justify-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
      >
        <svg
          class="mr-2 h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
          ></path>
        </svg>
        退出登录
      </button>
    </div>
  </aside>

  <!-- 遮罩层 (移动端) -->
  <div
    v-if="isOpen"
    class="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
    @click="$emit('close')"
  ></div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useReminderStore } from '@/stores/reminder'

/**
 * 应用侧边栏组件
 * 用于仪表板等需要侧边导航的页面
 */

// Props
interface Props {
  isOpen: boolean
}

defineProps<Props>()

// Emits
defineEmits<{
  close: []
  navigate: []
}>()

const route = useRoute()
const { user, logout } = useAuth()
const reminderStore = useReminderStore()

// 计算属性
const userName = computed(() => user.value?.username || '')
const userEmail = computed(() => user.value?.email || '')

// 今日提醒数量
const reminderCount = computed(() => {
  return reminderStore.todayReminders.length
})

// 组件挂载时获取今日提醒
onMounted(async () => {
  try {
    await reminderStore.fetchTodayReminders()
  } catch (error) {
    console.error('获取今日提醒失败:', error)
  }
})

/**
 * 检查路由是否激活
 */
const isActive = (path: string) => {
  return route.path === path
}

/**
 * 处理登出
 */
const handleLogout = async () => {
  await logout()
}
</script>
