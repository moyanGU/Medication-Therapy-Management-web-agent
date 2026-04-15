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
            <RefreshCw
              :class="{ 'animate-spin': loading }"
              class="w-4 h-4 mr-2"
            />
            刷新
          </button>
          <router-link to="/reminders/create" class="btn-primary">
            <Plus class="w-4 h-4 mr-2" />
            新建提醒
          </router-link>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mt-4">
        <button
          :class="[
            'cta-btn',
            pushSubscribed ? 'success' : 'primary',
          ]"
          @click="subscribePush"
          :disabled="subscribing || pushBusy"
        >
          {{
            subscribing || pushBusy
              ? '处理中...'
              : pushSubscribed
                ? '订阅成功'
                : '订阅提醒'
          }}
        </button>
        <button
          :class="['cta-btn', pushSubscribed ? 'secondary' : 'muted']"
          @click="unsubscribePush"
          :disabled="pushBusy"
        >
          {{ pushBusy ? '处理中...' : pushSubscribed ? '取消订阅' : '已取消' }}
        </button>
        <button class="cta-btn outline" @click="testLocal" :disabled="pushBusy">
          {{ pushBusy ? '处理中...' : '测试通知' }}
        </button>
      </div>
      <p class="mt-2 text-sm" :class="pushHintType === 'success' ? 'text-green-600' : 'text-gray-600'">
        {{ pushHintText }}
      </p>
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
            <p class="text-2xl font-bold text-gray-900">
              {{ stats.total_reminders ?? 0 }}
            </p>
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
            <p class="text-2xl font-bold text-gray-900">
              {{ stats.active_reminders ?? 0 }}
            </p>
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
            <p class="text-2xl font-bold text-gray-900">
              {{ stats.today_reminders ?? 0 }}
            </p>
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
            <p class="text-2xl font-bold text-gray-900">
              {{ stats.response_rate ?? 0 }}%
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <!-- 搜索框 -->
        <div class="relative">
          <Search
            class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4"
          />
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
          :class="['quick-filter-btn', quickFilter === 'all' ? 'active' : '']"
        >
          全部
        </button>
        <button
          @click="setQuickFilter('today')"
          :class="['quick-filter-btn', quickFilter === 'today' ? 'active' : '']"
        >
          今日提醒
        </button>
        <button
          @click="setQuickFilter('active')"
          :class="[
            'quick-filter-btn',
            quickFilter === 'active' ? 'active' : '',
          ]"
        >
          活跃提醒
        </button>
        <button
          @click="setQuickFilter('expired')"
          :class="[
            'quick-filter-btn',
            quickFilter === 'expired' ? 'active' : '',
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
            <button @click="batchDelete" class="btn-sm btn-danger">
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
          <div
            class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
          ></div>
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
            <router-link to="/reminders/create" class="btn-primary">
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
            'border-l-4 border-l-gray-300': !reminder.is_active,
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
                      reminder.is_active ? 'status-active' : 'status-inactive',
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
                    {{ reminder.dosage }}
                    {{ getDosageUnitLabel(reminder.dosage_unit) }}
                  </p>

                  <p class="text-sm text-gray-600">
                    <Clock class="inline w-4 h-4 mr-1" />
                    {{ formatTime(reminder.reminder_time) }}
                    <span class="mx-2">•</span>
                    {{ getFrequencyLabel(reminder.frequency) }}
                    <span class="mx-2">•</span>
                    {{ getMealTimingLabel(reminder.meal_timing) }}
                  </p>

                  <div
                    class="flex items-center space-x-4 text-sm text-gray-500"
                  >
                    <span>
                      <Calendar class="inline w-4 h-4 mr-1" />
                      {{ formatDate(reminder.start_date) }}
                      {{
                        reminder.end_date
                          ? ` - ${formatDate(reminder.end_date)}`
                          : ' 起'
                      }}
                    </span>

                    <span> 提醒 {{ reminder.reminder_count }} 次 </span>

                    <span> 响应 {{ reminder.response_count }} 次 </span>

                    <span v-if="reminder.reminder_count > 0">
                      响应率
                      {{
                        Math.round(
                          (reminder.response_count / reminder.reminder_count) *
                            100
                        )
                      }}%
                    </span>
                  </div>

                  <div
                    v-if="reminder.special_instructions"
                    class="text-sm text-gray-600"
                  >
                    <FileText class="inline w-4 h-4 mr-1" />
                    {{ reminder.special_instructions }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="flex flex-wrap items-center gap-2">
              <button
                @click="quickTake(reminder)"
                class="btn-sm rounded-lg bg-green-600 px-3 py-2 text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="isConfirmingReminder(reminder.id) || !reminder.is_active"
              >
                已服药
              </button>

              <button
                @click="quickMiss(reminder)"
                class="btn-sm rounded-lg bg-rose-600 px-3 py-2 text-white transition hover:bg-rose-700 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="isConfirmingReminder(reminder.id) || !reminder.is_active"
              >
                漏服
              </button>

              <button
                @click="
                  actionPanelReminderId === reminder.id
                    ? closeActionPanel()
                    : openActionPanel(reminder)
                "
                class="btn-sm rounded-lg border border-slate-200 bg-white px-3 py-2 text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="isConfirmingReminder(reminder.id) || !reminder.is_active"
              >
                <MoreHorizontal class="mr-1 inline h-4 w-4" />
                更多处理
              </button>

              <button
                @click="toggleReminderActive(reminder)"
                :class="[
                  'btn-sm',
                  reminder.is_active ? 'btn-secondary' : 'btn-primary',
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

          <div
            v-if="actionPanelReminderId === reminder.id"
            class="mt-4 rounded-2xl border border-sky-100 bg-sky-50/70 p-4"
          >
            <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <p class="text-sm font-medium text-slate-900">补充处理这次提醒</p>
                <p class="mt-1 text-sm text-slate-600">
                  如果不是直接已服药或漏服，可以在这里补充说明。
                </p>
              </div>
              <button
                class="inline-flex items-center gap-1 self-start text-sm text-slate-500 hover:text-slate-700"
                @click="closeActionPanel"
              >
                <XCircle class="h-4 w-4" />
                收起
              </button>
            </div>

            <div class="mt-4 flex flex-wrap gap-2">
              <button
                class="rounded-full px-3 py-1 text-sm transition"
                :class="
                  actionPanelMode === 'delayed'
                    ? 'bg-sky-600 text-white'
                    : 'border border-slate-200 bg-white text-slate-700'
                "
                @click="openActionPanel(reminder, 'delayed')"
              >
                <Clock3 class="mr-1 inline h-4 w-4" />
                延迟服用
              </button>
              <button
                class="rounded-full px-3 py-1 text-sm transition"
                :class="
                  actionPanelMode === 'partial'
                    ? 'bg-sky-600 text-white'
                    : 'border border-slate-200 bg-white text-slate-700'
                "
                @click="openActionPanel(reminder, 'partial')"
              >
                <CheckCircle class="mr-1 inline h-4 w-4" />
                部分服用
              </button>
            </div>

            <div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
              <label v-if="actionPanelMode === 'delayed'" class="block">
                <span class="mb-2 block text-sm font-medium text-slate-700">延迟了多久</span>
                <input
                  v-model.number="actionForm.delay_minutes"
                  type="number"
                  min="1"
                  class="input-field"
                  placeholder="例如 15"
                />
              </label>

              <label v-if="actionPanelMode === 'partial'" class="block">
                <span class="mb-2 block text-sm font-medium text-slate-700">
                  实际服用了多少
                </span>
                <input
                  v-model.number="actionForm.quantity_taken"
                  type="number"
                  min="1"
                  :max="Math.max(reminder.dosage - 1, 1)"
                  class="input-field"
                  placeholder="请输入实际服用数量"
                />
                <p class="mt-1 text-xs text-slate-500">
                  本次提醒剂量是 {{ reminder.dosage }} {{ getDosageUnitLabel(reminder.dosage_unit) }}
                </p>
              </label>

              <label class="block md:col-span-2">
                <span class="mb-2 block text-sm font-medium text-slate-700">备注</span>
                <textarea
                  v-model="actionForm.notes"
                  rows="2"
                  class="input-field"
                  placeholder="可选，方便你回头查看这次为什么没按原计划执行"
                ></textarea>
              </label>
            </div>

            <div class="mt-4 flex flex-wrap gap-3">
              <button
                v-if="actionPanelMode === 'delayed'"
                class="rounded-xl bg-sky-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="isConfirmingReminder(reminder.id)"
                @click="submitDelayedAction(reminder)"
              >
                记录为延迟服用
              </button>
              <button
                v-if="actionPanelMode === 'partial'"
                class="rounded-xl bg-sky-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="isConfirmingReminder(reminder.id)"
                @click="submitPartialAction(reminder)"
              >
                记录为部分服用
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div
      v-if="pagination.total > pagination.page_size"
      class="pagination-wrapper"
    >
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-700">
          显示第 {{ (pagination.page - 1) * pagination.page_size + 1 }} -
          {{
            Math.min(pagination.page * pagination.page_size, pagination.total)
          }}
          条， 共 {{ pagination.total }} 条记录
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
                page === pagination.page ? 'btn-primary' : 'btn-secondary',
              ]"
            >
              {{ page }}
            </button>
          </div>

          <button
            @click="changePage(pagination.page + 1)"
            :disabled="
              pagination.page >=
              Math.ceil(pagination.total / pagination.page_size)
            "
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
import { useToast } from '@/composables/useToast'
import { useReminderStore } from '@/stores/reminder'
import { debounce } from 'lodash-es'
import { notificationService } from '@/services/notificationService'
import { isRequestCancelledError } from '@/utils/api'
import {
  subscribeAndSave,
  unsubscribeAndCleanup,
  showLocalTestNotification,
  getCurrentSubscription,
} from '@/services/pushService'
import {
  Bell,
  CheckCircle,
  Clock,
  Clock3,
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
  ChevronRight,
  MoreHorizontal,
  XCircle,
} from 'lucide-vue-next'
import type { ReminderConfirmPayload } from '@/services/reminderService'

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
const { success, error } = useToast()

const reminderStore = useReminderStore()
const loading = computed(() => reminderStore.loading)
const reminders = computed<Reminder[]>(() => reminderStore.reminders as any)
const stats = ref<Stats>({
  total_reminders: 0,
  active_reminders: 0,
  today_reminders: 0,
  response_rate: 0,
})

const searchQuery = ref('')
const quickFilter = ref('all')
const selectedReminders = ref<number[]>([])
const actionPanelReminderId = ref<number | null>(null)
const actionPanelMode = ref<'delayed' | 'partial'>('delayed')
const actionLoadingReminderId = ref<number | null>(null)
const actionForm = reactive({
  delay_minutes: 15,
  quantity_taken: 1,
  notes: '',
})

const filters = reactive({
  is_active: '',
  frequency: '',
  meal_timing: '',
})

const pagination = reactive<Pagination>({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0,
})

const subscribing = ref(false)
const pushBusy = ref(false)
const pushSubscribed = ref(false)
const pushHintType = ref<'default' | 'success'>('default')
const pushHintText = ref('未订阅')

// 计算属性
const hasFilters = computed(() => {
  return (
    searchQuery.value ||
    filters.is_active !== '' ||
    filters.frequency ||
    filters.meal_timing ||
    quickFilter.value !== 'all'
  )
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
    if (isRequestCancelledError(err)) {
      console.log('获取提醒列表请求已取消')
      return
    }

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
      response_rate: 0,
    }
    console.log('[Reminders] 统计数据(store):', data)
  } catch (err: any) {
    if (isRequestCancelledError(err)) {
      console.log('获取统计数据请求已取消')
      return
    }

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
const toggleReminderActive = async (reminder: Reminder) => {
  try {
    console.log('[Reminders] 切换提醒状态(store):', reminder.id)
    const result = await reminderStore.toggleReminderActive(reminder.id)
    if (result) {
      success(`提醒已${result.is_active ? '启用' : '停用'}`)
      await fetchReminders()
      await fetchStats()
    }
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
  if (
    !confirm(`确定要删除提醒"${reminder.title || reminder.medicine_name}"吗？`)
  )
    return
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
      is_active: isActive,
    })
    success(
      `已${isActive ? '启用' : '停用'} ${selectedReminders.value.length} 个提醒`
    )
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
  if (!confirm(`确定要删除选中的 ${selectedReminders.value.length} 个提醒吗？`))
    return
  try {
    await reminderStore.batchDeleteReminders({
      reminder_ids: selectedReminders.value,
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

/**
 * 订阅通知入口
 */
const subscribePush = async () => {
  try {
    pushBusy.value = true
    if (!notificationService.isSupported()) {
      pushHintType.value = 'default'
      pushHintText.value = '当前浏览器不支持通知订阅'
      error('当前浏览器不支持通知订阅')
      return
    }
    const insecureContext =
      typeof window !== 'undefined' &&
      !window.isSecureContext &&
      !['localhost', '127.0.0.1', '::1'].includes(window.location.hostname)
    if (insecureContext) {
      pushHintType.value = 'default'
      pushHintText.value = '当前站点不是 HTTPS 或 localhost，浏览器会禁用通知订阅'
      error('当前站点不是 HTTPS 或 localhost，浏览器会禁用通知订阅')
      return
    }
    const currentPermission = notificationService.getPermission()
    if (currentPermission === 'denied') {
      pushHintType.value = 'default'
      pushHintText.value = '通知权限已被禁用，请点击地址栏左侧图标重新允许通知'
      error('通知权限已被禁用，请点击地址栏左侧图标重新允许通知')
      return
    }
    const perm = await notificationService.requestPermission()
    if (perm.permission !== 'granted') {
      pushHintType.value = 'default'
      pushHintText.value =
        perm.permission === 'default'
          ? '通知权限尚未授权，请允许通知后重试'
          : '通知权限未开启，无法订阅'
      error(pushHintText.value)
      return
    }
    subscribing.value = true
    await subscribeAndSave()
    pushSubscribed.value = true
    pushHintType.value = 'success'
    pushHintText.value = '订阅成功'
    success('订阅成功')
  } catch (e: any) {
    pushHintType.value = 'default'
    pushHintText.value = '订阅失败'
    error(e?.message || '订阅失败')
  } finally {
    subscribing.value = false
    pushBusy.value = false
  }
}

/**
 * 取消订阅
 */
const unsubscribePush = async () => {
  try {
    pushBusy.value = true
    const unsubscribed = await unsubscribeAndCleanup()
    if (unsubscribed) {
      pushSubscribed.value = false
      pushHintType.value = 'default'
      pushHintText.value = '已取消'
      success('已取消')
      return
    }
    pushSubscribed.value = false
    pushHintType.value = 'default'
    pushHintText.value = '当前未订阅'
    success('当前未订阅')
  } catch (e: any) {
    pushHintType.value = 'default'
    pushHintText.value = '取消失败'
    error(e?.message || '取消订阅失败')
  } finally {
    pushBusy.value = false
  }
}

/**
 * 测试本地通知
 */
const testLocal = async () => {
  try {
    pushBusy.value = true
    const result = await showLocalTestNotification()
    pushHintType.value = 'success'
    pushHintText.value =
      result.channel === 'sw'
        ? '测试通知已触发（Service Worker）'
        : '测试通知已触发（页面通知）'
    success('测试通知已触发')
  } catch (e: any) {
    pushHintType.value = 'default'
    pushHintText.value = '测试通知失败'
    error(e?.message || '测试通知失败')
  } finally {
    pushBusy.value = false
  }
}

const syncPushSubscriptionState = async () => {
  try {
    const sub = await getCurrentSubscription()
    pushSubscribed.value = !!sub
    pushHintType.value = sub ? 'success' : 'default'
    pushHintText.value = sub ? '订阅成功' : '未订阅'
  } catch (e) {
    console.error('[Reminders] 同步推送订阅状态失败:', e)
    pushSubscribed.value = false
    pushHintType.value = 'default'
    pushHintText.value = '未订阅'
  }
}

/**
 * 打开提醒快捷处理面板
 */
const openActionPanel = (
  reminder: Reminder,
  mode: 'delayed' | 'partial' = 'delayed'
) => {
  actionPanelReminderId.value = reminder.id
  actionPanelMode.value = mode
  actionForm.delay_minutes = 15
  actionForm.quantity_taken = Math.max(1, reminder.dosage - 1)
  actionForm.notes = ''
}

/**
 * 关闭快捷处理面板
 */
const closeActionPanel = () => {
  actionPanelReminderId.value = null
  actionForm.delay_minutes = 15
  actionForm.quantity_taken = 1
  actionForm.notes = ''
}

/**
 * 执行提醒确认动作并刷新列表与统计
 */
const confirmReminder = async (
  reminder: Reminder,
  payload: ReminderConfirmPayload
) => {
  try {
    actionLoadingReminderId.value = reminder.id
    console.log('[Reminders] confirmReminder:start', {
      id: reminder.id,
      payload,
    })
    const result = await reminderStore.confirmReminderAction(reminder.id, payload)
    if (result) {
      success(confirmActionSuccessText(payload.action))
      closeActionPanel()
      await fetchReminders()
      await fetchStats()
    }
  } catch (err: any) {
    console.error('[Reminders] confirmReminder:error', err)
    error(err?.message || '提醒处理失败')
  } finally {
    actionLoadingReminderId.value = null
  }
}

/**
 * 列表页快捷标记已服药
 */
const quickTake = async (reminder: Reminder) => {
  await confirmReminder(reminder, {
    action: 'taken',
    notes: '列表页快捷标记已服药',
  })
}

/**
 * 列表页快捷标记漏服
 */
const quickMiss = async (reminder: Reminder) => {
  await confirmReminder(reminder, {
    action: 'missed',
    notes: '列表页快捷标记漏服',
  })
}

/**
 * 提交延迟服用
 */
const submitDelayedAction = async (reminder: Reminder) => {
  if (!actionForm.delay_minutes || actionForm.delay_minutes <= 0) {
    error('请填写延迟分钟数')
    return
  }
  await confirmReminder(reminder, {
    action: 'delayed',
    delay_minutes: actionForm.delay_minutes,
    notes: actionForm.notes || '列表页标记延迟服用',
  })
}

/**
 * 提交部分服用
 */
const submitPartialAction = async (reminder: Reminder) => {
  if (!actionForm.quantity_taken || actionForm.quantity_taken <= 0) {
    error('请填写实际服用数量')
    return
  }
  if (actionForm.quantity_taken >= reminder.dosage) {
    error('部分服用数量必须小于提醒剂量')
    return
  }
  await confirmReminder(reminder, {
    action: 'partial',
    quantity_taken: actionForm.quantity_taken,
    notes: actionForm.notes || '列表页标记部分服用',
  })
}

/**
 * 生成动作成功提示文案
 */
const confirmActionSuccessText = (action: ReminderConfirmPayload['action']) => {
  const texts: Record<ReminderConfirmPayload['action'], string> = {
    taken: '已记录为已服药',
    missed: '已记录为漏服',
    delayed: '已记录为延迟服用',
    partial: '已记录为部分服用',
  }
  return texts[action]
}

/**
 * 判断当前提醒是否正在执行动作
 */
const isConfirmingReminder = (reminderId: number) =>
  actionLoadingReminderId.value === reminderId

// 格式化函数
const formatTime = (time: string) => {
  return new Date(`2000-01-01T${time}`).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
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
    custom: '自定义',
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
    anytime: '任意时间',
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
    patch: '贴',
  }
  return labels[unit] || unit
}

// 监听器
watch(
  [() => filters.is_active, () => filters.frequency, () => filters.meal_timing],
  () => {
    pagination.page = 1
    fetchReminders()
  }
)

// 生命周期
onMounted(() => {
  fetchReminders()
  fetchStats()
  syncPushSubscriptionState()
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

.cta-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  padding: 14px 18px;
  font-size: 16px;
  font-weight: 600;
}
.cta-btn.primary {
  background: #2563eb;
  color: #fff;
}
.cta-btn.warn {
  background: #ef4444;
  color: #fff;
}
.cta-btn.success {
  background: #16a34a;
  color: #fff;
}
.cta-btn.secondary {
  background: #64748b;
  color: #fff;
}
.cta-btn.muted {
  background: #e5e7eb;
  color: #6b7280;
}
.cta-btn.outline {
  background: #fff;
  border: 1px solid #cbd5e1;
  color: #374151;
}
.cta-btn.toggle {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #111827;
}
.cta-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
