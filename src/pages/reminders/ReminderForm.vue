<template>
  <div class="reminder-form-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button
            @click="goBack"
            class="btn-secondary"
          >
            <ArrowLeft class="w-4 h-4 mr-2" />
            返回
          </button>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">
              {{ isEdit ? '编辑提醒' : '新建提醒' }}
            </h1>
            <p class="text-gray-600 mt-1">
              {{ isEdit ? '修改提醒设置' : '创建新的用药提醒' }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 表单内容 -->
    <div class="form-container">
      <form @submit.prevent="handleSubmit" class="space-y-8">
        <!-- 基本信息 -->
        <div class="form-section">
          <h2 class="section-title">
            <Pill class="w-5 h-5 mr-2" />
            基本信息
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 药品选择 -->
            <div class="form-group">
              <label class="form-label required">药品</label>
              <select
                v-model="form.medicine_id"
                class="input-field"
                :class="{ 'border-red-500': errors.medicine_id }"
                required
              >
                <option value="">请选择药品</option>
                <option
                  v-for="medicine in medicines"
                  :key="medicine.id"
                  :value="medicine.id"
                >
                  {{ medicine.name }} - {{ medicine.specification }}
                </option>
              </select>
              <p v-if="errors.medicine_id" class="error-text">{{ errors.medicine_id }}</p>
            </div>
            
            <!-- 提醒标题 -->
            <div class="form-group">
              <label class="form-label">提醒标题</label>
              <input
                v-model="form.title"
                type="text"
                class="input-field"
                :class="{ 'border-red-500': errors.title }"
                placeholder="可选，默认使用药品名称"
              />
              <p v-if="errors.title" class="error-text">{{ errors.title }}</p>
            </div>
            
            <!-- 剂量 -->
            <div class="form-group">
              <label class="form-label required">剂量</label>
              <div class="grid grid-cols-2 gap-2 items-start">
                <input
                  v-model.number="form.dosage"
                  type="number"
                  step="0.1"
                  min="0"
                  class="input-field w-full min-w-0"
                  :class="{ 'border-red-500': errors.dosage }"
                  placeholder="剂量"
                  required
                />
                <select
                  v-model="form.dosage_unit"
                  class="input-field w-full min-w-0"
                  :class="{ 'border-red-500': errors.dosage_unit }"
                  required
                >
                  <option value="tablet">片</option>
                  <option value="capsule">粒</option>
                  <option value="ml">毫升</option>
                  <option value="mg">毫克</option>
                  <option value="g">克</option>
                  <option value="drop">滴</option>
                  <option value="spray">喷</option>
                  <option value="patch">贴</option>
                  <option value="injection">针</option>
                </select>
              </div>
              <p v-if="errors.dosage" class="error-text">{{ errors.dosage }}</p>
            </div>
            
            <!-- 用药时机 -->
            <div class="form-group">
              <label class="form-label required">用药时机</label>
              <select
                v-model="form.meal_timing"
                class="input-field"
                :class="{ 'border-red-500': errors.meal_timing }"
                required
              >
                <option value="before_meal">餐前</option>
                <option value="with_meal">餐中</option>
                <option value="after_meal">餐后</option>
                <option value="anytime">任意时间</option>
                <option value="before_breakfast">早饭前</option>
                <option value="after_dinner">晚饭后</option>
                <option value="before_bed">睡前</option>
              </select>
              <p v-if="errors.meal_timing" class="error-text">{{ errors.meal_timing }}</p>
            </div>
          </div>
        </div>

        <!-- 时间设置 -->
        <div class="form-section">
          <h2 class="section-title">
            <Clock class="w-5 h-5 mr-2" />
            时间设置
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 频率选择 -->
            <div class="form-group">
              <label class="form-label required">服药频率</label>
              <select
                v-model="form.frequency"
                class="input-field"
                :class="{ 'border-red-500': errors.frequency }"
                @change="onFrequencyChange"
                required
              >
                <option value="daily">每日一次</option>
                <option value="twice_daily">每日两次</option>
                <option value="three_times_daily">每日三次</option>
                <option value="four_times_daily">每日四次</option>
                <option value="weekly">每周一次</option>
                <option value="every_other_day">隔日一次</option>
                <option value="custom">自定义</option>
              </select>
              <p v-if="errors.frequency" class="error-text">{{ errors.frequency }}</p>
            </div>
            
            <!-- 提醒时间 -->
            <div class="form-group">
              <label class="form-label required">提醒时间</label>
              <div v-if="form.frequency === 'custom'" class="space-y-2">
                <div
                  v-for="(time, index) in customTimes"
                  :key="index"
                  class="flex items-center space-x-2"
                >
                  <input
                    v-model="customTimes[index]"
                    type="time"
                    class="input-field flex-1"
                    required
                  />
                  <button
                    v-if="customTimes.length > 1"
                    @click="removeCustomTime(index)"
                    type="button"
                    class="btn-sm btn-danger"
                  >
                    <Minus class="w-4 h-4" />
                  </button>
                </div>
                <button
                  @click="addCustomTime"
                  type="button"
                  class="btn-sm btn-secondary"
                >
                  <Plus class="w-4 h-4 mr-1" />
                  添加时间
                </button>
              </div>
              <div v-else class="space-y-2">
                <div
                  v-for="(time, index) in reminderTimes"
                  :key="index"
                  class="flex items-center space-x-2"
                >
                  <input
                    v-model="reminderTimes[index]"
                    type="time"
                    class="input-field flex-1"
                    :class="{ 'border-red-500': errors.reminder_time }"
                    required
                  />
                  <span class="text-sm text-gray-500">
                    {{ getTimeLabel(index) }}
                  </span>
                </div>
              </div>
              <p v-if="errors.reminder_time" class="error-text">{{ errors.reminder_time }}</p>
            </div>
          </div>
        </div>

        <!-- 日期范围 -->
        <div class="form-section">
          <h2 class="section-title">
            <Calendar class="w-5 h-5 mr-2" />
            日期范围
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 开始日期 -->
            <div class="form-group">
              <label class="form-label required">开始日期</label>
              <input
                v-model="form.start_date"
                type="date"
                class="input-field"
                :class="{ 'border-red-500': errors.start_date }"
                :min="today"
                required
              />
              <p v-if="errors.start_date" class="error-text">{{ errors.start_date }}</p>
            </div>
            
            <!-- 结束日期 -->
            <div class="form-group">
              <label class="form-label">结束日期</label>
              <div class="space-y-2">
                <div class="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="no-end-date"
                    v-model="noEndDate"
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label for="no-end-date" class="text-sm text-gray-700">
                    无结束日期（长期服药）
                  </label>
                </div>
                <input
                  v-if="!noEndDate"
                  v-model="form.end_date"
                  type="date"
                  class="input-field"
                  :class="{ 'border-red-500': errors.end_date }"
                  :min="form.start_date || today"
                />
              </div>
              <p v-if="errors.end_date" class="error-text">{{ errors.end_date }}</p>
            </div>
          </div>
        </div>

        <!-- 重复规则 -->
        <div v-if="form.frequency === 'weekly' || form.frequency === 'custom'" class="form-section">
          <h2 class="section-title">
            <Repeat class="w-5 h-5 mr-2" />
            重复规则
          </h2>
          
          <div class="form-group">
            <label class="form-label">重复周期</label>
            <div v-if="form.frequency === 'weekly'" class="space-y-3">
              <p class="text-sm text-gray-600">选择每周的哪几天重复提醒：</p>
              <div class="grid grid-cols-7 gap-2">
                <label
                  v-for="(day, index) in weekDays"
                  :key="index"
                  class="flex flex-col items-center space-y-1 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    :value="index"
                    v-model="selectedWeekDays"
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span class="text-sm text-gray-700">{{ day }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- 特殊说明 -->
        <div class="form-section">
          <h2 class="section-title">
            <FileText class="w-5 h-5 mr-2" />
            特殊说明
          </h2>
          
          <div class="form-group">
            <label class="form-label">用药说明</label>
            <textarea
              v-model="form.special_instructions"
              class="input-field"
              :class="{ 'border-red-500': errors.special_instructions }"
              rows="4"
              placeholder="请输入特殊用药说明，如注意事项、副作用等..."
            ></textarea>
            <p v-if="errors.special_instructions" class="error-text">{{ errors.special_instructions }}</p>
          </div>
        </div>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <div class="flex items-center justify-end space-x-4">
            <button
              type="button"
              @click="goBack"
              class="btn-secondary"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="btn-primary"
            >
              <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              {{ isEdit ? '更新提醒' : '创建提醒' }}
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useMedicineStore } from '@/stores/medicine'
import { useReminderStore } from '@/stores/reminder'
import {
  ArrowLeft,
  Pill,
  Clock,
  Calendar,
  Repeat,
  FileText,
  Plus,
  Minus
} from 'lucide-vue-next'

// 接口类型定义
interface Medicine {
  id: number
  name: string
  specification: string
}

interface ReminderForm {
  medicine_id: number | ''
  title: string
  dosage: number | ''
  dosage_unit: string
  frequency: string
  meal_timing: string
  reminder_time: string
  start_date: string
  end_date: string
  special_instructions: string
  is_active: boolean
}

// 响应式数据
const router = useRouter()
const route = useRoute()
const { success: showSuccess, error: showError, warning: showWarning, info: showInfo } = useToast()

const loading = ref(false)
const medicineStore = useMedicineStore()
const reminderStore = useReminderStore()
const medicines = computed<Medicine[]>(() => medicineStore.medicines as any)
const noEndDate = ref(false)
const customTimes = ref<string[]>(['09:00'])
const reminderTimes = ref<string[]>(['09:00'])
const selectedWeekDays = ref<number[]>([1]) // 默认选择周一

const form = reactive<ReminderForm>({
  medicine_id: '',
  title: '',
  dosage: '',
  dosage_unit: 'tablet',
  frequency: 'daily',
  meal_timing: 'after_meal',
  reminder_time: '09:00',
  start_date: '',
  end_date: '',
  special_instructions: '',
  is_active: true
})

const errors = reactive<Record<string, string>>({})

// 计算属性
const isEdit = computed(() => !!route.params.id)
const today = computed(() => new Date().toISOString().split('T')[0])

const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

// 方法
/**
 * 获取药品列表（使用 Pinia Store）
 * 函数级注释：调用 medicineStore.fetchMedicines，支持分页与普通列表。
 * - 输入：无（使用默认分页或列表参数，可后续扩展）
 * - 输出：更新 store 中的 medicines 状态，当前页面通过 computed 绑定。
 */
const fetchMedicines = async () => {
  try {
    await medicineStore.fetchMedicines({ page: 1, page_size: 100 })
    console.log('获取到药品列表(store):', medicines.value?.length)
  } catch (error) {
    console.error('获取药品列表失败(store):', error)
    showError('获取药品列表失败')
  }
}

/**
 * 获取提醒详情（使用 Pinia Store）
 * 函数级注释：根据 id 调用 reminderStore.fetchReminder，解析返回填充表单。
 */
const fetchReminder = async (id: string) => {
  try {
    loading.value = true
    const reminder: any = await reminderStore.fetchReminder(Number(id))
    if (!reminder) {
      showError('获取提醒信息失败')
      goBack()
      return
    }
    Object.assign(form, {
      // 兼容后端返回的联合类型：number | { id: number; ... }
      // 若为对象则取其 id，若为 number 则直接使用该数值
      medicine_id: typeof reminder.medicine === 'object' ? reminder.medicine.id : reminder.medicine,
      title: reminder.title,
      dosage: reminder.dosage,
      dosage_unit: reminder.dosage_unit,
      frequency: reminder.frequency,
      meal_timing: reminder.meal_timing,
      reminder_time: reminder.reminder_time,
      start_date: reminder.start_date,
      end_date: reminder.end_date || '',
      special_instructions: reminder.special_instructions || '',
      is_active: reminder.is_active
    })

    noEndDate.value = !reminder.end_date

    // 处理提醒时间
    if (reminder.frequency === 'custom' && reminder.custom_times) {
      customTimes.value = reminder.custom_times
    } else {
      updateReminderTimes()
    }

    // 处理周重复
    if (reminder.frequency === 'weekly' && reminder.weekdays) {
      selectedWeekDays.value = reminder.weekdays
    }
  } catch (error) {
    console.error('获取提醒信息失败(store):', error)
    showError('获取提醒信息失败')
  } finally {
    loading.value = false
  }
}

const onFrequencyChange = () => {
  updateReminderTimes()
  if (form.frequency !== 'custom') {
    customTimes.value = ['09:00']
  }
  if (form.frequency !== 'weekly') {
    selectedWeekDays.value = [1]
  }
}

const updateReminderTimes = () => {
  const timeCount = {
    daily: 1,
    twice_daily: 2,
    three_times_daily: 3,
    four_times_daily: 4,
    weekly: 1,
    every_other_day: 1,
    custom: 0
  }[form.frequency] ?? 1
  
  if (timeCount > 0) {
    reminderTimes.value = Array(timeCount).fill('').map((_, index) => {
      const defaultTimes = ['09:00', '13:00', '18:00', '21:00']
      return defaultTimes[index] || '09:00'
    })
    form.reminder_time = reminderTimes.value[0]
  }
}

const addCustomTime = () => {
  customTimes.value.push('09:00')
}

const removeCustomTime = (index: number) => {
  if (customTimes.value.length > 1) {
    customTimes.value.splice(index, 1)
  }
}

const getTimeLabel = (index: number) => {
  const labels = ['第一次', '第二次', '第三次', '第四次']
  return labels[index] || `第${index + 1}次`
}

const validateForm = () => {
  Object.keys(errors).forEach(key => delete errors[key])
  
  if (!form.medicine_id) {
    errors.medicine_id = '请选择药品'
  }
  
  if (!form.dosage || form.dosage <= 0) {
    errors.dosage = '请输入有效的剂量'
  }
  
  if (!form.start_date) {
    errors.start_date = '请选择开始日期'
  }
  
  if (!noEndDate.value && form.end_date && form.end_date < form.start_date) {
    errors.end_date = '结束日期不能早于开始日期'
  }
  
  if (form.frequency === 'weekly' && selectedWeekDays.value.length === 0) {
    errors.frequency = '请至少选择一天'
  }
  
  return Object.keys(errors).length === 0
}

/**
 * 提交提醒表单（使用 Pinia Store）
 * 函数级注释：校验通过后，调用 createReminder 或 updateReminder；处理双层 data 结构由 ApiClient/Service 统一完成。
 */
const handleSubmit = async () => {
  if (!validateForm()) {
    showError('请检查表单信息')
    return
  }

  try {
    loading.value = true

    // 组装提交数据
    const { medicine_id, ...rest } = form
    const submitData: any = {
      ...rest,
      medicine: medicine_id, // 后端期望字段名
      end_date: noEndDate.value ? null : (form.end_date || null),
      weekdays: form.frequency === 'weekly' ? selectedWeekDays.value : [],
      custom_times: form.frequency === 'custom' ? customTimes.value : [],
    }

    console.log('提交数据payload(store):', submitData)

    if (isEdit.value) {
      await reminderStore.updateReminder(Number(route.params.id), submitData)
    } else {
      await reminderStore.createReminder(submitData)
    }

    showSuccess(`提醒${isEdit.value ? '更新' : '创建'}成功`)
    router.push('/reminders')
  } catch (error: any) {
    console.error('提交失败(store):', {
      message: error?.message,
      code: error?.code,
      stack: error?.stack,
    })
    // 如服务端返回表单字段错误且已由 store 传递，可在此扩展错误映射逻辑
    showError(error?.message || '提交失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

// 监听器
watch(() => noEndDate.value, (value) => {
  if (value) {
    form.end_date = ''
  }
})

watch(() => form.frequency, () => {
  onFrequencyChange()
})

watch(() => reminderTimes.value[0], (value) => {
  if (value) {
    form.reminder_time = value
  }
})

// 生命周期
onMounted(() => {
  form.start_date = today.value
  fetchMedicines()
  
  if (isEdit.value) {
    fetchReminder(route.params.id as string)
  } else {
    updateReminderTimes()
  }
})
</script>

<style scoped lang="postcss">
.reminder-form-page {
  @apply p-6 max-w-4xl mx-auto;
}

.page-header {
  @apply mb-6;
}

.form-container {
  @apply bg-white rounded-lg shadow p-8;
}

.form-section {
  @apply border-b border-gray-200 pb-8 last:border-b-0 last:pb-0;
}

.section-title {
  @apply text-lg font-semibold text-gray-900 mb-6 flex items-center;
}

.form-group {
  @apply space-y-2;
}

.form-label {
  @apply block text-sm font-medium text-gray-700;
}

.form-label.required::after {
  content: ' *';
  @apply text-red-500;
}

.input-field {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors;
}

.error-text {
  @apply text-sm text-red-600;
}

.form-actions {
  @apply pt-6 border-t border-gray-200;
}

.btn-primary {
  @apply bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply bg-gray-100 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-200 transition-colors flex items-center;
}

.btn-danger {
  @apply bg-red-600 text-white px-3 py-1 rounded-lg hover:bg-red-700 transition-colors flex items-center;
}

.btn-sm {
  @apply px-3 py-1 text-sm;
}
</style>
