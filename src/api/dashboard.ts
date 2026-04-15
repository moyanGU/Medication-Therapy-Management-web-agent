import { api } from '@/utils/api'
import type { DashboardSummaryData } from '@/types/dashboard'

const isDebug = import.meta.env.MODE !== 'production'
const log = (...args: unknown[]) => {
  if (isDebug) console.log(...args)
}

/**
 * 首页聚合 API
 */
export const dashboardApi = {
  /**
   * 获取首页聚合摘要
   */
  async getSummary() {
    log('🔵 [Dashboard API] getSummary 开始请求')
    const response = await api.get<DashboardSummaryData>('/dashboard/summary/')
    log('🟢 [Dashboard API] getSummary 响应:', response)
    return response
  },
}
