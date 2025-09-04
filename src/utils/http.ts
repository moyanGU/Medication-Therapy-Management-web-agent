import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

/**
 * HTTP请求工具类
 * 基于axios封装，提供统一的请求和响应处理
 */
class HttpClient {
  private instance: AxiosInstance

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

  /**
   * GET请求
   */
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.get(url, config)
  }

  /**
   * POST请求
   */
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.post(url, data, config)
  }

  /**
   * PUT请求
   */
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.put(url, data, config)
  }

  /**
   * PATCH请求
   */
  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.patch(url, data, config)
  }

  /**
   * DELETE请求
   */
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.instance.delete(url, config)
  }

  /**
   * 上传文件
   */
  upload<T = any>(url: string, file: File, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    const formData = new FormData()
    formData.append('file', file)
    
    return this.instance.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers
      }
    })
  }

  /**
   * 下载文件
   */
  download(url: string, filename?: string, config?: AxiosRequestConfig): Promise<void> {
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
}

// 创建并导出HTTP客户端实例
export const http = new HttpClient()

// 导出类型
export type { AxiosRequestConfig, AxiosResponse }