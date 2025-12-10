<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">用药提醒</h1>
            <p class="text-gray-600 mt-1">设置和管理您的用药提醒</p>
          </div>
          <div class="flex items-center gap-3">
            <button class="px-5 py-3 rounded-xl text-white bg-blue-600 hover:bg-blue-700 text-base font-semibold" @click="openCreate">添加提醒</button>
            <button class="px-5 py-3 rounded-xl border border-blue-600 text-blue-700 bg-white hover:bg-blue-50 text-base font-semibold" @click="downloadIcs">下载日历订阅ICS</button>
          </div>
        </div>
        <div class="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
          <button class="cta-btn primary" @click="subscribePush" :disabled="subscribing">{{ subscribing ? '订阅中...' : '订阅通知' }}</button>
          <button class="cta-btn warn" @click="unsubscribePush">取消订阅</button>
          <button class="cta-btn outline" @click="testLocal">测试通知</button>
          <button class="cta-btn toggle" @click="toggleSenior">{{ isSenior ? '老年人模式：开' : '老年人模式：关' }}</button>
          <button class="cta-btn toggle" :disabled="!isSpeechSupported" @click="toggleSpeech">{{ isSpeechEnabled ? '语音播报：开' : '语音播报：关' }}</button>
        </div>
      </div>

      <!-- 今日提醒概览 -->
      <div class="bg-white rounded-lg shadow mb-6 p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">今日提醒</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-600">
              {{ stats?.total_reminders ?? 0 }}
            </div>
            <div class="text-sm text-gray-600">总提醒数</div>
          </div>
          <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-600">
              {{ completedToday }}
            </div>
            <div class="text-sm text-gray-600">已完成</div>
          </div>
          <div class="text-center p-4 bg-orange-50 rounded-lg" :class="pendingCount > 0 ? 'glow-danger' : ''">
            <div class="text-2xl font-bold text-orange-600">
              {{ stats?.today_reminders ?? 0 }}
            </div>
            <div class="text-sm text-gray-600">今日待提醒</div>
          </div>
        </div>
      </div>

      <!-- 待你确认（未响应） -->
      <div class="bg-white rounded-lg shadow mb-6 p-6" v-if="pendingCount > 0">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-medium text-gray-900">待确认</h3>
          <button class="px-3 py-1.5 text-sm rounded border bg-white hover:bg-gray-50" @click="reloadToday">刷新</button>
        </div>
        <div class="space-y-3">
          <div
            v-for="h in pendingToday"
            :key="h.id"
            class="flex items-center justify-between p-4 rounded border glow-danger"
          >
            <div>
              <div class="text-sm font-medium text-gray-900">
                {{ h.reminder_title || h.medicine_name || '用药提醒' }}
              </div>
              <div class="text-xs text-gray-600 mt-1">
                计划时间 {{ h.scheduled_time }} · 发送时间 {{ h.sent_at }}
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button class="btn-respond success" @click="respond(h.id, 'taken')">已服药</button>
              <button class="btn-respond warn" @click="respond(h.id, 'skipped')">未服药</button>
              <button class="btn-respond" @click="respond(h.id, 'delayed')">稍后</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 提醒列表 -->
      <div class="space-y-6">
        <!-- 活跃提醒 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">活跃提醒</h3>
          </div>
          <div class="divide-y divide-gray-200">
            <div
              v-if="activeReminders.length === 0"
              class="px-6 py-8 text-center text-gray-500"
            >
              暂无活跃提醒
            </div>
            <div v-for="r in activeReminders" :key="r.id" class="px-6 py-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                  <div class="flex-shrink-0">
                    <img
                      src="/icons/app-icon.svg"
                      alt="药品图片"
                      class="w-12 h-12 rounded-lg object-cover bg-gray-100"
                    />
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">
                      {{ r.title || r.medicine_name || '用药提醒' }}
                    </h4>
                    <p class="text-sm text-gray-600">
                      {{ r.dosage }} {{ r.dosage_unit }}
                    </p>
                    <div class="flex items-center space-x-4 mt-1">
                      <span class="text-xs text-gray-500"
                        >提醒时间 {{ r.reminder_time }}</span
                      >
                      <span
                        v-if="r.meal_timing"
                        class="text-xs text-gray-500"
                        >{{ r.meal_timing }}</span
                      >
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-4">
                  <div class="text-right">
                    <div class="text-sm font-medium text-gray-900">状态</div>
                    <div
                      class="text-sm"
                      :class="r.is_active ? 'text-green-600' : 'text-gray-600'"
                    >
                      {{ r.is_active ? '进行中' : '已停用' }}
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <label
                      class="relative inline-flex items-center cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        :checked="r.is_active"
                        class="sr-only peer"
                        @change="toggleActive(r)"
                      />
                      <div
                        class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
                      ></div>
                    </label>
                    <button class="text-gray-400 hover:text-gray-500">
                      <svg
                        class="h-5 w-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
                        ></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 已暂停的提醒（真实数据） -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">已暂停的提醒</h3>
          </div>
          <div class="divide-y divide-gray-200">
            <div
              v-if="pausedReminders.length === 0"
              class="px-6 py-8 text-center text-gray-500"
            >
              暂无已暂停提醒
            </div>
            <div
              v-for="r in pausedReminders"
              :key="r.id"
              class="px-6 py-4 opacity-80"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                  <div class="flex-shrink-0">
                    <img
                      src="/icons/app-icon.svg"
                      alt="药品图片"
                      class="w-12 h-12 rounded-lg object-cover bg-gray-100"
                    />
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-900">
                      {{ r.title || r.medicine_name || '用药提醒' }}
                    </h4>
                    <p class="text-sm text-gray-600">
                      {{ r.dosage }} {{ r.dosage_unit }}
                    </p>
                    <div class="flex items-center space-x-4 mt-1">
                      <span class="text-xs text-gray-500"
                        >提醒时间 {{ r.reminder_time }}</span
                      >
                      <span
                        v-if="r.meal_timing"
                        class="text-xs text-gray-500"
                        >{{ r.meal_timing }}</span
                      >
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-4">
                  <div class="text-right">
                    <div class="text-sm font-medium text-gray-500">已暂停</div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <label
                      class="relative inline-flex items-center cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        :checked="false"
                        class="sr-only peer"
                        @change="toggleActive(r)"
                      />
                      <div
                        class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
                      ></div>
                    </label>
                    <button class="text-gray-400 hover:text-gray-500">
                      <svg
                        class="h-5 w-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
                        ></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 依从性统计 -->
        <div class="bg-white rounded-lg shadow">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">依从性统计</h3>
          </div>
          <div class="p-6">
            <div class="mb-4 flex items-center justify-between">
              <div class="text-sm text-gray-600">过去 {{ metrics?.period_days ?? selectedDays }} 天统计</div>
              <select v-model.number="selectedDays" @change="reloadMetrics" class="px-2 py-1 border rounded text-sm">
                <option :value="7">7天</option>
                <option :value="30">30天</option>
              </select>
            </div>
            <div v-if="(metrics?.response_rate ?? 0) < 60 || (metrics?.failed ?? 0) > (metrics?.sent ?? 0) * 0.2" class="mb-4 rounded border border-red-300 bg-red-50 text-red-700 px-3 py-2 text-sm">
              <div class="font-medium">指标异常告警</div>
              <div>
                <span v-if="(metrics?.response_rate ?? 0) < 60">响应率偏低（当前 {{ metrics?.response_rate ?? 0 }}%），建议优化提醒策略与通道覆盖。</span>
                <span v-if="(metrics?.failed ?? 0) > (metrics?.sent ?? 0) * 0.2" class="ml-2">失败率偏高（当前 {{ metrics?.failed ?? 0 }}/{{ metrics?.sent ?? 0 }}），请检查网络/权限与短信通道配置。</span>
              </div>
            </div>
            <div v-if="(metrics?.warnings?.length ?? 0) > 0" class="mb-4 rounded border border-yellow-300 bg-yellow-50 text-yellow-700 px-3 py-2 text-sm">
              <div class="font-medium">系统告警</div>
              <ul class="list-disc list-inside">
                <li v-for="(w,i) in metrics.warnings" :key="i">{{ w }}</li>
              </ul>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-3">
                  本周依从性
                </h4>
                <div class="space-y-2">
                  <div class="flex justify-between text-sm">
                    <span>已发送</span>
                    <span class="font-medium text-green-600">{{
                      metrics?.sent ?? 0
                    }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span>响应率</span>
                    <span
                      :class="
                        (metrics?.response_rate ?? 0) < 60
                          ? 'font-medium text-red-600'
                          : 'font-medium text-blue-600'
                      "
                      >{{ metrics?.response_rate ?? 0 }}%</span
                    >
                  </div>
                </div>
                <div class="space-y-2 mt-4">
                  <div class="flex justify-between text-sm">
                    <span>平均延迟(分钟)</span>
                    <span class="font-medium text-yellow-600">{{
                      metrics?.avg_response_delay_minutes ?? 0
                    }}</span>
                  </div>
                </div>
                <div class="space-y-2 mt-4">
                  <div class="flex justify-between text-sm">
                    <span>失败</span>
                    <span
                      :class="
                        (metrics?.failed ?? 0) > (metrics?.sent ?? 0) * 0.2
                          ? 'font-medium text-red-700'
                          : 'font-medium text-red-600'
                      "
                      >{{ metrics?.failed ?? 0 }}</span
                    >
                  </div>
                  <div class="flex justify-between text-xs text-gray-600">
                    <span>失败率</span>
                    <span>{{ failRate }}%</span>
                  </div>
                  <div class="flex justify-between text-xs text-gray-600">
                    <span>Push失败</span>
                    <span>{{ metrics?.channel?.push_failed ?? 0 }}</span>
                  </div>
                  <div class="flex justify-between text-xs text-gray-600">
                    <span>短信失败</span>
                    <span>{{ metrics?.channel?.sms_failed ?? 0 }}</span>
                  </div>
                  <div class="flex justify-between text-xs text-gray-600">
                    <span>邮箱失败</span>
                    <span>{{ metrics?.channel?.email_failed ?? 0 }}</span>
                  </div>
                  <div class="pt-3">
                    <button
                      class="inline-flex items-center px-3 py-1.5 border text-xs font-medium rounded bg-white border-gray-300 hover:bg-gray-50"
                      @click="exportMetricsCsv"
                    >
                      导出指标CSV
                    </button>
                  </div>
                </div>
              </div>
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-3">
                  提醒响应时间
                </h4>
                <div class="text-center">
                  <div class="text-3xl font-bold text-blue-600">
                    {{ metrics?.avg_response_delay_minutes ?? 0 }}
                  </div>
                  <div class="text-sm text-gray-600">分钟</div>
                  <div class="text-xs text-gray-500 mt-1">
                    过去{{ metrics?.period_days ?? 7 }}天平均响应时间
                  </div>
                </div>
                <div class="mt-4 space-y-2">
                  <div class="flex justify-between text-sm">
                    <span>Push渠道</span>
                    <span class="font-medium">{{
                      metrics?.channel?.push_sent ?? 0
                    }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span>短信渠道</span>
                    <span class="font-medium">{{
                      metrics?.channel?.sms_sent ?? 0
                    }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span>邮箱渠道</span>
                    <span class="font-medium">{{
                      metrics?.channel?.email_sent ?? 0
                    }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span>通道升级成功率</span>
                    <span class="font-medium text-indigo-600"
                      >{{
                        metrics?.escalation?.escalation_success_rate ?? 0
                      }}%</span
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { api } from '@/utils/api'
import { ref, onMounted, computed } from 'vue'
import {
  reminderService,
  type ReminderStats,
  type ReminderHistory,
  type Reminder,
} from '@/services/reminderService'
import { notificationService } from '@/services/notificationService'
import { subscribeAndSave, unsubscribeAndCleanup, showLocalTestNotification } from '@/services/pushService'
import { useTheme } from '@/composables/useTheme'
import { useSpeech } from '@/composables/useSpeech'

const downloading = ref(false)
const stats = ref<ReminderStats | null>(null)
const todayHistory = ref<ReminderHistory[]>([])
const pendingToday = ref<ReminderHistory[]>([])
const activeReminders = ref<Reminder[]>([])
const pausedReminders = ref<Reminder[]>([])
const metrics = ref<any | null>(null)
const selectedDays = ref<number>(7)
const subscribing = ref(false)
const { isSenior, toggleSenior: toggleSeniorMode } = useTheme()
const { isSpeechEnabled, isSpeechSupported, toggleSpeech: toggleSpeechMode, speak } = useSpeech()
const completedToday = computed(() => {
  return todayHistory.value.filter(
    h => h.is_responded && h.response_type === 'taken'
  ).length
})
const pendingCount = computed(() => pendingToday.value.length)
const failRate = computed(() => {
  const m = metrics.value
  const sent = (m?.sent ?? 0) as number
  const failed = (m?.failed ?? 0) as number
  if (!sent) return 0
  return Math.round((failed / sent) * 10000) / 100
})

async function downloadIcs() {
  if (downloading.value) return
  downloading.value = true
  try {
    await api.download('/calendar/ics/', 'mtm-reminders.ics')
  } finally {
    downloading.value = false
  }
}

function openCreate() {
  window.location.href = '/reminders/create'
}

async function subscribePush() {
  try {
    const perm = await notificationService.requestPermission()
    if (perm.permission !== 'granted') return
    subscribing.value = true
    await subscribeAndSave()
  } finally {
    subscribing.value = false
  }
}

async function unsubscribePush() {
  await unsubscribeAndCleanup()
}

async function testLocal() {
  await showLocalTestNotification()
}

function toggleSenior() {
  toggleSeniorMode()
}

function toggleSpeech() {
  toggleSpeechMode()
  if (isSpeechEnabled.value) speak('语音播报已开启')
}

onMounted(async () => {
  try {
    const s = await reminderService.getReminderStats()
    stats.value = s.data
  } catch (e) {
    console.warn('[RemindersPage] getReminderStats failed', e)
  }
  try {
    const h = await reminderService.getTodayHistory()
    todayHistory.value = h.data || []
    pendingToday.value = (todayHistory.value || []).filter(x => !x.is_responded)
  } catch (e) {
    console.warn('[RemindersPage] getTodayHistory failed', e)
  }
  try {
    const r = await reminderService.getActiveReminders()
    activeReminders.value = r.data || []
  } catch (e) {
    console.warn('[RemindersPage] getActiveReminders failed', e)
  }
  try {
    const pr = await reminderService.getReminders({
      is_active: false,
      page_size: 50,
    })
    pausedReminders.value = (pr.data?.results || []) as Reminder[]
  } catch (e) {
    console.warn('[RemindersPage] getPausedReminders failed', e)
  }
  await reloadMetrics()
})

async function toggleActive(r: Reminder) {
  try {
    await reminderService.toggleReminderActive(r.id)
    const rlist = await reminderService.getActiveReminders()
    activeReminders.value = rlist.data || []
    const pr = await reminderService.getReminders({
      is_active: false,
      page_size: 50,
    })
    pausedReminders.value = (pr.data?.results || []) as Reminder[]
  } catch (e) {
    console.warn('[RemindersPage] toggleReminderActive failed', e)
  }
}

async function reloadToday() {
  try {
    const h = await reminderService.getTodayHistory()
    todayHistory.value = h.data || []
    pendingToday.value = (todayHistory.value || []).filter(x => !x.is_responded)
  } catch (e) {
    console.warn('[RemindersPage] reloadToday failed', e)
  }
}

async function respond(id: number, type: 'taken' | 'skipped' | 'delayed' | 'ignored') {
  try {
    console.log('[RemindersPage] respond', id, type)
    await reminderService.respondToReminder(id, { response_type: type })
    await reloadToday()
    await reloadMetrics()
  } catch (e) {
    console.warn('[RemindersPage] respond failed', e)
  }
}

function exportMetricsCsv() {
  const m = metrics.value || {}
  const rows = [
    ['period_days', m.period_days ?? ''],
    ['sent', m.sent ?? ''],
    ['failed', m.failed ?? ''],
    ['pending', m.pending ?? ''],
    ['avg_response_delay_minutes', m.avg_response_delay_minutes ?? ''],
    ['response_rate', m.response_rate ?? ''],
    ['push_sent', m.channel?.push_sent ?? ''],
    ['sms_sent', m.channel?.sms_sent ?? ''],
    ['email_sent', m.channel?.email_sent ?? ''],
    ['push_failed', m.channel?.push_failed ?? ''],
    ['sms_failed', m.channel?.sms_failed ?? ''],
    ['email_failed', m.channel?.email_failed ?? ''],
    ['escalated_total', m.escalation?.escalated_total ?? ''],
    ['escalated_sent', m.escalation?.escalated_sent ?? ''],
    ['escalation_success_rate', m.escalation?.escalation_success_rate ?? ''],
  ]
  const csv = rows.map(r => r.map(x => String(x)).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `metrics-${selectedDays.value}d-${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
async function reloadMetrics() {
  try {
    const m = await reminderService.getHistoryMetrics(selectedDays.value)
    metrics.value = m.data
  } catch (e) {
    console.warn('[RemindersPage] reloadMetrics failed', e)
  }
}
</script>

<style scoped>
@keyframes glowPulse {
  0% { box-shadow: 0 0 0px 0 rgba(239,68,68,0.6); }
  50% { box-shadow: 0 0 12px 4px rgba(239,68,68,0.6); }
  100% { box-shadow: 0 0 0px 0 rgba(239,68,68,0.6); }
}
.glow-danger {
  animation: glowPulse 1.6s ease-in-out infinite;
  border-color: #ef4444;
}
.btn-respond {
  padding: 6px 10px;
  font-size: 12px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: #fff;
}
.btn-respond.success { border-color: #16a34a; color: #16a34a; }
.btn-respond.warn { border-color: #dc2626; color: #dc2626; }
.cta-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  padding: 14px 18px;
  font-size: 16px;
  font-weight: 600;
}
.cta-btn.primary { background:#2563eb; color:#fff; }
.cta-btn.warn { background:#ef4444; color:#fff; }
.cta-btn.outline { background:#fff; border:1px solid #cbd5e1; color:#374151; }
.cta-btn.toggle { background:#f8fafc; border:1px solid #e2e8f0; color:#111827; }
.cta-btn:disabled { opacity:.6; cursor:not-allowed; }
</style>
