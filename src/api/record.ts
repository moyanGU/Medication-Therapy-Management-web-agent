import { api } from '../utils/api'
import type {
  MedicationRecord,
  MedicationRecordForm,
  MedicationRecordStats,
  MedicationTrend,
  MedicationRecordQuery
} from '../types/record'

/**
 * 用药记录API接口
 */
export const recordApi = {
  /**
   * 获取用药记录列表
   */
  async getRecords(params?: MedicationRecordQuery) {
    console.log('获取用药记录列表:', params)
    const response = await api.get('/records/medication-records/', { params })
    console.log('用药记录列表响应:', response.data)
    return response
  },

  /**
   * 获取用药记录详情
   */
  async getRecord(id: number) {
    console.log('获取用药记录详情:', id)
    const response = await api.get(`/records/medication-records/${id}/`)
    console.log('用药记录详情响应:', response.data)
    return response
  },

  /**
   * 创建用药记录
   */
  async createRecord(data: MedicationRecordForm) {
    console.log('创建用药记录:', data)
    const response = await api.post('/records/medication-records/', data)
    console.log('创建用药记录完整响应:', response)
    console.log('创建用药记录响应数据:', response.data)
    console.log('响应数据类型:', typeof response.data)
    console.log('响应是否有success字段:', 'success' in response)
    return response
  },

  /**
   * 更新用药记录
   */
  async updateRecord(id: number, data: Partial<MedicationRecordForm>) {
    console.log('更新用药记录:', id, data)
    const response = await api.patch(`/records/medication-records/${id}/`, data)
    console.log('更新用药记录响应:', response.data)
    return response
  },

  /**
   * 删除用药记录
   */
  async deleteRecord(id: number) {
    console.log('删除用药记录:', id)
    const response = await api.delete(`/records/medication-records/${id}/`)
    console.log('删除用药记录响应:', response.data)
    return response
  },

  /**
   * 获取用药记录统计信息
   */
  async getStatistics(params?: {
    start_date?: string
    end_date?: string
    medicine?: string | number
  }) {
    console.log('获取用药记录统计:', params)
    const response = await api.get('/records/medication-records/statistics/', { params })
    console.log('用药记录统计响应:', response.data)
    return response
  },

  /**
   * 获取用药趋势数据
   */
  async getTrends(params?: {
    start_date?: string
    end_date?: string
    medicine?: string | number
  }) {
    console.log('获取用药趋势数据:', params)
    const response = await api.get('/records/medication-records/trends/', {
      params
    })
    console.log('用药趋势数据响应:', response.data)
    return response
  },

  /**
   * 获取最近的用药记录
   */
  async getRecentRecords(limit: number = 10) {
    console.log('获取最近用药记录:', limit)
    const response = await api.get('/records/medication-records/recent/', {
      params: { limit }
    })
    console.log('最近用药记录响应:', response.data)
    return response
  },

  /**
   * 获取今日用药种类（去重后的药品数）
   */
  async getTodayMedicineTypes(date?: string) {
    const params = date ? { date } : undefined
    console.log('获取今日用药种类:', params)
    const response = await api.get('/records/medication-records/today-medicine-types/', { params })
    console.log('今日用药种类响应:', response.data)
    return response
  },

  /**
   * 导出用药记录
   */
  async exportRecords(params?: {
    format?: string
    start_date?: string
    end_date?: string
  }) {
    console.log('导出用药记录:', params)
    const response = await api.get('/records/medication-records/export/', {
      params,
      responseType: 'blob'
    })
    console.log('导出用药记录响应:', response.data)
    return response.data
  }
}