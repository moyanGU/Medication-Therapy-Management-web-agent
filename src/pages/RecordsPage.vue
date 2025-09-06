<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题和操作按钮 -->
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">用药记录</h1>
          <p class="text-gray-600 mt-1">管理和查看您的用药历史记录</p>
        </div>
        <div class="flex space-x-3">
          <router-link
            to="/records/stats"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <i class="fas fa-chart-bar mr-2"></i>
            药量统计
          </router-link>
          <button
            @click="exportRecords"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            :disabled="loading"
          >
            <i class="fas fa-download mr-2"></i>
            导出记录
          </button>
          <button
            @click="showCreateForm = true"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <i class="fas fa-plus mr-2"></i>
            添加记录
          </button>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6" v-if="statistics">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-blue-100 text-blue-600">
              <i class="fas fa-pills text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">总记录数</p>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.total_records }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-green-100 text-green-600">
              <i class="fas fa-check-circle text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">依从性</p>
              <p class="text-2xl font-bold text-gray-900">{{ statistics.adherence_rate }}%</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-orange-100 text-orange-600">
              <i class="fas fa-capsules text-xl"></i>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">当日用药种类</p>
              <p class="text-2xl font-bold text-gray-900">{{ todayMedicineTypes }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- 搜索框 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">搜索</label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索药品名称、备注..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="debouncedSearch"
            />
          </div>
          
          <!-- 状态筛选 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">状态</label>
            <select
              v-model="filters.status"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="applyFilters"
            >
              <option value="">全部状态</option>
              <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          
          <!-- 日期范围 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">开始日期</label>
            <input
              v-model="filters.start_date"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="applyFilters"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">结束日期</label>
            <input
              v-model="filters.end_date"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="applyFilters"
            />
          </div>
        </div>
        
        <div class="flex justify-end mt-4">
          <button
            @click="resetFilters"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            重置筛选
          </button>
        </div>
      </div>

      <!-- 记录列表 -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div v-if="loading" class="p-8 text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="mt-2 text-gray-600">加载中...</p>
        </div>
        
        <div v-else-if="error" class="p-8 text-center text-red-600">
          <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
          <p>{{ error }}</p>
          <button
            @click="loadRecords"
            class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            重试
          </button>
        </div>
        
        <div v-else-if="!hasRecords" class="p-8 text-center text-gray-500">
          <i class="fas fa-clipboard-list text-4xl mb-4"></i>
          <p>暂无用药记录</p>
          <button
            @click="showCreateForm = true"
            class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            添加第一条记录
          </button>
        </div>
        
        <div v-else>
          <!-- 表格头部 -->
          <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
            <div class="grid grid-cols-7 gap-4 text-sm font-medium text-gray-700">
              <div>药品信息</div>
              <div>服药时间</div>
              <div>数量</div>
              <div>状态</div>
              <div>依从性</div>
              <div>效果评分</div>
              <div>操作</div>
            </div>
          </div>
          
          <!-- 记录列表 -->
          <div class="divide-y divide-gray-200">
            <div
              v-for="record in records"
              :key="record.id"
              class="px-6 py-4 hover:bg-gray-50 transition-colors"
            >
              <div class="grid grid-cols-7 gap-4 items-center">
                <!-- 药品信息 -->
                <div class="flex items-center">
                  <img
                    :src="record.medicine_image || '/placeholder-medicine.png'"
                    :alt="record.medicine_name"
                    class="w-10 h-10 rounded-lg object-cover mr-3"
                  />
                  <div>
                    <p class="font-medium text-gray-900">{{ record.medicine_name }}</p>
                    <p class="text-sm text-gray-500">{{ record.medicine_specification }}</p>
                  </div>
                </div>
                
                <!-- 服药时间 -->
                <div>
                  <p class="text-sm text-gray-900">{{ formatDateTime(record.taken_at) }}</p>
                  <p class="text-xs text-gray-500">{{ formatTimeAgo(record.taken_at) }}</p>
                </div>
                
                <!-- 数量 -->
                <div>
                  <span class="text-sm text-gray-900">{{ record.quantity_taken }}</span>
                </div>
                
                <!-- 状态 -->
                <div>
                  <span :class="getStatusClass(record.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ getStatusLabel(record.status) }}
                  </span>
                </div>
                
                <!-- 依从性 -->
                <div>
                  <div class="flex items-center">
                    <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        class="h-2 rounded-full"
                        :class="getAdherenceColor(record.adherence_score || 0)"
                        :style="{ width: `${record.adherence_score || 0}%` }"
                      ></div>
                    </div>
                    <span class="text-xs text-gray-600">{{ record.adherence_score || 0 }}%</span>
                  </div>
                </div>
                
                <!-- 效果评分 -->
                <div>
                  <div v-if="record.effectiveness_score" class="flex items-center">
                    <div class="flex text-yellow-400">
                      <i
                        v-for="i in 5"
                        :key="i"
                        :class="i <= record.effectiveness_score ? 'fas fa-star' : 'far fa-star'"
                        class="text-xs"
                      ></i>
                    </div>
                    <span class="ml-1 text-xs text-gray-600">{{ record.effectiveness_score }}</span>
                  </div>
                  <span v-else class="text-xs text-gray-400">未评分</span>
                </div>
                
                <!-- 操作 -->
                <div class="flex space-x-2">
                  <button
                    @click="viewRecord(record)"
                    class="text-blue-600 hover:text-blue-800 transition-colors"
                    title="查看详情"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                  <button
                    @click="editRecord(record)"
                    class="text-green-600 hover:text-green-800 transition-colors"
                    title="编辑"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                    @click="confirmDelete(record)"
                    class="text-red-600 hover:text-red-800 transition-colors"
                    title="删除"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="pagination.totalPages > 1" class="mt-6 flex justify-center">
        <nav class="flex space-x-2">
          <button
            @click="changePage(pagination.page - 1)"
            :disabled="pagination.page <= 1"
            class="px-3 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一页
          </button>
          
          <button
            v-for="page in getPageNumbers()"
            :key="page"
            @click="changePage(page)"
            :class="{
              'bg-blue-600 text-white': page === pagination.page,
              'bg-white text-gray-700 hover:bg-gray-50': page !== pagination.page
            }"
            class="px-3 py-2 text-sm border border-gray-300 rounded-md"
          >
            {{ page }}
          </button>
          
          <button
            @click="changePage(pagination.page + 1)"
            :disabled="pagination.page >= pagination.totalPages"
            class="px-3 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </nav>
      </div>
    </div>

    <!-- 创建/编辑表单模态框 -->
    <RecordForm
      v-if="showCreateForm || showEditForm"
      :record="editingRecord"
      @close="closeForm"
      @success="handleFormSuccess"
    />

    <!-- 记录详情模态框 -->
    <RecordDetail
      v-if="showDetailModal"
      :record="selectedRecord"
      @close="showDetailModal = false"
      @edit="editRecord"
      @delete="confirmDelete"
    />

    <!-- 删除确认模态框 -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">确认删除</h3>
        <p class="text-gray-600 mb-6">确定要删除这条用药记录吗？此操作无法撤销。</p>
        <div class="flex justify-end space-x-3">
          <button
            @click="showDeleteModal = false"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            取消
          </button>
          <button
            @click="handleDelete"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            :disabled="loading"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { useRecordStore } from '../stores/record'
import { useAuthStore } from '../stores/auth'
import { MEDICATION_STATUS_OPTIONS } from '../types/record'
import type { MedicationRecord } from '../types/record'
import RecordForm from '../components/RecordForm.vue'
import RecordDetail from '../components/RecordDetail.vue'
import { debounce } from 'lodash-es'

// 路由和认证
const router = useRouter()
const authStore = useAuthStore()

// 状态管理
const recordStore = useRecordStore()
const {
  records,
  statistics,
  loading,
  error,
  pagination,
  hasRecords,
  fetchRecords,
  fetchStatistics,
  deleteRecord,
  exportRecords: storeExportRecords
} = recordStore

// 计算属性
const todayMedicineTypes = computed(() => {
  if (!records.value || !Array.isArray(records.value)) {
    return 0
  }
  
  const today = new Date().toISOString().split('T')[0]
  const todayRecords = records.value.filter(record => {
    if (!record || !record.taken_at) return false
    const recordDate = new Date(record.taken_at).toISOString().split('T')[0]
    return recordDate === today
  })
  
  // 获取今日用药的唯一药品ID
  const uniqueMedicineIds = new Set(todayRecords.map(record => record.medicine).filter(Boolean))
  return uniqueMedicineIds.size
})

// 本地状态
const searchQuery = ref('')
const filters = ref({
  status: '',
  start_date: '',
  end_date: ''
})

// 模态框状态
const showCreateForm = ref(false)
const showEditForm = ref(false)
const showDetailModal = ref(false)
const showDeleteModal = ref(false)

// 选中的记录
const selectedRecord = ref<MedicationRecord | null>(null)
const editingRecord = ref<MedicationRecord | null>(null)
const deletingRecord = ref<MedicationRecord | null>(null)

// 状态选项
const statusOptions = MEDICATION_STATUS_OPTIONS

// 防抖搜索
const debouncedSearch = debounce(() => {
  applyFilters()
}, 500)

// 加载记录
const loadRecords = async () => {
  console.log('🔵 [RecordsPage] loadRecords被调用')
  const params: any = {
    page: pagination.page,
    page_size: pagination.pageSize
  }
  
  if (searchQuery.value) {
    params.search = searchQuery.value
  }
  
  if (filters.value.status) {
    params.status = filters.value.status
  }
  
  if (filters.value.start_date) {
    params.start_date = filters.value.start_date
  }
  
  if (filters.value.end_date) {
    params.end_date = filters.value.end_date
  }
  
  console.log('🔵 [RecordsPage] 调用fetchRecords，参数:', params)
  await fetchRecords(params)
  console.log('🔵 [RecordsPage] fetchRecords完成，当前records数量:', records.value?.length || 0)
}

// 应用筛选
const applyFilters = () => {
  pagination.page = 1
  loadRecords()
}

// 重置筛选
const resetFilters = () => {
  searchQuery.value = ''
  filters.value = {
    status: '',
    start_date: '',
    end_date: ''
  }
  pagination.page = 1
  loadRecords()
}

// 分页
const changePage = (page: number) => {
  if (page >= 1 && page <= pagination.totalPages) {
    pagination.page = page
    loadRecords()
  }
}

const getPageNumbers = () => {
  const pages = []
  const total = pagination.totalPages
  const current = pagination.page
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...', total)
    } else if (current >= total - 3) {
      pages.push(1, '...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1, '...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...', total)
    }
  }
  
  return pages
}

// 记录操作
const viewRecord = (record: MedicationRecord) => {
  selectedRecord.value = record
  showDetailModal.value = true
}

const editRecord = (record: MedicationRecord) => {
  editingRecord.value = record
  showEditForm.value = true
  showDetailModal.value = false
}

const confirmDelete = (record: MedicationRecord) => {
  deletingRecord.value = record
  showDeleteModal.value = true
  showDetailModal.value = false
}

const handleDelete = async () => {
  if (deletingRecord.value) {
    try {
      await deleteRecord(deletingRecord.value.id)
      showDeleteModal.value = false
      deletingRecord.value = null
      // 重新加载当前页数据
      await loadRecords()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }
}

// 表单操作
const closeForm = () => {
  showCreateForm.value = false
  showEditForm.value = false
  editingRecord.value = null
}

const handleFormSuccess = () => {
  console.log('🟢 [RecordsPage] handleFormSuccess被调用')
  closeForm()
  console.log('🟢 [RecordsPage] 表单已关闭，开始重新加载记录')
  loadRecords()
}

// 导出记录
const exportRecords = async () => {
  try {
    const params: any = {}
    
    if (filters.value.start_date) {
      params.start_date = filters.value.start_date
    }
    
    if (filters.value.end_date) {
      params.end_date = filters.value.end_date
    }
    
    await storeExportRecords(params)
  } catch (error) {
    console.error('导出失败:', error)
  }
}

// 工具函数
const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString('zh-CN')
}

const formatTimeAgo = (dateTime: string) => {
  const now = new Date()
  const date = new Date(dateTime)
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return '今天'
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return `${Math.floor(days / 7)}周前`
  }
}

const getStatusLabel = (status: string) => {
  const option = statusOptions.find(opt => opt.value === status)
  return option?.label || status
}

const getStatusClass = (status: string) => {
  const classes = {
    taken: 'bg-green-100 text-green-800',
    missed: 'bg-red-100 text-red-800',
    delayed: 'bg-yellow-100 text-yellow-800',
    partial: 'bg-blue-100 text-blue-800'
  }
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800'
}

const getAdherenceColor = (score: number) => {
  if (score >= 90) return 'bg-green-500'
  if (score >= 70) return 'bg-yellow-500'
  return 'bg-red-500'
}

// 生命周期
// 使用watchEffect监听认证状态变化
const dataLoaded = ref(false)

watchEffect(async () => {
  console.log('🔵 [RecordsPage] watchEffect触发，检查认证状态')
  console.log('🔵 [RecordsPage] isAuthenticated:', authStore.isAuthenticated)
  console.log('🔵 [RecordsPage] localStorage access_token:', !!localStorage.getItem('access_token'))
  console.log('🔵 [RecordsPage] accessToken value:', authStore.accessToken)
  
  // 如果用户未登录，重定向到登录页面
  if (authStore.isAuthenticated === false) {
    console.log('🔴 [RecordsPage] 用户未登录，重定向到登录页面')
    router.push('/login')
    return
  }
  
  // 如果用户已登录且数据未加载，则加载数据
  if (authStore.isAuthenticated === true && !dataLoaded.value) {
    console.log('🔵 [RecordsPage] 用户已登录，开始加载数据')
    dataLoaded.value = true
    try {
      await loadRecords()
      await fetchStatistics()
      console.log('🔵 [RecordsPage] 数据加载完成')
    } catch (error) {
      console.error('🔴 [RecordsPage] 数据加载失败:', error)
      // 不重置dataLoaded状态，避免无限循环
      // 用户可以通过刷新页面或重新登录来重试
    }
  }
})

onMounted(() => {
  console.log('🔵 [RecordsPage] 组件挂载完成')
})
</script>