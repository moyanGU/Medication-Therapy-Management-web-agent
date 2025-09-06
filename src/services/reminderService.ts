import { api } from '@/utils/api'
import type { PaginatedResponse } from '@/types/medicine'

// 提醒相关接口
export interface Reminder {
  id: number
  user: number
  medicine: {
    id: number
    name: string
    generic_name?: string
    dosage_form?: string
  }
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
  async getReminders(filters?: ReminderFilters): Promise<PaginatedResponse<Reminder>> {
    const params = new URLSearchParams()
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const { data } = await api.get<PaginatedResponse<Reminder>>(
      `/reminders/?${params.toString()}`
    )
    return data
  }

  async getReminder(id: number): Promise<Reminder> {
    const { data } = await api.get<Reminder>(
      `/reminders/${id}/`
    )
    return data
  }

  async createReminder(payload: ReminderCreate): Promise<Reminder> {
    const { data } = await api.post<Reminder>(
      `/reminders/`,
      payload
    )
    return data
  }

  async updateReminder(id: number, payload: Partial<ReminderCreate>): Promise<Reminder> {
    const { data } = await api.patch<Reminder>(
      `/reminders/${id}/`,
      payload
    )
    return data
  }

  async deleteReminder(id: number): Promise<void> {
    await api.delete<void>(`/reminders/${id}/`)
  }

  // 特殊查询
  async getTodayReminders(): Promise<Reminder[]> {
    const { data } = await api.get<Reminder[]>(
      `/reminders/today/`
    )
    return data
  }

  async getUpcomingReminders(): Promise<Reminder[]> {
    const { data } = await api.get<Reminder[]>(
      `/reminders/upcoming/`
    )
    return data
  }

  async getActiveReminders(): Promise<Reminder[]> {
    const { data } = await api.get<Reminder[]>(
      `/reminders/active/`
    )
    return data
  }

  async getExpiredReminders(): Promise<Reminder[]> {
    const { data } = await api.get<Reminder[]>(
      `/reminders/expired/`
    )
    return data
  }

  // 统计信息
  async getReminderStats(): Promise<ReminderStats> {
    const { data } = await api.get<ReminderStats>(
      `/reminders/stats/`
    )
    return data
  }

  // 操作
  async toggleReminderActive(id: number): Promise<Reminder> {
    const { data } = await api.post<Reminder>(
      `/reminders/${id}/toggle_active/`
    )
    return data
  }

  async markReminderResponded(id: number): Promise<Reminder> {
    const { data } = await api.post<Reminder>(
      `/reminders/${id}/mark_responded/`
    )
    return data
  }

  async testNotification(id: number): Promise<void> {
    await api.post<void>(`/reminders/${id}/test_notification/`)
  }

  // 批量操作
  async batchToggleReminders(reminderIds: number[], isActive: boolean): Promise<{ updated_count: number }> {
    const { data } = await api.post<{ updated_count: number }>(
      `/reminders/batch_toggle/`,
      {
        reminder_ids: reminderIds,
        is_active: isActive
      }
    )
    return data
  }

  async batchDeleteReminders(reminderIds: number[]): Promise<{ deleted_count: number }> {
    const { data } = await api.delete<{ deleted_count: number }>(
      `/reminders/batch_delete/`,
      {
        body: JSON.stringify({
          reminder_ids: reminderIds
        })
      }
    )
    return data
  }

  // 提醒历史记录
  async getReminderHistory(filters?: ReminderHistoryFilters): Promise<PaginatedResponse<ReminderHistory>> {
    const params = new URLSearchParams()
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const { data } = await api.get<PaginatedResponse<ReminderHistory>>(
      `/reminder-history/?${params.toString()}`
    )
    return data
  }

  async getReminderHistoryItem(id: number): Promise<ReminderHistory> {
    const { data } = await api.get<ReminderHistory>(
      `/reminder-history/${id}/`
    )
    return data
  }

  async respondToReminder(id: number, payload: ReminderHistoryResponse): Promise<ReminderHistory> {
    const { data } = await api.post<ReminderHistory>(
      `/reminder-history/${id}/respond/`,
      payload
    )
    return data
  }

  async getTodayHistory(): Promise<ReminderHistory[]> {
    const { data } = await api.get<ReminderHistory[]>(
      `/reminder-history/today/`
    )
    return data
  }

  async getRecentHistory(): Promise<ReminderHistory[]> {
    const { data } = await api.get<ReminderHistory[]>(
      `/reminder-history/recent/`
    )
    return data
  }

  async getUnrespondedHistory(): Promise<ReminderHistory[]> {
    const { data } = await api.get<ReminderHistory[]>(
      `/reminder-history/unresponded/`
    )
    return data
  }

  async getHistoryStatistics(days: number = 30): Promise<any> {
    const { data } = await api.get<any>(
      `/reminder-history/statistics/?days=${days}`
    )
    return data
  }

  // 批量响应
  async batchRespondToReminders(
    historyIds: number[], 
    responseType: string, 
    notes?: string
  ): Promise<{ updated_count: number }> {
    const { data } = await api.post<{ updated_count: number }>(
      `/reminder-history/batch_respond/`,
      {
        history_ids: historyIds,
        response_type: responseType,
        notes
      }
    )
    return data
  }

  // 统计相关
  async getStatsSummary(days: number = 30): Promise<any> {
    const { data } = await api.get<any>(
      `/reminder-stats/summary/?days=${days}`
    )
    return data
  }

  async getStatsTrends(days: number = 30): Promise<any> {
    const { data } = await api.get<any>(
      `/reminder-stats/trend/?days=${days}`
    )
    return data
  }

  async getComplianceAnalysis(): Promise<any> {
    const { data } = await api.get<any>(
      `/reminder-stats/compliance/`
    )
    return data
  }
}

export const reminderService = new ReminderService()