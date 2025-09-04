import { http } from '@/utils/http'
import type { Medicine, MedicineCreateData, MedicineUpdateData, MedicineListParams } from '@/types/medicine'

/**
 * 药品管理API
 */
export const medicineApi = {
  /**
   * 获取药品列表
   */
  getMedicines(params?: MedicineListParams) {
    return http.get('/api/medicines/', { params })
  },

  /**
   * 获取单个药品详情
   */
  getMedicine(id: number) {
    return http.get(`/api/medicines/${id}/`)
  },

  /**
   * 创建药品
   */
  createMedicine(data: MedicineCreateData) {
    console.log('🔵 [Medicine API] createMedicine 开始调用', {
      url: '/api/medicines/',
      method: 'POST',
      originalData: data,
      timestamp: new Date().toISOString()
    })
    
    // 智能处理image_url字段：如果为空则不发送，如果有值则发送
    const cleanData = { ...data }
    
    console.log('🔵 [Medicine API] 原始数据包含image_url:', 'image_url' in data)
    console.log('🔵 [Medicine API] image_url值:', data.image_url)
    
    // 如果image_url为空字符串、null或undefined，则删除该字段
    if (!cleanData.image_url || cleanData.image_url.trim() === '') {
      delete cleanData.image_url
      console.log('🔵 [Medicine API] 删除空的image_url字段')
    } else {
      console.log('🔵 [Medicine API] 保留有效的image_url字段:', cleanData.image_url)
    }
    
    console.log('🔵 [Medicine API] 清理后的数据:', cleanData)
    console.log('🔵 [Medicine API] 发送的字段:', Object.keys(cleanData))
    console.log('🔵 [Medicine API] 清理后包含image_url:', 'image_url' in cleanData)
    
    const request = http.post('/api/medicines/', cleanData)
    
    // 添加请求拦截日志
    request.then(response => {
      console.log('🟢 [Medicine API] createMedicine 请求成功', {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
        data: response.data,
        timestamp: new Date().toISOString()
      })
      return response
    }).catch(error => {
      console.error('🔴 [Medicine API] createMedicine 请求失败', {
        error: error,
        message: error.message,
        response: error.response,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        timestamp: new Date().toISOString()
      })
      throw error
    })
    
    return request
  },

  /**
   * 更新药品信息
   */
  updateMedicine(id: number, data: MedicineUpdateData) {
    return http.put(`/api/medicines/${id}/`, data)
  },

  /**
   * 部分更新药品信息
   */
  patchMedicine(id: number, data: Partial<MedicineUpdateData>) {
    return http.patch(`/api/medicines/${id}/`, data)
  },

  /**
   * 删除药品
   */
  deleteMedicine(id: number) {
    return http.delete(`/api/medicines/${id}/`)
  },

  /**
   * 更新药品数量
   */
  updateQuantity(id: number, quantity: number) {
    return http.post(`/api/medicines/${id}/update_quantity/`, { quantity })
  },

  /**
   * 获取已过期的药品列表
   */
  getExpiredMedicines() {
    return http.get('/api/medicines/expired/')
  },

  /**
   * 获取即将过期的药品列表
   */
  getExpiringSoonMedicines() {
    return http.get('/api/medicines/expiring_soon/')
  },

  /**
   * 获取库存不足的药品列表
   */
  getLowStockMedicines(threshold = 5) {
    return http.get('/api/medicines/low_stock/', {
      params: { threshold }
    })
  },

  /**
   * 获取药品统计信息
   */
  getStatistics() {
    return http.get('/api/medicines/statistics/')
  },

  /**
   * 获取药品类型列表
   */
  getMedicineTypes() {
    return http.get('/api/medicines/types/')
  }
}