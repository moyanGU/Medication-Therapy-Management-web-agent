/**
 * API客户端封装
 * 统一处理HTTP请求和响应，包括错误处理、认证、拦截器等
 */

// API响应接口
interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  code?: number
}

// 请求配置接口
interface RequestConfig extends RequestInit {
  timeout?: number
  skipAuth?: boolean
  skipErrorHandler?: boolean
  params?: Record<string, any>
  isFormData?: boolean
}

// 错误类型
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

/**
 * API客户端类
 */
class ApiClient {
  private baseURL: string
  private defaultTimeout: number
  
  constructor(baseURL: string = 'http://127.0.0.1:8000/api', timeout: number = 10000) {
    this.baseURL = baseURL
    this.defaultTimeout = timeout
  }

  /**
   * 获取认证token
   */
  private getAuthToken(): string | null {
    // 优先使用access_token，兼容旧的token键名
    return localStorage.getItem('access_token') || localStorage.getItem('token')
  }

  /**
   * 构建完整URL
   */
  private buildURL(endpoint: string, params?: Record<string, any>): string {
    let url: string
    if (endpoint.startsWith('http')) {
      url = endpoint
    } else {
      url = `${this.baseURL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`
    }
    
    // 添加查询参数
    if (params && Object.keys(params).length > 0) {
      const searchParams = new URLSearchParams()
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          searchParams.append(key, String(value))
        }
      })
      const queryString = searchParams.toString()
      if (queryString) {
        url += (url.includes('?') ? '&' : '?') + queryString
      }
    }
    
    return url
  }

  /**
   * 构建请求头
   */
  private buildHeaders(config: RequestConfig = {}): HeadersInit {
    const headers: Record<string, string> = {}

    if (!config.isFormData) {
      headers['Content-Type'] = 'application/json'
    }

    // 添加认证头
    if (!config.skipAuth) {
      const token = this.getAuthToken()
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }

    // 合并自定义头
    if (config.headers) {
      Object.assign(headers, config.headers)
    }

    return headers
  }

  /**
   * 处理响应
   */
  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    // 处理204 No Content响应
    if (response.status === 204) {
      return {
        success: true,
        data: null as T
      }
    }
    
    let data: any
    
    try {
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        data = await response.json()
      } else {
        data = await response.text()
      }
    } catch (error) {
      throw new ApiError('响应解析失败', response.status, response)
    }

    if (!response.ok) {
      const message = data?.message || `HTTP ${response.status}: ${response.statusText}`
      throw new ApiError(message, response.status, response)
    }

    // 如果响应数据不是标准格式，包装成标准格式
    if (typeof data === 'object' && data !== null && 'success' in data) {
      return data as ApiResponse<T>
    }

    // 处理双重data结构：如果后端返回 { data: { data: [...] } }，则提取内层data
    if (typeof data === 'object' && data !== null && 'data' in data) {
      return {
        success: true,
        data: data.data as T
      }
    }

    return {
      success: true,
      data: data as T
    }
  }

  /**
   * 处理错误
   */
  private handleError(error: any, config: RequestConfig): never {
    console.error('API请求错误:', error)

    // 如果跳过错误处理，直接抛出
    if (config.skipErrorHandler) {
      throw error
    }

    // 处理不同类型的错误
    if (error instanceof ApiError) {
      // 401 未授权 - 清除token并跳转登录
      if (error.code === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        localStorage.removeItem('user_info')
        window.location.href = '/login'
      }
      throw error
    }

    // 网络错误
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new ApiError('网络连接失败，请检查网络设置', 0)
    }

    // 超时错误
    if (error.name === 'AbortError') {
      throw new ApiError('请求超时，请稍后重试', 0)
    }

    // 其他错误
    throw new ApiError(error.message || '请求失败', 0)
  }

  /**
   * 发送请求
   */
  private async request<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const { params, ...requestConfig } = config
    const url = this.buildURL(endpoint, params)
    const timeout = config.timeout || this.defaultTimeout
    
    // 创建AbortController用于超时控制
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      const finalRequestConfig: RequestInit = {
        ...requestConfig,
        headers: this.buildHeaders(config),
        signal: controller.signal,
      }

      console.log(`API请求: ${config.method || 'GET'} ${url}`, {
        headers: requestConfig.headers,
        body: config.body
      })

      const response = await fetch(url, finalRequestConfig)
      const result = await this.handleResponse<T>(response)
      
      console.log(`API响应: ${config.method || 'GET'} ${url}`, result)
      
      return result
    } catch (error) {
      this.handleError(error, config)
    } finally {
      clearTimeout(timeoutId)
    }
  }

  /**
   * GET请求
   */
  async get<T = any>(endpoint: string, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'GET',
    })
  }

  /**
   * POST请求
   */
  async post<T = any>(
    endpoint: string,
    data?: any,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const isForm = typeof FormData !== 'undefined' && data instanceof FormData
    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      isFormData: isForm || config.isFormData,
      body: isForm ? data : (data ? JSON.stringify(data) : undefined),
    })
  }

  /**
   * PUT请求
   */
  async put<T = any>(
    endpoint: string,
    data?: any,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const isForm = typeof FormData !== 'undefined' && data instanceof FormData
    return this.request<T>(endpoint, {
      ...config,
      method: 'PUT',
      isFormData: isForm || config.isFormData,
      body: isForm ? data : (data ? JSON.stringify(data) : undefined),
    })
  }

  /**
   * PATCH请求
   */
  async patch<T = any>(
    endpoint: string,
    data?: any,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const isForm = typeof FormData !== 'undefined' && data instanceof FormData
    return this.request<T>(endpoint, {
      ...config,
      method: 'PATCH',
      isFormData: isForm || config.isFormData,
      body: isForm ? data : (data ? JSON.stringify(data) : undefined),
    })
  }

  /**
   * DELETE请求
   */
  async delete<T = any>(endpoint: string, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'DELETE',
    })
  }

  /**
   * 文件上传
   */
  async upload<T = any>(
    endpoint: string,
    file: File,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const formData = new FormData()
    formData.append('file', file)

    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      isFormData: true,
      body: formData,
    })
  }

  /**
   * 下载文件
   */
  async download(
    endpoint: string,
    filename?: string,
    config: RequestConfig = {}
  ): Promise<void> {
    // 对下载场景特殊处理：
    // 1) http(s) 绝对URL：直接使用
    // 2) 以 '/' 开头：按后端根域拼接，避免叠加 /api 前缀导致 404
    // 3) 其他：按 buildURL 常规拼接到 baseURL 之下
    let url: string
    try {
      const base = new URL(this.baseURL)
      if (endpoint.startsWith('http')) {
        url = endpoint
      } else if (endpoint.startsWith('/')) {
        url = `${base.protocol}//${base.host}${endpoint}`
      } else {
        url = this.buildURL(endpoint)
      }
    } catch (e) {
      // 回退策略：在极端情况下仍使用旧逻辑
      url = this.buildURL(endpoint)
    }

    const headers = this.buildHeaders(config)

    try {
      console.log('🔵 [ApiClient.download] 开始下载', { url, filename })
      const response = await fetch(url, {
        ...config,
        headers,
      })

      if (!response.ok) {
        throw new ApiError(`下载失败: ${response.status} ${response.statusText}`, response.status, response)
      }

      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || 'download'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      window.URL.revokeObjectURL(downloadUrl)
      console.log('🟢 [ApiClient.download] 下载完成')
    } catch (error) {
      console.error('🔴 [ApiClient.download] 下载异常', error)
      this.handleError(error, config)
    }
  }
}

// 创建默认API客户端实例
export const api = new ApiClient()

// 导出类型和错误类
export { ApiClient, ApiError }
export type { ApiResponse, RequestConfig }

// 便捷方法
export const { get, post, put, patch, delete: del, upload, download } = api