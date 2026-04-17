import { api } from '@/utils/api'
import type {
  MtmAssessmentDraftPayload,
  MtmAssessmentSummary,
  MtmFollowUpPayload,
  MtmFollowUpSummary,
  MtmInterviewDraftPayload,
  MtmInterviewSummary,
  MtmPlanDraftPayload,
  MtmPlanSummary,
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
    log('🔵 [mtmApi] completeAssessment called with caseId =', serviceCaseId)
    const response = await api.post<MtmAssessmentSummary>(
      `/mtm/service-cases/${serviceCaseId}/assessment/complete/`,
      payload
    )
    log('🟢 [mtmApi] completeAssessment response =', response.data)
    return response.data
  },

  /**
   * 获取单条 MTM 服务单的干预计划草稿或初始化最小草稿
   */
  async getPlan(
    serviceCaseId: number | string
  ): Promise<MtmPlanSummary> {
    log('🔵 [mtmApi] getPlan called with caseId =', serviceCaseId)
    const response = await api.get<MtmPlanSummary>(
      `/mtm/service-cases/${serviceCaseId}/plan/`
    )
    log('🟢 [mtmApi] getPlan response =', response.data)
    return response.data
  },

  /**
   * 手动保存单条 MTM 服务单的干预计划草稿
   */
  async savePlanDraft(
    serviceCaseId: number | string,
    payload: MtmPlanDraftPayload
  ): Promise<MtmPlanSummary> {
    log('🔵 [mtmApi] savePlanDraft called with caseId =', serviceCaseId)
    const response = await api.put<MtmPlanSummary>(
      `/mtm/service-cases/${serviceCaseId}/plan/`,
      payload
    )
    log('🟢 [mtmApi] savePlanDraft response =', response.data)
    return response.data
  },

  /**
   * 完成单条 MTM 服务单的干预计划填写
   */
  async completePlan(
    serviceCaseId: number | string,
    payload: MtmPlanDraftPayload
  ): Promise<MtmPlanSummary> {
    log('🔵 [mtmApi] completePlan called with caseId =', serviceCaseId)
    const response = await api.post<MtmPlanSummary>(
      `/mtm/service-cases/${serviceCaseId}/plan/complete/`,
      payload
    )
    log('🟢 [mtmApi] completePlan response =', response.data)
    return response.data
  },

  /**
   * 创建单条随访记录
   */
  async createFollowUp(
    payload: MtmFollowUpPayload
  ): Promise<MtmFollowUpSummary> {
    log('🔵 [mtmApi] createFollowUp called')
    const response = await api.post<MtmFollowUpSummary>(
      '/mtm/follow-ups/',
      payload
    )
    log('🟢 [mtmApi] createFollowUp response =', response.data)
    return response.data
  },

  /**
   * 更新单条随访记录
   */
  async updateFollowUp(
    followUpId: number | string,
    payload: MtmFollowUpPayload
  ): Promise<MtmFollowUpSummary> {
    log('🔵 [mtmApi] updateFollowUp called with id =', followUpId)
    const response = await api.put<MtmFollowUpSummary>(
      `/mtm/follow-ups/${followUpId}/`,
      payload
    )
    log('🟢 [mtmApi] updateFollowUp response =', response.data)
    return response.data
  },

  /**
   * 获取单条随访记录详情
   */
  async getFollowUp(
    followUpId: number | string
  ): Promise<MtmFollowUpSummary> {
    log('🔵 [mtmApi] getFollowUp called with id =', followUpId)
    const response = await api.get<MtmFollowUpSummary>(
      `/mtm/follow-ups/${followUpId}/`
    )
    log('🟢 [mtmApi] getFollowUp response =', response.data)
    return response.data
  },
}
