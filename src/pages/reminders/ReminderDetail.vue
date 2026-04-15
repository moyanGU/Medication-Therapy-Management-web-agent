<template>
  <div class="reminder-detail-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <button @click="handleGoBack" class="back-btn">
            <ArrowLeft class="w-4 h-4" />
          </button>
          <div>
            <h1 class="page-title">提醒详情</h1>
            <p class="page-description">查看提醒设置和执行历史</p>
          </div>
        </div>
        <div class="header-right" v-if="reminder">
          <button
            @click="testNotification"
            class="btn btn-outline"
            :disabled="loading"
          >
            <Volume2 class="w-4 h-4 mr-2" />
            测试通知
          </button>
          <button
            @click="toggleActive"
            :class="['btn', reminder.is_active ? 'btn-warning' : 'btn-success']"
            :disabled="loading"
          >
            <component
              :is="reminder.is_active ? PauseCircleIcon : PlayCircleIcon"
              class="w-4 h-4 mr-2"
            />
            {{ reminder.is_active ? '停用提醒' : '启用提醒' }}
          </button>
          <router-link
            :to="`/reminders/${reminder.id}/edit`"
            class="btn btn-primary"
          >
            <Edit class="w-4 h-4 mr-2" />
            编辑提醒
          </router-link>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && !reminder" class="loading-state">
      <div class="flex items-center justify-center py-12">
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
        ></div>
        <span class="ml-3 text-gray-600">加载中...</span>
      </div>
    </div>

    <!-- 提醒详情 -->
    <div v-else-if="reminder" class="detail-content">
      <!-- 基本信息卡片 -->
      <div class="info-card">
        <div class="card-header">
          <div class="flex items-center space-x-3">
            <div
              class="status-indicator"
              :class="reminder.is_active ? 'active' : 'inactive'"
            >
              <Bell class="w-5 h-5" />
            </div>
            <div>
              <h2 class="card-title">
                {{ reminder.title || reminder.medicine_name }}
              </h2>
              <p class="card-subtitle">
                <span
                  :class="[
                    'status-badge',
                    reminder.is_active ? 'status-active' : 'status-inactive',
                  ]"
                >
                  {{ reminder.is_active ? '活跃' : '停用' }}
                </span>
                <span class="mx-2">•</span>
                创建于 {{ formatDateTime(reminder.created_at) }}
              </p>
            </div>
          </div>
        </div>

        <div class="card-content">
          <div class="info-grid">
            <!-- 药品信息 -->
            <div class="info-item">
              <div class="info-label">
                <Pill class="w-4 h-4 mr-2" />
                药品信息
              </div>
              <div class="info-value">
                <div class="font-medium">{{ reminder.medicine_name }}</div>
                <div class="text-sm text-gray-600">
                  {{ medicineObj?.specification || '无规格信息' }}
                </div>
                <div class="text-sm text-gray-600">
                  {{
                    getMedicineTypeText(medicineObj?.medicine_type) ||
                    '无类型信息'
                  }}
                </div>
              </div>
            </div>

            <!-- 剂量信息 -->
            <div class="info-item">
              <div class="info-label">
                <Calculator class="w-4 h-4 mr-2" />
                服用剂量
              </div>
              <div class="info-value">
                <span class="text-lg font-semibold">{{ reminder.dosage }}</span>
                <span class="ml-1">{{
                  getDosageUnitLabel(reminder.dosage_unit)
                }}</span>
              </div>
            </div>

            <!-- 提醒时间 -->
            <div class="info-item">
              <div class="info-label">
                <Clock class="w-4 h-4 mr-2" />
                提醒时间
              </div>
              <div class="info-value">
                <span class="text-lg font-semibold">{{
                  formatTime(reminder.reminder_time)
                }}</span>
              </div>
            </div>

            <!-- 提醒频率 -->
            <div class="info-item">
              <div class="info-label">
                <Repeat class="w-4 h-4 mr-2" />
                提醒频率
              </div>
              <div class="info-value">
                <div class="font-medium">
                  {{ getFrequencyLabel(reminder.frequency) }}
                </div>
                <div
                  v-if="
                    reminder.frequency === 'custom' &&
                    reminder.weekdays.length > 0
                  "
                  class="text-sm text-gray-600"
                >
                  {{ getWeekdaysDisplay(reminder.weekdays) }}
                </div>
              </div>
            </div>

            <!-- 用药时机 -->
            <div class="info-item">
              <div class="info-label">
                <Utensils class="w-4 h-4 mr-2" />
                用药时机
              </div>
              <div class="info-value">
                {{ getMealTimingLabel(reminder.meal_timing) }}
              </div>
            </div>

            <!-- 有效期 -->
            <div class="info-item">
              <div class="info-label">
                <Calendar class="w-4 h-4 mr-2" />
                有效期
              </div>
              <div class="info-value">
                <div>{{ formatDate(reminder.start_date) }}</div>
                <div class="text-sm text-gray-600">
                  {{
                    reminder.end_date
                      ? `至 ${formatDate(reminder.end_date)}`
                      : '长期有效'
                  }}
                </div>
              </div>
            </div>
          </div>

          <!-- 高级设置 -->
          <div v-if="hasAdvancedSettings" class="advanced-settings">
            <h3 class="settings-title">
              <Settings class="w-4 h-4 mr-2" />
              高级设置
            </h3>
            <div class="settings-grid">
              <div v-if="reminder.advance_minutes > 0" class="setting-item">
                <span class="setting-label">提前提醒:</span>
                <span class="setting-value"
                  >{{ reminder.advance_minutes }} 分钟</span
                >
              </div>
              <div v-if="reminder.repeat_interval > 0" class="setting-item">
                <span class="setting-label">重复间隔:</span>
                <span class="setting-value"
                  >{{ reminder.repeat_interval }} 分钟</span
                >
              </div>
              <div v-if="reminder.max_repeats > 0" class="setting-item">
                <span class="setting-label">最大重复:</span>
                <span class="setting-value">{{ reminder.max_repeats }} 次</span>
              </div>
              <div
                v-if="reminder.notification_types.length > 0"
                class="setting-item"
              >
                <span class="setting-label">通知方式:</span>
                <span class="setting-value">{{
                  getNotificationTypesDisplay(reminder.notification_types)
                }}</span>
              </div>
            </div>
          </div>

          <!-- 特殊说明 -->
          <div
            v-if="reminder.special_instructions"
            class="special-instructions"
          >
            <h3 class="instructions-title">
              <FileText class="w-4 h-4 mr-2" />
              特殊说明
            </h3>
            <p class="instructions-content">
              {{ reminder.special_instructions }}
            </p>
          </div>

          <!-- 自定义消息 -->
          <div v-if="reminder.message" class="custom-message">
            <h3 class="message-title">
              <MessageSquare class="w-4 h-4 mr-2" />
              自定义消息
            </h3>
            <p class="message-content">{{ reminder.message }}</p>
          </div>
        </div>
      </div>

      <!-- 统计信息卡片 -->
      <div class="stats-card">
        <div class="card-header">
          <h2 class="card-title">
            <BarChart3 class="w-5 h-5 mr-2" />
            执行统计
          </h2>
        </div>
        <div class="card-content">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ reminder.reminder_count ?? 0 }}</div>
              <div class="stat-label">总提醒次数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ reminder.response_count ?? 0 }}</div>
              <div class="stat-label">响应次数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ responseRate }}%</div>
              <div class="stat-label">响应率</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ consecutiveDays }}</div>
              <div class="stat-label">连续天数</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快速处理 -->
      <div class="stats-card">
        <div class="card-header">
          <h2 class="card-title">
            <CheckCircle class="w-5 h-5 mr-2" />
            快速处理这次提醒
          </h2>
        </div>
        <div class="card-content">
          <div class="space-y-4">
            <p class="text-sm text-gray-600">
              如果你已经处理了这次提醒，可以直接在这里记录结果，后续会自动进入记录和统计。
            </p>

            <div class="flex flex-wrap gap-3">
              <button
                @click="submitTaken"
                class="btn btn-success"
                :disabled="confirmLoading || !reminder.is_active"
              >
                <Check class="w-4 h-4 mr-2" />
                已服药
              </button>
              <button
                @click="submitMissed"
                class="btn btn-warning"
                :disabled="confirmLoading || !reminder.is_active"
              >
                <XCircle class="w-4 h-4 mr-2" />
                漏服
              </button>
            </div>

            <div class="flex flex-wrap gap-2">
              <button
                class="btn btn-outline"
                :class="{ 'ring-2 ring-blue-200': confirmMode === 'delayed' }"
                :disabled="confirmLoading || !reminder.is_active"
                @click="confirmMode = 'delayed'"
              >
                <Clock3 class="w-4 h-4 mr-2" />
                延迟服用
              </button>
              <button
                class="btn btn-outline"
                :class="{ 'ring-2 ring-blue-200': confirmMode === 'partial' }"
                :disabled="confirmLoading || !reminder.is_active"
                @click="confirmMode = 'partial'"
              >
                <CheckCircle class="w-4 h-4 mr-2" />
                部分服用
              </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label v-if="confirmMode === 'delayed'" class="block">
                <span class="block text-sm font-medium text-gray-700 mb-2">延迟了多久</span>
                <input
                  v-model.number="confirmForm.delay_minutes"
                  type="number"
                  min="1"
                  class="filter-select w-full"
                  placeholder="例如 15"
                />
              </label>

              <label v-if="confirmMode === 'partial'" class="block">
                <span class="block text-sm font-medium text-gray-700 mb-2">实际服用了多少</span>
                <input
                  v-model.number="confirmForm.quantity_taken"
                  type="number"
                  min="1"
                  :max="Math.max(reminder.dosage - 1, 1)"
                  class="filter-select w-full"
                  placeholder="请输入实际服用数量"
                />
                <p class="mt-1 text-xs text-gray-500">
                  本次提醒剂量是 {{ reminder.dosage }} {{ getDosageUnitLabel(reminder.dosage_unit) }}
                </p>
              </label>

              <label class="block md:col-span-2">
                <span class="block text-sm font-medium text-gray-700 mb-2">备注</span>
                <textarea
                  v-model="confirmForm.notes"
                  rows="3"
                  class="filter-select w-full"
                  placeholder="可选，方便你之后回看这次为什么没按原计划执行"
                ></textarea>
              </label>
            </div>

            <div class="flex flex-wrap gap-3">
              <button
                v-if="confirmMode === 'delayed'"
                @click="submitDelayed"
                class="btn btn-primary"
                :disabled="confirmLoading || !reminder.is_active"
              >
                记录为延迟服用
              </button>
              <button
                v-if="confirmMode === 'partial'"
                @click="submitPartial"
                class="btn btn-primary"
                :disabled="confirmLoading || !reminder.is_active"
              >
                记录为部分服用
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 执行历史 -->
      <div class="history-card">
        <div class="card-header">
          <div class="flex items-center justify-between">
            <h2 class="card-title">
              <History class="w-5 h-5 mr-2" />
              执行历史
            </h2>
            <div class="flex items-center space-x-2">
              <select v-model="historyFilter" class="filter-select">
                <option value="all">全部记录</option>
                <option value="responded">已响应</option>
                <option value="missed">未响应</option>
                <option value="failed">失败</option>
                <option value="pending">待发送</option>
                <option value="recent">最近7天</option>
              </select>
              <div class="flex items-center space-x-2 text-xs text-gray-600">
                <span>总{{ historyStats.total }}</span>
                <span class="text-green-600"
                  >已响应{{ historyStats.responded }}</span
                >
                <span class="text-yellow-600"
                  >待发送{{ historyStats.pending }}</span
                >
                <span class="text-red-600">失败{{ historyStats.failed }}</span>
              </div>
              <button @click="refreshHistory" class="btn btn-sm btn-outline">
                <RefreshCw
                  :class="{ 'animate-spin': historyLoading }"
                  class="w-4 h-4"
                />
              </button>
            </div>
          </div>
        </div>

        <div class="card-content">
          <div v-if="historyLoading" class="loading-state">
            <div class="flex items-center justify-center py-8">
              <div
                class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"
              ></div>
              <span class="ml-3 text-gray-600">加载历史记录...</span>
            </div>
          </div>

          <div v-else-if="filteredHistory.length === 0" class="empty-state">
            <div class="text-center py-8">
              <History class="mx-auto h-8 w-8 text-gray-400" />
              <h3 class="mt-2 text-sm font-medium text-gray-900">
                暂无执行记录
              </h3>
              <p class="mt-1 text-sm text-gray-500">还没有执行记录</p>
            </div>
          </div>

          <div v-else class="history-list">
            <div
              v-for="record in filteredHistory"
              :key="record.id"
              class="history-item"
              :class="{
                responded: record.is_responded,
                missed:
                  !record.is_responded && isPastDue(record.scheduled_time),
              }"
            >
              <div class="history-icon">
                <component
                  :is="getHistoryIcon(record)"
                  class="w-4 h-4"
                  :class="getHistoryIconClass(record)"
                />
              </div>

              <div class="history-content">
                <div class="history-main">
                  <div class="history-time">
                    {{ formatDateTime(record.scheduled_time) }}
                  </div>
                  <div class="history-status">
                    <span
                      :class="['status-badge', getHistoryStatusClass(record)]"
                    >
                      {{ getHistoryStatusText(record) }}
                    </span>
                  </div>
                </div>

                <div v-if="record.is_responded" class="history-details">
                  <div class="detail-item">
                    <span class="detail-label">响应时间:</span>
                    <span class="detail-value">{{
                      formatDateTime(record.responded_at)
                    }}</span>
                  </div>
                  <div v-if="record.response_delay_minutes" class="detail-item">
                    <span class="detail-label">延迟:</span>
                    <span class="detail-value"
                      >{{ record.response_delay_minutes }} 分钟</span
                    >
                  </div>
                  <div v-if="record.notes" class="detail-item">
                    <span class="detail-label">备注:</span>
                    <span class="detail-value">{{ record.notes }}</span>
                  </div>
                </div>

                <div
                  v-if="!record.is_responded && !isPastDue(record.scheduled_time)"
                  class="history-actions"
                >
                  <span class="text-xs text-gray-500">
                    这条记录还没处理，请使用上方“快速处理这次提醒”来记录结果。
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div v-if="historyPagination.total > 0" class="history-pagination">
            <div class="flex items-center justify-between">
              <div class="text-sm text-gray-700">
                显示第
                {{
                  (historyPagination.page - 1) * historyPagination.pageSize + 1
                }}
                -
                {{
                  Math.min(
                    historyPagination.page * historyPagination.pageSize,
                    historyPagination.total
                  )
                }}
                条， 共 {{ historyPagination.total }} 条记录
              </div>

              <div class="flex items-center space-x-2">
                <button
                  @click="changeHistoryPage(historyPagination.page - 1)"
                  :disabled="historyPagination.page <= 1"
                  class="btn btn-sm btn-outline"
                >
                  <ChevronLeft class="w-4 h-4" />
                </button>

                <span class="text-sm text-gray-600">
                  {{ historyPagination.page }} /
                  {{ historyPagination.totalPages }}
                </span>

                <button
                  @click="changeHistoryPage(historyPagination.page + 1)"
                  :disabled="
                    historyPagination.page >= historyPagination.totalPages
                  "
                  class="btn btn-sm btn-outline"
                >
                  <ChevronRight class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-state">
      <div class="text-center py-12">
        <AlertCircle class="mx-auto h-12 w-12 text-red-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">加载失败</h3>
        <p class="mt-1 text-sm text-gray-500">无法加载提醒详情</p>
        <div class="mt-6">
          <button @click="loadReminderData" class="btn btn-primary">
            重试
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useReminderStore } from '@/stores/reminder'
import { useToast } from '@/composables/useToast'
import { isRequestCancelledError } from '@/utils/api'
import { showLocalTestNotification } from '@/services/pushService'
import {
  ArrowLeft,
  Bell,
  Edit,
  Volume2,
  PauseCircle as PauseCircleIcon,
  PlayCircle as PlayCircleIcon,
  Pill,
  Calculator,
  Clock,
  Repeat,
  Utensils,
  Calendar,
  Settings,
  FileText,
  MessageSquare,
  BarChart3,
  History,
  RefreshCw,
  Check,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock3,
} from 'lucide-vue-next'
import type {
  Reminder,
  ReminderConfirmPayload,
  ReminderHistory,
} from '@/services/reminderService'

const router = useRouter()
const route = useRoute()
const reminderStore = useReminderStore()
const toast = useToast()

// 响应式数据
const loading = ref(false)
const historyLoading = ref(false)
const reminder = ref<Reminder | null>(null)
const historyFilter = ref('all')
const confirmLoading = ref(false)
const confirmMode = ref<'delayed' | 'partial'>('delayed')
const confirmForm = ref({
  delay_minutes: 15,
  quantity_taken: 1,
  notes: '',
})

const reminderId = computed(() => Number(route.params.id))

// 计算属性
// 将可能为 number 的 medicine 收窄为对象，避免模板访问 union 类型属性时报 TS 错误
const medicineObj = computed(() => {
  const m = reminder.value?.medicine as any
  return m && typeof m === 'object' ? m : undefined
})

const responseRate = computed(() => {
  if (!reminder.value || reminder.value.reminder_count === 0) return 0
  return Math.round(
    (reminder.value.response_count / reminder.value.reminder_count) * 100
  )
})

/**
 * 计算连续服药天数
 * 从历史记录中按天汇总 is_responded=true 的记录，按日期倒序计算连续天数。
 * 注意：受分页影响（当前仅加载前 20 条），该值为近记录范围的估算值，但不再使用模拟数据。
 */
const consecutiveDays = computed(() => {
  const history = reminderHistory.value
  const respondedDays = new Set<string>()
  for (const h of history) {
    if (h.is_responded) {
      const key = new Date(h.scheduled_time).toISOString().split('T')[0]
      respondedDays.add(key)
    }
  }
  let count = 0
  const d = new Date()
  let key = d.toISOString().split('T')[0]
  while (respondedDays.has(key)) {
    count += 1
    d.setDate(d.getDate() - 1)
    key = d.toISOString().split('T')[0]
    if (count > 365) break
  }
  return count
})

const hasAdvancedSettings = computed(() => {
  if (!reminder.value) return false
  return (
    reminder.value.advance_minutes > 0 ||
    reminder.value.repeat_interval > 0 ||
    reminder.value.max_repeats > 0 ||
    reminder.value.notification_types.length > 0
  )
})

const reminderHistory = computed(() => reminderStore.reminderHistory)
const historyPagination = computed(() => reminderStore.historyPagination)

const historyStats = computed(() => {
  const history = reminderHistory.value
  const failed = history.filter(h => h.status === 'failed').length
  const pending = history.filter(h => h.status === 'pending').length
  const responded = history.filter(h => h.is_responded).length
  return {
    total: history.length,
    failed,
    pending,
    responded,
  }
})

const filteredHistory = computed(() => {
  let history = reminderHistory.value

  switch (historyFilter.value) {
    case 'responded':
      history = history.filter(h => h.is_responded)
      break
    case 'missed':
      history = history.filter(
        h => !h.is_responded && isPastDue(h.scheduled_time)
      )
      break
    case 'failed':
      history = history.filter(h => h.status === 'failed')
      break
    case 'pending':
      history = history.filter(h => h.status === 'pending')
      break
    case 'recent': {
      const sevenDaysAgo = new Date()
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
      history = history.filter(h => new Date(h.scheduled_time) >= sevenDaysAgo)
      break
    }
  }

  return history
})

// 生命周期
onMounted(() => {
  loadReminderData()
  loadHistoryData()
})

// 监听器
watch(historyFilter, () => {
  loadHistoryData()
})

// 方法
/**
 * 加载提醒详情
 * 来源：调用 useReminderStore.fetchReminder(id)
 * 处理：将返回的 Reminder 对象写入本地状态 reminder
 * 注意：保留关键日志，便于控制台调试
 */
const loadReminderData = async () => {
  try {
    loading.value = true
    console.log('[ReminderDetail] loadReminderData:start', {
      id: reminderId.value,
    })
    const data = await reminderStore.fetchReminder(reminderId.value)
    reminder.value = data
    if (reminder.value) {
      confirmForm.value.quantity_taken = Math.max(1, reminder.value.dosage - 1)
    }
    console.log('[ReminderDetail] loadReminderData:success', {
      reminder: reminder.value,
    })
  } catch (error) {
    if (isRequestCancelledError(error)) {
      console.log('[ReminderDetail] loadReminderData:cancelled')
      return
    }

    console.error('[ReminderDetail] loadReminderData:error', error)
    toast.error('加载提醒详情失败')
  } finally {
    loading.value = false
  }
}

/**
 * 加载提醒执行历史
 * 来源：调用 useReminderStore.fetchReminderHistory(filters)
 * 处理：写入 store 的 reminderHistory 与 historyPagination 状态
 * 注意：保留关键日志，便于控制台调试
 */
const loadHistoryData = async () => {
  try {
    historyLoading.value = true
    console.log('[ReminderDetail] loadHistoryData:start', {
      filter: historyFilter.value,
      id: reminderId.value,
    })
    const params: Record<string, any> = {
      reminder: reminderId.value,
      page: 1,
      page_size: 20,
    }
    if (historyFilter.value === 'responded') {
      params.is_responded = true
    } else if (historyFilter.value === 'missed') {
      params.is_responded = false
    } else if (historyFilter.value === 'failed') {
      params.status = 'failed'
    } else if (historyFilter.value === 'pending') {
      params.status = 'pending'
    } else if (historyFilter.value === 'recent') {
      params.time_range = 'last_7_days'
    }
    await reminderStore.fetchReminderHistory({
      ...params,
    })
    console.log('[ReminderDetail] loadHistoryData:success', {
      count: reminderStore.reminderHistory.length,
      pagination: reminderStore.historyPagination,
    })
  } catch (error) {
    if (isRequestCancelledError(error)) {
      console.log('[ReminderDetail] loadHistoryData:cancelled')
      return
    }

    console.error('[ReminderDetail] loadHistoryData:error', error)
    toast.error('加载执行历史失败')
  } finally {
    historyLoading.value = false
  }
}

/**
 * 刷新历史记录
 */
const refreshHistory = () => {
  console.log('[ReminderDetail] refreshHistory')
  loadHistoryData()
}

/**
 * 切换历史分页
 * @param page 目标页码
 * 说明：使用 reminderStore.fetchReminderHistory 进行分页查询，并记录关键日志。
 */
const changeHistoryPage = (page: number) => {
  if (page >= 1 && page <= historyPagination.value.totalPages) {
    console.log('[ReminderDetail] changeHistoryPage', { page })
    reminderStore.fetchReminderHistory({
      reminder: reminderId.value,
      page,
      page_size: 20,
    })
  }
}

/**
 * 返回提醒列表
 */
const handleGoBack = () => {
  console.log('[ReminderDetail] handleGoBack')
  router.push('/reminders')
}

/**
 * 切换提醒启停状态
 */
const toggleActive = async () => {
  if (!reminder.value) return

  try {
    console.log('[ReminderDetail] toggleActive', { id: reminder.value.id })
    const result = await reminderStore.toggleReminderActive(reminder.value.id)
    if (result) {
      reminder.value = result
      toast.success(`提醒已${result.is_active ? '启用' : '停用'}`)
    }
  } catch (error) {
    console.error('[ReminderDetail] toggleActive:error', error)
    toast.error('切换提醒状态失败')
  }
}

/**
 * 发送测试通知
 */
const testNotification = async () => {
  if (!reminder.value) return

  try {
    console.log('[ReminderDetail] testNotification', { id: reminder.value.id })
    const result = await reminderStore.testNotification(reminder.value.id)
    if (!result.success) {
      toast.error(result.message || '发送测试通知失败')
      return
    }

    try {
      await showLocalTestNotification()
      if (result.delivered) {
        toast.success('测试通知已触发，已显示本地提示框')
      } else {
        toast.warning('服务器通知通道不可用，已显示本地测试提示框')
      }
    } catch (notifyError: any) {
      toast.warning(notifyError?.message || '本地提示框触发失败')
    }
  } catch (error) {
    console.error('[ReminderDetail] testNotification:error', error)
    toast.error('发送测试通知失败')
  }
}

/**
 * 执行提醒确认动作并刷新详情与历史
 */
const submitReminderConfirm = async (payload: ReminderConfirmPayload) => {
  if (!reminder.value) return

  try {
    confirmLoading.value = true
    console.log('[ReminderDetail] submitReminderConfirm:start', {
      reminderId: reminder.value.id,
      payload,
    })
    const result = await reminderStore.confirmReminderAction(reminder.value.id, payload)
    if (result) {
      toast.success(confirmActionSuccessText(payload.action))
      await loadReminderData()
      await loadHistoryData()
      confirmForm.value.notes = ''
    }
  } catch (error) {
    console.error('[ReminderDetail] submitReminderConfirm:error', error)
    toast.error('提醒处理失败')
  } finally {
    confirmLoading.value = false
  }
}

/**
 * 快速标记已服药
 */
const submitTaken = async () => {
  await submitReminderConfirm({
    action: 'taken',
    notes: '详情页标记已服药',
  })
}

/**
 * 快速标记漏服
 */
const submitMissed = async () => {
  await submitReminderConfirm({
    action: 'missed',
    notes: '详情页标记漏服',
  })
}

/**
 * 提交延迟服用
 */
const submitDelayed = async () => {
  if (!confirmForm.value.delay_minutes || confirmForm.value.delay_minutes <= 0) {
    toast.error('请填写延迟分钟数')
    return
  }

  await submitReminderConfirm({
    action: 'delayed',
    delay_minutes: confirmForm.value.delay_minutes,
    notes: confirmForm.value.notes || '详情页标记延迟服用',
  })
}

/**
 * 提交部分服用
 */
const submitPartial = async () => {
  if (!reminder.value) return
  if (!confirmForm.value.quantity_taken || confirmForm.value.quantity_taken <= 0) {
    toast.error('请填写实际服用数量')
    return
  }
  if (confirmForm.value.quantity_taken >= reminder.value.dosage) {
    toast.error('部分服用数量必须小于提醒剂量')
    return
  }

  await submitReminderConfirm({
    action: 'partial',
    quantity_taken: confirmForm.value.quantity_taken,
    notes: confirmForm.value.notes || '详情页标记部分服用',
  })
}

/**
 * 生成提醒确认动作的成功提示文案
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
 * 工具方法：格式化时间为 HH:mm
 * @param time 形如 "HH:mm:ss" 或 "HH:mm" 的时间字符串
 * @returns 本地化的小时:分钟展示
 */
const formatTime = (time: string) => {
  return new Date(`2000-01-01T${time}`).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * 工具方法：格式化日期
 * @param date ISO日期字符串
 * @returns 本地化的日期展示
 */
const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

/**
 * 工具方法：格式化日期时间
 * @param datetime ISO日期时间字符串
 * @returns 本地化的日期时间展示
 */
const formatDateTime = (datetime: string) => {
  return new Date(datetime).toLocaleString('zh-CN')
}

/**
 * 获取药品类型中文文本
 * @param type 药品类型英文枚举
 * @returns 中文标签
 */
const getMedicineTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    tablet: '片剂',
    capsule: '胶囊',
    liquid: '液体',
    injection: '注射剂',
    ointment: '软膏',
    powder: '粉剂',
    other: '其他',
  }
  return typeMap[type] || type
}

/**
 * 获取剂量单位中文文本
 * @param unit 剂量单位英文枚举
 * @returns 中文标签
 */
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
    injection: '针',
  }
  return labels[unit] || unit
}

/**
 * 获取频次中文文本
 * @param frequency 频次英文枚举
 * @returns 中文标签
 */
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

/**
 * 获取与进餐关系中文文本
 * @param timing 英文枚举
 * @returns 中文标签
 */
const getMealTimingLabel = (timing: string) => {
  const labels: Record<string, string> = {
    before_meal: '餐前',
    with_meal: '餐中',
    after_meal: '餐后',
    anytime: '任意时间',
    before_breakfast: '早饭前',
    after_dinner: '晚饭后',
    before_bed: '睡前',
  }
  return labels[timing] || timing
}

/**
 * 将星期数字数组转为中文展示
 * @param weekdays 数组（1-7，对应周一-周日）
 * @returns 形如 "周一、周三、周五"
 */
const getWeekdaysDisplay = (weekdays: number[]) => {
  const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  return weekdays.map(day => dayNames[day - 1]).join('、')
}

/**
 * 通知类型数组转中文展示
 * @param types 通知类型英文数组
 * @returns 中文标签拼接
 */
const getNotificationTypesDisplay = (types: string[]) => {
  const typeLabels: Record<string, string> = {
    push: '推送',
    sound: '声音',
    vibration: '震动',
    email: '邮件',
  }
  return types.map(type => typeLabels[type] || type).join('、')
}

/**
 * 判断计划时间是否已过期
 * @param scheduledTime ISO时间
 * @returns 是否已过当前时间
 */
const isPastDue = (scheduledTime: string) => {
  return new Date(scheduledTime) < new Date()
}

/**
 * 根据历史记录状态返回图标组件
 * @param record 历史记录
 * @returns lucide 图标组件
 */
const getHistoryIcon = (record: ReminderHistory) => {
  if (record.status === 'failed') {
    return XCircle
  }
  if (record.status === 'pending') {
    return Clock3
  }
  if (record.is_responded) {
    return CheckCircle
  } else if (isPastDue(record.scheduled_time)) {
    return XCircle
  } else {
    return Clock3
  }
}

/**
 * 根据历史记录状态返回图标颜色类
 * @param record 历史记录
 * @returns tailwind 文本颜色类
 */
const getHistoryIconClass = (record: ReminderHistory) => {
  if (record.status === 'failed') {
    return 'text-red-500'
  }
  if (record.status === 'pending') {
    return 'text-yellow-500'
  }
  if (record.is_responded) {
    return 'text-green-500'
  } else if (isPastDue(record.scheduled_time)) {
    return 'text-red-500'
  } else {
    return 'text-yellow-500'
  }
}

const getHistoryStatusText = (record: ReminderHistory) => {
  if (record.status === 'failed') return '失败'
  if (record.status === 'pending') return '待发送'
  if (record.is_responded) return '已响应'
  return '未响应'
}

const getHistoryStatusClass = (record: ReminderHistory) => {
  if (record.status === 'failed') return 'status-error'
  if (record.status === 'pending') return 'status-warning'
  if (record.is_responded) return 'status-success'
  return 'status-warning'
}
</script>

<style scoped lang="postcss">
.reminder-detail-page {
  @apply max-w-6xl mx-auto p-6 space-y-6;
}

/* 页面头部 */
.page-header {
  @apply bg-white rounded-lg shadow-sm border p-6;
}

.header-content {
  @apply flex items-center justify-between;
}

.header-left {
  @apply flex items-center space-x-4;
}

.back-btn {
  @apply p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors;
}

.page-title {
  @apply text-2xl font-bold text-gray-900;
}

.page-description {
  @apply text-gray-600 mt-1;
}

.header-right {
  @apply flex items-center space-x-3;
}

/* 详情内容 */
.detail-content {
  @apply space-y-6;
}

/* 卡片样式 */
.info-card,
.stats-card,
.history-card {
  @apply bg-white rounded-lg shadow-sm border;
}

.card-header {
  @apply px-6 py-4 border-b border-gray-200;
}

.card-title {
  @apply flex items-center text-lg font-semibold text-gray-900;
}

.card-subtitle {
  @apply flex items-center text-sm text-gray-600 mt-1;
}

.card-content {
  @apply p-6;
}

/* 状态指示器 */
.status-indicator {
  @apply flex items-center justify-center w-12 h-12 rounded-full;
}

.status-indicator.active {
  @apply bg-green-100 text-green-600;
}

.status-indicator.inactive {
  @apply bg-gray-100 text-gray-600;
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

.status-success {
  @apply bg-green-100 text-green-800;
}

.status-warning {
  @apply bg-yellow-100 text-yellow-800;
}

.status-error {
  @apply bg-red-100 text-red-800;
}

/* 信息网格 */
.info-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6;
}

.info-item {
  @apply space-y-2;
}

.info-label {
  @apply flex items-center text-sm font-medium text-gray-600;
}

.info-value {
  @apply text-gray-900;
}

/* 高级设置 */
.advanced-settings {
  @apply mt-6 pt-6 border-t border-gray-200;
}

.settings-title {
  @apply flex items-center text-base font-medium text-gray-900 mb-4;
}

.settings-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4;
}

.setting-item {
  @apply flex justify-between items-center py-2;
}

.setting-label {
  @apply text-sm text-gray-600;
}

.setting-value {
  @apply text-sm font-medium text-gray-900;
}

/* 特殊说明和自定义消息 */
.special-instructions,
.custom-message {
  @apply mt-6 pt-6 border-t border-gray-200;
}

.instructions-title,
.message-title {
  @apply flex items-center text-base font-medium text-gray-900 mb-2;
}

.instructions-content,
.message-content {
  @apply text-gray-700 leading-relaxed;
}

/* 统计网格 */
.stats-grid {
  @apply grid grid-cols-2 md:grid-cols-4 gap-6;
}

.stat-item {
  @apply text-center;
}

.stat-value {
  @apply text-2xl font-bold text-gray-900;
}

.stat-label {
  @apply text-sm text-gray-600 mt-1;
}

/* 历史记录 */
.filter-select {
  @apply px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.history-list {
  @apply space-y-4;
}

.history-item {
  @apply flex items-start space-x-3 p-4 border border-gray-200 rounded-lg;
}

.history-item.responded {
  @apply bg-green-50 border-green-200;
}

.history-item.missed {
  @apply bg-red-50 border-red-200;
}

.history-icon {
  @apply flex-shrink-0 mt-1;
}

.history-content {
  @apply flex-1 space-y-2;
}

.history-main {
  @apply flex items-center justify-between;
}

.history-time {
  @apply font-medium text-gray-900;
}

.history-status {
  @apply flex items-center;
}

.history-details {
  @apply space-y-1 text-sm text-gray-600;
}

.detail-item {
  @apply flex items-center space-x-2;
}

.detail-label {
  @apply font-medium;
}

.detail-value {
  @apply text-gray-900;
}

.history-actions {
  @apply flex items-center space-x-2;
}

.history-pagination {
  @apply mt-6 pt-4 border-t border-gray-200;
}

/* 状态页面 */
.loading-state,
.empty-state,
.error-state {
  @apply bg-white rounded-lg shadow-sm border;
}

/* 按钮样式 */
.btn {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
  @apply text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500;
}

.btn-success {
  @apply text-white bg-green-600 hover:bg-green-700 focus:ring-green-500;
}

.btn-warning {
  @apply text-white bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500;
}

.btn-outline {
  @apply text-gray-700 bg-white border-gray-300 hover:bg-gray-50 focus:ring-blue-500;
}

.btn-sm {
  @apply px-3 py-1.5 text-xs;
}
</style>
