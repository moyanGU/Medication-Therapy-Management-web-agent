<template>
  <div class="min-h-screen bg-slate-50">
    <main class="mx-auto max-w-5xl px-4 py-6 sm:px-6 lg:px-8">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
          @click="goBack"
        >
          <ArrowLeft class="h-4 w-4" />
          返回详情
        </button>

        <div class="flex flex-wrap items-center gap-3">
          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 transition hover:border-emerald-300 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="loading || saving || completing"
            @click="handleSaveDraft"
          >
            <RefreshCw v-if="saving" class="h-4 w-4 animate-spin" />
            <Save v-else class="h-4 w-4" />
            {{ saving ? '保存中...' : '手动保存草稿' }}
          </button>
          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-full bg-sky-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-sky-300"
            :disabled="loading || saving || completing"
            @click="handleCompletePlan"
          >
            <RefreshCw v-if="completing" class="h-4 w-4 animate-spin" />
            <CheckCircle2 v-else class="h-4 w-4" />
            {{ completing ? '提交中...' : '完成计划' }}
          </button>
        </div>
      </div>

      <section class="mt-6 rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
        <div class="flex items-start gap-3">
          <ClipboardList class="mt-1 h-5 w-5 text-indigo-600" />
          <div>
            <h1 class="text-2xl font-semibold text-slate-900">干预计划起草</h1>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              基于评估结果，为患者制定具体的干预措施和行动指南。你可以先手动保存草稿，确认无误后再标记完成。
            </p>
          </div>
        </div>

        <div v-if="serviceCase" class="mt-5 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div class="rounded-2xl bg-slate-50 p-4">
            <p class="text-sm text-slate-500">服务单编号</p>
            <p class="mt-2 text-base font-medium text-slate-900">{{ serviceCase.case_number }}</p>
          </div>
          <div class="rounded-2xl bg-slate-50 p-4">
            <p class="text-sm text-slate-500">当前阶段</p>
            <p class="mt-2 text-base font-medium text-slate-900">{{ statusText }}</p>
          </div>
          <div class="rounded-2xl bg-slate-50 p-4">
            <p class="text-sm text-slate-500">患者</p>
            <p class="mt-2 text-base font-medium text-slate-900">
              {{ serviceCase.patient.username }}
            </p>
          </div>
        </div>

        <p
          v-if="serviceCase?.assessment?.completed_at"
          class="mt-5 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm leading-6 text-emerald-700"
        >
          评估已完成，你现在可以继续起草并完善干预计划。
        </p>

        <p
          v-else
          class="mt-5 rounded-2xl border border-amber-100 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-800"
        >
          当前还没有看到已完成的评估记录。你仍可先保存计划草稿，但更建议先把评估内容补完整。
        </p>

        <p
          v-if="completionHint"
          class="mt-5 rounded-2xl border border-sky-100 bg-sky-50 px-4 py-3 text-sm leading-6 text-sky-800"
        >
          完成前还需要补充：{{ completionHint }}
        </p>
      </section>

      <div
        v-if="loadError"
        class="mt-6 rounded-3xl border border-rose-100 bg-rose-50 px-5 py-4 text-sm leading-6 text-rose-700"
      >
        {{ loadError }}
      </div>

      <div
        v-if="loading"
        class="mt-6 rounded-3xl border border-slate-100 bg-white px-5 py-10 text-center text-sm text-slate-500 shadow-sm"
      >
        正在加载干预计划内容...
      </div>

      <template v-else-if="serviceCase">
        <section class="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">
          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">计划优先级</h2>
            <p class="mt-2 text-sm leading-6 text-slate-500">
              根据干预措施的紧迫程度和患者风险情况进行定级。
            </p>

            <label class="mt-5 block">
              <span class="text-sm font-medium text-slate-700">优先级</span>
              <select
                v-model="form.priority"
                class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-indigo-400"
              >
                <option value="">请选择</option>
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
                <option value="urgent">紧急</option>
              </select>
            </label>
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm xl:row-span-2">
            <h2 class="text-lg font-semibold text-slate-900">干预措施</h2>
            <p class="mt-2 text-sm leading-6 text-slate-500">
              一行写一项具体的行动指南或干预动作，例如“停用当前药物”、“增加早晨测量血压频率”等。
            </p>
            <textarea
              v-model="form.interventionsText"
              rows="12"
              class="mt-4 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-indigo-400"
              placeholder="例如：&#10;建议停用重复的降压药物&#10;调整用药时间到餐后半小时&#10;建议患者两周后进行血常规复查"
            />
          </article>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft,
  CheckCircle2,
  ClipboardList,
  RefreshCw,
  Save,
} from 'lucide-vue-next'
import { mtmApi } from '@/api/mtm'
import { useToast } from '@/composables/useToast'
import type {
  MtmPlanDraftPayload,
  MtmPlanSummary,
  MtmServiceCase,
} from '@/types/mtm'
import { isRequestCancelledError } from '@/utils/api'
import { getMtmStatusText } from '@/utils/mtm'

const isDebug = import.meta.env.MODE !== 'production'
const log = (...args: unknown[]) => {
  if (isDebug) console.log(...args)
}

const route = useRoute()
const router = useRouter()
const { success: showSuccess, error: showError } = useToast()

const serviceCase = ref<MtmServiceCase | null>(null)
const plan = ref<MtmPlanSummary | null>(null)
const loading = ref(false)
const saving = ref(false)
const completing = ref(false)
const loadError = ref('')

const form = reactive({
  priority: '',
  interventionsText: '',
})

const serviceCaseId = computed(() => String(route.params.id || '').trim())
const statusText = computed(() =>
  serviceCase.value ? getMtmStatusText(serviceCase.value.status) : '未开始'
)
const completionHint = computed(() => buildCompletionIssues().join('、'))

/**
 * 从列表型结构中提取可直接编辑的逐行文本。
 */
function extractLineText(items: unknown): string {
  if (!Array.isArray(items)) {
    return ''
  }

  return items
    .map(item => {
      if (typeof item === 'string') {
        return item.trim()
      }
      if (item && typeof item === 'object') {
        const record = item as Record<string, unknown>
        for (const key of ['item', 'summary', 'title', 'name', 'label', 'type', 'action']) {
          const candidate = record[key]
          if (typeof candidate === 'string' && candidate.trim()) {
            return candidate.trim()
          }
        }
      }
      return ''
    })
    .filter(Boolean)
    .join('\n')
}

/**
 * 把多行文本转成去重后的有效行列表。
 */
function parseLines(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map(item => item.trim())
    .filter(Boolean)
}

/**
 * 把后端计划摘要同步到页面表单状态。
 */
function syncFormFromPlan(currentPlan: MtmPlanSummary) {
  form.priority = currentPlan.priority || ''
  form.interventionsText = extractLineText(currentPlan.interventions)
}

/**
 * 将页面表单状态整理为干预计划接口需要的最小 payload。
 */
function buildPlanPayload(): MtmPlanDraftPayload {
  return {
    priority: (form.priority || undefined) as 'low' | 'medium' | 'high' | 'urgent' | undefined,
    interventions: parseLines(form.interventionsText).map(item => ({
      item,
    })),
  }
}

/**
 * 在前端先做一层最小完成校验，减少无效提交。
 */
function buildCompletionIssues(): string[] {
  const issues: string[] = []

  if (!form.priority) {
    issues.push('优先级')
  }

  if (!parseLines(form.interventionsText).length) {
    issues.push('至少一项干预措施')
  }

  return issues
}

/**
 * 加载服务单详情与干预计划草稿，供当前表单页编辑。
 */
async function loadPlanForm() {
  if (!serviceCaseId.value) {
    loadError.value = '缺少服务单编号，暂时无法进入干预计划表单。'
    return
  }

  try {
    loading.value = true
    loadError.value = ''
    log('🔵 [MtmPlanFormPage] 开始加载干预计划表单', {
      serviceCaseId: serviceCaseId.value,
    })
    const [detail, planData] = await Promise.all([
      mtmApi.getServiceCaseDetail(serviceCaseId.value),
      mtmApi.getPlan(serviceCaseId.value),
    ])
    serviceCase.value = detail
    plan.value = planData
    syncFormFromPlan(planData)
    log('🟢 [MtmPlanFormPage] 干预计划表单加载成功', {
      detail,
      planData,
    })
  } catch (error) {
    if (isRequestCancelledError(error)) {
      log('🟡 [MtmPlanFormPage] 干预计划表单请求已取消')
      return
    }

    console.error('🔴 [MtmPlanFormPage] 干预计划加载失败', error)
    loadError.value = error instanceof Error ? error.message : '干预计划内容加载失败，请稍后重试'
    showError(loadError.value)
  } finally {
    loading.value = false
  }
}

/**
 * 手动保存当前干预计划草稿。
 */
async function handleSaveDraft() {
  if (!serviceCaseId.value || saving.value || completing.value) {
    return
  }

  try {
    saving.value = true
    const payload = buildPlanPayload()
    log('🔵 [MtmPlanFormPage] 开始保存干预计划草稿', {
      serviceCaseId: serviceCaseId.value,
      payload,
    })
    const res = await mtmApi.savePlanDraft(serviceCaseId.value, payload)
    plan.value = res
    showSuccess('干预计划草稿已保存')
    log('🟢 [MtmPlanFormPage] 干预计划草稿保存成功', plan.value)
  } catch (error) {
    console.error('🔴 [MtmPlanFormPage] 干预计划草稿保存失败', error)
    showError(error instanceof Error ? error.message : '干预计划草稿保存失败')
  } finally {
    saving.value = false
  }
}

/**
 * 提交当前干预计划内容，并标记为已完成。
 */
async function handleCompletePlan() {
  if (!serviceCaseId.value || saving.value || completing.value) {
    return
  }

  const issues = buildCompletionIssues()
  if (issues.length) {
    showError(`完成前请先补充：${issues.join('、')}`)
    return
  }

  try {
    completing.value = true
    const payload = buildPlanPayload()
    log('🔵 [MtmPlanFormPage] 开始完成干预计划', {
      serviceCaseId: serviceCaseId.value,
      payload,
    })
    const res = await mtmApi.completePlan(serviceCaseId.value, payload)
    plan.value = res
    showSuccess('干预计划已完成，当前不会自动推进服务状态')
    log('🟢 [MtmPlanFormPage] 干预计划完成成功', plan.value)
    await router.push({
      path: `/mtm/service-cases/${serviceCaseId.value}`,
      query: { ...route.query },
    })
  } catch (error) {
    console.error('🔴 [MtmPlanFormPage] 完成干预计划失败', error)
    showError(error instanceof Error ? error.message : '完成干预计划失败')
  } finally {
    completing.value = false
  }
}

/**
 * 返回服务单详情页。
 */
function goBack() {
  if (!serviceCaseId.value) {
    router.push('/mtm/service-cases')
    return
  }
  router.push({
    path: `/mtm/service-cases/${serviceCaseId.value}`,
    query: { ...route.query },
  })
}

onMounted(() => {
  void loadPlanForm()
})
</script>