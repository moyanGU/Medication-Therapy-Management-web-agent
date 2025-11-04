// 病历记录相关类型定义

// 就诊类型
export type VisitType = 
  | 'outpatient'     // 门诊
  | 'emergency'      // 急诊
  | 'inpatient'      // 住院
  | 'follow_up'      // 复诊
  | 'consultation'   // 会诊
  | 'physical_exam'  // 体检
  | 'vaccination'    // 疫苗接种

// 就医状态
export type MedicalStatus = 
  | 'scheduled'      // 已预约
  | 'completed'      // 已完成
  | 'cancelled'      // 已取消
  | 'no_show'        // 未到诊
  | 'rescheduled'    // 已改期

// 紧急程度
export type UrgencyLevel = 
  | 'routine'        // 常规
  | 'urgent'         // 紧急
  | 'emergency'      // 急诊
  | 'critical'       // 危重

// 附件信息
export interface MedicalAttachment {
  id: string
  filename: string
  file_path: string
  file_size: number
  file_type: string
  upload_time: string
  description?: string
  download_url?: string
  status?: 'file_missing'
}

// 处方药品
export interface PrescribedMedicine {
  name: string
  dosage?: string
  frequency?: string
  duration?: string
  instructions?: string
}

// 检查项目
export interface Examination {
  name: string
  type?: string
  result?: string
  normal_range?: string
  unit?: string
}

// 化验结果
export interface LabResult {
  [key: string]: {
    value: number | string
    unit?: string
    normal_range?: string
    status?: 'normal' | 'high' | 'low' | 'abnormal'
  }
}

// 病历记录基础接口
export interface MedicalRecordBase {
  visit_date: string
  visit_time?: string
  hospital: string
  hospital_address?: string
  department?: string
  doctor?: string
  doctor_title?: string
  visit_type: VisitType
  chief_complaint?: string
  present_illness?: string
  diagnosis?: string
  diagnosis_code?: string
  treatment?: string
  prescribed_medicines?: PrescribedMedicine[]
  examinations?: Examination[]
  examination_results?: string
  lab_results?: LabResult
  medical_orders?: string
  notes?: string
  total_cost?: number
  insurance_coverage?: number
  self_pay_amount?: number
  follow_up_date?: string
  follow_up_notes?: string
  symptom_score_before?: number
  symptom_score_after?: number
  satisfaction_score?: number
  status: MedicalStatus
  urgency: UrgencyLevel
  attachments?: MedicalAttachment[]
}

// 完整的病历记录（包含ID和时间戳）
export interface MedicalRecord extends MedicalRecordBase {
  id: number
  user: number
  created_at: string
  updated_at: string
  
  // 计算属性
  visit_datetime?: string
  days_since_visit?: number
  days_until_follow_up?: number
  symptom_improvement?: number
  prescribed_medicine_names?: string[]
  examination_names?: string[]
  out_of_pocket_cost?: number
  is_follow_up_due?: boolean
}

// 创建病历记录的数据
export interface MedicalRecordCreate extends MedicalRecordBase {}

// 更新病历记录的数据
export interface MedicalRecordUpdate extends Partial<MedicalRecordBase> {}

// 病历记录列表项（简化版）
export interface MedicalRecordListItem {
  id: number
  visit_date: string
  visit_time?: string
  hospital: string
  department?: string
  doctor?: string
  visit_type: VisitType
  diagnosis?: string
  status: MedicalStatus
  urgency: UrgencyLevel
  total_cost?: number
  follow_up_date?: string
  days_since_visit?: number
  days_until_follow_up?: number
  is_follow_up_due?: boolean
  created_at: string
}

// 搜索参数
export interface MedicalRecordSearchParams {
  keyword?: string
  date_from?: string
  date_to?: string
  hospital?: string
  department?: string
  doctor?: string
  diagnosis?: string
  visit_type?: VisitType
  status?: MedicalStatus
  urgency?: UrgencyLevel
  cost_min?: number
  cost_max?: number
  satisfaction_min?: number
  has_follow_up?: boolean
  ordering?: string
  page?: number
  page_size?: number
}

// 分类统计
export interface CategoryStats {
  [key: string]: number
}

export interface MedicalRecordCategories {
  departments: CategoryStats[]
  hospitals: CategoryStats[]
  doctors: CategoryStats[]
  diagnoses: CategoryStats[]
  visit_types: CategoryStats[]
  urgency_levels: CategoryStats[]
}

// 统计数据
export interface MedicalRecordStatistics {
  total_visits: number
  recent_visits: number
  total_cost: number
  average_cost: number
  follow_up_due: number
  monthly_visits: Array<{
    month: string
    count: number
  }>
  department_distribution: Array<{
    department: string
    count: number
  }>
  cost_trend: Array<{
    month: string
    total_cost: number
    average_cost: number
  }>
}

// 病历摘要
export interface MedicalRecordSummary {
  id: number
  visit_summary: {
    date: string
    hospital: string
    department?: string
    doctor?: string
    diagnosis?: string
    treatment?: string
    medicines: string[]
    examinations: string[]
    follow_up?: string
    cost?: number
  }
}

// API响应类型
export interface MedicalRecordResponse {
  success: boolean
  data: MedicalRecord
  message: string
}

export interface MedicalRecordListResponse {
  success: boolean
  data: {
    results: MedicalRecordListItem[]
    count: number
    next?: string
    previous?: string
  }
  message: string
}

export interface MedicalRecordCategoriesResponse {
  success: boolean
  data: MedicalRecordCategories
  message: string
}

export interface MedicalRecordStatisticsResponse {
  success: boolean
  data: MedicalRecordStatistics
  message: string
}

// 表单验证规则
export interface MedicalRecordFormRules {
  visit_date: Array<{
    required: boolean
    message: string
    trigger: string
  }>
  hospital: Array<{
    required: boolean
    message: string
    trigger: string
  }>
  visit_type: Array<{
    required: boolean
    message: string
    trigger: string
  }>
  status: Array<{
    required: boolean
    message: string
    trigger: string
  }>
  urgency: Array<{
    required: boolean
    message: string
    trigger: string
  }>
}

// 就诊类型选项
export const VISIT_TYPE_OPTIONS = [
  { value: 'outpatient', label: '门诊' },
  { value: 'emergency', label: '急诊' },
  { value: 'inpatient', label: '住院' },
  { value: 'follow_up', label: '复诊' },
  { value: 'consultation', label: '会诊' },
  { value: 'physical_exam', label: '体检' },
  { value: 'vaccination', label: '疫苗接种' }
]

// 就医状态选项
export const STATUS_OPTIONS = [
  { value: 'scheduled', label: '已预约' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' },
  { value: 'no_show', label: '未到诊' },
  { value: 'rescheduled', label: '已改期' }
]

// 紧急程度选项
export const URGENCY_OPTIONS = [
  { value: 'routine', label: '常规' },
  { value: 'urgent', label: '紧急' },
  { value: 'emergency', label: '急诊' },
  { value: 'critical', label: '危重' }
]

// 排序选项（与后端 ordering 字段对齐）
export const SORT_OPTIONS = [
  { value: '-visit_date', label: '就诊时间（新→旧）' },
  { value: 'visit_date', label: '就诊时间（旧→新）' },
  { value: '-total_cost', label: '总费用（高→低）' },
  { value: 'total_cost', label: '总费用（低→高）' },
  { value: '-satisfaction_score', label: '满意度（高→低）' },
  { value: 'satisfaction_score', label: '满意度（低→高）' }
]