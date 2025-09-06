<template>
  <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- 背景遮罩 -->
      <div 
        class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" 
        @click="$emit('close')"
      ></div>

      <!-- 对话框 -->
      <div class="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg">
        <!-- 标题 -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-medium text-gray-900">
            {{ medicine ? '编辑药品' : '添加药品' }}
          </h3>
          <button 
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600"
          >
            <X class="w-6 h-6" />
          </button>
        </div>

        <!-- 表单 -->
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- 基本信息 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 药品名称 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                药品名称 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.name }"
                placeholder="请输入药品名称"
              />
              <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
            </div>

            <!-- 规格 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                药品规格
              </label>
              <input
                v-model="formData.specification"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="如：100mg*30片"
              />
            </div>

            <!-- 厂商 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                生产厂商
              </label>
              <input
                v-model="formData.manufacturer"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入生产厂商"
              />
            </div>

            <!-- 药品类型 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                药品类型 <span class="text-red-500">*</span>
              </label>
              <select
                v-model="formData.medicine_type"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.medicine_type }"
              >
                <option value="">请选择药品类型</option>
                <option value="tablet">片剂</option>
                <option value="capsule">胶囊</option>
                <option value="liquid">液体</option>
                <option value="injection">注射剂</option>
                <option value="ointment">软膏</option>
                <option value="drops">滴剂</option>
                <option value="other">其他</option>
              </select>
              <p v-if="errors.medicine_type" class="mt-1 text-sm text-red-600">{{ errors.medicine_type }}</p>
            </div>

            <!-- 库存数量 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                库存数量 <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="formData.quantity"
                type="number"
                min="0"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.quantity }"
                placeholder="请输入库存数量"
              />
              <p v-if="errors.quantity" class="mt-1 text-sm text-red-600">{{ errors.quantity }}</p>
            </div>

            <!-- 是否处方药 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                药品分类
              </label>
              <div class="flex items-center space-x-4">
                <label class="flex items-center">
                  <input
                    v-model="formData.is_prescription"
                    type="radio"
                    :value="true"
                    class="mr-2 text-blue-600 focus:ring-blue-500"
                  />
                  处方药
                </label>
                <label class="flex items-center">
                  <input
                    v-model="formData.is_prescription"
                    type="radio"
                    :value="false"
                    class="mr-2 text-blue-600 focus:ring-blue-500"
                  />
                  非处方药
                </label>
              </div>
            </div>
          </div>

          <!-- 日期和价格信息 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 有效期 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                有效期
              </label>
              <input
                v-model="formData.expiry_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <!-- 采购日期 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                采购日期
              </label>
              <input
                v-model="formData.purchase_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <!-- 采购价格 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                采购价格
              </label>
              <input
                v-model.number="formData.purchase_price"
                type="number"
                min="0"
                step="0.01"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入采购价格"
              />
            </div>

            <!-- 批号 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                批号
              </label>
              <input
                v-model="formData.batch_number"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入批号"
              />
            </div>
          </div>

          <!-- 存储条件 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              存储条件
            </label>
            <input
              v-model="formData.storage_conditions"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="如：阴凉干燥处保存，温度不超过25℃"
            />
          </div>

          <!-- 药品图片 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              药品图片
            </label>
            <div class="flex items-center space-x-4">
              <button
                type="button"
                @click="handleImageUpload"
                class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center"
              >
                <Upload class="w-4 h-4 mr-2" />
                上传图片
              </button>
              <span v-if="formData.image_path" class="text-sm text-gray-600">
                已选择图片
              </span>
            </div>
            <!-- 图片预览 -->
            <div v-if="formData.image_path" class="mt-2">
              <img 
                :src="getImagePreviewUrl(formData.image_path)" 
                alt="药品图片预览" 
                class="w-20 h-20 object-cover rounded-lg border border-gray-200"
                @error="handleImageError"
              />
              <button
                type="button"
                @click="removeImage"
                class="mt-1 text-sm text-red-600 hover:text-red-800"
              >
                删除图片
              </button>
            </div>
          </div>

          <!-- 描述 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              药品描述
            </label>
            <textarea
              v-model="formData.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="请输入药品描述、用法用量等信息"
            ></textarea>
          </div>

          <!-- 表单按钮 -->
          <div class="flex justify-end space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              @click="$emit('close')"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              <span v-if="loading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
              {{ loading ? '保存中...' : (medicine ? '更新药品' : '添加药品') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { X, Upload } from 'lucide-vue-next'
import { useMedicineStore } from '@/stores/medicine'
import type { Medicine, MedicineCreateData, MedicineUpdateData } from '@/types/medicine'
import { toast } from 'vue-sonner'

// Props
interface Props {
  visible: boolean
  medicine?: Medicine | null
}

const props = withDefaults(defineProps<Props>(), {
  medicine: null
})

// Emits
const emit = defineEmits<{
  close: []
  success: []
}>()

// Store
const medicineStore = useMedicineStore()

// 响应式数据
const loading = ref(false)
const errors = ref<Record<string, string>>({})

// 表单数据
const formData = reactive<MedicineCreateData>({
  name: '',
  specification: '',
  manufacturer: '',
  medicine_type: 'tablet',
  quantity: 0,
  purchase_price: undefined,
  purchase_date: '',
  expiry_date: '',
  batch_number: '',
  storage_conditions: '',
  description: '',
  image_path: '', // 使用image_path替代image_url
  is_prescription: false
})

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    name: '',
    specification: '',
    manufacturer: '',
    medicine_type: 'tablet',
    quantity: 0,
    purchase_price: undefined,
    purchase_date: '',
    expiry_date: '',
    batch_number: '',
    storage_conditions: '',
    description: '',
    image_path: '', // 使用image_path替代image_url
    is_prescription: false
  })
  errors.value = {}
}

// 监听medicine变化，用于编辑模式
watch(
  () => props.medicine,
  (newMedicine) => {
    if (newMedicine) {
      // 编辑模式，填充表单数据
      Object.assign(formData, {
        name: newMedicine.name || '',
        specification: newMedicine.specification || '',
        manufacturer: newMedicine.manufacturer || '',
        medicine_type: newMedicine.medicine_type || 'tablet',
        quantity: newMedicine.quantity || 0,
        purchase_price: newMedicine.purchase_price,
        purchase_date: newMedicine.purchase_date || '',
        expiry_date: newMedicine.expiry_date || '',
        batch_number: newMedicine.batch_number || '',
        storage_conditions: newMedicine.storage_conditions || '',
        description: newMedicine.description || '',
        image_path: newMedicine.image_path || '', // 使用image_path字段
        is_prescription: newMedicine.is_prescription || false
      })
    } else {
      // 添加模式，重置表单
      resetForm()
    }
  },
  { immediate: true }
)

// 表单验证
const validateForm = (): boolean => {
  errors.value = {}

  if (!formData.name.trim()) {
    errors.value.name = '请输入药品名称'
  }

  if (!formData.medicine_type) {
    errors.value.medicine_type = '请选择药品类型'
  }

  if (formData.quantity < 0) {
    errors.value.quantity = '库存数量不能为负数'
  }

  if (formData.purchase_price !== undefined && formData.purchase_price < 0) {
    errors.value.purchase_price = '采购价格不能为负数'
  }

  return Object.keys(errors.value).length === 0
}

// 处理表单提交
const handleSubmit = async () => {
  console.log('🔵 [MedicineForm] === FORM SUBMIT START ===')
  console.log('🔵 [MedicineForm] Form submit started:', {
    isEditMode: !!props.medicine,
    formData: formData,
    tokenExists: !!localStorage.getItem('access_token')
  })
  
  const validationResult = validateForm()
  if (!validationResult) {
    console.log('🔴 [MedicineForm] Form validation failed:', errors.value)
    return
  }

  loading.value = true
  
  try {
    // 清理表单数据，处理空字符串字段
    const cleanFormData = { ...formData }
    
    console.log('🔵 [MedicineForm] Original form data:', cleanFormData)
    
    // 清理其他可能的空字符串字段
    Object.keys(cleanFormData).forEach(key => {
      const value = cleanFormData[key as keyof typeof cleanFormData]
      // 保留名称字段和图片路径字段，其他空字段删除
      if (value === '' && key !== 'name' && key !== 'image_path') {
        delete cleanFormData[key as keyof typeof cleanFormData]
        console.log(`🔵 [MedicineForm] Deleted empty field: ${key}`)
      }
    })
    
    console.log('🔵 [MedicineForm] Cleaned form data:', cleanFormData)
    console.log('🔵 [MedicineForm] Fields included:', Object.keys(cleanFormData))
    
    if (props.medicine) {
      // 编辑模式
      console.log('🔵 [MedicineForm] Updating medicine:', props.medicine.id)
      const updateData: MedicineUpdateData = cleanFormData
      
      const result = await medicineStore.updateMedicine(props.medicine.id, updateData)
      console.log('🟢 [MedicineForm] Medicine updated successfully')
      toast.success('药品更新成功')
    } else {
      // 添加模式
      console.log('🔵 [MedicineForm] Creating new medicine')
      
      const result = await medicineStore.createMedicine(cleanFormData)
      console.log('🟢 [MedicineForm] Medicine created successfully')
      toast.success('药品添加成功')
    }
    
    emit('success')
    
  } catch (error: any) {
    console.error('🔴 [MedicineForm] Save failed:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      timestamp: new Date().toISOString()
    })
    
    // 处理表单验证错误
    if (error.response?.data?.errors) {
      errors.value = error.response.data.errors
      console.log('🔴 [MedicineForm] Form validation errors:', error.response.data.errors)
      console.log('🔴 [MedicineForm] Detailed error analysis:')
      Object.entries(error.response.data.errors).forEach(([field, fieldErrors]) => {
        console.log(`  - ${field}:`, fieldErrors)
      })
    } else {
      const errorMessage = error.response?.data?.message || error.message || '保存失败，请重试'
      toast.error(errorMessage)
    }
  } finally {
    loading.value = false
  }
}

// 处理图片上传
const handleImageUpload = async () => {
  // 创建文件输入元素
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (file) {
      try {
        console.log('🔵 [MedicineForm] Starting image upload:', file.name)
        toast.info('正在上传图片...')
        
        // 调用上传API
        const { uploadApi } = await import('@/api/upload')
        const response = await uploadApi.uploadMedicineImage(file)
        
        console.log('🟢 [MedicineForm] Image upload response:', response)
        console.log('🔵 [MedicineForm] Response data structure:', response.data)
        
        // 检查响应数据结构 - 后端返回 {success: true, data: {image_path: '...'}}
        if (response.data?.success && response.data?.data?.image_path) {
          formData.image_path = response.data.data.image_path
          console.log('🟢 [MedicineForm] Image path set:', formData.image_path)
          toast.success('图片上传成功')
        } else {
          console.error('🔴 [MedicineForm] Invalid response structure:', response)
          console.error('🔴 [MedicineForm] Expected: response.data.data.image_path, got:', response.data?.data?.image_path)
          toast.error('图片上传失败：响应格式错误')
        }
      } catch (error) {
        console.error('🔴 [MedicineForm] Image upload failed:', error)
        toast.error('图片上传失败，请重试')
      }
    }
  }
  input.click()
}

// 删除图片
const removeImage = () => {
  formData.image_path = ''
  toast.success('图片已删除')
}

// 获取图片预览URL
const getImagePreviewUrl = (imagePath: string): string => {
  if (!imagePath) return ''
  // 如果已经是完整URL，直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  // 构建完整的服务器URL - 后端返回的path已经包含了相对路径
  const baseUrl = 'http://127.0.0.1:8000'
  // 确保路径以/开头
  const path = imagePath.startsWith('/') ? imagePath : `/${imagePath}`
  return `${baseUrl}/media${path}`
}

// 处理图片加载错误
const handleImageError = () => {
  formData.image_path = ''
  toast.error('图片加载失败，请重新上传')
}

// 组件挂载时设置默认采购日期
onMounted(() => {
  console.log('=== MedicineForm Component Mounted ===')
  console.log('Props medicine:', props.medicine)
  console.log('Initial form data:', formData)
  
  if (!props.medicine && !formData.purchase_date) {
    formData.purchase_date = new Date().toISOString().split('T')[0]
  }
  
  console.log('=== Component Mount Complete ===')
})
</script>

<style scoped>
/* 自定义样式 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 表单样式增强 */
input:focus,
select:focus,
textarea:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 错误状态样式 */
.border-red-500 {
  border-color: #ef4444;
}

/* 加载动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>