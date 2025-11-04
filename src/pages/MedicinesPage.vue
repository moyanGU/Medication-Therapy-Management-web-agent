<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">药品管理</h1>
            <p class="text-gray-600 mt-1">管理您的药品信息和库存</p>
          </div>
          <button
            @click="showAddDialog = true"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            添加药品
          </button>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="bg-white rounded-lg shadow mb-6 p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">搜索药品</label>
            <div class="flex gap-2">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="输入药品名称或拼音首字母"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                @keyup.enter="handleSearch"
              />
              <button
                @click="handleSearch"
                :disabled="loading"
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ loading ? '搜索中...' : '搜索' }}
              </button>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">状态筛选</label>
            <select 
              v-model="filters.status"
              @change="handleFilter"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">全部状态</option>
              <option value="normal">正常</option>
              <option value="low-stock">库存不足</option>
              <option value="expired">即将过期</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">排序方式</label>
            <select 
              v-model="filters.sortBy"
              @change="handleFilter"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="name">按名称</option>
              <option value="expiry_date">按有效期</option>
              <option value="quantity">按库存</option>
              <option value="-created_at">按添加时间</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 药品列表 -->
      <div v-if="medicines.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- 动态药品卡片 -->
        <div 
          v-for="medicine in medicines" 
          :key="medicine.id"
          class="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200"
        >
          <div class="p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ medicine.name }}</h3>
                <p class="text-sm text-gray-600">{{ medicine.specification }}</p>
                <p class="text-sm text-gray-500">{{ medicine.manufacturer }}</p>
              </div>
              <div class="ml-4">
                <!-- 调试信息 -->
                <div class="text-xs text-gray-500 mb-1">{{ medicine.image_path || '无图片' }}</div>
                <img
                  :src="getImageUrl(medicine.image_path) || '/icons/app-icon.svg'"
                  :alt="`${medicine.name}图片`"
                  class="w-16 h-16 rounded-lg object-cover bg-gray-100"
                  @error="handleImageError"
                />
              </div>
            </div>

            <div class="space-y-2 mb-4">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">剩余数量:</span>
                <span :class="{
                  'font-medium text-gray-900': medicine.quantity > 10,
                  'font-medium text-orange-600': medicine.quantity <= 10 && medicine.quantity > 5,
                  'font-medium text-red-600': medicine.quantity <= 5
                }">{{ medicine.quantity }}{{ getMedicineTypeUnit(medicine.medicine_type) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">有效期:</span>
                <span :class="{
                  'font-medium text-gray-900': !isExpiringSoon(medicine.expiry_date),
                  'font-medium text-red-600': isExpiringSoon(medicine.expiry_date)
                }">{{ formatDate(medicine.expiry_date) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">存储条件:</span>
                <span class="font-medium text-gray-900">{{ medicine.storage_conditions }}</span>
              </div>
            </div>

            <div class="flex items-center justify-between">
              <span :class="getStatusBadgeClass(medicine)"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                {{ getStatusText(medicine) }}
              </span>
              <div class="flex space-x-2">
                <router-link
                  :to="`/medicines/${medicine.id}`"
                  class="text-blue-600 hover:text-blue-500 text-sm font-medium"
                >
                  查看详情
                </router-link>
                <button 
                  @click="editMedicine(medicine)"
                  class="text-gray-400 hover:text-gray-500"
                  title="编辑药品"
                >
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                </button>
                <button 
                  @click="deleteMedicine(medicine)"
                  class="text-red-400 hover:text-red-500"
                  title="删除药品"
                >
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 7.172V5L8 4z"></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">暂无药品</h3>
        <p class="mt-1 text-sm text-gray-500">开始添加您的第一个药品吧</p>
        <div class="mt-6">
          <button
            @click="showAddDialog = true"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            添加药品
          </button>
        </div>
      </div>
    </div>

    <!-- 药品表单对话框 -->
    <MedicineForm
      :visible="showAddDialog || showEditDialog"
      :medicine="editingMedicine"
      @close="closeDialog"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useMedicineStore } from '@/stores/medicine'
import { storeToRefs } from 'pinia'
import MedicineForm from '@/components/MedicineForm.vue'
import type { Medicine } from '@/types/medicine'
import { getBackendOrigin } from '@/utils/api'

/**
 * 药品管理页面组件
 * 显示药品列表，支持搜索、筛选和管理功能
 */

// 使用medicine store
const medicineStore = useMedicineStore()

// 对话框状态
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const editingMedicine = ref<Medicine | null>(null)

// 搜索状态
const searchQuery = ref('')
const filters = ref({
  status: '',
  sortBy: 'name'
})

// 计算属性（使用 storeToRefs 获取 Ref 再暴露为数组）
const { medicines: medicinesRef } = storeToRefs(medicineStore)
const medicines = computed(() => medicinesRef.value)
const loading = computed(() => medicineStore.loading)
const error = computed(() => medicineStore.error)

// 搜索和筛选方法
const handleSearch = async () => {
  console.log('🔵 [MedicinesPage] 开始搜索:', searchQuery.value)
  await loadMedicines()
}

const handleFilter = async () => {
  console.log('🔵 [MedicinesPage] 筛选条件变更:', filters.value)
  await loadMedicines()
}

// 加载药品列表
const loadMedicines = async () => {
  try {
    const params: any = {}
    
    // 添加搜索参数
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    
    // 添加排序参数
    if (filters.value.sortBy) {
      params.ordering = filters.value.sortBy
    }
    
    // 添加状态筛选参数
    if (filters.value.status === 'low-stock') {
      params.low_stock = true
    } else if (filters.value.status === 'expired') {
      params.expiry_date__lt = new Date().toISOString().split('T')[0]
    }
    
    console.log('🔵 [MedicinesPage] 请求参数:', params)
    await medicineStore.fetchMedicines(params)
    console.log('🟢 [MedicinesPage] 药品列表加载成功', {
      count: medicines.value.length,
      searchQuery: searchQuery.value,
      filters: filters.value
    })
  } catch (err) {
    console.error('🔴 [MedicinesPage] 加载药品列表失败:', err)
  }
}

// 组件挂载时的调试信息和数据获取
onMounted(async () => {
  console.log('=== MedicinesPage Component Mounted ===')
  console.log('showAddDialog:', showAddDialog.value)
  console.log('showEditDialog:', showEditDialog.value)
  
  // 获取药品列表
  await loadMedicines()
})

// 关闭对话框
const closeDialog = () => {
  showAddDialog.value = false
  showEditDialog.value = false
  editingMedicine.value = null
}

// 编辑药品
const editMedicine = (medicine: Medicine) => {
  editingMedicine.value = medicine
  showEditDialog.value = true
}

// 删除药品
const deleteMedicine = async (medicine: Medicine) => {
  // 确认删除
  const confirmed = confirm(`确定要删除药品「${medicine.name}」吗？\n\n删除后将无法恢复，请谨慎操作。`)
  
  if (!confirmed) {
    return
  }
  
  try {
    console.log('🔵 [MedicinesPage] 开始删除药品:', medicine.id, medicine.name)
    await medicineStore.deleteMedicine(medicine.id)
    console.log('🟢 [MedicinesPage] 药品删除成功:', medicine.name)
    
    // 显示成功提示
    alert(`药品「${medicine.name}」已成功删除`)
  } catch (err: any) {
    console.error('🔴 [MedicinesPage] 删除药品失败:', err)
    alert(`删除药品失败：${err.message || '未知错误'}`)
  }
}

// 处理表单成功提交
const handleFormSuccess = async () => {
  console.log('🟢 [MedicinesPage] 表单提交成功，刷新列表')
  closeDialog()
  // 刷新药品列表，保持当前搜索和筛选条件
  await loadMedicines()
}

// 处理图片加载错误
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/icons/app-icon.svg'
}

// 获取药品类型对应的单位
const getMedicineTypeUnit = (type: string) => {
  const units: Record<string, string> = {
    tablet: '片',
    capsule: '粒',
    liquid: 'ml',
    injection: '支',
    powder: '包',
    ointment: 'g',
    other: '个'
  }
  return units[type] || '个'
}

// 判断是否即将过期（30天内）
const isExpiringSoon = (expiryDate: string) => {
  const expiry = new Date(expiryDate)
  const today = new Date()
  const diffTime = expiry.getTime() - today.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays <= 30 && diffDays > 0
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toISOString().split('T')[0]
}

// 获取状态徽章样式
const getStatusBadgeClass = (medicine: Medicine) => {
  if (medicine.quantity <= 5) {
    return 'bg-red-100 text-red-800'
  } else if (medicine.quantity <= 10) {
    return 'bg-orange-100 text-orange-800'
  } else if (isExpiringSoon(medicine.expiry_date)) {
    return 'bg-yellow-100 text-yellow-800'
  } else {
    return 'bg-green-100 text-green-800'
  }
}

// 获取状态文本
const getStatusText = (medicine: Medicine) => {
  if (medicine.quantity <= 5) {
    return '库存不足'
  } else if (medicine.quantity <= 10) {
    return '库存偏低'
  } else if (isExpiringSoon(medicine.expiry_date)) {
    return '即将过期'
  } else {
    return '正常'
  }
}

// 获取完整的图片URL
const getImageUrl = (imagePath: string | null | undefined) => {
  console.log('🔵 [MedicinesPage] getImageUrl called with:', imagePath)
  if (!imagePath) {
    console.log('🔵 [MedicinesPage] imagePath is null/undefined, returning null')
    return null
  }
  // 如果已经是完整URL，直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    console.log('🔵 [MedicinesPage] imagePath is full URL, returning as-is:', imagePath)
    return imagePath
  }
  // 构建完整的服务器URL - 后端返回的path已经包含了相对路径
  const baseURL = getBackendOrigin()
  // 确保路径以/开头
  const path = imagePath.startsWith('/') ? imagePath : `/${imagePath}`
  const fullUrl = `${baseURL}/media${path}`
  console.log('🔵 [MedicinesPage] constructed full URL:', fullUrl)
  return fullUrl
}
</script>