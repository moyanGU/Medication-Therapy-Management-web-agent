<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button 
              @click="$router.back()"
              class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="-ml-0.5 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
              </svg>
              返回
            </button>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">{{ medicine?.name || '药品详情' }}</h1>
              <p class="text-gray-600 mt-1">查看药品的详细信息</p>
            </div>
          </div>
          <div class="flex items-center space-x-3" v-if="medicine">
            <button 
              @click="editMedicine"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="-ml-1 mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
              编辑药品
            </button>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="text-center py-12">
        <div class="text-red-500 text-lg mb-2">加载失败</div>
        <div class="text-gray-600 mb-4">{{ error }}</div>
        <button
          @click="fetchMedicineDetail"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          重试
        </button>
      </div>

      <!-- 药品详情内容 -->
      <div v-else-if="medicine" class="bg-white shadow rounded-lg">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 p-8">
          <!-- 左侧：药品图片 -->
          <div class="lg:col-span-1">
            <div class="aspect-square bg-gray-100 rounded-lg overflow-hidden mb-6">
              <img 
                :src="getImageUrl(medicine.image_path) || '/icons/app-icon.svg'"
                :alt="medicine.name"
                class="w-full h-full object-cover"
                @error="handleImageError"
              />
            </div>
            
            <!-- 状态标签 -->
            <div class="space-y-3">
              <div :class="getStatusBadgeClass(medicine)"
                   class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium w-full justify-center">
                {{ getStatusText(medicine) }}
              </div>
            </div>
          </div>

          <!-- 右侧：药品信息 -->
          <div class="lg:col-span-2">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 基本信息 -->
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-900 border-b pb-2">基本信息</h3>
                
                <div class="space-y-3">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">药品名称</label>
                    <p class="mt-1 text-sm text-gray-900">{{ medicine.name }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">药品类型</label>
                    <p class="mt-1 text-sm text-gray-900">{{ getMedicineTypeText(medicine.medicine_type) }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">规格</label>
                    <p class="mt-1 text-sm text-gray-900">{{ medicine.specification || '未设置' }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">生产厂家</label>
                    <p class="mt-1 text-sm text-gray-900">{{ medicine.manufacturer || '未设置' }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">批号</label>
                    <p class="mt-1 text-sm text-gray-900">{{ medicine.batch_number || '未设置' }}</p>
                  </div>
                </div>
              </div>

              <!-- 库存和日期信息 -->
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-900 border-b pb-2">库存信息</h3>
                
                <div class="space-y-3">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">当前库存</label>
                    <p class="mt-1 text-sm font-semibold" :class="{
                      'text-gray-900': medicine.quantity > 10,
                      'text-orange-600': medicine.quantity <= 10 && medicine.quantity > 5,
                      'text-red-600': medicine.quantity <= 5
                    }">{{ medicine.quantity }}{{ getMedicineTypeUnit(medicine.medicine_type) }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">有效期</label>
                    <p class="mt-1 text-sm" :class="{
                      'text-gray-900': !isExpiringSoon(medicine.expiry_date),
                      'text-red-600': isExpiringSoon(medicine.expiry_date)
                    }">{{ formatDate(medicine.expiry_date) }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">购买日期</label>
                    <p class="mt-1 text-sm text-gray-900">{{ formatDate(medicine.purchase_date) }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">购买价格</label>
                    <p class="mt-1 text-sm text-gray-900">{{ medicine.purchase_price ? `¥${medicine.purchase_price}` : '未设置' }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">存储条件</label>
                    <p class="mt-1 text-sm text-gray-900">{{ medicine.storage_conditions || '常温保存' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 药品描述 -->
            <div class="mt-8" v-if="medicine.description">
              <h3 class="text-lg font-semibold text-gray-900 border-b pb-2 mb-4">药品描述</h3>
              <p class="text-sm text-gray-700 leading-relaxed">{{ medicine.description }}</p>
            </div>

            <!-- 创建和更新时间 -->
            <div class="mt-8 pt-6 border-t border-gray-200">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-500">
                <div>
                  <span class="font-medium">创建时间：</span>
                  {{ formatDateTime(medicine.created_at) }}
                </div>
                <div>
                  <span class="font-medium">更新时间：</span>
                  {{ formatDateTime(medicine.updated_at) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 未找到药品 -->
      <div v-else class="text-center py-12">
        <div class="text-gray-500 text-lg mb-2">未找到药品信息</div>
        <button
          @click="$router.push('/medicines')"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          返回药品列表
        </button>
      </div>
    </div>

    <!-- 编辑对话框 -->
    <MedicineForm
      :visible="showEditDialog"
      :medicine="medicine"
      @close="showEditDialog = false"
      @success="handleEditSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMedicineStore } from '@/stores/medicine'
import MedicineForm from '@/components/MedicineForm.vue'
import type { Medicine } from '@/types/medicine'
import { getBackendOrigin } from '@/utils/api'

/**
 * 药品详情页面组件
 */

const route = useRoute()
const router = useRouter()
const medicineStore = useMedicineStore()

// 响应式数据
const medicine = ref<Medicine | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const showEditDialog = ref(false)

// 获取药品详情
const fetchMedicineDetail = async () => {
  try {
    loading.value = true
    error.value = null
    
    const medicineId = route.params.id as string
    if (!medicineId) {
      error.value = '药品ID无效'
      return
    }
    
    await medicineStore.fetchMedicine(parseInt(medicineId))
    medicine.value = medicineStore.currentMedicine
    
    if (!medicine.value) {
      error.value = '未找到药品信息'
    }
  } catch (err: any) {
    error.value = err.message || '获取药品详情失败'
    console.error('获取药品详情失败:', err)
  } finally {
    loading.value = false
  }
}

// 编辑药品
const editMedicine = () => {
  showEditDialog.value = true
}

// 处理编辑成功
const handleEditSuccess = () => {
  showEditDialog.value = false
  fetchMedicineDetail() // 重新获取数据
}

// 获取完整的图片URL
const getImageUrl = (imagePath: string | null | undefined) => {
  if (!imagePath) {
    return null
  }
  // 如果已经是完整URL，直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  // 构建完整的服务器URL - 后端返回的path已经包含了相对路径
  const baseURL = getBackendOrigin()
  // 确保路径以/开头
  const path = imagePath.startsWith('/') ? imagePath : `/${imagePath}`
  return `${baseURL}/media${path}`
}

// 处理图片加载错误
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/icons/app-icon.svg'
}

// 获取药品类型文本
const getMedicineTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    tablet: '片剂',
    capsule: '胶囊',
    liquid: '液体',
    injection: '注射剂',
    ointment: '软膏',
    powder: '粉剂',
    other: '其他'
  }
  return typeMap[type] || type
}

// 获取药品类型单位
const getMedicineTypeUnit = (type: string) => {
  const unitMap: Record<string, string> = {
    tablet: '片',
    capsule: '粒',
    liquid: 'ml',
    injection: '支',
    ointment: 'g',
    powder: 'g',
    other: '个'
  }
  return unitMap[type] || '个'
}

// 检查是否即将过期
const isExpiringSoon = (expiryDate: string | null) => {
  if (!expiryDate) return false
  const expiry = new Date(expiryDate)
  const now = new Date()
  const diffTime = expiry.getTime() - now.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays <= 30 && diffDays >= 0
}

// 格式化日期
const formatDate = (dateString: string | null) => {
  if (!dateString) return '未设置'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 格式化日期时间
const formatDateTime = (dateString: string | null) => {
  if (!dateString) return '未设置'
  return new Date(dateString).toLocaleString('zh-CN')
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

// 获取状态样式类
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

// 组件挂载时获取数据
onMounted(() => {
  fetchMedicineDetail()
})
</script>

<style scoped>
/* 自定义样式 */
</style>