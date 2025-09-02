import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { reminderService } from '@/services/reminderService'
import type { 
  Reminder, 
  ReminderHistory, 
  ReminderStats,
  CreateReminderData,
  ReminderListParams,
  ReminderHistoryParams,
  BatchToggleData,
  BatchDeleteData,
  BatchRespondData,
  RespondData
} from '@/services/reminderService'
import { useToast } from '@/composables/useToast'

export const useReminderStore = defineStore('reminder', () => {
  const { showToast } = useToast()

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
  const filters = ref<ReminderListParams>({})
  const historyFilters = ref<ReminderHistoryParams>({})
  
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
  const fetchReminders = async (params?: ReminderListParams) => {
    try {
      loading.value = true
      error.value = null
      
      const mergedParams = { ...filters.value, ...params }
      const response = await reminderService.getReminders(mergedParams)
      
      if (response.success) {
        reminders.value = response.data.data || response.data
        
        // 更新分页信息
        if (response.data.pagination) {
          pagination.value = {
            page: response.data.pagination.page,
            pageSize: response.data.pagination.page_size,
            total: response.data.pagination.total,
            totalPages: response.data.pagination.total_pages
          }
        }
      } else {
        throw new Error(response.message || '获取提醒列表失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取提醒列表失败'
      showToast(error.value, 'error')
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
      showToast(error.value, 'error')
      return null
    } finally {
      loading.value = false
    }
  }

  const createReminder = async (data: CreateReminderData) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await reminderService.createReminder(data)
      
      if (response.success) {
        reminders.value.unshift(response.data)
        showToast('提醒创建成功', 'success')
        return response.data
      } else {
        throw new Error(response.message || '创建提醒失败')
      }
    } catch (err: any) {
      error.value = err.message || '创建提醒失败'
      showToast(error.value, 'error')
      return null
    } finally {
      loading.value = false
    }
  }

  const updateReminder = async (id: number, data: Partial<CreateReminderData>) => {
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
        showToast('提醒更新成功', 'success')
        return response.data
      } else {
        throw new Error(response.message || '更新提醒失败')
      }
    } catch (err: any) {
      error.value = err.message || '更新提醒失败'
      showToast(error.value, 'error')
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
        showToast('提醒删除成功', 'success')
        return true
      } else {
        throw new Error(response.message || '删除提醒失败')
      }
    } catch (err: any) {
      error.value = err.message || '删除提醒失败'
      showToast(error.value, 'error')
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
      showToast(error.value, 'error')
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
      showToast(error.value, 'error')
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
        showToast(response.message || '提醒状态更新成功', 'success')
        return response.data
      } else {
        throw new Error(response.message || '更新提醒状态失败')
      }
    } catch (err: any) {
      error.value = err.message || '更新提醒状态失败'
      showToast(error.value, 'error')
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
        showToast(response.message || '提醒已标记为已响应', 'success')
        return response.data
      } else {
        throw new Error(response.message || '标记提醒响应失败')
      }
    } catch (err: any) {
      error.value = err.message || '标记提醒响应失败'
      showToast(error.value, 'error')
      return null
    }
  }

  const testNotification = async (id: number) => {
    try {
      const response = await reminderService.testNotification(id)
      
      if (response.success) {
        showToast(response.message || '测试通知发送成功', 'success')
        return true
      } else {
        throw new Error(response.message || '测试通知发送失败')
      }
    } catch (err: any) {
      error.value = err.message || '测试通知发送失败'
      showToast(error.value, 'error')
      return false
    }
  }

  // 批量操作方法
  const batchToggleReminders = async (data: BatchToggleData) => {
    try {
      loading.value = true
      const response = await reminderService.batchToggleReminders(data)
      
      if (response.success) {
        // 刷新列表
        await fetchReminders()
        showToast(response.message || `成功更新 ${response.data.updated_count} 个提醒`, 'success')
        return response.data
      } else {
        throw new Error(response.message || '批量更新提醒状态失败')
      }
    } catch (err: any) {
      error.value = err.message || '批量更新提醒状态失败'
      showToast(error.value, 'error')
      return null
    } finally {
      loading.value = false
    }
  }

  const batchDeleteReminders = async (data: BatchDeleteData) => {
    try {
      loading.value = true
      const response = await reminderService.batchDeleteReminders(data)
      
      if (response.success) {
        // 从本地状态中移除删除的提醒
        reminders.value = reminders.value.filter(r => !data.reminder_ids.includes(r.id))
        showToast(response.message || `成功删除 ${response.data.deleted_count} 个提醒`, 'success')
        return response.data
      } else {
        throw new Error(response.message || '批量删除提醒失败')
      }
    } catch (err: any) {
      error.value = err.message || '批量删除提醒失败'
      showToast(error.value, 'error')
      return null
    } finally {
      loading.value = false
    }
  }

  // 提醒历史方法
  const fetchReminderHistory = async (params?: ReminderHistoryParams) => {
    try {
      loading.value = true
      error.value = null
      
      const mergedParams = { ...historyFilters.value, ...params }
      const response = await reminderService.getReminderHistory(mergedParams)
      
      if (response.success) {
        reminderHistory.value = response.data.data || response.data
        
        // 更新分页信息
        if (response.data.pagination) {
          historyPagination.value = {
            page: response.data.pagination.page,
            pageSize: response.data.pagination.page_size,
            total: response.data.pagination.total,
            totalPages: response.data.pagination.total_pages
          }
        }
      } else {
        throw new Error(response.message || '获取提醒历史失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取提醒历史失败'
      showToast(error.value, 'error')
    } finally {
      loading.value = false
    }
  }

  const respondToReminder = async (id: number, data: RespondData) => {
    try {
      const response = await reminderService.respondToReminder(id, data)
      
      if (response.success) {
        const index = reminderHistory.value.findIndex(h => h.id === id)
        if (index !== -1) {
          reminderHistory.value[index] = response.data
        }
        showToast(response.message || '响应记录成功', 'success')
        return response.data
      } else {
        throw new Error(response.message || '响应提醒失败')
      }
    } catch (err: any) {
      error.value = err.message || '响应提醒失败'
      showToast(error.value, 'error')
      return null
    }
  }

  const batchRespondToReminders = async (data: BatchRespondData) => {
    try {
      loading.value = true
      const response = await reminderService.batchRespondToReminders(data)
      
      if (response.success) {
        // 刷新历史列表
        await fetchReminderHistory()
        showToast(response.message || `成功响应 ${response.data.updated_count} 条提醒`, 'success')
        return response.data
      } else {
        throw new Error(response.message || '批量响应提醒失败')
      }
    } catch (err: any) {
      error.value = err.message || '批量响应提醒失败'
      showToast(error.value, 'error')
      return null
    } finally {
      loading.value = false
    }
  }

  // 统计数据方法
  const fetchStatistics = async (params?: { days?: number }) => {
    try {
      loading.value = true
      const response = await reminderService.getHistoryStatistics(params)
      
      if (response.success) {
        statistics.value = response.data
        return response.data
      } else {
        throw new Error(response.message || '获取统计数据失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取统计数据失败'
      showToast(error.value, 'error')
      return {}
    } finally {
      loading.value = false
    }
  }

  const fetchCompliance = async (params?: { days?: number }) => {
    try {
      loading.value = true
      const response = await reminderService.getComplianceData(params)
      
      if (response.success) {
        compliance.value = response.data
        return response.data
      } else {
        throw new Error(response.message || '获取依从性数据失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取依从性数据失败'
      showToast(error.value, 'error')
      return {}
    } finally {
      loading.value = false
    }
  }

  const fetchTrends = async (params?: { days?: number }) => {
    try {
      loading.value = true
      const response = await reminderService.getStatsTrends(params)
      
      if (response.success) {
        trends.value = response.data
        return response.data
      } else {
        throw new Error(response.message || '获取趋势数据失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取趋势数据失败'
      showToast(error.value, 'error')
      return []
    } finally {
      loading.value = false
    }
  }

  // 工具方法
  const setFilters = (newFilters: ReminderListParams) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const setHistoryFilters = (newFilters: ReminderHistoryParams) => {
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