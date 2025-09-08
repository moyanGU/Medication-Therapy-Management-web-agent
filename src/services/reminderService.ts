import { api } from '@/utils/api'
import type { PaginatedResponse } from '@/types/medicine'
import type { ApiResponse } from '@/utils/api'

// 提醒相关接口
export interface Reminder {
  id: number
  user: number
  /**
   * 注意：后端在不同序列化器下，medicine 可能仅返回主键ID，或包含部分对象信息。
   * 因此统一声明为 number | { id: number; name?: string; medicine_type?: string; specification?: string }。
   */
  medicine: number | {
    id: number
    name?: string
    medicine_type?: string
    specification?: string
  }
  /** 补充的派生字段，来自 serializers: source='medicine.name' */
  medicine_name?: string
  /** 可能存在的图片字段 */
  medicine_image?: string
  reminder_time: string
  frequency: 'daily' | 'twice_daily' | 'three_times_daily' | 'four_times_daily' | 'weekly' | 'every_other_day' | 'custom'
  dosage: number
  dosage_unit: 'tablet' | 'capsule' | 'ml' | 'mg' | 'g' | 'drop' | 'spray' | 'patch' | 'injection'
  is_active: boolean
  title?: string
  message?: string
  notification_types: string[]
  advance_minutes: number
  repeat_interval: number
  max_repeats: number
  start_date: string
  end_date?: string
  weekdays: number[]
  meal_timing: 'before_meal' | 'after_meal' | 'with_meal' | 'anytime'
  special_instructions?: string
  last_reminded_at?: string
  reminder_count: number
  response_count: number
  created_at: string
  updated_at: string
}

export interface ReminderCreate {
  medicine: number
  reminder_time: string
  frequency: string
  dosage: number
  dosage_unit: string
  is_active?: boolean
  title?: string
  message?: string
  notification_types?: string[]
  advance_minutes?: number
  repeat_interval?: number
  max_repeats?: number
  start_date: string
  end_date?: string
  weekdays?: number[]
  meal_timing?: string
  special_instructions?: string
}

export interface ReminderUpdate extends Partial<ReminderCreate> {
  id: number
}

export interface ReminderStats {
  total_reminders: number
  active_reminders: number
  inactive_reminders: number
  expired_reminders: number
  today_reminders: number
  response_rate: number
  total_responses: number
}

export interface ReminderHistory {
  id: number
  reminder: number
  reminder_title: string
  medicine_name: string
  medicine_id: number
  sent_at: string
  scheduled_time: string
  reminder_type: 'scheduled' | 'repeat' | 'manual' | 'makeup'
  title: string
  message: string
  notification_methods: string[]
  status: 'sent' | 'failed' | 'pending' | 'cancelled'
  responded_at?: string
  response_type: 'taken' | 'skipped' | 'delayed' | 'ignored' | 'no_response'
  response_delay_minutes?: number
  response_delay_display: string
  notes?: string
  device_info: Record<string, any>
  is_responded: boolean
  is_successful: boolean
  created_at: string
}

export interface ReminderHistoryResponse {
  response_type: 'taken' | 'skipped' | 'delayed' | 'ignored'
  notes?: string
}

export interface ReminderFilters {
  medicine?: number
  medicine_name?: string
  is_active?: boolean
  frequency?: string
  meal_timing?: string
  start_date?: string
  end_date?: string
  search?: string
  ordering?: string
  page?: number
  page_size?: number
}

export interface ReminderHistoryFilters {
  reminder?: number
  medicine?: number
  medicine_name?: string
  status?: string
  response_type?: string
  reminder_type?: string
  sent_date?: string
  sent_date_after?: string
  sent_date_before?: string
  is_responded?: boolean
  is_successful?: boolean
  time_range?: string
  search?: string
  ordering?: string
  page?: number
  page_size?: number
}

class ReminderService {
  // 使用统一 api 客户端的 baseURL，无需 '/api' 前缀

  // 提醒CRUD操作
  async getReminders(filters?: ReminderFilters): Promise<ApiResponse<PaginatedResponse<Reminder>>> {
    const params = new URLSearchParams()
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const res = await api.get<PaginatedResponse<Reminder>>(
      `/reminders/?${params.toString()}`
    )
    return res
  }

  async getReminder(id: number): Promise<ApiResponse<Reminder>> {
    const res = await api.get<Reminder>(
      `/reminders/${id}/`
    )
    return res
  }

  async createReminder(payload: ReminderCreate): Promise<ApiResponse<Reminder>> {
    const res = await api.post<Reminder>(
      `/reminders/`,
      payload
    )
    return res
  }

  async updateReminder(id: number, payload: Partial<ReminderCreate>): Promise<ApiResponse<Reminder>> {
    const res = await api.patch<Reminder>(
      `/reminders/${id}/`,
      payload
    )
    return res
  }

  async deleteReminder(id: number): Promise<ApiResponse<void>> {
    const res = await api.delete<void>(`/reminders/${id}/`)
    return res
  }

  // 特殊查询
  async getTodayReminders(): Promise<ApiResponse<Reminder[]>> {
    const res = await api.get<Reminder[]>(
      `/reminders/today/`
    )
    return res
  }

  async getUpcomingReminders(): Promise<ApiResponse<Reminder[]>> {
    const res = await api.get<Reminder[]>(
      `/reminders/upcoming/`
    )
    return res
  }

  async getActiveReminders(): Promise<ApiResponse<Reminder[]>> {
    const res = await api.get<Reminder[]>(
      `/reminders/active/`
    )
    return res
  }

  async getExpiredReminders(): Promise<ApiResponse<Reminder[]>> {
    const res = await api.get<Reminder[]>(
      `/reminders/expired/`
    )
    return res
  }

  // 统计信息
  async getReminderStats(): Promise<ApiResponse<ReminderStats>> {
    const res = await api.get<ReminderStats>(
      `/reminders/stats/`
    )
    return res
  }

  // 操作
  async toggleReminderActive(id: number): Promise<ApiResponse<Reminder>> {
    const res = await api.post<Reminder>(
      `/reminders/${id}/toggle_active/`
    )
    return res
  }

  async markReminderResponded(id: number): Promise<ApiResponse<Reminder>> {
    const res = await api.post<Reminder>(
      `/reminders/${id}/mark_responded/`
    )
    return res
  }

  async testNotification(id: number): Promise<ApiResponse<void>> {
    const res = await api.post<void>(`/reminders/${id}/test_notification/`)
    return res
  }

  // 批量操作
  async batchToggleReminders(reminderIds: number[], isActive: boolean): Promise<ApiResponse<{ updated_count: number }>> {
    const res = await api.post<{ updated_count: number }>(
      `/reminders/batch_toggle/`,
      {
        reminder_ids: reminderIds,
        is_active: isActive
      }
    )
    return res
  }

  async batchDeleteReminders(reminderIds: number[]): Promise<ApiResponse<{ deleted_count: number }>> {
    const res = await api.post<{ deleted_count: number }>(
      `/reminders/batch_delete/`,
      {
        reminder_ids: reminderIds
      }
    )
    return res
  }

  // 提醒历史记录
  async getReminderHistory(filters?: ReminderHistoryFilters): Promise<ApiResponse<PaginatedResponse<ReminderHistory>>> {
    const params = new URLSearchParams()
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const res = await api.get<PaginatedResponse<ReminderHistory>>(
      `/reminder-history/?${params.toString()}`
    )
    return res
  }

  async getReminderHistoryItem(id: number): Promise<ApiResponse<ReminderHistory>> {
    const res = await api.get<ReminderHistory>(
      `/reminder-history/${id}/`
    )
    return res
  }

  async respondToReminder(id: number, payload: ReminderHistoryResponse): Promise<ApiResponse<ReminderHistory>> {
    const res = await api.post<ReminderHistory>(
      `/reminder-history/${id}/respond/`,
      payload
    )
    return res
  }

  async getTodayHistory(): Promise<ApiResponse<ReminderHistory[]>> {
    const res = await api.get<ReminderHistory[]>(
      `/reminder-history/today/`
    )
    return res
  }

  async getRecentHistory(): Promise<ApiResponse<ReminderHistory[]>> {
    const res = await api.get<ReminderHistory[]>(
      `/reminder-history/recent/`
    )
    return res
  }

  async getUnrespondedHistory(): Promise<ApiResponse<ReminderHistory[]>> {
    const res = await api.get<ReminderHistory[]>(
      `/reminder-history/unresponded/`
    )
    return res
  }

  async getHistoryStatistics(days: number = 30): Promise<ApiResponse<any>> {
    const res = await api.get<any>(
      `/reminder-history/statistics/?days=${days}`
    )
    return res
  }

  // 批量响应
  async batchRespondToReminders(
    historyIds: number[], 
    responseType: string, 
    notes?: string
  ): Promise<ApiResponse<{ updated_count: number }>> {
    const res = await api.post<{ updated_count: number }>(
      `/reminder-history/batch_respond/`,
      {
        history_ids: historyIds,
        response_type: responseType,
        notes
      }
    )
    return res
  }

  // 统计相关
  async getStatsSummary(days: number = 30): Promise<ApiResponse<any>> {
    const res = await api.get<any>(
      `/reminder-stats/summary/?days=${days}`
    )
    return res
  }

  async getStatsTrends(days: number = 30): Promise<ApiResponse<any>> {
    const res = await api.get<any>(
      `/reminder-stats/trend/?days=${days}`
    )
    return res
  }

  async getComplianceAnalysis(): Promise<ApiResponse<any>> {
    const res = await api.get<any>(
      `/reminder-stats/compliance/`
    )
    return res
  }
}

export const reminderService = new ReminderService()