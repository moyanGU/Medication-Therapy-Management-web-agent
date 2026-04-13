import { api } from '@/utils/api'
import type {
  MedicationPlan,
  PlanListParams,
  PaginatedData,
  PlanCreateData,
  PlanUpdateData,
} from '@/types/plan'

const isDebug = import.meta.env.MODE !== 'production'
const log = (...args: any[]) => {
  if (isDebug) console.log(...args)
}
const warn = (message: string, error?: unknown) => {
  if (isDebug && error !== undefined) {
    console.warn(message, error)
    return
  }
  console.warn(message)
}

/**
 * 用药计划 API 模块
 * 注意：后端统一响应为 { success, data }，分页列表为 data: { results, pagination }
 * 前端必须按双层 data 结构解包
 */
export const plansApi = {
  /**
   * 获取计划列表（分页）
   */
  async getPlans(
    params: PlanListParams = {}
  ): Promise<PaginatedData<MedicationPlan>> {
    log('[plansApi.getPlans] params =', params)
    const res = await api.get<PaginatedData<MedicationPlan>>('/plans/', params)
    // 解包 ApiClient 返回的 ApiResponse<T>
    const payload = res.data
    if (!payload) {
      warn('[plansApi.getPlans] empty payload, raw =', res)
      return {
        results: [],
        pagination: {
          count: 0,
          next: null,
          previous: null,
          page_size: 0,
          current_page: 1,
          total_pages: 0,
        },
      }
    }
    log('[plansApi.getPlans] pagination =', payload.pagination)
    return payload
  },

  /** 获取计划详情 */
  async getPlan(id: number): Promise<MedicationPlan> {
    log('[plansApi.getPlan] id =', id)
    const res = await api.get<MedicationPlan>(`/plans/${id}/`)
    const data = res.data as MedicationPlan
    log('[plansApi.getPlan] plan =', data)
    return data
  },

  /** 创建计划 */
  async createPlan(payload: PlanCreateData): Promise<MedicationPlan> {
    log('[plansApi.createPlan] payload =', payload)
    const res = await api.post<MedicationPlan>('/plans/', payload)
    const data = res.data as MedicationPlan
    log('[plansApi.createPlan] created =', data)
    return data
  },

  /** 更新计划 */
  async updatePlan(
    id: number,
    payload: PlanUpdateData
  ): Promise<MedicationPlan> {
    log('[plansApi.updatePlan] id =', id, 'payload =', payload)
    const res = await api.put<MedicationPlan>(`/plans/${id}/`, payload)
    const data = res.data as MedicationPlan
    log('[plansApi.updatePlan] updated =', data)
    return data
  },

  /** 删除计划 */
  async deletePlan(id: number): Promise<void> {
    log('[plansApi.deletePlan] id =', id)
    await api.delete<null>(`/plans/${id}/`)
    log('[plansApi.deletePlan] deleted')
  },
}

export default plansApi
