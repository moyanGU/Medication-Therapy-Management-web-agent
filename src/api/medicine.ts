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
    return http.get('/medicines/api/medicines/', { params })
  },

  /**
   * 获取单个药品详情
   */
  getMedicine(id: number) {
    return http.get(`/medicines/api/medicines/${id}/`)
  },

  /**
   * 创建药品
   */
  createMedicine(data: MedicineCreateData) {
    return http.post('/medicines/api/medicines/', data)
  },

  /**
   * 更新药品信息
   */
  updateMedicine(id: number, data: MedicineUpdateData) {
    return http.put(`/medicines/api/medicines/${id}/`, data)
  },

  /**
   * 部分更新药品信息
   */
  patchMedicine(id: number, data: Partial<MedicineUpdateData>) {
    return http.patch(`/medicines/api/medicines/${id}/`, data)
  },

  /**
   * 删除药品
   */
  deleteMedicine(id: number) {
    return http.delete(`/medicines/api/medicines/${id}/`)
  },

  /**
   * 更新药品数量
   */
  updateQuantity(id: number, quantity: number) {
    return http.post(`/medicines/api/medicines/${id}/update_quantity/`, { quantity })
  },

  /**
   * 获取已过期的药品列表
   */
  getExpiredMedicines() {
    return http.get('/medicines/api/medicines/expired/')
  },

  /**
   * 获取即将过期的药品列表
   */
  getExpiringSoonMedicines() {
    return http.get('/medicines/api/medicines/expiring_soon/')
  },

  /**
   * 获取库存不足的药品列表
   */
  getLowStockMedicines(threshold = 5) {
    return http.get('/medicines/api/medicines/low_stock/', {
      params: { threshold }
    })
  },

  /**
   * 获取药品统计信息
   */
  getStatistics() {
    return http.get('/medicines/api/medicines/statistics/')
  },

  /**
   * 获取药品类型列表
   */
  getMedicineTypes() {
    return http.get('/medicines/api/medicines/types/')
  }
}