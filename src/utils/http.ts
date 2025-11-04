import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'

/**
 * 解析 VITE_API_BASE_URL，生产环境回退到 window.location.origin
 */
function resolveAxiosBaseURL(): string {
  const envVal = (typeof import.meta !== 'undefined' && (import.meta as any).env && (import.meta as any).env.VITE_API_BASE_URL) || ''
  const fromEnv = typeof envVal === 'string' ? envVal.trim() : ''
  if (fromEnv) return fromEnv
  if (typeof window !== 'undefined' && window.location) {
    return `${window.location.origin}`
  }
  // SSR/测试环境兜底：返回空串，使用相对路径同源访问
  return ''
}

export interface HttpResponse<T = any> {
  success: boolean
  data: T
  message?: string
  code?: number
}

/**
 * HTTP 客户端，封装 axios
 */
class HttpClient {
  private instance: AxiosInstance

  constructor(config?: AxiosRequestConfig) {
    this.instance = axios.create({
      baseURL: resolveAxiosBaseURL(), // 支持环境变量控制
      timeout: 10000,
      withCredentials: true,
      ...(config || {}),
    })

    console.log('[HttpClient] baseURL =', this.instance.defaults.baseURL)

    // 请求拦截器：在默认 headers 上设置 Authorization，避免直接赋值 cfg.headers 导致类型不匹配
    this.instance.interceptors.request.use(
      (cfg) => {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token')
        if (token) {
          // 使用默认头避免 TS2322 类型错误
          ;(this.instance.defaults.headers.common as any)['Authorization'] = `Bearer ${token}`
        }
        return cfg
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截器：不改变 AxiosResponse 类型，仅做 401 处理
    this.instance.interceptors.response.use(
      (response: AxiosResponse<any>) => {
        return response
      },
      (error) => {
        const status = error?.response?.status
        if (status === 401) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          localStorage.removeItem('user_info')

          const guestPaths = ['/login', '/register', '/welcome', '/forgot-password']
          const currentPath = typeof window !== 'undefined' ? window.location.pathname : ''
          if (!guestPaths.includes(currentPath)) {
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  /**
   * 统一解包响应，兼容后端 { success, data } 双层结构
   * @param response Axios 原始响应
   * @returns 标准 HttpResponse
   */
  private unwrapResponse<T = any>(response: AxiosResponse<any>): HttpResponse<T> {
    const { data } = response
    try {
      if (data && typeof data === 'object') {
        const hasSuccess = Object.prototype.hasOwnProperty.call(data, 'success')
        const hasData = Object.prototype.hasOwnProperty.call(data, 'data')
        if (hasSuccess && hasData) {
          console.debug('[HttpClient.unwrap] 已识别标准结构 {success, data}')
          return data as HttpResponse<T>
        }
        if (hasData) {
          console.warn('[HttpClient.unwrap] 发现非标准结构，已自动提取外层 data -> 内层 data')
          return { success: true, data: (data as any).data as T }
        }
      }
      console.warn('[HttpClient.unwrap] 响应非对象或缺少 data 字段，直接透传为 data')
      return { success: true, data: data as T }
    } catch (e) {
      console.error('[HttpClient.unwrap] 解析响应异常，透传原始数据', e)
      return { success: true, data: data as T }
    }
  }

  /**
   * GET 请求
   */
  get<T = any>(url: string, config?: AxiosRequestConfig) {
    return this.instance.get<T>(url, config).then((res) => this.unwrapResponse<T>(res))
  }

  /**
   * POST 请求
   */
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.instance.post<T>(url, data, config).then((res) => this.unwrapResponse<T>(res))
  }

  /**
   * PUT 请求
   */
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.instance.put<T>(url, data, config).then((res) => this.unwrapResponse<T>(res))
  }

  /**
   * PATCH 请求
   */
  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.instance.patch<T>(url, data, config).then((res) => this.unwrapResponse<T>(res))
  }

  /**
   * DELETE 请求
   */
  delete<T = any>(url: string, config?: AxiosRequestConfig) {
    return this.instance.delete<T>(url, config).then((res) => this.unwrapResponse<T>(res))
  }
}

const http = new HttpClient()
export default http
export { HttpClient }