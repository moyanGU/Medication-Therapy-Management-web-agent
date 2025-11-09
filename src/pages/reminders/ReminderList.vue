<template>
  <div class="reminder-list-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">用药提醒</h1>
          <p class="text-gray-600 mt-1">管理您的用药提醒设置</p>
        </div>
        <div class="flex items-center space-x-3">
          <button
            @click="refreshData"
            :disabled="loading"
            class="btn-secondary"
          >
            <RefreshCw :class="{ 'animate-spin': loading }" class="w-4 h-4 mr-2" />
            刷新
          </button>
          <router-link
            to="/reminders/create"
            class="btn-primary"
          >
            <Plus class="w-4 h-4 mr-2" />
            新建提醒
          </router-link>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      <div class="stats-card">
        <div class="flex items-center">
          <div class="stats-icon bg-blue-100 text-blue-600">
            <Bell class="w-6 h-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">总提醒数</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.total_reminders ?? 0 }}</p>
          </div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="flex items-center">
          <div class="stats-icon bg-green-100 text-green-600">
            <CheckCircle class="w-6 h-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">活跃提醒</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.active_reminders ?? 0 }}</p>
          </div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="flex items-center">
          <div class="stats-icon bg-yellow-100 text-yellow-600">
            <Clock class="w-6 h-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">今日提醒</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.today_reminders ?? 0 }}</p>
          </div>
        </div>
      </div>
      
      <div class="stats-card">
        <div class="flex items-center">
          <div class="stats-icon bg-purple-100 text-purple-600">
            <TrendingUp class="w-6 h-6" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">响应率</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.response_rate ?? 0 }}%</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <!-- 搜索框 -->
        <div class="relative">
          <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索提醒标题或药品名称..."
            class="input-field pl-10"
            @input="debouncedSearch"
          />
        </div>
        
        <!-- 状态筛选 -->
        <select v-model="filters.is_active" class="input-field">
          <option value="">全部状态</option>
          <option :value="true">活跃</option>
          <option :value="false">停用</option>
        </select>
        
        <!-- 频率筛选 -->
        <select v-model="filters.frequency" class="input-field">
          <option value="">全部频率</option>
          <option value="daily">每日</option>
          <option value="twice_daily">每日两次</option>
          <option value="three_times_daily">每日三次</option>
          <option value="four_times_daily">每日四次</option>
          <option value="weekly">每周</option>
          <option value="every_other_day">隔日</option>
          <option value="custom">自定义</option>
        </select>
        
        <!-- 用药时机筛选 -->
        <select v-model="filters.meal_timing" class="input-field">
          <option value="">全部时机</option>
          <option value="before_meal">餐前</option>
          <option value="with_meal">餐中</option>
          <option value="after_meal">餐后</option>
          <option value="before_breakfast">早饭前</option>
          <option value="after_dinner">晚饭后</option>
          <option value="before_bed">睡前</option>
          <option value="anytime">任意时间</option>
        </select>
      </div>
      
      <!-- 快速筛选标签 -->
      <div class="flex flex-wrap gap-2 mb-4">
        <button
          @click="setQuickFilter('all')"
          :class="[
            'quick-filter-btn',
            quickFilter === 'all' ? 'active' : ''
          ]"
        >
          全部
        </button>
        <button
          @click="setQuickFilter('today')"
          :class="[
            'quick-filter-btn',
            quickFilter === 'today' ? 'active' : ''
          ]"
        >
          今日提醒
        </button>
        <button
          @click="setQuickFilter('active')"
          :class="[
            'quick-filter-btn',
            quickFilter === 'active' ? 'active' : ''
          ]"
        >
          活跃提醒
        </button>
        <button
          @click="setQuickFilter('expired')"
          :class="[
            'quick-filter-btn',
            quickFilter === 'expired' ? 'active' : ''
          ]"
        >
          已过期
        </button>
      </div>
      
      <!-- 批量操作 -->
      <div v-if="selectedReminders.length > 0" class="batch-actions">
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600">
            已选择 {{ selectedReminders.length }} 个提醒
          </span>
          <div class="flex items-center space-x-2">
            <button
              @click="batchToggleActive(true)"
              class="btn-sm btn-secondary"
            >
              批量启用
            </button>
            <button
              @click="batchToggleActive(false)"
              class="btn-sm btn-secondary"
            >
              批量停用
            </button>
            <button
              @click="batchDelete"
              class="btn-sm btn-danger"
            >
              批量删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 提醒列表 -->
    <div class="reminder-list">
      <div v-if="loading && reminders.length === 0" class="loading-state">
        <div class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="ml-3 text-gray-600">加载中...</span>
        </div>
      </div>
      
      <div v-else-if="reminders.length === 0" class="empty-state">
        <div class="text-center py-12">
          <Bell class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900">暂无提醒</h3>
          <p class="mt-1 text-sm text-gray-500">
            {{ hasFilters ? '没有找到符合条件的提醒' : '您还没有创建任何提醒' }}
          </p>
          <div class="mt-6">
            <router-link
              to="/reminders/create"
              class="btn-primary"
            >
              <Plus class="w-4 h-4 mr-2" />
              创建第一个提醒
            </router-link>
          </div>
        </div>
      </div>
      
      <div v-else class="space-y-4">
        <div
          v-for="reminder in reminders"
          :key="reminder.id"
          class="reminder-card"
          :class="{
            'opacity-60': !reminder.is_active,
            'border-l-4 border-l-green-500': reminder.is_active,
            'border-l-4 border-l-gray-300': !reminder.is_active
          }"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start space-x-3">
              <!-- 选择框 -->
              <input
                type="checkbox"
                :value="reminder.id"
                v-model="selectedReminders"
                class="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              
              <!-- 提醒信息 -->
              <div class="flex-1">
                <div class="flex items-center space-x-2">
                  <h3 class="text-lg font-medium text-gray-900">
                    {{ reminder.title || reminder.medicine_name }}
                  </h3>
                  <span
                    :class="[
                      'status-badge',
                      reminder.is_active ? 'status-active' : 'status-inactive'
                    ]"
                  >
                    {{ reminder.is_active ? '活跃' : '停用' }}
                  </span>
                </div>
                
                <div class="mt-1 space-y-1">
                  <p class="text-sm text-gray-600">
                    <Pill class="inline w-4 h-4 mr-1" />
                    {{ reminder.medicine_name }}
                    <span class="mx-2">•</span>
                    {{ reminder.dosage }} {{ getDosageUnitLabel(reminder.dosage_unit) }}
                  </p>
                  
                  <p class="text-sm text-gray-600">
                    <Clock class="inline w-4 h-4 mr-1" />
                    {{ formatTime(reminder.reminder_time) }}
                    <span class="mx-2">•</span>
                    {{ getFrequencyLabel(reminder.frequency) }}
                    <span class="mx-2">•</span>
                    {{ getMealTimingLabel(reminder.meal_timing) }}
                  </p>
                  
                  <div class="flex items-center space-x-4 text-sm text-gray-500">
                    <span>
                      <Calendar class="inline w-4 h-4 mr-1" />
                      {{ formatDate(reminder.start_date) }}
                      {{ reminder.end_date ? ` - ${formatDate(reminder.end_date)}` : ' 起' }}
                    </span>
                    
                    <span>
                      提醒 {{ reminder.reminder_count }} 次
                    </span>
                    
                    <span>
                      响应 {{ reminder.response_count }} 次
                    </span>
                    
                    <span v-if="reminder.reminder_count > 0">
                      响应率 {{ Math.round((reminder.response_count / reminder.reminder_count) * 100) }}%
                    </span>
                  </div>
                  
                  <div v-if="reminder.special_instructions" class="text-sm text-gray-600">
                    <FileText class="inline w-4 h-4 mr-1" />
                    {{ reminder.special_instructions }}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="flex items-center space-x-2">
              <button
                @click="toggleReminderActive(reminder)"
                :class="[
                  'btn-sm',
                  reminder.is_active ? 'btn-secondary' : 'btn-primary'
                ]"
              >
                {{ reminder.is_active ? '停用' : '启用' }}
              </button>
              
              <router-link
                :to="`/reminders/${reminder.id}/edit`"
                class="btn-sm btn-secondary"
              >
                <Edit class="w-4 h-4 mr-1" />
                编辑
              </router-link>
              
              <button
                @click="deleteReminder(reminder)"
                class="btn-sm btn-danger"
              >
                <Trash2 class="w-4 h-4 mr-1" />
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="pagination.total > pagination.page_size" class="pagination-wrapper">
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-700">
          显示第 {{ (pagination.page - 1) * pagination.page_size + 1 }} - 
          {{ Math.min(pagination.page * pagination.page_size, pagination.total) }} 条，
          共 {{ pagination.total }} 条记录
        </div>
        
        <div class="flex items-center space-x-2">
          <button
            @click="changePage(pagination.page - 1)"
            :disabled="pagination.page <= 1"
            class="btn-sm btn-secondary"
          >
            <ChevronLeft class="w-4 h-4" />
            上一页
          </button>
          
          <div class="flex items-center space-x-1">
            <button
              v-for="page in getPageNumbers()"
              :key="page"
              @click="changePage(page)"
              :class="[
                'btn-sm',
                page === pagination.page ? 'btn-primary' : 'btn-secondary'
              ]"
            >
              {{ page }}
            </button>
          </div>
          
          <button
            @click="changePage(pagination.page + 1)"
            :disabled="pagination.page >= Math.ceil(pagination.total / pagination.page_size)"
            class="btn-sm btn-secondary"
          >
            下一页
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useReminderStore } from '@/stores/reminder'
import { debounce } from 'lodash-es'
import {
  Bell,
  CheckCircle,
  Clock,
  TrendingUp,
  Search,
  Plus,
  RefreshCw,
  Calendar,
  Pill,
  FileText,
  Edit,
  Trash2,
  ChevronLeft,
  ChevronRight
} from 'lucide-vue-next'

// 接口类型定义
interface Reminder {
  id: number
  title: string
  // 后端列表返回 medicine 为主键ID，同时提供 medicine_name 字段
  medicine: number | { id: number; name: string }
  medicine_name: string
  dosage: number
  dosage_unit: string
  frequency: string
  meal_timing: string
  reminder_time: string
  start_date: string
  end_date?: string
  is_active: boolean
  special_instructions?: string
  reminder_count: number
  response_count: number
  created_at: string
  updated_at: string
}

interface Stats {
  total_reminders: number
  active_reminders: number
  today_reminders: number
  response_rate: number
}

interface Pagination {
  page: number
  page_size: number
  total: number
  total_pages: number
}

// 响应式数据
const router = useRouter()
const { success, error, warning, info } = useToast()

const reminderStore = useReminderStore()
const loading = computed(() => reminderStore.loading)
const reminders = computed<Reminder[]>(() => reminderStore.reminders as any)
const stats = ref<Stats>({
  total_reminders: 0,
  active_reminders: 0,
  today_reminders: 0,
  response_rate: 0
})

const searchQuery = ref('')
const quickFilter = ref('all')
const selectedReminders = ref<number[]>([])

const filters = reactive({
  is_active: '',
  frequency: '',
  meal_timing: ''
})

const pagination = reactive<Pagination>({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0
})

// 计算属性
const hasFilters = computed(() => {
  return searchQuery.value || 
         filters.is_active !== '' || 
         filters.frequency || 
         filters.meal_timing ||
         quickFilter.value !== 'all'
})

// 防抖搜索
const debouncedSearch = debounce(() => {
  pagination.page = 1
  fetchReminders()
}, 300)

// 方法
/**
 * 获取提醒列表（使用 Pinia Store + Service）
 * 函数级注释：
 * - 输入：来自页面的筛选参数与分页参数
 * - 过程：调用 reminderStore.fetchReminders，将筛选与分页组合传入；
 *         ApiClient 已处理双层 data 结构，store 内部也已解析分页信息。
 * - 输出：更新本地分页显示（page、total、total_pages），列表绑定到 store 状态。
 */
const fetchReminders = async () => {
  try {
    const params: Record<string, any> = {
      page: pagination.page,
      page_size: pagination.page_size,
    }
    if (searchQuery.value) params.search = searchQuery.value
    if (filters.is_active !== '') params.is_active = filters.is_active
    if (filters.frequency) params.frequency = filters.frequency
    if (filters.meal_timing) params.meal_timing = filters.meal_timing
    if (quickFilter.value !== 'all') params.filter = quickFilter.value

    console.log('[Reminders] 请求列表参数(store):', params)
    await reminderStore.fetchReminders(params)
    // 同步分页到本地展示对象
    const pg = reminderStore.pagination
    pagination.page = pg.page
    pagination.total = pg.total
    pagination.page_size = pg.pageSize
    pagination.total_pages = pg.totalPages
    console.log('[Reminders] 列表分页(store):', pg)
  } catch (err: any) {
    console.error('获取提醒列表失败(store):', err)
    error(err?.message || '获取提醒列表失败')
  }
}

/**
 * 获取提醒统计（使用 Pinia Store 提供的 fetchReminderStats）
 * 函数级注释：直接从 /reminders/stats/ 获取概览统计并写入页面状态。
 */
const fetchStats = async () => {
  try {
    console.log('[Reminders] 请求统计数据(store)')
    const data = await reminderStore.fetchReminderStats()
    stats.value = (data as any) ?? {
      total_reminders: 0,
      active_reminders: 0,
      today_reminders: 0,
      response_rate: 0
    }
    console.log('[Reminders] 统计数据(store):', data)
  } catch (err: any) {
    console.error('获取统计数据失败(store):', err)
    error(err?.message || '获取统计数据失败')
  }
}

const refreshData = () => {
  fetchReminders()
  fetchStats()
}

const setQuickFilter = (filter: string) => {
  quickFilter.value = filter
  pagination.page = 1
  fetchReminders()
}

const changePage = (page: number) => {
  pagination.page = page
  fetchReminders()
}

const getPageNumbers = () => {
  const pages = [] as number[]
  const start = Math.max(1, pagination.page - 2)
  const end = Math.min(pagination.total_pages, pagination.page + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
}

/**
 * 启用/停用提醒
 */
/**
 * 启用/停用提醒（使用 Store）
 * 函数级注释：调用 store.toggleReminderActive，避免直接操作 API；
 * 成功后由 store 更新列表状态并刷新统计。
 */
const toggleReminderActive = async (reminder: Reminder) => {
  try {
    console.log('[Reminders] 切换提醒状态(store):', reminder.id)
    await reminderStore.toggleReminderActive(reminder.id)
    success(`提醒已${reminder.is_active ? '启用' : '停用'}`)
    fetchStats()
  } catch (err: any) {
    console.error('切换提醒状态失败(store):', err)
    error(err?.message || '操作失败')
  }
}

/**
 * 删除提醒
 */
/**
 * 删除提醒（使用 Store）
 * 函数级注释：调用 store.deleteReminder 并刷新列表与统计。
 */
const deleteReminder = async (reminder: Reminder) => {
  if (!confirm(`确定要删除提醒"${reminder.title || reminder.medicine_name}"吗？`)) return
  try {
    await reminderStore.deleteReminder(reminder.id)
    success('提醒已删除')
    fetchReminders()
    fetchStats()
  } catch (err: any) {
    console.error('删除提醒失败(store):', err)
    error(err?.message || '删除失败')
  }
}

/**
 * 批量启停
 */
/**
 * 批量启停（使用 Store）
 * 函数级注释：调用 store.batchToggleReminders 执行后端批量接口，并刷新列表与统计。
 */
const batchToggleActive = async (isActive: boolean) => {
  if (selectedReminders.value.length === 0) return
  try {
    await reminderStore.batchToggleReminders({
      reminder_ids: selectedReminders.value,
      is_active: isActive
    })
    success(`已${isActive ? '启用' : '停用'} ${selectedReminders.value.length} 个提醒`)
    selectedReminders.value = []
    fetchReminders()
    fetchStats()
  } catch (err: any) {
    console.error('批量启停失败(store):', err)
    error(err?.message || '批量操作失败')
  }
}

/**
 * 批量删除 - 使用POST方法传递JSON
 */
/**
 * 批量删除（使用 Store）
 * 函数级注释：调用 store.batchDeleteReminders，并刷新列表与统计。
 */
const batchDelete = async () => {
  if (selectedReminders.value.length === 0) return
  if (!confirm(`确定要删除选中的 ${selectedReminders.value.length} 个提醒吗？`)) return
  try {
    await reminderStore.batchDeleteReminders({
      reminder_ids: selectedReminders.value
    })
    success(`已删除 ${selectedReminders.value.length} 个提醒`)
    selectedReminders.value = []
    fetchReminders()
    fetchStats()
  } catch (err: any) {
    console.error('批量删除失败(store):', err)
    error(err?.message || '批量删除失败')
  }
}

// 格式化函数
const formatTime = (time: string) => {
  return new Date(`2000-01-01T${time}`).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

const getFrequencyLabel = (frequency: string) => {
  const labels: Record<string, string> = {
    daily: '每日',
    twice_daily: '每日两次',
    three_times_daily: '每日三次',
    four_times_daily: '每日四次',
    weekly: '每周',
    every_other_day: '隔日',
    custom: '自定义'
  }
  return labels[frequency] || frequency
}

const getMealTimingLabel = (timing: string) => {
  const labels: Record<string, string> = {
    before_meal: '餐前',
    with_meal: '餐中',
    after_meal: '餐后',
    before_breakfast: '早饭前',
    after_dinner: '晚饭后',
    before_bed: '睡前',
    anytime: '任意时间'
  }
  return labels[timing] || timing
}

const getDosageUnitLabel = (unit: string) => {
  const labels: Record<string, string> = {
    tablet: '片',
    capsule: '粒',
    ml: '毫升',
    mg: '毫克',
    g: '克',
    drop: '滴',
    spray: '喷',
    patch: '贴'
  }
  return labels[unit] || unit
}

// 监听器
watch([() => filters.is_active, () => filters.frequency, () => filters.meal_timing], () => {
  pagination.page = 1
  fetchReminders()
})

// 生命周期
onMounted(() => {
  fetchReminders()
  fetchStats()
})
</script>

<style scoped lang="postcss">
.reminder-list-page {
  @apply p-6 max-w-7xl mx-auto;
}

.page-header {
  @apply mb-6;
}

.stats-card {
  @apply bg-white rounded-lg shadow p-6;
}

.stats-icon {
  @apply w-12 h-12 rounded-lg flex items-center justify-center;
}

.filter-section {
  @apply bg-white rounded-lg shadow p-6 mb-6;
}

.quick-filter-btn {
  @apply px-3 py-1 text-sm rounded-full border transition-colors;
}

.quick-filter-btn.active {
  @apply bg-blue-600 text-white border-blue-600;
}

.quick-filter-btn:not(.active) {
  @apply bg-white text-gray-700 border-gray-300 hover:bg-gray-50;
}

.batch-actions {
  @apply mt-4 p-4 bg-blue-50 rounded-lg;
}

.reminder-list {
  @apply space-y-4;
}

.reminder-card {
  @apply bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow;
}

.status-badge {
  @apply px-2 py-1 text-xs font-medium rounded-full;
}

.status-active {
  @apply bg-green-100 text-green-800;
}

.status-inactive {
  @apply bg-gray-100 text-gray-800;
}

.pagination-wrapper {
  @apply mt-6 bg-white rounded-lg shadow p-4;
}

.loading-state,
.empty-state {
  @apply bg-white rounded-lg shadow;
}

.btn-primary {
  @apply bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center;
}

.btn-secondary {
  @apply bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors flex items-center;
}

.btn-danger {
  @apply bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors flex items-center;
}

.btn-sm {
  @apply px-3 py-1 text-sm;
}

.input-field {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}
</style>