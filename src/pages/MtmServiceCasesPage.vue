<template>
  <div class="min-h-screen bg-slate-50">
    <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <section class="mb-6 rounded-3xl border border-violet-100 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <span class="inline-flex items-center rounded-full bg-violet-100 px-3 py-1 text-xs font-medium text-violet-700">
                MTM 专业服务
              </span>
              <span class="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                历史服务承接
              </span>
            </div>
            <h1 class="mt-3 text-2xl font-bold text-slate-900">我的专业服务</h1>
            <p class="mt-2 max-w-2xl text-sm text-slate-600">
              在这里集中查看全部专业服务进度、历史记录和当前可继续跟进的服务单。
            </p>
          </div>

          <div
            v-if="recommendedAction"
            class="flex flex-col items-start rounded-2xl border border-violet-100 bg-violet-50/70 p-4 lg:max-w-sm lg:items-end"
          >
            <p class="text-sm font-medium text-violet-800">当前推荐操作</p>
            <p class="mt-1 text-sm text-violet-700">
              {{ recommendedAction.description }}
            </p>
            <button
              v-if="recommendedAction.action"
              type="button"
              class="mt-3 inline-flex items-center rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-700"
              :disabled="loading"
              @click="handleQuickAction(recommendedAction.action)"
            >
              {{ recommendedAction.label }}
            </button>
            <router-link
              v-else-if="recommendedAction.to"
              :to="recommendedAction.to"
              class="mt-3 inline-flex items-center rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-700"
            >
              {{ recommendedAction.label }}
            </router-link>
          </div>
        </div>

      </section>

      <section class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        <article class="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
          <p class="text-sm text-slate-500">服务总数</p>
          <p class="mt-3 text-3xl font-bold text-slate-900">
            {{ summaryLoading ? '--' : summary.total }}
          </p>
          <p class="mt-2 text-sm text-slate-500">当前用户参与过的全部专业服务单</p>
        </article>

        <article class="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
          <p class="text-sm text-slate-500">进行中</p>
          <p class="mt-3 text-3xl font-bold text-violet-700">
            {{ summaryLoading ? '--' : summary.active }}
          </p>
          <p class="mt-2 text-sm text-slate-500">还可以继续跟进或推进状态的服务单</p>
        </article>

        <article class="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
          <p class="text-sm text-slate-500">已完成</p>
          <p class="mt-3 text-3xl font-bold text-emerald-700">
            {{ summaryLoading ? '--' : summary.completed }}
          </p>
          <p class="mt-2 text-sm text-slate-500">已经结束并可回看的服务记录</p>
        </article>
      </section>

      <section class="mb-6 rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-4">
          <div class="lg:col-span-2">
            <label class="mb-2 block text-sm font-medium text-slate-700">搜索服务</label>
            <input
              v-model.trim="searchInput"
              type="text"
              placeholder="搜索服务编号、目标或备注..."
              class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-violet-300 focus:ring-2 focus:ring-violet-100"
              @keyup.enter="applyFilters"
            />
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">状态筛选</label>
            <select
              v-model="filters.status"
              class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-violet-300 focus:ring-2 focus:ring-violet-100"
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

          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">触发来源</label>
            <select
              v-model="filters.triggerSource"
              class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-violet-300 focus:ring-2 focus:ring-violet-100"
              @change="applyFilters"
            >
              <option value="">全部来源</option>
              <option
                v-for="option in triggerSourceOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">排序方式</label>
            <select
              v-model="filters.ordering"
              class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-violet-300 focus:ring-2 focus:ring-violet-100"
              @change="applyOrdering"
            >
              <option
                v-for="option in orderingOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>

        <div class="mt-4 flex flex-wrap justify-end gap-3">
          <button
            type="button"
            class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            @click="resetFilters"
          >
            重置筛选
          </button>
          <button
            type="button"
            class="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-700"
            :disabled="loading"
            @click="applyFilters"
          >
            {{ loading ? '正在查询...' : '确认搜索' }}
          </button>
        </div>
      </section>

      <section class="rounded-3xl border border-slate-100 bg-white shadow-sm">
        <div class="border-b border-slate-100 px-6 py-4">
          <div class="rounded-2xl border border-slate-100 bg-slate-50/80 p-4">
            <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div class="max-w-3xl space-y-4">
                <div class="space-y-3">
                  <div class="flex flex-wrap items-center gap-2">
                    <span
                      v-for="badge in summaryHeaderBadges"
                      :key="badge.label"
                      class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium"
                      :class="badge.className"
                    >
                      {{ badge.label }}
                    </span>
                  </div>
                  <div class="space-y-1">
                    <h2 class="text-lg font-semibold text-slate-900">
                      {{ resultViewMeta.heading }}
                    </h2>
                    <p class="text-sm text-slate-600">
                      {{ resultViewMeta.summary }}
                    </p>
                  </div>
                </div>
                <div v-if="summaryInfoBlocks.length" class="grid gap-2">
                  <div
                    v-for="block in summaryInfoBlocks"
                    :key="block.key"
                    class="rounded-xl border px-3 py-2"
                    :class="block.className"
                  >
                    <p class="text-xs font-medium uppercase tracking-wide">
                      {{ block.label }}
                    </p>
                    <p class="mt-1 text-sm">
                      {{ block.description }}
                    </p>
                  </div>
                </div>
                <div
                  v-if="summaryActions.length"
                  class="space-y-3 pt-1"
                >
                  <div class="space-y-1">
                    <p class="text-xs font-medium uppercase tracking-wide text-slate-500">
                      {{ summaryActionsSectionCopy.title }}
                    </p>
                    <p class="mt-1 text-sm text-slate-500">
                      {{ summaryActionsSectionCopy.description }}
                    </p>
                  </div>
                  <div class="grid gap-3">
                    <div
                      v-for="group in summaryActionGroups"
                      :key="group.key"
                      class="rounded-2xl border border-slate-200 bg-white/80 p-3"
                    >
                      <p class="text-xs font-medium uppercase tracking-wide text-slate-500">
                        {{ group.title }}
                      </p>
                      <p class="mt-1 text-sm text-slate-500">
                        {{ group.description }}
                      </p>
                      <div class="mt-3 flex flex-wrap gap-3">
                        <template v-for="item in group.items" :key="item.key">
                          <button
                            v-if="item.action"
                            type="button"
                            class="rounded-xl px-4 py-2 text-sm font-medium transition"
                            :class="
                              item.variant === 'secondary'
                                ? 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                                : 'bg-violet-600 text-white hover:bg-violet-700'
                            "
                            :disabled="loading"
                            @click="handleQuickAction(item.action)"
                          >
                            {{ item.label }}
                          </button>
                          <router-link
                            v-else-if="item.to"
                            :to="item.to"
                            class="rounded-xl px-4 py-2 text-sm font-medium transition"
                            :class="
                              item.variant === 'secondary'
                                ? 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                                : 'bg-violet-600 text-white hover:bg-violet-700'
                            "
                          >
                            {{ item.label }}
                          </router-link>
                        </template>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div class="max-w-2xl space-y-1">
              <p class="text-sm font-medium text-slate-900">{{ resultSectionCopy.title }}</p>
              <p class="text-sm text-slate-500">
                {{ resultSectionCopy.description }}
              </p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-500 lg:max-w-xs lg:text-right">
              <p class="font-medium text-slate-700">{{ resultPageStatus.title }}</p>
              <p class="mt-1">{{ resultPageStatus.description }}</p>
            </div>
          </div>
        </div>

        <div v-if="loading" class="px-8 py-7 text-center">
          <div class="mx-auto max-w-2xl">
            <div class="inline-block h-8 w-8 animate-spin rounded-full border-b-2 border-violet-600"></div>
            <p class="mt-3 text-sm text-slate-500">正在加载专业服务列表...</p>
          </div>
        </div>

        <div v-else-if="loadError" class="px-8 py-7 text-center">
          <div class="mx-auto max-w-2xl">
            <div class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-red-50">
              <AlertTriangle class="h-5 w-5 text-red-500" />
            </div>
            <div class="mt-3 space-y-1">
              <h3 class="text-lg font-semibold text-slate-900">列表暂时没加载成功</h3>
              <p class="text-sm text-slate-600">{{ loadError }}</p>
            </div>
            <button
              type="button"
              class="mt-4 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-700"
              @click="refreshPage"
            >
              重新加载
            </button>
          </div>
        </div>

        <div v-else-if="!serviceCases.length" class="px-8 py-7 text-center">
          <div class="mx-auto max-w-2xl">
            <div class="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-slate-100">
              <ClipboardList class="h-6 w-6 text-slate-500" />
            </div>
            <div class="mt-3 space-y-3">
              <div>
                <h3 class="text-lg font-semibold text-slate-900">
                  {{ emptyStateHeaderCopy.title }}
                </h3>
                <p class="mt-1.5 text-sm text-slate-600">
                  {{ emptyStateHeaderCopy.description }}
                </p>
              </div>
              <div
                v-if="emptyStateRecommendationBlock"
                class="rounded-xl border border-violet-100 bg-violet-50/70 px-3 py-2 text-left"
              >
                <p class="text-xs font-medium uppercase tracking-wide text-violet-600">
                  {{ emptyStateRecommendationBlock.title }}
                </p>
                <p class="mt-1 text-sm text-violet-700">
                  {{ emptyStateRecommendationBlock.description }}
                </p>
              </div>
            </div>
          </div>
          <div class="mx-auto mt-4 max-w-2xl">
            <div class="space-y-1 text-left">
              <p class="text-xs font-medium uppercase tracking-wide text-slate-500">
                {{ emptyStateActionsSectionCopy.title }}
              </p>
              <p class="mt-1 text-sm text-slate-500">
                {{ emptyStateActionsSectionCopy.description }}
              </p>
            </div>
            <div class="mt-3 grid gap-3">
              <div
                v-for="group in emptyStateActionGroups"
                :key="group.key"
                class="rounded-2xl border border-slate-200 bg-white/80 p-3 text-left"
              >
                <p class="text-xs font-medium uppercase tracking-wide text-slate-500">
                  {{ group.title }}
                </p>
                <p class="mt-1 text-sm text-slate-500">
                  {{ group.description }}
                </p>
                <div class="mt-3 flex flex-wrap gap-3">
                  <template v-for="item in group.items" :key="`empty-${item.key}`">
                    <button
                      v-if="item.action"
                      type="button"
                      class="rounded-xl px-4 py-2 text-sm font-medium transition"
                      :class="
                        item.variant === 'secondary'
                          ? 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                          : 'bg-violet-600 text-white hover:bg-violet-700'
                      "
                      :disabled="loading"
                      @click="handleQuickAction(item.action)"
                    >
                      {{ item.label }}
                    </button>
                    <router-link
                      v-else-if="item.to"
                      :to="item.to"
                      class="rounded-xl px-4 py-2 text-sm font-medium transition"
                      :class="
                        item.variant === 'secondary'
                          ? 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                          : 'bg-violet-600 text-white hover:bg-violet-700'
                      "
                    >
                      {{ item.label }}
                    </router-link>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="divide-y divide-slate-100">
          <article
            v-for="item in serviceCases"
            :key="item.id"
            class="px-6 py-5 transition hover:bg-slate-50/80"
          >
            <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <h3 class="text-base font-semibold text-slate-900">
                    {{ item.case_number }}
                  </h3>
                  <span
                    class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium"
                    :class="getMtmStatusBadgeClass(item.status)"
                  >
                    {{ getMtmStatusText(item.status) }}
                  </span>
                  <span class="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                    {{ getMtmTriggerText(item.trigger_source) }}
                  </span>
                </div>

                <p class="mt-3 text-sm text-slate-700">
                  {{ item.service_goal || `${getMtmTriggerText(item.trigger_source)}发起的专业服务` }}
                </p>

                <div class="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-sm text-slate-500">
                  <span>创建于 {{ formatDateTime(item.created_at) }}</span>
                  <span>患者：{{ item.patient.username }}</span>
                  <span>药师：{{ item.assigned_pharmacist?.username || '暂未分配' }}</span>
                </div>

                <p class="mt-3 text-sm text-slate-600">
                  {{ getProgressText(item) }}
                </p>
              </div>

              <div class="flex flex-col items-start gap-3 xl:items-end">
                <router-link
                  :to="buildDetailRoute(item.id)"
                  class="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-700"
                >
                  查看详情
                  <ChevronRight class="h-4 w-4" />
                </router-link>
                <span
                  class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium"
                  :class="isMtmCaseActive(item.status) ? 'bg-violet-100 text-violet-700' : 'bg-emerald-100 text-emerald-700'"
                >
                  {{ isMtmCaseActive(item.status) ? '仍可继续跟进' : '已归档可回看' }}
                </span>
              </div>
            </div>
          </article>
        </div>

        <div
          v-if="pagination.total_pages > 1 && serviceCases.length"
          class="flex items-center justify-between border-t border-slate-100 px-6 py-4"
        >
          <button
            type="button"
            class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="pagination.current_page <= 1 || loading"
            @click="changePage(pagination.current_page - 1)"
          >
            上一页
          </button>

          <div class="text-sm text-slate-500">
            第 {{ pagination.current_page }} / {{ pagination.total_pages }} 页，共
            {{ pagination.count }} 条
          </div>

          <button
            type="button"
            class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="pagination.current_page >= pagination.total_pages || loading"
            @click="changePage(pagination.current_page + 1)"
          >
            下一页
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import {
  useRoute,
  useRouter,
  type LocationQuery,
  type LocationQueryRaw,
} from 'vue-router'
import {
  AlertTriangle,
  ChevronRight,
  ClipboardList,
} from 'lucide-vue-next'
import { mtmApi } from '@/api/mtm'
import { useToast } from '@/composables/useToast'
import type { Pagination } from '@/types/plan'
import type {
  MtmServiceCase,
  MtmServiceCaseListParams,
  MtmServiceCaseOrdering,
  MtmListPresetSource,
  MtmServiceStatus,
  MtmTriggerSource,
} from '@/types/mtm'
import { isRequestCancelledError } from '@/utils/api'
import {
  buildMtmListQuickActions,
  buildMtmListFilterSummary,
  getMtmListEmptyStateCopy,
  getMtmListPresetSourceBadge,
  getMtmServiceCaseOrderingText,
  getMtmListPresetSourceDescription,
  getMtmListPresetSourceTitle,
  getMtmStatusBadgeClass,
  getMtmStatusText,
  getMtmTriggerText,
  isValidMtmListPresetSource,
  isValidMtmServiceCaseOrdering,
  isValidMtmTriggerSource,
  isMtmCaseActive,
  mtmServiceCaseOrderings,
  mtmTriggerSources,
} from '@/utils/mtm'

const isDebug = import.meta.env.MODE !== 'production'
const log = (...args: unknown[]) => {
  if (isDebug) console.log(...args)
}

const route = useRoute()
const router = useRouter()
const { error: showError } = useToast()
const defaultOrdering: MtmServiceCaseOrdering = '-created_at'

const searchInput = ref('')
const filters = reactive<{
  status: MtmServiceStatus | ''
  triggerSource: MtmTriggerSource | ''
  ordering: MtmServiceCaseOrdering
}>({
  status: '',
  triggerSource: '',
  ordering: defaultOrdering,
})
const presetSource = ref<MtmListPresetSource | ''>('')
const loading = ref(false)
const summaryLoading = ref(false)
const loadError = ref('')
const page = ref(1)
const pageSize = ref(10)
const serviceCases = ref<MtmServiceCase[]>([])
const pagination = ref<Pagination>({
  count: 0,
  next: null,
  previous: null,
  page_size: 10,
  current_page: 1,
  total_pages: 0,
})
const summary = reactive({
  total: 0,
  active: 0,
  completed: 0,
})
const validStatuses: MtmServiceStatus[] = [
  'pending',
  'interviewing',
  'assessing',
  'intervening',
  'following_up',
  'completed',
]

const statusOptions = computed(() => {
  return validStatuses.map(status => ({
    value: status,
    label: getMtmStatusText(status),
  }))
})

const triggerSourceOptions = computed(() => {
  return mtmTriggerSources.map(triggerSource => ({
    value: triggerSource,
    label: getMtmTriggerText(triggerSource),
  }))
})

const orderingOptions = computed(() => {
  return mtmServiceCaseOrderings
    .filter(ordering =>
      ['-created_at', 'created_at', '-started_at', '-completed_at'].includes(ordering)
    )
    .map(ordering => ({
      value: ordering,
      label: getMtmServiceCaseOrderingText(ordering),
    }))
})

const hasSearchFilters = computed(() =>
  Boolean(searchInput.value || filters.status || filters.triggerSource)
)

const hasOrderingChanged = computed(() => filters.ordering !== defaultOrdering)

const hasManualAdjustments = computed(() =>
  Boolean(hasSearchFilters.value || hasOrderingChanged.value)
)

const activeFilterSummaryText = computed(() => {
  const summary = buildMtmListFilterSummary({
    search: searchInput.value,
    status: filters.status,
    triggerSource: filters.triggerSource,
    ordering: filters.ordering,
  })
  return summary.join('，')
})

const presetSourceTitle = computed(() => {
  if (!presetSource.value) {
    return ''
  }
  return getMtmListPresetSourceTitle(presetSource.value, {
    status: filters.status,
    triggerSource: filters.triggerSource,
  })
})

const presetSourceDescription = computed(() => {
  if (!presetSource.value) {
    return ''
  }
  return getMtmListPresetSourceDescription(presetSource.value, {
    status: filters.status,
    triggerSource: filters.triggerSource,
  })
})

const presetSourceBadge = computed(() =>
  getMtmListPresetSourceBadge(presetSource.value)
)

const quickActions = computed(() =>
  buildMtmListQuickActions({
    presetSource: presetSource.value,
    hasSearchFilters: hasSearchFilters.value,
    hasOrderingChanged: hasOrderingChanged.value,
  })
)

const recommendedAction = computed(() => quickActions.value[0] || null)
const summaryActions = computed(() => quickActions.value.slice(1))

const emptyStateCopy = computed(() =>
  getMtmListEmptyStateCopy({
    presetSource: presetSource.value,
    search: searchInput.value,
    status: filters.status,
    triggerSource: filters.triggerSource,
    ordering: filters.ordering,
  })
)

/**
 * 输出空态头部标题与原因说明，避免和推荐下一步块重复承接动作建议。
 */
const emptyStateHeaderCopy = computed(() => {
  if (presetSource.value === 'active_status') {
    return {
      title: emptyStateCopy.value.title,
      description: filters.status
        ? `当前还没有匹配到${getMtmStatusText(filters.status)}阶段的专业服务记录。`
        : '当前首页推荐阶段下还没有匹配到专业服务记录。',
    }
  }

  if (presetSource.value === 'suggested_trigger') {
    return {
      title: emptyStateCopy.value.title,
      description: filters.triggerSource
        ? `当前还没有匹配到与“${getMtmTriggerText(filters.triggerSource)}”相关的专业服务记录。`
        : '当前首页推荐来源下还没有匹配到专业服务记录。',
    }
  }

  if (searchInput.value.trim()) {
    return {
      title: emptyStateCopy.value.title,
      description: '当前搜索词和筛选条件下还没有匹配结果。',
    }
  }

  if (filters.status || filters.triggerSource) {
    return {
      title: emptyStateCopy.value.title,
      description: '当前筛选条件下还没有匹配到专业服务记录。',
    }
  }

  return {
    title: emptyStateCopy.value.title,
    description: '这里暂时还没有可展示的专业服务历史记录。',
  }
})

/**
 * 输出当前结果视图的统一语义，供顶部标签和底部说明共用。
 */
const resultViewMeta = computed(() => {
  if (presetSource.value) {
    return {
      heading: '首页预设服务',
      summary: '这里已经按首页入口为你切好当前最相关的一组专业服务。',
      title: '首页预设结果',
      description: '当前结果来自首页快捷入口，适合先顺着这批服务继续浏览，再按需要打开详情查看具体进度。',
      badgeLabel: '首页预设结果',
      badgeClassName: 'bg-violet-100 text-violet-700',
    }
  }

  if (hasSearchFilters.value && hasOrderingChanged.value) {
    return {
      heading: '筛选服务',
      summary: '这里展示的是你按搜索、筛选和排序收窄后的专业服务结果。',
      title: '筛选结果',
      description: '当前结果已经按你的搜索、筛选和排序收窄，适合先确认目标服务，再进入详情继续跟进。',
      badgeLabel: '筛选结果',
      badgeClassName: 'bg-amber-100 text-amber-700',
    }
  }

  if (hasSearchFilters.value) {
    return {
      heading: '筛选服务',
      summary: '这里展示的是你按当前条件筛出来的专业服务结果。',
      title: '筛选结果',
      description: '当前结果已经按你的条件收窄，适合先逐条确认目标服务，再打开详情查看具体服务进度。',
      badgeLabel: '筛选结果',
      badgeClassName: 'bg-amber-100 text-amber-700',
    }
  }

  if (hasOrderingChanged.value) {
    return {
      heading: '排序浏览',
      summary: '这里仍是完整专业服务列表，只是已经按你选择的顺序重新排好。',
      title: '排序结果',
      description: '当前结果仍是完整服务列表，只是换了查看顺序，适合先按现在的顺序浏览，再进入详情查看进度。',
      badgeLabel: '排序结果',
      badgeClassName: 'bg-sky-100 text-sky-700',
    }
  }

  return {
    heading: '全部服务',
    summary: '这里集中展示你当前参与过的全部专业服务记录。',
    title: '列表结果',
    description: '当前展示的是完整专业服务列表，适合先浏览整体情况，再打开详情查看具体服务进度。',
    badgeLabel: '完整列表',
    badgeClassName: 'bg-slate-100 text-slate-700',
  }
})

/**
 * 输出摘要卡顶部标签，统一承接结果类型、结果数量和可选来源信息。
 */
const summaryHeaderBadges = computed(() => {
  const badges = [
    {
      label: resultViewMeta.value.badgeLabel,
      className: resultViewMeta.value.badgeClassName,
    },
    {
      label: `当前结果 ${pagination.value.count} 条`,
      className: 'bg-white text-slate-700',
    },
  ]

  if (presetSource.value) {
    badges.push({
      label: `来源：${presetSourceBadge.value.label}`,
      className: 'bg-white text-slate-600',
    })
  }

  return badges
})

/**
 * 输出底部“列表结果”说明区的人话标题和描述，保持与当前主路径语义一致。
 */
const resultSectionCopy = computed(() => ({
  title: resultViewMeta.value.title,
  description: resultViewMeta.value.description,
}))

/**
 * 输出摘要卡上方当前最关键的一条上下文说明，避免来源说明和条件说明重复堆叠。
 */
const summaryContextCopy = computed(() => {
  if (presetSource.value) {
    return {
      label: presetSourceTitle.value,
      description: presetSourceDescription.value,
    }
  }

  if (hasManualAdjustments.value && activeFilterSummaryText.value) {
    return {
      label: '当前条件',
      description: activeFilterSummaryText.value,
    }
  }

  return null
})

/**
 * 输出摘要卡中的当前上下文块与推荐下一步块，明确两者职责边界。
 */
const summaryInfoBlocks = computed(() => {
  const blocks: Array<{
    key: 'context' | 'next-step'
    label: string
    description: string
    className: string
  }> = []

  if (summaryContextCopy.value) {
    blocks.push({
      key: 'context',
      label: summaryContextCopy.value.label,
      description: summaryContextCopy.value.description,
      className: 'border-slate-200 bg-white/80 text-slate-600',
    })
  }

  if (recommendedAction.value) {
    blocks.push({
      key: 'next-step',
      label: '推荐下一步',
      description: recommendedAction.value.description,
      className: 'border-violet-100 bg-violet-50/70 text-violet-700',
    })
  }

  return blocks
})

/**
 * 输出补充动作区的轻量标题和说明，强调其属于主路径之后的次级选择。
 */
const summaryActionsSectionCopy = computed(() => {
  if (recommendedAction.value) {
    return {
      title: '补充选择',
      description: '如果当前推荐路径不完全适合，你也可以直接从这些补充操作继续处理。',
    }
  }

  return {
    title: '可继续操作',
    description: '当前没有单独强调的主路径时，可以直接从这些操作里选择下一步。',
  }
})

/**
 * 输出补充动作区的按钮分组，继续复用现有 variant 语义，不改变动作集合和顺序。
 */
const summaryActionGroups = computed(() => {
  const groups: Array<{
    key: 'primary' | 'secondary'
    title: string
    description: string
    items: typeof summaryActions.value
  }> = []

  const primaryItems = summaryActions.value.filter(item => item.variant === 'primary')
  const secondaryItems = summaryActions.value.filter(item => item.variant !== 'primary')

  if (primaryItems.length) {
    groups.push({
      key: 'primary',
      title: '可直接切换',
      description: '这些补充操作会把你切到另一条可直接继续处理的路径。',
      items: primaryItems,
    })
  }

  if (secondaryItems.length) {
    groups.push({
      key: 'secondary',
      title: '辅助操作',
      description: '这些操作更适合用来刷新、回看或退回其他入口，不会替代当前主路径。',
      items: secondaryItems,
    })
  }

  return groups
})

/**
 * 输出空态中的推荐下一步块，保持“推荐说明在前”的主路径表达。
 */
const emptyStateRecommendationBlock = computed(() => {
  if (!recommendedAction.value) {
    return null
  }

  return {
    title: '推荐下一步',
    description: recommendedAction.value.description,
  }
})

/**
 * 输出空态动作区的轻量标题和说明，明确它位于推荐说明之后。
 */
const emptyStateActionsSectionCopy = computed(() => {
  if (emptyStateRecommendationBlock.value) {
    return {
      title: '还可以这样继续',
      description: '如果当前推荐路径不完全适合，也可以直接从下面这些操作开始。',
    }
  }

  return {
    title: '接下来可做的事',
    description: '当前没有单独强调的推荐路径时，可以直接从下面这些操作里选择下一步。',
  }
})

/**
 * 输出空态动作区的按钮分组，继续复用现有 variant 语义，不改变 quickActions 集合和顺序。
 */
const emptyStateActionGroups = computed(() => {
  const groups: Array<{
    key: 'primary' | 'secondary'
    title: string
    description: string
    items: typeof quickActions.value
  }> = []

  const primaryItems = quickActions.value.filter(item => item.variant === 'primary')
  const secondaryItems = quickActions.value.filter(item => item.variant !== 'primary')

  if (primaryItems.length) {
    groups.push({
      key: 'primary',
      title: '可直接开始',
      description: '这些操作更适合作为空态下的直接下一步，帮助你尽快回到可继续处理的路径。',
      items: primaryItems,
    })
  }

  if (secondaryItems.length) {
    groups.push({
      key: 'secondary',
      title: '辅助选择',
      description: '这些操作更适合用来回看、切换入口或做补充处理，不会替代当前推荐方向。',
      items: secondaryItems,
    })
  }

  return groups
})

/**
 * 输出结果区首屏唯一分页状态，避免摘要卡内重复展示相同页码。
 */
const resultPageStatus = computed(() => {
  const totalPages = Math.max(pagination.value.total_pages || 1, 1)
  const currentPage = Math.min(Math.max(pagination.value.current_page || 1, 1), totalPages)

  if (totalPages <= 1) {
    return {
      title: '当前结果已全部显示',
      description: `共 ${pagination.value.count} 条，当前这一页已经全部展示。`,
    }
  }

  return {
    title: `当前浏览第 ${currentPage} / ${totalPages} 页`,
    description: '可继续翻页查看其余结果，或直接打开详情跟进当前服务。',
  }
})

/**
 * 从路由查询参数中读取单个字符串值。
 */
const getQueryValue = (query: LocationQuery, key: string) => {
  const value = query[key]
  return Array.isArray(value) ? value[0] || '' : value || ''
}

/**
 * 判断查询参数中的状态值是否合法。
 */
const isValidStatus = (value: string): value is MtmServiceStatus => {
  return validStatuses.includes(value as MtmServiceStatus)
}

/**
 * 解析页码查询参数，非法时统一回退到第一页。
 */
const parsePageQuery = (value: string) => {
  const parsed = Number.parseInt(value, 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 1
}

/**
 * 从路由查询参数恢复列表页本地状态。
 */
const applyRouteQueryToState = (query: LocationQuery) => {
  const nextSearch = getQueryValue(query, 'search').trim()
  const nextStatus = getQueryValue(query, 'status')
  const nextTriggerSource = getQueryValue(query, 'trigger_source')
  const nextOrdering = getQueryValue(query, 'ordering')
  const nextPresetSource = getQueryValue(query, 'preset_source')
  const nextPage = parsePageQuery(getQueryValue(query, 'page'))

  searchInput.value = nextSearch
  filters.status = isValidStatus(nextStatus) ? nextStatus : ''
  filters.triggerSource = isValidMtmTriggerSource(nextTriggerSource)
    ? nextTriggerSource
    : ''
  filters.ordering = isValidMtmServiceCaseOrdering(nextOrdering)
    ? nextOrdering
    : defaultOrdering
  presetSource.value = isValidMtmListPresetSource(nextPresetSource)
    ? nextPresetSource
    : ''
  page.value = nextPage

  log('🔵 [MtmServiceCasesPage] 已按路由查询恢复列表状态', {
    page: page.value,
    search: searchInput.value,
    status: filters.status,
    triggerSource: filters.triggerSource,
    ordering: filters.ordering,
    presetSource: presetSource.value,
  })
}

/**
 * 生成当前列表页应写入 URL 的查询参数。
 */
const buildRouteQuery = (): LocationQueryRaw => {
  const query: LocationQueryRaw = {}

  if (page.value > 1) {
    query.page = String(page.value)
  }
  if (searchInput.value.trim()) {
    query.search = searchInput.value.trim()
  }
  if (filters.status) {
    query.status = filters.status
  }
  if (filters.triggerSource) {
    query.trigger_source = filters.triggerSource
  }
  if (filters.ordering !== defaultOrdering) {
    query.ordering = filters.ordering
  }
  if (presetSource.value) {
    query.preset_source = presetSource.value
  }

  return query
}

/**
 * 标准化路由中的最小列表查询参数，便于与目标 query 对比。
 */
const normalizeListQuery = (query: LocationQuery | LocationQueryRaw) => {
  const normalized: Record<string, string> = {}
  const pageValue = parsePageQuery(getQueryValue(query as LocationQuery, 'page'))
  const searchValue = getQueryValue(query as LocationQuery, 'search').trim()
  const statusValue = getQueryValue(query as LocationQuery, 'status')
  const triggerSourceValue = getQueryValue(query as LocationQuery, 'trigger_source')
  const orderingValue = getQueryValue(query as LocationQuery, 'ordering')
  const presetSourceValue = getQueryValue(query as LocationQuery, 'preset_source')

  if (pageValue > 1) {
    normalized.page = String(pageValue)
  }
  if (searchValue) {
    normalized.search = searchValue
  }
  if (isValidStatus(statusValue)) {
    normalized.status = statusValue
  }
  if (isValidMtmTriggerSource(triggerSourceValue)) {
    normalized.trigger_source = triggerSourceValue
  }
  if (isValidMtmServiceCaseOrdering(orderingValue) && orderingValue !== defaultOrdering) {
    normalized.ordering = orderingValue
  }
  if (isValidMtmListPresetSource(presetSourceValue)) {
    normalized.preset_source = presetSourceValue
  }

  return normalized
}

/**
 * 将本地列表状态同步到 URL；如 query 未变化，则返回 false。
 */
const syncRouteQuery = async () => {
  const targetQuery = buildRouteQuery()
  const currentQuery = normalizeListQuery(route.query)
  const nextQuery = normalizeListQuery(targetQuery)

  if (JSON.stringify(currentQuery) === JSON.stringify(nextQuery)) {
    log('🟡 [MtmServiceCasesPage] 当前路由查询无需更新', nextQuery)
    return false
  }

  log('🔵 [MtmServiceCasesPage] 开始同步列表查询到路由', nextQuery)
  await router.replace({
    path: '/mtm/service-cases',
    query: targetQuery,
  })
  return true
}

/**
 * 构造列表查询参数，保证筛选和分页统一从这里输出。
 */
const buildListParams = (): MtmServiceCaseListParams => {
  return {
    page: page.value,
    page_size: pageSize.value,
    search: searchInput.value || undefined,
    status: filters.status || undefined,
    trigger_source: filters.triggerSource || undefined,
    ordering: filters.ordering !== defaultOrdering ? filters.ordering : undefined,
  }
}

/**
 * 构造列表到详情页的最小返回上下文。
 */
const buildDetailRoute = (serviceCaseId: number) => {
  return {
    path: `/mtm/service-cases/${serviceCaseId}`,
    query: {
      ...buildRouteQuery(),
      from: 'mtm-list',
    },
  }
}

/**
 * 清除首页预设来源标识，避免用户手动改筛选后仍显示旧提示。
 */
const clearPresetSource = () => {
  if (!presetSource.value) {
    return
  }
  log('🟡 [MtmServiceCasesPage] 用户手动修改列表条件，清除预设来源标识', presetSource.value)
  presetSource.value = ''
}

/**
 * 加载 MTM 服务单列表，并更新分页信息。
 */
const fetchServiceCases = async () => {
  try {
    loading.value = true
    loadError.value = ''
    const params = buildListParams()
    log('🔵 [MtmServiceCasesPage] 开始加载服务列表', params)
    const payload = await mtmApi.getServiceCases(params)
    serviceCases.value = payload.results
    pagination.value = payload.pagination
    log('🟢 [MtmServiceCasesPage] 服务列表加载成功', {
      count: payload.pagination.count,
      currentPage: payload.pagination.current_page,
      resultLength: payload.results.length,
    })
  } catch (error) {
    if (isRequestCancelledError(error)) {
      log('🟡 [MtmServiceCasesPage] 服务列表请求已取消')
      return
    }

    console.error('🔴 [MtmServiceCasesPage] 服务列表加载失败', error)
    loadError.value = error instanceof Error ? error.message : '获取专业服务列表失败'
    showError(loadError.value)
  } finally {
    loading.value = false
  }
}

/**
 * 加载列表顶部摘要统计，作为列表页概览。
 */
const fetchSummary = async () => {
  try {
    summaryLoading.value = true
    log('🔵 [MtmServiceCasesPage] 开始加载服务摘要统计')
    const [allPayload, completedPayload] = await Promise.all([
      mtmApi.getServiceCases({ page: 1, page_size: 1 }),
      mtmApi.getServiceCases({ page: 1, page_size: 1, status: 'completed' }),
    ])
    summary.total = allPayload.pagination.count
    summary.completed = completedPayload.pagination.count
    summary.active = Math.max(summary.total - summary.completed, 0)
    log('🟢 [MtmServiceCasesPage] 服务摘要统计加载成功', { ...summary })
  } catch (error) {
    if (isRequestCancelledError(error)) {
      log('🟡 [MtmServiceCasesPage] 服务摘要统计请求已取消')
      return
    }
    console.error('🔴 [MtmServiceCasesPage] 服务摘要统计加载失败', error)
  } finally {
    summaryLoading.value = false
  }
}

/**
 * 应用当前筛选条件，并回到第一页重新拉取列表。
 */
const applyFilters = async () => {
  clearPresetSource()
  page.value = 1
  const changed = await syncRouteQuery()
  if (!changed) {
    await fetchServiceCases()
  }
}

/**
 * 应用当前排序方式，并回到第一页重新拉取列表。
 */
const applyOrdering = async () => {
  clearPresetSource()
  page.value = 1
  const changed = await syncRouteQuery()
  if (!changed) {
    await fetchServiceCases()
  }
}

/**
 * 重置搜索和状态筛选，并恢复第一页。
 */
const resetFilters = async () => {
  clearPresetSource()
  searchInput.value = ''
  filters.status = ''
  filters.triggerSource = ''
  filters.ordering = defaultOrdering
  page.value = 1
  const changed = await syncRouteQuery()
  if (!changed) {
    await fetchServiceCases()
  }
}

/**
 * 切换列表页码，并保持当前筛选条件。
 */
const changePage = async (nextPage: number) => {
  if (nextPage < 1 || nextPage > Math.max(pagination.value.total_pages, 1) || loading.value) {
    return
  }
  page.value = nextPage
  const changed = await syncRouteQuery()
  if (!changed) {
    await fetchServiceCases()
  }
}

/**
 * 同时刷新列表和顶部摘要。
 */
const refreshPage = async () => {
  await Promise.all([fetchServiceCases(), fetchSummary()])
}

/**
 * 执行列表页统一快捷动作。
 */
const handleQuickAction = async (action: 'refresh' | 'clear_filters') => {
  if (action === 'refresh') {
    await refreshPage()
    return
  }

  await resetFilters()
}

/**
 * 输出服务单当前进度的人话说明。
 */
const getProgressText = (serviceCase: MtmServiceCase) => {
  if (serviceCase.completed_at) {
    return `本次服务已于 ${formatDateTime(serviceCase.completed_at)} 完成，可继续回看详情。`
  }
  return `当前处于 ${getMtmStatusText(serviceCase.status)} 阶段，可进入详情继续查看或推进。`
}

/**
 * 格式化时间，空值时返回统一文案。
 */
const formatDateTime = (value?: string | null) => {
  if (!value) {
    return '未记录'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return '未记录'
  }

  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  applyRouteQueryToState(route.query)
  fetchSummary()
})

watch(
  () => route.query,
  async query => {
    applyRouteQueryToState(query)
    await fetchServiceCases()
  },
  { immediate: true }
)
</script>
