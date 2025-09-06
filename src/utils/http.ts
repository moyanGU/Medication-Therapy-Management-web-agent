import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'
import { api, type ApiResponse } from '@/utils/api'

/**
 * HTTP请求工具类
 * 基于axios封装，提供统一的请求和响应处理
 */
class HttpClient {
  private instance: AxiosInstance
  private useApiProxy = true

  constructor() {
    // 创建axios实例
    this.instance = axios.create({
      baseURL: 'http://127.0.0.1:8000', // 后端API基础URL
      timeout: 10000, // 请求超时时间
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 设置请求拦截器
    this.setupRequestInterceptor()
    
    // 设置响应拦截器
    this.setupResponseInterceptor()
  }

  /**
   * 归一化接口地址：
   * - 兼容老代码传入 '/api/xxx'，统一移除 '/api' 前缀后交给新 api 客户端（其 baseURL 已包含 /api）
   */
  private normalizeEndpoint(url: string): string {
    if (!url) return url
    try {
      if (url.startsWith('http://') || url.startsWith('https://')) return url
      return url.startsWith('/api/') ? url.slice(4) : url
    } catch {
      return url
    }
  }

  /**
   * 将 ApiResponse 包装为 AxiosResponse 兼容结构
   */
  private toAxiosResponse<T>(resp: ApiResponse<T>, config?: AxiosRequestConfig): AxiosResponse<ApiResponse<T>> {
    return {
      data: resp,
      status: 200,
      statusText: 'OK',
      headers: {},
      config: (config || {}) as any,
      request: {}
    }
  }

  /**
   * GET请求
   */
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    if (!this.useApiProxy) {
      return this.instance.get(url, config) as any
    }
    const endpoint = this.normalizeEndpoint(url)
    console.log('🔵 [http->api] GET', { url, endpoint, params: config?.params })
    const resp = await api.get<T>(endpoint, { params: config?.params, headers: config?.headers })
    return this.toAxiosResponse<T>(resp, config)
  }

  /**
   * POST请求
   */
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    if (!this.useApiProxy) {
      return this.instance.post(url, data, config) as any
    }
    const endpoint = this.normalizeEndpoint(url)
    console.log('🔵 [http->api] POST', { url, endpoint, data })
    const resp = await api.post<T>(endpoint, data, { headers: config?.headers })
    return this.toAxiosResponse<T>(resp, config)
  }

  /**
   * PUT请求
   */
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    if (!this.useApiProxy) {
      return this.instance.put(url, data, config) as any
    }
    const endpoint = this.normalizeEndpoint(url)
    console.log('🔵 [http->api] PUT', { url, endpoint, data })
    const resp = await api.put<T>(endpoint, data, { headers: config?.headers })
    return this.toAxiosResponse<T>(resp, config)
  }

  /**
   * PATCH请求
   */
  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    if (!this.useApiProxy) {
      return this.instance.patch(url, data, config) as any
    }
    const endpoint = this.normalizeEndpoint(url)
    console.log('🔵 [http->api] PATCH', { url, endpoint, data })
    const resp = await api.patch<T>(endpoint, data, { headers: config?.headers })
    return this.toAxiosResponse<T>(resp, config)
  }

  /**
   * DELETE请求
   */
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    if (!this.useApiProxy) {
      return this.instance.delete(url, config) as any
    }
    const endpoint = this.normalizeEndpoint(url)
    console.log('🔵 [http->api] DELETE', { url, endpoint })
    const resp = await api.delete<T>(endpoint, { headers: config?.headers })
    return this.toAxiosResponse<T>(resp, config)
  }

  /**
   * 上传文件
   */
  upload<T = any>(url: string, file: File, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
  async upload<T = any>(url: string, file: File, config?: AxiosRequestConfig): Promise<AxiosResponse<ApiResponse<T>>> {
    if (!this.useApiProxy) {
      // 回退到 axios 处理
      const formData = new FormData()
      formData.append('file', file)
      return this.instance.post(url, formData, {
        ...config,
        headers: {
          'Content-Type': 'multipart/form-data',
          ...config?.headers
        }
      }) as any
    }
    const endpoint = this.normalizeEndpoint(url)
    console.log('🔵 [http->api] UPLOAD', { url, endpoint })
    const resp = await api.upload<T>(endpoint, file, { headers: config?.headers })
    return this.toAxiosResponse<T>(resp, config)
  }

  /**
   * 下载文件
   */
  download(url: string, filename?: string, config?: AxiosRequestConfig): Promise<void>
  async download(url: string, filename?: string, config?: AxiosRequestConfig): Promise<void> {
    if (!this.useApiProxy) {
      return this.instance.get(url, {
        ...config,
        responseType: 'blob'
      }).then(response => {
        const blob = new Blob([response.data])
        const downloadUrl = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = filename || 'download'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(downloadUrl)
      })
    }
    const endpoint = this.normalizeEndpoint(url)
    console.log('🔵 [http->api] DOWNLOAD', { url, endpoint })
    return api.download(endpoint, filename)
  }

  /**
   * 设置请求拦截器
   */
  private setupRequestInterceptor() {
    this.instance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        console.log('=== HTTP Request Debug ===')
        console.log('URL:', config.url)
        console.log('Method:', config.method)
        console.log('Token exists:', !!token)
        console.log('Token type:', typeof token)
        console.log('Token value:', token)
        console.log('Token length:', token ? token.length : 'null')
        console.log('Token === "undefined":', token === 'undefined')
        console.log('Token === "null":', token === 'null')
        
        // 检查token是否为字符串"undefined"或"null"
        if (token && token !== 'undefined' && token !== 'null' && token.trim() !== '') {
          config.headers.Authorization = `Bearer ${token}`
          console.log('Authorization header set:', config.headers.Authorization.substring(0, 50) + '...')
        } else {
          console.log('No valid token found. Token value:', token)
          console.log('localStorage keys:', Object.keys(localStorage))
          console.log('All localStorage data:')
          for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i)
            if (key) {
              console.log(`  ${key}: ${localStorage.getItem(key)?.substring(0, 50)}...`)
            }
          }
        }
        console.log('=== End Debug ===')
        
        console.log('发送请求:', {
          method: config.method?.toUpperCase(),
          url: config.url,
          data: config.data,
          params: config.params
        })
        
        return config
      },
      (error) => {
        console.error('Request interceptor error:', error)
        return Promise.reject(error)
      }
    )
  }

  /**
   * 设置响应拦截器
   */
  private setupResponseInterceptor() {
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log('🟢 [HTTP] 成功响应:', {
          status: response.status,
          url: response.config.url,
          method: response.config.method?.toUpperCase(),
          dataSize: JSON.stringify(response.data).length + ' bytes'
        })
        
        return response
      },
      async (error) => {
        console.error('🔴 [HTTP] 请求失败:', {
          message: error.message,
          status: error.response?.status,
          url: error.config?.url,
          method: error.config?.method?.toUpperCase(),
          timestamp: new Date().toISOString()
        })
        
        // 处理认证错误
        if (error.response?.status === 401) {
          console.warn('🟠 [HTTP] 检测到401认证错误，尝试刷新token')
          
          // 尝试刷新token
          const authStore = useAuthStore()
          try {
            await authStore.refreshAccessToken()
            console.log('🟢 [HTTP] Token刷新成功，重试原请求')
            
            // 重试原请求
            const originalRequest = error.config
            if (originalRequest) {
              // 更新请求头中的token
              const newToken = localStorage.getItem('access_token')
              if (newToken) {
                originalRequest.headers.Authorization = `Bearer ${newToken}`
              }
              return this.instance.request(originalRequest)
            }
          } catch (refreshError) {
            console.error('🔴 [HTTP] Token刷新失败，执行登出:', refreshError)
            
            console.log('🔴 [HTTP] 401 ERROR - PAUSING FOR DEBUG')
            debugger; // 暂停执行，让用户查看错误详情
            
            // 延迟3秒，让用户有时间查看控制台错误
            await new Promise(resolve => setTimeout(resolve, 3000))
            
            // 清理认证状态并重定向到登录页
            authStore.logout()
            router.push('/login')
          }
        }
        
        // 处理其他HTTP错误
        const errorMessage = this.getErrorMessage(error)
        console.error('🔴 [HTTP] 最终错误:', {
          errorMessage,
          status: error.response?.status,
          url: error.config?.url
        })
        
        return Promise.reject(error)
      }
    )
  }

  /**
   * 获取错误信息
   */
  private getErrorMessage(error: any): string {
    if (error.response) {
      // 服务器响应错误
      const { status, data } = error.response
      if (data?.message) {
        return data.message
      }
      return `HTTP ${status}: ${error.response.statusText}`
    } else if (error.request) {
      // 网络错误
      return '网络连接失败，请检查网络设置'
    } else {
      // 其他错误
      return error.message || '未知错误'
    }
  }

}

// 创建并导出HTTP客户端实例
export const http = new HttpClient()

// 导出类型
export type { AxiosRequestConfig, AxiosResponse }