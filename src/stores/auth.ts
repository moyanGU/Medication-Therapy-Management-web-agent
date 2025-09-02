import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// 用户信息接口
interface UserInfo {
  id: number
  username: string
  phone: string
  email?: string
  createdAt: string
  updatedAt: string
}

// 登录凭据接口
interface LoginCredentials {
  username: string
  password: string
}

// 注册数据接口
interface RegisterData {
  username: string
  phone: string
  password: string
  verification_code: string
}

// API响应接口
interface ApiResponse<T = any> {
  success: boolean
  message: string
  data: T
}

// 登录响应数据
interface LoginResponseData {
  access_token: string
  refresh_token: string
  user: UserInfo
}

/**
 * 认证状态管理
 * 管理用户登录状态、JWT令牌等
 */
export const useAuthStore = defineStore('auth', () => {
  // 状态
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const user = ref<UserInfo | null>(null)
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!accessToken.value)
  const userName = computed(() => user.value?.username || '')
  const userPhone = computed(() => user.value?.phone || '')

  // API基础URL
  const API_BASE_URL = 'http://localhost:8000/api'

  /**
   * 设置认证令牌
   */
  const setTokens = (access: string, refresh: string) => {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    
    // 设置axios默认请求头
    axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
  }

  /**
   * 清除认证令牌
   */
  const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
    
    // 清除axios默认请求头
    delete axios.defaults.headers.common['Authorization']
  }

  /**
   * 用户登录
   */
  const login = async (credentials: LoginCredentials) => {
    loading.value = true
    
    try {
      console.log('发送登录请求:', credentials)
      
      const response = await axios.post<ApiResponse<LoginResponseData>>(
        `${API_BASE_URL}/auth/login/`,
        credentials,
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      )
      
      console.log('登录响应:', response.data)
      
      if (response.data.success) {
        const { access_token, refresh_token, user: userInfo } = response.data.data
        
        // 保存令牌和用户信息
        setTokens(access_token, refresh_token)
        user.value = userInfo
        localStorage.setItem('user_info', JSON.stringify(userInfo))
        
        console.log('登录成功，用户信息:', userInfo)
        console.log('认证状态已更新，isAuthenticated:', isAuthenticated.value)
        console.log('accessToken.value:', accessToken.value)
        console.log('localStorage access_token:', localStorage.getItem('access_token'))
        
        return { success: true, message: '登录成功' }
      } else {
        throw new Error(response.data.message || '登录失败')
      }
    } catch (error: any) {
      console.error('登录失败:', error)
      
      let errorMessage = '登录失败，请稍后重试'
      
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      
      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户注册
   */
  const register = async (data: RegisterData) => {
    loading.value = true
    
    try {
      console.log('发送注册请求:', data)
      
      const response = await axios.post<ApiResponse>(
        `${API_BASE_URL}/auth/register/`,
        data,
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      )
      
      console.log('注册响应:', response.data)
      
      if (response.data.success) {
        return { success: true, message: response.data.message || '注册成功' }
      } else {
        throw new Error(response.data.message || '注册失败')
      }
    } catch (error: any) {
      console.error('注册失败:', error)
      
      let errorMessage = '注册失败，请稍后重试'
      
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      
      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }

  /**
   * 发送验证码
   */
  const sendVerificationCode = async (phone: string) => {
    loading.value = true
    
    try {
      console.log('发送验证码请求:', { phone })
      
      const response = await axios.post<ApiResponse>(
        `${API_BASE_URL}/auth/send-code/`,
        { phone },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      )
      
      console.log('验证码响应:', response.data)
      
      if (response.data.success) {
        return { success: true, message: response.data.message || '验证码发送成功' }
      } else {
        throw new Error(response.data.message || '验证码发送失败')
      }
    } catch (error: any) {
      console.error('验证码发送失败:', error)
      
      let errorMessage = '验证码发送失败，请稍后重试'
      
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      
      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登出
   */
  const logout = async () => {
    try {
      if (accessToken.value) {
        console.log('发送登出请求')
        
        const response = await axios.post<ApiResponse>(
          `${API_BASE_URL}/auth/logout/`,
          {
            refresh_token: refreshToken.value
          },
          {
            headers: {
              'Authorization': `Bearer ${accessToken.value}`,
              'Content-Type': 'application/json'
            }
          }
        )
        
        console.log('登出响应:', response.data)
        
        if (response.data.success) {
          console.log('登出成功')
        } else {
          console.warn('登出API返回失败:', response.data.message)
        }
      }
    } catch (error: any) {
      console.error('登出API调用失败:', error)
      
      // 即使API调用失败，也要清除本地token
      let errorMessage = '登出失败'
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      console.warn('登出错误详情:', errorMessage)
    } finally {
      // 无论API调用是否成功，都清除本地认证信息
      clearTokens()
      console.log('本地认证信息已清除')
    }
  }

  /**
   * 刷新访问令牌
   */
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('没有刷新令牌')
    }
    
    try {
      const response = await axios.post<ApiResponse<{ access_token: string }>>(
        `${API_BASE_URL}/auth/refresh/`,
        { refresh_token: refreshToken.value }
      )
      
      if (response.data.success) {
        const { access_token } = response.data.data
        accessToken.value = access_token
        localStorage.setItem('access_token', access_token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        return access_token
      } else {
        throw new Error('令牌刷新失败')
      }
    } catch (error) {
      console.error('令牌刷新失败:', error)
      clearTokens()
      throw error
    }
  }

  /**
   * 初始化认证状态
   */
  const initializeAuth = () => {
    const savedAccessToken = localStorage.getItem('access_token')
    const savedRefreshToken = localStorage.getItem('refresh_token')
    const savedUserInfo = localStorage.getItem('user_info')
    
    if (savedAccessToken && savedRefreshToken) {
      accessToken.value = savedAccessToken
      refreshToken.value = savedRefreshToken
      axios.defaults.headers.common['Authorization'] = `Bearer ${savedAccessToken}`
    }
    
    if (savedUserInfo) {
      try {
        user.value = JSON.parse(savedUserInfo)
      } catch (error) {
        console.error('解析用户信息失败:', error)
        localStorage.removeItem('user_info')
      }
    }
  }

  /**
   * 检查令牌是否有效
   */
  const checkTokenValidity = async () => {
    if (!accessToken.value) {
      return false
    }
    
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/verify/`, {
        headers: {
          'Authorization': `Bearer ${accessToken.value}`
        }
      })
      
      return response.data.success
    } catch (error) {
      console.error('令牌验证失败:', error)
      return false
    }
  }

  return {
    // 状态
    accessToken,
    refreshToken,
    user,
    loading,
    
    // 计算属性
    isAuthenticated,
    userName,
    userPhone,
    
    // 方法
    login,
    register,
    logout,
    sendVerificationCode,
    refreshAccessToken,
    initializeAuth,
    checkTokenValidity,
    setTokens,
    clearTokens
  }
})