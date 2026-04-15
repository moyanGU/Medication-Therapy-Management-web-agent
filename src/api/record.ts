import { api } from '../utils/api'
import type {
  MedicationAdherenceSummary,
  MedicationRecordForm,
  MedicationRecordQuery,
} from '../types/record'

/**
 * 用药记录API接口
 */
const isDebug = import.meta.env.MODE !== 'production'
const log = (...args: any[]) => {
  if (isDebug) console.log(...args)
}

export const recordApi = {
  /**
   * 获取用药记录列表
   */
  async getRecords(params?: MedicationRecordQuery) {
    log('获取用药记录列表:', params)
    const response = await api.get('/records/medication-records/', params)
    log('用药记录列表响应:', response.data)
    return response
  },

  /**
   * 获取用药记录详情
   */
  async getRecord(id: number) {
    log('获取用药记录详情:', id)
    const response = await api.get(`/records/medication-records/${id}/`)
    log('用药记录详情响应:', response.data)
    return response
  },

  /**
   * 创建用药记录
   */
  async createRecord(data: MedicationRecordForm) {
    log('创建用药记录:', data)
    const response = await api.post('/records/medication-records/', data)
    log('创建用药记录完整响应:', response)
    return response
  },

  /**
   * 更新用药记录
   */
  async updateRecord(id: number, data: Partial<MedicationRecordForm>) {
    log('更新用药记录:', id, data)
    const response = await api.patch(`/records/medication-records/${id}/`, data)
    log('更新用药记录响应:', response.data)
    return response
  },

  /**
   * 删除用药记录
   */
  async deleteRecord(id: number) {
    log('删除用药记录:', id)
    const response = await api.delete(`/records/medication-records/${id}/`)
    log('删除用药记录响应:', response.data)
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
    log('获取用药记录统计:', params)
    const response = await api.get('/records/medication-records/statistics/', {
      params,
    })
    log('用药记录统计响应:', response.data)
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
    log('获取用药趋势数据:', params)
    const response = await api.get('/records/medication-records/trends/', params)
    log('用药趋势数据响应:', response.data)
    return response
  },

  /**
   * 获取依从性聚合数据
   */
  async getAdherence(params?: {
    start_date?: string
    end_date?: string
    medicine_id?: string | number
    days?: number
  }) {
    log('获取依从性聚合数据:', params)
    const response = await api.get<MedicationAdherenceSummary>(
      '/records/medication-records/adherence/',
      params
    )
    log('依从性聚合数据响应:', response.data)
    return response
  },

  /**
   * 获取最近的用药记录
   */
  async getRecentRecords(limit: number = 10) {
    log('获取最近用药记录:', limit)
    const response = await api.get('/records/medication-records/recent/', {
      params: { limit },
    })
    log('最近用药记录响应:', response.data)
    return response
  },

  /**
   * 获取今日用药种类（去重后的药品数）
   */
  async getTodayMedicineTypes(date?: string) {
    const params = date ? { date } : undefined
    log('获取今日用药种类:', params)
    const response = await api.get(
      '/records/medication-records/today-medicine-types/',
      params
    )
    log('今日用药种类响应:', response.data)
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
    log('导出用药记录:', params)
    const response = await api.get(
      '/records/medication-records/export/',
      params,
      { responseType: 'blob' }
    )
    log('导出用药记录响应:', response.data)
    return response.data
  },
}
