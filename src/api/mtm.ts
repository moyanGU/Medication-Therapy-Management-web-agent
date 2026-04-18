import { api } from '@/utils/api'
import type {
  MtmAssessmentDraftPayload,
  MtmAssessmentSummary,
  MtmPlanSummary,
  MtmFollowUpSummary,
  MtmInterviewDraftPayload,
  MtmInterviewSummary,
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

  /**
   * 读取单条 MTM 服务单的问诊草稿
   */
  async getInterview(serviceCaseId: number | string): Promise<MtmInterviewSummary> {
    log('🔵 [mtmApi] getInterview id =', serviceCaseId)
    const response = await api.get<MtmInterviewSummary>(
      `/mtm/service-cases/${serviceCaseId}/interview/`
    )
    log('🟢 [mtmApi] getInterview response =', response.data)
    return response.data
  },

  /**
   * 手动保存单条 MTM 服务单的问诊草稿
   */
  async saveInterviewDraft(
    serviceCaseId: number | string,
    payload: MtmInterviewDraftPayload
  ): Promise<MtmInterviewSummary> {
    log('🔵 [mtmApi] saveInterviewDraft payload =', {
      serviceCaseId,
      ...payload,
    })
    const response = await api.put<MtmInterviewSummary>(
      `/mtm/service-cases/${serviceCaseId}/interview/`,
      payload
    )
    log('🟢 [mtmApi] saveInterviewDraft response =', response.data)
    return response.data
  },

  /**
   * 完成单条 MTM 服务单的问诊填写
   */
  async completeInterview(
    serviceCaseId: number | string,
    payload: MtmInterviewDraftPayload
  ): Promise<MtmInterviewSummary> {
    log('🔵 [mtmApi] completeInterview payload =', {
      serviceCaseId,
      ...payload,
    })
    const response = await api.post<MtmInterviewSummary>(
      `/mtm/service-cases/${serviceCaseId}/interview/complete/`,
      payload
    )
    log('🟢 [mtmApi] completeInterview response =', response.data)
    return response.data
  },

  /**
   * 读取单条 MTM 服务单的评估草稿
   */
  async getAssessment(serviceCaseId: number | string): Promise<MtmAssessmentSummary> {
    log('🔵 [mtmApi] getAssessment id =', serviceCaseId)
    const response = await api.get<MtmAssessmentSummary>(
      `/mtm/service-cases/${serviceCaseId}/assessment/`
    )
    log('🟢 [mtmApi] getAssessment response =', response.data)
    return response.data
  },

  /**
   * 手动保存单条 MTM 服务单的评估草稿
   */
  async saveAssessmentDraft(
    serviceCaseId: number | string,
    payload: MtmAssessmentDraftPayload
  ): Promise<MtmAssessmentSummary> {
    log('🔵 [mtmApi] saveAssessmentDraft payload =', {
      serviceCaseId,
      ...payload,
    })
    const response = await api.put<MtmAssessmentSummary>(
      `/mtm/service-cases/${serviceCaseId}/assessment/`,
      payload
    )
    log('🟢 [mtmApi] saveAssessmentDraft response =', response.data)
    return response.data
  },

  /**
   * 完成单条 MTM 服务单的评估填写
   */
  async completeAssessment(
    serviceCaseId: number | string,
    payload: MtmAssessmentDraftPayload
  ): Promise<MtmAssessmentSummary> {
    log('🔵 [mtmApi] completeAssessment payload =', {
      serviceCaseId,
      ...payload,
    })
    const response = await api.post<MtmAssessmentSummary>(
      `/mtm/service-cases/${serviceCaseId}/assessment/complete/`,
      payload
    )
    log('🟢 [mtmApi] completeAssessment response =', response.data)
    return response.data
  },


  // ============================
  // 干预计划 (Plan)
  // ============================

  async getPlan(serviceCaseId: number | string): Promise<MtmPlanSummary> {
    log('🔵 [mtmApi] getPlan called with id =', serviceCaseId)
    const response = await api.get<MtmPlanSummary>(`/mtm/service-cases/${serviceCaseId}/plan/`)
    log('🟢 [mtmApi] getPlan response =', response.data)
    return response.data
  },

  async savePlanDraft(
    serviceCaseId: number | string,
    payload: Partial<MtmPlanSummary>
  ): Promise<MtmPlanSummary> {
    log('🔵 [mtmApi] savePlanDraft payload =', { serviceCaseId, ...payload })
    const response = await api.put<MtmPlanSummary>(
      `/mtm/service-cases/${serviceCaseId}/plan/`,
      payload
    )
    log('🟢 [mtmApi] savePlanDraft response =', response.data)
    return response.data
  },

  async completePlan(
    serviceCaseId: number | string,
    payload: Partial<MtmPlanSummary>
  ): Promise<MtmPlanSummary> {
    log('🔵 [mtmApi] completePlan payload =', { serviceCaseId, ...payload })
    const response = await api.post<MtmPlanSummary>(
      `/mtm/service-cases/${serviceCaseId}/plan/complete/`,
      payload
    )
    log('🟢 [mtmApi] completePlan response =', response.data)
    return response.data
  },

  // ============================
  // 随访记录 (Follow-up)
  // ============================

  async getFollowUps(serviceCaseId: number | string): Promise<MtmFollowUpSummary[]> {
    log('🔵 [mtmApi] getFollowUps called with id =', serviceCaseId)
    const response = await api.get<MtmFollowUpSummary[]>(`/mtm/service-cases/${serviceCaseId}/follow-ups/`)
    log('🟢 [mtmApi] getFollowUps response =', response.data)
    return response.data
  },

  async addFollowUp(
    serviceCaseId: number | string,
    payload: Partial<MtmFollowUpSummary>
  ): Promise<MtmFollowUpSummary> {
    log('🔵 [mtmApi] addFollowUp payload =', { serviceCaseId, ...payload })
    const response = await api.post<MtmFollowUpSummary>(
      `/mtm/service-cases/${serviceCaseId}/follow-ups/`,
      payload
    )
    log('🟢 [mtmApi] addFollowUp response =', response.data)
    return response.data
  },


  // ============================
  // PMR / MAP 报告 (Report)
  // ============================

  async getReport(serviceCaseId: number | string): Promise<any> {
    log('🔵 [mtmApi] getReport called with id =', serviceCaseId)
    const response = await api.get<any>(`/mtm/service-cases/${serviceCaseId}/report/`)
    log('🟢 [mtmApi] getReport response =', response.data)
    return response.data
  },

  /**
   * 认领服务单 (仅药师)
   */
  async claimServiceCase(id: number | string): Promise<MtmServiceCase> {
    log('🔵 [mtmApi] claimServiceCase called with id =', id)
    const response = await api.post<MtmServiceCase>(`/mtm/service-cases/${id}/claim/`)
    log('🟢 [mtmApi] claimServiceCase response =', response.data)
    return response.data
  },
}
