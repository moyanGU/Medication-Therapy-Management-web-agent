import { api } from '@/utils/api'
import type { PaginatedResponse } from '@/types/medicine'
import type { ApiResponse, RequestConfig } from '@/utils/api'

const isDebug = import.meta.env.MODE !== 'production'

// 提醒相关接口
export interface Reminder {
  id: number
  user: number
  /**
   * 注意：后端在不同序列化器下，medicine 可能仅返回主键ID，或包含部分对象信息。
   * 因此统一声明为 number | { id: number; name?: string; medicine_type?: string; specification?: string }。
   */
  medicine:
    | number
    | {
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
  frequency:
    | 'daily'
    | 'twice_daily'
    | 'three_times_daily'
    | 'four_times_daily'
    | 'weekly'
    | 'every_other_day'
    | 'custom'
  dosage: number
  dosage_unit:
    | 'tablet'
    | 'capsule'
    | 'ml'
    | 'mg'
    | 'g'
    | 'drop'
    | 'spray'
    | 'patch'
    | 'injection'
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

export interface ReminderTestNotificationResult {
  delivered: boolean
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

export interface ReminderConfirmPayload {
  action: 'taken' | 'missed' | 'delayed' | 'partial'
  taken_at?: string
  delay_minutes?: number
  quantity_taken?: number
  notes?: string
}

export interface ReminderConfirmResult {
  reminder_id: number
  action: 'taken' | 'missed' | 'delayed' | 'partial'
  response_recorded: boolean
  response_count: number
  history_recorded: boolean
  record_id?: number | null
  record_created?: boolean
  record_payload: {
    reminder_id: number
    medicine_id: number
    action: 'taken' | 'missed' | 'delayed' | 'partial'
    record_status: 'taken' | 'missed' | 'delayed' | 'partial'
    scheduled_time: string
    taken_at: string | null
    delay_minutes?: number | null
    quantity_taken: number
    notes?: string
    source: 'reminder'
    administration_method: string
  }
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
  private async call<T>(
    action: string,
    fn: () => Promise<ApiResponse<T>>
  ): Promise<ApiResponse<T>> {
    try {
      const res = await fn()
      return res
    } catch (error) {
      if (isDebug) {
        console.error(`[ReminderService] ${action} 失败`, error)
      } else {
        console.error(`[ReminderService] ${action} 失败`)
      }
      throw error
    }
  }

  async getReminders(
    filters?: ReminderFilters
  ): Promise<ApiResponse<PaginatedResponse<Reminder>>> {
    const params = new URLSearchParams()

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }

    const query = params.toString()
    const url = query ? `/reminders/?${query}` : '/reminders/'
    return this.call('getReminders', () =>
      api.get<PaginatedResponse<Reminder>>(url)
    )
  }

  async getReminder(id: number): Promise<ApiResponse<Reminder>> {
    return this.call('getReminder', () =>
      api.get<Reminder>(`/reminders/${id}/`)
    )
  }

  async createReminder(
    payload: ReminderCreate,
    config: RequestConfig = {}
  ): Promise<ApiResponse<Reminder>> {
    return this.call('createReminder', () =>
      api.post<Reminder>(`/reminders/`, payload, config)
    )
  }

  async updateReminder(
    id: number,
    payload: Partial<ReminderCreate>,
    config: RequestConfig = {}
  ): Promise<ApiResponse<Reminder>> {
    return this.call('updateReminder', () =>
      api.patch<Reminder>(`/reminders/${id}/`, payload, config)
    )
  }

  async deleteReminder(id: number): Promise<ApiResponse<void>> {
    return this.call('deleteReminder', () =>
      api.delete<void>(`/reminders/${id}/`)
    )
  }

  async getTodayReminders(): Promise<ApiResponse<Reminder[]>> {
    return this.call('getTodayReminders', () =>
      api.get<Reminder[]>(`/reminders/today/`)
    )
  }

  async getUpcomingReminders(): Promise<ApiResponse<Reminder[]>> {
    return this.call('getUpcomingReminders', () =>
      api.get<Reminder[]>(`/reminders/upcoming/`)
    )
  }

  async getActiveReminders(): Promise<ApiResponse<Reminder[]>> {
    return this.call('getActiveReminders', () =>
      api.get<Reminder[]>(`/reminders/active/`)
    )
  }

  async getExpiredReminders(): Promise<ApiResponse<Reminder[]>> {
    return this.call('getExpiredReminders', () =>
      api.get<Reminder[]>(`/reminders/expired/`)
    )
  }

  async getReminderStats(): Promise<ApiResponse<ReminderStats>> {
    return this.call('getReminderStats', () =>
      api.get<ReminderStats>(`/reminders/stats/`)
    )
  }

  async toggleReminderActive(id: number): Promise<ApiResponse<Reminder>> {
    return this.call('toggleReminderActive', () =>
      api.post<Reminder>(`/reminders/${id}/toggle_active/`)
    )
  }

  async markReminderResponded(id: number): Promise<ApiResponse<Reminder>> {
    return this.call('markReminderResponded', () =>
      api.post<Reminder>(`/reminders/${id}/mark_responded/`)
    )
  }

  async confirmReminder(
    id: number,
    payload: ReminderConfirmPayload
  ): Promise<ApiResponse<ReminderConfirmResult>> {
    return this.call('confirmReminder', () =>
      api.post<ReminderConfirmResult>(`/reminders/${id}/confirm/`, payload)
    )
  }

  async testNotification(
    id: number
  ): Promise<ApiResponse<ReminderTestNotificationResult>> {
    return this.call('testNotification', () =>
      api.post<ReminderTestNotificationResult>(`/reminders/${id}/test_notification/`)
    )
  }

  async batchToggleReminders(
    reminderIds: number[],
    isActive: boolean
  ): Promise<ApiResponse<{ updated_count: number }>> {
    return this.call('batchToggleReminders', () =>
      api.post<{ updated_count: number }>(`/reminders/batch_toggle/`, {
        reminder_ids: reminderIds,
        is_active: isActive,
      })
    )
  }

  async batchDeleteReminders(
    reminderIds: number[]
  ): Promise<ApiResponse<{ deleted_count: number }>> {
    return this.call('batchDeleteReminders', () =>
      api.post<{ deleted_count: number }>(`/reminders/batch_delete/`, {
        reminder_ids: reminderIds,
      })
    )
  }

  async getReminderHistory(
    filters?: ReminderHistoryFilters
  ): Promise<ApiResponse<PaginatedResponse<ReminderHistory>>> {
    const params = new URLSearchParams()

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }

    const query = params.toString()
    const url = query
      ? `/reminders/reminder-history/?${query}`
      : '/reminders/reminder-history/'
    return this.call('getReminderHistory', () =>
      api.get<PaginatedResponse<ReminderHistory>>(url)
    )
  }

  async getReminderHistoryItem(
    id: number
  ): Promise<ApiResponse<ReminderHistory>> {
    return this.call('getReminderHistoryItem', () =>
      api.get<ReminderHistory>(`/reminders/reminder-history/${id}/`)
    )
  }

  async respondToReminder(
    id: number,
    payload: ReminderHistoryResponse
  ): Promise<ApiResponse<ReminderHistory>> {
    return this.call('respondToReminder', () =>
      api.post<ReminderHistory>(
        `/reminders/reminder-history/${id}/respond/`,
        payload
      )
    )
  }

  async getTodayHistory(): Promise<ApiResponse<ReminderHistory[]>> {
    return this.call('getTodayHistory', () =>
      api.get<ReminderHistory[]>(`/reminders/reminder-history/today/`)
    )
  }

  async getRecentHistory(): Promise<ApiResponse<ReminderHistory[]>> {
    return this.call('getRecentHistory', () =>
      api.get<ReminderHistory[]>(`/reminders/reminder-history/recent/`)
    )
  }

  async getUnrespondedHistory(): Promise<ApiResponse<ReminderHistory[]>> {
    return this.call('getUnrespondedHistory', () =>
      api.get<ReminderHistory[]>(`/reminders/reminder-history/unresponded/`)
    )
  }

  async getHistoryStatistics(days: number = 30): Promise<ApiResponse<any>> {
    return this.call('getHistoryStatistics', () =>
      api.get<any>(`/reminders/reminder-history/statistics/?days=${days}`)
    )
  }

  async getHistoryMetrics(days: number = 7): Promise<ApiResponse<any>> {
    return this.call('getHistoryMetrics', () =>
      api.get<any>(`/reminders/reminder-history/metrics/?days=${days}`)
    )
  }

  async batchRespondToReminders(
    historyIds: number[],
    responseType: string,
    notes?: string
  ): Promise<ApiResponse<{ updated_count: number }>> {
    return this.call('batchRespondToReminders', () =>
      api.post<{ updated_count: number }>(
        `/reminders/reminder-history/batch_respond/`,
        {
          history_ids: historyIds,
          response_type: responseType,
          notes,
        }
      )
    )
  }

  async getStatsSummary(days: number = 30): Promise<ApiResponse<any>> {
    return this.call('getStatsSummary', () =>
      api.get<any>(`/reminder-stats/summary/?days=${days}`)
    )
  }

  async getStatsTrends(days: number = 30): Promise<ApiResponse<any>> {
    return this.call('getStatsTrends', () =>
      api.get<any>(`/reminder-stats/trend/?days=${days}`)
    )
  }

  async getComplianceAnalysis(): Promise<ApiResponse<any>> {
    return this.call('getComplianceAnalysis', () =>
      api.get<any>(`/reminder-stats/compliance/`)
    )
  }
}

export const reminderService = new ReminderService()
