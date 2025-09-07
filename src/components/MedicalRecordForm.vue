<template>
  <div v-if="visible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-bold text-gray-900">
          {{ isEdit ? '编辑病历' : '添加病历' }}
        </h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <X class="w-6 h-6" />
        </button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              医院名称 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.hospital"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              科室 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.department"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              医生姓名 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.doctor_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              就诊日期 <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.visit_date"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              主诉 <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="form.chief_complaint"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              诊断结果 <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="form.diagnosis"
              rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              治疗方案 <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="form.treatment_plan"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            ></textarea>
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="isSubmitting"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md disabled:opacity-50"
          >
            {{ isSubmitting ? '保存中...' : (isEdit ? '更新' : '保存') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { useMedicalRecordStore } from '@/stores/medicalRecords'
import { toast } from 'vue-sonner'
import { X } from 'lucide-vue-next'

interface Props {
  visible: boolean
  record?: any
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  record: null
})

const emit = defineEmits<{
  close: []
  success: []
}>()

const medicalRecordsStore = useMedicalRecordStore()
const isSubmitting = ref(false)

const form = reactive({
  hospital: '',
  department: '',
  doctor_name: '',
  visit_date: '',
  visit_type: 'outpatient',
  urgency_level: 'medium',
  chief_complaint: '',
  present_illness: '',
  diagnosis: '',
  treatment_plan: '',
  total_cost: 0,
  satisfaction_score: 5,
  status: 'active',
  notes: ''
})

const isEdit = computed(() => !!props.record)

watch(() => props.record, (newRecord) => {
  if (newRecord) {
    Object.assign(form, {
      hospital: newRecord.hospital || '',
      department: newRecord.department || '',
      doctor_name: newRecord.doctor_name || '',
      visit_date: newRecord.visit_date || '',
      visit_type: newRecord.visit_type || 'outpatient',
      urgency_level: newRecord.urgency_level || 'medium',
      chief_complaint: newRecord.chief_complaint || '',
      present_illness: newRecord.present_illness || '',
      diagnosis: newRecord.diagnosis || '',
      treatment_plan: newRecord.treatment_plan || '',
      total_cost: newRecord.total_cost ?? 0,
      satisfaction_score: newRecord.satisfaction_score ?? 5,
      status: newRecord.status || 'active',
      notes: newRecord.notes || ''
    })
  } else {
    Object.assign(form, {
      hospital: '',
      department: '',
      doctor_name: '',
      visit_date: '',
      visit_type: 'outpatient',
      urgency_level: 'medium',
      chief_complaint: '',
      present_illness: '',
      diagnosis: '',
      treatment_plan: '',
      total_cost: 0,
      satisfaction_score: 5,
      status: 'active',
      notes: ''
    })
  }
}, { immediate: true })

const handleSubmit = async () => {
  try {
    isSubmitting.value = true

    if (isEdit.value) {
      await medicalRecordsStore.updateRecord(props.record!.id, form)
    } else {
      await medicalRecordsStore.createRecord(form)
    }

    // 成功即触发事件与提示
    emit('success')
    toast.success(isEdit.value ? '更新成功' : '保存成功')
  } catch (err: unknown) {
    console.error('Error saving medical record:', err)
    const message = err instanceof Error ? err.message : '保存失败'
    toast.error(message)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
/* 样式 */
</style>