/**
 * 首页聚合数据类型定义
 */

export type DashboardTaskStatus = 'taken' | 'missed' | 'delayed' | 'partial' | null
export type DashboardRiskLevel = 'low' | 'medium' | 'high'
export type DashboardRiskType =
  | 'low_stock'
  | 'expiring_soon'
  | 'adherence_risk'
  | 'followup_due'

export interface DashboardTaskItem {
  reminder_id: number
  medicine_id: number
  medicine_name: string
  title: string
  reminder_time: string
  dosage: number
  dosage_unit: string
  meal_timing: string
  is_completed: boolean
  record_status: DashboardTaskStatus
  scheduled_date: string
}

export interface DashboardTodayTasks {
  date: string
  total: number
  completed: number
  pending: number
  items: DashboardTaskItem[]
}

export interface DashboardRiskAlert {
  type: DashboardRiskType
  level: DashboardRiskLevel
  title: string
  count: number
  message: string
}

export interface DashboardMedicineItem {
  id: number
  name: string
  quantity: number
  expiry_date: string | null
  days_until_expiry: number | null
  is_low_stock: boolean
}

export interface DashboardMedicationSummary {
  total_medicines: number
  active_reminders: number
  low_stock_count: number
  expiring_soon_count: number
  low_stock_items: DashboardMedicineItem[]
  expiring_soon_items: DashboardMedicineItem[]
}

export interface DashboardFollowupItem {
  id: number
  hospital: string
  department: string
  doctor: string
  visit_date: string
  follow_up_date: string | null
  days_until_follow_up: number | null
  is_follow_up_due: boolean
}

export interface DashboardFollowupSummary {
  due_count: number
  upcoming_count: number
  next_followup: DashboardFollowupItem | null
  due_items: DashboardFollowupItem[]
  upcoming_items: DashboardFollowupItem[]
}

export interface DashboardResponseSummary {
  scheduled_count: number
  responded_count: number
  unresponded_count: number
  response_rate: number
}

export interface DashboardAdherencePeriodSummary {
  total_records: number
  taken_count: number
  missed_count: number
  delayed_count: number
  partial_count: number
  completed_count: number
  adherence_rate: number
  on_time_rate: number
  avg_delay_minutes: number
  risk_level: DashboardRiskLevel
  risk_flags: string[]
  response_summary: DashboardResponseSummary
}

export interface DashboardAdherenceSummary {
  summary_7d: DashboardAdherencePeriodSummary
  summary_30d: DashboardAdherencePeriodSummary
  current_period: DashboardAdherencePeriodSummary
}

export interface DashboardMtmEntryHint {
  recommended: boolean
  reason_count: number
  reasons: string[]
  message: string
}

export interface DashboardSummaryData {
  today_tasks: DashboardTodayTasks
  risk_alerts: DashboardRiskAlert[]
  medication_summary: DashboardMedicationSummary
  followup_summary: DashboardFollowupSummary
  adherence_summary: DashboardAdherenceSummary
  mtm_entry_hint: DashboardMtmEntryHint
}
