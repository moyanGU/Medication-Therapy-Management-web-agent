<template>
  <MedicineFormView
    :visible="props.visible"
    :medicine="props.medicine"
    :form-data="formData"
    :errors="errors"
    :loading="loading"
    :image-preview-url="imagePreviewUrl"
    :assistive-summary-lines="assistiveSummaryLines"
    :assistive-missing-fields="assistiveMissingFields"
    :validation-priority-lines="validationPriorityLines"
    @close="emit('close')"
    @submit="handleSubmit"
    @upload-image="handleImageUpload"
    @remove-image="removeImage"
    @image-error="handleImageError"
    @focus-field="handleFieldFocus"
    @blur-field="handleFieldBlur"
  />
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, computed, nextTick } from 'vue'
import { useMedicineStore } from '@/stores/medicine'
import { useSpeech } from '@/composables/useSpeech'
import type {
  Medicine,
  MedicineCreateData,
  MedicineUpdateData,
} from '@/types/medicine'
import { toast } from 'vue-sonner'
import {
  createSubmissionTraceContext,
  createTraceId,
  extractApiValidationErrors,
  logClientTraceEvent,
  logApiErrorEvent,
  resolveMediaUrl,
} from '@/utils/api'
import MedicineFormView from '@/components/MedicineFormView.vue'

// Props
interface Props {
  visible: boolean
  medicine?: Medicine | null
  draftQuery?: Record<string, string>
}

const props = withDefaults(defineProps<Props>(), {
  medicine: null,
  draftQuery: () => ({}),
})

// Emits
const emit = defineEmits<{
  close: []
  success: []
}>()

// Store
const medicineStore = useMedicineStore()
const { isSpeechEnabled, isSpeechSupported, speak } = useSpeech()

// 响应式数据
const loading = ref(false)
const errors = ref<Record<string, string>>({})
const assistiveSummaryLines = ref<string[]>([])
const lastAppliedDraftSignature = ref('')
const assistiveGuidanceEnabled = ref(false)
const lastFieldGuidanceKey = ref('')
const lastAssistiveInteractionAt = ref(0)
const assistiveInteractionTick = ref(0)
const FIELD_GUIDANCE_THROTTLE_KEY = 'medicine-form-field-guidance'
const CONTINUOUS_INTERACTION_WINDOW_MS = 4000
const IDLE_REMINDER_DELAY_MS = 12000

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
  is_prescription: false,
})

const assistiveMissingFields = computed(() => {
  const missing: string[] = []

  if (!formData.name.trim()) {
    missing.push('药品名称')
  }
  if (!formData.medicine_type) {
    missing.push('药品类型')
  }
  if (formData.quantity < 0) {
    missing.push('库存数量')
  }

  return missing
})

const assistiveRequiredFieldCount = computed(() => 3)

const buildFieldGuidanceKey = () => assistiveMissingFields.value.join('|') || 'completed'

const formatAssistiveFieldLabel = (field: string) => {
  const fieldLabelMap: Record<string, string> = {
    药品名称: '药名',
    药品类型: '药品类型',
    库存数量: '库存数量',
  }
  return fieldLabelMap[field] || field
}

const buildFinalActionGuidance = () => {
  return '药品表单关键项已经补齐，请检查一遍信息，确认无误后手动保存，不会自动保存。'
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
    name: '药名还没填好，请再看一眼。',
    medicine_type: '药品类型还没选好，请再确认。',
    quantity: '库存数量还没填好，请再确认。',
  }
  return messageMap[field] || '这个字段还没填好，请再确认。'
}

const formatValidationIssueLabel = (field: string) => {
  const labelMap: Record<string, string> = {
    name: '药名',
    medicine_type: '药品类型',
    quantity: '库存数量',
    purchase_price: '采购价格',
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
  Object.entries(errors.value).filter(([, message]) => Boolean(message))

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
    return '药品表单还不能保存，请先检查关键内容。'
  }
  if (issueDescriptions.length === 1) {
    return `药品表单还不能保存，请先处理：${issueDescriptions[0]}。`
  }
  return `药品表单还不能保存，请先处理：${issueDescriptions[0]}，然后再检查：${issueDescriptions[1]}。`
}

const focusValidationField = async (field?: string) => {
  await nextTick()
  if (field === 'non_field_errors') {
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
      const targetField = field === 'non_field_errors' ? 'non_field_errors' : field
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

  errors.value = Object.fromEntries(mappedEntries)
  logClientTraceEvent(
    'MedicineForm',
    'server_validation_mapped',
    {
      requestId: requestId ?? null,
      submitSessionId: submitSessionId ?? null,
      rawFields: Object.keys(serverErrors),
      mappedFields: Object.keys(errors.value),
      validationErrors: errors.value,
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
    药品名称: '请先输入药名，方便后面查找和提醒。',
    药品类型: '请选药品类型，比如片剂、胶囊或冲剂。',
    库存数量: '请填写库存数量，不能是负数。',
  }
  const suffix =
    remainingCount > 1 ? ` 之后还需要确认${remainingCount - 1}项。` : ' 这是最后一步，完成后请手动保存。'

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
    return `${completedFieldSummary}药品表单关键项已全部完成，共${assistiveRequiredFieldCount.value}项。请检查一遍信息，确认无误后手动保存，不会自动保存。`
  }

  const previousMissingCount = parseMissingCountFromKey(previousKey)
  if (previousKey !== undefined && previousMissingCount > currentMissingCount) {
    return `${completedFieldSummary}已完成${currentCompletedCount}/${assistiveRequiredFieldCount.value}项关键内容。${buildNextFieldGuidance()}`
  }

  return buildNextFieldGuidance()
}

const getFieldFocusPrompt = (field: string) => {
  const promptMap: Record<string, string> = {
    name: '当前是药品名称，请输入清晰的药品名，方便后续提醒和库存管理。',
    medicine_type: '当前是药品类型，请选择片剂、胶囊或其他类型。',
    quantity: '当前是库存数量，请填写现有库存，不能是负数。',
  }

  return promptMap[field] || ''
}

const isFieldCompleted = (field: string) => {
  if (field === 'name') {
    return !!formData.name.trim()
  }
  if (field === 'medicine_type') {
    return !!formData.medicine_type
  }
  if (field === 'quantity') {
    return formData.quantity >= 0
  }
  return true
}

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
    is_prescription: false,
  })
  errors.value = {}
  assistiveSummaryLines.value = []
  lastAppliedDraftSignature.value = ''
  assistiveGuidanceEnabled.value = false
  lastFieldGuidanceKey.value = ''
}

// 监听medicine变化，用于编辑模式
watch(
  () => props.medicine,
  newMedicine => {
    if (newMedicine) {
      // 编辑模式，填充表单数据
      Object.assign(formData, {
        name: newMedicine.name || '',
        specification: newMedicine.specification || '',
        manufacturer: newMedicine.manufacturer || '',
        medicine_type: newMedicine.medicine_type || 'tablet',
        quantity: newMedicine.quantity ?? 0,
        purchase_price: newMedicine.purchase_price,
        purchase_date: newMedicine.purchase_date || '',
        expiry_date: newMedicine.expiry_date || '',
        batch_number: newMedicine.batch_number || '',
        storage_conditions: newMedicine.storage_conditions || '',
        description: newMedicine.description || '',
        image_path: newMedicine.image_path || '', // 使用image_path字段
        is_prescription: newMedicine.is_prescription ?? false,
      })
    } else {
      // 添加模式，重置表单
      resetForm()
    }
  },
  { immediate: true }
)

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

const applyDraftQuery = () => {
  if (props.medicine) {
    assistiveSummaryLines.value = []
    return
  }

  const source = props.draftQuery?.source
  if (source && source !== 'page-agent') {
    return
  }

  const name = String(props.draftQuery?.name || '')
  const medicineType = String(props.draftQuery?.medicine_type || '')
  const quantity = String(props.draftQuery?.quantity || '')
  const specification = String(props.draftQuery?.specification || '')
  const manufacturer = String(props.draftQuery?.manufacturer || '')
  const purchasePrice = String(props.draftQuery?.purchase_price || '')
  const purchaseDate = String(props.draftQuery?.purchase_date || '')
  const expiryDate = String(props.draftQuery?.expiry_date || '')
  const batchNumber = String(props.draftQuery?.batch_number || '')
  const storageConditions = String(props.draftQuery?.storage_conditions || '')
  const description = String(props.draftQuery?.description || '')
  const isPrescription = String(props.draftQuery?.is_prescription || '')

  const typeSet = new Set([
    'tablet',
    'capsule',
    'liquid',
    'injection',
    'ointment',
    'drops',
    'other',
  ])

  if (name) {
    formData.name = name.slice(0, 80)
  }
  if (typeSet.has(medicineType)) {
    formData.medicine_type = medicineType
  }
  if (quantity) {
    const parsedQuantity = Number(quantity)
    if (!Number.isNaN(parsedQuantity)) {
      formData.quantity = parsedQuantity
    }
  }
  if (specification) {
    formData.specification = specification.slice(0, 80)
  }
  if (manufacturer) {
    formData.manufacturer = manufacturer.slice(0, 80)
  }
  if (purchasePrice) {
    const parsedPrice = Number(purchasePrice)
    if (!Number.isNaN(parsedPrice)) {
      formData.purchase_price = parsedPrice
    }
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(purchaseDate)) {
    formData.purchase_date = purchaseDate
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(expiryDate)) {
    formData.expiry_date = expiryDate
  }
  if (batchNumber) {
    formData.batch_number = batchNumber.slice(0, 40)
  }
  if (storageConditions) {
    formData.storage_conditions = storageConditions.slice(0, 120)
  }
  if (description) {
    formData.description = description.slice(0, 200)
  }
  if (isPrescription === '1') {
    formData.is_prescription = true
  }
  if (isPrescription === '0') {
    formData.is_prescription = false
  }

  const typeLabels: Record<string, string> = {
    tablet: '片剂',
    capsule: '胶囊',
    liquid: '液体',
    injection: '注射剂',
    ointment: '软膏',
    drops: '滴剂',
    other: '其他',
  }

  assistiveSummaryLines.value = [
    formData.name ? `药品名称：${formData.name}` : '',
    formData.medicine_type
      ? `药品类型：${typeLabels[formData.medicine_type] || formData.medicine_type}`
      : '',
    Number.isFinite(formData.quantity) ? `库存数量：${formData.quantity}` : '',
    formData.specification ? `规格：${formData.specification}` : '',
    formData.expiry_date ? `有效期：${formData.expiry_date}` : '',
  ].filter(Boolean)

  if (
    source === 'page-agent' &&
    (formData.name ||
      formData.quantity > 0 ||
      formData.specification ||
      formData.manufacturer)
  ) {
    const signature = JSON.stringify({
      name: formData.name,
      medicineType: formData.medicine_type,
      quantity: formData.quantity,
      specification: formData.specification,
      manufacturer: formData.manufacturer,
      purchasePrice: formData.purchase_price,
      purchaseDate: formData.purchase_date,
      expiryDate: formData.expiry_date,
      batchNumber: formData.batch_number,
      storageConditions: formData.storage_conditions,
      isPrescription: formData.is_prescription,
    })
    if (signature === lastAppliedDraftSignature.value) {
      return
    }
    lastAppliedDraftSignature.value = signature
    console.log('[MedicineForm] 应用页面助手草稿', {
      name: formData.name,
      medicineType: formData.medicine_type,
      quantity: formData.quantity,
      manufacturer: formData.manufacturer,
      expiryDate: formData.expiry_date,
    })
    toast.success('已载入页面助手草稿，请确认后再保存')
    activateFieldGuidance('已帮你预填药品表单。', 'prefill')
  }
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
  const submitTrace = createSubmissionTraceContext('MedicineForm')
  const requestId = createTraceId('request')
  logClientTraceEvent(
    'MedicineForm',
    'submit_start',
    {
      requestId,
      action: props.medicine ? 'update' : 'create',
      isEditMode: !!props.medicine,
      tokenExists: !!localStorage.getItem('access_token'),
    },
    { traceContext: submitTrace }
  )

  const validationResult = validateForm()
  if (!validationResult) {
    const validationGuidance = buildValidationFailureGuidance()
    const firstValidationField = getFirstValidationIssueField()
    logClientTraceEvent(
      'MedicineForm',
      'client_validation_failed',
      {
        requestId,
        validationErrors: errors.value,
        validationGuidance,
        firstValidationField,
      },
      { traceContext: submitTrace, severity: 'warn' }
    )
    toast.error(validationGuidance)
    activateFieldGuidance('', 'validation', validationGuidance)
    logClientTraceEvent(
      'MedicineForm',
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
    console.log(
      '🔵 [MedicineForm] Fields included:',
      Object.keys(cleanFormData)
    )
    logClientTraceEvent(
      'MedicineForm',
      'request_dispatch',
      {
        requestId,
        action: props.medicine ? 'update' : 'create',
        payloadFields: Object.keys(cleanFormData),
      },
      { traceContext: submitTrace }
    )

    if (props.medicine) {
      // 编辑模式
      console.log('🔵 [MedicineForm] Updating medicine:', props.medicine.id)
      const updateData: MedicineUpdateData = cleanFormData

      await medicineStore.updateMedicine(props.medicine.id, updateData, {
        requestId,
      })
      console.log('🟢 [MedicineForm] Medicine updated successfully')
      logClientTraceEvent(
        'MedicineForm',
        'submit_success',
        {
          requestId,
          action: 'update',
          medicineId: props.medicine.id,
        },
        { traceContext: submitTrace }
      )
      toast.success('药品更新成功')
    } else {
      // 添加模式
      console.log('🔵 [MedicineForm] Creating new medicine')

      await medicineStore.createMedicine(cleanFormData, { requestId })
      console.log('🟢 [MedicineForm] Medicine created successfully')
      logClientTraceEvent(
        'MedicineForm',
        'submit_success',
        {
          requestId,
          action: 'create',
        },
        { traceContext: submitTrace }
      )
      toast.success('药品添加成功')
    }

    emit('success')
  } catch (error: any) {
    logApiErrorEvent('MedicineForm', error, {
      action: props.medicine?.id ? 'update' : 'create',
      form: 'medicine',
      medicineId: props.medicine?.id ?? null,
      submitSessionId: submitTrace.submitSessionId,
      requestId,
    })

    if (applyServerValidationErrors(error, submitTrace.submitSessionId, requestId)) {
      const validationGuidance = buildValidationFailureGuidance()
      const firstValidationField = getFirstValidationIssueField()
      toast.error(validationGuidance)
      activateFieldGuidance('', 'validation', validationGuidance)
      logClientTraceEvent(
        'MedicineForm',
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

    // 统一错误提示，ApiClient 抛出的为 ApiError
    const errorMessage = error?.message || '保存失败，请重试'
    logClientTraceEvent(
      'MedicineForm',
      'submit_failed',
      {
        requestId,
        errorMessage,
      },
      { traceContext: submitTrace, severity: 'error' }
    )
    toast.error(errorMessage)
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
  input.onchange = async e => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (file) {
      try {
        console.log('🔵 [MedicineForm] Starting image upload:', file.name)
        toast.info('正在上传图片...')

        // 调用上传API
        const { uploadApi } = await import('@/api/upload')
        const response = await uploadApi.uploadMedicineImage(file)
        console.log('🟢 [MedicineForm] 图片上传响应:', response)
        const payload = ((response as any)?.data?.data ?? response?.data ?? {}) as any
        const imagePath = payload?.image_path
        if (response?.success && typeof imagePath === 'string' && imagePath.trim()) {
          formData.image_path = imagePath
          toast.success('图片上传成功')
        } else {
          console.error(
            '🔴 [MedicineForm] Expected image_path in response.data, got:',
            response
          )
          toast.error(response?.message || '图片上传失败：缺少图片路径')
        }
      } catch (error: any) {
        console.error('🔴 [MedicineForm] Image upload failed:', error)
        const errorMessage =
          typeof error?.message === 'string' && error.message.trim()
            ? error.message.trim()
            : '图片上传失败，请重试'
        toast.error(errorMessage)
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
  return resolveMediaUrl(imagePath)
}

// 处理图片加载错误
const handleImageError = () => {
  formData.image_path = ''
  toast.error('图片加载失败，请重新上传')
}

const imagePreviewUrl = computed(() =>
  getImagePreviewUrl(formData.image_path)
)

// 组件挂载时设置默认采购日期
onMounted(() => {
  console.log('=== MedicineForm Component Mounted ===')
  console.log('Props medicine:', props.medicine)
  console.log('Initial form data:', formData)

  if (!props.medicine && !formData.purchase_date) {
    formData.purchase_date = new Date().toISOString().split('T')[0]
  }

  applyDraftQuery()

  console.log('=== Component Mount Complete ===')
})

watch(
  () => props.visible,
  v => {
    console.log('[MedicineForm] visible changed:', v)
    if (v && !props.medicine) {
      resetForm()
      // 默认采购日期
      if (!formData.purchase_date) {
        formData.purchase_date = new Date().toISOString().split('T')[0]
      }
      applyDraftQuery()
      return
    }

    if (!v) {
      assistiveGuidanceEnabled.value = false
      lastFieldGuidanceKey.value = ''
    }
  }
)

watch(
  () => props.draftQuery,
  () => {
    if (props.visible) {
      applyDraftQuery()
    }
  },
  { deep: true }
)

watch(
  () => assistiveMissingFields.value.join('|'),
  (key, oldKey) => {
    if (
      !assistiveGuidanceEnabled.value ||
      !props.visible ||
      !key ||
      key === lastFieldGuidanceKey.value
    ) {
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
    props.visible,
    isSpeechEnabled.value,
    isSpeechSupported.value,
    assistiveMissingFields.value.join('|'),
    assistiveInteractionTick.value,
  ],
  ([enabled, visible, speechEnabled, speechSupported, key], _oldValue, onCleanup) => {
    if (!enabled || !visible || !speechEnabled || !speechSupported || !key) {
      return
    }

    const timer = window.setTimeout(() => {
      if (!assistiveGuidanceEnabled.value || !props.visible || !assistiveMissingFields.value.length) {
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
</script>
