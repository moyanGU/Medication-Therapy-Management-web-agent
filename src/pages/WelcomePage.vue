<template>
  <div
    class="relative min-h-screen bg-gradient-to-br from-blue-50 via-slate-50 to-indigo-100 flex items-center justify-center overflow-hidden"
  >
    <div
      class="absolute inset-0 pointer-events-none bg-center bg-cover opacity-35 blur-xl scale-110"
      style="background-image: url('/images/mtm-cover-logo.svg')"
    ></div>
    <div
      class="absolute inset-0 pointer-events-none bg-white/45 backdrop-blur-[2px]"
    ></div>
    <div class="relative z-10 max-w-md w-full space-y-8 p-8 bg-white/78 backdrop-blur-md rounded-2xl shadow-xl border border-white/70">
      <!-- Logo区域 -->
      <div class="text-center">
        <div
          class="mx-auto h-20 w-20 bg-blue-600 rounded-full flex items-center justify-center mb-4"
        >
          <svg
            class="h-12 w-12 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 7.172V5L8 4z"
            ></path>
          </svg>
        </div>
        <h1 class="text-4xl font-bold text-gray-900 mb-2">MTM Helper</h1>
        <p class="text-lg text-gray-600 mb-8">智能药品管理助手</p>
        <p class="text-sm text-gray-500 mb-8">
          专为老年人设计的安全、便捷药品管理系统
        </p>
      </div>

      <!-- 功能特色 -->
      <div class="space-y-4 mb-8">
        <div class="flex items-center space-x-3">
          <div
            class="flex-shrink-0 h-8 w-8 bg-green-100 rounded-full flex items-center justify-center"
          >
            <svg
              class="h-5 w-5 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              ></path>
            </svg>
          </div>
          <span class="text-gray-700">智能用药提醒</span>
        </div>
        <div class="flex items-center space-x-3">
          <div
            class="flex-shrink-0 h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center"
          >
            <svg
              class="h-5 w-5 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              ></path>
            </svg>
          </div>
          <span class="text-gray-700">药品库存管理</span>
        </div>
        <div class="flex items-center space-x-3">
          <div
            class="flex-shrink-0 h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center"
          >
            <svg
              class="h-5 w-5 text-purple-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              ></path>
            </svg>
          </div>
          <span class="text-gray-700">就医记录管理</span>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="space-y-4">
        <router-link
          to="/login"
          class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-lg font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
        >
          登录
        </router-link>
        <router-link
          to="/register"
          class="w-full flex justify-center py-3 px-4 border border-gray-300 rounded-lg shadow-sm text-lg font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
        >
          注册账号
        </router-link>
      </div>

      <!-- 底部信息 -->
      <div class="text-center text-sm text-gray-500">
        <p>安全可靠 · 简单易用 · 专业贴心</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 欢迎页面组件
 * 展示应用logo、功能特色和登录注册入口
 */
</script>
