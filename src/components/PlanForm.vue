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
            {{ plan ? '编辑计划' : '创建计划' }}
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
            <!-- 计划名称 -->
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                计划名称 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.name }"
                placeholder="请输入计划名称，如：降血压用药方案"
              />
              <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
            </div>

            <!-- 计划类型 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                计划类型 <span class="text-red-500">*</span>
              </label>
              <select
                v-model="formData.plan_type"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.plan_type }"
              >
                <option value="">请选择计划类型</option>
                <option value="long_term">长期用药</option>
                <option value="short_term">短期用药</option>
                <option value="acute">急性期</option>
                <option value="chronic">慢性病管理</option>
                <option value="preventive">预防性</option>
                <option value="rehabilitation">康复</option>
              </select>
              <p v-if="errors.plan_type" class="mt-1 text-sm text-red-600">{{ errors.plan_type }}</p>
            </div>

            <!-- 优先级 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                优先级
              </label>
              <select
                v-model="formData.priority"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
                <option value="urgent">紧急</option>
              </select>
            </div>

            <!-- 开始日期 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                开始日期 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="formData.start_date"
                type="date"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.start_date }"
              />
              <p v-if="errors.start_date" class="mt-1 text-sm text-red-600">{{ errors.start_date }}</p>
            </div>

            <!-- 结束日期 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                结束日期
              </label>
              <input
                v-model="formData.end_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p class="text-xs text-gray-500 mt-1">不设置则为长期计划</p>
            </div>
          </div>

          <!-- 医疗信息 -->
          <div class="space-y-4">
            <h4 class="text-base font-medium text-gray-900">医疗信息（可选）</h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 来源 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  计划来源
                </label>
                <select
                  v-model="formData.source"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="self">自己制定</option>
                  <option value="doctor">医生制定</option>
                  <option value="pharmacist">药师建议</option>
                  <option value="import">导入</option>
                  <option value="template">模板</option>
                </select>
              </div>

              <!-- 医生姓名 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  医生姓名
                </label>
                <input
                  v-model="formData.doctor_name"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="请输入医生姓名"
                />
              </div>

              <!-- 医院 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  医院名称
                </label>
                <input
                  v-model="formData.hospital_name"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="请输入医院名称"
                />
              </div>

              <!-- 科室 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  科室
                </label>
                <input
                  v-model="formData.department"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="请输入科室"
                />
              </div>
            </div>
          </div>

          <!-- 治疗目标和诊断 -->
          <div class="space-y-4">
            <!-- 诊断 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                诊断
              </label>
              <input
                v-model="formData.diagnosis"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入相关诊断信息"
              />
            </div>

            <!-- 治疗目标 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                治疗目标
              </label>
              <textarea
                v-model="formData.treatment_goal"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入治疗目标，如：血压控制在130/80mmHg以下"
              ></textarea>
            </div>

            <!-- 计划描述 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                计划描述
              </label>
              <textarea
                v-model="formData.description"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入计划的详细描述和说明"
              ></textarea>
            </div>
          </div>

          <!-- 安全提醒 -->
          <div class="space-y-4">
            <!-- 注意事项 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                注意事项
              </label>
              <textarea
                v-model="formData.precautions"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入用药注意事项"
              ></textarea>
            </div>

            <!-- 副作用监测 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                副作用监测
              </label>
              <textarea
                v-model="formData.side_effects_monitoring"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请输入需要监测的副作用"
              ></textarea>
            </div>

            <!-- 复查日期 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                复查日期
              </label>
              <input
                v-model="formData.review_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
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
              {{ loading ? '保存中...' : (plan ? '更新计划' : '创建计划') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { X } from 'lucide-vue-next'
import plansApi from '@/api/plans'
import type { MedicationPlan, PlanCreateData, PlanUpdateData } from '@/types/plan'
import { toast } from 'vue-sonner'

// Props
interface Props {
  visible: boolean
  plan?: MedicationPlan | null
}

const props = withDefaults(defineProps<Props>(), {
  plan: null
})

// Emits
const emit = defineEmits<{
  close: []
  success: []
}>()

// 响应式数据
const loading = ref(false)
const errors = ref<Record<string, string>>({})

// 表单数据
const formData = reactive<PlanCreateData>({
  name: '',
  plan_type: 'long_term',
  start_date: '',
  end_date: null,
  description: '',
  treatment_goal: '',
  is_active: true,
  priority: 'medium',
  source: 'self',
  doctor_name: '',
  hospital_name: '',
  department: '',
  diagnosis: '',
  precautions: '',
  side_effects_monitoring: '',
  review_date: '',
  status: 'active'
})

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    name: '',
    plan_type: 'long_term',
    start_date: '',
    end_date: null,
    description: '',
    treatment_goal: '',
    is_active: true,
    priority: 'medium',
    source: 'self',
    doctor_name: '',
    hospital_name: '',
    department: '',
    diagnosis: '',
    precautions: '',
    side_effects_monitoring: '',
    review_date: '',
    status: 'active'
  })
  errors.value = {}
}

// 监听plan变化，用于编辑模式
watch(
  () => props.plan,
  (newPlan) => {
    if (newPlan) {
      // 编辑模式，填充表单数据
      Object.assign(formData, {
        name: newPlan.name || '',
        plan_type: newPlan.plan_type || 'long_term',
        start_date: newPlan.start_date || '',
        end_date: newPlan.end_date || null,
        description: newPlan.description || '',
        treatment_goal: newPlan.treatment_goal || '',
        is_active: newPlan.is_active ?? true,
        priority: newPlan.priority || 'medium',
        source: newPlan.source || 'self',
        doctor_name: newPlan.doctor_name || '',
        hospital_name: newPlan.hospital_name || '',
        department: newPlan.department || '',
        diagnosis: newPlan.diagnosis || '',
        precautions: newPlan.precautions || '',
        side_effects_monitoring: newPlan.side_effects_monitoring || '',
        review_date: newPlan.review_date || '',
        status: newPlan.status || 'active'
      })
    } else {
      // 添加模式，重置表单
      resetForm()
    }
  },
  { immediate: true }
)

// 监听 visible 变化，在创建模式下每次打开时重置表单
watch(
  () => props.visible,
  (v) => {
    console.log('[PlanForm] visible changed:', v)
    if (v && !props.plan) {
      resetForm()
      // 默认开始日期为今天
      if (!formData.start_date) {
        formData.start_date = new Date().toISOString().split('T')[0]
      }
    }
  }
)

// 表单验证
const validateForm = (): boolean => {
  errors.value = {}

  if (!formData.name.trim()) {
    errors.value.name = '请输入计划名称'
  }

  if (!formData.plan_type) {
    errors.value.plan_type = '请选择计划类型'
  }

  if (!formData.start_date) {
    errors.value.start_date = '请选择开始日期'
  }

  // 结束日期不能早于开始日期
  if (formData.end_date && formData.start_date && formData.end_date < formData.start_date) {
    errors.value.end_date = '结束日期不能早于开始日期'
  }

  return Object.keys(errors.value).length === 0
}

// 处理表单提交
const handleSubmit = async () => {
  console.log('🔵 [PlanForm] === FORM SUBMIT START ===')
  console.log('🔵 [PlanForm] Form submit started:', {
    isEditMode: !!props.plan,
    formData: formData,
    tokenExists: !!localStorage.getItem('access_token')
  })
  
  const validationResult = validateForm()
  if (!validationResult) {
    console.log('🔴 [PlanForm] Form validation failed:', errors.value)
    return
  }

  loading.value = true
  
  try {
    // 清理表单数据，处理空字符串字段
    const cleanFormData = { ...formData }
    
    console.log('🔵 [PlanForm] Original form data:', cleanFormData)
    
    // 清理空字符串字段，保留必填项
    Object.keys(cleanFormData).forEach(key => {
      const value = cleanFormData[key as keyof typeof cleanFormData]
      // 保留名称、类型、开始日期等必填字段，其他空字段删除
      if (value === '' && !['name', 'plan_type', 'start_date'].includes(key)) {
        delete cleanFormData[key as keyof typeof cleanFormData]
        console.log(`🔵 [PlanForm] Deleted empty field: ${key}`)
      }
    })
    
    // 处理 end_date 空字符串转为 null
    if (cleanFormData.end_date === '') {
      cleanFormData.end_date = null
    }
    
    console.log('🔵 [PlanForm] Cleaned form data:', cleanFormData)
    console.log('🔵 [PlanForm] Fields included:', Object.keys(cleanFormData))
    
    if (props.plan) {
      // 编辑模式
      console.log('🔵 [PlanForm] Updating plan:', props.plan.id)
      const updateData: PlanUpdateData = cleanFormData
      
      const result = await plansApi.updatePlan(props.plan.id, updateData)
      console.log('🟢 [PlanForm] Plan updated successfully')
      toast.success('计划更新成功')
    } else {
      // 添加模式
      console.log('🔵 [PlanForm] Creating new plan')
      
      const result = await plansApi.createPlan(cleanFormData)
      console.log('🟢 [PlanForm] Plan created successfully')
      toast.success('计划创建成功')
    }
    
    emit('success')
    
  } catch (error: any) {
    console.error('🔴 [PlanForm] Save failed:', {
      message: error?.message,
      code: error?.code,
      timestamp: new Date().toISOString()
    })
    
    // 统一错误提示
    const errorMessage = error?.message || '保存失败，请重试'
    toast.error(errorMessage)
  } finally {
    loading.value = false
  }
}

// 组件挂载时设置默认日期
onMounted(() => {
  console.log('=== PlanForm Component Mounted ===')
  console.log('Props plan:', props.plan)
  console.log('Initial form data:', formData)
  
  if (!props.plan && !formData.start_date) {
    formData.start_date = new Date().toISOString().split('T')[0]
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