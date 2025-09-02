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
                规格
              </label>
              <input
                v-model="formData.specification"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="如：100mg/片"
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
              <input
                v-model="formData.image_url"
                type="url"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入图片URL"
              />
              <button
                type="button"
                @click="handleImageUpload"
                class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Upload class="w-4 h-4 mr-2 inline" />
                上传图片
              </button>
            </div>
            <!-- 图片预览 -->
            <div v-if="formData.image_url" class="mt-2">
              <img 
                :src="formData.image_url" 
                alt="药品图片预览" 
                class="w-20 h-20 object-cover rounded-lg border border-gray-200"
                @error="handleImageError"
              />
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
  is_prescription: false,
  expiry_date: '',
  purchase_date: '',
  purchase_price: undefined,
  batch_number: '',
  storage_conditions: '',
  image_url: '',
  description: ''
})

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
        is_prescription: newMedicine.is_prescription || false,
        expiry_date: newMedicine.expiry_date || '',
        purchase_date: newMedicine.purchase_date || '',
        purchase_price: newMedicine.purchase_price,
        batch_number: newMedicine.batch_number || '',
        storage_conditions: newMedicine.storage_conditions || '',
        image_url: newMedicine.image_url || '',
        description: newMedicine.description || ''
      })
    } else {
      // 添加模式，重置表单
      resetForm()
    }
  },
  { immediate: true }
)

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    name: '',
    specification: '',
    manufacturer: '',
    medicine_type: 'tablet',
    quantity: 0,
    is_prescription: false,
    expiry_date: '',
    purchase_date: '',
    purchase_price: undefined,
    batch_number: '',
    storage_conditions: '',
    image_url: '',
    description: ''
  })
  errors.value = {}
}

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
  if (!validateForm()) {
    return
  }

  loading.value = true
  try {
    if (props.medicine) {
      // 编辑模式
      const updateData: MedicineUpdateData = { ...formData }
      await medicineStore.updateMedicine(props.medicine.id, updateData)
      toast.success('药品更新成功')
    } else {
      // 添加模式
      await medicineStore.createMedicine(formData)
      toast.success('药品添加成功')
    }
    emit('success')
  } catch (error: any) {
    console.error('保存药品失败:', error)
    if (error.response?.data?.errors) {
      errors.value = error.response.data.errors
    } else {
      toast.error(error.message || '保存失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

// 处理图片上传
const handleImageUpload = () => {
  // 创建文件输入元素
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (file) {
      // 这里可以实现图片上传到服务器的逻辑
      // 目前使用本地预览
      const reader = new FileReader()
      reader.onload = (e) => {
        formData.image_url = e.target?.result as string
      }
      reader.readAsDataURL(file)
      toast.info('图片上传功能待实现，当前为本地预览')
    }
  }
  input.click()
}

// 处理图片加载错误
const handleImageError = () => {
  formData.image_url = ''
  toast.error('图片加载失败，请检查URL是否正确')
}

// 组件挂载时设置默认采购日期
onMounted(() => {
  if (!props.medicine && !formData.purchase_date) {
    formData.purchase_date = new Date().toISOString().split('T')[0]
  }
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