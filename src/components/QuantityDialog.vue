<template>
  <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto">
    <div
      class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0"
    >
      <!-- 背景遮罩 -->
      <div
        class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
        @click="emitClose"
      />

      <!-- 对话框 -->
      <div
        class="inline-block w-full max-w-md p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg"
      >
        <!-- 标题 -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-medium text-gray-900">库存调整</h3>
          <button @click="emitClose" class="text-gray-400 hover:text-gray-600">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <!-- 内容 -->
        <div class="space-y-4">
          <div class="bg-gray-50 p-3 rounded-md text-sm text-gray-700">
            <div>
              药品：<span class="font-medium">{{ medicine?.name || '-' }}</span>
            </div>
            <div class="mt-1">
              当前库存：<span class="font-medium">{{
                medicine?.quantity ?? '-'
              }}</span>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              新的库存数量（将设置为该值，非增量）
            </label>
            <input
              v-model.number="localQuantity"
              type="number"
              min="0"
              :disabled="loading || !medicine"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="请输入非负整数"
            />
            <p v-if="errorMessage" class="mt-1 text-sm text-red-600">
              {{ errorMessage }}
            </p>
          </div>
        </div>

        <!-- 按钮 -->
        <div
          class="flex justify-end space-x-4 pt-6 border-t border-gray-200 mt-6"
        >
          <button
            type="button"
            @click="emitClose"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            :disabled="loading"
          >
            取消
          </button>
          <button
            type="button"
            @click="onSubmit"
            class="px-4 py-2 rounded-lg text-white transition-colors"
            :class="loading ? 'bg-blue-300' : 'bg-blue-600 hover:bg-blue-700'"
            :disabled="loading || !canSubmit"
          >
            {{ loading ? '提交中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useMedicineStore } from '@/stores/medicine'
import type { Medicine } from '@/types/medicine'

// Props 与 emits 定义，需与调用方完全兼容
const props = defineProps<{
  visible: boolean
  medicine: Medicine | null
}>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'success'): void
}>()

// 本地状态
const localQuantity = ref<number>(0)
const loading = ref(false)
const errorMessage = ref('')

// 计算属性：是否可提交
const canSubmit = computed(() => {
  return (
    props.medicine != null &&
    Number.isInteger(localQuantity.value) &&
    localQuantity.value >= 0
  )
})

// 同步初始值为当前库存
watch(
  () => props.medicine,
  med => {
    if (med) {
      localQuantity.value = Number.isFinite(med.quantity as any)
        ? Number(med.quantity)
        : 0
    } else {
      localQuantity.value = 0
    }
    errorMessage.value = ''
  },
  { immediate: true }
)

const medicineStore = useMedicineStore()

/**
 * 提交库存调整（设置为绝对值）
 * 步骤：校验 → 调用 store.updateMedicineQuantity → 触发 success/close 事件
 */
async function onSubmit() {
  console.log('🟡 [QuantityDialog] 提交库存调整: ', {
    id: props.medicine?.id,
    newQuantity: localQuantity.value,
  })
  errorMessage.value = ''

  if (!props.medicine) {
    errorMessage.value = '未选择药品'
    return
  }
  if (!Number.isInteger(localQuantity.value) || localQuantity.value < 0) {
    errorMessage.value = '请输入有效的非负整数'
    return
  }

  try {
    loading.value = true
    const id = props.medicine.id
    await medicineStore.updateMedicineQuantity(id, localQuantity.value)
    console.log('🟢 [QuantityDialog] 更新成功')
    emit('success')
    emitClose()
  } catch (err: any) {
    console.error('🔴 [QuantityDialog] 更新失败: ', err)
    errorMessage.value = err?.message || '更新库存失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

/**
 * 关闭对话框
 */
function emitClose() {
  emit('close')
}
</script>

<style scoped>
/* 可按需微调样式，保持与 MedicineForm 对话框一致的观感 */
</style>
