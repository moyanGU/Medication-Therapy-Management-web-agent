<template>
  <div class="reminder-form-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button @click="goBack" class="btn-secondary">
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
      <div
        v-if="
          assistiveSummaryLines.length ||
          assistiveMissingFields.length ||
          validationPriorityLines.length
        "
        class="mb-6 rounded-lg border border-blue-200 bg-blue-50 px-4 py-4"
      >
        <h3 class="text-base font-semibold text-blue-900">辅助填写提示</h3>
        <p class="mt-2 text-sm text-blue-800">
          系统会先帮你尽量填好内容，你只需要重点确认下面这些信息。
        </p>
        <p v-if="assistiveSummaryLines.length" class="mt-3 text-sm text-blue-900">
          已识别内容：{{ assistiveSummaryLines.join('；') }}
        </p>
        <p
          v-for="line in validationPriorityLines"
          :key="line"
          class="mt-2 text-sm font-medium text-red-700"
        >
          {{ line }}
        </p>
        <p
          v-if="assistiveMissingFields.length"
          class="mt-2 text-sm font-medium text-amber-700"
        >
          还需要确认：{{ assistiveMissingFields.join('、') }}
        </p>
      </div>
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
                data-field="medicine_id"
                @focus="handleFieldFocus('medicine_id')"
                @blur="handleFieldBlur('medicine_id')"
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
              <p v-if="errors.medicine_id" class="error-text">
                {{ errors.medicine_id }}
              </p>
            </div>

            <!-- 提醒标题（仅编辑模式显示） -->
            <div v-if="isEdit" class="form-group">
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
                  data-field="dosage"
                  placeholder="剂量"
                  @focus="handleFieldFocus('dosage')"
                  @blur="handleFieldBlur('dosage')"
                  required
                />
                <select
                  v-model="form.dosage_unit"
                  class="input-field w-full min-w-0"
                  :class="{ 'border-red-500': errors.dosage_unit }"
                  data-field="dosage_unit"
                  @focus="handleFieldFocus('dosage_unit')"
                  @blur="handleFieldBlur('dosage_unit')"
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
              <p v-if="errors.meal_timing" class="error-text">
                {{ errors.meal_timing }}
              </p>
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
                data-field="frequency"
                @change="onFrequencyChange"
                @focus="handleFieldFocus('frequency')"
                @blur="handleFieldBlur('frequency')"
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
              <p v-if="errors.frequency" class="error-text">
                {{ errors.frequency }}
              </p>
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
                    :class="{ 'border-red-500': errors.reminder_time }"
                    data-field="reminder_time"
                    @focus="handleFieldFocus('reminder_time')"
                    @blur="handleFieldBlur('reminder_time')"
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
                    data-field="reminder_time"
                    @focus="handleFieldFocus('reminder_time')"
                    @blur="handleFieldBlur('reminder_time')"
                    required
                  />
                  <span class="text-sm text-gray-500">
                    {{ getTimeLabel(index) }}
                  </span>
                </div>
              </div>
              <p v-if="errors.reminder_time" class="error-text">
                {{ errors.reminder_time }}
              </p>
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
                data-field="start_date"
                :min="today"
                @focus="handleFieldFocus('start_date')"
                @blur="handleFieldBlur('start_date')"
                required
              />
              <p v-if="errors.start_date" class="error-text">
                {{ errors.start_date }}
              </p>
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
                  data-field="end_date"
                  :min="form.start_date || today"
                />
              </div>
              <p v-if="errors.end_date" class="error-text">
                {{ errors.end_date }}
              </p>
            </div>
          </div>
        </div>

        <!-- 重复规则 -->
        <div
          v-if="form.frequency === 'weekly' || form.frequency === 'custom'"
          class="form-section"
        >
          <h2 class="section-title">
            <Repeat class="w-5 h-5 mr-2" />
            重复规则
          </h2>

          <div class="form-group">
            <label class="form-label">重复周期</label>
            <div
              v-if="form.frequency === 'weekly' || form.frequency === 'custom'"
              class="space-y-3"
            >
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
                    data-field="weekdays"
                    @focus="handleFieldFocus('weekdays')"
                    @blur="handleFieldBlur('weekdays')"
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
            <p v-if="errors.special_instructions" class="error-text">
              {{ errors.special_instructions }}
            </p>
          </div>
        </div>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <div class="flex items-center justify-end space-x-4">
            <button type="button" @click="goBack" class="btn-secondary">
              取消
            </button>
            <button type="submit" :disabled="loading" class="btn-primary">
              <div
                v-if="loading"
                class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"
              ></div>
              {{ isEdit ? '更新提醒' : '创建提醒' }}
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useSpeech } from '@/composables/useSpeech'
import { useMedicineStore } from '@/stores/medicine'
import { useReminderStore } from '@/stores/reminder'
import { isRequestCancelledError } from '@/utils/api'
import {
  createSubmissionTraceContext,
  createTraceId,
  extractApiValidationErrors,
  logApiErrorEvent,
  logClientTraceEvent,
} from '@/utils/api'
import {
  ArrowLeft,
  Pill,
  Clock,
  Calendar,
  Repeat,
  FileText,
  Plus,
  Minus,
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
const { success: showSuccess, error: showError } = useToast()
const { isSpeechEnabled, isSpeechSupported, speak } = useSpeech()

const loading = ref(false)
const medicineStore = useMedicineStore()
const reminderStore = useReminderStore()
const medicines = computed<Medicine[]>(() => medicineStore.medicines as any)
const noEndDate = ref(false)
const customTimes = ref<string[]>(['09:00'])
const reminderTimes = ref<string[]>(['09:00'])
const selectedWeekDays = ref<number[]>([1]) // 默认选择周一
const assistiveSummaryLines = ref<string[]>([])
const lastAppliedDraftSignature = ref('')

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
  is_active: true,
})

const errors = reactive<Record<string, string>>({})
const allowedDosageUnits = new Set([
  'tablet',
  'capsule',
  'ml',
  'mg',
  'g',
  'drop',
  'spray',
  'patch',
  'injection',
])
const allowedFrequencies = new Set([
  'daily',
  'twice_daily',
  'three_times_daily',
  'four_times_daily',
  'weekly',
  'every_other_day',
  'custom',
])
const allowedMealTimings = new Set([
  'before_meal',
  'with_meal',
  'after_meal',
  'anytime',
  'before_breakfast',
  'after_dinner',
  'before_bed',
])

// 计算属性
const isEdit = computed(() => !!route.params.id)
const today = computed(() => new Date().toISOString().split('T')[0])

const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
const assistiveMissingFields = computed(() => {
  const missing: string[] = []

  if (!form.medicine_id) {
    missing.push('药品')
  }
  if (!form.dosage || Number(form.dosage) <= 0) {
    missing.push('剂量')
  }
  if (!form.start_date) {
    missing.push('开始日期')
  }

  if (form.frequency === 'weekly' || form.frequency === 'custom') {
    if (selectedWeekDays.value.length === 0) {
      missing.push('提醒星期')
    }
  }

  if (form.frequency === 'custom') {
    if (customTimes.value.length === 0) {
      missing.push('提醒时间')
    }
  } else if (!form.reminder_time) {
    missing.push('提醒时间')
  }

  return missing
})
const assistiveGuidanceEnabled = ref(false)
const lastFieldGuidanceKey = ref('')
const lastAssistiveInteractionAt = ref(0)
const assistiveInteractionTick = ref(0)
const FIELD_GUIDANCE_THROTTLE_KEY = 'reminder-form-field-guidance'
const CONTINUOUS_INTERACTION_WINDOW_MS = 4000
const IDLE_REMINDER_DELAY_MS = 12000

const assistiveRequiredFieldCount = computed(() => {
  let total = 4
  if (form.frequency === 'weekly' || form.frequency === 'custom') {
    total += 1
  }
  return total
})

const buildFieldGuidanceKey = () => assistiveMissingFields.value.join('|') || 'completed'

const formatAssistiveFieldLabel = (field: string) => {
  const fieldLabelMap: Record<string, string> = {
    药品: '提醒药品',
    剂量: '用药剂量',
    开始日期: '开始日期',
    提醒星期: '重复星期',
    提醒时间: '提醒时间',
  }
  return fieldLabelMap[field] || field
}

const buildFinalActionGuidance = () => {
  return '提醒表单关键项已经补齐，请检查提醒时间和日期，确认无误后手动提交，不会自动提交。'
}

const markAssistiveInteraction = () => {
  lastAssistiveInteractionAt.value = Date.now()
  assistiveInteractionTick.value += 1
}

const isContinuousInteraction = () => {
  return Date.now() - lastAssistiveInteractionAt.value < CONTINUOUS_INTERACTION_WINDOW_MS
}

const buildFieldCorrectionGuidance = (field: string) => {
  const messageMap: Record<string, string> = {
    medicine_id: '提醒药品还没选好，请再确认。',
    dosage: '用药剂量还没填好，请再确认。',
    dosage_unit: '剂量单位还没选好，请再确认。',
    frequency: '服药频率还没选好，请再确认。',
    reminder_time: '提醒时间还没填好，请再确认。',
    start_date: '开始日期还没选好，请再确认。',
    weekdays: '重复星期还没选好，请再确认。',
  }
  return messageMap[field] || '这个字段还没填好，请再确认。'
}

const formatValidationIssueLabel = (field: string) => {
  const labelMap: Record<string, string> = {
    medicine_id: '提醒药品',
    dosage: '用药剂量',
    dosage_unit: '剂量单位',
    start_date: '开始日期',
    end_date: '结束日期',
    frequency: '服药频率',
    reminder_time: '提醒时间',
    weekdays: '重复星期',
    non_field_errors: '整体内容',
  }
  return labelMap[field] || '填写内容'
}

const normalizeAssistiveValidationMessage = (field: string, message: string) => {
  const normalized = message
    .replace(/^[A-Za-z0-9_]+:\s*/, '')
    .replace('This field is required.', `${formatValidationIssueLabel(field)}还没填。`)
    .replace('This field may not be blank.', `${formatValidationIssueLabel(field)}还没填。`)
    .replace('A valid number is required.', `${formatValidationIssueLabel(field)}需要填写数字。`)
    .trim()

  return normalized || `${formatValidationIssueLabel(field)}还需要再确认。`
}

const getValidationIssueEntries = () =>
  Object.entries(errors).filter(([, message]) => Boolean(message))

const getValidationIssueFields = () => getValidationIssueEntries().map(([field]) => field)

const getValidationIssueDescriptions = () =>
  getValidationIssueEntries().map(([field, message]) =>
    normalizeAssistiveValidationMessage(field, message)
  )

const getFirstValidationIssueField = () => getValidationIssueFields()[0]

const validationPriorityLines = computed(() => {
  const issueDescriptions = getValidationIssueDescriptions()
  if (issueDescriptions.length === 0) {
    return []
  }
  if (issueDescriptions.length === 1) {
    return [`请先处理：${issueDescriptions[0]}`]
  }
  return [
    `请先处理：${issueDescriptions[0]}`,
    `然后再检查：${issueDescriptions.slice(1, 2).join('；')}`,
  ]
})

const buildValidationFailureGuidance = () => {
  const issueDescriptions = getValidationIssueDescriptions()
  if (issueDescriptions.length === 0) {
    return '提醒表单还不能提交，请先检查关键内容。'
  }
  if (issueDescriptions.length === 1) {
    return `提醒表单还不能提交，请先处理：${issueDescriptions[0]}。`
  }
  return `提醒表单还不能提交，请先处理：${issueDescriptions[0]}，然后再检查：${issueDescriptions[1]}。`
}

const focusValidationField = async (field?: string) => {
  await nextTick()
  if (field === 'non_field_errors') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }

  const selector = field ? `[data-field="${field}"]` : '.border-red-500'
  const target =
    document.querySelector<HTMLElement>(selector) ||
    document.querySelector<HTMLElement>('.border-red-500')

  if (!target) {
    return
  }

  target.scrollIntoView({ behavior: 'smooth', block: 'center' })
  target.focus()
}

const applyServerValidationErrors = (
  error: unknown,
  submitSessionId?: string,
  requestId?: string
) => {
  const serverErrors = extractApiValidationErrors(error)
  const mappedEntries = Object.entries(serverErrors)
    .map(([field, message]) => {
      const targetField =
        field === 'medicine'
          ? 'medicine_id'
          : field === 'weekdays'
            ? 'weekdays'
            : field === 'non_field_errors'
              ? 'non_field_errors'
              : field
      const normalizedMessage = normalizeAssistiveValidationMessage(targetField, message)
      if (!normalizedMessage) {
        return null
      }
      return [targetField, normalizedMessage] as const
    })
    .filter((entry): entry is readonly [string, string] => entry !== null)

  if (mappedEntries.length === 0) {
    return false
  }

  Object.keys(errors).forEach(key => delete errors[key])
  mappedEntries.forEach(([field, message]) => {
    errors[field] = message
  })
  logClientTraceEvent(
    'ReminderForm',
    'server_validation_mapped',
    {
      requestId: requestId ?? null,
      submitSessionId: submitSessionId ?? null,
      rawFields: Object.keys(serverErrors),
      mappedFields: Object.keys(errors),
      validationErrors: { ...errors },
    },
    { severity: 'warn' }
  )
  return true
}

const buildNextFieldGuidance = () => {
  const nextField = assistiveMissingFields.value[0]
  const remainingCount = assistiveMissingFields.value.length

  if (!nextField) {
    return buildFinalActionGuidance()
  }

  const fieldMessageMap: Record<string, string> = {
    药品: '请先选择这次要提醒的药品。',
    剂量: '请填写每次要服用多少。',
    开始日期: '请确认从哪一天开始提醒。',
    提醒星期: '请至少选择一个需要重复提醒的星期。',
    提醒时间: '请填写具体提醒时间。',
  }
  const suffix =
    remainingCount > 1 ? ` 之后还需要确认${remainingCount - 1}项。` : ' 这是最后一步，完成后请手动提交。'

  return `${fieldMessageMap[nextField] || `请补充${nextField}。`}${suffix}`
}

const parseMissingFieldsFromKey = (key?: string) => {
  if (!key || key === 'completed') {
    return []
  }
  return key.split('|').filter(Boolean)
}

const parseMissingCountFromKey = (key?: string) => {
  return parseMissingFieldsFromKey(key).length
}

const buildCompletedFieldSummary = (fields: string[]) => {
  if (fields.length === 0) {
    return ''
  }
  const labels = fields.map(formatAssistiveFieldLabel)
  if (fields.length === 1) {
    return `已完成${labels[0]}。`
  }
  if (fields.length === 2) {
    return `已完成${labels[0]}和${labels[1]}。`
  }
  return `已完成${labels.slice(0, -1).join('、')}和${labels[labels.length - 1]}。`
}

const buildProgressGuidance = (previousKey?: string) => {
  const currentMissingCount = assistiveMissingFields.value.length
  const currentCompletedCount =
    assistiveRequiredFieldCount.value - currentMissingCount
  const previousMissingFields = parseMissingFieldsFromKey(previousKey)
  const completedFields = previousMissingFields.filter(
    field => !assistiveMissingFields.value.includes(field)
  )
  const completedFieldSummary = buildCompletedFieldSummary(completedFields)

  if (currentMissingCount === 0) {
    return `${completedFieldSummary}提醒表单关键项已全部完成，共${assistiveRequiredFieldCount.value}项。请检查提醒时间和日期，确认无误后手动提交，不会自动提交。`
  }

  const previousMissingCount = parseMissingCountFromKey(previousKey)
  if (previousKey !== undefined && previousMissingCount > currentMissingCount) {
    return `${completedFieldSummary}已完成${currentCompletedCount}/${assistiveRequiredFieldCount.value}项关键内容。${buildNextFieldGuidance()}`
  }

  return buildNextFieldGuidance()
}

const speakFieldGuidance = (
  text: string,
  options?: {
    priority?: 'low' | 'normal' | 'high'
    interrupt?: boolean
    dedupeWindowMs?: number
    throttleWindowMs?: number
  }
) => {
  speak(text, {
    rate: 0.82,
    category: 'assistant',
    priority: options?.priority ?? 'normal',
    interrupt: options?.interrupt ?? false,
    dedupeWindowMs: options?.dedupeWindowMs ?? 1800,
    maxSegmentLength: 32,
    throttleKey: FIELD_GUIDANCE_THROTTLE_KEY,
    throttleWindowMs: options?.throttleWindowMs ?? 900,
  })
}

const activateFieldGuidance = (
  prefix: string,
  mode: 'prefill' | 'validation' = 'prefill',
  customMessage?: string
) => {
  assistiveGuidanceEnabled.value = true
  lastFieldGuidanceKey.value = buildFieldGuidanceKey()
  markAssistiveInteraction()
  if (!isSpeechEnabled.value || !isSpeechSupported.value) {
    return
  }

  speakFieldGuidance(customMessage || `${prefix}${buildNextFieldGuidance()}`, {
    priority: mode === 'validation' ? 'high' : 'normal',
    interrupt: true,
    dedupeWindowMs: 3000,
    throttleWindowMs: mode === 'validation' ? 0 : 900,
  })
}

const getFieldFocusPrompt = (field: string) => {
  const promptMap: Record<string, string> = {
    medicine_id: '当前是药品选择，请确认这次提醒对应的是哪一种药。',
    dosage: '当前是剂量，请填写每次需要服用多少。',
    dosage_unit: '当前是剂量单位，请确认是片、粒还是毫升。',
    frequency: '当前是服药频率，请先确认每天几次或是否自定义。',
    reminder_time: '当前是提醒时间，请填写实际要提醒的时间点。',
    start_date: '当前是开始日期，请确认从哪一天开始提醒。',
    weekdays: '当前是提醒星期，请勾选需要重复提醒的星期。',
  }

  return promptMap[field] || ''
}

const isFieldCompleted = (field: string) => {
  if (field === 'medicine_id') {
    return !!form.medicine_id
  }
  if (field === 'dosage') {
    return !!form.dosage && Number(form.dosage) > 0
  }
  if (field === 'dosage_unit') {
    return !!form.dosage_unit
  }
  if (field === 'frequency') {
    return !!form.frequency
  }
  if (field === 'reminder_time') {
    return form.frequency === 'custom'
      ? customTimes.value.some(time => /^\d{2}:\d{2}$/.test(time))
      : /^\d{2}:\d{2}$/.test(form.reminder_time)
  }
  if (field === 'start_date') {
    return !!form.start_date
  }
  if (field === 'weekdays') {
    return form.frequency === 'weekly' || form.frequency === 'custom'
      ? selectedWeekDays.value.length > 0
      : true
  }
  return true
}

const handleFieldFocus = (field: string) => {
  markAssistiveInteraction()
  const prompt = getFieldFocusPrompt(field)
  if (!prompt || !isSpeechEnabled.value || !isSpeechSupported.value) {
    return
  }

  speakFieldGuidance(prompt, {
    priority: 'low',
    dedupeWindowMs: 1200,
    throttleWindowMs: 900,
  })
}

const handleFieldBlur = (field: string) => {
  if (!assistiveGuidanceEnabled.value || !isSpeechEnabled.value || !isSpeechSupported.value) {
    return
  }

  markAssistiveInteraction()
  if (isFieldCompleted(field)) {
    return
  }

  speakFieldGuidance(buildFieldCorrectionGuidance(field), {
    priority: 'low',
    interrupt: false,
    dedupeWindowMs: 1800,
    throttleWindowMs: 600,
  })
}

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
    if (isRequestCancelledError(error)) {
      console.log('获取药品列表请求已取消')
      return
    }

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
      if (!reminderStore.error) {
        console.log('获取提醒信息请求已取消')
        return
      }

      showError('获取提醒信息失败')
      goBack()
      return
    }
    Object.assign(form, {
      // 兼容后端返回的联合类型：number | { id: number; ... }
      // 若为对象则取其 id，若为 number 则直接使用该数值
      medicine_id:
        typeof reminder.medicine === 'object'
          ? reminder.medicine.id
          : reminder.medicine,
      title: reminder.title,
      dosage: reminder.dosage,
      dosage_unit: reminder.dosage_unit,
      frequency: reminder.frequency,
      meal_timing: reminder.meal_timing,
      reminder_time: reminder.reminder_time,
      start_date: reminder.start_date,
      end_date: reminder.end_date || '',
      special_instructions: reminder.special_instructions || '',
      is_active: reminder.is_active,
    })

    noEndDate.value = !reminder.end_date

    // 处理提醒时间
    if (reminder.frequency === 'custom' && reminder.custom_times) {
      customTimes.value = reminder.custom_times
    } else {
      updateReminderTimes()
    }

    // 处理周重复
    if ((reminder.frequency === 'weekly' || reminder.frequency === 'custom') && reminder.weekdays) {
      selectedWeekDays.value = Array.from(
        new Set((reminder.weekdays as number[]).map(day => toUiWeekday(Number(day))))
      ).sort((left, right) => left - right)
    }
  } catch (error) {
    if (isRequestCancelledError(error)) {
      console.log('获取提醒信息请求已取消')
      return
    }

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
  if (form.frequency !== 'weekly' && form.frequency !== 'custom') {
    selectedWeekDays.value = [1]
  }
}

const updateReminderTimes = () => {
  const timeCount =
    {
      daily: 1,
      twice_daily: 2,
      three_times_daily: 3,
      four_times_daily: 4,
      weekly: 1,
      every_other_day: 1,
      custom: 0,
    }[form.frequency] ?? 1

  if (timeCount > 0) {
    reminderTimes.value = Array(timeCount)
      .fill('')
      .map((_, index) => {
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

const toUiWeekday = (weekday: number) => {
  if (weekday >= 1 && weekday <= 6) {
    return weekday
  }
  if (weekday === 7) {
    return 0
  }
  return weekday
}

const toBackendWeekday = (weekday: number) => {
  if (weekday >= 1 && weekday <= 6) {
    return weekday
  }
  if (weekday === 0) {
    return 7
  }
  return weekday
}

const getQueryValue = (key: string) => {
  const value = route.query[key]
  return Array.isArray(value) ? value[0] || '' : value || ''
}

const parseTimeList = (raw: string) => {
  return Array.from(
    new Set(
      raw
        .split(',')
        .map(item => item.trim())
        .filter(item => /^\d{2}:\d{2}$/.test(item))
    )
  )
}

const parseWeekdayList = (raw: string) => {
  return Array.from(
    new Set(
      raw
        .split(',')
        .map(item => Number(item.trim()))
        .filter(item => Number.isInteger(item) && item >= 0 && item <= 7)
        .map(toUiWeekday)
    )
  )
}

const findMedicineIdByName = (name: string) => {
  const normalized = name.trim().toLowerCase()
  if (!normalized) {
    return ''
  }

  const exactMatch = medicines.value.find(
    medicine => medicine.name.trim().toLowerCase() === normalized
  )
  if (exactMatch) {
    return exactMatch.id
  }

  const fuzzyMatch = medicines.value.find(medicine =>
    medicine.name.trim().toLowerCase().includes(normalized)
  )
  return fuzzyMatch?.id ?? ''
}

const applyDraftQuery = () => {
  const source = getQueryValue('source')
  if (source && source !== 'page-agent') {
    return
  }

  const medicineId = Number(getQueryValue('medicine_id'))
  const medicineName = getQueryValue('medicine_name')
  const dosage = Number(getQueryValue('dosage'))
  const dosageUnit = getQueryValue('dosage_unit')
  const frequency = getQueryValue('frequency')
  const mealTiming = getQueryValue('meal_timing')
  const reminderTime = getQueryValue('reminder_time')
  const customTimeList = parseTimeList(getQueryValue('custom_times'))
  const weekdayList = parseWeekdayList(getQueryValue('weekdays'))
  const startDate = getQueryValue('start_date')
  const endDate = getQueryValue('end_date')
  const title = getQueryValue('title')
  const specialInstructions = getQueryValue('special_instructions')
  const noEndDateFlag = getQueryValue('no_end_date')

  if (Number.isInteger(medicineId) && medicineId > 0) {
    form.medicine_id = medicineId
  } else if (medicineName) {
    form.medicine_id = findMedicineIdByName(medicineName)
  }

  if (title) {
    form.title = title.slice(0, 80)
  }
  if (!title && medicineName) {
    form.title = `${medicineName}用药提醒`.slice(0, 80)
  }

  if (!Number.isNaN(dosage) && dosage > 0) {
    form.dosage = dosage
  }
  if (allowedDosageUnits.has(dosageUnit)) {
    form.dosage_unit = dosageUnit
  }
  if (allowedFrequencies.has(frequency)) {
    form.frequency = frequency
  }
  if (allowedMealTimings.has(mealTiming)) {
    form.meal_timing = mealTiming
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(startDate)) {
    form.start_date = startDate
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(endDate)) {
    form.end_date = endDate
  }
  if (specialInstructions) {
    form.special_instructions = specialInstructions.slice(0, 200)
  }

  noEndDate.value = noEndDateFlag === '1'

  if (noEndDate.value) {
    form.end_date = ''
  }

  if (form.frequency === 'custom') {
    const nextCustomTimes = customTimeList.length
      ? customTimeList
      : /^\d{2}:\d{2}$/.test(reminderTime)
        ? [reminderTime]
        : []
    if (nextCustomTimes.length > 0) {
      customTimes.value = nextCustomTimes
      form.reminder_time = nextCustomTimes[0]
    }
  } else if (/^\d{2}:\d{2}$/.test(reminderTime)) {
    form.reminder_time = reminderTime
    reminderTimes.value = reminderTimes.value.map((existingTime, index) =>
      index === 0 ? reminderTime : existingTime
    )
  }

  if ((form.frequency === 'weekly' || form.frequency === 'custom') && weekdayList.length > 0) {
    selectedWeekDays.value = weekdayList
  }

  assistiveSummaryLines.value = [
    form.medicine_id
      ? `药品：${medicines.value.find(item => item.id === form.medicine_id)?.name || medicineName || '已选择'}`
      : medicineName
        ? `药品：${medicineName}`
        : '',
    form.dosage ? `剂量：${form.dosage}${form.dosage_unit || ''}` : '',
    form.frequency ? `频率：${form.frequency}` : '',
    form.reminder_time ? `时间：${form.reminder_time}` : '',
    form.start_date ? `开始：${form.start_date}` : '',
  ].filter(Boolean)

  console.log('[ReminderForm] 应用页面助手草稿', {
    medicineId: form.medicine_id,
    frequency: form.frequency,
    reminderTime: form.reminder_time,
    customTimes: customTimes.value,
    weekdays: selectedWeekDays.value,
    source,
  })

  if (
    source === 'page-agent' &&
    (medicineName ||
      form.medicine_id ||
      form.dosage ||
      form.reminder_time ||
      form.special_instructions)
  ) {
    const signature = JSON.stringify({
      medicineId: form.medicine_id,
      dosage: form.dosage,
      frequency: form.frequency,
      reminderTime: form.reminder_time,
      customTimes: customTimes.value,
      weekdays: selectedWeekDays.value,
      startDate: form.start_date,
      endDate: form.end_date,
    })
    if (lastAppliedDraftSignature.value === signature) {
      return
    }
    lastAppliedDraftSignature.value = signature
    showSuccess('已载入页面助手草稿，请确认后再提交')
    activateFieldGuidance('已帮你预填提醒表单。', 'prefill')
  }
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
  const submitTrace = createSubmissionTraceContext('ReminderForm')
  const requestId = createTraceId('request')
  logClientTraceEvent(
    'ReminderForm',
    'submit_start',
    {
      requestId,
      action: isEdit.value ? 'update' : 'create',
      reminderId: isEdit.value ? Number(route.params.id) : null,
      frequency: form.frequency || null,
    },
    { traceContext: submitTrace }
  )

  if (!validateForm()) {
    const validationGuidance = buildValidationFailureGuidance()
    const firstValidationField = getFirstValidationIssueField()
    logClientTraceEvent(
      'ReminderForm',
      'client_validation_failed',
      {
        requestId,
        validationErrors: { ...errors },
        validationGuidance,
        firstValidationField,
      },
      { traceContext: submitTrace, severity: 'warn' }
    )
    showError(validationGuidance)
    activateFieldGuidance('', 'validation', validationGuidance)
    logClientTraceEvent(
      'ReminderForm',
      'focus_validation_field',
      {
        requestId,
        field: firstValidationField,
        source: 'client-validation',
      },
      { traceContext: submitTrace, severity: 'warn' }
    )
    await focusValidationField(firstValidationField)
    return
  }

  try {
    loading.value = true

    // 组装提交数据
    const { medicine_id, ...rest } = form
    const submitData: any = {
      ...rest,
      medicine: medicine_id, // 后端期望字段名
      end_date: noEndDate.value ? null : form.end_date || null,
      weekdays:
        form.frequency === 'weekly' || form.frequency === 'custom'
          ? selectedWeekDays.value.map(day => toBackendWeekday(day))
          : [],
      custom_times: form.frequency === 'custom' ? customTimes.value : [],
    }

    console.log('提交数据payload(store):', submitData)
    logClientTraceEvent(
      'ReminderForm',
      'request_dispatch',
      {
        requestId,
        action: isEdit.value ? 'update' : 'create',
        payloadFields: Object.keys(submitData),
        frequency: submitData.frequency ?? null,
      },
      { traceContext: submitTrace }
    )

    if (isEdit.value) {
      await reminderStore.updateReminder(Number(route.params.id), submitData, {
        requestId,
      })
    } else {
      await reminderStore.createReminder(submitData, { requestId })
    }

    logClientTraceEvent(
      'ReminderForm',
      'submit_success',
      {
        requestId,
        action: isEdit.value ? 'update' : 'create',
        reminderId: isEdit.value ? Number(route.params.id) : null,
      },
      { traceContext: submitTrace }
    )
    showSuccess(`提醒${isEdit.value ? '更新' : '创建'}成功`)
    router.push('/reminders')
  } catch (error: any) {
    logApiErrorEvent('ReminderForm', error, {
      action: isEdit.value ? 'update' : 'create',
      form: 'reminder',
      reminderId: isEdit.value ? Number(route.params.id) : null,
      frequency: form.frequency || null,
      submitSessionId: submitTrace.submitSessionId,
      requestId,
    })

    if (applyServerValidationErrors(error, submitTrace.submitSessionId, requestId)) {
      const validationGuidance = buildValidationFailureGuidance()
      const firstValidationField = getFirstValidationIssueField()
      showError(validationGuidance)
      activateFieldGuidance('', 'validation', validationGuidance)
      logClientTraceEvent(
        'ReminderForm',
        'focus_validation_field',
        {
          requestId,
          field: firstValidationField,
          source: 'server-validation',
        },
        { traceContext: submitTrace, severity: 'warn' }
      )
      await focusValidationField(firstValidationField)
      return
    }

    const errorMessage = error?.message || '提交失败'
    logClientTraceEvent(
      'ReminderForm',
      'submit_failed',
      {
        requestId,
        errorMessage,
      },
      { traceContext: submitTrace, severity: 'error' }
    )
    showError(errorMessage)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

// 监听器
watch(
  () => noEndDate.value,
  value => {
    if (value) {
      form.end_date = ''
    }
  }
)

watch(
  () => form.frequency,
  () => {
    onFrequencyChange()
  }
)

watch(
  () => reminderTimes.value[0],
  value => {
    if (value) {
      form.reminder_time = value
    }
  }
)

watch(
  () => route.fullPath,
  () => {
    applyDraftQuery()
  }
)

watch(
  () => assistiveMissingFields.value.join('|'),
  (key, oldKey) => {
    if (!assistiveGuidanceEnabled.value || !key || key === lastFieldGuidanceKey.value) {
      return
    }

    lastFieldGuidanceKey.value = key
    if (!isSpeechEnabled.value || !isSpeechSupported.value) {
      return
    }

    const continuous = isContinuousInteraction()
    markAssistiveInteraction()
    speakFieldGuidance(buildProgressGuidance(oldKey), {
      priority: continuous ? 'low' : 'normal',
      interrupt: !continuous,
      dedupeWindowMs: 2500,
      throttleWindowMs: continuous ? 900 : 500,
    })
  }
)

watch(
  () => [
    assistiveGuidanceEnabled.value,
    isSpeechEnabled.value,
    isSpeechSupported.value,
    assistiveMissingFields.value.join('|'),
    assistiveInteractionTick.value,
  ],
  ([enabled, speechEnabled, speechSupported, key], _oldValue, onCleanup) => {
    if (!enabled || !speechEnabled || !speechSupported || !key) {
      return
    }

    const timer = window.setTimeout(() => {
      if (!assistiveGuidanceEnabled.value || !assistiveMissingFields.value.length) {
        return
      }

      speakFieldGuidance(`先不着急，${buildNextFieldGuidance()}`, {
        priority: 'low',
        interrupt: false,
        dedupeWindowMs: 5000,
        throttleWindowMs: 0,
      })
    }, IDLE_REMINDER_DELAY_MS)

    onCleanup(() => window.clearTimeout(timer))
  }
)

// 生命周期
onMounted(async () => {
  form.start_date = today.value
  await fetchMedicines()

  if (isEdit.value) {
    await fetchReminder(route.params.id as string)
  } else {
    updateReminderTimes()
    applyDraftQuery()
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
