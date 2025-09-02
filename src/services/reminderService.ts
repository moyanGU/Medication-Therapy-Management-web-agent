import { http } from '@/utils/http'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

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
  private baseUrl = '/api/reminders'

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
    
    const response = await http.get<ApiResponse<PaginatedResponse<Reminder>>>(
      `${this.baseUrl}/reminders/?${params.toString()}`
    )
    return response.data.data
  }

  async getReminder(id: number): Promise<Reminder> {
    const response = await http.get<ApiResponse<Reminder>>(
      `${this.baseUrl}/reminders/${id}/`
    )
    return response.data.data
  }

  async createReminder(data: ReminderCreate): Promise<Reminder> {
    const response = await http.post<ApiResponse<Reminder>>(
      `${this.baseUrl}/reminders/`,
      data
    )
    return response.data.data
  }

  async updateReminder(id: number, data: Partial<ReminderCreate>): Promise<Reminder> {
    const response = await http.patch<ApiResponse<Reminder>>(
      `${this.baseUrl}/reminders/${id}/`,
      data
    )
    return response.data.data
  }

  async deleteReminder(id: number): Promise<void> {
    await http.delete(`${this.baseUrl}/reminders/${id}/`)
  }

  // 特殊查询
  async getTodayReminders(): Promise<Reminder[]> {
    const response = await http.get<ApiResponse<Reminder[]>>(
      `${this.baseUrl}/reminders/today/`
    )
    return response.data.data
  }

  async getUpcomingReminders(): Promise<Reminder[]> {
    const response = await http.get<ApiResponse<Reminder[]>>(
      `${this.baseUrl}/reminders/upcoming/`
    )
    return response.data.data
  }

  async getActiveReminders(): Promise<Reminder[]> {
    const response = await http.get<ApiResponse<Reminder[]>>(
      `${this.baseUrl}/reminders/active/`
    )
    return response.data.data
  }

  async getExpiredReminders(): Promise<Reminder[]> {
    const response = await http.get<ApiResponse<Reminder[]>>(
      `${this.baseUrl}/reminders/expired/`
    )
    return response.data.data
  }

  // 统计信息
  async getReminderStats(): Promise<ReminderStats> {
    const response = await http.get<ApiResponse<ReminderStats>>(
      `${this.baseUrl}/reminders/stats/`
    )
    return response.data.data
  }

  // 操作
  async toggleReminderActive(id: number): Promise<Reminder> {
    const response = await http.post<ApiResponse<Reminder>>(
      `${this.baseUrl}/reminders/${id}/toggle_active/`
    )
    return response.data.data
  }

  async markReminderResponded(id: number): Promise<Reminder> {
    const response = await http.post<ApiResponse<Reminder>>(
      `${this.baseUrl}/reminders/${id}/mark_responded/`
    )
    return response.data.data
  }

  async testNotification(id: number): Promise<void> {
    await http.post(`${this.baseUrl}/reminders/${id}/test_notification/`)
  }

  // 批量操作
  async batchToggleReminders(reminderIds: number[], isActive: boolean): Promise<{ updated_count: number }> {
    const response = await http.post<ApiResponse<{ updated_count: number }>>(
      `${this.baseUrl}/reminders/batch_toggle/`,
      {
        reminder_ids: reminderIds,
        is_active: isActive
      }
    )
    return response.data.data
  }

  async batchDeleteReminders(reminderIds: number[]): Promise<{ deleted_count: number }> {
    const response = await http.delete<ApiResponse<{ deleted_count: number }>>(
      `${this.baseUrl}/reminders/batch_delete/`,
      {
        data: {
          reminder_ids: reminderIds
        }
      }
    )
    return response.data.data
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
    
    const response = await http.get<ApiResponse<PaginatedResponse<ReminderHistory>>>(
      `${this.baseUrl}/reminder-history/?${params.toString()}`
    )
    return response.data.data
  }

  async getReminderHistoryItem(id: number): Promise<ReminderHistory> {
    const response = await http.get<ApiResponse<ReminderHistory>>(
      `${this.baseUrl}/reminder-history/${id}/`
    )
    return response.data.data
  }

  async respondToReminder(id: number, data: ReminderHistoryResponse): Promise<ReminderHistory> {
    const response = await http.post<ApiResponse<ReminderHistory>>(
      `${this.baseUrl}/reminder-history/${id}/respond/`,
      data
    )
    return response.data.data
  }

  async getTodayHistory(): Promise<ReminderHistory[]> {
    const response = await http.get<ApiResponse<ReminderHistory[]>>(
      `${this.baseUrl}/reminder-history/today/`
    )
    return response.data.data
  }

  async getRecentHistory(): Promise<ReminderHistory[]> {
    const response = await http.get<ApiResponse<ReminderHistory[]>>(
      `${this.baseUrl}/reminder-history/recent/`
    )
    return response.data.data
  }

  async getUnrespondedHistory(): Promise<ReminderHistory[]> {
    const response = await http.get<ApiResponse<ReminderHistory[]>>(
      `${this.baseUrl}/reminder-history/unresponded/`
    )
    return response.data.data
  }

  async getHistoryStatistics(days: number = 30): Promise<any> {
    const response = await http.get<ApiResponse<any>>(
      `${this.baseUrl}/reminder-history/statistics/?days=${days}`
    )
    return response.data.data
  }

  // 批量响应
  async batchRespondToReminders(
    historyIds: number[], 
    responseType: string, 
    notes?: string
  ): Promise<{ updated_count: number }> {
    const response = await http.post<ApiResponse<{ updated_count: number }>>(
      `${this.baseUrl}/reminder-history/batch_respond/`,
      {
        history_ids: historyIds,
        response_type: responseType,
        notes
      }
    )
    return response.data.data
  }

  // 统计相关
  async getStatsSummary(days: number = 30): Promise<any> {
    const response = await http.get<ApiResponse<any>>(
      `${this.baseUrl}/reminder-stats/summary/?days=${days}`
    )
    return response.data.data
  }

  async getStatsTrends(days: number = 30): Promise<any> {
    const response = await http.get<ApiResponse<any>>(
      `${this.baseUrl}/reminder-stats/trend/?days=${days}`
    )
    return response.data.data
  }

  async getComplianceAnalysis(): Promise<any> {
    const response = await http.get<ApiResponse<any>>(
      `${this.baseUrl}/reminder-stats/compliance/`
    )
    return response.data.data
  }
}

export const reminderService = new ReminderService()