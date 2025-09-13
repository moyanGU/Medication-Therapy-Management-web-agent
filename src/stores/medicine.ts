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
      console.log('🔵 [Medicine Store] fetchMedicines 响应:', response)
      
      if (response.success) {
        // API工具已处理双重data结构，直接使用response.data
        const actualData = response.data
        
        // 判断是否为分页数据结构
        const isPaginated = actualData && Array.isArray(actualData.results)
        
        if (isPaginated) {
          const results: Medicine[] = actualData.results ?? []
          medicines.value = results
          const firstImagePath = results[0]?.image_path
          console.log('🔵 [Medicine Store] 分页数据 results.length:', results.length)
          console.log('🔵 [Medicine Store] 第一个药品的 image_path:', firstImagePath)
          
          // 兼容不同字段命名
          const currentPage = actualData.current_page ?? actualData.page ?? 1
          const pageSize = actualData.page_size ?? actualData.pageSize ?? results.length
          const total = actualData.total ?? actualData.count ?? results.length
          const totalPages = actualData.total_pages ?? (
            pageSize > 0 ? Math.max(1, Math.ceil(total / pageSize)) : 1
          )
          
          pagination.value = {
            current: currentPage,
            pageSize,
            total,
            totalPages
          }
        } else {
          // 非分页：后端可能直接返回数组，或者返回 { items: [], medicines: [] }
          let list: any = []
          if (Array.isArray(actualData)) {
            list = actualData
          } else {
            list = actualData?.medicines ?? actualData?.items ?? []
          }
          if (!Array.isArray(list)) list = []
          medicines.value = list
          console.log('🔵 [Medicine Store] 非分页数据 length:', list.length)
          // 非分页时，重置分页为单页
          pagination.value = {
            current: 1,
            pageSize: Math.max(1, Number((list?.length ?? 20))),
            total: Math.max(0, Number((list?.length ?? 0))),
            totalPages: 1
          }
        }
      } else {
        error.value = response.message || '获取药品列表失败'
        console.error('🔴 [Medicine Store] 服务器返回失败', { message: error.value })
        // 向上抛出错误，供调用方处理
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = err.message || '获取药品列表失败'
      console.error('获取药品列表失败:', err)
      // 继续向上抛出，避免调用方误判成功
      throw err
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
      
      if (response.success) {
        currentMedicine.value = response.data
      } else {
        error.value = response.message || '获取药品详情失败'
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
        success: response.success,
        timestamp: new Date().toISOString()
      })
      
      if (response.success) {
        // 添加到列表中
        medicines.value.unshift(response.data)
        console.log('🟢 [Medicine Store] 药品创建成功', {
          newMedicine: response.data,
          totalMedicines: medicines.value.length
        })
        return response.data
      } else {
        error.value = response.message || '创建药品失败'
        console.error('🔴 [Medicine Store] 服务器返回失败', {
          message: response.message,
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
      
      if (response.success) {
        // 更新列表中的药品
        const index = medicines.value.findIndex(m => m.id === id)
        if (index !== -1) {
          medicines.value[index] = response.data
        }
        
        // 更新当前药品
        if (currentMedicine.value?.id === id) {
          currentMedicine.value = response.data
        }
        
        return response.data
      } else {
        error.value = response.message || '更新药品失败'
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
      
      if (response.success) {
        // 从列表中移除
        medicines.value = medicines.value.filter(m => m.id !== id)
        
        // 清除当前药品
        if (currentMedicine.value?.id === id) {
          currentMedicine.value = null
        }
        
        return true
      } else {
        error.value = response.message || '删除药品失败'
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
      
      if (response.success) {
        // 更新列表中的药品
        const index = medicines.value.findIndex(m => m.id === id)
        if (index !== -1) {
          medicines.value[index] = response.data
        }
        
        // 更新当前药品
        if (currentMedicine.value?.id === id) {
          currentMedicine.value = response.data
        }
        
        return response.data
      } else {
        error.value = response.message || '更新数量失败'
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
      
      if (response.success) {
        return response.data
      } else {
        error.value = response.message || '获取过期药品失败'
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
      
      if (response.success) {
        return response.data
      } else {
        error.value = response.message || '获取库存不足药品失败'
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
      
      if (response.success) {
        statistics.value = response.data
        return response.data
      } else {
        error.value = response.message || '获取统计信息失败'
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