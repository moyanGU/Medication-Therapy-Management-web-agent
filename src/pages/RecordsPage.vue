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
              <p class="text-2xl font-bold text-gray-900">
                {{ statistics.total_records }}
              </p>
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
              <p class="text-2xl font-bold text-gray-900">
                {{ statistics.adherence_rate }}%
              </p>
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
              <p class="text-2xl font-bold text-gray-900">
                {{ todayMedicineTypes }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- 搜索框：保留输入防抖，不新增多余按钮 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"
              >搜索</label
            >
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索药品名称、备注..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="debouncedSearch"
              @keyup.enter="applyFilters"
            />
          </div>

          <!-- 状态筛选 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"
              >状态</label
            >
            <select
              v-model="filters.status"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="applyFilters"
            >
              <option value="">全部状态</option>
              <option
                v-for="option in statusOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>

          <!-- 日期范围 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"
              >开始日期</label
            >
            <input
              v-model="filters.start_date"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="applyFilters"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"
              >结束日期</label
            >
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
            @click="applyFilters"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors mr-2"
          >
            确认搜索
          </button>
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
          <div
            class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
          ></div>
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
            <div
              class="grid grid-cols-7 gap-4 text-sm font-medium text-gray-700"
            >
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
                  <div
                    class="w-10 h-10 rounded-lg bg-gray-100 mr-3 flex items-center justify-center text-gray-400 flex-shrink-0"
                    aria-hidden="true"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      class="w-5 h-5"
                    >
                      <path d="M10 2h4" />
                      <path d="M12 14v8" />
                      <path d="M8 10a4 4 0 0 1 8 0v2a4 4 0 0 1-8 0z" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">
                      {{ record.medicine_name }}
                    </p>
                    <p class="text-sm text-gray-500">
                      {{ record.medicine_specification }}
                    </p>
                  </div>
                </div>

                <!-- 服药时间 -->
                <div>
                  <p class="text-sm text-gray-900">
                    {{ formatDateTime(record.taken_at) }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ formatTimeAgo(record.taken_at) }}
                  </p>
                </div>

                <!-- 数量 -->
                <div>
                  <span class="text-sm text-gray-900">{{
                    record.quantity_taken
                  }}</span>
                </div>

                <!-- 状态 -->
                <div>
                  <span
                    :class="getStatusClass(record.status)"
                    class="px-2 py-1 rounded-full text-xs font-medium"
                  >
                    {{ getStatusLabel(record.status) }}
                  </span>
                </div>

                <!-- 依从性 -->
                <div>
                  <div class="flex items-center">
                    <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        class="h-2 rounded-full"
                        :class="getAdherenceColor(record.adherence_score ?? 0)"
                        :style="{ width: `${record.adherence_score ?? 0}%` }"
                      ></div>
                    </div>
                    <span class="text-xs text-gray-600"
                      >{{ record.adherence_score ?? 0 }}%</span
                    >
                  </div>
                </div>

                <!-- 效果评分（修复：支持0分显示，使用星级+数值） -->
                <div>
                  <div
                    v-if="
                      record.effectiveness_score !== undefined &&
                      record.effectiveness_score !== null
                    "
                    class="flex items-center"
                  >
                    <div class="flex text-yellow-400">
                      <i
                        v-for="i in 10"
                        :key="i"
                        :class="
                          i <= (Number(record.effectiveness_score) || 0)
                            ? 'fas fa-star'
                            : 'far fa-star'
                        "
                        class="text-xs"
                      ></i>
                    </div>
                    <span class="ml-1 text-xs text-gray-600">{{
                      record.effectiveness_score
                    }}</span>
                  </div>
                  <span v-else class="text-xs text-gray-400">未评分</span>
                </div>

                <!-- 操作（包含删除按钮） -->
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
            @click="changePage(page as number)"
            :class="{
              'bg-blue-600 text-white': page === pagination.page,
              'bg-white text-gray-700 hover:bg-gray-50':
                page !== pagination.page,
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

    <!-- 删除确认模态框（单条） -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">确认删除</h3>
        <p class="text-gray-600 mb-6">
          确定要删除这条用药记录吗？此操作无法撤销。
        </p>
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
import { ref, computed, onMounted, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { useRecordStore } from '../stores/record'
import { useAuthStore } from '../stores/auth'
import { MEDICATION_STATUS_OPTIONS } from '../types/record'
import type { MedicationRecord } from '../types/record'
import RecordForm from '../components/RecordForm.vue'
import RecordDetail from '../components/RecordDetail.vue'
import { debounce } from 'lodash-es'
import { recordApi } from '../api/record'
import { storeToRefs } from 'pinia'
import { isRequestCancelledError } from '@/utils/api'

// 当日用药种类（修复：从独立查询计算）
// 保留唯一定义，删除重复定义
const todayMedicineTypesCount = ref(0)
const todayMedicineTypes = computed(() => todayMedicineTypesCount.value)

// 本地状态
const searchQuery = ref('')
const filters = ref({
  status: '',
  start_date: '',
  end_date: '',
})

// 模态框状态
const showCreateForm = ref(false)
const showEditForm = ref(false)
const showDetailModal = ref(false)
const showDeleteModal = ref(false)
const showDeleteAllModal = ref(false)

// 选中的记录
const selectedRecord = ref<MedicationRecord | null>(null)
const editingRecord = ref<MedicationRecord | null>(null)
const deletingRecord = ref<MedicationRecord | null>(null)

// 状态选项
const statusOptions = MEDICATION_STATUS_OPTIONS

/**
 * 格式化日期时间为本地化字符串（zh-CN）
 * @param dateTime ISO 日期时间字符串
 * @returns 本地化的日期时间，如 2025/01/01 12:30:00
 */
const formatDateTime = (dateTime: string) => {
  try {
    const d = new Date(dateTime)
    if (isNaN(d.getTime())) return '-'
    const result = d.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
    return result
  } catch (e) {
    console.warn('[RecordsPage] formatDateTime 解析失败:', dateTime, e)
    return '-'
  }
}

/**
 * 将时间转换为相对时间描述（如“5分钟前”）
 * @param dateTime ISO 日期时间字符串
 * @returns 相对时间文本
 */
const formatTimeAgo = (dateTime: string) => {
  try {
    const now = new Date().getTime()
    const t = new Date(dateTime).getTime()
    if (isNaN(t)) return ''
    const diff = Math.max(0, now - t)

    const sec = Math.floor(diff / 1000)
    if (sec < 60) return `${sec}秒前`

    const min = Math.floor(sec / 60)
    if (min < 60) return `${min}分钟前`

    const hour = Math.floor(min / 60)
    if (hour < 24) return `${hour}小时前`

    const day = Math.floor(hour / 24)
    if (day < 30) return `${day}天前`

    const month = Math.floor(day / 30)
    if (month < 12) return `${month}个月前`

    const year = Math.floor(month / 12)
    return `${year}年前`
  } catch (e) {
    console.warn('[RecordsPage] formatTimeAgo 解析失败:', dateTime, e)
    return ''
  }
}

/**
 * 获取状态标签
 * 复用全局 MEDICATION_STATUS_OPTIONS 以保证一致性
 */
const getStatusLabel = (status: string) => {
  const opt = MEDICATION_STATUS_OPTIONS.find(o => o.value === status)
  return opt?.label || status || '-'
}

/**
 * 根据状态返回样式类
 * taken: 绿色；missed: 红色；delayed: 黄色；partial: 橙色；其他：灰色
 */
const getStatusClass = (status: string) => {
  const map: Record<string, string> = {
    taken: 'bg-green-100 text-green-800',
    missed: 'bg-red-100 text-red-800',
    delayed: 'bg-yellow-100 text-yellow-800',
    partial: 'bg-orange-100 text-orange-800',
  }
  return map[status] || 'bg-gray-100 text-gray-800'
}

/**
 * 根据依从性分数返回进度条颜色
 * >=80: 绿色；>=50: 黄色；否则红色
 */
const getAdherenceColor = (score: number) => {
  const s = Number(score) || 0
  if (s >= 80) return 'bg-green-500'
  if (s >= 50) return 'bg-yellow-500'
  return 'bg-red-500'
}

// 路由和认证
const router = useRouter()
const authStore = useAuthStore()

// 状态管理
const recordStore = useRecordStore()
// 使用 storeToRefs 保持状态/计算属性的响应性，避免直接解构导致的响应性丢失
const { records, statistics, loading, error, pagination, hasRecords } =
  storeToRefs(recordStore)
// 方法可直接从 store 解构
const {
  fetchRecords,
  fetchStatistics,
  deleteRecord,
  exportRecords: storeExportRecords,
} = recordStore

// 为模板暴露导出函数别名，避免 @click="exportRecords" 未定义导致的类型错误
const exportRecords = async () => {
  try {
    await storeExportRecords()
  } catch (e) {
    console.error('[RecordsPage] 导出记录失败:', e)
  }
}

// 防抖搜索
const debouncedSearch = debounce(() => {
  applyFilters()
}, 500)

// 加载记录
const loadRecords = async () => {
  console.log('🔵 [RecordsPage] loadRecords被调用')
  const params: any = {
    page: pagination.value.page,
    page_size: pagination.value.pageSize,
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
  console.log(
    '🔵 [RecordsPage] fetchRecords完成，当前records数量:',
    records.value?.length ?? 0
  )
}

// 应用筛选
const applyFilters = () => {
  pagination.value.page = 1
  loadRecords()
}

// 重置筛选
const resetFilters = () => {
  searchQuery.value = ''
  filters.value = {
    status: '',
    start_date: '',
    end_date: '',
  }
  pagination.value.page = 1
  loadRecords()
}

// 分页
const changePage = (page: number) => {
  if (page >= 1 && page <= pagination.value.totalPages) {
    pagination.value.page = page
    loadRecords()
  }
}

const getPageNumbers = () => {
  const pages: Array<number | string> = []
  const total = pagination.value.totalPages
  const current = pagination.value.page

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
      await updateTodayMedicineTypes()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }
}

// 批量删除（当前筛选结果，最多1000条）
const _confirmDeleteAll = () => {
  showDeleteAllModal.value = true
}

/**
 * 批量删除（分页抓取，page_size=100，直到取完）
 */
const _handleDeleteAll = async () => {
  try {
    console.log('🔵 [RecordsPage] 开始批量删除（分页抓取）')

    const baseParams: any = {}
    if (searchQuery.value) baseParams.search = searchQuery.value
    if (filters.value.status) baseParams.status = filters.value.status
    if (filters.value.start_date)
      baseParams.start_date = filters.value.start_date
    if (filters.value.end_date) baseParams.end_date = filters.value.end_date

    const pageSize = 100
    let page = 1
    let totalDeleted = 0

    let hasMore = true
    while (hasMore) {
      const params = { ...baseParams, page, page_size: pageSize }
      console.log('🔵 [RecordsPage] 批量删除抓取页:', params)
      const resp = await recordApi.getRecords(params)
      const rawData: any = resp?.data ?? {}
      const results: any[] = Array.isArray(rawData.results)
        ? rawData.results
        : Array.isArray(rawData)
          ? rawData
          : []

      console.log(`🔵 [RecordsPage] 第${page}页记录数量:`, results.length)
      if (!results.length) break

      const ids: number[] = results
        .map((r: any) => r?.id)
        .filter((id: any) => typeof id === 'number')

      for (const id of ids) {
        try {
          await deleteRecord(id)
          totalDeleted += 1
        } catch (e) {
          console.error('🔴 [RecordsPage] 删除记录失败，ID:', id, e)
        }
      }

      hasMore = results.length === pageSize
      if (hasMore) page += 1
    }

    showDeleteAllModal.value = false
    await loadRecords()
    await fetchStatistics()
    await updateTodayMedicineTypes()
    console.log('🟢 [RecordsPage] 批量删除完成，总计删除:', totalDeleted)
  } catch (e) {
    console.error('🔴 [RecordsPage] 批量删除异常:', e)
  }
}

/**
 * 计算当日用药种类（改为调用后端聚合接口）
 */
const updateTodayMedicineTypes = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    console.log(
      '🔵 [RecordsPage] 调用后端聚合接口获取当日用药种类，日期:',
      today
    )
    const resp = await recordApi.getTodayMedicineTypes(today)

    const data: any = resp?.data ?? {}
    const count = (data?.count ?? 0) as number

    todayMedicineTypesCount.value = Number(count) || 0
    console.log(
      '🟢 [RecordsPage] 当日用药种类（来自后端聚合）:',
      todayMedicineTypesCount.value
    )
  } catch (e) {
    if (isRequestCancelledError(e)) {
      console.log('🟡 [RecordsPage] 获取当日用药种类请求已取消')
      return
    }

    console.error('🔴 [RecordsPage] 获取当日用药种类失败:', e)
    todayMedicineTypesCount.value = 0
  }
}

// 生命周期
// 使用watchEffect监听认证状态变化
const dataLoaded = ref(false)

watchEffect(async () => {
  console.log('🔵 [RecordsPage] watchEffect触发，检查认证状态')
  console.log('🔵 [RecordsPage] isAuthenticated:', authStore.isAuthenticated)
  console.log(
    '🔵 [RecordsPage] localStorage access_token:',
    !!localStorage.getItem('access_token')
  )
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
      await updateTodayMedicineTypes()
      console.log('🔵 [RecordsPage] 数据加载完成')
    } catch (error) {
      if (isRequestCancelledError(error)) {
        console.log('🟡 [RecordsPage] 初始化数据请求已取消')
        return
      }

      console.error('🔴 [RecordsPage] 数据加载失败:', error)
      // 不重置dataLoaded状态，避免无限循环
      // 用户可以通过刷新页面或重新登录来重试
    }
  }
})

onMounted(() => {
  console.log('🔵 [RecordsPage] 组件挂载完成')
})

// 表单操作
const closeForm = () => {
  showCreateForm.value = false
  showEditForm.value = false
  editingRecord.value = null
}

const handleFormSuccess = async () => {
  closeForm()
  // 重新加载数据
  await loadRecords()
  await fetchStatistics()
  await updateTodayMedicineTypes()
}
</script>
