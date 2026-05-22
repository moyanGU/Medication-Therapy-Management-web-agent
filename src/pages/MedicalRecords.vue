<template>
  <div class="medical-records-page">
    <!-- 页面标题 -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">病历管理</h1>
        <p class="text-gray-600 mt-1">管理您的就医记录和病历信息</p>
      </div>
      <button
        @click="router.push({ name: 'MedicalRecordCreate' })"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
      >
        <Plus class="w-4 h-4" />
        添加病历
      </button>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <!-- 关键词搜索 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >关键词搜索</label
          >
          <div class="relative">
            <Search
              class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4"
            />
            <input
              v-model="searchParams.keyword"
              type="text"
              placeholder="搜索医院、科室、医生、诊断..."
              class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              @keyup.enter="handleSearch"
            />
          </div>
        </div>

        <!-- 日期范围 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >就诊日期</label
          >
          <div class="flex gap-2">
            <input
              v-model="searchParams.dateFrom"
              type="date"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <span class="self-center text-gray-500">至</span>
            <input
              v-model="searchParams.dateTo"
              type="date"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <!-- 医院筛选 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >医院</label
          >
          <select
            v-model="searchParams.hospital"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">全部医院</option>
            <option
              v-for="hospital in categories.hospitals"
              :key="hospital.hospital"
              :value="hospital.hospital"
            >
              {{ hospital.hospital }} ({{ hospital.count }})
            </option>
          </select>
        </div>

        <!-- 科室筛选 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >科室</label
          >
          <select
            v-model="searchParams.department"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">全部科室</option>
            <option
              v-for="dept in categories.departments"
              :key="dept.department"
              :value="dept.department"
            >
              {{ dept.department }} ({{ dept.count }})
            </option>
          </select>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <!-- 就诊类型 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >就诊类型</label
          >
          <select
            v-model="searchParams.visitType"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">全部类型</option>
            <option
              v-for="option in VISIT_TYPE_OPTIONS"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </div>

        <!-- 状态筛选 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >状态</label
          >
          <select
            v-model="searchParams.status"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">全部状态</option>
            <option
              v-for="option in RECORD_STATUS_OPTIONS"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </div>

        <!-- 紧急程度 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >紧急程度</label
          >
          <select
            v-model="searchParams.urgency"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">全部程度</option>
            <option
              v-for="option in URGENCY_LEVEL_OPTIONS"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </div>

        <!-- 排序 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >排序方式</label
          >
          <select
            v-model="sortBy"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            @change="handleSearch"
          >
            <option value="-visit_date">就诊日期（最新）</option>
            <option value="visit_date">就诊日期（最早）</option>
            <option value="-total_cost">费用（高到低）</option>
            <option value="total_cost">费用（低到高）</option>
            <option value="-satisfaction_score">满意度（高到低）</option>
            <option value="-created_at">创建时间（最新）</option>
          </select>
        </div>
      </div>

      <!-- 搜索按钮 -->
      <div class="flex gap-3">
        <button
          @click="handleSearch"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center gap-2 transition-colors"
          :disabled="isLoading"
        >
          <Search class="w-4 h-4" />
          搜索
        </button>
        <button
          @click="handleReset"
          class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md flex items-center gap-2 transition-colors"
        >
          <RotateCcw class="w-4 h-4" />
          重置
        </button>
      </div>
    </div>

    <!-- 病历列表 -->
    <div class="bg-white rounded-lg shadow-sm border">
      <!-- 列表头部 -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold text-gray-900">病历列表</h2>
          <div class="text-sm text-gray-500">
            共 {{ pagination.total }} 条记录
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="flex justify-center items-center py-12">
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
        ></div>
        <span class="ml-2 text-gray-600">加载中...</span>
      </div>

      <!-- 错误状态 -->
      <div
        v-else-if="error"
        class="flex flex-col items-center justify-center py-12"
      >
        <AlertCircle class="w-12 h-12 text-red-500 mb-4" />
        <p class="text-gray-600 mb-4">{{ error }}</p>
        <button
          @click="loadRecords"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
        >
          重新加载
        </button>
      </div>

      <!-- 空状态 -->
      <div
        v-else-if="records.length === 0"
        class="flex flex-col items-center justify-center py-12"
      >
        <FileText class="w-12 h-12 text-gray-400 mb-4" />
        <p class="text-gray-600 mb-4">暂无病历记录</p>
        <button
          @click="router.push({ name: 'MedicalRecordCreate' })"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
        >
          添加第一条病历
        </button>
      </div>

      <!-- 病历列表内容 -->
      <div v-else class="divide-y divide-gray-200">
        <div
          v-for="record in records"
          :key="record.id"
          class="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
          @click="viewRecord(record.id)"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-lg font-semibold text-gray-900">
                  {{ record.hospital }}
                </h3>
                <span
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="getStatusClass(record.status)"
                >
                  {{ getStatusLabel(record.status) }}
                </span>
                <span
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="getUrgencyClass(record.urgency_level)"
                >
                  {{ getUrgencyLabel(record.urgency_level) }}
                </span>
              </div>

              <div
                class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600"
              >
                <div class="flex items-center gap-2">
                  <Calendar class="w-4 h-4" />
                  <span>{{ formatDate(record.visit_date) }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <Building class="w-4 h-4" />
                  <span>{{ record.department }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <User class="w-4 h-4" />
                  <span>{{ record.doctor_name }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <DollarSign class="w-4 h-4" />
                  <span>¥{{ record.total_cost }}</span>
                </div>
              </div>

              <div class="mt-3">
                <p class="text-gray-900 font-medium">
                  主诉：{{ record.chief_complaint }}
                </p>
                <p class="text-gray-600 mt-1">诊断：{{ record.diagnosis }}</p>
                <p class="text-gray-600 mt-1">
                  治疗方案：{{ record.treatment_plan }}
                </p>
              </div>

              <div
                v-if="record.attachments && record.attachments.length > 0"
                class="mt-3"
              >
                <div class="flex items-center gap-2 text-sm text-gray-500">
                  <Paperclip class="w-4 h-4" />
                  <span>{{ record.attachments.length }} 个附件</span>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-2 ml-4">
              <button
                @click.stop="editRecord(record)"
                class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                title="编辑"
              >
                <Edit class="w-4 h-4" />
              </button>
              <button
                @click.stop="deleteRecord(record.id)"
                class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                title="删除"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="records.length > 0" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700">
            显示第 {{ (pagination.page - 1) * pagination.pageSize + 1 }} -
            {{
              Math.min(pagination.page * pagination.pageSize, pagination.total)
            }}
            条， 共 {{ pagination.total }} 条记录
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="changePage(pagination.page - 1)"
              :disabled="pagination.page <= 1"
              class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              上一页
            </button>
            <span class="px-3 py-1 text-sm">
              第 {{ pagination.page }} /
              {{ Math.ceil(pagination.total / pagination.pageSize) }} 页
            </span>
            <button
              @click="changePage(pagination.page + 1)"
              :disabled="
                pagination.page >=
                Math.ceil(pagination.total / pagination.pageSize)
              "
              class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑病历模态框 -->
    <!-- <MedicalRecordForm
      v-if="showCreateModal || showEditModal"
      :visible="showCreateModal || showEditModal"
      :record="editingRecord"
      @close="closeModal"
      @success="handleFormSuccess"
    /> -->
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMedicalRecordStore } from '@/stores/medicalRecords'
import { toast } from 'sonner'
import { isRequestCancelledError } from '@/utils/api'
import {
  Plus,
  Search,
  RotateCcw,
  FileText,
  DollarSign,
  AlertCircle,
  Calendar,
  Building,
  User,
  Paperclip,
  Edit,
  Trash2,
} from 'lucide-vue-next'
// import MedicalRecordForm from '@/components/MedicalRecordForm.vue'

// 常量定义
const VISIT_TYPE_OPTIONS = [
  { value: 'outpatient', label: '门诊' },
  { value: 'emergency', label: '急诊' },
  { value: 'inpatient', label: '住院' },
  { value: 'physical_exam', label: '体检' },
]

const RECORD_STATUS_OPTIONS = [
  { value: 'active', label: '有效' },
  { value: 'archived', label: '已归档' },
  { value: 'draft', label: '草稿' },
]

const URGENCY_LEVEL_OPTIONS = [
  { value: 'low', label: '低' },
  { value: 'medium', label: '中' },
  { value: 'high', label: '高' },
  { value: 'critical', label: '紧急' },
]

// 路由和状态管理
const router = useRouter()
const medicalRecordsStore = useMedicalRecordStore()

// 响应式数据
const isLoading = ref(false)
const error = ref('')
const records = ref([])
const categories = ref({
  hospitals: [],
  departments: [],
})
const statistics = ref({
  totalRecords: 0,
  monthlyRecords: 0,
  totalCost: 0,
  avgSatisfaction: 0,
})

// 搜索参数
const searchParams = reactive({
  keyword: '',
  dateFrom: '',
  dateTo: '',
  hospital: '',
  department: '',
  visitType: '',
  status: '',
  urgency: '',
})

// 排序和分页
const sortBy = ref('-visit_date')
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})

// 模态框状态
// const showCreateModal = ref(false)
// const showEditModal = ref(false)
// const editingRecord = ref(null)

// 计算属性
const _hasFilters = computed(() => {
  return (
    searchParams.keyword ||
    searchParams.dateFrom ||
    searchParams.dateTo ||
    searchParams.hospital ||
    searchParams.department ||
    searchParams.visitType ||
    searchParams.status ||
    searchParams.urgency
  )
})

// 方法定义
/**
 * 加载病历列表
 */
const loadRecords = async () => {
  try {
    isLoading.value = true
    error.value = ''

    const params = {
      ...searchParams,
      ordering: sortBy.value,
      page: pagination.page,
      page_size: pagination.pageSize,
    }

    console.log('Loading medical records with params:', params)
    await medicalRecordsStore.fetchRecords(params)

    // 直接使用 store 状态，避免构造模拟响应
    records.value = medicalRecordsStore.records
    pagination.total = medicalRecordsStore.pagination.total
    console.log(
      'Medical records loaded:',
      records.value.length,
      'total:',
      pagination.total
    )
  } catch (err: any) {
    if (isRequestCancelledError(err)) {
      console.log('[MedicalRecords] 病历列表请求已取消')
      return
    }

    console.error('Error loading medical records:', err)
    error.value = err.message || '加载病历列表失败'
    toast.error(error.value)
  } finally {
    isLoading.value = false
  }
}

/**
 * 加载统计数据
 */
const loadStatistics = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const params = {
      dateFrom: searchParams.dateFrom || undefined,
      dateTo: searchParams.dateTo || undefined,
      hospital: searchParams.hospital || undefined,
      department: searchParams.department || undefined,
      visitType: searchParams.visitType || undefined,
    }
    await medicalRecordsStore.fetchStatistics(params)
    // 将 store 的统计结果同步到本地，供模板渲染使用
    statistics.value = medicalRecordsStore.statistics
    console.log('[MedicalRecords] Statistics loaded:', statistics.value)
  } catch (err) {
    if (isRequestCancelledError(err)) {
      console.log('[MedicalRecords] 统计加载请求已取消')
      return
    }

    console.error('[MedicalRecords] 统计加载失败:', err)
    error.value = '统计信息加载失败，请稍后重试。'
    // 设置安全默认值到 store 和本地，避免渲染报错
    const fallback = {
      // 前端展示字段
      totalRecords: 0,
      monthlyRecords: 0,
      totalCost: 0,
      avgSatisfaction: 0,
      // 后端字段（保持完整类型，避免 TS 报错）
      total_visits: 0,
      recent_visits: 0,
      total_cost: 0,
      average_cost: 0,
      follow_up_due: 0,
      monthly_visits: [],
      department_distribution: [],
      cost_trend: [],
    }
    medicalRecordsStore.statistics = fallback
    statistics.value = fallback
  } finally {
    isLoading.value = false
  }
}

// 安全格式化函数，避免 undefined.toFixed 报错
/**
 * 加载分类数据
 */
const loadCategories = async () => {
  try {
    console.log('Loading medical records categories')
    await medicalRecordsStore.fetchCategories()

    // 直接使用 store 状态
    categories.value = medicalRecordsStore.categories
    console.log('Categories loaded:', categories.value)
  } catch (err) {
    console.error('Error loading categories:', err)
  }
}

/**
 * 搜索处理
 */
const handleSearch = () => {
  pagination.page = 1
  loadRecords()
}

/**
 * 重置搜索
 */
const handleReset = () => {
  Object.assign(searchParams, {
    keyword: '',
    dateFrom: '',
    dateTo: '',
    hospital: '',
    department: '',
    visitType: '',
    status: '',
    urgency: '',
  })
  sortBy.value = '-visit_date'
  pagination.page = 1
  loadRecords()
}

/**
 * 分页处理
 */
const changePage = (page: number) => {
  if (page >= 1 && page <= Math.ceil(pagination.total / pagination.pageSize)) {
    pagination.page = page
    loadRecords()
  }
}

/**
 * 查看病历详情
 */
const viewRecord = (recordId: number) => {
  router.push(`/medical-records/${recordId}`)
}

/**
 * 编辑病历
 */
const editRecord = (record: any) => {
  console.log(
    '[MedicalRecords] Edit clicked, navigating to edit page for id:',
    record?.id
  )
  router.push({ name: 'MedicalRecordEdit', params: { id: record.id } })
}

/**
 * 删除病历
 */
const deleteRecord = async (recordId: number) => {
  if (!confirm('确定要删除这条病历记录吗？此操作不可恢复。')) {
    return
  }

  try {
    console.log('Deleting medical record:', recordId)
    const ok = await medicalRecordsStore.deleteRecord(recordId)

    if (ok) {
      toast.success('病历删除成功')
      loadRecords()
      loadStatistics()
    } else {
      throw new Error('删除病历失败')
    }
  } catch (err: any) {
    console.error('Error deleting medical record:', err)
    toast.error(err.message || '删除病历失败')
  }
}

/**
 * 关闭模态框
 */
// const closeModal = () => {
//   showCreateModal.value = false
//   showEditModal.value = false
//   editingRecord.value = null
// }

/**
 * 表单提交成功处理
 */
// const handleFormSuccess = () => {
//   closeModal()
//   loadRecords()
//   loadStatistics()
//   toast.success(editingRecord.value ? '病历更新成功' : '病历创建成功')
// }

/**
 * 格式化日期
 */
const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

/**
 * 获取状态样式类
 */
const getStatusClass = (status: string) => {
  const classes = {
    active: 'bg-green-100 text-green-800',
    archived: 'bg-gray-100 text-gray-800',
    draft: 'bg-yellow-100 text-yellow-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

/**
 * 获取状态标签
 */
const getStatusLabel = (status: string) => {
  const option = RECORD_STATUS_OPTIONS.find(opt => opt.value === status)
  return option ? option.label : status
}

/**
 * 获取紧急程度样式类
 */
const getUrgencyClass = (urgency: string) => {
  const classes = {
    low: 'bg-blue-100 text-blue-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  }
  return classes[urgency] || 'bg-gray-100 text-gray-800'
}

/**
 * 获取紧急程度标签
 */
const getUrgencyLabel = (urgency: string) => {
  const option = URGENCY_LEVEL_OPTIONS.find(opt => opt.value === urgency)
  return option ? option.label : urgency
}

// 组件挂载时加载数据
onMounted(() => {
  console.log('MedicalRecords component mounted')
  loadRecords()
  loadStatistics()
  loadCategories()
})
</script>

<style scoped>
.medical-records-page {
  min-height: 100vh;
  background-color: #f9fafb;
  padding: 1.5rem;
}

@media (max-width: 768px) {
  .medical-records-page {
    padding: 1rem;
  }
}

/* 加载动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* 响应式表格 */
@media (max-width: 1024px) {
  .grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .grid-cols-4,
  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

/* 卡片悬停效果 */
.hover\:bg-gray-50:hover {
  background-color: #f9fafb;
}

/* 按钮禁用状态 */
.disabled\:opacity-50:disabled {
  opacity: 0.5;
}

.disabled\:cursor-not-allowed:disabled {
  cursor: not-allowed;
}
</style>
