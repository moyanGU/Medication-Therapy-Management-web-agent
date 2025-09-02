<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- 头部 -->
      <div class="text-center">
        <router-link to="/" class="inline-block">
          <div class="mx-auto h-16 w-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
            <svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 7.172V5L8 4z"></path>
            </svg>
          </div>
        </router-link>
        <h2 class="text-3xl font-bold text-gray-900 mb-2">注册账号</h2>
        <p class="text-gray-600">创建您的MTM Helper账号</p>
      </div>

      <!-- 注册表单 -->
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="space-y-4">
          <!-- 用户名输入 -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
              用户名
            </label>
            <input
              id="username"
              v-model="registerForm.username"
              type="text"
              required
              class="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 text-lg"
              placeholder="请输入用户名"
            />
          </div>

          <!-- 手机号输入 -->
          <div>
            <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
              手机号
            </label>
            <input
              id="phone"
              v-model="registerForm.phone"
              type="tel"
              required
              class="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 text-lg"
              placeholder="请输入手机号"
            />
          </div>

          <!-- 验证码输入 -->
          <div>
            <label for="verification-code" class="block text-sm font-medium text-gray-700 mb-2">
              验证码
            </label>
            <div class="flex space-x-3">
              <input
                id="verification-code"
                v-model="registerForm.verificationCode"
                type="text"
                required
                class="flex-1 appearance-none relative block px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 text-lg"
                placeholder="请输入验证码"
              />
              <button
                type="button"
                :disabled="isSendingCode || countdown > 0"
                @click="sendVerificationCode"
                class="px-4 py-3 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                {{ countdown > 0 ? `${countdown}s` : isSendingCode ? '发送中...' : '发送验证码' }}
              </button>
            </div>
          </div>

          <!-- 密码输入 -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              密码
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="registerForm.password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 text-lg pr-10"
                placeholder="请输入密码"
              />
              <button
                type="button"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
                @click="showPassword = !showPassword"
              >
                <svg
                  v-if="showPassword"
                  class="h-5 w-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                </svg>
                <svg
                  v-else
                  class="h-5 w-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
                </svg>
              </button>
            </div>
            <p class="mt-1 text-sm text-gray-500">密码长度至少6位，建议包含字母和数字</p>
          </div>

          <!-- 确认密码输入 -->
          <div>
            <label for="confirm-password" class="block text-sm font-medium text-gray-700 mb-2">
              确认密码
            </label>
            <input
              id="confirm-password"
              v-model="registerForm.confirmPassword"
              type="password"
              required
              class="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 text-lg"
              placeholder="请再次输入密码"
            />
          </div>
        </div>

        <!-- 服务条款 -->
        <div class="flex items-center">
          <input
            id="agree-terms"
            v-model="registerForm.agreeTerms"
            type="checkbox"
            required
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="agree-terms" class="ml-2 block text-sm text-gray-700">
            我已阅读并同意
            <a href="#" class="text-blue-600 hover:text-blue-500">服务条款</a>
            和
            <a href="#" class="text-blue-600 hover:text-blue-500">隐私政策</a>
          </label>
        </div>

        <!-- 注册按钮 -->
        <div>
          <button
            type="submit"
            :disabled="isLoading || !isFormValid"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-lg font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ isLoading ? '注册中...' : '注册' }}
          </button>
        </div>

        <!-- 登录链接 -->
        <div class="text-center">
          <span class="text-gray-600">已有账号？</span>
          <router-link to="/login" class="font-medium text-blue-600 hover:text-blue-500 ml-1">
            立即登录
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'

/**
 * 注册页面组件
 * 提供用户注册功能，包含手机验证码验证
 */

const router = useRouter()

// 表单数据
const registerForm = reactive({
  username: '',
  phone: '',
  verificationCode: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
})

// 组件状态
const showPassword = ref(false)
const isLoading = ref(false)
const isSendingCode = ref(false)
const countdown = ref(0)

// 表单验证
const isFormValid = computed(() => {
  return (
    registerForm.username.trim() &&
    registerForm.phone.trim() &&
    registerForm.verificationCode.trim() &&
    registerForm.password.length >= 6 &&
    registerForm.password === registerForm.confirmPassword &&
    registerForm.agreeTerms
  )
})

/**
 * 发送验证码
 */
const sendVerificationCode = async () => {
  if (!registerForm.phone.trim()) {
    alert('请先输入手机号')
    return
  }

  console.log('发送验证码到:', registerForm.phone)
  
  isSendingCode.value = true
  
  try {
    // TODO: 调用发送验证码API
    // 模拟发送过程
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 开始倒计时
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
    
    console.log('验证码发送成功')
  } catch (error) {
    console.error('验证码发送失败:', error)
    // TODO: 显示错误提示
  } finally {
    isSendingCode.value = false
  }
}

/**
 * 处理注册提交
 */
const handleRegister = async () => {
  if (!isFormValid.value) {
    return
  }

  console.log('注册表单提交:', registerForm)
  
  isLoading.value = true
  
  try {
    // TODO: 调用注册API
    // 模拟注册过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 注册成功后跳转到登录页面
    router.push('/login')
  } catch (error) {
    console.error('注册失败:', error)
    // TODO: 显示错误提示
  } finally {
    isLoading.value = false
  }
}
</script>