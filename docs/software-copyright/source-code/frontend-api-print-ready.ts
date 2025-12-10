// =============================================================================
// MTM-用药助手 - API客户端封装
// 文件: src/utils/api.ts
// 页码: 8-13/60
// =============================================================================

/**
 * API客户端统一封装
 * 提供统一的HTTP请求处理、错误处理、认证管理和响应解析
 */

// ==================== 接口定义 ====================

/**
 * API响应接口
 * 标准化后端响应格式
 */
interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  code?: number
}

/**
 * 请求配置接口
 * 扩展原生RequestInit，增加自定义配置
 */
interface RequestConfig extends RequestInit {
  timeout?: number
  skipAuth?: boolean
  skipErrorHandler?: boolean
  params?: Record<string, any>
  isFormData?: boolean
  responseType?: 'json' | 'text' | 'blob'
}

/**
 * API错误类
 * 统一错误处理，包含错误码和原始响应
 */
class ApiError extends Error {
  code: number
  response?: Response
  
  constructor(message: string, code: number, response?: Response) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.response = response
  }
}

// ==================== 工具函数 ====================

/**
 * 安全解析API基础URL
 * 支持多环境配置，提供优雅降级
 */
function resolveApiBaseURL(): string {
  const envVal = (typeof import.meta !== 'undefined' && 
                 (import.meta as any).env && 
                 (import.meta as any).env.VITE_API_BASE_URL) || ''
  
  const fromEnv = typeof envVal === 'string' ? envVal.trim() : ''
  
  if (fromEnv) return fromEnv
  
  // 浏览器环境：使用当前域名
  if (typeof window !== 'undefined' && window.location) {
    return `${window.location.origin}/api`
  }
  
  // SSR/测试环境兜底：使用相对路径
  return '/api'
}

/**
 * 构建完整URL
 * 处理查询参数和路径拼接
 */
function buildFullURL(url: string, params?: Record<string, any>): string {
  const baseURL = resolveApiBaseURL()
  let fullURL = url.startsWith('http') ? url : `${baseURL}${url}`
  
  // 处理查询参数
  if (params && Object.keys(params).length > 0) {
    const searchParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => searchParams.append(key, v.toString()))
        } else {
          searchParams.append(key, value.toString())
        }
      }
    })
    
    fullURL += `${fullURL.includes('?') ? '&' : '?'}${searchParams.toString()}`
  }
  
  return fullURL
}

/**
 * 超时控制器
 * 请求超时自动取消
 */
function createTimeoutController(timeout: number): AbortController {
  const controller = new AbortController()
  
  setTimeout(() => {
    controller.abort()
  }, timeout)
  
  return controller
}

/**
 * 处理响应数据
 * 根据Content-Type自动解析响应格式
 */
async function handleResponse<T>(
  response: Response, 
  responseType?: string
): Promise<T> {
  if (!response.ok) {
    throw new ApiError(
      `HTTP错误: ${response.status} ${response.statusText}`,
      response.status,
      response
    )
  }
  
  const contentType = response.headers.get('content-type') || ''
  
  // 根据配置或Content-Type决定解析方式
  if (responseType === 'text' || contentType.includes('text/plain')) {
    return response.text() as unknown as T
  }
  
  if (responseType === 'blob' || contentType.includes('application/octet-stream')) {
    return response.blob() as unknown as T
  }
  
  // 默认JSON解析
  try {
    const data = await response.json()
    return data as T
  } catch (error) {
    throw new ApiError(
      '响应解析失败: 无效的JSON格式',
      500,
      response
    )
  }
}

/**
 * 处理请求错误
 * 统一错误处理和用户提示
 */
function handleRequestError(error: any, config: RequestConfig): never {
  if (error instanceof ApiError) {
    throw error
  }
  
  if (error.name === 'AbortError') {
    throw new ApiError('请求超时', 408)
  }
  
  if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
    throw new ApiError('网络连接失败', 0)
  }
  
  throw new ApiError(`请求失败: ${error.message}`, 500)
}

// ==================== 核心API客户端 ====================

/**
 * 创建API客户端实例
 * 支持自定义配置和中间件
 */
function createApiClient(baseConfig: RequestConfig = {}) {
  const defaultConfig: RequestConfig = {
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 30000, // 30秒超时
    ...baseConfig
  }
  
  /**
   * 核心请求方法
   */
  async function request<T = any>(
    url: string, 
    config: RequestConfig = {}
  ): Promise<T> {
    const mergedConfig: RequestConfig = {
      ...defaultConfig,
      ...config,
      headers: {
        ...defaultConfig.headers,
        ...config.headers,
      }
    }
    
    const {
      timeout,
      params,
      responseType,
      skipAuth,
      skipErrorHandler,
      isFormData,
      ...fetchConfig
    } = mergedConfig
    
    // 构建完整URL
    const fullURL = buildFullURL(url, params)
    
    // 处理FormData
    if (isFormData && fetchConfig.body && !(fetchConfig.body instanceof FormData)) {
      const formData = new FormData()
      Object.entries(fetchConfig.body as Record<string, any>).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          formData.append(key, value)
        }
      })
      fetchConfig.body = formData
    }
    
    // 添加认证token
    if (!skipAuth) {
      const token = localStorage.getItem('access_token')
      if (token) {
        fetchConfig.headers = {
          ...fetchConfig.headers,
          'Authorization': `Bearer ${token}`
        }
      }
    }
    
    // 创建超时控制器
    const controller = createTimeoutController(timeout || 30000)
    
    try {
      const response = await fetch(fullURL, {
        ...fetchConfig,
        signal: controller.signal
      })
      
      const data = await handleResponse<T>(response, responseType)
      return data
      
    } catch (error) {
      if (!skipErrorHandler) {
        handleRequestError(error, mergedConfig)
      }
      throw error
    }
  }
  
  // 便捷方法
  return {
    get: <T = any>(url: string, config?: RequestConfig) => 
      request<T>(url, { ...config, method: 'GET' }),
    
    post: <T = any>(url: string, data?: any, config?: RequestConfig) => 
      request<T>(url, { ...config, method: 'POST', body: JSON.stringify(data) }),
    
    put: <T = any>(url: string, data?: any, config?: RequestConfig) => 
      request<T>(url, { ...config, method: 'PUT', body: JSON.stringify(data) }),
    
    patch: <T = any>(url: string, data?: any, config?: RequestConfig) => 
      request<T>(url, { ...config, method: 'PATCH', body: JSON.stringify(data) }),
    
    delete: <T = any>(url: string, config?: RequestConfig) => 
      request<T>(url, { ...config, method: 'DELETE' }),
    
    // 文件上传
    upload: <T = any>(url: string, formData: FormData, config?: RequestConfig) =>
      request<T>(url, { 
        ...config, 
        method: 'POST', 
        body: formData,
        headers: {
          ...config?.headers,
        }
      })
  }
}

// 创建默认API实例
export const api = createApiClient()

// 导出类型和工具
export type { ApiResponse, RequestConfig }
export { ApiError, createApiClient }

export default api