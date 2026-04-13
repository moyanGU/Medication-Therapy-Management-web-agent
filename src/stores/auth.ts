import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'

const isDebug = import.meta.env.MODE !== 'production'
const log = (...args: any[]) => {
  if (isDebug) console.log(...args)
}
const warn = (message: string, error?: unknown) => {
  if (isDebug && error !== undefined) {
    console.warn(message, error)
    return
  }
  console.warn(message)
}
const logError = (message: string, error?: unknown) => {
  if (isDebug && error !== undefined) {
    console.error(message, error)
    return
  }
  console.error(message)
}

// 用户信息接口
interface UserInfo {
  id: number
  username: string
  phone: string
  email?: string
  createdAt: string
  updatedAt: string
  // 可选的用户角色字段，后端若未返回则为 undefined
  // 这样在其它地方访问 user.role 不会触发 TS 的属性不存在错误
  role?: string
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

// 登录响应数据（兼容多种后端返回形态）
interface LoginResponseData {
  // 新结构：后端返回 data.tokens.access / data.tokens.refresh
  tokens?: { access: string; refresh: string }
  // 旧结构：直接返回扁平的 access_token / refresh_token
  access_token?: string
  refresh_token?: string
  // 其它可能的字段名（如刷新接口可能返回 data.access）
  access?: string
  refresh?: string
  user?: UserInfo
}

/**
 * 认证状态管理
 * 管理用户登录状态、JWT令牌等
 */
export const useAuthStore = defineStore('auth', () => {
  // 辅助函数：安全获取localStorage值
  const getValidToken = (key: string): string | null => {
    const value = localStorage.getItem(key)
    if (
      !value ||
      value === 'null' ||
      value === 'undefined' ||
      value.trim() === ''
    ) {
      return null
    }
    return value
  }

  // 状态
  const accessToken = ref<string | null>(getValidToken('access_token'))
  const refreshToken = ref<string | null>(getValidToken('refresh_token'))
  const user = ref<UserInfo | null>(null)
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => {
    const hasValidToken =
      !!accessToken.value &&
      accessToken.value !== 'null' &&
      accessToken.value !== 'undefined'
    log('🔵 [AuthStore] isAuthenticated计算:', {
      hasAccessToken: !!accessToken.value,
      tokenLength: accessToken.value?.length ?? 0,
      tokenType: typeof accessToken.value,
      hasValidToken,
    })
    return hasValidToken
  })
  const userName = computed(() => user.value?.username || '')
  const userPhone = computed(() => user.value?.phone || '')

  // API基础URL: 使用 ApiClient 的 baseURL（由 import.meta.env.VITE_API_BASE_URL 控制）

  /**
   * 设置认证令牌
   */
  const setTokens = (access: string, refresh: string) => {
    log('🔵 [AuthStore] setTokens 被调用')
    log('🔵 [AuthStore] Access token type:', typeof access)
    log('🔵 [AuthStore] Access token length:', access ? access.length : 'null')
    log('🔵 [AuthStore] Refresh token type:', typeof refresh)
    log('🔵 [AuthStore] Refresh token length:', refresh ? refresh.length : 'null')

    // 验证token的有效性
    if (
      !access ||
      typeof access !== 'string' ||
      access.trim() === '' ||
      access === 'undefined' ||
      access === 'null'
    ) {
      logError('🔴 [AuthStore] Invalid access token provided')
      throw new Error('Invalid access token')
    }

    if (
      !refresh ||
      typeof refresh !== 'string' ||
      refresh.trim() === '' ||
      refresh === 'undefined' ||
      refresh === 'null'
    ) {
      logError('🔴 [AuthStore] Invalid refresh token provided')
      throw new Error('Invalid refresh token')
    }

    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)

    log('🔵 [AuthStore] Tokens 设置成功')
    log(
      '🔵 [AuthStore] localStorage access_token 存储成功:',
      !!localStorage.getItem('access_token')
    )
    log(
      '🔵 [AuthStore] localStorage refresh_token 存储成功:',
      !!localStorage.getItem('refresh_token')
    )
  }

  /**
   * 清理认证令牌
   */
  const clearTokens = () => {
    log('🔵 [AuthStore] clearTokens 被调用')
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
    log('🔵 [AuthStore] 所有认证信息已清理')
  }

  /**
   * 清理无效的localStorage数据
   */
  const cleanupInvalidTokens = () => {
    log('🔵 [AuthStore] 检查并清理无效token')

    const accessTokenValue = localStorage.getItem('access_token')
    const refreshTokenValue = localStorage.getItem('refresh_token')

    log(
      '🔵 [AuthStore] 当前localStorage access_token 存在:',
      !!accessTokenValue
    )
    log(
      '🔵 [AuthStore] 当前localStorage refresh_token 存在:',
      !!refreshTokenValue
    )

    let needsCleanup = false

    // 检查access_token
    if (
      accessTokenValue &&
      (accessTokenValue === 'undefined' ||
        accessTokenValue === 'null' ||
        accessTokenValue.trim() === '' ||
        typeof accessTokenValue !== 'string' ||
        accessTokenValue.length < 50) // JWT token应该很长，至少50个字符
    ) {
      warn('🟡 [AuthStore] 发现无效的access_token')
      needsCleanup = true
    }

    // 检查refresh_token
    if (
      refreshTokenValue &&
      (refreshTokenValue === 'undefined' ||
        refreshTokenValue === 'null' ||
        refreshTokenValue.trim() === '' ||
        typeof refreshTokenValue !== 'string' ||
        refreshTokenValue.length < 50) // JWT token应该很长，至少50个字符
    ) {
      warn('🟡 [AuthStore] 发现无效的refresh_token')
      needsCleanup = true
    }

    if (needsCleanup) {
      log('🔴 [AuthStore] 清理无效token')
      clearTokens()
      return false
    }

    log('🟢 [AuthStore] Token校验通过')
    return true
  }

  /**
   * 用户登录
   */
  const login = async (credentials: LoginCredentials) => {
    loading.value = true

    try {
      log('发送登录请求(ApiClient):', {
        username: credentials.username,
      })

      // 使用统一 ApiClient 调用后端登录接口（跳过鉴权头）
      const response = await api.post<LoginResponseData>(
        '/auth/login/',
        credentials,
        { skipAuth: true, skipErrorHandler: true }
      )
      log('🟢 [AuthStore] 登录响应(ApiClient):', {
        success: response.success,
        hasData: !!response.data,
      })

      if (response.success) {
        // 兼容多种返回结构：
        // 1) data.tokens.access|refresh
        // 2) data.access_token|refresh_token
        // 3) data.access|refresh（如刷新接口）
        const d: LoginResponseData = response.data || ({} as any)
        const access =
          d?.access_token || d?.access || d?.tokens?.access || (d as any)?.token
        const refresh = d?.refresh_token || d?.refresh || d?.tokens?.refresh
        const userInfo = (d as any)?.user

        log('🔵 [AuthStore] 解析登录令牌:', {
          hasAccess: !!access,
          hasRefresh: !!refresh,
          hasUser: !!userInfo,
        })

        if (!access || !refresh) {
          logError('🔴 [AuthStore] 登录响应缺少令牌')
          return { success: false, message: '登录响应缺少令牌' }
        }

        // 设置令牌与用户信息
        setTokens(access, refresh)
        user.value = userInfo ?? null
        if (userInfo) {
          localStorage.setItem('user_info', JSON.stringify(userInfo))
        }

        return { success: true }
      } else {
        const msg = response.message || '用户名或密码错误'
        return { success: false, message: msg }
      }
    } catch (error: any) {
      logError('🔴 [AuthStore] 登录失败', {
        message: error?.message,
        code: error?.code,
        raw: error,
      })
      return {
        success: false,
        message: error?.message || '登录失败，请稍后重试',
      }
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
      log('发送注册请求(ApiClient):', {
        username: data.username,
        phone: data.phone,
      })

      // 使用统一 ApiClient 调用后端注册接口（跳过鉴权头）
      const response = await api.post('/auth/register/', data, {
        skipAuth: true,
        skipErrorHandler: true,
      })
      log('🟢 [AuthStore] 注册响应(ApiClient):', response)

      if (response.success) {
        return { success: true, message: response.message || '注册成功' }
      }
      return { success: false, message: response.message || '注册失败' }
    } catch (error: any) {
      logError('🔴 [AuthStore] 注册失败', {
        message: error?.message,
        code: error?.code,
        raw: error,
      })
      return {
        success: false,
        message: error?.message || '注册失败，请稍后重试',
      }
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
      log('发送验证码请求:', { phone })

      const response = await api.post(
        '/auth/send-code/',
        { phone },
        { skipAuth: true, skipErrorHandler: true }
      )
      log('验证码响应(ApiClient):', response)

      if (response.success) {
        const devCode = (response as any)?.data?.code
        return {
          success: true,
          message: response.message || '验证码发送成功',
          code: devCode,
        }
      } else {
        throw new Error(response.message || '验证码发送失败')
      }
    } catch (error: any) {
      logError('验证码发送失败', error)
      const errorMessage = error?.message || '验证码发送失败，请稍后重试'
      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登出
   */
  const logout = async () => {
    log('🔵 [AuthStore] === Logout Started ===')
    log('🔵 [AuthStore] Current access token exists:', !!accessToken.value)
    log('🔵 [AuthStore] Current refresh token exists:', !!refreshToken.value)
    log('🔵 [AuthStore] User info exists:', !!user.value)

    try {
      if (accessToken.value) {
        log('🔵 [AuthStore] 发送登出请求到服务器(ApiClient)')
        log('🔵 [AuthStore] Request endpoint:', '/auth/logout/')
        log(
          '🔵 [AuthStore] VITE_API_BASE_URL (effective):',
          (import.meta as any)?.env?.VITE_API_BASE_URL ||
            '(not set, using default)'
        )
        log('🔵 [AuthStore] Request payload: refresh token exists')

        const response = await api.post('/auth/logout/', {
          refresh_token: refreshToken.value,
        })

        log('🔵 [AuthStore] 登出响应数据:', {
          success: response.success,
          message: response.message,
        })

        if (response.success) {
        log('🟢 [AuthStore] 服务器登出成功')
        } else {
        warn('🟡 [AuthStore] 登出API返回失败', response.message)
        }
      } else {
        log('🟡 [AuthStore] 没有访问令牌，跳过服务器登出请求')
      }
    } catch (error: any) {
      logError('🔴 [AuthStore] 登出API调用失败', {
        error: error,
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString(),
      })

      // 即使API调用失败，也要清除本地token
      const errorMessage = error?.message || '登出失败'
      warn('🔴 [AuthStore] 登出错误详情', errorMessage)
    } finally {
      // 无论API调用是否成功，都清除本地认证信息
      log('🔵 [AuthStore] 开始清除本地认证信息')
      log(
        '🔵 [AuthStore] 清除前 - localStorage access_token:',
        !!localStorage.getItem('access_token')
      )
      log(
        '🔵 [AuthStore] 清除前 - localStorage refresh_token:',
        !!localStorage.getItem('refresh_token')
      )
      log(
        '🔵 [AuthStore] 清除前 - localStorage user_info:',
        !!localStorage.getItem('user_info')
      )

      clearTokens()

      log(
        '🔵 [AuthStore] 清除后 - localStorage access_token:',
        !!localStorage.getItem('access_token')
      )
      log(
        '🔵 [AuthStore] 清除后 - localStorage refresh_token:',
        !!localStorage.getItem('refresh_token')
      )
      log(
        '🔵 [AuthStore] 清除后 - localStorage user_info:',
        !!localStorage.getItem('user_info')
      )
      log('🔵 [AuthStore] 清除后 - store accessToken:', !!accessToken.value)
      log('🔵 [AuthStore] 清除后 - store user:', user.value)
      log('🟢 [AuthStore] 本地认证信息已清除')
      log('🔵 [AuthStore] === Logout Completed ===')
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
      const response = await api.post<{
        access_token?: string
        refresh_token?: string
        access?: string
        refresh?: string
      }>('/auth/refresh/', { refresh_token: refreshToken.value })

      if (response.success) {
        const data = response.data || ({} as any)
        const access = data.access_token || data.access
        const refresh = data.refresh_token || data.refresh

        log('🔵 [AuthStore] 刷新token成功:', access)

        if (!access) {
          throw new Error('刷新token响应中缺少access_token')
        }

        accessToken.value = access
        localStorage.setItem('access_token', access)

        if (refresh) {
          refreshToken.value = refresh
          localStorage.setItem('refresh_token', refresh)
        }

        return access
      } else {
        throw new Error(response.message || '令牌刷新失败')
      }
    } catch (error) {
      logError('令牌刷新失败', error)
      clearTokens()
      throw error
    }
  }

  /**
   * 初始化认证状态
   */
  const initializeAuth = () => {
    log('🔵 [AuthStore] 初始化认证状态')

    // 先清理无效token
    const hasValidTokens = cleanupInvalidTokens()

    if (!hasValidTokens) {
      log('🟡 [AuthStore] 没有有效token，初始化停止')
      return
    }

    const savedAccessToken = localStorage.getItem('access_token')
    const savedRefreshToken = localStorage.getItem('refresh_token')
    const savedUserInfo = localStorage.getItem('user_info')

    log('🔵 [AuthStore] 保存的token情况:')
    log('  - access_token 存在:', !!savedAccessToken)
    log('  - refresh_token 存在:', !!savedRefreshToken)
    log('  - user_info 存在:', !!savedUserInfo)

    if (savedAccessToken && savedRefreshToken) {
      accessToken.value = savedAccessToken
      refreshToken.value = savedRefreshToken
      log('🟢 [AuthStore] Token恢复成功')
    }

    if (savedUserInfo) {
      try {
        user.value = JSON.parse(savedUserInfo)
        log('🟢 [AuthStore] 用户信息恢复成功:', user.value?.username)
      } catch (error) {
        logError('🔴 [AuthStore] 解析用户信息失败', error)
        localStorage.removeItem('user_info')
      }
    }

    log('🟢 [AuthStore] 初始化完成，认证状态:', isAuthenticated.value)
  }

  /**
   * 检查令牌是否有效
   */
  const checkTokenValidity = async () => {
    if (!accessToken.value) {
      return false
    }

    try {
      const response = await api.get('/auth/verify/')
      return !!response.success
    } catch (error) {
      logError('令牌验证失败', error)
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
    cleanupInvalidTokens,
  }
})
