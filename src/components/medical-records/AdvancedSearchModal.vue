<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 overflow-y-auto"
    aria-labelledby="modal-title"
    role="dialog"
    aria-modal="true"
  >
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- 背景遮罩 -->
      <div
        class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
        @click="closeModal"
      ></div>

      <!-- 模态框内容 -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <div class="w-full">
              <!-- 标题 -->
              <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  高级搜索
                </h3>
                <button
                  @click="closeModal"
                  class="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon class="h-6 w-6" />
                </button>
              </div>

              <!-- 搜索表单 -->
              <form @submit.prevent="handleSearch" class="space-y-6">
                <!-- 基础搜索 -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      关键词搜索
                    </label>
                    <input
                      v-model="searchForm.keyword"
                      type="text"
                      placeholder="搜索医院、科室、医生、诊断等"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      医院名称
                    </label>
                    <input
                      v-model="searchForm.hospital"
                      type="text"
                      placeholder="输入医院名称"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                  </div>
                </div>

                <!-- 时间范围 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    就诊时间范围
                  </label>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">开始日期</label>
                      <input
                        v-model="searchForm.date_from"
                        type="date"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      >
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">结束日期</label>
                      <input
                        v-model="searchForm.date_to"
                        type="date"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      >
                    </div>
                  </div>
                </div>

                <!-- 医疗信息 -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      科室
                    </label>
                    <input
                      v-model="searchForm.department"
                      type="text"
                      placeholder="输入科室名称"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      医生姓名
                    </label>
                    <input
                      v-model="searchForm.doctor"
                      type="text"
                      placeholder="输入医生姓名"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                  </div>
                </div>

                <!-- 诊断和疾病 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    诊断或疾病
                  </label>
                  <input
                    v-model="searchForm.diagnosis"
                    type="text"
                    placeholder="输入诊断结果或疾病名称"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                </div>

                <!-- 分类筛选 -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      就诊类型
                    </label>
                    <select
                      v-model="searchForm.visit_type"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">全部类型</option>
                      <option v-for="option in VISIT_TYPE_OPTIONS" :key="option.value" :value="option.value">
                        {{ option.label }}
                      </option>
                    </select>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      就医状态
                    </label>
                    <select
                      v-model="searchForm.status"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">全部状态</option>
                      <option v-for="option in STATUS_OPTIONS" :key="option.value" :value="option.value">
                        {{ option.label }}
                      </option>
                    </select>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      紧急程度
                    </label>
                    <select
                      v-model="searchForm.urgency"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">全部程度</option>
                      <option v-for="option in URGENCY_OPTIONS" :key="option.value" :value="option.value">
                        {{ option.label }}
                      </option>
                    </select>
                  </div>
                </div>

                <!-- 费用范围 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    费用范围（元）
                  </label>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">最低费用</label>
                      <input
                        v-model.number="searchForm.cost_min"
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder="0.00"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      >
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">最高费用</label>
                      <input
                        v-model.number="searchForm.cost_max"
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder="不限"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      >
                    </div>
                  </div>
                </div>

                <!-- 其他筛选条件 -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      满意度评分（最低）
                    </label>
                    <select
                      v-model.number="searchForm.satisfaction_min"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">不限</option>
                      <option :value="1">1分及以上</option>
                      <option :value="2">2分及以上</option>
                      <option :value="3">3分及以上</option>
                      <option :value="4">4分及以上</option>
                      <option :value="5">5分</option>
                    </select>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      复诊安排
                    </label>
                    <select
                      v-model="searchForm.has_follow_up"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">全部</option>
                      <option value="true">有复诊安排</option>
                      <option value="false">无复诊安排</option>
                    </select>
                  </div>
                </div>

                <!-- 排序方式 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    排序方式
                  </label>
                  <select
                    v-model="searchForm.ordering"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option v-for="option in SORT_OPTIONS" :key="option.value" :value="option.value">
                      {{ option.label }}
                    </option>
                  </select>
                </div>
              </form>
            </div>
          </div>
        </div>
        
        <!-- 底部按钮 -->
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button
            @click="handleSearch"
            type="button"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
          >
            搜索
          </button>
          <button
            @click="resetForm"
            type="button"
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
          >
            重置
          </button>
          <button
            @click="closeModal"
            type="button"
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm"
          >
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import {
  VISIT_TYPE_OPTIONS,
  STATUS_OPTIONS,
  URGENCY_OPTIONS,
  SORT_OPTIONS,
  type MedicalRecordSearchParams
} from '@/types/medicalRecord'

// Props
interface Props {
  show: boolean
}

const props = defineProps<Props>()

// Emits
interface Emits {
  (e: 'update:show', value: boolean): void
  (e: 'search', params: MedicalRecordSearchParams): void
}

const emit = defineEmits<Emits>()

// 搜索表单数据
const searchForm = reactive<MedicalRecordSearchParams>({
  keyword: '',
  date_from: '',
  date_to: '',
  hospital: '',
  department: '',
  doctor: '',
  diagnosis: '',
  visit_type: '',
  status: '',
  urgency: '',
  cost_min: undefined,
  cost_max: undefined,
  satisfaction_min: undefined,
  has_follow_up: undefined,
  ordering: '-visit_date'
})

// 方法
const closeModal = () => {
  emit('update:show', false)
}

const handleSearch = () => {
  // 过滤掉空值
  const params: MedicalRecordSearchParams = {}
  
  Object.keys(searchForm).forEach(key => {
    const value = searchForm[key as keyof MedicalRecordSearchParams]
    if (value !== '' && value !== undefined && value !== null) {
      params[key as keyof MedicalRecordSearchParams] = value as any
    }
  })
  
  emit('search', params)
}

const resetForm = () => {
  Object.assign(searchForm, {
    keyword: '',
    date_from: '',
    date_to: '',
    hospital: '',
    department: '',
    doctor: '',
    diagnosis: '',
    visit_type: '',
    status: '',
    urgency: '',
    cost_min: undefined,
    cost_max: undefined,
    satisfaction_min: undefined,
    has_follow_up: undefined,
    ordering: '-visit_date'
  })
}

// 监听show变化，重置表单
watch(() => props.show, (newShow) => {
  if (newShow) {
    resetForm()
  }
})
</script>