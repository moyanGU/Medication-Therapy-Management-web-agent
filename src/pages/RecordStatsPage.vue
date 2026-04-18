<template>
  <div class="min-h-screen bg-slate-50 py-8">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-slate-900">依从性统计</h1>
        <p class="mt-2 text-slate-600">
          看看最近执行得稳不稳，哪些天容易漏服或延迟。
        </p>
      </div>

      <div class="mb-8 rounded-2xl bg-white p-6 shadow-sm">
        <div class="flex flex-wrap items-end gap-4">
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">开始日期</label>
            <input
              v-model="dateRange.start"
              type="date"
              class="rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">结束日期</label>
            <input
              v-model="dateRange.end"
              type="date"
              class="rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">药品筛选</label>
            <select
              v-model="selectedMedicine"
              class="rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sky-500"
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
          <div class="flex gap-3">
            <button
              @click="loadData"
              class="rounded-xl bg-sky-600 px-4 py-2 text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="loading"
            >
              {{ loading ? '更新中...' : '更新数据' }}
            </button>
            <button
              @click="resetDateRange"
              class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-slate-700 transition hover:bg-slate-50"
              :disabled="loading"
            >
              最近30天
            </button>
          </div>
        </div>
      </div>

      <div class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
        <div
          v-for="card in summaryCards"
          :key="card.title"
          class="rounded-2xl bg-white p-6 shadow-sm"
        >
          <p class="text-sm text-slate-500">{{ card.title }}</p>
          <p class="mt-3 text-3xl font-semibold text-slate-900">{{ card.value }}</p>
          <p class="mt-2 text-sm text-slate-500">{{ card.description }}</p>
        </div>
      </div>

      <div class="mb-8 grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div class="rounded-2xl bg-white p-6 shadow-sm xl:col-span-2">
          <div class="mb-5 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">趋势变化</h2>
              <p class="mt-1 text-sm text-slate-500">
                每天的完成率和按时率，会直接反映最近执行是否稳定。
              </p>
            </div>
            <span
              class="rounded-full px-3 py-1 text-xs font-medium"
              :class="riskBadgeClass(adherence.current_period.risk_level)"
            >
              当前风险：{{ riskText(adherence.current_period.risk_level) }}
            </span>
          </div>

          <div v-if="adherence.trend.length" class="space-y-4">
            <div
              v-for="item in visibleTrend"
              :key="item.date"
              class="rounded-2xl border border-slate-100 bg-slate-50 p-4"
            >
              <div class="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p class="font-medium text-slate-900">{{ formatDate(item.date) }}</p>
                  <p class="mt-1 text-sm text-slate-500">
                    总任务 {{ item.total }}，完成 {{ item.completed }}，漏服 {{ item.missed }}
                  </p>
                </div>
                <div class="text-sm text-slate-600">
                  按时 {{ rateText(item.on_time_rate) }} · 完成 {{ rateText(item.adherence_rate) }}
                </div>
              </div>

              <div class="space-y-3">
                <div>
                  <div class="mb-1 flex items-center justify-between text-xs text-slate-500">
                    <span>完成率</span>
                    <span>{{ rateText(item.adherence_rate) }}</span>
                  </div>
                  <div class="h-2 rounded-full bg-slate-200">
                    <div
                      class="h-2 rounded-full bg-emerald-500 transition-all"
                      :style="{ width: `${item.adherence_rate}%` }"
                    ></div>
                  </div>
                </div>

                <div>
                  <div class="mb-1 flex items-center justify-between text-xs text-slate-500">
                    <span>按时率</span>
                    <span>{{ rateText(item.on_time_rate) }}</span>
                  </div>
                  <div class="h-2 rounded-full bg-slate-200">
                    <div
                      class="h-2 rounded-full bg-sky-500 transition-all"
                      :style="{ width: `${item.on_time_rate}%` }"
                    ></div>
                  </div>
                </div>
              </div>

              <div class="mt-3 flex flex-wrap gap-2">
                <span class="rounded-full bg-emerald-100 px-3 py-1 text-xs text-emerald-700">
                  已服药 {{ item.taken }}
                </span>
                <span class="rounded-full bg-amber-100 px-3 py-1 text-xs text-amber-700">
                  延迟 {{ item.delayed }}
                </span>
                <span class="rounded-full bg-sky-100 px-3 py-1 text-xs text-sky-700">
                  部分服用 {{ item.partial }}
                </span>
                <span class="rounded-full bg-rose-100 px-3 py-1 text-xs text-rose-700">
                  漏服 {{ item.missed }}
                </span>
              </div>
            </div>
          </div>

          <div
            v-else
            class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-8 text-center text-sm text-slate-500"
          >
            当前筛选区间还没有足够的依从性数据。
          </div>
        </div>

        <div class="space-y-6">
          <div class="rounded-2xl bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">风险提示</h2>
            <div class="mt-4 space-y-3">
              <div
                v-for="flag in currentRiskFlags"
                :key="flag"
                class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
              >
                {{ flag }}
              </div>
              <div
                v-if="!currentRiskFlags.length"
                class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"
              >
                当前筛选区间整体执行较稳定，没有明显异常。
              </div>
            </div>
          </div>

          <div class="rounded-2xl bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">提醒响应情况</h2>
            <div class="mt-4 space-y-4">
              <div>
                <div class="mb-1 flex items-center justify-between text-sm text-slate-500">
                  <span>响应率</span>
                  <span>{{ rateText(adherence.current_period.response_summary.response_rate) }}</span>
                </div>
                <div class="h-2 rounded-full bg-slate-200">
                  <div
                    class="h-2 rounded-full bg-violet-500 transition-all"
                    :style="{
                      width: `${adherence.current_period.response_summary.response_rate}%`,
                    }"
                  ></div>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div class="rounded-2xl bg-slate-50 p-4">
                  <p class="text-sm text-slate-500">已安排提醒</p>
                  <p class="mt-2 text-2xl font-semibold text-slate-900">
                    {{ adherence.current_period.response_summary.scheduled_count }}
                  </p>
                </div>
                <div class="rounded-2xl bg-slate-50 p-4">
                  <p class="text-sm text-slate-500">未响应</p>
                  <p class="mt-2 text-2xl font-semibold text-slate-900">
                    {{ adherence.current_period.response_summary.unresponded_count }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div class="rounded-2xl bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">两个周期对比</h2>
            <div class="mt-4 space-y-4">
              <div
                v-for="period in periodComparison"
                :key="period.title"
                class="rounded-2xl bg-slate-50 p-4"
              >
                <div class="flex items-center justify-between">
                  <p class="font-medium text-slate-900">{{ period.title }}</p>
                  <span class="text-sm text-slate-500">{{ rateText(period.rate) }}</span>
                </div>
                <div class="mt-3 h-2 rounded-full bg-slate-200">
                  <div
                    class="h-2 rounded-full transition-all"
                    :class="period.barClass"
                    :style="{ width: `${period.rate}%` }"
                  ></div>
                </div>
                <p class="mt-2 text-sm text-slate-500">{{ period.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-2xl bg-white p-6 shadow-sm">
        <h2 class="mb-4 text-lg font-semibold text-slate-900">药品库存概览</h2>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <div
            v-for="medicine in medicineInventory"
            :key="medicine.id"
            class="rounded-2xl border p-4"
            :class="inventoryCardClass(medicine.quantity)"
          >
            <div class="mb-2 flex items-center justify-between gap-3">
              <h3 class="truncate font-medium text-slate-900">{{ medicine.name }}</h3>
              <span
                class="rounded-full px-2 py-1 text-xs"
                :class="inventoryBadgeClass(medicine.quantity)"
              >
                {{ inventoryLevelText(medicine.quantity) }}
              </span>
            </div>
            <div class="space-y-1 text-sm text-slate-600">
              <p>剩余数量：{{ medicine.quantity }}</p>
              <p v-if="medicine.specification">规格：{{ medicine.specification }}</p>
              <p v-if="medicine.expiry_date">有效期：{{ formatDate(medicine.expiry_date) }}</p>
            </div>
          </div>
        </div>

        <div class="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div class="rounded-2xl border border-rose-200 bg-rose-50 p-4">
            <p class="text-sm text-rose-700">急需补充</p>
            <p class="mt-2 text-2xl font-semibold text-slate-900">{{ lowStockCount }} 种</p>
          </div>
          <div class="rounded-2xl border border-amber-200 bg-amber-50 p-4">
            <p class="text-sm text-amber-700">库存偏低</p>
            <p class="mt-2 text-2xl font-semibold text-slate-900">{{ mediumStockCount }} 种</p>
          </div>
          <div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
            <p class="text-sm text-emerald-700">库存充足</p>
            <p class="mt-2 text-2xl font-semibold text-slate-900">{{ goodStockCount }} 种</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { recordApi } from '@/api/record'
import { useMedicineStore } from '../stores/medicine'
import type {
  MedicationAdherencePeriodSummary,
  MedicationAdherenceSummary,
} from '../types/record'
import { isRequestCancelledError } from '@/utils/api'

const medicineStore = useMedicineStore()
const { fetchMedicines } = medicineStore
const { medicines: medicinesRef } = storeToRefs(medicineStore)
const medicines = computed(() => medicinesRef.value)

const loading = ref(false)
const dateRange = ref({
  start: '',
  end: '',
})
const selectedMedicine = ref('')
const medicineInventory = ref<any[]>([])
const adherence = ref<MedicationAdherenceSummary>({
  period: {
    start_date: '',
    end_date: '',
    days: 30,
    medicine_id: null,
  },
  summary_7d: createEmptyPeriodSummary(),
  summary_30d: createEmptyPeriodSummary(),
  current_period: createEmptyPeriodSummary(),
  trend: [],
})

function createEmptyPeriodSummary(): MedicationAdherencePeriodSummary {
  return {
    total_records: 0,
    taken_count: 0,
    missed_count: 0,
    delayed_count: 0,
    partial_count: 0,
    completed_count: 0,
    adherence_rate: 0,
    on_time_rate: 0,
    avg_delay_minutes: 0,
    risk_level: 'low',
    risk_flags: [],
    response_summary: {
      scheduled_count: 0,
      responded_count: 0,
      unresponded_count: 0,
      response_rate: 0,
    },
  }
}

const initDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 29)
  dateRange.value.end = end.toISOString().split('T')[0]
  dateRange.value.start = start.toISOString().split('T')[0]
}

const resetDateRange = async () => {
  initDateRange()
  await loadData()
}

const summaryCards = computed(() => [
  {
    title: '当前区间完成率',
    value: rateText(adherence.value.current_period.adherence_rate),
    description: `按时率 ${rateText(adherence.value.current_period.on_time_rate)}`,
  },
  {
    title: '近 7 天完成率',
    value: rateText(adherence.value.summary_7d.adherence_rate),
    description: `漏服 ${adherence.value.summary_7d.missed_count} 次`,
  },
  {
    title: '近 30 天完成率',
    value: rateText(adherence.value.summary_30d.adherence_rate),
    description: `延迟 ${adherence.value.summary_30d.delayed_count} 次`,
  },
  {
    title: '当前风险等级',
    value: riskText(adherence.value.current_period.risk_level),
    description: `已记录 ${adherence.value.current_period.total_records} 次处理结果`,
  },
])

const currentRiskFlags = computed(() => adherence.value.current_period.risk_flags)
const visibleTrend = computed(() => adherence.value.trend.slice(-14))

const periodComparison = computed(() => [
  {
    title: '近 7 天完成率',
    rate: adherence.value.summary_7d.adherence_rate,
    description: `按时率 ${rateText(adherence.value.summary_7d.on_time_rate)}`,
    barClass: 'bg-emerald-500',
  },
  {
    title: '近 30 天完成率',
    rate: adherence.value.summary_30d.adherence_rate,
    description: `按时率 ${rateText(adherence.value.summary_30d.on_time_rate)}`,
    barClass: 'bg-sky-500',
  },
])

const loadData = async () => {
  try {
    loading.value = true
    const params = {
      start_date: dateRange.value.start,
      end_date: dateRange.value.end,
      medicine_id: selectedMedicine.value || undefined,
    }
    console.log('[RecordStatsPage] loadData:start', params)
    const [adherenceResponse] = await Promise.all([
      recordApi.getAdherence(params),
      loadMedicineInventory(),
    ])

    if (adherenceResponse?.success && adherenceResponse.data) {
      adherence.value = adherenceResponse.data
    } else {
      adherence.value = {
        period: {
          start_date: dateRange.value.start,
          end_date: dateRange.value.end,
          days: 0,
          medicine_id: selectedMedicine.value ? Number(selectedMedicine.value) : null,
        },
        summary_7d: createEmptyPeriodSummary(),
        summary_30d: createEmptyPeriodSummary(),
        current_period: createEmptyPeriodSummary(),
        trend: [],
      }
    }
    console.log('[RecordStatsPage] loadData:success', adherence.value)
  } catch (error) {
    if (isRequestCancelledError(error)) {
      console.log('加载依从性统计请求已取消')
      return
    }

    console.error('加载依从性统计失败:', error)
  } finally {
    loading.value = false
  }
}

const loadMedicineInventory = async () => {
  try {
    await fetchMedicines()
    medicineInventory.value = medicines.value.map(medicine => ({
      ...medicine,
      quantity: medicine.quantity ?? 0,
    }))
  } catch (error) {
    if (isRequestCancelledError(error)) {
      console.log('加载药品库存数据请求已取消')
      return
    }
    console.error('加载药品库存数据失败:', error)
    medicineInventory.value = []
  }
}

const lowStockCount = computed(
  () => medicineInventory.value.filter(medicine => medicine.quantity <= 5).length
)
const mediumStockCount = computed(
  () =>
    medicineInventory.value.filter(
      medicine => medicine.quantity > 5 && medicine.quantity <= 10
    ).length
)
const goodStockCount = computed(
  () => medicineInventory.value.filter(medicine => medicine.quantity > 10).length
)

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const rateText = (value: number) => `${Math.round(value)}%`

const riskText = (level: MedicationAdherencePeriodSummary['risk_level']) => {
  const mapping = {
    low: '低',
    medium: '中',
    high: '高',
  }
  return mapping[level]
}

const riskBadgeClass = (level: MedicationAdherencePeriodSummary['risk_level']) => {
  if (level === 'high') return 'bg-rose-100 text-rose-700'
  if (level === 'medium') return 'bg-amber-100 text-amber-700'
  return 'bg-emerald-100 text-emerald-700'
}

const inventoryLevelText = (quantity: number) => {
  if (quantity <= 5) return '急需补充'
  if (quantity <= 10) return '库存偏低'
  return '库存充足'
}

const inventoryCardClass = (quantity: number) => {
  if (quantity <= 5) return 'border-rose-300 bg-rose-50'
  if (quantity <= 10) return 'border-amber-300 bg-amber-50'
  return 'border-emerald-300 bg-emerald-50'
}

const inventoryBadgeClass = (quantity: number) => {
  if (quantity <= 5) return 'bg-rose-100 text-rose-700'
  if (quantity <= 10) return 'bg-amber-100 text-amber-700'
  return 'bg-emerald-100 text-emerald-700'
}

onMounted(async () => {
  initDateRange()
  if (medicines.value.length === 0) {
    await fetchMedicines()
  }
  await loadData()
})
</script>
