<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">用药计划</h1>
            <p class="text-gray-600 mt-1">制定和管理您的用药方案</p>
          </div>
          <button
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            @click="openCreate"
          >
            <svg
              class="-ml-1 mr-2 h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              ></path>
            </svg>
            创建计划
          </button>
        </div>
      </div>

      <!-- 冲突检测提醒（用药安全提醒，始终可见并突出显示） -->
      <div
        role="alert"
        class="sticky top-4 z-20 bg-orange-50/90 border-2 border-orange-400 rounded-lg p-4 mb-6 shadow ring-1 ring-orange-200 backdrop-blur-sm"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg
              class="h-6 w-6 text-orange-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01M4.93 19h14.14c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.198 16.5C2.428 17.333 3.39 19 4.93 19z"
              ></path>
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-base font-semibold text-orange-800">
              用药安全提醒
            </h3>
            <div class="mt-2 text-sm text-orange-700">
              <p>
                在制定用药计划时，请注意药物之间的相互作用。如有疑问，请及时咨询您的医生或药师。
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 计划分类标签 -->
      <div class="mb-6">
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-8">
            <button :class="tabClass('all')" @click="setTab('all')">
              全部计划
            </button>
            <button :class="tabClass('long')" @click="setTab('long')">
              长期用药
            </button>
            <button :class="tabClass('short')" @click="setTab('short')">
              短期用药
            </button>
            <button :class="tabClass('completed')" @click="setTab('completed')">
              已完成
            </button>
          </nav>
        </div>
      </div>

      <!-- 用药计划列表 -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">我的用药计划</h3>
        </div>
        <div class="border-t border-gray-200">
          <!-- 加载/错误状态 -->
          <div v-if="loading" class="p-6 text-gray-500">
            正在加载计划数据...
          </div>
          <div v-else-if="error" class="p-6 text-red-600">{{ error }}</div>

          <!-- 列表渲染 -->
          <ul v-else role="list" class="divide-y divide-gray-200">
            <li v-for="plan in plans" :key="plan.id" class="p-6">
              <div class="flex items-start justify-between">
                <div>
                  <h4 class="text-lg font-semibold text-gray-900">
                    {{ plan.name || '未命名计划' }}
                  </h4>
                  <p class="mt-1 text-sm text-gray-500">
                    类型：{{ planTypeLabel(plan.plan_type) }}
                    <span class="ml-4">优先级：{{ plan.priority }}</span>
                    <span class="ml-4"
                      >起止：{{ plan.start_date }} ~
                      {{ plan.end_date || '未设置' }}</span
                    >
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <span
                    class="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium"
                    :class="statusBadgeClass(displayStatus(plan))"
                  >
                    {{ statusLabel(displayStatus(plan)) }}
                  </span>
                  <button
                    v-if="displayStatus(plan) === 'completed'"
                    type="button"
                    class="inline-flex items-center px-3 py-1 rounded-md text-sm font-medium border border-red-200 text-red-600 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    :disabled="deletingPlanId === plan.id"
                    @click="confirmDeletePlan(plan)"
                  >
                    {{ deletingPlanId === plan.id ? '删除中…' : '删除' }}
                  </button>
                </div>
              </div>

              <!-- 药品列表 -->
              <div
                v-if="plan.medicines && plan.medicines.length"
                class="mt-4 space-y-2"
              >
                <div
                  v-for="m in plan.medicines"
                  :key="m.id"
                  class="flex items-center justify-between"
                >
                  <div class="text-sm text-gray-700">
                    {{ m.medicine_name || m.medicine }}
                    <span class="ml-2 text-gray-500"
                      >{{ m.single_dose || m.daily_dosage }}
                      {{ m.frequency }}</span
                    >
                  </div>
                  <div class="text-xs text-gray-400">
                    开始：{{ plan.start_date }}，持续：{{
                      plan.duration_days || '-'
                    }}
                    天
                  </div>
                </div>
              </div>

              <!-- 进度条 -->
              <div class="mt-4">
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full"
                    :style="{
                      width: progressText(
                        plan.status,
                        plan.progress_percentage
                      ),
                    }"
                  ></div>
                </div>
                <div class="mt-1 text-xs text-gray-500">
                  完成度：{{
                    progressText(plan.status, plan.progress_percentage)
                  }}
                </div>
              </div>
            </li>

            <!-- 空状态 -->
            <li v-if="!plans.length" class="p-6 text-gray-500">暂无数据</li>
          </ul>

          <!-- 分页 -->
          <div
            v-if="pagination"
            class="px-6 py-4 flex items-center justify-between border-t border-gray-200"
          >
            <button
              type="button"
              class="px-3 py-1.5 text-sm rounded border"
              :class="{ 'opacity-50 cursor-not-allowed': !pagination.previous }"
              :disabled="!pagination.previous"
              @click="goPrev"
            >
              上一页
            </button>
            <div class="text-sm text-gray-600">
              第 {{ pagination.current_page || 1 }} /
              {{ pagination.total_pages || 1 }} 页，共
              {{ pagination.count || 0 }} 条
            </div>
            <button
              type="button"
              class="px-3 py-1.5 text-sm rounded border"
              :class="{ 'opacity-50 cursor-not-allowed': !pagination.next }"
              :disabled="!pagination.next"
              @click="goNext"
            >
              下一页
            </button>
          </div>
        </div>
      </div>

      <!-- 创建计划表单（弹窗） -->
      <PlanForm
        v-if="showCreateDialog"
        :visible="showCreateDialog"
        @close="closeCreate"
        @success="
          () => {
            console.log('[PlansPage] 创建成功 -> 刷新列表并关闭对话框')
            fetchPlans()
            closeCreate()
          }
        "
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import plansApi from '@/api/plans'
import { isRequestCancelledError } from '@/utils/api'
import type {
  MedicationPlan,
  Pagination,
  PlanStatus,
  PlanType,
  PlanListParams,
} from '@/types/plan'
import PlanForm from '@/components/PlanForm.vue'

// 标签筛选状态
const activeTab = ref<'all' | 'long' | 'short' | 'completed'>('all')

// 列表与状态
const plans = ref<MedicationPlan[]>([])
const pagination = ref<Pagination | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const page = ref(1)
const pageSize = ref(10)

// 创建弹窗状态
const showCreateDialog = ref(false)

const deletingPlanId = ref<number | null>(null)

function openCreate() {
  console.log('[PlansPage] 点击创建计划按钮 -> 打开创建对话框')
  showCreateDialog.value = true
}

function closeCreate() {
  console.log('[PlansPage] 关闭创建对话框')
  showCreateDialog.value = false
}

// 切换标签
function setTab(tab: 'all' | 'long' | 'short' | 'completed') {
  console.log('[PlansPage] 切换标签:', tab)
  activeTab.value = tab
}

// 计算标签样式
function tabClass(tab: 'all' | 'long' | 'short' | 'completed') {
  const isActive = activeTab.value === tab
  return [
    'whitespace-nowrap py-4 px-1 border-b-2 text-sm font-medium',
    isActive
      ? 'border-blue-500 text-blue-600'
      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
  ]
}

// 标签到查询参数映射
function buildParams(): PlanListParams {
  const params: PlanListParams = { page: page.value, page_size: pageSize.value }
  if (activeTab.value === 'long') params.plan_type = 'long_term'
  if (activeTab.value === 'short') params.plan_type = 'short_term'
  if (activeTab.value === 'completed') params.status = 'completed'
  console.log('[PlansPage] 查询参数:', params)
  return params
}

// 拉取列表
async function fetchPlans() {
  loading.value = true
  error.value = null
  try {
    const data = await plansApi.getPlans(buildParams())
    plans.value = data.results || []
    pagination.value = data.pagination
    console.log(
      '[PlansPage] 拉取成功, count=',
      pagination.value?.count,
      'page=',
      pagination.value?.current_page
    )
  } catch (e: any) {
    if (isRequestCancelledError(e)) {
      console.log('[PlansPage] 拉取计划列表请求已取消')
      error.value = null
      return
    }

    console.error('[PlansPage] 拉取失败:', e)
    error.value = e?.message || '获取计划列表失败'
  } finally {
    loading.value = false
  }
}

async function confirmDeletePlan(plan: MedicationPlan) {
  if (!plan?.id) return
  if (displayStatus(plan) !== 'completed') return
  if (deletingPlanId.value) return

  const ok = window.confirm(
    '确定要删除这个已完成的用药计划吗？删除后不可恢复。'
  )
  if (!ok) return

  deletingPlanId.value = plan.id
  console.log('[PlansPage] 删除计划:', { id: plan.id, name: plan.name })
  try {
    await plansApi.deletePlan(plan.id)
    plans.value = plans.value.filter(p => p.id !== plan.id)
    console.log('[PlansPage] 删除成功 -> 刷新列表')
    await fetchPlans()
  } catch (e: any) {
    console.error('[PlansPage] 删除失败:', e)
    error.value = e?.message || '删除计划失败'
  } finally {
    deletingPlanId.value = null
  }
}

function goPrev() {
  if (pagination.value?.previous) {
    page.value = Math.max(1, (pagination.value.current_page || 1) - 1)
    console.log('[PlansPage] 上一页 ->', page.value)
    fetchPlans()
  }
}

function goNext() {
  if (pagination.value?.next) {
    page.value = (pagination.value.current_page || 1) + 1
    console.log('[PlansPage] 下一页 ->', page.value)
    fetchPlans()
  }
}

// 辅助：显示标签/状态与进度
function planTypeLabel(t: PlanType): string {
  switch (t) {
    case 'long_term':
      return '长期用药'
    case 'short_term':
      return '短期用药'
    case 'acute':
      return '急性期'
    case 'chronic':
      return '慢性病管理'
    case 'preventive':
      return '预防性'
    case 'rehabilitation':
      return '康复'
    default:
      return String(t)
  }
}

function statusLabel(s: PlanStatus): string {
  switch (s) {
    case 'draft':
      return '草稿'
    case 'active':
      return '进行中'
    case 'paused':
      return '已暂停'
    case 'completed':
      return '已完成'
    case 'cancelled':
      return '已取消'
    default:
      return String(s)
  }
}

function statusBadgeClass(s: PlanStatus): string {
  switch (s) {
    case 'active':
      return 'bg-blue-100 text-blue-800'
    case 'completed':
      return 'bg-green-100 text-green-800'
    case 'paused':
      return 'bg-yellow-100 text-yellow-800'
    case 'draft':
      return 'bg-gray-100 text-gray-800'
    case 'cancelled':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

function displayStatus(plan: MedicationPlan): PlanStatus {
  const status = plan.status
  if (status !== 'active') return status
  const percent = progressPercent(status, plan.progress_percentage)
  if (percent >= 100) return 'completed'
  return status
}

function progressPercent(status: PlanStatus, percent?: number | null): number {
  if (status === 'completed') return 100
  if (typeof percent === 'number' && percent >= 0)
    return Math.min(100, Math.max(0, Math.round(percent)))
  return 0
}

function progressText(status: PlanStatus, percent?: number | null): string {
  return `${progressPercent(status, percent)}%`
}

// 首次与标签切换
onMounted(fetchPlans)
watch(activeTab, () => {
  page.value = 1
  fetchPlans()
})
</script>
