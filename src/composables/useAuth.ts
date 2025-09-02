import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

/**
 * 认证相关的组合式函数
 * 提供认证状态检查、登录跳转等功能
 */
export function useAuth() {
  const authStore = useAuthStore()
  const router = useRouter()

  // 计算属性
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const user = computed(() => authStore.user)
  const isLoading = computed(() => authStore.loading)

  /**
   * 要求用户登录
   * 如果未登录，跳转到登录页
   */
  const requireAuth = (redirectPath?: string) => {
    if (!isAuthenticated.value) {
      const currentPath = redirectPath || router.currentRoute.value.fullPath
      router.push({
        path: '/login',
        query: { redirect: currentPath }
      })
      return false
    }
    return true
  }

  /**
   * 检查是否为访客（未登录）
   * 如果已登录，跳转到仪表板
   */
  const requireGuest = () => {
    if (isAuthenticated.value) {
      router.push('/dashboard')
      return false
    }
    return true
  }

  /**
   * 登录
   */
  const login = async (credentials: {
    username: string
    password: string
    remember?: boolean
  }) => {
    const result = await authStore.login(credentials)
    
    if (result.success) {
      // 登录成功，检查是否有重定向路径
      const redirect = router.currentRoute.value.query.redirect as string
      if (redirect && redirect !== '/login') {
        router.push(redirect)
      } else {
        router.push('/dashboard')
      }
    }
    
    return result
  }

  /**
   * 注册
   */
  const register = async (data: {
    username: string
    phone: string
    password: string
    confirmPassword: string
    verificationCode: string
    agreeTerms: boolean
  }) => {
    const registerData = {
      username: data.username,
      phone: data.phone,
      password: data.password,
      verification_code: data.verificationCode
    }
    const result = await authStore.register(registerData)
    
    if (result.success) {
      // 注册成功，跳转到登录页
      router.push({
        path: '/login',
        query: { message: '注册成功，请登录' }
      })
    }
    
    return result
  }

  /**
   * 登出
   */
  const logout = async () => {
    await authStore.logout()
    router.push('/login')
  }

  /**
   * 发送验证码
   */
  const sendVerificationCode = async (phone: string) => {
    return await authStore.sendVerificationCode(phone)
  }

  /**
   * 初始化用户状态
   */
  const initializeAuth = () => {
    authStore.initializeAuth()
  }

  /**
   * 检查权限
   * 可以扩展为基于角色的权限检查
   */
  const hasPermission = (permission: string): boolean => {
    // TODO: 实现基于角色的权限检查
    // 目前只检查是否已登录
    return isAuthenticated.value
  }

  /**
   * 检查是否为管理员
   */
  const isAdmin = computed(() => {
    // TODO: 根据用户角色判断
    return user.value?.role === 'admin'
  })

  return {
    // 状态
    isAuthenticated,
    user,
    isLoading,
    isAdmin,
    
    // 方法
    requireAuth,
    requireGuest,
    login,
    register,
    logout,
    sendVerificationCode,
    initializeAuth,
    hasPermission,
  }
}

/**
 * 认证守卫装饰器
 * 用于组件中快速检查认证状态
 */
export function withAuth<T extends (...args: any[]) => any>(fn: T): T {
  return ((...args: any[]) => {
    const { requireAuth } = useAuth()
    if (requireAuth()) {
      return fn(...args)
    }
  }) as T
}

/**
 * 访客守卫装饰器
 * 用于组件中快速检查访客状态
 */
export function withGuest<T extends (...args: any[]) => any>(fn: T): T {
  return ((...args: any[]) => {
    const { requireGuest } = useAuth()
    if (requireGuest()) {
      return fn(...args)
    }
  }) as T
}