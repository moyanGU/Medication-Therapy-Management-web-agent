<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 主要内容区域 -->
    <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- 欢迎信息 -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-2">欢迎回来！</h2>
        <p class="text-gray-600">今天是 {{ currentDate }}，请选择您需要的功能</p>
      </div>

      <!-- 快捷统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-2 bg-blue-100 rounded-lg">
              <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 7.172V5L8 4z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">药品总数</p>
              <p class="text-2xl font-semibold text-gray-900">{{ medicineStats?.total_medicines ?? 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 rounded-lg">
              <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">今日提醒</p>
              <p class="text-2xl font-semibold text-gray-900">{{ todayReminders?.length ?? 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-2 bg-yellow-100 rounded-lg">
              <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">即将过期</p>
              <p class="text-2xl font-semibold text-gray-900">{{ medicineStats?.expiring_soon_count ?? 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-2 bg-purple-100 rounded-lg">
              <svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">用药计划</p>
              <p class="text-2xl font-semibold text-gray-900">{{ activeReminders?.length ?? 0 }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 功能导航网格 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- 药品管理 -->
        <router-link
          to="/medicines"
          class="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200 p-6 group"
        >
          <div class="flex items-center mb-4">
            <div class="p-3 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors duration-200">
              <svg class="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 7.172V5L8 4z"></path>
              </svg>
            </div>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">药品管理</h3>
          <p class="text-gray-600 text-sm">管理您的药品信息，包括添加、编辑、查看药品详情和存储条件</p>
        </router-link>

        <!-- 用药记录 -->
        <router-link
          to="/records"
          class="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200 p-6 group"
        >
          <div class="flex items-center mb-4">
            <div class="p-3 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors duration-200">
              <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">用药记录</h3>
          <p class="text-gray-600 text-sm">记录和查看您的用药历史，统计用药依从性和剩余药量</p>
        </router-link>

        <!-- 用药提醒 -->
        <router-link
          to="/reminders"
          class="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200 p-6 group"
        >
          <div class="flex items-center mb-4">
            <div class="p-3 bg-yellow-100 rounded-lg group-hover:bg-yellow-200 transition-colors duration-200">
              <svg class="h-8 w-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">用药提醒</h3>
          <p class="text-gray-600 text-sm">设置智能用药提醒，确保按时服药，提高用药依从性</p>
        </router-link>

        <!-- 用药计划 -->
        <router-link
          to="/plans"
          class="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200 p-6 group"
        >
          <div class="flex items-center mb-4">
            <div class="p-3 bg-purple-100 rounded-lg group-hover:bg-purple-200 transition-colors duration-200">
              <svg class="h-8 w-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">用药计划</h3>
          <p class="text-gray-600 text-sm">制定长期和短期用药计划，检测药物冲突，优化治疗方案</p>
        </router-link>

        <!-- 就医记录 -->
        <router-link
          to="/medical-records"
          class="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200 p-6 group"
        >
          <div class="flex items-center mb-4">
            <div class="p-3 bg-indigo-100 rounded-lg group-hover:bg-indigo-200 transition-colors duration-200">
              <svg class="h-8 w-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
              </svg>
            </div>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">就医记录</h3>
          <p class="text-gray-600 text-sm">记录就诊信息、诊断结果和治疗方案，便于复诊参考</p>
        </router-link>

        <!-- 个人设置 -->
        <router-link
          to="/profile"
          class="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200 p-6 group"
        >
          <div class="flex items-center mb-4">
            <div class="p-3 bg-gray-100 rounded-lg group-hover:bg-gray-200 transition-colors duration-200">
              <svg class="h-8 w-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
            </div>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">个人设置</h3>
          <p class="text-gray-600 text-sm">管理个人信息、偏好设置和账号安全</p>
        </router-link>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useMedicineStore } from '@/stores/medicine'
import { useReminderStore } from '@/stores/reminder'
import { useToast } from '@/composables/useToast'

/**
 * 主导航页面组件
 * 提供系统功能导航和快捷统计信息
 */

// 状态管理
const medicineStore = useMedicineStore()
const reminderStore = useReminderStore()
const { error: showError } = useToast()

// 响应式数据
const loading = ref(false)

// 当前日期
const currentDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 统计数据计算属性
const medicineStats = computed(() => medicineStore.statistics)
const todayReminders = computed(() => reminderStore.todayReminders)
const activeReminders = computed(() => reminderStore.activeReminders)

// 获取仪表盘数据
const fetchDashboardData = async () => {
  try {
    loading.value = true
    
    // 并行获取所有数据
    await Promise.all([
      medicineStore.fetchStatistics(),
      reminderStore.fetchReminders(),
      reminderStore.fetchTodayReminders()
    ])
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
    showError('获取数据失败，请刷新页面重试')
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchDashboardData()
})
</script>