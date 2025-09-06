/**
 * 用药记录相关类型定义
 */

// 服药方式枚举
export enum AdministrationMethod {
  ORAL = 'oral',
  INJECTION = 'injection',
  TOPICAL = 'topical',
  INHALATION = 'inhalation',
  SUBLINGUAL = 'sublingual',
  RECTAL = 'rectal',
  OTHER = 'other'
}

// 服药状态枚举
export enum MedicationStatus {
  TAKEN = 'taken',
  MISSED = 'missed',
  DELAYED = 'delayed',
  PARTIAL = 'partial'
}

// 记录来源枚举
export enum RecordSource {
  MANUAL = 'manual',
  REMINDER = 'reminder',
  IMPORT = 'import',
  AUTO = 'auto'
}

// 用药记录接口
export interface MedicationRecord {
  id: number
  user: number
  medicine: number
  taken_at: string
  quantity_taken: number
  administration_method: AdministrationMethod
  status: MedicationStatus
  notes?: string
  symptom_score?: number
  effectiveness_score?: number
  side_effects?: string
  is_on_time: boolean
  delay_minutes?: number
  source: RecordSource
  created_at: string
  updated_at: string
  medicine_name?: string
  medicine_specification?: string
  medicine_image?: string
  user_name?: string
  adherence_score?: number
}

// 用药记录创建/更新数据
export interface MedicationRecordForm {
  medicine: number | string
  taken_at: string
  quantity_taken: number
  administration_method: AdministrationMethod
  status: MedicationStatus
  notes?: string
  symptom_score?: number
  effectiveness_score?: number
  side_effects?: string
  delay_minutes?: number
  source?: RecordSource
}

// 用药记录统计数据
export interface MedicationRecordStats {
  total_records: number
  taken_count: number
  missed_count: number
  delayed_count: number
  adherence_rate: number
  avg_effectiveness: number
  most_used_medicine: string
  daily_average: number
  medicine_stats?: MedicineStats[]
}

// 药品统计数据
export interface MedicineStats {
  medicine: number
  medicine_name: string
  total_records: number
  taken_count: number
  missed_count: number
  delayed_count: number
  adherence_rate: number
  avg_effectiveness?: number
  side_effects_count?: number
}

// 用药趋势数据
export interface MedicationTrend {
  date: string
  total: number
  taken: number
  missed: number
  delayed: number
}

// 用药记录查询参数
export interface MedicationRecordQuery {
  page?: number
  page_size?: number
  start_date?: string
  end_date?: string
  medicine?: number
  medicine_name?: string
  status?: MedicationStatus
  administration_method?: AdministrationMethod
  is_on_time?: boolean
  source?: RecordSource
  effectiveness_min?: number
  effectiveness_max?: number
  symptom_min?: number
  symptom_max?: number
  quantity_min?: number
  quantity_max?: number
  delay_min?: number
  delay_max?: number
  has_side_effects?: boolean
  has_notes?: boolean
  search?: string
  ordering?: string
}

// 服药方式选项
export const ADMINISTRATION_METHOD_OPTIONS = [
  { value: AdministrationMethod.ORAL, label: '口服' },
  { value: AdministrationMethod.INJECTION, label: '注射' },
  { value: AdministrationMethod.TOPICAL, label: '外用' },
  { value: AdministrationMethod.INHALATION, label: '吸入' },
  { value: AdministrationMethod.SUBLINGUAL, label: '舌下含服' },
  { value: AdministrationMethod.RECTAL, label: '直肠给药' },
  { value: AdministrationMethod.OTHER, label: '其他' }
]

// 服药状态选项
export const MEDICATION_STATUS_OPTIONS = [
  { value: MedicationStatus.TAKEN, label: '已服用' },
  { value: MedicationStatus.MISSED, label: '漏服' },
  { value: MedicationStatus.DELAYED, label: '延迟服用' },
  { value: MedicationStatus.PARTIAL, label: '部分服用' }
]

// 记录来源选项
export const RECORD_SOURCE_OPTIONS = [
  { value: RecordSource.MANUAL, label: '手动记录' },
  { value: RecordSource.REMINDER, label: '提醒记录' },
  { value: RecordSource.IMPORT, label: '导入记录' },
  { value: RecordSource.AUTO, label: '自动记录' }
]