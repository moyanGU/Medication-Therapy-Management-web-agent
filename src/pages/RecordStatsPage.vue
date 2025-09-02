<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">用药统计分析</h1>
        <p class="mt-2 text-gray-600">查看您的用药趋势和统计数据</p>
      </div>

      <!-- 时间范围选择 -->
      <div class="bg-white rounded-lg shadow p-6 mb-8">
        <div class="flex flex-wrap items-center gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">开始日期</label>
            <input
              v-model="dateRange.start"
              type="date"
              class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">结束日期</label>
            <input
              v-model="dateRange.end"
              type="date"
              class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">药品筛选</label>
            <select
              v-model="selectedMedicine"
              class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部药品</option>
              <option
                v-for="medicine in medicines"
                :key="medicine.id"
                :value="medicine.id"
              >
                {{ medicine.name }}
              </option>
            </select>
          </div>
          <div class="flex items-end">
            <button
              @click="loadData"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              :disabled="loading"
            >
              <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>
              更新数据
            </button>
          </div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <i class="fas fa-pills text-blue-600"></i>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">总服药次数</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats?.total_records || 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <i class="fas fa-check-circle text-green-600"></i>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">按时服药率</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats?.adherence_rate || 0 }}%</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                <i class="fas fa-star text-yellow-600"></i>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">平均效果评分</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats?.avg_effectiveness || 0 }}/10</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                <i class="fas fa-exclamation-triangle text-red-600"></i>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">漏服次数</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats?.missed_count || 0 }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- 服药趋势图 -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">服药趋势</h3>
          <div class="h-80">
            <canvas ref="trendChart" class="w-full h-full"></canvas>
          </div>
        </div>

        <!-- 服药状态分布 -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">服药状态分布</h3>
          <div class="h-80">
            <canvas ref="statusChart" class="w-full h-full"></canvas>
          </div>
        </div>
      </div>

      <!-- 药品统计表格 -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">药品统计详情</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  药品名称
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  服药次数
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  按时率
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  平均效果
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  副作用次数
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="item in medicineStats" :key="item.medicine_name">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ item.medicine_name }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ item.total_records }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="item.adherence_rate >= 80 ? 'bg-green-100 text-green-800' : 
                             item.adherence_rate >= 60 ? 'bg-yellow-100 text-yellow-800' : 
                             'bg-red-100 text-red-800'"
                  >
                    {{ item.adherence_rate }}%
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ item.avg_effectiveness || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ item.side_effects_count || 0 }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRecordStore } from '../stores/record'
import { useMedicineStore } from '../stores/medicine'
import Chart from 'chart.js/auto'
import type { Chart as ChartType } from 'chart.js'

// 状态管理
const recordStore = useRecordStore()
const medicineStore = useMedicineStore()
const { loading, stats, trends, fetchStats, fetchTrends } = recordStore
const { fetchMedicines } = medicineStore
const medicines = computed(() => medicineStore.medicines)

// 响应式数据
const dateRange = ref({
  start: '',
  end: ''
})
const selectedMedicine = ref('')
const medicineStats = ref<any[]>([])

// 图表引用
const trendChart = ref<HTMLCanvasElement>()
const statusChart = ref<HTMLCanvasElement>()
let trendChartInstance: ChartType | null = null
let statusChartInstance: ChartType | null = null

// 初始化日期范围（最近30天）
const initDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  
  dateRange.value.end = end.toISOString().split('T')[0]
  dateRange.value.start = start.toISOString().split('T')[0]
}

// 加载数据
const loadData = async () => {
  try {
    const params = {
      start_date: dateRange.value.start,
      end_date: dateRange.value.end,
      medicine: selectedMedicine.value || undefined
    }
    
    // 并行加载统计数据和趋势数据
    await Promise.all([
      fetchStats(params),
      fetchTrends(params)
    ])
    
    // 更新图表
    await nextTick()
    updateCharts()
    
    // 生成药品统计数据
    generateMedicineStats()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 更新图表
const updateCharts = () => {
  updateTrendChart()
  updateStatusChart()
}

// 更新趋势图表
const updateTrendChart = () => {
  if (!trendChart.value || !trends.value?.length) return
  
  // 销毁现有图表
  if (trendChartInstance) {
    trendChartInstance.destroy()
  }
  
  const ctx = trendChart.value.getContext('2d')
  if (!ctx) return
  
  trendChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: trends.value.map(item => item.date),
      datasets: [
        {
          label: '服药次数',
          data: trends.value.map(item => item.total_records),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.1
        },
        {
          label: '按时服药次数',
          data: trends.value.map(item => item.on_time_records),
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          tension: 0.1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      },
      plugins: {
        legend: {
          position: 'top'
        }
      }
    }
  })
}

// 更新状态分布图表
const updateStatusChart = () => {
  if (!statusChart.value || !stats.value) return
  
  // 销毁现有图表
  if (statusChartInstance) {
    statusChartInstance.destroy()
  }
  
  const ctx = statusChart.value.getContext('2d')
  if (!ctx) return
  
  const statusData = [
    { label: '按时服药', value: stats.value.on_time_count || 0, color: '#22c55e' },
    { label: '延迟服药', value: stats.value.delayed_count || 0, color: '#f59e0b' },
    { label: '漏服', value: stats.value.missed_count || 0, color: '#ef4444' },
    { label: '部分服药', value: stats.value.partial_count || 0, color: '#f97316' }
  ].filter(item => item.value > 0)
  
  statusChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: statusData.map(item => item.label),
      datasets: [{
        data: statusData.map(item => item.value),
        backgroundColor: statusData.map(item => item.color),
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  })
}

// 生成药品统计数据
const generateMedicineStats = () => {
  if (!stats.value?.medicine_stats) {
    medicineStats.value = []
    return
  }
  
  medicineStats.value = stats.value.medicine_stats.map((item: any) => {
    const medicine = medicines.value.find(m => m.id === item.medicine)
    return {
      ...item,
      medicine_name: medicine?.name || '未知药品'
    }
  })
}

// 生命周期
onMounted(async () => {
  // 初始化日期范围
  initDateRange()
  
  // 加载药品列表
  if (medicines.value.length === 0) {
    await fetchMedicines()
  }
  
  // 加载统计数据
  await loadData()
})

// 组件卸载时清理图表
const cleanup = () => {
  if (trendChartInstance) {
    trendChartInstance.destroy()
    trendChartInstance = null
  }
  if (statusChartInstance) {
    statusChartInstance.destroy()
    statusChartInstance = null
  }
}

// 监听组件卸载
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(cleanup)
</script>