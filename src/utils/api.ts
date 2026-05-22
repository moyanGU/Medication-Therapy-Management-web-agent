/**
 * API客户端封装
 * 统一处理HTTP请求和响应，包括错误处理、认证、拦截器等
 */

// API响应接口
interface ApiResponse<T = unknown> {
  success: boolean
  data: T
  message?: string
  code?: number
}

type QueryValue =
  | string
  | number
  | boolean
  | null
  | undefined
  | string[]
  | number[]
  | boolean[]
type QueryParams = Record<string, QueryValue>
type ApiErrorKind =
  | 'validation'
  | 'auth'
  | 'cancelled'
  | 'timeout'
  | 'network'
  | 'server'
  | 'client'
  | 'unknown'
type TraceSeverity = 'info' | 'warn' | 'error'
type SubmissionTraceContext = {
  scope: string
  submitSessionId: string
  startedAt: number
  startedAtIso: string
}

// 请求配置接口
interface RequestOptions extends RequestInit {
  timeout?: number
  skipAuth?: boolean
  skipErrorHandler?: boolean
  isFormData?: boolean
  requestId?: string
  // 明确指定响应解析方式：不指定时按 Content-Type 自动解析
  responseType?: 'json' | 'text' | 'blob'
  _retry401?: boolean
}
type RequestConfig = RequestOptions & { params?: QueryParams }

// 错误类型
class ApiError extends Error {
  code: number
  response?: Response
  details?: any

  constructor(
    message: string,
    code: number,
    response?: Response,
    details?: any
  ) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.response = response
    this.details = details
  }
}

const isPlainObject = (value: unknown): value is Record<string, unknown> => {
  return Object.prototype.toString.call(value) === '[object Object]'
}

const collectValidationMessages = (value: unknown): string[] => {
  if (typeof value === 'string') {
    const normalized = value.trim()
    return normalized ? [normalized] : []
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return [String(value)]
  }

  if (Array.isArray(value)) {
    return value.flatMap(item => collectValidationMessages(item))
  }

  if (isPlainObject(value)) {
    return Object.values(value).flatMap(item => collectValidationMessages(item))
  }

  return []
}

const pickValidationSource = (value: unknown): Record<string, unknown> | null => {
  if (!isPlainObject(value)) {
    return null
  }

  const filteredEntries = Object.entries(value).filter(([key]) => {
    return !['success', 'message', 'error_code', 'status_code'].includes(key)
  })

  if (filteredEntries.length === 0) {
    return null
  }

  return Object.fromEntries(filteredEntries)
}

export const extractApiValidationErrors = (
  error: unknown
): Record<string, string> => {
  const details = (error as { details?: unknown } | undefined)?.details
  const candidates = [
    pickValidationSource((details as { data?: unknown } | undefined)?.data),
    pickValidationSource((details as { errors?: unknown } | undefined)?.errors),
    pickValidationSource(details),
  ].filter((candidate): candidate is Record<string, unknown> => candidate !== null)

  for (const candidate of candidates) {
    const entries = Object.entries(candidate)
      .map(([field, value]) => {
        const messages = collectValidationMessages(value)
        if (messages.length === 0) {
          return null
        }
        return [field, messages[0]] as const
      })
      .filter((entry): entry is readonly [string, string] => entry !== null)

    if (entries.length > 0) {
      return Object.fromEntries(entries)
    }
  }

  const message = typeof (error as { message?: unknown } | undefined)?.message === 'string'
    ? (error as { message: string }).message.trim()
    : ''
  const fieldMessageMatch = message.match(/^([A-Za-z0-9_]+):\s*(.+)$/)

  if (fieldMessageMatch) {
    return {
      [fieldMessageMatch[1]]: fieldMessageMatch[2].trim(),
    }
  }

  if (message) {
    return {
      non_field_errors: message,
    }
  }

  return {}
}

const getApiErrorStatus = (error: unknown) => {
  const responseStatus = (error as { response?: { status?: unknown } } | undefined)?.response
    ?.status
  if (typeof responseStatus === 'number') {
    return responseStatus
  }

  const code = (error as { code?: unknown } | undefined)?.code
  return typeof code === 'number' ? code : null
}

const getApiErrorName = (error: unknown) => {
  const name = (error as { name?: unknown } | undefined)?.name
  return typeof name === 'string' && name.trim() ? name : 'UnknownError'
}

const getApiErrorMessage = (error: unknown) => {
  const message = (error as { message?: unknown } | undefined)?.message
  return typeof message === 'string' && message.trim()
    ? message.trim()
    : '未知错误'
}

const getApiErrorCode = (error: unknown) => {
  const details = (error as {
    details?: {
      error_code?: unknown
      error?: { code?: unknown; type?: unknown }
    }
  } | undefined)?.details
  const detailCode = details?.error_code
  if (typeof detailCode === 'string' && detailCode.trim()) {
    return detailCode.trim()
  }

  const nestedCode = details?.error?.code
  if (typeof nestedCode === 'string' && nestedCode.trim()) {
    return nestedCode.trim()
  }

  const nestedType = details?.error?.type
  if (typeof nestedType === 'string' && nestedType.trim()) {
    return nestedType.trim().toUpperCase()
  }

  const code = (error as { code?: unknown } | undefined)?.code
  if (typeof code === 'string' && code.trim()) {
    return code.trim()
  }
  if (typeof code === 'number') {
    return String(code)
  }

  return null
}

const isAbortLikeError = (error: unknown) => {
  const errorName = getApiErrorName(error)
  const message = getApiErrorMessage(error).toLowerCase()

  if (errorName === 'AbortError') {
    return true
  }

  return (
    message.includes('err_aborted') ||
    message.includes('request aborted') ||
    message.includes('request was aborted') ||
    message.includes('signal is aborted') ||
    message.includes('user aborted') ||
    message.includes('aborted')
  )
}

const getApiErrorDetailsSnapshot = (error: unknown) => {
  const details = (error as { details?: unknown } | undefined)?.details
  if (!details) {
    return null
  }

  if (Array.isArray(details)) {
    return details.slice(0, 5)
  }

  if (isPlainObject(details)) {
    return details
  }

  return String(details)
}

const getValidationErrorFieldList = (validationErrors: Record<string, string>) => {
  return Object.keys(validationErrors).sort()
}

const classifyApiError = (error: unknown): ApiErrorKind => {
  const errorName = getApiErrorName(error)
  const status = getApiErrorStatus(error)
  const validationErrors = extractApiValidationErrors(error)

  if (Object.keys(validationErrors).length > 0) {
    return 'validation'
  }

  if (status === 499 || isAbortLikeError(error)) {
    return 'cancelled'
  }

  if (status === 401 || status === 403) {
    return 'auth'
  }

  if (errorName === 'AbortError') {
    return 'timeout'
  }

  if (errorName === 'TypeError' && getApiErrorMessage(error).includes('fetch')) {
    return 'network'
  }

  if (typeof status === 'number' && status >= 500) {
    return 'server'
  }

  if (typeof status === 'number' && status >= 400) {
    return 'client'
  }

  return 'unknown'
}

const buildApiErrorFingerprint = (error: unknown) => {
  const validationErrors = extractApiValidationErrors(error)
  const fieldSignature = getValidationErrorFieldList(validationErrors).join('|') || 'none'
  return [
    classifyApiError(error),
    getApiErrorStatus(error) ?? 'no-status',
    getApiErrorCode(error) ?? 'no-code',
    getApiErrorMessage(error),
    fieldSignature,
  ].join('::')
}

const RECENT_API_ERROR_LIMIT = 100
const REQUEST_ID_HEADER = 'X-Request-ID'
const recentApiErrorTimeline = new Map<
  string,
  { count: number; firstSeenAt: string; lastSeenAt: string }
>()

export const createTraceId = (prefix = 'trace') => {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return `${prefix}-${crypto.randomUUID()}`
  }

  return `${prefix}-${Date.now().toString(36)}-${Math.random()
    .toString(36)
    .slice(2, 10)}`
}

export const createSubmissionTraceContext = (
  scope: string
): SubmissionTraceContext => {
  const startedAt = Date.now()
  return {
    scope,
    submitSessionId: createTraceId('submit'),
    startedAt,
    startedAtIso: new Date(startedAt).toISOString(),
  }
}

export const logClientTraceEvent = (
  scope: string,
  event: string,
  context: Record<string, unknown> = {},
  options: {
    traceContext?: SubmissionTraceContext
    severity?: TraceSeverity
  } = {}
) => {
  const timestamp = new Date().toISOString()
  const { traceContext, severity = 'info' } = options
  const logger =
    severity === 'error'
      ? console.error
      : severity === 'warn'
        ? console.warn
        : console.log

  logger(`🔵 [${scope}] ${event}`, {
    timestamp,
    event,
    severity,
    submitSessionId: traceContext?.submitSessionId ?? null,
    submitStartedAt: traceContext?.startedAtIso ?? null,
    elapsedMs: traceContext ? Date.now() - traceContext.startedAt : null,
    context,
  })
}

const readRequestIdHeader = (
  headers?: Headers | { get?: (name: string) => string | null } | null
) => {
  if (!headers || typeof headers.get !== 'function') {
    return null
  }

  const requestId =
    headers.get(REQUEST_ID_HEADER) ?? headers.get(REQUEST_ID_HEADER.toLowerCase())
  return typeof requestId === 'string' && requestId.trim() ? requestId.trim() : null
}

const getApiBackendRequestId = (error: unknown) => {
  const detailsRequestId = (
    error as { details?: { request_id?: unknown } } | undefined
  )?.details?.request_id
  if (typeof detailsRequestId === 'string' && detailsRequestId.trim()) {
    return detailsRequestId.trim()
  }

  const responseHeaders = (
    error as { response?: { headers?: Headers | { get?: (name: string) => string | null } } } | undefined
  )?.response?.headers
  return readRequestIdHeader(responseHeaders)
}

const trackApiErrorOccurrence = (error: unknown) => {
  const fingerprint = buildApiErrorFingerprint(error)
  const now = new Date().toISOString()
  const existing = recentApiErrorTimeline.get(fingerprint)

  if (existing) {
    const updated = {
      count: existing.count + 1,
      firstSeenAt: existing.firstSeenAt,
      lastSeenAt: now,
    }
    recentApiErrorTimeline.set(fingerprint, updated)
    return { fingerprint, ...updated }
  }

  if (recentApiErrorTimeline.size >= RECENT_API_ERROR_LIMIT) {
    const oldestKey = recentApiErrorTimeline.keys().next().value
    if (oldestKey) {
      recentApiErrorTimeline.delete(oldestKey)
    }
  }

  const created = {
    count: 1,
    firstSeenAt: now,
    lastSeenAt: now,
  }
  recentApiErrorTimeline.set(fingerprint, created)
  return { fingerprint, ...created }
}

export const buildApiErrorDebugPayload = (
  error: unknown,
  context: Record<string, unknown> = {}
) => {
  const validationErrors = extractApiValidationErrors(error)
  const occurrence = trackApiErrorOccurrence(error)
  const backendRequestId = getApiBackendRequestId(error)
  return {
    timestamp: new Date().toISOString(),
    kind: classifyApiError(error),
    errorName: getApiErrorName(error),
    message: getApiErrorMessage(error),
    status: getApiErrorStatus(error),
    errorCode: getApiErrorCode(error),
    validationErrors,
    validationFields: getValidationErrorFieldList(validationErrors),
    details: getApiErrorDetailsSnapshot(error),
    fingerprint: occurrence.fingerprint,
    occurrenceCount: occurrence.count,
    firstSeenAt: occurrence.firstSeenAt,
    lastSeenAt: occurrence.lastSeenAt,
    frontendRequestId:
      typeof context.requestId === 'string' && context.requestId.trim()
        ? context.requestId.trim()
        : null,
    backendRequestId,
    context,
  }
}

export const isRequestCancelledError = (error: unknown) => {
  return getApiErrorStatus(error) === 499 || classifyApiError(error) === 'cancelled'
}

export const logApiErrorEvent = (
  scope: string,
  error: unknown,
  context: Record<string, unknown> = {}
) => {
  const payload = buildApiErrorDebugPayload(error, context)
  const logger =
    payload.kind === 'cancelled'
      ? console.info
      : payload.kind === 'validation' || payload.kind === 'client'
        ? console.warn
        : console.error
  logger(`🔴 [${scope}] API错误`, payload)
}

/**
 * 安全解析 VITE_API_BASE_URL，回退到同域 /api
 */
function isPrivateIpv4Host(host: string): boolean {
  return (
    /^10\./.test(host) ||
    /^192\.168\./.test(host) ||
    /^172\.(1[6-9]|2\d|3[0-1])\./.test(host)
  )
}

function isLoopbackHost(host: string): boolean {
  return host === 'localhost' || host === '127.0.0.1' || host === '::1'
}

function shouldUseExplicitBackendOrigin(host: string, port: string): boolean {
  if (!port || port === '8000') {
    return false
  }

  return (
    ['5173', '4173', '3000', '8080'].includes(port) ||
    isLoopbackHost(host) ||
    isPrivateIpv4Host(host)
  )
}

function buildOriginWithPort(locationLike: Location, port: string): string {
  const protocol = locationLike.protocol || 'http:'
  const host = locationLike.hostname
  const formattedHost = host.includes(':') && !host.startsWith('[') ? `[${host}]` : host
  return `${protocol}//${formattedHost}:${port}`
}

export function resolveApiBaseURL(): string {
  const envVal =
    (typeof import.meta !== 'undefined' &&
      (import.meta as any).env &&
      (import.meta as any).env.VITE_API_BASE_URL) ||
    ''
  const fromEnv = typeof envVal === 'string' ? envVal.trim() : ''
  if (fromEnv) return fromEnv
  const backendOriginFromEnv =
    (typeof import.meta !== 'undefined' &&
      (import.meta as any).env &&
      ((import.meta as any).env.VITE_BACKEND_ORIGIN ||
        (import.meta as any).env.VITE_BACKEND_URL)) ||
    ''
  const normalizedBackendOrigin =
    typeof backendOriginFromEnv === 'string' ? backendOriginFromEnv.trim() : ''
  if (normalizedBackendOrigin) {
    return `${normalizedBackendOrigin.replace(/\/+$/, '')}/api`
  }
  if (typeof window !== 'undefined' && window.location) {
    const host = window.location.hostname
    const port = window.location.port
    if (shouldUseExplicitBackendOrigin(host, port)) {
      return `${buildOriginWithPort(window.location, '8000')}/api`
    }
    return `${window.location.origin}/api`
  }
  // SSR/测试环境兜底：使用相对路径，避免硬编码主机
  return '/api'
}

/**
 * 返回后端 Origin（不带 /api），用于拼接 /media 等静态/媒体资源
 */
export function getBackendOrigin(): string {
  const base = resolveApiBaseURL()
  try {
    if (base.startsWith('http')) {
      const u = new URL(base)
      // 去掉末尾的 /api 片段
      const path = u.pathname.replace(/\/?api\/?$/, '')
      return `${u.origin}${path}` || u.origin
    }
  } catch (_) {
    // ignore
  }
  // 若为相对路径（如 /api），在浏览器环境下退回到当前 origin
  if (typeof window !== 'undefined' && window.location)
    return window.location.origin
  // SSR/测试环境兜底：返回空串，调用处以相对路径访问同源
  return ''
}

export function resolveMediaUrl(imagePath?: string | null): string {
  if (!imagePath) {
    return ''
  }
  const rawPath = imagePath.trim()
  if (!rawPath) {
    return ''
  }
  if (rawPath.startsWith('http://') || rawPath.startsWith('https://')) {
    return rawPath
  }
  const normalizedPath = rawPath.startsWith('/') ? rawPath : `/${rawPath}`
  if (normalizedPath.startsWith('/media/')) {
    return `${getBackendOrigin()}${normalizedPath}`
  }
  return `${getBackendOrigin()}/media${normalizedPath}`
}

/**
 * API客户端类
 */
class ApiClient {
  private baseURL: string
  private defaultTimeout: number
  private isDebug: boolean
  private refreshTokenPromise: Promise<boolean> | null

  constructor(baseURL: string = resolveApiBaseURL(), timeout: number = 10000) {
    this.baseURL = baseURL
    this.defaultTimeout = timeout
    this.refreshTokenPromise = null
    const envMode =
      typeof import.meta !== 'undefined' &&
      (import.meta as any).env &&
      (import.meta as any).env.MODE
    this.isDebug =
      typeof envMode === 'string'
        ? envMode.toLowerCase() !== 'production'
        : true
    if (this.isDebug) {
      console.log('[ApiClient] baseURL =', this.baseURL)
    }
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
  private buildURL(endpoint: string, params?: QueryParams): string {
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

  private isAuthRefreshEndpoint(endpoint: string): boolean {
    return /\/auth\/refresh\/?$/.test(endpoint)
  }

  private isAuthLoginEndpoint(endpoint: string): boolean {
    return /\/auth\/login\/?$/.test(endpoint)
  }

  private isAuthLogoutEndpoint(endpoint: string): boolean {
    return /\/auth\/logout\/?$/.test(endpoint)
  }

  private isTokenRefreshEligible(endpoint: string, config: RequestOptions): boolean {
    if (config.skipAuth) {
      return false
    }
    if (config._retry401) {
      return false
    }
    if (this.isAuthRefreshEndpoint(endpoint)) {
      return false
    }
    if (this.isAuthLoginEndpoint(endpoint)) {
      return false
    }
    if (this.isAuthLogoutEndpoint(endpoint)) {
      return false
    }
    return true
  }

  private async tryRefreshAccessToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      return false
    }

    if (this.refreshTokenPromise) {
      return this.refreshTokenPromise
    }

    const refreshUrl = this.buildURL('/auth/refresh/')
    this.refreshTokenPromise = (async () => {
      try {
        const response = await fetch(refreshUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        })

        const raw = await response.json().catch(() => null)
        if (!response.ok || !raw || raw.success !== true) {
          return false
        }

        const payload = raw.data && typeof raw.data === 'object' ? raw.data : {}
        const access =
          payload.access_token || payload.access || payload?.tokens?.access || ''
        const nextRefresh =
          payload.refresh_token || payload.refresh || payload?.tokens?.refresh || ''

        if (typeof access !== 'string' || !access.trim()) {
          return false
        }

        localStorage.setItem('access_token', access)
        if (typeof nextRefresh === 'string' && nextRefresh.trim()) {
          localStorage.setItem('refresh_token', nextRefresh)
        }

        return true
      } catch (_) {
        return false
      } finally {
        this.refreshTokenPromise = null
      }
    })()

    return this.refreshTokenPromise
  }

  private getRequestBodySummary(body: RequestInit['body']) {
    if (!body) {
      return { hasBody: false }
    }
    if (typeof FormData !== 'undefined' && body instanceof FormData) {
      const keys = Array.from(body.keys())
      return { hasBody: true, bodyType: 'form-data', fieldCount: keys.length }
    }
    if (typeof body === 'string') {
      return { hasBody: true, bodyType: 'string', size: body.length }
    }
    return { hasBody: true, bodyType: typeof body }
  }

  private getResponseSummary(response: Response, result: ApiResponse<any>) {
    return {
      status: response.status,
      ok: response.ok,
      success: result?.success,
      code: result?.code,
      message: result?.message,
    }
  }

  /**
   * 构建请求头
   */
  private shouldAttachRequestId(url: string): boolean {
    if (typeof window === 'undefined' || !window.location) {
      return true
    }

    try {
      const target = new URL(url, window.location.origin)
      return target.origin === window.location.origin
    } catch (_) {
      return true
    }
  }

  private buildHeaders(config: RequestConfig = {}, requestUrl = ''): HeadersInit {
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

    if (
      typeof config.requestId === 'string' &&
      config.requestId.trim() &&
      this.shouldAttachRequestId(requestUrl)
    ) {
      headers[REQUEST_ID_HEADER] = config.requestId.trim()
    }

    // 合并自定义头
    if (config.headers) {
      Object.assign(headers, config.headers)
    }

    return headers
  }

  /**
   * 处理响应
   * - 当显式指定 responseType 时，按指定类型解析
   * - 否则按 Content-Type 自动解析
   */
  private async handleResponse<T>(
    response: Response,
    responseType?: RequestOptions['responseType']
  ): Promise<ApiResponse<T>> {
    // 处理204 No Content响应
    if (response.status === 204) {
      return {
        success: true,
        data: null as T,
      }
    }

    let data: any

    try {
      if (responseType === 'blob') {
        data = await response.blob()
      } else if (responseType === 'text') {
        data = await response.text()
      } else if (responseType === 'json') {
        data = await response.json()
      } else {
        // 未指定时根据 Content-Type 自动判断
        const contentType = response.headers.get('content-type')
        if (contentType && contentType.includes('application/json')) {
          data = await response.json()
        } else if (
          contentType &&
          (contentType.includes('application/') ||
            contentType.includes('image/') ||
            contentType.includes('video/') ||
            contentType.includes('audio/'))
        ) {
          // 其它二进制类型按 blob 处理
          data = await response.blob()
        } else {
          data = await response.text()
        }
      }
    } catch (error) {
      throw new ApiError('响应解析失败', response.status, response)
    }

    if (!response.ok) {
      const rawMessage =
        (data as any)?.message ||
        `HTTP ${response.status}: ${response.statusText}`
      const message = this.isDebug
        ? rawMessage
        : response.status >= 500
          ? "服务暂时不可用，请稍后重试"
          : "请求失败，请稍后重试"
      throw new ApiError(message, response.status, response, data)
    }

    if (typeof data === 'object' && data !== null && 'success' in data) {
      const payload: any = (data as any).data
      if (
        payload &&
        typeof payload === 'object' &&
        'data' in payload &&
        Object.keys(payload).length === 1
      ) {
        return { ...(data as any), data: payload.data as T }
      }
      return data as ApiResponse<T>
    }

    if (typeof data === 'object' && data !== null && 'data' in data) {
      const payload: any = (data as any).data
      if (
        payload &&
        typeof payload === 'object' &&
        'data' in payload &&
        Object.keys(payload).length === 1
      ) {
        return {
          success: true,
          data: payload.data as T,
        }
      }
      return {
        success: true,
        data: payload as T,
      }
    }

    return {
      success: true,
      data: data as T,
    }
  }

  /**
   * 处理错误：支持 401 清理并跳转
   */
  private handleError(
    error: any,
    config: RequestConfig,
    requestMeta: Record<string, unknown> = {}
  ): never {
    if (this.isDebug) {
      logApiErrorEvent('ApiClient', error, {
        ...requestMeta,
        requestId: config.requestId ?? null,
        skipAuth: Boolean(config.skipAuth),
        skipErrorHandler: Boolean(config.skipErrorHandler),
        responseType: config.responseType || 'auto',
      })
    } else {
      console.error('API请求错误')
    }

    // 如果跳过错误处理，直接抛出
    if (config.skipErrorHandler) {
      throw error
    }

    // 处理不同类型的错误
    if (error instanceof ApiError) {
      // 401 未授权 - 清除token并在必要时跳转登录
      if (error.code === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        localStorage.removeItem('user_info')

        // 在访客页（登录/注册/欢迎/忘记密码）不触发跳转，避免打断当前流程
        const guestPaths = [
          '/login',
          '/register',
          '/welcome',
          '/forgot-password',
        ]
        const currentPath =
          typeof window !== 'undefined' ? window.location.pathname : ''
        const shouldRedirect = currentPath
          ? !guestPaths.includes(currentPath)
          : true

        if (shouldRedirect) {
          window.location.href = '/login'
        }
      }
      throw error
    }

    // 网络错误
    if (isAbortLikeError(error)) {
      throw new ApiError('请求已取消', 499)
    }

    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new ApiError('网络连接失败，请检查网络设置', 0)
    }

    // 超时错误
    if (error.name === 'AbortError') {
      throw new ApiError('请求超时，请稍后重试', 0)
    }

    // 其他错误
    throw new ApiError('请求失败，请稍后重试', 0)
  }

  /**
   * 发送请求
   * @param endpoint 接口路径
   * @param config 请求配置，支持 responseType 指定响应解析方式
   */
  private normalizeRequestConfig(
    paramsOrConfig?: QueryParams | RequestConfig,
    config?: RequestOptions
  ): { params?: QueryParams; config: RequestOptions } {
    if (paramsOrConfig && typeof paramsOrConfig === 'object') {
      const hasConfigKeys =
        'timeout' in paramsOrConfig ||
        'skipAuth' in paramsOrConfig ||
        'skipErrorHandler' in paramsOrConfig ||
        'isFormData' in paramsOrConfig ||
        'requestId' in paramsOrConfig ||
        'responseType' in paramsOrConfig ||
        'headers' in paramsOrConfig ||
        'method' in paramsOrConfig ||
        'params' in paramsOrConfig
      if (hasConfigKeys) {
        const { params, ...rest } = paramsOrConfig as RequestConfig
        return { params, config: rest }
      }
      return { params: paramsOrConfig as QueryParams, config: config || {} }
    }
    return { params: undefined, config: config || {} }
  }

  private async request<T>(
    endpoint: string,
    config: RequestOptions = {},
    params?: QueryParams
  ): Promise<ApiResponse<T>> {
    const url = this.buildURL(endpoint, params)
    const timeout = config.timeout || this.defaultTimeout

    // 创建AbortController用于超时控制
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      const finalRequestConfig: RequestInit = {
        ...config,
        headers: this.buildHeaders(config, url),
        signal: controller.signal,
      }

      const method = config.method || 'GET'
      const bodySummary = this.getRequestBodySummary(
        (config as any).body as RequestInit['body']
      )
      if (this.isDebug) {
        console.log(`API请求: ${method} ${url}`, {
          ...bodySummary,
          requestId: config.requestId ?? null,
        })
      }

      const response = await fetch(url, finalRequestConfig)
      const result = await this.handleResponse<T>(response, config.responseType)

      const responseSummary = this.getResponseSummary(response, result)
      const responseRequestId = readRequestIdHeader(response.headers)
      if (this.isDebug) {
        console.log(`API响应: ${method} ${url}`, {
          ...responseSummary,
          requestId: config.requestId ?? null,
          responseRequestId,
        })
      }

      return result
    } catch (error) {
      if (
        error instanceof ApiError &&
        error.code === 401 &&
        this.isTokenRefreshEligible(endpoint, config)
      ) {
        const refreshed = await this.tryRefreshAccessToken()
        if (refreshed) {
          return this.request<T>(
            endpoint,
            {
              ...config,
              _retry401: true,
            },
            params
          )
        }
      }
      this.handleError(error, config as RequestConfig, {
        url,
        method: config.method || 'GET',
        requestId: config.requestId ?? null,
      })
    } finally {
      clearTimeout(timeoutId)
    }
  }

  /** GET请求 */
  async get<T = any>(
    endpoint: string,
    paramsOrConfig?: QueryParams | RequestConfig,
    config?: RequestOptions
  ): Promise<ApiResponse<T>> {
    const normalized = this.normalizeRequestConfig(paramsOrConfig, config)
    return this.request<T>(
      endpoint,
      {
        ...normalized.config,
        method: 'GET',
      },
      normalized.params
    )
  }

  /** POST请求 */
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
      body: isForm ? data : data ? JSON.stringify(data) : undefined,
    })
  }

  /** PUT请求 */
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
      body: isForm ? data : data ? JSON.stringify(data) : undefined,
    })
  }

  /** PATCH请求 */
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
      body: isForm ? data : data ? JSON.stringify(data) : undefined,
    })
  }

  /** DELETE请求（支持可选 body） */
  async delete<T = any>(
    endpoint: string,
    data?: any,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const isForm = typeof FormData !== 'undefined' && data instanceof FormData
    return this.request<T>(endpoint, {
      ...config,
      method: 'DELETE',
      isFormData: isForm || config.isFormData,
      body: isForm ? data : data ? JSON.stringify(data) : undefined,
    })
  }

  /** 文件上传 */
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

  /** 文件下载 */
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
      if (this.isDebug) {
        console.log('🔵 [ApiClient.download] 开始下载', { url, filename })
      }
      const response = await fetch(url, {
        ...config,
        headers,
      })

      if (!response.ok) {
        throw new ApiError(
          `下载失败: ${response.status} ${response.statusText}`,
          response.status,
          response
        )
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
      if (this.isDebug) {
        console.log('🟢 [ApiClient.download] 下载完成')
      }
    } catch (error) {
      if (this.isDebug) {
        console.error('🔴 [ApiClient.download] 下载异常', error)
      } else {
        console.error('🔴 [ApiClient.download] 下载异常')
      }
      this.handleError(error, config)
    }
  }

  /**
   * 流式请求处理 (SSE / NDJSON)
   */
  async stream(
    endpoint: string,
    data: any,
    onChunk: (chunkText: string, isJson: boolean, rawData: any) => void,
    config: RequestConfig = {}
  ): Promise<void> {
    const url = this.buildURL(endpoint)
    const timeout = config.timeout || 70000

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    const isForm = typeof FormData !== 'undefined' && data instanceof FormData
    const headers = this.buildHeaders({ ...config, isFormData: isForm }, url)

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: isForm ? data : data ? JSON.stringify(data) : undefined,
        signal: controller.signal,
      })

      if (!response.ok) {
        throw new ApiError(`流请求失败: ${response.status}`, response.status, response)
      }

      if (!response.body) {
        throw new ApiError('响应体为空', 0)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      let reading = true
      while (reading) {
        const { done, value } = await reader.read()
        if (done) {
          reading = false
          continue
        }

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 留着最后一段不完整的

        for (const line of lines) {
          const trimmed = line.trim()
          if (!trimmed) continue
          
          try {
            const parsed = JSON.parse(trimmed)
            onChunk(trimmed, true, parsed)
          } catch (e) {
            onChunk(trimmed, false, null)
          }
        }
      }
      
      if (buffer.trim()) {
        try {
          const parsed = JSON.parse(buffer.trim())
          onChunk(buffer.trim(), true, parsed)
        } catch (e) {
          onChunk(buffer.trim(), false, null)
        }
      }

    } catch (error) {
      if (
        error instanceof ApiError &&
        error.code === 401 &&
        this.isTokenRefreshEligible(endpoint, config)
      ) {
        const refreshed = await this.tryRefreshAccessToken()
        if (refreshed) {
          return this.stream(endpoint, data, onChunk, { ...config, _retry401: true })
        }
      }
      this.handleError(error, config as RequestConfig, { url, method: 'POST' })
    } finally {
      clearTimeout(timeoutId)
    }
  }
}

// 创建默认API客户端实例
export const api = new ApiClient()

// 导出类型和错误类
export { ApiClient, ApiError }
export { getApiErrorCode }
export type {
  ApiErrorKind,
  ApiResponse,
  RequestConfig,
  SubmissionTraceContext,
  TraceSeverity,
}

// 便捷方法
export const { get, post, put, patch, delete: del, upload, download } = api
