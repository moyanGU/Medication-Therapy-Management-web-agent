<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <!-- 头部导航 -->
    <AppHeader />
    
    <!-- 主要内容区域 -->
    <main class="flex-1">
      <slot />
    </main>
    
    <!-- 底部 -->
    <AppFooter v-if="showFooter" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './AppHeader.vue'
import AppFooter from './AppFooter.vue'

/**
 * 应用主布局组件
 * 包含头部导航、主要内容区域和底部
 */

const route = useRoute()

// 定义不显示Footer的页面
const hideFooterRoutes = ['/login', '/register']

// 计算是否显示Footer
const showFooter = computed(() => {
  return !hideFooterRoutes.includes(route.path)
})
</script>

<script lang="ts">
export default {
  name: 'AppLayout'
}
</script>