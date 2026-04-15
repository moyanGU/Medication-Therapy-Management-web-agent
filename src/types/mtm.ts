import type { PaginatedData } from '@/types/plan'
import type { RouteLocationRaw } from 'vue-router'

/**
 * MTM 服务状态
 */
export type MtmServiceStatus =
  | 'pending'
  | 'interviewing'
  | 'assessing'
  | 'intervening'
  | 'following_up'
  | 'completed'

/**
 * MTM 服务触发来源
 */
export type MtmTriggerSource =
  | 'manual'
  | 'self_requested'
  | 'adherence_alert'
  | 'followup_due'
  | 'polypharmacy'
  | 'referral'

/**
 * MTM 服务单排序字段
 */
export type MtmServiceCaseOrdering =
  | '-created_at'
  | 'created_at'
  | '-started_at'
  | 'started_at'
  | '-completed_at'
  | 'completed_at'

/**
 * MTM 参与者最小信息
 */
export interface MtmUserSummary {
  id: number
  username: string
  phone: string
}

/**
 * MTM 问诊摘要
 */
export interface MtmInterviewSummary {
  id: number
  basic_info_snapshot: Record<string, unknown>
  medication_history: Array<Record<string, unknown>>
  allergy_history: Array<Record<string, unknown>>
  lifestyle_info: Record<string, unknown>
  economic_context: string | null
  health_expectations: string | null
  notes: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

/**
 * MTM 评估摘要
 */
export interface MtmAssessmentSummary {
  id: number
  appropriateness_score: number | null
  effectiveness_score: number | null
  safety_score: number | null
  adherence_score: number | null
  economic_score: number | null
  problem_list: unknown[]
  summary: string | null
  risk_level: 'low' | 'medium' | 'high'
  completed_at: string | null
  created_at: string
  updated_at: string
}

/**
 * MTM 干预计划摘要
 */
export interface MtmPlanSummary {
  id: number
  interventions: unknown[]
  priority: 'low' | 'medium' | 'high' | 'urgent'
  patient_confirmation_status: 'pending' | 'confirmed' | 'declined'
  patient_confirmation_notes: string | null
  confirmed_at: string | null
  created_at: string
  updated_at: string
}

/**
 * MTM 随访摘要
 */
export interface MtmFollowUpSummary {
  id: number
  follow_up_time: string
  follow_up_method: string
  execution_status: string
  risk_change: string
  summary: string | null
  next_follow_up_time: string | null
  created_at: string
  updated_at: string
}

/**
 * MTM 服务单详情
 */
export interface MtmServiceCase {
  id: number
  case_number: string
  patient: MtmUserSummary
  assigned_pharmacist: MtmUserSummary | null
  status: MtmServiceStatus
  trigger_source: MtmTriggerSource
  service_goal: string | null
  started_at: string
  completed_at: string | null
  created_at: string
  notes?: string | null
  updated_at?: string
  interview?: MtmInterviewSummary | null
  assessment?: MtmAssessmentSummary | null
  plan?: MtmPlanSummary | null
  follow_ups?: MtmFollowUpSummary[]
}

/**
 * MTM 服务单创建参数
 */
export interface MtmServiceCaseCreatePayload {
  trigger_source: MtmTriggerSource
  service_goal?: string
  notes?: string
}

/**
 * MTM 服务单分页结果
 */
export type MtmServiceCasePaginatedData = PaginatedData<MtmServiceCase>

/**
 * MTM 服务单状态流转请求参数
 */
export interface MtmServiceCaseTransitionPayload {
  target_status: MtmServiceStatus
  notes?: string
}

/**
 * MTM 服务单可执行动作
 */
export interface MtmServiceCaseTransitionAction {
  targetStatus: MtmServiceStatus
  label: string
  description: string
  variant?: 'primary' | 'secondary'
}

/**
 * MTM 服务单列表查询参数
 */
export interface MtmServiceCaseListParams {
  [key: string]: string | number | boolean | null | undefined
  page?: number
  page_size?: number
  search?: string
  status?: MtmServiceStatus | ''
  ordering?: MtmServiceCaseOrdering | ''
  trigger_source?: MtmTriggerSource | ''
}

/**
 * MTM 列表预设入口
 */
export interface MtmListPresetEntry {
  key: 'all' | 'active_status' | 'suggested_trigger'
  title: string
  shortLabel: string
  description: string
  to: RouteLocationRaw
}

/**
 * MTM 列表预设来源标识
 */
export type MtmListPresetSource = MtmListPresetEntry['key']

/**
 * MTM 列表页快捷动作
 */
export interface MtmListQuickAction {
  key: 'refresh' | 'clear_filters' | 'view_all' | 'back_dashboard'
  label: string
  description: string
  to?: RouteLocationRaw
  action?: 'refresh' | 'clear_filters'
  variant?: 'primary' | 'secondary'
}
