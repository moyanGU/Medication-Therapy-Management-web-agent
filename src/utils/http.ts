import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/auth'

/**
 * HTTP请求工具类
 * 基于axios封装，提供统一的请求和响应处理
 */
class HttpClient {
  private instance: AxiosInstance

  constructor() {
    // 创建axios实例
    this.instance = axios.create({
      baseURL: 'http://localhost:8000', // 后端API基础URL
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
        // 添加认证token
        const authStore = useAuthStore()
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`
        }
        
        console.log('发送请求:', {
          method: config.method?.toUpperCase(),
          url: config.url,
          data: config.data,
          params: config.params
        })
        
        return config
      },
      (error) => {
        console.error('请求拦截器错误:', error)
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
        console.log('收到响应:', {
          status: response.status,
          url: response.config.url,
          data: response.data
        })
        
        return response
      },
      (error) => {
        console.error('响应拦截器错误:', error)
        
        // 处理认证错误
        if (error.response?.status === 401) {
          const authStore = useAuthStore()
          authStore.logout()
          // 重定向到登录页
          window.location.href = '/login'
        }
        
        // 处理其他HTTP错误
        const errorMessage = this.getErrorMessage(error)
        console.error('HTTP请求失败:', errorMessage)
        
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