import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'

/**
 * 用户状态管理
 * 管理用户登录状态、个人信息等
 */
export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('token'))
  const userInfo = ref<UserInfo | null>(null)
  const isLoading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() => userInfo.value?.username || '')
  const userPhone = computed(() => userInfo.value?.phone || '')

  // 用户信息接口
  interface UserInfo {
    id: number
    username: string
    phone: string
    email?: string
    birthDate?: string
    gender?: 'male' | 'female'
    height?: number
    weight?: number
    bloodType?: string
    allergies?: string
    medicalHistory?: string
    avatar?: string
    role?: string
    createdAt: string
    updatedAt: string
  }

  // 登录信息接口
  interface LoginCredentials {
    username: string
    password: string
    remember?: boolean
  }

  // 注册信息接口
  interface RegisterData {
    username: string
    phone: string
    password: string
    confirmPassword: string
    verificationCode: string
    agreeTerms: boolean
  }

  // 登录响应接口
  interface LoginResponse {
    token: string
    user: UserInfo
  }

  /**
   * 用户登录
   */
  const login = async (credentials: LoginCredentials) => {
    isLoading.value = true
    try {
      const response = await api.post('/auth/login', credentials, { skipAuth: true })
      
      if (response.success) {
        const loginData = response.data as LoginResponse
        token.value = loginData.token
        userInfo.value = loginData.user
        
        // 保存到本地存储
        localStorage.setItem('token', loginData.token)
        if (credentials.remember) {
          localStorage.setItem('userInfo', JSON.stringify(loginData.user))
        }
        
        return { success: true }
      } else {
        throw new Error(response.message || '登录失败')
      }
    } catch (error) {
      console.error('登录错误:', error)
      return { 
        success: false, 
        message: error instanceof Error ? error.message : '登录失败' 
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 用户注册
   */
  const register = async (data: RegisterData) => {
    isLoading.value = true
    try {
      const response = await api.post('/auth/register', data, { skipAuth: true })
      
      if (response.success) {
        return { success: true, message: '注册成功' }
      } else {
        throw new Error(response.message || '注册失败')
      }
    } catch (error) {
      console.error('注册错误:', error)
      return { 
        success: false, 
        message: error instanceof Error ? error.message : '注册失败' 
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 获取用户信息
   */
  const fetchUserInfo = async () => {
    if (!token.value) return
    
    isLoading.value = true
    try {
      const response = await api.get('/user/profile')
      
      if (response.success) {
        userInfo.value = response.data as UserInfo
        localStorage.setItem('userInfo', JSON.stringify(response.data))
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新用户信息
   */
  const updateUserInfo = async (updates: Partial<UserInfo>) => {
    isLoading.value = true
    try {
      const response = await api.put('/user/profile', updates)
      
      if (response.success) {
        userInfo.value = { ...userInfo.value, ...response.data as Partial<UserInfo> }
        localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
        return { success: true }
      } else {
        throw new Error(response.message || '更新失败')
      }
    } catch (error) {
      console.error('更新用户信息失败:', error)
      return { 
        success: false, 
        message: error instanceof Error ? error.message : '更新失败' 
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 用户登出
   */
  const logout = async () => {
    try {
      if (token.value) {
        await api.post('/auth/logout')
      }
    } catch (error) {
      console.error('登出API调用失败:', error)
    } finally {
      // 清除本地状态
      token.value = null
      userInfo.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    }
  }

  /**
   * 初始化用户状态
   * 从本地存储恢复用户信息
   */
  const initializeUser = () => {
    const savedToken = localStorage.getItem('token')
    const savedUserInfo = localStorage.getItem('userInfo')
    
    if (savedToken) {
      token.value = savedToken
    }
    
    if (savedUserInfo) {
      try {
        userInfo.value = JSON.parse(savedUserInfo)
      } catch (error) {
        console.error('解析用户信息失败:', error)
        localStorage.removeItem('userInfo')
      }
    }
    
    // 如果有token但没有用户信息，尝试获取
    if (token.value && !userInfo.value) {
      fetchUserInfo()
    }
  }

  /**
   * 发送验证码
   */
  const sendVerificationCode = async (phone: string) => {
    try {
      const response = await api.post('/auth/send-code', { phone }, { skipAuth: true })
      
      if (response.success) {
        return { success: true, message: '验证码已发送' }
      } else {
        throw new Error(response.message || '发送失败')
      }
    } catch (error) {
      console.error('发送验证码失败:', error)
      return { 
        success: false, 
        message: error instanceof Error ? error.message : '发送失败' 
      }
    }
  }

  return {
    // 状态
    token,
    userInfo,
    isLoading,
    
    // 计算属性
    isAuthenticated,
    userName,
    userPhone,
    
    // 方法
    login,
    register,
    logout,
    fetchUserInfo,
    updateUserInfo,
    initializeUser,
    sendVerificationCode,
  }
})