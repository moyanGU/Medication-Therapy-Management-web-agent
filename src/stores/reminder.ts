import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { reminderService } from '@/services/reminderService'
import type { 
  Reminder, 
  ReminderHistory, 
  ReminderStats,
  ReminderCreate,
  ReminderFilters,
  ReminderHistoryFilters,
  ReminderHistoryResponse
} from '@/services/reminderService'
import { useToast } from '@/composables/useToast'

export const useReminderStore = defineStore('reminder', () => {
  const { success: showSuccess, error: showError } = useToast()

  // 状态
  const reminders = ref<Reminder[]>([])
  const reminderHistory = ref<ReminderHistory[]>([])
  const reminderStats = ref<ReminderStats[]>([])
  const currentReminder = ref<Reminder | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 分页信息
  const pagination = ref({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  })
  
  const historyPagination = ref({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  })
  
  // 筛选参数
  const filters = ref<ReminderFilters>({})
  const historyFilters = ref<ReminderHistoryFilters>({})
  
  // 统计数据
  const statistics = ref<any>({})
  const compliance = ref<any>({})
  const trends = ref<any[]>([])

  // 计算属性
  const activeReminders = computed(() => 
    reminders.value.filter(reminder => reminder.is_active)
  )
  
  const inactiveReminders = computed(() => 
    reminders.value.filter(reminder => !reminder.is_active)
  )
  
  const todayReminders = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return reminders.value.filter(reminder => {
      if (!reminder.is_active) return false
      if (reminder.start_date > today) return false
      if (reminder.end_date && reminder.end_date < today) return false
      return true
    })
  })
  
  const unrespondedHistory = computed(() => 
    reminderHistory.value.filter(history => !history.is_responded)
  )
  
  const totalReminders = computed(() => reminders.value.length)
  const totalActiveReminders = computed(() => activeReminders.value.length)
  const totalInactiveReminders = computed(() => inactiveReminders.value.length)

  // 提醒管理方法
  const fetchReminders = async (params?: ReminderFilters) => {
    try {
      loading.value = true
      error.value = null
      
      const mergedParams = { ...filters.value, ...params }
      const response = await reminderService.getReminders(mergedParams)
      
      if (response.success) {
        const pg: any = response.data
        console.log('[reminder] fetchReminders response.data:', pg)
        const results: Reminder[] = Array.isArray(pg?.results) ? pg.results : []
        reminders.value = results
        pagination.value = {
          page: pg?.current_page ?? pagination.value.page,
          pageSize: pg?.page_size ?? pagination.value.pageSize,
          total: pg?.count ?? results.length,
          totalPages: pg?.total_pages ?? Math.ceil((pg?.count ?? results.length) / (pg?.page_size ?? (pagination.value.pageSize ?? 1)))
        }
      } else {
        throw new Error(response.message || '获取提醒列表失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取提醒列表失败'
      showError(error.value)
    } finally {
      loading.value = false
    }
  }

  const fetchReminder = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await reminderService.getReminder(id)
      
      if (response.success) {
        currentReminder.value = response.data
        return response.data
      } else {
        throw new Error(response.message || '获取提醒详情失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取提醒详情失败'
      showError(error.value)
      return null
    } finally {
      loading.value = false
    }
  }

  const createReminder = async (data: ReminderCreate) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await reminderService.createReminder(data)
      
      if (response.success) {
        reminders.value.unshift(response.data)
        showSuccess('提醒创建成功')
        return response.data
      } else {
        throw new Error(response.message || '创建提醒失败')
      }
    } catch (err: any) {
      error.value = err.message || '创建提醒失败'
      showError(error.value)
      return null
    } finally {
      loading.value = false
    }
  }

  const updateReminder = async (id: number, data: Partial<ReminderCreate>) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await reminderService.updateReminder(id, data)
      
      if (response.success) {
        const index = reminders.value.findIndex(r => r.id === id)
        if (index !== -1) {
          reminders.value[index] = response.data
        }
        if (currentReminder.value?.id === id) {
          currentReminder.value = response.data
        }
        showSuccess('提醒更新成功')
        return response.data
      } else {
        throw new Error(response.message || '更新提醒失败')
      }
    } catch (err: any) {
        error.value = err.message || '更新提醒失败'
        showError(error.value)
        return null
    } finally {
      loading.value = false
    }
  }

  const deleteReminder = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await reminderService.deleteReminder(id)
      
      if (response.success) {
        reminders.value = reminders.value.filter(r => r.id !== id)
        if (currentReminder.value?.id === id) {
          currentReminder.value = null
        }
        showSuccess('提醒删除成功')
        return true
      } else {
        throw new Error(response.message || '删除提醒失败')
      }
    } catch (err: any) {
        error.value = err.message || '删除提醒失败'
        showError(error.value)
        return false
    } finally {
      loading.value = false
    }
  }

  // 特定查询方法
  const fetchTodayReminders = async () => {
    try {
      loading.value = true
      const response = await reminderService.getTodayReminders()
      
      if (response.success) {
        return response.data
      } else {
        throw new Error(response.message || '获取今日提醒失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取今日提醒失败'
      showError(error.value)
      return []
    } finally {
      loading.value = false
    }
  }

  const fetchUpcomingReminders = async () => {
    try {
      loading.value = true
      const response = await reminderService.getUpcomingReminders()
      
      if (response.success) {
        return response.data
      } else {
        throw new Error(response.message || '获取即将到来的提醒失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取即将到来的提醒失败'
      showError(error.value)
      return []
    } finally {
      loading.value = false
    }
  }

  // 提醒操作方法
  const toggleReminderActive = async (id: number) => {
    try {
      const response = await reminderService.toggleReminderActive(id)
      
      if (response.success) {
        const index = reminders.value.findIndex(r => r.id === id)
        if (index !== -1) {
          reminders.value[index] = response.data
        }
        if (currentReminder.value?.id === id) {
          currentReminder.value = response.data
        }
        showSuccess(response.message ?? `成功更新 ${(response.data as any)?.updated_count ?? 0} 个提醒`)
        return response.data
      } else {
        throw new Error(response.message || '更新提醒状态失败')
      }
    } catch (err: any) {
      error.value = err.message || '更新提醒状态失败'
      showError(error.value)
      return null
    }
  }

  const markReminderResponded = async (id: number) => {
    try {
      const response = await reminderService.markReminderResponded(id)
      
      if (response.success) {
        const index = reminders.value.findIndex(r => r.id === id)
        if (index !== -1) {
          reminders.value[index] = response.data
        }
        showSuccess(response.message || '提醒已标记为已响应')
        return response.data
      } else {
        throw new Error(response.message || '标记提醒响应失败')
      }
    } catch (err: any) {
        error.value = err.message || '标记提醒失败'
        showError(error.value)
        return null
    }
  }

  const testNotification = async (id: number) => {
    try {
      const response = await reminderService.testNotification(id)
      
      if (response.success) {
        showSuccess(response.message || '测试通知发送成功')
        return true
      } else {
        throw new Error(response.message || '测试通知发送失败')
      }
    } catch (err: any) {
        error.value = err.message || '发送测试通知失败'
        showError(error.value)
        return false
    }
  }

  // 批量操作方法
  const batchToggleReminders = async (data: { reminder_ids: number[]; is_active: boolean }) => {
    try {
      loading.value = true
      const response = await reminderService.batchToggleReminders(data.reminder_ids, data.is_active)
      
      if (response.success) {
        // 刷新列表
        await fetchReminders()
        showSuccess((response.message ?? `成功更新 ${(response.data as any)?.updated_count ?? 0} 个提醒`))
        return response.data
      } else {
        throw new Error(response.message || '批量更新提醒状态失败')
      }
    } catch (err: any) {
        error.value = err.message || '批量更新提醒失败'
        showError(error.value)
        return null
    } finally {
      loading.value = false
    }
  }

  const batchDeleteReminders = async (data: { reminder_ids: number[] }) => {
    try {
      loading.value = true
      const response = await reminderService.batchDeleteReminders(data.reminder_ids)
      
      if (response.success) {
        // 从本地状态中移除删除的提醒
        reminders.value = reminders.value.filter(r => !data.reminder_ids.includes(r.id))
        showSuccess(response.message ?? `成功删除 ${(response.data as any)?.deleted_count ?? 0} 个提醒`)
        return response.data
      } else {
        throw new Error(response.message || '批量删除提醒失败')
      }
    } catch (err: any) {
      error.value = err.message || '批量删除提醒失败'
      showError(error.value)
      return null
    } finally {
      loading.value = false
    }
  }

  // 提醒历史方法
  const fetchReminderHistory = async (params?: ReminderHistoryFilters) => {
    try {
      loading.value = true
      error.value = null
      
      const mergedParams = { ...historyFilters.value, ...params }
      const response = await reminderService.getReminderHistory(mergedParams)
      
      if (response.success) {
        const payload: any = response.data
        console.log('[reminder] fetchReminderHistory payload:', payload)
        
        // 兼容两种结构：
        // 1) 标准：{ results, pagination: { count, current_page, total_pages, page_size } }
        // 2) 旧版：{ results, count, current_page, total_pages, page_size }
        const results: ReminderHistory[] = Array.isArray(payload?.results)
          ? payload.results
          : Array.isArray(payload?.data?.results)
            ? payload.data.results
            : []
        
        const pagination = payload?.pagination || payload?.data?.pagination || null
        const count = pagination?.count ?? payload?.count ?? results.length
        const currentPage = pagination?.current_page ?? payload?.current_page ?? historyPagination.value.page
        const pageSize = pagination?.page_size ?? payload?.page_size ?? historyPagination.value.pageSize
        const totalPages = pagination?.total_pages ?? payload?.total_pages ?? Math.ceil(count / (pageSize || 1))
        
        reminderHistory.value = results
        historyPagination.value = {
          page: currentPage,
          pageSize: pageSize,
          total: count,
          totalPages: totalPages
        }
        
        console.log('[reminder] fetchReminderHistory parsed:', {
          count, currentPage, pageSize, totalPages, resultsLen: results.length
        })
      } else {
        throw new Error(response.message || '获取提醒历史失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取提醒历史失败'
      showError(error.value)
    } finally {
      loading.value = false
    }
  }

  const respondToReminder = async (id: number, data: ReminderHistoryResponse) => {
    try {
      const response = await reminderService.respondToReminder(id, data)
      
      if (response.success) {
        const index = reminderHistory.value.findIndex(h => h.id === id)
        if (index !== -1) {
          reminderHistory.value[index] = response.data
        }
        showSuccess(response.message || '响应记录成功')
        return response.data
      } else {
        throw new Error(response.message || '响应提醒失败')
      }
    } catch (err: any) {
      error.value = err.message || '响应提醒失败'
      showError(error.value)
      return null
    }
  }

  const batchRespondToReminders = async (data: { history_ids: number[]; response_type: string; notes?: string }) => {
    try {
      loading.value = true
      const response = await reminderService.batchRespondToReminders(data.history_ids, data.response_type, data.notes)
      
      if (response.success) {
        // 刷新历史列表
        await fetchReminderHistory()
        showSuccess(response.message ?? `成功响应 ${(response.data as any)?.updated_count ?? 0} 条提醒`)
        return response.data
      } else {
        throw new Error(response.message || '批量响应提醒失败')
      }
    } catch (err: any) {
      error.value = err.message || '批量响应提醒失败'
      showError(error.value)
      return null
    } finally {
      loading.value = false
    }
  }

  // 统计数据方法
  const fetchStatistics = async (params?: { days?: number }) => {
    try {
      loading.value = true
      const days = params?.days ?? 30
      const response = await reminderService.getHistoryStatistics(days)
      
      if (response.success) {
        statistics.value = response.data
        return response.data
      } else {
        throw new Error(response.message || '获取统计数据失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取统计数据失败'
      showError(error.value)
      return {}
    } finally {
      loading.value = false
    }
  }

  const fetchCompliance = async (_params?: { days?: number }) => {
    try {
      loading.value = true
      const response = await reminderService.getComplianceAnalysis()
      
      if (response.success) {
        compliance.value = response.data
        return response.data
      } else {
        throw new Error(response.message || '获取依从性数据失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取依从性数据失败'
      showError(error.value)
      return {}
    } finally {
      loading.value = false
    }
  }

  const fetchTrends = async (params?: { days?: number }) => {
    try {
      loading.value = true
      const days = params?.days ?? 30
      const response = await reminderService.getStatsTrends(days)
      
      if (response.success) {
        trends.value = response.data
        return response.data
      } else {
        throw new Error(response.message || '获取趋势数据失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取趋势数据失败'
      showError(error.value)
      return []
    } finally {
      loading.value = false
    }
  }

  // 工具方法
  const setFilters = (newFilters: ReminderFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const setHistoryFilters = (newFilters: ReminderHistoryFilters) => {
    historyFilters.value = { ...historyFilters.value, ...newFilters }
  }

  const clearFilters = () => {
    filters.value = {}
  }

  const clearHistoryFilters = () => {
    historyFilters.value = {}
  }

  const resetState = () => {
    reminders.value = []
    reminderHistory.value = []
    reminderStats.value = []
    currentReminder.value = null
    loading.value = false
    error.value = null
    pagination.value = { page: 1, pageSize: 20, total: 0, totalPages: 0 }
    historyPagination.value = { page: 1, pageSize: 20, total: 0, totalPages: 0 }
    filters.value = {}
    historyFilters.value = {}
    statistics.value = {}
    compliance.value = {}
    trends.value = []
  }

  return {
    // 状态
    reminders,
    reminderHistory,
    reminderStats,
    currentReminder,
    loading,
    error,
    pagination,
    historyPagination,
    filters,
    historyFilters,
    statistics,
    compliance,
    trends,
    
    // 计算属性
    activeReminders,
    inactiveReminders,
    todayReminders,
    unrespondedHistory,
    totalReminders,
    totalActiveReminders,
    totalInactiveReminders,
    
    // 提醒管理方法
    fetchReminders,
    fetchReminder,
    createReminder,
    updateReminder,
    deleteReminder,
    
    // 特定查询方法
    fetchTodayReminders,
    fetchUpcomingReminders,
    
    // 提醒操作方法
    toggleReminderActive,
    markReminderResponded,
    testNotification,
    
    // 批量操作方法
    batchToggleReminders,
    batchDeleteReminders,
    
    // 提醒历史方法
    fetchReminderHistory,
    respondToReminder,
    batchRespondToReminders,
    
    // 统计数据方法
    fetchStatistics,
    fetchCompliance,
    fetchTrends,
    
    // 工具方法
    setFilters,
    setHistoryFilters,
    clearFilters,
    clearHistoryFilters,
    resetState
  }
})