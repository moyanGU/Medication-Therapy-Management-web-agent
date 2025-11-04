<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-gray-900 mb-2">用户注册</h2>
        <p class="text-gray-600">创建您的新账号</p>
      </div>
      
      <form @submit.prevent="handleRegister" class="space-y-6">
        <!-- 用户名输入 -->
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
            用户名
          </label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            :class="{ 'border-red-500': errors.username }"
            placeholder="请输入用户名"
          />
          <p v-if="errors.username" class="mt-1 text-sm text-red-600">{{ errors.username }}</p>
        </div>
        
        <!-- 手机号输入 -->
        <div>
          <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
            手机号
          </label>
          <input
            id="phone"
            v-model="form.phone"
            type="tel"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            :class="{ 'border-red-500': errors.phone }"
            placeholder="请输入手机号"
          />
          <p v-if="errors.phone" class="mt-1 text-sm text-red-600">{{ errors.phone }}</p>
        </div>
        
        <!-- 验证码输入 -->
        <div>
          <label for="verificationCode" class="block text-sm font-medium text-gray-700 mb-2">
            验证码
          </label>
          <div class="flex space-x-2">
            <input
              id="verificationCode"
              v-model="form.verification_code"
              type="text"
              required
              maxlength="6"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              :class="{ 'border-red-500': errors.verification_code }"
              placeholder="请输入验证码"
            />
            <button
              type="button"
              @click="sendCode"
              :disabled="codeSending || countdown > 0 || !isPhoneValid"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              <span v-if="codeSending" class="animate-spin h-4 w-4">⏳</span>
              <span v-else-if="countdown > 0">{{ countdown }}s</span>
              <span v-else>发送验证码</span>
            </button>
          </div>
          <p v-if="errors.verification_code" class="mt-1 text-sm text-red-600">{{ errors.verification_code }}</p>
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
              <span v-if="!showPassword">👁️</span>
              <span v-else>🙈</span>
            </button>
          </div>
          <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
        </div>
        
        <!-- 确认密码输入 -->
        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
            确认密码
          </label>
          <div class="relative">
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-10"
              :class="{ 'border-red-500': errors.confirmPassword }"
              placeholder="请再次输入密码"
            />
            <button
              type="button"
              @click="showConfirmPassword = !showConfirmPassword"
              class="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              <span v-if="!showConfirmPassword">👁️</span>
              <span v-else>🙈</span>
            </button>
          </div>
          <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-600">{{ errors.confirmPassword }}</p>
        </div>
        
        <!-- 同意条款 -->
        <div class="flex items-center">
          <input
            id="agreeTerms"
            v-model="form.agreeTerms"
            type="checkbox"
            required
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            :class="{ 'border-red-500': errors.agreeTerms }"
          />
          <label for="agreeTerms" class="ml-2 block text-sm text-gray-700">
            我已阅读并同意
            <a href="#" class="text-blue-600 hover:text-blue-500">用户协议</a>
            和
            <a href="#" class="text-blue-600 hover:text-blue-500">隐私政策</a>
          </label>
        </div>
        <p v-if="errors.agreeTerms" class="mt-1 text-sm text-red-600">{{ errors.agreeTerms }}</p>
        
        <!-- 错误信息显示 -->
        <div v-if="errorMessage" class="bg-red-50 border border-red-200 rounded-md p-3">
          <div class="flex">
            <span class="text-red-400">⚠️</span>
            <div class="ml-3">
              <p class="text-sm text-red-800">{{ errorMessage }}</p>
            </div>
          </div>
        </div>
        
        <!-- 成功信息显示 -->
        <div v-if="successMessage" class="bg-green-50 border border-green-200 rounded-md p-3">
          <div class="flex">
            <span class="text-green-500">✅</span>
            <div class="ml-3">
              <p class="text-sm text-green-800">{{ successMessage }}</p>
            </div>
          </div>
        </div>
        
        <!-- 注册按钮 -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading" class="animate-spin -ml-1 mr-3 text-white">⏳</span>
          {{ loading ? '注册中...' : '注册' }}
        </button>
        
        <!-- 登录链接 -->
        <div class="text-center">
          <span class="text-sm text-gray-600">已有账号？</span>
          <router-link
            to="/login"
            class="text-sm text-blue-600 hover:text-blue-500 ml-1"
          >
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
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const form = reactive({
  username: '',
  phone: '',
  verification_code: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
})

// 表单验证错误
const errors = reactive({
  username: '',
  phone: '',
  verification_code: '',
  password: '',
  confirmPassword: '',
  agreeTerms: ''
})

// 组件状态
const loading = ref(false)
const codeSending = ref(false)
const countdown = ref(0)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// 计算属性
const isPhoneValid = computed(() => {
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(form.phone)
})

/**
 * 验证表单数据
 */
const validateForm = (): boolean => {
  // 重置错误信息
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = ''
  })
  errorMessage.value = ''
  
  let isValid = true
  
  // 验证用户名
  if (!form.username.trim()) {
    errors.username = '请输入用户名'
    isValid = false
  } else if (form.username.trim().length < 2) {
    errors.username = '用户名至少2个字符'
    isValid = false
  } else if (form.username.trim().length > 20) {
    errors.username = '用户名不能超过20个字符'
    isValid = false
  }
  
  // 验证手机号
  if (!form.phone) {
    errors.phone = '请输入手机号'
    isValid = false
  } else if (!isPhoneValid.value) {
    errors.phone = '请输入正确的手机号'
    isValid = false
  }
  
  // 验证验证码
  if (!form.verification_code) {
    errors.verification_code = '请输入验证码'
    isValid = false
  } else if (form.verification_code.length !== 6) {
    errors.verification_code = '验证码应为6位数字'
    isValid = false
  }
  
  // 验证密码
  if (!form.password) {
    errors.password = '请输入密码'
    isValid = false
  } else if (form.password.length < 6) {
    errors.password = '密码至少6个字符'
    isValid = false
  } else if (form.password.length > 20) {
    errors.password = '密码不能超过20个字符'
    isValid = false
  }
  
  // 验证确认密码
  if (!form.confirmPassword) {
    errors.confirmPassword = '请确认密码'
    isValid = false
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = '两次输入的密码不一致'
    isValid = false
  }
  
  // 验证同意条款
  if (!form.agreeTerms) {
    errors.agreeTerms = '请同意用户协议和隐私政策'
    isValid = false
  }
  
  return isValid
}

/**
 * 发送验证码
 */
const sendCode = async () => {
  if (!isPhoneValid.value) {
    errors.phone = '请输入正确的手机号'
    return
  }
  
  codeSending.value = true
  successMessage.value = ''
  errorMessage.value = ''
  
  try {
    console.log('发送验证码到:', form.phone)
    const res = await authStore.sendVerificationCode(form.phone)
    
    if (res && res.success) {
      successMessage.value = '验证码已发送，请查收短信'
      if ((res as any).code) {
        successMessage.value += `（开发环境验证码：${(res as any).code}）`
      }
      
      // 开始倒计时（仅在发送成功时）
      countdown.value = 60
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    } else {
      errorMessage.value = res?.message || '验证码发送失败'
    }
  } catch (error: any) {
    console.error('发送验证码失败:', error)
    errorMessage.value = error.message || '验证码发送失败，请稍后重试'
  } finally {
    codeSending.value = false
  }
}

/**
 * 处理注册
 */
const handleRegister = async () => {
  console.log('开始注册流程', form)
  
  if (!validateForm()) {
    console.log('表单验证失败')
    return
  }
  
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  try {
    console.log('调用注册API')
    const result = await authStore.register({
      username: form.username.trim(),
      phone: form.phone,
      password: form.password,
      verification_code: form.verification_code
    })
    
    if (result.success) {
      successMessage.value = result.message || '注册成功！请登录'
      console.log('注册成功，跳转到登录页')
      await router.push('/login')
    } else {
      errorMessage.value = result.message || '注册失败，请稍后重试'
      console.error('注册失败:', errorMessage.value)
    }
  } catch (error: any) {
    console.error('注册失败:', error)
    
    // 处理不同类型的错误
    if (error.message.includes('用户名已存在')) {
      errors.username = '用户名已存在'
    } else if (error.message.includes('手机号已注册')) {
      errors.phone = '手机号已注册'
    } else if (error.message.includes('验证码')) {
      errors.verification_code = '验证码错误或已过期'
    } else {
      errorMessage.value = error.message || '注册失败，请稍后重试'
    }
    
    console.error('注册失败:', errorMessage.value || '注册失败')
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