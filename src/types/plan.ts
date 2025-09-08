/**
 * 用药计划相关类型定义
 */

// 计划类型枚举（与后端 models.MedicationPlan.PLAN_TYPE_CHOICES 对齐）
export type PlanType =
  | 'long_term'
  | 'short_term'
  | 'acute'
  | 'chronic'
  | 'preventive'
  | 'rehabilitation'

// 计划优先级（与后端 PRIORITY_CHOICES 对齐）
export type PlanPriority = 'low' | 'medium' | 'high' | 'urgent'

// 计划状态（与后端 STATUS_CHOICES 对齐）
export type PlanStatus = 'draft' | 'active' | 'paused' | 'completed' | 'cancelled'

// 分页信息（与后端 StandardResultsSetPagination.get_paginated_response 对齐）
export interface Pagination {
  count: number
  next: string | null
  previous: string | null
  page_size: number
  current_page: number
  total_pages: number
}

export interface PaginatedData<T> {
  results: T[]
  pagination: Pagination
}

// 计划中的药品（与 PlanMedicineSerializer 对齐）
export interface PlanMedicine {
  id: number
  medicine: number
  medicine_name?: string
  medicine_specification?: string
  daily_dosage?: string
  frequency?: string
  single_dose?: string
  instructions?: string
  // 后端序列化中为 administration_times，类型可能为字符串或数组，前端以 any 兼容
  administration_times?: any
  meal_timing?: string
  is_required?: boolean
  start_day?: number
  duration_days?: number
  special_requirements?: string
  dosage_adjustments?: string
  created_at?: string
  updated_at?: string
}

// 用药计划（列表+详情的并集，列表字段为主，详情可选）
export interface MedicationPlan {
  id: number
  name: string
  plan_type: PlanType
  start_date: string
  end_date?: string | null
  status: PlanStatus
  priority: PlanPriority
  is_active: boolean
  duration_days?: number
  is_expired?: boolean
  progress_percentage?: number
  medicines_count?: number
  created_at: string
  updated_at?: string
  // 详情字段（在详情接口中出现）
  description?: string | null
  treatment_goal?: string | null
  source?: 'doctor' | 'self' | 'pharmacist' | 'import' | 'template'
  doctor_name?: string | null
  hospital_name?: string | null
  department?: string | null
  diagnosis?: string | null
  precautions?: string | null
  side_effects_monitoring?: string | null
  review_date?: string | null
  medicines?: PlanMedicine[]
}

// 查询参数（与 ViewSet 的 filterset/search/order 对齐）
export interface PlanListParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
  plan_type?: PlanType
  status?: PlanStatus | PlanStatus[]
  is_active?: boolean
  priority?: PlanPriority | PlanPriority[]
  // DjangoFilterBackend lookup 格式
  start_date__gte?: string
  start_date__lte?: string
  end_date__gte?: string
  end_date__lte?: string
  end_date__isnull?: boolean
  created_at__gte?: string
  created_at__lte?: string
}

// 创建/更新DTO（后端 HiddenField 自动注入 user）
export interface PlanCreateData {
  name: string
  plan_type: PlanType
  start_date: string
  end_date?: string | null
  description?: string | null
  treatment_goal?: string | null
  is_active?: boolean
  priority?: PlanPriority
  source?: 'doctor' | 'self' | 'pharmacist' | 'import' | 'template'
  doctor_name?: string | null
  hospital_name?: string | null
  department?: string | null
  diagnosis?: string | null
  precautions?: string | null
  side_effects_monitoring?: string | null
  review_date?: string | null
  status?: PlanStatus
}

export type PlanUpdateData = Partial<PlanCreateData>