<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
  >
    <div
      class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
    >
      <!-- 详情标题 -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-bold text-gray-900">用药记录详情</h2>
        <div class="flex space-x-2">
          <button
            @click="$emit('edit', record)"
            class="text-blue-600 hover:text-blue-800 transition-colors"
            title="编辑记录"
          >
            <i class="fas fa-edit text-lg"></i>
          </button>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>
      </div>

      <!-- 记录内容 -->
      <div v-if="record" class="space-y-6">
        <!-- 基本信息 -->
        <div class="bg-gray-50 rounded-lg p-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">基本信息</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-600"
                >药品名称</label
              >
              <p class="text-gray-900 font-medium">
                {{ medicineInfo?.name || '未知药品' }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600"
                >规格</label
              >
              <p class="text-gray-900">
                {{ medicineInfo?.specification || '-' }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600"
                >服药时间</label
              >
              <p class="text-gray-900">{{ formatDateTime(record.taken_at) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600"
                >记录时间</label
              >
              <p class="text-gray-900">
                {{ formatDateTime(record.created_at) }}
              </p>
            </div>
          </div>
        </div>

        <!-- 服药详情 -->
        <div class="bg-gray-50 rounded-lg p-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">服药详情</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-600"
                >服药数量</label
              >
              <p class="text-gray-900">{{ record.quantity_taken }} 片</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600"
                >服药方式</label
              >
              <p class="text-gray-900">
                {{ getAdministrationMethodLabel(record.administration_method) }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600"
                >服药状态</label
              >
              <div class="flex items-center space-x-2">
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="getStatusClass(record.status)"
                >
                  {{ getStatusLabel(record.status) }}
                </span>
                <span v-if="record.is_on_time" class="text-green-600 text-sm">
                  <i class="fas fa-check-circle"></i> 按时服用
                </span>
                <span v-else class="text-orange-600 text-sm">
                  <i class="fas fa-clock"></i> 延迟服用
                </span>
              </div>
            </div>
            <div v-if="record.delay_minutes">
              <label class="block text-sm font-medium text-gray-600"
                >延迟时间</label
              >
              <p class="text-gray-900">{{ record.delay_minutes }} 分钟</p>
            </div>
          </div>
        </div>

        <!-- 评分信息 -->
        <div
          v-if="record.symptom_score || record.effectiveness_score"
          class="bg-gray-50 rounded-lg p-4"
        >
          <h3 class="text-lg font-semibold text-gray-900 mb-4">评分信息</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-if="record.symptom_score">
              <label class="block text-sm font-medium text-gray-600"
                >症状评分</label
              >
              <div class="flex items-center space-x-2">
                <div class="flex space-x-1">
                  <span
                    v-for="i in 10"
                    :key="i"
                    class="w-3 h-3 rounded-full"
                    :class="
                      i <= record.symptom_score ? 'bg-red-500' : 'bg-gray-200'
                    "
                  ></span>
                </div>
                <span class="text-gray-900 font-medium"
                  >{{ record.symptom_score }}/10</span
                >
              </div>
            </div>
            <div v-if="record.effectiveness_score">
              <label class="block text-sm font-medium text-gray-600"
                >效果评分</label
              >
              <div class="flex items-center space-x-2">
                <div class="flex space-x-1">
                  <span
                    v-for="i in 10"
                    :key="i"
                    class="w-3 h-3 rounded-full"
                    :class="
                      i <= record.effectiveness_score
                        ? 'bg-green-500'
                        : 'bg-gray-200'
                    "
                  ></span>
                </div>
                <span class="text-gray-900 font-medium"
                  >{{ record.effectiveness_score }}/10</span
                >
              </div>
            </div>
          </div>
        </div>

        <!-- 备注信息 -->
        <div
          v-if="record.notes || record.side_effects"
          class="bg-gray-50 rounded-lg p-4"
        >
          <h3 class="text-lg font-semibold text-gray-900 mb-4">备注信息</h3>
          <div class="space-y-4">
            <div v-if="record.notes">
              <label class="block text-sm font-medium text-gray-600 mb-2"
                >备注</label
              >
              <p class="text-gray-900 whitespace-pre-wrap">
                {{ record.notes }}
              </p>
            </div>
            <div v-if="record.side_effects">
              <label class="block text-sm font-medium text-gray-600 mb-2"
                >副作用</label
              >
              <p class="text-gray-900 whitespace-pre-wrap text-red-600">
                {{ record.side_effects }}
              </p>
            </div>
          </div>
        </div>

        <!-- 统计信息 -->
        <div class="bg-gray-50 rounded-lg p-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">统计信息</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-600"
                >依从性评分</label
              >
              <p class="text-gray-900 font-medium">
                {{ record.adherence_score }}%
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600"
                >记录来源</label
              >
              <p class="text-gray-900">{{ getSourceLabel(record.source) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600"
                >时间差</label
              >
              <p class="text-gray-900">{{ getTimeDifference(record) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-else class="flex justify-center items-center py-8">
        <i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i>
      </div>

      <!-- 操作按钮 -->
      <div class="flex justify-end space-x-3 mt-8">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
        >
          关闭
        </button>
        <button
          @click="$emit('edit', record)"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <i class="fas fa-edit mr-2"></i>
          编辑记录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useMedicineStore } from '../stores/medicine'
import {
  ADMINISTRATION_METHOD_OPTIONS,
  MEDICATION_STATUS_OPTIONS,
  RECORD_SOURCE_OPTIONS,
} from '../types/record'
import type { MedicationRecord } from '../types/record'

// Props
interface Props {
  record: MedicationRecord | null
}

const props = defineProps<Props>()

// Emits
defineEmits<{
  close: []
  edit: [record: MedicationRecord]
}>()

// 状态管理
const medicineStore = useMedicineStore()
// 使用 storeToRefs 保持响应式引用，避免 Pinia 的自动解包导致 .value 访问报错
// 重命名为 medicinesRef，避免与潜在的同名数组变量混淆导致类型推断问题
const { medicines: medicinesRef } = storeToRefs(medicineStore)
const { fetchMedicines } = medicineStore

// 计算属性
const medicineInfo = computed(() => {
  if (!props.record) return null
  return medicinesRef.value.find(m => m.id === props.record!.medicine) || null
})

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

// 计算并格式化记录时间与服药时间的差异
const getTimeDifference = (record: MedicationRecord | null) => {
  if (!record) return '-'
  try {
    const taken = new Date(record.taken_at).getTime()
    const created = new Date(record.created_at).getTime()
    if (isNaN(taken) || isNaN(created)) return '-'
    const diffMs = Math.abs(created - taken)
    const totalMinutes = Math.floor(diffMs / 60000)
    const days = Math.floor(totalMinutes / (60 * 24))
    const hours = Math.floor((totalMinutes % (60 * 24)) / 60)
    const minutes = totalMinutes % 60
    const parts: string[] = []
    if (days) parts.push(`${days}天`)
    if (hours) parts.push(`${hours}小时`)
    parts.push(`${minutes}分钟`)
    return parts.join(' ')
  } catch (e) {
    return '-'
  }
}

// 获取服药方式标签
const getAdministrationMethodLabel = (method: string) => {
  const option = ADMINISTRATION_METHOD_OPTIONS.find(opt => opt.value === method)
  return option?.label || method
}

// 获取状态标签
const getStatusLabel = (status: string) => {
  const option = MEDICATION_STATUS_OPTIONS.find(opt => opt.value === status)
  return option?.label || status
}

// 获取状态样式类
const getStatusClass = (status: string) => {
  const statusClasses = {
    taken: 'bg-green-100 text-green-800',
    missed: 'bg-red-100 text-red-800',
    delayed: 'bg-yellow-100 text-yellow-800',
    partial: 'bg-orange-100 text-orange-800',
  }
  return (
    statusClasses[status as keyof typeof statusClasses] ||
    'bg-gray-100 text-gray-800'
  )
}

// 获取记录来源标签
const getSourceLabel = (source: string) => {
  const option = RECORD_SOURCE_OPTIONS.find(opt => opt.value === source)
  return option?.label || source
}

// 生命周期
onMounted(async () => {
  // 确保药品数据已加载
  if (medicinesRef.value.length === 0) {
    await fetchMedicines()
  }
})
</script>

<style scoped>
/* 自定义样式 */
.whitespace-pre-wrap {
  white-space: pre-wrap;
}
</style>
