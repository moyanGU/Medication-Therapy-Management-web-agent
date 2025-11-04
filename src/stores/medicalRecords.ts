import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiClient } from '@/utils/api'

const apiClient = new ApiClient()
import type {
  MedicalRecord,
  MedicalRecordCreate,
  MedicalRecordUpdate,
  MedicalRecordStatistics
} from '@/types/medicalRecord'

const BASE_PATH = '/medical-records/records/'

// 归一化后的统计数据类型：在后端原始统计结构基础上，补充前端展示所需的字段
type NormalizedMedicalRecordStatistics = MedicalRecordStatistics & {
  totalRecords: number
  monthlyRecords: number
  totalCost: number
  avgSatisfaction: number
}

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
  
  // 统计数据（包含后端字段与前端展示需要的归一化字段）
  const statistics = ref<NormalizedMedicalRecordStatistics>({
    // 后端字段（snake_case）
    total_visits: 0,
    recent_visits: 0,
    total_cost: 0,
    average_cost: 0,
    follow_up_due: 0,
    monthly_visits: [],
    department_distribution: [],
    cost_trend: [],

    // 前端展示字段（camelCase，页面直接使用）
    totalRecords: 0,
    monthlyRecords: 0,
    totalCost: 0,
    avgSatisfaction: 0
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
      
      const queryParams: Record<string, any> = {
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
        ...searchParams.value,
        ...params
      }
      // 规范化查询键名：camelCase -> snake_case（与后端 FilterSet 字段一致）
      if (queryParams.dateFrom) {
        queryParams.visit_date_from = queryParams.dateFrom
        delete queryParams.dateFrom
      }
      if (queryParams.dateTo) {
        queryParams.visit_date_to = queryParams.dateTo
        delete queryParams.dateTo
      }
      if (queryParams.visitType) {
        queryParams.visit_type = queryParams.visitType
        delete queryParams.visitType
      }
      if (queryParams.keyword) {
        queryParams.search = queryParams.keyword
        delete queryParams.keyword
      }
      // 移除空值
      Object.keys(queryParams).forEach(k => {
        if (queryParams[k] === '' || queryParams[k] === undefined || queryParams[k] === null) {
          delete queryParams[k]
        }
      })
      
      console.log('[medicalRecords] fetchRecords params:', queryParams)
      const response = await apiClient.get(BASE_PATH, { params: queryParams })
      
      if (response.success) {
        const list = response.data?.results ?? []
        // 兼容新的分页结构(data.pagination.count)与旧结构(data.count)
        const count = response.data?.pagination?.count ?? response.data?.count ?? 0
        records.value = list
        
        // 更新分页信息（优先采用服务端返回的分页信息）
        const serverPg = response.data?.pagination
        const pageSize = Number(serverPg?.page_size ?? pagination.value.pageSize)
        pagination.value.pageSize = pageSize
        pagination.value.total = Number(count)
        pagination.value.totalPages = Number(serverPg?.total_pages ?? Math.ceil(Number(count) / pageSize))
        console.log('[medicalRecords] fetchRecords success:', {
          size: list.length,
          total: pagination.value.total,
          pageSize: pagination.value.pageSize,
          totalPages: pagination.value.totalPages
        })
      } else {
        throw new Error(response.message || '获取病历列表失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取病历列表失败'
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
      const response = await apiClient.get(`${BASE_PATH}${id}/`)
      
      if (response.success) {
        currentRecord.value = response.data
        return response.data
      } else {
        throw new Error(response.message || '获取病历详情失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取病历详情失败'
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
      const response = await apiClient.post(BASE_PATH, recordData)
      
      if (response.success) {
        // 重新获取列表
        await fetchRecords()
        return response.data
      } else {
        throw new Error(response.message || '创建病历记录失败')
      }
    } catch (err: any) {
      error.value = err.message || '创建病历记录失败'
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
      const response = await apiClient.put(`${BASE_PATH}${id}/`, recordData)
      
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
      error.value = err.message || '更新病历记录失败'
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
      const response = await apiClient.delete(`${BASE_PATH}${id}/`)
      
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
      error.value = err.message || '删除病历记录失败'
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
      const response = await apiClient.get(`${BASE_PATH}categories/`)
      
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
      const statsParams: Record<string, any> = { ...params }

      // 统一参数命名与格式（后端需要 snake_case 与 YYYY-MM-DD）
      if (statsParams.dateFrom) {
        statsParams.date_from = statsParams.dateFrom
        delete statsParams.dateFrom
      }
      if (statsParams.dateTo) {
        statsParams.date_to = statsParams.dateTo
        delete statsParams.dateTo
      }
      if (statsParams.visitType) {
        statsParams.visit_type = statsParams.visitType
        delete statsParams.visitType
      }

      // 将日期对象或ISO字符串格式化为 YYYY-MM-DD，避免后端解析错误导致400
      const toYMD = (input: any) => {
        try {
          const d = input instanceof Date ? input : new Date(input)
          if (Number.isNaN(d.getTime())) return undefined
          const y = d.getFullYear()
          const m = String(d.getMonth() + 1).padStart(2, '0')
          const day = String(d.getDate()).padStart(2, '0')
          return `${y}-${m}-${day}`
        } catch {
          return undefined
        }
      }
      if (statsParams.date_from) statsParams.date_from = toYMD(statsParams.date_from)
      if (statsParams.date_to) statsParams.date_to = toYMD(statsParams.date_to)

      console.log('[medicalRecords] fetchStatistics final params:', statsParams)
      const response = await apiClient.get(`${BASE_PATH}statistics/`, {
        params: statsParams
      })
      console.log('[medicalRecords] fetchStatistics response:', response)
      
      if (response.success) {
        const s: any = response.data || {}
        // 处理 monthly_visits 数组，取最近一个月的计数作为回退
        const monthlyArr = Array.isArray(s.monthly_visits)
          ? s.monthly_visits
          : (Array.isArray(s.monthlyVisits) ? s.monthlyVisits : [])
        const lastMonthCount = monthlyArr.length
          ? Number(monthlyArr[monthlyArr.length - 1]?.count ?? 0)
          : 0

        // 规范化键名映射，确保与页面使用的字段一致
        const normalized: NormalizedMedicalRecordStatistics = {
          // 页面需要的四个核心指标
          totalRecords: Number(
            s.total_visits ?? s.total_records ?? s.total_records_count ?? 0
          ),
          monthlyRecords: Number(
            s.recent_visits ?? s.monthly_records ?? lastMonthCount
          ),
          totalCost: Number(s.total_cost ?? s.totalCost ?? 0),
          avgSatisfaction: Number(
            s.average_satisfaction ?? s.avg_satisfaction ?? s.avg_effectiveness ?? 0
          ),
          
          // 保留原始返回，供其他页面或图表使用
          ...s
        }
        statistics.value = normalized
        console.log('[medicalRecords] normalized statistics:', statistics.value)
      }
    } catch (err: any) {
      console.error('获取统计信息失败:', err)
    }
  }
  
  // 获取最近就诊记录
  const fetchRecentRecords = async (days: number = 30) => {
    try {
      console.log('[medicalRecords] fetchRecentRecords days=', days)
      const response = await apiClient.get(`${BASE_PATH}recent/`, {
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
      const response = await apiClient.get(`${BASE_PATH}follow_up_due/`)
      
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