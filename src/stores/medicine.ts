import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { medicineApi } from '@/api/medicine'
import type { Medicine, MedicineCreateData, MedicineUpdateData, MedicineListParams } from '@/types/medicine'

export const useMedicineStore = defineStore('medicine', () => {
  // 状态
  const medicines = ref<Medicine[]>([])
  const currentMedicine = ref<Medicine | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    current: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  })
  
  // 统计信息
  const statistics = ref({
    total_medicines: 0,
    expired_count: 0,
    expiring_soon_count: 0,
    low_stock_count: 0,
    prescription_count: 0,
    total_quantity: 0
  })
  
  // 计算属性
  const expiredMedicines = computed(() => 
    medicines.value.filter(medicine => medicine.is_expired)
  )
  
  const lowStockMedicines = computed(() => 
    medicines.value.filter(medicine => medicine.is_low_stock)
  )
  
  const prescriptionMedicines = computed(() => 
    medicines.value.filter(medicine => medicine.is_prescription)
  )
  
  // 获取药品列表
  const fetchMedicines = async (params?: MedicineListParams) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await medicineApi.getMedicines(params)
      
      if (response.data.success) {
        if (response.data.data.results) {
          // 分页数据
          console.log('🔵 [Medicine Store] 分页数据:', response.data.data.results)
          console.log('🔵 [Medicine Store] 第一个药品的image_path:', response.data.data.results[0]?.image_path)
          medicines.value = response.data.data.results
          pagination.value = {
            current: response.data.data.pagination.current_page,
            pageSize: response.data.data.pagination.page_size,
            total: response.data.data.pagination.count,
            totalPages: response.data.data.pagination.total_pages
          }
        } else {
          // 非分页数据
          console.log('🔵 [Medicine Store] 非分页数据:', response.data.data)
          medicines.value = response.data.data
        }
      } else {
        error.value = response.data.message || '获取药品列表失败'
      }
    } catch (err: any) {
      error.value = err.message || '获取药品列表失败'
      console.error('获取药品列表失败:', err)
    } finally {
      loading.value = false
    }
  }
  
  // 获取单个药品详情
  const fetchMedicine = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await medicineApi.getMedicine(id)
      
      if (response.data.success) {
        currentMedicine.value = response.data.data
      } else {
        error.value = response.data.message || '获取药品详情失败'
      }
    } catch (err: any) {
      error.value = err.message || '获取药品详情失败'
      console.error('获取药品详情失败:', err)
    } finally {
      loading.value = false
    }
  }
  
  // 创建药品
  const createMedicine = async (data: MedicineCreateData) => {
    console.log('🔵 [Medicine Store] createMedicine 开始执行', {
      data,
      timestamp: new Date().toISOString()
    })
    
    try {
      loading.value = true
      error.value = null
      
      console.log('🔵 [Medicine Store] 准备调用 medicineApi.createMedicine', {
        apiData: data
      })
      
      const response = await medicineApi.createMedicine(data)
      
      console.log('🔵 [Medicine Store] medicineApi.createMedicine 响应', {
        response: response,
        responseData: response.data,
        success: response.data?.success,
        timestamp: new Date().toISOString()
      })
      
      if (response.data.success) {
        // 添加到列表中
        medicines.value.unshift(response.data.data)
        console.log('🟢 [Medicine Store] 药品创建成功', {
          newMedicine: response.data.data,
          totalMedicines: medicines.value.length
        })
        return response.data.data
      } else {
        error.value = response.data.message || '创建药品失败'
        console.error('🔴 [Medicine Store] 服务器返回失败', {
          message: response.data.message,
          responseData: response.data
        })
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || '创建药品失败'
      console.error('🔴 [Medicine Store] 创建药品异常', {
        error: err,
        message: err.message,
        stack: err.stack,
        response: err.response,
        timestamp: new Date().toISOString()
      })
      throw err
    } finally {
      loading.value = false
      console.log('🔵 [Medicine Store] createMedicine 执行完成', {
        loading: loading.value,
        timestamp: new Date().toISOString()
      })
    }
  }
  
  // 更新药品
  const updateMedicine = async (id: number, data: MedicineUpdateData) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await medicineApi.updateMedicine(id, data)
      
      if (response.data.success) {
        // 更新列表中的药品
        const index = medicines.value.findIndex(m => m.id === id)
        if (index !== -1) {
          medicines.value[index] = response.data.data
        }
        
        // 更新当前药品
        if (currentMedicine.value?.id === id) {
          currentMedicine.value = response.data.data
        }
        
        return response.data.data
      } else {
        error.value = response.data.message || '更新药品失败'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || '更新药品失败'
      console.error('更新药品失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 删除药品
  const deleteMedicine = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await medicineApi.deleteMedicine(id)
      
      if (response.data.success) {
        // 从列表中移除
        medicines.value = medicines.value.filter(m => m.id !== id)
        
        // 清除当前药品
        if (currentMedicine.value?.id === id) {
          currentMedicine.value = null
        }
        
        return true
      } else {
        error.value = response.data.message || '删除药品失败'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || '删除药品失败'
      console.error('删除药品失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 更新药品数量
  const updateMedicineQuantity = async (id: number, quantity: number) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await medicineApi.updateQuantity(id, quantity)
      
      if (response.data.success) {
        // 更新列表中的药品
        const index = medicines.value.findIndex(m => m.id === id)
        if (index !== -1) {
          medicines.value[index] = response.data.data
        }
        
        // 更新当前药品
        if (currentMedicine.value?.id === id) {
          currentMedicine.value = response.data.data
        }
        
        return response.data.data
      } else {
        error.value = response.data.message || '更新数量失败'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || '更新数量失败'
      console.error('更新数量失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 获取过期药品
  const fetchExpiredMedicines = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await medicineApi.getExpiredMedicines()
      
      if (response.data.success) {
        return response.data.data
      } else {
        error.value = response.data.message || '获取过期药品失败'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || '获取过期药品失败'
      console.error('获取过期药品失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 获取库存不足药品
  const fetchLowStockMedicines = async (threshold = 5) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await medicineApi.getLowStockMedicines(threshold)
      
      if (response.data.success) {
        return response.data.data
      } else {
        error.value = response.data.message || '获取库存不足药品失败'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || '获取库存不足药品失败'
      console.error('获取库存不足药品失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 获取统计信息
  const fetchStatistics = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await medicineApi.getStatistics()
      
      if (response.data.success) {
        statistics.value = response.data.data
        return response.data.data
      } else {
        error.value = response.data.message || '获取统计信息失败'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || '获取统计信息失败'
      console.error('获取统计信息失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 清除错误
  const clearError = () => {
    error.value = null
  }
  
  // 重置状态
  const reset = () => {
    medicines.value = []
    currentMedicine.value = null
    loading.value = false
    error.value = null
    pagination.value = {
      current: 1,
      pageSize: 20,
      total: 0,
      totalPages: 0
    }
  }
  
  return {
    // 状态
    medicines,
    currentMedicine,
    loading,
    error,
    pagination,
    statistics,
    
    // 计算属性
    expiredMedicines,
    lowStockMedicines,
    prescriptionMedicines,
    
    // 方法
    fetchMedicines,
    fetchMedicine,
    createMedicine,
    updateMedicine,
    deleteMedicine,
    updateMedicineQuantity,
    fetchExpiredMedicines,
    fetchLowStockMedicines,
    fetchStatistics,
    clearError,
    reset
  }
})