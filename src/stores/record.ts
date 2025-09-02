import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { recordApi } from '../api/record'
import type {
  MedicationRecord,
  MedicationRecordForm,
  MedicationRecordStats,
  MedicationTrend,
  MedicationRecordQuery
} from '../types/record'

/**
 * 用药记录状态管理
 */
export const useRecordStore = defineStore('record', () => {
  // 状态
  const records = ref<MedicationRecord[]>([])
  const currentRecord = ref<MedicationRecord | null>(null)
  const statistics = ref<MedicationRecordStats | null>(null)
  const trends = ref<MedicationTrend[]>([])
  const recentRecords = ref<MedicationRecord[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 分页信息
  const pagination = ref({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  })
  
  // 查询参数
  const queryParams = ref<MedicationRecordQuery>({})
  
  // 计算属性
  const hasRecords = computed(() => records.value.length > 0)
  const adherenceRate = computed(() => statistics.value?.adherence_rate || 0)
  const totalRecords = computed(() => statistics.value?.total_records || 0)
  
  /**
   * 获取用药记录列表
   */
  const fetchRecords = async (params?: MedicationRecordQuery) => {
    try {
      loading.value = true
      error.value = null
      
      if (params) {
        queryParams.value = { ...queryParams.value, ...params }
      }
      
      const response = await recordApi.getRecords(queryParams.value)
      
      if (response.success) {
        records.value = response.data.results || response.data
        
        // 更新分页信息
        if (response.data.count !== undefined) {
          pagination.value = {
            page: queryParams.value.page || 1,
            pageSize: queryParams.value.page_size || 20,
            total: response.data.count,
            totalPages: Math.ceil(response.data.count / (queryParams.value.page_size || 20))
          }
        }
      } else {
        throw new Error(response.message || '获取用药记录失败')
      }
    } catch (err: any) {
      console.error('获取用药记录失败:', err)
      error.value = err.message || '获取用药记录失败'
      records.value = []
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 获取用药记录详情
   */
  const fetchRecord = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await recordApi.getRecord(id)
      
      if (response.success) {
        currentRecord.value = response.data
      } else {
        throw new Error(response.message || '获取用药记录详情失败')
      }
    } catch (err: any) {
      console.error('获取用药记录详情失败:', err)
      error.value = err.message || '获取用药记录详情失败'
      currentRecord.value = null
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 创建用药记录
   */
  const createRecord = async (data: MedicationRecordForm) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await recordApi.createRecord(data)
      
      if (response.success) {
        // 添加到记录列表开头
        records.value.unshift(response.data)
        
        // 更新统计信息
        await fetchStatistics()
        
        return response.data
      } else {
        throw new Error(response.message || '创建用药记录失败')
      }
    } catch (err: any) {
      console.error('创建用药记录失败:', err)
      error.value = err.message || '创建用药记录失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 更新用药记录
   */
  const updateRecord = async (id: number, data: Partial<MedicationRecordForm>) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await recordApi.updateRecord(id, data)
      
      if (response.success) {
        // 更新记录列表中的对应项
        const index = records.value.findIndex(record => record.id === id)
        if (index !== -1) {
          records.value[index] = response.data
        }
        
        // 更新当前记录
        if (currentRecord.value?.id === id) {
          currentRecord.value = response.data
        }
        
        // 更新统计信息
        await fetchStatistics()
        
        return response.data
      } else {
        throw new Error(response.message || '更新用药记录失败')
      }
    } catch (err: any) {
      console.error('更新用药记录失败:', err)
      error.value = err.message || '更新用药记录失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 删除用药记录
   */
  const deleteRecord = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await recordApi.deleteRecord(id)
      
      if (response.success) {
        // 从记录列表中移除
        records.value = records.value.filter(record => record.id !== id)
        
        // 清空当前记录（如果是被删除的记录）
        if (currentRecord.value?.id === id) {
          currentRecord.value = null
        }
        
        // 更新统计信息
        await fetchStatistics()
        
        return true
      } else {
        throw new Error(response.message || '删除用药记录失败')
      }
    } catch (err: any) {
      console.error('删除用药记录失败:', err)
      error.value = err.message || '删除用药记录失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 获取统计信息
   */
  const fetchStatistics = async (params?: {
    start_date?: string
    end_date?: string
    medicine_id?: number
  }) => {
    try {
      const response = await recordApi.getStatistics(params)
      
      if (response.success) {
        statistics.value = response.data
      } else {
        throw new Error(response.message || '获取统计信息失败')
      }
    } catch (err: any) {
      console.error('获取统计信息失败:', err)
      statistics.value = null
    }
  }
  
  /**
   * 获取趋势数据
   */
  const fetchTrends = async () => {
    try {
      const response = await recordApi.getTrends()
      
      if (response.success) {
        trends.value = response.data
      } else {
        throw new Error(response.message || '获取趋势数据失败')
      }
    } catch (err: any) {
      console.error('获取趋势数据失败:', err)
      trends.value = []
    }
  }
  
  /**
   * 获取最近记录
   */
  const fetchRecentRecords = async (limit: number = 10) => {
    try {
      const response = await recordApi.getRecentRecords(limit)
      
      if (response.success) {
        recentRecords.value = response.data
      } else {
        throw new Error(response.message || '获取最近记录失败')
      }
    } catch (err: any) {
      console.error('获取最近记录失败:', err)
      recentRecords.value = []
    }
  }
  
  /**
   * 导出记录
   */
  const exportRecords = async (params?: {
    format?: string
    start_date?: string
    end_date?: string
  }) => {
    try {
      loading.value = true
      error.value = null
      
      const blob = await recordApi.exportRecords(params)
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `medication_records_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      return true
    } catch (err: any) {
      console.error('导出记录失败:', err)
      error.value = err.message || '导出记录失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 重置状态
   */
  const resetState = () => {
    records.value = []
    currentRecord.value = null
    statistics.value = null
    trends.value = []
    recentRecords.value = []
    loading.value = false
    error.value = null
    pagination.value = {
      page: 1,
      pageSize: 20,
      total: 0,
      totalPages: 0
    }
    queryParams.value = {}
  }
  
  /**
   * 设置查询参数
   */
  const setQueryParams = (params: MedicationRecordQuery) => {
    queryParams.value = { ...queryParams.value, ...params }
  }
  
  /**
   * 清空错误
   */
  const clearError = () => {
    error.value = null
  }
  
  return {
    // 状态
    records,
    currentRecord,
    statistics,
    trends,
    recentRecords,
    loading,
    error,
    pagination,
    queryParams,
    
    // 计算属性
    hasRecords,
    adherenceRate,
    totalRecords,
    
    // 方法
    fetchRecords,
    fetchRecord,
    createRecord,
    updateRecord,
    deleteRecord,
    fetchStatistics,
    fetchTrends,
    fetchRecentRecords,
    exportRecords,
    resetState,
    setQueryParams,
    clearError
  }
})