import { api } from '@/utils/api'
import type {
  MtmServiceCase,
  MtmServiceCaseCreatePayload,
  MtmServiceCaseListParams,
  MtmServiceCasePaginatedData,
  MtmServiceCaseTransitionPayload,
} from '@/types/mtm'

const isDebug = import.meta.env.MODE !== 'production'
const log = (...args: unknown[]) => {
  if (isDebug) console.log(...args)
}

/**
 * MTM 服务接口
 */
export const mtmApi = {
  /**
   * 获取当前用户参与的 MTM 服务单列表
   */
  async getServiceCases(params?: MtmServiceCaseListParams): Promise<MtmServiceCasePaginatedData> {
    log('🔵 [mtmApi] getServiceCases params =', params)
    const response = await api.get<MtmServiceCasePaginatedData>('/mtm/service-cases/', params)
    const payload = response.data

    if (!payload) {
      return {
        results: [],
        pagination: {
          count: 0,
          next: null,
          previous: null,
          page_size: params?.page_size || 3,
          current_page: 1,
          total_pages: 0,
        },
      }
    }

    log('🟢 [mtmApi] getServiceCases payload =', payload)
    return payload
  },

  /**
   * 创建 MTM 服务单
   */
  async createServiceCase(payload: MtmServiceCaseCreatePayload): Promise<MtmServiceCase> {
    log('🔵 [mtmApi] createServiceCase payload =', payload)
    const response = await api.post<MtmServiceCase>('/mtm/service-cases/', payload)
    log('🟢 [mtmApi] createServiceCase response =', response.data)
    return response.data
  },

  /**
   * 获取单条 MTM 服务单详情
   */
  async getServiceCaseDetail(serviceCaseId: number | string): Promise<MtmServiceCase> {
    log('🔵 [mtmApi] getServiceCaseDetail id =', serviceCaseId)
    const response = await api.get<MtmServiceCase>(`/mtm/service-cases/${serviceCaseId}/`)
    log('🟢 [mtmApi] getServiceCaseDetail response =', response.data)
    return response.data
  },

  /**
   * 推进单条 MTM 服务单到下一个合法状态
   */
  async transitionServiceCase(
    serviceCaseId: number | string,
    payload: MtmServiceCaseTransitionPayload
  ): Promise<MtmServiceCase> {
    log('🔵 [mtmApi] transitionServiceCase payload =', {
      serviceCaseId,
      ...payload,
    })
    const response = await api.post<MtmServiceCase>(
      `/mtm/service-cases/${serviceCaseId}/transition/`,
      payload
    )
    log('🟢 [mtmApi] transitionServiceCase response =', response.data)
    return response.data
  },
}
