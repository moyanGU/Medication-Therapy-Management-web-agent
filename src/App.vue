<template>
  <AppLayout>
    <router-view />
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuth } from '@/composables/useAuth'

/**
 * 应用根组件
 * 初始化应用状态和布局
 */

const { initializeAuth } = useAuth()

// 应用初始化
onMounted(() => {
  // 初始化用户认证状态
  initializeAuth()
})
</script>