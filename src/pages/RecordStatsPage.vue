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
              <p class="text-2xl font-bold text-gray-900">{{ stats?.total_records ?? 0 }}</p>
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
              <p class="text-2xl font-bold text-gray-900">{{ stats?.adherence_rate ?? 0 }}%</p>
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
              <p class="text-2xl font-bold text-gray-900">{{ stats?.avg_effectiveness ?? 0 }}/10</p>
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
              <p class="text-2xl font-bold text-gray-900">{{ stats?.missed_count ?? 0 }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 药品库存统计 -->
      <div class="bg-white rounded-lg shadow p-6 mb-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">药品库存统计</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div 
            v-for="medicine in medicineInventory" 
            :key="medicine.id"
            class="border rounded-lg p-4"
            :class="{
              'border-red-300 bg-red-50': medicine.quantity <= 5,
              'border-yellow-300 bg-yellow-50': medicine.quantity > 5 && medicine.quantity <= 10,
              'border-green-300 bg-green-50': medicine.quantity > 10
            }"
          >
            <div class="flex items-center justify-between mb-2">
              <h4 class="font-medium text-gray-900 truncate">{{ medicine.name }}</h4>
              <span 
                class="px-2 py-1 text-xs rounded-full"
                :class="{
                  'bg-red-100 text-red-800': medicine.quantity <= 5,
                  'bg-yellow-100 text-yellow-800': medicine.quantity > 5 && medicine.quantity <= 10,
                  'bg-green-100 text-green-800': medicine.quantity > 10
                }"
              >
                {{ medicine.quantity <= 5 ? '急需补充' : medicine.quantity <= 10 ? '库存偏低' : '库存充足' }}
              </span>
            </div>
            <div class="space-y-1 text-sm text-gray-600">
              <p><span class="font-medium">剩余数量:</span> {{ medicine.quantity }}</p>
              <p v-if="medicine.specification"><span class="font-medium">规格:</span> {{ medicine.specification }}</p>
              <p v-if="medicine.expiry_date"><span class="font-medium">有效期:</span> {{ formatDate(medicine.expiry_date) }}</p>
              <p v-if="medicine.manufacturer"><span class="font-medium">厂商:</span> {{ medicine.manufacturer }}</p>
            </div>
            <div v-if="medicine.quantity <= 10" class="mt-3">
              <div class="flex items-center text-sm">
                <i class="fas fa-exclamation-triangle text-orange-500 mr-1"></i>
                <span class="text-orange-600">建议及时补充库存</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 库存统计摘要 -->
        <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex items-center">
              <i class="fas fa-exclamation-circle text-red-500 mr-2"></i>
              <div>
                <p class="text-sm font-medium text-red-800">急需补充</p>
                <p class="text-lg font-bold text-red-900">{{ lowStockCount }} 种</p>
              </div>
            </div>
          </div>
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div class="flex items-center">
              <i class="fas fa-exclamation-triangle text-yellow-500 mr-2"></i>
              <div>
                <p class="text-sm font-medium text-yellow-800">库存偏低</p>
                <p class="text-lg font-bold text-yellow-900">{{ mediumStockCount }} 种</p>
              </div>
            </div>
          </div>
          <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <div class="flex items-center">
              <i class="fas fa-check-circle text-green-500 mr-2"></i>
              <div>
                <p class="text-sm font-medium text-green-800">库存充足</p>
                <p class="text-lg font-bold text-green-900">{{ goodStockCount }} 种</p>
              </div>
            </div>
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
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">副作用次数</th>
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
                  {{ item.avg_effectiveness ?? '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ item.side_effects_count ?? 0 }}
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
import { ref, computed, onMounted } from 'vue'
import { useRecordStore } from '../stores/record'
import { useMedicineStore } from '../stores/medicine'

// 状态管理
const recordStore = useRecordStore()
const medicineStore = useMedicineStore()
const { loading, statistics, fetchStatistics } = recordStore
const { fetchMedicines } = medicineStore
const medicines = computed(() => medicineStore.medicines)

// 修复：使用正确的统计数据属性名
const stats = computed(() => statistics.value)

// 响应式数据
const dateRange = ref({
  start: '',
  end: ''
})
const selectedMedicine = ref('')
const medicineStats = ref<any[]>([])
const medicineInventory = ref<any[]>([])

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
      medicine: selectedMedicine.value ?? undefined
    }
    
    // 并行加载统计数据和药品库存数据
    await Promise.all([
      fetchStatistics(params),
      loadMedicineInventory()
    ])
    
    // 生成药品统计数据
    generateMedicineStats()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 加载药品库存数据
const loadMedicineInventory = async () => {
  try {
    // 获取所有药品数据（包含库存信息）
    await fetchMedicines()
    medicineInventory.value = medicines.value.map(medicine => ({
      ...medicine,
      // 确保数量字段存在
      quantity: medicine.quantity ?? 0
    }))
  } catch (error) {
    console.error('加载药品库存数据失败:', error)
    medicineInventory.value = []
  }
}

// 库存统计计算属性
const lowStockCount = computed(() => {
  return medicineInventory.value.filter(medicine => medicine.quantity <= 5).length
})

const mediumStockCount = computed(() => {
  return medicineInventory.value.filter(medicine => medicine.quantity > 5 && medicine.quantity <= 10).length
})

const goodStockCount = computed(() => {
  return medicineInventory.value.filter(medicine => medicine.quantity > 10).length
})

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 生成药品统计数据
const generateMedicineStats = () => {
  if (!stats.value?.medicine_stats) {
    medicineStats.value = []
    return
  }
  
  medicineStats.value = stats.value?.medicine_stats?.map((item: any) => {
    const medicine = medicines.value.find(m => m.id === item.medicine)
    return {
      ...item,
      medicine_name: medicine?.name || '未知药品'
    }
  }) ?? []
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


</script>