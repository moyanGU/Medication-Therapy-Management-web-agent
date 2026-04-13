import { api } from '@/utils/api'
import type { RequestConfig } from '@/utils/api'
import type {
  MedicineCreateData,
  MedicineUpdateData,
  MedicineListParams,
} from '@/types/medicine'

const isDebug = import.meta.env.MODE !== 'production'
const log = (...args: any[]) => {
  if (isDebug) console.log(...args)
}
const logError = (message: string, error?: unknown) => {
  if (isDebug && error !== undefined) {
    console.error(message, error)
    return
  }
  console.error(message)
}

/**
 * 药品管理API
 */
export const medicineApi = {
  /**
   * 获取药品列表
   */
  async getMedicines(params?: MedicineListParams) {
    log('🔵 [Medicine API] getMedicines params:', params)
    const res = await api.get('/medicines/', params)
    log('🟢 [Medicine API] getMedicines 响应:', res)
    return res
  },

  /**
   * 获取单个药品详情
   */
  async getMedicine(id: number) {
    log('🔵 [Medicine API] getMedicine id:', id)
    const res = await api.get(`/medicines/${id}/`)
    log('🟢 [Medicine API] getMedicine 响应:', res)
    return res
  },

  /**
   * 创建药品
   */
  async createMedicine(data: MedicineCreateData, config: RequestConfig = {}) {
    log('🔵 [Medicine API] createMedicine 开始调用', {
      url: '/medicines/',
      method: 'POST',
      originalData: data,
      timestamp: new Date().toISOString(),
    })

    // 智能处理 image_path 字段：如果为空则不发送，如果有值则发送
    const cleanData = { ...data }

    log(
      '🔵 [Medicine API] 原始数据包含 image_path:',
      'image_path' in data
    )
    log('🔵 [Medicine API] image_path 值:', (data as any).image_path)

    const imagePath = (cleanData as any).image_path

    // 如果 image_path 为空字符串、null 或 undefined，则删除该字段
    if (!imagePath || String(imagePath).trim() === '') {
      delete (cleanData as any).image_path
      log('🔵 [Medicine API] 删除空的 image_path 字段')
    } else {
      log('🔵 [Medicine API] 保留有效的 image_path 字段:', imagePath)
    }

    log('🔵 [Medicine API] 清理后的数据:', cleanData)
    log('🔵 [Medicine API] 发送的字段:', Object.keys(cleanData))
    log(
      '🔵 [Medicine API] 清理后包含 image_path:',
      'image_path' in cleanData
    )

    try {
      const res = await api.post('/medicines/', cleanData, config)
      log('🟢 [Medicine API] createMedicine 响应:', res)
      return res
    } catch (error) {
      logError('🔴 [Medicine API] createMedicine 请求异常', error)
      throw error
    }
  },

  /**
   * 更新药品信息
   */
  async updateMedicine(
    id: number,
    data: MedicineUpdateData,
    config: RequestConfig = {}
  ) {
    log('🔵 [Medicine API] updateMedicine id,data:', id, data)
    const res = await api.put(`/medicines/${id}/`, data, config)
    log('🟢 [Medicine API] updateMedicine 响应:', res)
    return res
  },

  /**
   * 部分更新药品信息
   */
  async patchMedicine(id: number, data: Partial<MedicineUpdateData>) {
    log('🔵 [Medicine API] patchMedicine id,data:', id, data)
    const res = await api.patch(`/medicines/${id}/`, data)
    log('🟢 [Medicine API] patchMedicine 响应:', res)
    return res
  },

  /**
   * 删除药品
   */
  async deleteMedicine(id: number) {
    log('🔵 [Medicine API] deleteMedicine id:', id)
    const res = await api.delete(`/medicines/${id}/`)
    log('🟢 [Medicine API] deleteMedicine 响应:', res)
    return res
  },

  /**
   * 更新药品数量
   */
  async updateQuantity(id: number, quantity: number) {
    log('🔵 [Medicine API] updateQuantity id,quantity:', id, quantity)
    const res = await api.post(`/medicines/${id}/update_quantity/`, {
      quantity,
    })
    log('🟢 [Medicine API] updateQuantity 响应:', res)
    return res
  },

  /**
   * 获取已过期的药品列表
   */
  async getExpiredMedicines() {
    log('🔵 [Medicine API] getExpiredMedicines')
    const res = await api.get('/medicines/expired/')
    log('🟢 [Medicine API] getExpiredMedicines 响应:', res)
    return res
  },

  /**
   * 获取即将过期的药品列表
   */
  async getExpiringSoonMedicines() {
    log('🔵 [Medicine API] getExpiringSoonMedicines')
    const res = await api.get('/medicines/expiring_soon/')
    log('🟢 [Medicine API] getExpiringSoonMedicines 响应:', res)
    return res
  },

  /**
   * 获取库存不足的药品列表
   */
  async getLowStockMedicines(threshold = 5) {
    log('🔵 [Medicine API] getLowStockMedicines threshold:', threshold)
    const res = await api.get('/medicines/low_stock/', {
      params: { threshold },
    })
    log('🟢 [Medicine API] getLowStockMedicines 响应:', res)
    return res
  },

  /**
   * 获取药品统计信息
   */
  async getStatistics() {
    log('🔵 [Medicine API] getStatistics')
    const res = await api.get('/medicines/statistics/')
    log('🟢 [Medicine API] getStatistics 响应:', res)
    return res
  },

  /**
   * 获取药品类型列表
   */
  async getMedicineTypes() {
    log('🔵 [Medicine API] getMedicineTypes')
    const res = await api.get('/medicines/types/')
    log('🟢 [Medicine API] getMedicineTypes 响应:', res)
    return res
  },
}
