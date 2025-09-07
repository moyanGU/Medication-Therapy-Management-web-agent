<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-gray-900 mb-2">用户登录</h2>
        <p class="text-gray-600">请输入您的账号信息</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="space-y-6">
        <!-- 用户名/手机号输入 -->
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
            用户名或手机号
          </label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            :class="{ 'border-red-500': errors.username }"
            placeholder="请输入用户名或手机号"
          />
          <p v-if="errors.username" class="mt-1 text-sm text-red-600">{{ errors.username }}</p>
        </div>
        
        <!-- 密码输入 -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
            密码
          </label>
          <div class="relative">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-10"
              :class="{ 'border-red-500': errors.password }"
              placeholder="请输入密码"
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              <span v-if="!showPassword" class="text-gray-400">👁</span>
              <span v-else class="text-gray-400">🙈</span>
            </button>
          </div>
          <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
        </div>
        
        <!-- 记住我 -->
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember"
              v-model="form.remember"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="remember" class="ml-2 block text-sm text-gray-700">
              记住我
            </label>
          </div>
          <router-link
            to="/forgot-password"
            class="text-sm text-blue-600 hover:text-blue-500"
          >
            忘记密码？
          </router-link>
        </div>
        
        <!-- 错误信息显示 -->
        <div v-if="errorMessage" class="bg-red-50 border border-red-200 rounded-md p-3">
          <div class="flex">
            <span class="text-red-400">⚠️</span>
            <div class="ml-3">
              <p class="text-sm text-red-800">{{ errorMessage }}</p>
            </div>
          </div>
        </div>
        
        <!-- 登录按钮 -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading" class="animate-spin -ml-1 mr-3 text-white">⏳</span>
          {{ loading ? '登录中...' : '登录' }}
        </button>
        
        <!-- 注册链接 -->
        <div class="text-center">
          <span class="text-sm text-gray-600">还没有账号？</span>
          <router-link
            to="/register"
            class="text-sm text-blue-600 hover:text-blue-500 ml-1"
          >
            立即注册
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const form = reactive({
  username: '',
  password: '',
  remember: false
})

// 表单验证错误
const errors = reactive({
  username: '',
  password: ''
})

// 组件状态
const loading = ref(false)
const showPassword = ref(false)
const errorMessage = ref('')

/**
 * 验证表单数据
 */
const validateForm = (): boolean => {
  // 重置错误信息
  errors.username = ''
  errors.password = ''
  errorMessage.value = ''
  
  let isValid = true
  
  // 验证用户名
  if (!form.username.trim()) {
    errors.username = '请输入用户名或手机号'
    isValid = false
  } else if (form.username.trim().length < 2) {
    errors.username = '用户名至少2个字符'
    isValid = false
  }
  
  // 验证密码
  if (!form.password) {
    errors.password = '请输入密码'
    isValid = false
  } else if (form.password.length < 6) {
    errors.password = '密码至少6个字符'
    isValid = false
  }
  
  return isValid
}

/**
 * 处理登录
 */
const handleLogin = async () => {
  console.log('开始登录流程', form)
  
  if (!validateForm()) {
    console.log('表单验证失败')
    return
  }
  
  loading.value = true
  errorMessage.value = ''
  
  try {
    console.log('调用登录API')
    const result = await authStore.login({
      username: form.username.trim(),
      password: form.password
    })

    if (!result?.success) {
      console.warn('登录失败（业务失败）：', result?.message)
      errorMessage.value = result?.message || '用户名或密码错误'
      return
    }
    
    console.log('登录成功，准备跳转')
    
    // 等待Vue响应式系统更新完成
    await nextTick()
    
    // 再次等待确保认证状态更新
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // 获取重定向路径
    const redirect = router.currentRoute.value.query.redirect as string
    const targetPath = redirect || '/dashboard'
    
    console.log('目标路径:', targetPath)
    console.log('当前认证状态:', authStore.isAuthenticated)
    console.log('accessToken:', authStore.accessToken)
    
    // 如果认证状态仍然是false，强制刷新页面
    if (!authStore.isAuthenticated) {
      console.log('认证状态异常，强制刷新页面')
      window.location.href = targetPath
      return
    }
    
    // 使用replace而不是push，避免在历史记录中留下登录页
    await router.replace(targetPath)
    
    console.log('路由跳转完成')
    
  } catch (error: any) {
    console.error('登录失败（异常）:', error)
    console.log('登录功能又出问题了')
    
    // ApiClient 抛出的为 ApiError，不含 axios 的 error.response 结构
    errorMessage.value = error?.message || '登录失败，请稍后重试'
    console.error('登录失败:', errorMessage.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 自定义样式 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>