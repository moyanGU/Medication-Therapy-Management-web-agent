<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
  >
    <div
      class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
    >
      <!-- 表单标题 -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-bold text-gray-900">
          {{ isEdit ? '编辑用药记录' : '添加用药记录' }}
        </h2>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <i class="fas fa-times text-xl"></i>
        </button>
      </div>

      <!-- 表单内容 -->
      <form @submit.prevent="handleSubmit">
        <div class="space-y-6">
          <!-- 药品选择 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              药品 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.medicine"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              :class="{ 'border-red-500': errors.medicine }"
              required
            >
              <option value="">请选择药品</option>
              <option
                v-for="medicine in medicinesRef"
                :key="medicine.id"
                :value="medicine.id"
              >
                {{ medicine.name }} - {{ medicine.specification }}
              </option>
            </select>
            <p v-if="errors.medicine" class="mt-1 text-sm text-red-600">
              {{ errors.medicine }}
            </p>
          </div>

          <!-- 服药时间 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                服药日期 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="takenDate"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                :class="{ 'border-red-500': errors.taken_at }"
                required
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                服药时间 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="takenTime"
                type="time"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                :class="{ 'border-red-500': errors.taken_at }"
                required
              />
            </div>
          </div>
          <p v-if="errors.taken_at" class="mt-1 text-sm text-red-600">
            {{ errors.taken_at }}
          </p>

          <!-- 服药数量和方式 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                服药数量 <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="form.quantity_taken"
                type="number"
                min="1"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                :class="{ 'border-red-500': errors.quantity_taken }"
                required
              />
              <p v-if="errors.quantity_taken" class="mt-1 text-sm text-red-600">
                {{ errors.quantity_taken }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                服药方式 <span class="text-red-500">*</span>
              </label>
              <select
                v-model="form.administration_method"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                :class="{ 'border-red-500': errors.administration_method }"
                required
              >
                <option
                  v-for="option in administrationOptions"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
              <p
                v-if="errors.administration_method"
                class="mt-1 text-sm text-red-600"
              >
                {{ errors.administration_method }}
              </p>
            </div>
          </div>

          <!-- 服药状态 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              服药状态 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.status"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              :class="{ 'border-red-500': errors.status }"
              required
            >
              <option
                v-for="option in statusOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
            <p v-if="errors.status" class="mt-1 text-sm text-red-600">
              {{ errors.status }}
            </p>
          </div>

          <!-- 延迟时间（仅当状态为延迟时显示） -->
          <div v-if="form.status === 'delayed'">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              延迟时间（分钟）
            </label>
            <input
              v-model.number="form.delay_minutes"
              type="number"
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              :class="{ 'border-red-500': errors.delay_minutes }"
              placeholder="延迟了多少分钟"
            />
            <p v-if="errors.delay_minutes" class="mt-1 text-sm text-red-600">
              {{ errors.delay_minutes }}
            </p>
          </div>

          <!-- 评分 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                症状评分（1-10分）
              </label>
              <input
                v-model.number="form.symptom_score"
                type="number"
                min="1"
                max="10"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                :class="{ 'border-red-500': errors.symptom_score }"
                placeholder="服药前症状严重程度"
              />
              <p v-if="errors.symptom_score" class="mt-1 text-sm text-red-600">
                {{ errors.symptom_score }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                效果评分（1-10分）
              </label>
              <input
                v-model.number="form.effectiveness_score"
                type="number"
                min="1"
                max="10"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                :class="{ 'border-red-500': errors.effectiveness_score }"
                placeholder="服药后效果评分"
              />
              <p
                v-if="errors.effectiveness_score"
                class="mt-1 text-sm text-red-600"
              >
                {{ errors.effectiveness_score }}
              </p>
            </div>
          </div>

          <!-- 备注 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              备注
            </label>
            <textarea
              v-model="form.notes"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              :class="{ 'border-red-500': errors.notes }"
              placeholder="记录服药时的感受、注意事项等"
            ></textarea>
            <p v-if="errors.notes" class="mt-1 text-sm text-red-600">
              {{ errors.notes }}
            </p>
          </div>

          <!-- 副作用 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              副作用
            </label>
            <textarea
              v-model="form.side_effects"
              rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              :class="{ 'border-red-500': errors.side_effects }"
              placeholder="记录服药后出现的副作用"
            ></textarea>
            <p v-if="errors.side_effects" class="mt-1 text-sm text-red-600">
              {{ errors.side_effects }}
            </p>
          </div>
        </div>

        <!-- 表单按钮 -->
        <div class="flex justify-end space-x-3 mt-8">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            取消
          </button>
          <button
            type="submit"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            :disabled="loading"
          >
            <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>
            {{ isEdit ? '更新' : '创建' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRecordStore } from '../stores/record'
import { useMedicineStore } from '../stores/medicine'
import {
  ADMINISTRATION_METHOD_OPTIONS,
  MEDICATION_STATUS_OPTIONS,
  AdministrationMethod,
  MedicationStatus,
} from '../types/record'
import type { MedicationRecord, MedicationRecordForm } from '../types/record'

// Props
interface Props {
  record?: MedicationRecord | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  close: []
  success: []
}>()

// 状态管理
const recordStore = useRecordStore()
const medicineStore = useMedicineStore()
const { loading, createRecord, updateRecord } = recordStore
const { fetchMedicines } = medicineStore
// 使用 storeToRefs 获取 Ref，并重命名为 medicinesRef，避免与可能的同名数组混淆导致类型推断问题
const { medicines: medicinesRef } = storeToRefs(medicineStore)

// 表单状态
const isEdit = computed(() => !!props.record)

// 表单数据
const form = ref<MedicationRecordForm>({
  medicine: '',
  taken_at: '',
  quantity_taken: 1,
  administration_method: AdministrationMethod.ORAL,
  status: MedicationStatus.TAKEN,
  notes: '',
  symptom_score: undefined,
  effectiveness_score: undefined,
  side_effects: '',
  delay_minutes: undefined,
})

// 日期时间分离
const takenDate = ref('')
const takenTime = ref('')

// 表单验证错误
const errors = ref<Record<string, string>>({})

// 选项数据
const administrationOptions = ADMINISTRATION_METHOD_OPTIONS
const statusOptions = MEDICATION_STATUS_OPTIONS

// 监听日期时间变化，合并为完整的datetime
watch([takenDate, takenTime], ([date, time]) => {
  if (date && time) {
    form.value.taken_at = `${date}T${time}:00`
  }
})

// 初始化表单数据
const initForm = () => {
  if (props.record) {
    // 编辑模式，填充现有数据
    const record = props.record
    form.value = {
      medicine: record.medicine,
      taken_at: record.taken_at,
      quantity_taken: record.quantity_taken,
      administration_method: record.administration_method,
      status: record.status,
      notes: record.notes || '',
      symptom_score: record.symptom_score,
      effectiveness_score: record.effectiveness_score,
      side_effects: record.side_effects || '',
      delay_minutes: record.delay_minutes,
    }

    // 分离日期和时间
    const datetime = new Date(record.taken_at)
    takenDate.value = datetime.toISOString().split('T')[0]
    takenTime.value = datetime.toTimeString().slice(0, 5)
  } else {
    // 新建模式，设置默认值
    const now = new Date()
    takenDate.value = now.toISOString().split('T')[0]
    takenTime.value = now.toTimeString().slice(0, 5)
    form.value.taken_at = `${takenDate.value}T${takenTime.value}:00`
  }
}

// 表单验证
const validateForm = () => {
  errors.value = {}

  if (
    !form.value.medicine ||
    form.value.medicine === '' ||
    form.value.medicine === 0
  ) {
    errors.value.medicine = '请选择药品'
  }

  if (!form.value.taken_at) {
    errors.value.taken_at = '请选择服药时间'
  } else {
    const takenAt = new Date(form.value.taken_at)
    const now = new Date()
    if (takenAt > now) {
      errors.value.taken_at = '服药时间不能是未来时间'
    }
  }

  if (!form.value.quantity_taken || form.value.quantity_taken <= 0) {
    errors.value.quantity_taken = '服药数量必须大于0'
  }

  if (!form.value.administration_method) {
    errors.value.administration_method = '请选择服药方式'
  }

  if (!form.value.status) {
    errors.value.status = '请选择服药状态'
  }

  if (form.value.status === 'delayed' && !form.value.delay_minutes) {
    errors.value.delay_minutes = '延迟服用状态必须提供延迟时间'
  }

  if (
    form.value.symptom_score &&
    (form.value.symptom_score < 1 || form.value.symptom_score > 10)
  ) {
    errors.value.symptom_score = '症状评分必须在1-10之间'
  }

  if (
    form.value.effectiveness_score &&
    (form.value.effectiveness_score < 1 || form.value.effectiveness_score > 10)
  ) {
    errors.value.effectiveness_score = '效果评分必须在1-10之间'
  }

  return Object.keys(errors.value).length === 0
}

// 提交表单
const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  try {
    // 清理空值
    const submitData = { ...form.value }
    if (!submitData.notes) delete submitData.notes
    if (!submitData.side_effects) delete submitData.side_effects
    if (!submitData.symptom_score) delete submitData.symptom_score
    if (!submitData.effectiveness_score) delete submitData.effectiveness_score
    if (!submitData.delay_minutes) delete submitData.delay_minutes

    // 确保medicine字段是数字类型
    if (typeof submitData.medicine === 'string') {
      const parsed = Number(submitData.medicine)
      if (Number.isNaN(parsed) || parsed <= 0) {
        console.error('🔴 [RecordForm] medicine 解析失败:', submitData.medicine)
        errors.value.medicine = '请选择药品'
        return
      }
      submitData.medicine = parsed
    }

    console.log('提交数据:', submitData)

    if (isEdit.value && props.record) {
      await updateRecord(props.record.id, submitData)
      console.log('🟢 [RecordForm] 更新记录成功，触发success事件')
    } else {
      const result = await createRecord(submitData)
      console.log('🟢 [RecordForm] 创建记录成功，结果:', result)
      console.log('🟢 [RecordForm] 触发success事件')
    }

    emit('success')
  } catch (error: any) {
    console.error('🔴 [RecordForm] 提交失败:', error)
    // 规范化错误对象：优先使用结构化 errors 字段；其次 message；最后使用兜底提示
    if (error?.errors && typeof error.errors === 'object') {
      errors.value = error.errors
    } else if (error?.message) {
      errors.value = { general: error.message }
    } else {
      errors.value = { general: '提交失败，请稍后重试' }
    }
  }
}

// 生命周期
onMounted(async () => {
  console.log('🔵 [RecordForm] onMounted - 开始加载药品列表')
  console.log('🔵 [RecordForm] 当前药品列表:', medicinesRef.value)

  // 加载药品列表
  if (!medicinesRef.value || medicinesRef.value.length === 0) {
    console.log('🔵 [RecordForm] 药品列表为空，开始获取药品列表')
    await fetchMedicines()
    console.log('🟢 [RecordForm] 药品列表获取完成:', medicinesRef.value)
  } else {
    console.log('🟢 [RecordForm] 药品列表已存在，无需重新获取')
  }

  // 初始化表单
  initForm()
  console.log('🟢 [RecordForm] 表单初始化完成')
})
</script>
