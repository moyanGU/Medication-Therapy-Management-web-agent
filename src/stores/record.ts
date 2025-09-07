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
  const adherenceRate = computed(() => statistics.value?.adherence_rate ?? 0)
  const totalRecords = computed(() => statistics.value?.total_records ?? 0)
  
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
      
      console.log('🔵 [Record Store] 获取记录列表参数:', queryParams.value)
      
      const response = await recordApi.getRecords(queryParams.value)
      
      if (!validateResponse(response, '获取记录列表')) {
        throw new Error('响应数据格式无效')
      }
      
      console.log('🔵 [Record Store] 记录列表响应:', response)
      
      if (response.success) {
        const data = response.data ?? {}
        console.log('🔵 [Record Store] 解析的data对象:', data)
        
        // 安全地访问results数组
        if (data && typeof data === 'object' && Array.isArray((data as any).results)) {
          records.value = (data as any).results
          console.log('🟢 [Record Store] 成功解析records数组，数量:', records.value.length)
        } else {
          console.warn('🟡 [Record Store] data.results不是数组，使用空数组')
          records.value = []
        }
        
        // 更新分页信息
        const pg = (data as any).pagination
        if (pg && typeof pg === 'object') {
          pagination.value = {
            page: Math.max(1, Number(queryParams.value.page ?? 1)),
            pageSize: Math.max(1, Number((queryParams.value as any).page_size ?? 20)),
            total: Math.max(0, Number(pg.count ?? 0)),
            totalPages: Math.max(1, Number(pg.total_pages ?? 1))
          }
          console.log('🟢 [Record Store] 分页信息更新:', pagination.value)
        } else {
          console.warn('🟡 [Record Store] 分页信息不可用')
        }
        
        console.log('🟢 [Record Store] 记录列表获取成功，数量:', records.value.length)
      } else {
        const errorMsg = (response as any).message || '获取用药记录失败'
        console.error('🔴 [Record Store] 获取记录列表失败:', errorMsg)
        throw new Error(errorMsg)
      }
    } catch (err: any) {
      error.value = err.message || '获取用药记录失败'
      console.error('🔴 [Record Store] 获取记录列表异常:', err)
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
      
      console.log('🔵 [Record Store] 获取记录详情，ID:', id)
      
      const response = await recordApi.getRecord(id)
      
      if (!validateResponse(response, '获取记录详情')) {
        throw new Error('响应数据格式无效')
      }
      
      console.log('🔵 [Record Store] 记录详情响应:', response)
      
      if (response.success) {
        currentRecord.value = response.data as MedicationRecord
        console.log('🟢 [Record Store] 记录详情获取成功:', currentRecord.value)
      } else {
        error.value = (response as any).message || '获取用药记录详情失败'
        console.error('🔴 [Record Store] 服务器返回失败:', response)
        throw new Error((response as any).message || '获取用药记录详情失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取用药记录详情失败'
      console.error('🔴 [Record Store] 获取用药记录详情异常:', err)
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
      
      console.log('🔵 [Record Store] 创建记录参数:', data)
      
      const response = await recordApi.createRecord(data)
      
      if (!validateResponse(response, '创建记录')) {
        throw new Error('响应数据格式无效')
      }
      
      console.log('🔵 [Record Store] 创建记录响应:', response)
      
      if (response.success) {
        console.log('🟢 [Record Store] 创建记录成功，准备更新records数组')
        console.log('🟢 [Record Store] 当前records数组长度:', records.value.length)
        console.log('🟢 [Record Store] 新记录数据:', response.data)
        
        // 添加到记录列表开头
        records.value.unshift(response.data as MedicationRecord)
        console.log('🟢 [Record Store] 更新后records数组长度:', records.value.length)
        
        // 更新统计信息
        await fetchStatistics()
        console.log('🟢 [Record Store] 统计信息已更新')
        
        return response.data
      } else {
        error.value = (response as any).message || '创建用药记录失败'
        console.error('🔴 [Record Store] 服务器返回失败:', response)
        throw new Error((response as any).message || '创建用药记录失败')
      }
    } catch (err: any) {
      error.value = err.message || '创建用药记录失败'
      console.error('🔴 [Record Store] 创建记录异常:', err)
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
      
      console.log('🔵 [Record Store] 更新记录，ID:', id, '数据:', data)
      
      const response = await recordApi.updateRecord(id, data)
      
      if (!validateResponse(response, '更新记录')) {
        throw new Error('响应数据格式无效')
      }
      
      console.log('🔵 [Record Store] 更新记录响应:', response)
      
      if (response.success) {
        // 更新记录列表中的对应项
        const index = records.value.findIndex(record => record.id === id)
        if (index !== -1) {
          records.value[index] = response.data as MedicationRecord
        }
        
        // 更新当前记录
        currentRecord.value = response.data as MedicationRecord
        
        // 更新统计信息
        await fetchStatistics()
        
        console.log('🟢 [Record Store] 记录更新成功')
        
        return currentRecord.value
      } else {
        error.value = (response as any).message || '更新用药记录失败'
        console.error('🔴 [Record Store] 服务器返回失败:', response)
        throw new Error((response as any).message || '更新用药记录失败')
      }
    } catch (err: any) {
      error.value = err.message || '更新用药记录失败'
      console.error('🔴 [Record Store] 更新记录异常:', err)
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
      
      console.log('🔵 [Record Store] 删除记录，ID:', id)
      
      const response = await recordApi.deleteRecord(id)
      
      if (!validateResponse(response, '删除记录')) {
        throw new Error('响应数据格式无效')
      }
      
      console.log('🔵 [Record Store] 删除记录响应:', response)
      
      if (response.success) {
        // 从记录列表中移除
        records.value = records.value.filter(record => record.id !== id)
        
        // 清空当前记录（如果是被删除的记录）
        if (currentRecord.value?.id === id) {
          currentRecord.value = null
        }
        
        // 更新统计信息
        await fetchStatistics()
        
        console.log('🟢 [Record Store] 记录删除成功')
        
        return true
      } else {
        error.value = (response as any).message || '删除用药记录失败'
        console.error('🔴 [Record Store] 服务器返回失败:', response)
        throw new Error(response.message || '删除用药记录失败')
      }
    } catch (err: any) {
      error.value = err.message || '删除用药记录失败'
      console.error('🔴 [Record Store] 删除记录异常:', err)
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
    medicine?: string | number
  }) => {
    try {
      loading.value = true
      error.value = null
      
      console.log('🔵 [Record Store] 获取统计信息参数:', params)
      
      const response = await recordApi.getStatistics(params)
      
      if (!validateResponse(response, '获取统计信息')) {
        throw new Error('响应数据格式无效')
      }
      
      console.log('🔵 [Record Store] 统计信息响应:', response)
      
      if (response.success) {
        statistics.value = response.data as MedicationRecordStats
        console.log('🟢 [Record Store] 统计信息获取成功:', statistics.value)
      } else {
        error.value = (response as any).message || '获取统计信息失败'
        console.error('🔴 [Record Store] 服务器返回失败:', response)
      }
    } catch (err: any) {
      error.value = err.message || '获取统计信息失败'
      console.error('🔴 [Record Store] 获取统计信息异常:', err)
      statistics.value = null
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 获取趋势数据
   */
  const fetchTrends = async (params?: {
    start_date?: string
    end_date?: string
    medicine?: string | number
  }) => {
    try {
      loading.value = true
      error.value = null
      
      console.log('🔵 [Record Store] 获取趋势数据参数:', params)
      
      const response = await recordApi.getTrends(params)
      
      if (!validateResponse(response, '获取趋势数据')) {
        throw new Error('响应数据格式无效')
      }
      
      console.log('🔵 [Record Store] 趋势数据响应:', response)
      
      if (response.success) {
        trends.value = Array.isArray(response.data) ? (response.data as MedicationTrend[]) : []
        console.log('🟢 [Record Store] 趋势数据获取成功，数量:', trends.value.length)
      } else {
        const errorMsg = (response as any).message || '获取趋势数据失败'
        console.error('🔴 [Record Store] 获取趋势数据失败:', errorMsg)
        throw new Error(errorMsg)
      }
    } catch (err: any) {
      error.value = err.message || '获取趋势数据失败'
      console.error('🔴 [Record Store] 获取趋势数据异常:', err)
      trends.value = []
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 获取最近记录
   */
  const fetchRecentRecords = async (limit: number = 10) => {
    try {
      loading.value = true
      error.value = null
      
      console.log('🔵 [Record Store] 获取最近记录，限制数量:', limit)
      
      const response = await recordApi.getRecentRecords(limit)
      
      if (!validateResponse(response, '获取最近记录')) {
        throw new Error('响应数据格式无效')
      }
      
      console.log('🔵 [Record Store] 最近记录响应:', response)
      
      if (response.success) {
        recentRecords.value = Array.isArray(response.data) ? (response.data as MedicationRecord[]) : []
        console.log('🟢 [Record Store] 最近记录获取成功，数量:', recentRecords.value.length)
      } else {
        const errorMsg = (response as any).message || '获取最近记录失败'
        console.error('🔴 [Record Store] 获取最近记录失败:', errorMsg)
        throw new Error(errorMsg)
      }
    } catch (err: any) {
      error.value = err.message || '获取最近记录失败'
      console.error('🔴 [Record Store] 获取最近记录异常:', err)
      recentRecords.value = []
    } finally {
      loading.value = false
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
      
      console.log('🔵 [Record Store] 导出记录参数:', params)
      
      const blob = await recordApi.exportRecords(params)
      
      console.log('🔵 [Record Store] 导出记录响应类型:', typeof blob)
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `medication_records_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      console.log('🟢 [Record Store] 记录导出成功')
      
      return true
    } catch (err: any) {
      error.value = err.message || '导出记录失败'
      console.error('🔴 [Record Store] 导出记录异常:', err)
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
  const setQueryParams = (params: Partial<MedicationRecordQuery>) => {
    queryParams.value = { ...queryParams.value, ...params }
  }
  
  /**
   * 清空错误信息
   */
  const clearError = () => {
    error.value = null
  }
  
  /**
   * 验证响应数据结构
   */
  const validateResponse = (response: any, methodName: string): boolean => {
    if (!response || typeof response !== 'object') {
      console.error(`🔴 [Record Store] ${methodName} 响应无效:`, response)
      return false
    }
    
    // ApiClient返回的数据形如: { success: boolean, data: any, message?: string }
    if (typeof (response as any).success !== 'boolean' || !('data' in response)) {
      console.error(`🔴 [Record Store] ${methodName} 响应数据结构不符合ApiResponse:`, response)
      return false
    }
    
    return true
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
    clearError,
    
    // 别名方法（向后兼容）
    fetchStats: fetchStatistics,
    stats: computed(() => statistics.value)
  }
})