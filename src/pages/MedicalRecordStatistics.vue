<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页面头部 -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">病历统计</h1>
              <p class="mt-1 text-sm text-gray-500">查看您的就医统计数据和健康趋势</p>
            </div>
            <div class="flex items-center space-x-3">
              <select
                v-model="selectedPeriod"
                @change="handlePeriodChange"
                class="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="month">近一个月</option>
                <option value="quarter">近三个月</option>
                <option value="year">近一年</option>
                <option value="all">全部时间</option>
              </select>
              <button
                @click="refreshData"
                class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <RotateCcw class="-ml-1 mr-2 h-4 w-4" />
                刷新
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <span class="ml-2 text-gray-600">加载中...</span>
    </div>

    <!-- 统计内容 -->
    <div v-else class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 概览卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-sm border p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <Calendar class="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">总就诊次数</p>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.total_visits || 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm border p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <Building class="w-5 h-5 text-green-600" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">就诊医院数</p>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.unique_hospitals || 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm border p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                <DollarSign class="w-5 h-5 text-yellow-600" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">总费用</p>
              <p class="text-2xl font-bold text-gray-900">¥{{ (statistics.total_cost || 0).toLocaleString() }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm border p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                <RotateCcw class="w-5 h-5 text-red-600" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">待复诊</p>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.follow_up_due || 0 }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- 就诊趋势图 -->
        <div class="bg-white rounded-lg shadow-sm border">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">就诊趋势</h3>
            <p class="text-sm text-gray-500">按月统计的就诊次数变化</p>
          </div>
          <div class="p-6">
            <div v-if="visitTrendData.length === 0" class="text-center py-8 text-gray-500">
              暂无数据
            </div>
            <div v-else class="h-64">
              <!-- 这里可以集成图表库，如 Chart.js 或 ECharts -->
              <div class="space-y-3">
                <div
                  v-for="item in visitTrendData"
                  :key="item.month"
                  class="flex items-center justify-between"
                >
                  <span class="text-sm text-gray-600">{{ item.month }}</span>
                  <div class="flex items-center space-x-2">
                    <div class="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        class="bg-blue-600 h-2 rounded-full"
                        :style="{ width: `${(item.count / maxVisitCount) * 100}%` }"
                      ></div>
                    </div>
                    <span class="text-sm font-medium text-gray-900 w-8">{{ item.count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 科室分布 -->
        <div class="bg-white rounded-lg shadow-sm border">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">科室分布</h3>
            <p class="text-sm text-gray-500">各科室就诊次数统计</p>
          </div>
          <div class="p-6">
            <div v-if="departmentData.length === 0" class="text-center py-8 text-gray-500">
              暂无数据
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="item in departmentData"
                :key="item.department"
                class="flex items-center justify-between"
              >
                <span class="text-sm text-gray-900">{{ item.department }}</span>
                <div class="flex items-center space-x-2">
                  <div class="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-green-600 h-2 rounded-full"
                      :style="{ width: `${(item.count / maxDepartmentCount) * 100}%` }"
                    ></div>
                  </div>
                  <span class="text-sm font-medium text-gray-900 w-8">{{ item.count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 疾病分布 -->
        <div class="bg-white rounded-lg shadow-sm border">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">疾病分布</h3>
            <p class="text-sm text-gray-500">常见疾病诊断统计</p>
          </div>
          <div class="p-6">
            <div v-if="diseaseData.length === 0" class="text-center py-8 text-gray-500">
              暂无数据
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="item in diseaseData"
                :key="item.diagnosis"
                class="flex items-center justify-between"
              >
                <span class="text-sm text-gray-900 truncate flex-1 mr-2">{{ item.diagnosis }}</span>
                <div class="flex items-center space-x-2">
                  <div class="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-purple-600 h-2 rounded-full"
                      :style="{ width: `${(item.count / maxDiseaseCount) * 100}%` }"
                    ></div>
                  </div>
                  <span class="text-sm font-medium text-gray-900 w-8">{{ item.count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 费用分析 -->
        <div class="bg-white rounded-lg shadow-sm border">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">费用分析</h3>
            <p class="text-sm text-gray-500">医疗费用统计和趋势</p>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">平均单次费用</span>
                <span class="text-lg font-semibold text-gray-900">
                  ¥{{ averageCost.toLocaleString() }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">最高单次费用</span>
                <span class="text-lg font-semibold text-red-600">
                  ¥{{ (statistics.max_cost || 0).toLocaleString() }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">最低单次费用</span>
                <span class="text-lg font-semibold text-green-600">
                  ¥{{ (statistics.min_cost || 0).toLocaleString() }}
                </span>
              </div>
              <div class="pt-4 border-t border-gray-200">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm text-gray-600">医保报销比例</span>
                  <span class="text-lg font-semibold text-blue-600">
                    {{ insuranceRate.toFixed(1) }}%
                  </span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full"
                    :style="{ width: `${insuranceRate}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 医院分布 -->
      <div class="mt-8 bg-white rounded-lg shadow-sm border">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">医院分布</h3>
          <p class="text-sm text-gray-500">各医院就诊次数和费用统计</p>
        </div>
        <div class="p-6">
          <div v-if="hospitalData.length === 0" class="text-center py-8 text-gray-500">
            暂无数据
          </div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    医院名称
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    就诊次数
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    总费用
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    平均费用
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    最近就诊
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="hospital in hospitalData" :key="hospital.hospital">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {{ hospital.hospital }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ hospital.visit_count }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ¥{{ hospital.total_cost.toLocaleString() }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ¥{{ hospital.average_cost.toLocaleString() }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(hospital.last_visit) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 健康指标 -->
      <div class="mt-8 bg-white rounded-lg shadow-sm border">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">健康指标</h3>
          <p class="text-sm text-gray-500">基于就诊记录的健康状况分析</p>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- 就诊频率 -->
            <div class="text-center">
              <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Calendar class="w-8 h-8 text-blue-600" />
              </div>
              <h4 class="text-lg font-medium text-gray-900 mb-1">就诊频率</h4>
              <p class="text-2xl font-bold text-blue-600 mb-2">{{ visitFrequency }}</p>
              <p class="text-sm text-gray-500">次/月</p>
            </div>

            <!-- 平均满意度 -->
            <div class="text-center">
              <div class="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <BarChart3 class="w-8 h-8 text-yellow-600" />
              </div>
              <h4 class="text-lg font-medium text-gray-900 mb-1">平均满意度</h4>
              <p class="text-2xl font-bold text-yellow-600 mb-2">{{ averageSatisfaction.toFixed(1) }}</p>
              <p class="text-sm text-gray-500">分 (满分5分)</p>
            </div>

            <!-- 症状改善率 -->
            <div class="text-center">
              <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <FileText class="w-8 h-8 text-green-600" />
              </div>
              <h4 class="text-lg font-medium text-gray-900 mb-1">症状改善率</h4>
              <p class="text-2xl font-bold text-green-600 mb-2">{{ improvementRate.toFixed(1) }}%</p>
              <p class="text-sm text-gray-500">基于症状评分</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMedicalRecordStore } from '@/stores/medicalRecords'
import {
  Calendar,
  BarChart3,
  FileText,
  DollarSign,
  Building,
  Users,
  RotateCcw
} from 'lucide-vue-next'
import type { MedicalRecordStatistics } from '@/types/medicalRecord'

const medicalRecordStore = useMedicalRecordStore()

// 响应式数据
const loading = ref(false)
const selectedPeriod = ref('year')
const statistics = ref<MedicalRecordStatistics>({
  total_visits: 0,
  unique_hospitals: 0,
  unique_departments: 0,
  total_cost: 0,
  average_cost: 0,
  max_cost: 0,
  min_cost: 0,
  insurance_coverage: 0,
  follow_up_due: 0,
  monthly_visits: [],
  department_distribution: [],
  cost_trend: []
})

// 模拟数据
const visitTrendData = ref([
  { month: '2024-01', count: 2 },
  { month: '2024-02', count: 1 },
  { month: '2024-03', count: 3 },
  { month: '2024-04', count: 2 },
  { month: '2024-05', count: 4 },
  { month: '2024-06', count: 1 }
])

const departmentData = ref([
  { department: '内科', count: 5 },
  { department: '外科', count: 3 },
  { department: '儿科', count: 2 },
  { department: '妇科', count: 2 },
  { department: '眼科', count: 1 }
])

const diseaseData = ref([
  { diagnosis: '感冒', count: 4 },
  { diagnosis: '胃炎', count: 3 },
  { diagnosis: '高血压', count: 2 },
  { diagnosis: '糖尿病', count: 2 },
  { diagnosis: '关节炎', count: 1 }
])

const hospitalData = ref([
  {
    hospital: '北京协和医院',
    visit_count: 5,
    total_cost: 2500,
    average_cost: 500,
    last_visit: '2024-06-15'
  },
  {
    hospital: '北京大学第一医院',
    visit_count: 3,
    total_cost: 1800,
    average_cost: 600,
    last_visit: '2024-05-20'
  },
  {
    hospital: '清华大学附属医院',
    visit_count: 2,
    total_cost: 1200,
    average_cost: 600,
    last_visit: '2024-04-10'
  }
])

// 计算属性
const maxVisitCount = computed(() => {
  return Math.max(...visitTrendData.value.map(item => item.count), 1)
})

const maxDepartmentCount = computed(() => {
  return Math.max(...departmentData.value.map(item => item.count), 1)
})

const maxDiseaseCount = computed(() => {
  return Math.max(...diseaseData.value.map(item => item.count), 1)
})

const averageCost = computed(() => {
  if (statistics.value.total_visits === 0) return 0
  return Math.round(statistics.value.total_cost / statistics.value.total_visits)
})

const insuranceRate = computed(() => {
  if (statistics.value.total_cost === 0) return 0
  return (statistics.value.insurance_coverage / statistics.value.total_cost) * 100
})

const visitFrequency = computed(() => {
  // 假设统计期间为12个月
  return (statistics.value.total_visits / 12).toFixed(1)
})

const averageSatisfaction = computed(() => {
  // 模拟平均满意度
  return 4.2
})

const improvementRate = computed(() => {
  // 模拟症状改善率
  return 78.5
})

// 方法
const loadStatistics = async () => {
  try {
    loading.value = true
    const data = await medicalRecordStore.fetchStatistics(selectedPeriod.value)
    statistics.value = data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handlePeriodChange = () => {
  loadStatistics()
}

const refreshData = () => {
  loadStatistics()
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadStatistics()
})
</script>