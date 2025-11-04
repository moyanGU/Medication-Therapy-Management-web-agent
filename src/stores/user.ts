import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'

// 顶层类型声明，供store导出类型安全引用，避免私有类型泄露错误
export interface UserInfo {
  id: number
  username: string
  phone: string
  email?: string
  birthDate?: string // 对应后端 birth_date
  gender?: 'male' | 'female' | 'other'
  emergencyContact?: string // 对应后端 emergency_contact
  emergencyPhone?: string // 对应后端 emergency_phone
  avatar?: string
  createdAt?: string // 对应后端 created_at
  updatedAt?: string // 对应后端 updated_at
}

export interface LoginCredentials {
  username: string
  password: string
  remember?: boolean
}

export interface RegisterData {
  username: string
  phone: string
  password: string
  confirmPassword: string
  verificationCode: string
  agreeTerms: boolean
}

/**
 * 用户状态管理
 * 管理用户登录状态、个人信息等
 */
export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string | null>(
    // 兼容两种本地存储的token键名，优先access_token
    localStorage.getItem('access_token') || localStorage.getItem('token')
  )
  const userInfo = ref<UserInfo | null>(null)
  const isLoading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() => userInfo.value?.username || '')
  const userPhone = computed(() => userInfo.value?.phone || '')

  // 与后端序列化器对齐的用户信息接口：已上移到模块顶层
  // 登录信息接口：已上移到模块顶层
  // 注册信息接口：已上移到模块顶层

  // 登录响应接口
  // interface LoginResponse {
  //   token: string
  //   user: UserInfo
  // }

  /**
   * DTO -> Store 映射（snake_case -> camelCase）
   */
  const mapDtoToUserInfo = (dto: any): UserInfo => {
    const mapped: UserInfo = {
      id: dto?.id,
      username: dto?.username ?? '',
      phone: dto?.phone ?? '',
      email: dto?.email ?? '',
      birthDate: dto?.birth_date ?? '',
      gender: dto?.gender,
      emergencyContact: dto?.emergency_contact ?? '',
      emergencyPhone: dto?.emergency_phone ?? '',
      avatar: dto?.avatar ?? '',
      createdAt: dto?.created_at ?? '',
      updatedAt: dto?.updated_at ?? ''
    }
    console.debug('[user.store] mapDtoToUserInfo ->', dto, '=>', mapped)
    return mapped
  }

  /**
   * Store -> API 映射（camelCase -> snake_case），并按白名单过滤出可写字段
   */
  const buildUpdatePayload = (updates: Partial<UserInfo>) => {
    const payload: Record<string, any> = {}
    // 仅允许后端可写字段：email, avatar, birth_date, gender, emergency_contact, emergency_phone
    if (Object.prototype.hasOwnProperty.call(updates, 'email')) payload.email = updates.email
    if (Object.prototype.hasOwnProperty.call(updates, 'avatar')) payload.avatar = updates.avatar
    if (Object.prototype.hasOwnProperty.call(updates, 'birthDate')) payload.birth_date = updates.birthDate
    if (Object.prototype.hasOwnProperty.call(updates, 'gender')) payload.gender = updates.gender
    if (Object.prototype.hasOwnProperty.call(updates, 'emergencyContact')) payload.emergency_contact = updates.emergencyContact
    if (Object.prototype.hasOwnProperty.call(updates, 'emergencyPhone')) payload.emergency_phone = updates.emergencyPhone

    console.debug('[user.store] buildUpdatePayload <-', updates, '=>', payload)
    return payload
  }

  /**
   * 用户登录
   */
  const login = async (credentials: LoginCredentials) => {
    isLoading.value = true
    try {
      const response = await api.post('/auth/login/', credentials, { skipAuth: true })
      
      if (response.success) {
        // 兼容多种返回结构：data.tokens.access|refresh / data.access_token|refresh_token / data.access|refresh
        const d: any = response.data || {}
        const access = d?.access_token || d?.access || d?.tokens?.access
        const refresh = d?.refresh_token || d?.refresh || d?.tokens?.refresh
        const u = d?.user

        if (!access || !refresh) {
          throw new Error('登录响应缺少令牌(access/refresh)')
        }
        
        // 使用 AuthStore 统一设置令牌与Axios头
        const { useAuthStore } = await import('@/stores/auth')
        const auth = useAuthStore()
        auth.setTokens(access, refresh)

        token.value = access
        userInfo.value = u ? mapDtoToUserInfo(u) : null

        // 本地持久化
        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)
        if (credentials.remember && userInfo.value) {
          localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
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
      const response = await api.post('/auth/register/', data, { skipAuth: true })
      
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
    // 若auth模块已设置全局Authorization，此处不强依赖本地token判断
    isLoading.value = true
    try {
      const response = await api.get('/user/profile/')
      
      if (response.success) {
        // 兼容双层 data 结构：{ success, data: { data: {...} } }
        const rawDto: any = (response.data && (response.data as any).data !== undefined)
          ? (response.data as any).data
          : response.data
        console.log('[user.store] fetchUserInfo 原始DTO:', rawDto)
        const mapped = mapDtoToUserInfo(rawDto)
        userInfo.value = mapped
        localStorage.setItem('userInfo', JSON.stringify(mapped))
      } else {
        console.warn('[user.store] 获取用户信息失败:', response.message)
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
      const payload = buildUpdatePayload(updates)
      const response = await api.patch('/user/profile/', payload)
      
      if (response.success) {
        // 兼容双层 data 结构
        const rawDto: any = (response.data && (response.data as any).data !== undefined)
          ? (response.data as any).data
          : response.data
        console.log('[user.store] updateUserInfo 原始DTO:', rawDto)
        const mapped = mapDtoToUserInfo(rawDto)
        userInfo.value = mapped
        localStorage.setItem('userInfo', JSON.stringify(mapped))
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
        await api.post('/auth/logout/')
      }
    } catch (error) {
      console.error('登出API调用失败:', error)
    } finally {
      // 清除本地状态
      token.value = null
      userInfo.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('access_token')
      localStorage.removeItem('userInfo')
    }
  }

  /**
   * 初始化用户状态
   * 从本地存储恢复用户信息
   */
  const initializeUser = () => {
    const savedToken = localStorage.getItem('access_token') || localStorage.getItem('token')
    const savedUserInfo = localStorage.getItem('userInfo')
    
    if (savedToken) {
      token.value = savedToken
    }
    
    if (savedUserInfo) {
      try {
        const parsed = JSON.parse(savedUserInfo)
        // 兼容历史数据：若是后端原始DTO，进行一次映射；否则直接使用
        userInfo.value = parsed && (parsed.birth_date || parsed.created_at)
          ? mapDtoToUserInfo(parsed)
          : parsed
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
      const response = await api.post('/auth/send-code/', { phone }, { skipAuth: true, skipErrorHandler: true })
      
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