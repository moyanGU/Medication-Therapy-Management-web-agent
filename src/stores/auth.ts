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
  const API_BASE_URL = 'http://127.0.0.1:8000/api'

  /**
   * 设置认证令牌
   */
  const setTokens = (access: string, refresh: string) => {
    console.log('🔵 [AuthStore] setTokens 被调用')
    console.log('🔵 [AuthStore] Access token type:', typeof access)
    console.log('🔵 [AuthStore] Access token length:', access ? access.length : 'null')
    console.log('🔵 [AuthStore] Access token preview:', access ? access.substring(0, 50) + '...' : 'null')
    console.log('🔵 [AuthStore] Refresh token type:', typeof refresh)
    console.log('🔵 [AuthStore] Refresh token length:', refresh ? refresh.length : 'null')
    
    // 验证token的有效性
    if (!access || typeof access !== 'string' || access.trim() === '' || access === 'undefined' || access === 'null') {
      console.error('🔴 [AuthStore] Invalid access token provided:', access)
      throw new Error('Invalid access token')
    }
    
    if (!refresh || typeof refresh !== 'string' || refresh.trim() === '' || refresh === 'undefined' || refresh === 'null') {
      console.error('🔴 [AuthStore] Invalid refresh token provided:', refresh)
      throw new Error('Invalid refresh token')
    }
    
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    
    console.log('🔵 [AuthStore] Tokens 设置成功')
    console.log('🔵 [AuthStore] localStorage access_token 存储成功:', !!localStorage.getItem('access_token'))
    console.log('🔵 [AuthStore] localStorage refresh_token 存储成功:', !!localStorage.getItem('refresh_token'))
    
    // 设置axios默认请求头
    axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
    console.log('🔵 [AuthStore] Axios authorization header 设置成功')
  }

  /**
   * 清理认证令牌
   */
  const clearTokens = () => {
    console.log('🔵 [AuthStore] clearTokens 被调用')
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
    
    // 清除axios默认请求头
    delete axios.defaults.headers.common['Authorization']
    console.log('🔵 [AuthStore] 所有认证信息已清理')
  }
  
  /**
   * 清理无效的localStorage数据
   */
  const cleanupInvalidTokens = () => {
    console.log('🔵 [AuthStore] 检查并清理无效token')
    
    const accessTokenValue = localStorage.getItem('access_token')
    const refreshTokenValue = localStorage.getItem('refresh_token')
    
    console.log('🔵 [AuthStore] 当前localStorage access_token:', accessTokenValue)
    console.log('🔵 [AuthStore] 当前localStorage refresh_token:', refreshTokenValue)
    
    let needsCleanup = false
    
    // 检查access_token
    if (accessTokenValue && (
      accessTokenValue === 'undefined' || 
      accessTokenValue === 'null' || 
      accessTokenValue.trim() === '' ||
      typeof accessTokenValue !== 'string' ||
      accessTokenValue.length < 10  // JWT token应该很长
    )) {
      console.warn('🟡 [AuthStore] 发现无效的access_token:', accessTokenValue)
      needsCleanup = true
    }
    
    // 检查refresh_token
    if (refreshTokenValue && (
      refreshTokenValue === 'undefined' || 
      refreshTokenValue === 'null' || 
      refreshTokenValue.trim() === '' ||
      typeof refreshTokenValue !== 'string' ||
      refreshTokenValue.length < 10  // JWT token应该很长
    )) {
      console.warn('🟡 [AuthStore] 发现无效的refresh_token:', refreshTokenValue)
      needsCleanup = true
    }
    
    if (needsCleanup) {
      console.log('🔴 [AuthStore] 清理无效token')
      clearTokens()
      return false
    }
    
    console.log('🟢 [AuthStore] Token校验通过')
    return true
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
        const { tokens, user: userInfo } = response.data.data
        
        console.log('🔵 [AuthStore] 解析登录响应数据:')
        console.log('  - tokens:', tokens)
        console.log('  - tokens.access:', tokens?.access)
        console.log('  - tokens.refresh:', tokens?.refresh)
        console.log('  - user:', userInfo)
        
        // 验证tokens结构
        if (!tokens || !tokens.access || !tokens.refresh) {
          throw new Error('登录响应中缺少有效的token信息')
        }
        
        // 保存令牌和用户信息
        setTokens(tokens.access, tokens.refresh)
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
    console.log('🔵 [AuthStore] === Logout Started ===')
    console.log('🔵 [AuthStore] Current access token exists:', !!accessToken.value)
    console.log('🔵 [AuthStore] Current refresh token exists:', !!refreshToken.value)
    console.log('🔵 [AuthStore] Access token preview:', accessToken.value?.substring(0, 30) + '...')
    console.log('🔵 [AuthStore] User info:', user.value)
    
    try {
      if (accessToken.value) {
        console.log('🔵 [AuthStore] 发送登出请求到服务器')
        console.log('🔵 [AuthStore] API URL:', `${API_BASE_URL}/auth/logout/`)
        console.log('🔵 [AuthStore] Request payload:', {
          refresh_token: refreshToken.value?.substring(0, 30) + '...'
        })
        
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
        
        console.log('🔵 [AuthStore] 登出响应状态:', response.status)
        console.log('🔵 [AuthStore] 登出响应数据:', response.data)
        
        if (response.data.success) {
          console.log('🟢 [AuthStore] 服务器登出成功')
        } else {
          console.warn('🟡 [AuthStore] 登出API返回失败:', response.data.message)
        }
      } else {
        console.log('🟡 [AuthStore] 没有访问令牌，跳过服务器登出请求')
      }
    } catch (error: any) {
      console.error('🔴 [AuthStore] 登出API调用失败:', {
        error: error,
        message: error.message,
        response: error.response,
        responseData: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText,
        stack: error.stack,
        timestamp: new Date().toISOString()
      })
      
      // 即使API调用失败，也要清除本地token
      let errorMessage = '登出失败'
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      console.warn('🔴 [AuthStore] 登出错误详情:', errorMessage)
    } finally {
      // 无论API调用是否成功，都清除本地认证信息
      console.log('🔵 [AuthStore] 开始清除本地认证信息')
      console.log('🔵 [AuthStore] 清除前 - localStorage access_token:', !!localStorage.getItem('access_token'))
      console.log('🔵 [AuthStore] 清除前 - localStorage refresh_token:', !!localStorage.getItem('refresh_token'))
      console.log('🔵 [AuthStore] 清除前 - localStorage user_info:', !!localStorage.getItem('user_info'))
      
      clearTokens()
      
      console.log('🔵 [AuthStore] 清除后 - localStorage access_token:', !!localStorage.getItem('access_token'))
      console.log('🔵 [AuthStore] 清除后 - localStorage refresh_token:', !!localStorage.getItem('refresh_token'))
      console.log('🔵 [AuthStore] 清除后 - localStorage user_info:', !!localStorage.getItem('user_info'))
      console.log('🔵 [AuthStore] 清除后 - store accessToken:', !!accessToken.value)
      console.log('🔵 [AuthStore] 清除后 - store user:', user.value)
      console.log('🟢 [AuthStore] 本地认证信息已清除')
      console.log('🔵 [AuthStore] === Logout Completed ===')
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
        const { access } = response.data.data
        
        console.log('🔵 [AuthStore] 刷新token成功:', access)
        
        if (!access) {
          throw new Error('刷新token响应中缺少access token')
        }
        
        accessToken.value = access
        localStorage.setItem('access_token', access)
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
        return access
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
    console.log('🔵 [AuthStore] 初始化认证状态')
    
    // 先清理无效token
    const hasValidTokens = cleanupInvalidTokens()
    
    if (!hasValidTokens) {
      console.log('🟡 [AuthStore] 没有有效token，初始化停止')
      return
    }
    
    const savedAccessToken = localStorage.getItem('access_token')
    const savedRefreshToken = localStorage.getItem('refresh_token')
    const savedUserInfo = localStorage.getItem('user_info')
    
    console.log('🔵 [AuthStore] 保存的token情况:')
    console.log('  - access_token 存在:', !!savedAccessToken)
    console.log('  - refresh_token 存在:', !!savedRefreshToken)
    console.log('  - user_info 存在:', !!savedUserInfo)
    
    if (savedAccessToken && savedRefreshToken) {
      accessToken.value = savedAccessToken
      refreshToken.value = savedRefreshToken
      axios.defaults.headers.common['Authorization'] = `Bearer ${savedAccessToken}`
      console.log('🟢 [AuthStore] Token恢复成功')
    }
    
    if (savedUserInfo) {
      try {
        user.value = JSON.parse(savedUserInfo)
        console.log('🟢 [AuthStore] 用户信息恢复成功:', user.value?.username)
      } catch (error) {
        console.error('🔴 [AuthStore] 解析用户信息失败:', error)
        localStorage.removeItem('user_info')
      }
    }
    
    console.log('🟢 [AuthStore] 初始化完成，认证状态:', isAuthenticated.value)
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
    clearTokens,
    cleanupInvalidTokens
  }
})