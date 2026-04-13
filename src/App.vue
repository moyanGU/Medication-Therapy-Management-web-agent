<script setup lang="ts">
import { onMounted, watch } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import AiAssistant from '@/components/AiAssistant.vue'
import { useAuth } from '@/composables/useAuth'

/**
 * 应用根组件
 * 初始化应用状态和布局
 */

const { initializeAuth, isAuthenticated } = useAuth()

// 应用初始化
onMounted(() => {
  // 初始化用户认证状态
  initializeAuth()
})

watch(
  isAuthenticated,
  isAuthed => {
    console.log('[App] 登录状态变更:', isAuthed)
  },
  { immediate: true }
)
</script>

<template>
  <AppLayout>
    <router-view />
  </AppLayout>
  <!-- 全局 AI 助手 -->
  <AiAssistant v-if="isAuthenticated" />
</template>
