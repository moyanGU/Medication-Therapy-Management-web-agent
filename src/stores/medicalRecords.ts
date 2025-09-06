import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiClient } from '@/utils/api'

const apiClient = new ApiClient()
import type { MedicalRecord, MedicalRecordCreate, MedicalRecordUpdate } from '@/types/medicalRecord'

export const useMedicalRecordStore = defineStore('medicalRecord', () => {
  // 状态
  const records = ref<MedicalRecord[]>([])
  const currentRecord = ref<MedicalRecord | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  })
  
  // 搜索和筛选状态
  const searchParams = ref({
    keyword: '',
    dateFrom: '',
    dateTo: '',
    hospital: '',
    department: '',
    doctor: '',
    diagnosis: '',
    visitType: '',
    status: '',
    urgency: ''
  })
  
  // 分类统计数据
  const categories = ref({
    departments: [],
    hospitals: [],
    doctors: [],
    diagnoses: [],
    visitTypes: [],
    urgencyLevels: []
  })
  
  // 统计数据
  const statistics = ref({
    totalVisits: 0,
    recentVisits: 0,
    totalCost: 0,
    averageCost: 0,
    followUpDue: 0,
    monthlyVisits: [],
    departmentDistribution: [],
    costTrend: []
  })
  
  // 计算属性
  const hasRecords = computed(() => records.value.length > 0)
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => !!error.value)
  
  // 获取病历列表
  const fetchRecords = async (params: any = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const queryParams = {
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
        ...searchParams.value,
        ...params
      }
      
      // 移除空值参数
      Object.keys(queryParams).forEach(key => {
        if (!queryParams[key]) {
          delete queryParams[key]
        }
      })
      
      console.log('[medicalRecords] fetchRecords params:', queryParams)
      const response = await apiClient.get('/records/medication-records/', {
        params: queryParams
      })
      
      if (response.success) {
        // 按标准结构解包 { success, data: { results: [], count: number } }
        const list = response.data?.results || []
        const count = response.data?.count ?? 0
        records.value = list
        
        // 更新分页信息
        pagination.value.total = count
        pagination.value.totalPages = Math.ceil(count / pagination.value.pageSize)
        console.log('[medicalRecords] fetchRecords success: size=', list.length, 'total=', count)
      } else {
        throw new Error(response.message || '获取病历列表失败')
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || '获取病历列表失败'
      console.error('获取病历列表失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 获取单个病历详情
  const fetchRecord = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      console.log('[medicalRecords] fetchRecord id=', id)
      const response = await apiClient.get(`/records/medication-records/${id}/`)
      
      if (response.success) {
        currentRecord.value = response.data
        return response.data
      } else {
        throw new Error(response.message || '获取病历详情失败')
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || '获取病历详情失败'
      console.error('获取病历详情失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 创建病历记录
  const createRecord = async (recordData: MedicalRecordCreate) => {
    try {
      loading.value = true
      error.value = null
      
      console.log('[medicalRecords] createRecord payload:', recordData)
      const response = await apiClient.post('/records/medication-records/', recordData)
      
      if (response.success) {
        // 重新获取列表
        await fetchRecords()
        return response.data
      } else {
        throw new Error(response.message || '创建病历记录失败')
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || '创建病历记录失败'
      console.error('创建病历记录失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 更新病历记录
  const updateRecord = async (id: number, recordData: MedicalRecordUpdate) => {
    try {
      loading.value = true
      error.value = null
      
      console.log('[medicalRecords] updateRecord id=', id, 'payload:', recordData)
      const response = await apiClient.put(`/records/medication-records/${id}/`, recordData)
      
      if (response.success) {
        // 更新当前记录
        if (currentRecord.value && currentRecord.value.id === id) {
          currentRecord.value = response.data
        }
        
        // 更新列表中的记录
        const index = records.value.findIndex(record => record.id === id)
        if (index !== -1) {
          records.value[index] = response.data as any
        }
        
        return response.data
      } else {
        throw new Error(response.message || '更新病历记录失败')
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || '更新病历记录失败'
      console.error('更新病历记录失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 删除病历记录
  const deleteRecord = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      console.log('[medicalRecords] deleteRecord id=', id)
      const response = await apiClient.delete(`/records/medication-records/${id}/`)
      
      if (response.success) {
        // 从列表中移除
        records.value = records.value.filter(record => record.id !== id)
        
        // 清除当前记录
        if (currentRecord.value && currentRecord.value.id === id) {
          currentRecord.value = null
        }
        
        // 更新分页信息
        pagination.value.total = Math.max(0, pagination.value.total - 1)
        pagination.value.totalPages = Math.ceil(pagination.value.total / pagination.value.pageSize)
        
        return true
      } else {
        throw new Error(response.message || '删除病历记录失败')
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || err.message || '删除病历记录失败'
      console.error('删除病历记录失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 搜索病历记录
  const searchRecords = async (searchData: any) => {
    searchParams.value = { ...searchParams.value, ...searchData }
    pagination.value.page = 1 // 重置到第一页
    await fetchRecords()
  }
  
  // 重置搜索条件
  const resetSearch = async () => {
    searchParams.value = {
      keyword: '',
      dateFrom: '',
      dateTo: '',
      hospital: '',
      department: '',
      doctor: '',
      diagnosis: '',
      visitType: '',
      status: '',
      urgency: ''
    }
    pagination.value.page = 1
    await fetchRecords()
  }
  
  // 获取分类信息
  const fetchCategories = async () => {
    try {
      console.log('[medicalRecords] fetchCategories')
      const response = await apiClient.get('/records/medication-records/categories/')
      
      if (response.success) {
        categories.value = response.data
      }
    } catch (err: any) {
      console.error('获取分类信息失败:', err)
    }
  }
  
  // 获取统计信息
  const fetchStatistics = async (params: any = {}) => {
    try {
      console.log('[medicalRecords] fetchStatistics params:', params)
      const response = await apiClient.get('/records/medication-records/statistics/', {
        params
      })
      
      if (response.success) {
        statistics.value = response.data
      }
    } catch (err: any) {
      console.error('获取统计信息失败:', err)
    }
  }
  
  // 获取最近就诊记录
  const fetchRecentRecords = async (days: number = 30) => {
    try {
      console.log('[medicalRecords] fetchRecentRecords days=', days)
      const response = await apiClient.get('/records/medication-records/recent/', {
        params: { days }
      })
      
      if (response.success) {
        return response.data
      }
    } catch (err: any) {
      console.error('获取最近就诊记录失败:', err)
    }
  }
  
  // 获取复诊提醒
  const fetchFollowUpDue = async () => {
    try {
      console.log('[medicalRecords] fetchFollowUpDue')
      const response = await apiClient.get('/records/medication-records/follow_up_due/')
      
      if (response.success) {
        return response.data
      }
    } catch (err: any) {
      console.error('获取复诊提醒失败:', err)
    }
  }
  
  // 设置分页
  const setPagination = (page: number, pageSize?: number) => {
    pagination.value.page = page
    if (pageSize) {
      pagination.value.pageSize = pageSize
    }
  }
  
  // 清除错误
  const clearError = () => {
    error.value = null
  }
  
  // 重置状态
  const reset = () => {
    records.value = []
    currentRecord.value = null
    loading.value = false
    error.value = null
    pagination.value = {
      page: 1,
      pageSize: 20,
      total: 0,
      totalPages: 0
    }
    searchParams.value = {
      keyword: '',
      dateFrom: '',
      dateTo: '',
      hospital: '',
      department: '',
      doctor: '',
      diagnosis: '',
      visitType: '',
      status: '',
      urgency: ''
    }
  }
  
  return {
    // 状态
    records,
    currentRecord,
    loading,
    error,
    pagination,
    searchParams,
    categories,
    statistics,
    
    // 计算属性
    hasRecords,
    isLoading,
    hasError,
    
    // 方法
    fetchRecords,
    fetchRecord,
    createRecord,
    updateRecord,
    deleteRecord,
    searchRecords,
    resetSearch,
    fetchCategories,
    fetchStatistics,
    fetchRecentRecords,
    fetchFollowUpDue,
    setPagination,
    clearError,
    reset
  }
})