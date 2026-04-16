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
            @click="handleCompleteAssessment"
          >
            <RefreshCw v-if="completing" class="h-4 w-4 animate-spin" />
            <CheckCircle2 v-else class="h-4 w-4" />
            {{ completing ? '提交中...' : '完成评估' }}
          </button>
        </div>
      </div>

      <section class="mt-6 rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
        <div class="flex items-start gap-3">
          <HeartPulse class="mt-1 h-5 w-5 text-rose-600" />
          <div>
            <h1 class="text-2xl font-semibold text-slate-900">用药评估表单</h1>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              先把当前风险、主要问题和综合判断整理清楚。你可以先手动保存草稿，确认没问题后再标记完成。
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
          v-if="serviceCase?.interview?.completed_at"
          class="mt-5 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm leading-6 text-emerald-700"
        >
          问诊已完成，你现在可以继续整理风险、问题清单和综合评估结论。
        </p>

        <p
          v-else
          class="mt-5 rounded-2xl border border-amber-100 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-800"
        >
          当前还没有看到已完成的问诊记录。你仍可先保存评估草稿，但更建议先把问诊内容补完整。
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
        正在加载评估内容...
      </div>

      <template v-else-if="serviceCase">
        <section class="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">
          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">五维评分</h2>
            <p class="mt-2 text-sm leading-6 text-slate-500">
              可以先填你最有把握的部分，不必一次全部填满；分值范围是 0 到 100。
            </p>

            <div class="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
              <label v-for="item in scoreFields" :key="item.key" class="block">
                <span class="text-sm font-medium text-slate-700">{{ item.label }}</span>
                <input
                  v-model="form[item.key]"
                  type="number"
                  min="0"
                  max="100"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
                  :placeholder="item.placeholder"
                />
              </label>
            </div>
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">综合风险等级</h2>
            <p class="mt-2 text-sm leading-6 text-slate-500">
              用一句最直观的判断，先标记当前整体风险高低。
            </p>

            <label class="mt-5 block">
              <span class="text-sm font-medium text-slate-700">风险等级</span>
              <select
                v-model="form.riskLevel"
                class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
              >
                <option value="">请选择</option>
                <option value="low">低风险</option>
                <option value="medium">中风险</option>
                <option value="high">高风险</option>
              </select>
            </label>
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">问题清单</h2>
            <p class="mt-2 text-sm leading-6 text-slate-500">
              一行写一项问题，例如重复用药、依从性差、不良反应风险等。
            </p>
            <textarea
              v-model="form.problemListText"
              rows="8"
              class="mt-4 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-sky-400"
              placeholder="例如：&#10;存在重复用药风险&#10;近期依从性偏低"
            />
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">评估总结</h2>
            <p class="mt-2 text-sm leading-6 text-slate-500">
              用一段人话总结当前最需要关注的问题和下一步判断。
            </p>
            <textarea
              v-model="form.summary"
              rows="8"
              class="mt-4 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-sky-400"
              placeholder="例如：当前方案需要优先关注依从性和安全性风险，建议下一步先明确重复用药与漏服原因。"
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
  HeartPulse,
  RefreshCw,
  Save,
} from 'lucide-vue-next'
import { mtmApi } from '@/api/mtm'
import { useToast } from '@/composables/useToast'
import type {
  MtmAssessmentDraftPayload,
  MtmAssessmentSummary,
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
const assessment = ref<MtmAssessmentSummary | null>(null)
const loading = ref(false)
const saving = ref(false)
const completing = ref(false)
const loadError = ref('')

const form = reactive({
  appropriatenessScore: '',
  effectivenessScore: '',
  safetyScore: '',
  adherenceScore: '',
  economicScore: '',
  riskLevel: '',
  problemListText: '',
  summary: '',
})

const scoreFields = [
  { key: 'appropriatenessScore', label: '适宜性评分', placeholder: '例如：80' },
  { key: 'effectivenessScore', label: '有效性评分', placeholder: '例如：75' },
  { key: 'safetyScore', label: '安全性评分', placeholder: '例如：60' },
  { key: 'adherenceScore', label: '依从性评分', placeholder: '例如：55' },
  { key: 'economicScore', label: '经济性评分', placeholder: '例如：70' },
] as const

const serviceCaseId = computed(() => String(route.params.id || '').trim())
const statusText = computed(() =>
  serviceCase.value ? getMtmStatusText(serviceCase.value.status) : '未开始'
)
const completionHint = computed(() => buildCompletionIssues().join('、'))

/**
 * 把未知值转成适合表单回填的纯文本。
 */
function asText(value: unknown): string {
  if (value === null || value === undefined) {
    return ''
  }
  if (typeof value === 'string') {
    return value.trim()
  }
  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }
  return ''
}

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
        for (const key of ['item', 'summary', 'title', 'name', 'label', 'type']) {
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
 * 把输入框中的值统一转成可安全处理的文本。
 */
function normalizeInputText(value: unknown): string {
  if (typeof value === 'string') {
    return value.trim()
  }
  if (typeof value === 'number' && Number.isFinite(value)) {
    return String(value)
  }
  return ''
}

/**
 * 把输入框中的分值转成接口需要的数字或空值。
 */
function parseScoreValue(value: unknown): number | null {
  const normalized = normalizeInputText(value)
  if (!normalized) {
    return null
  }
  const parsed = Number(normalized)
  if (!Number.isFinite(parsed)) {
    return null
  }
  return Math.max(0, Math.min(100, Math.round(parsed)))
}

/**
 * 把后端评估摘要同步到页面表单状态。
 */
function syncFormFromAssessment(currentAssessment: MtmAssessmentSummary) {
  form.appropriatenessScore = asText(currentAssessment.appropriateness_score)
  form.effectivenessScore = asText(currentAssessment.effectiveness_score)
  form.safetyScore = asText(currentAssessment.safety_score)
  form.adherenceScore = asText(currentAssessment.adherence_score)
  form.economicScore = asText(currentAssessment.economic_score)
  form.riskLevel = currentAssessment.risk_level || ''
  form.problemListText = extractLineText(currentAssessment.problem_list)
  form.summary = currentAssessment.summary || ''
}

/**
 * 将页面表单状态整理为评估接口需要的最小 payload。
 */
function buildAssessmentPayload(): MtmAssessmentDraftPayload {
  return {
    appropriateness_score: parseScoreValue(form.appropriatenessScore),
    effectiveness_score: parseScoreValue(form.effectivenessScore),
    safety_score: parseScoreValue(form.safetyScore),
    adherence_score: parseScoreValue(form.adherenceScore),
    economic_score: parseScoreValue(form.economicScore),
    risk_level: (form.riskLevel || undefined) as 'low' | 'medium' | 'high' | undefined,
    problem_list: parseLines(form.problemListText).map(item => ({
      item,
    })),
    summary: form.summary.trim(),
  }
}

/**
 * 在前端先做一层最小完成校验，减少无效提交。
 */
function buildCompletionIssues(): string[] {
  const issues: string[] = []
  const scoreValues = [
    form.appropriatenessScore,
    form.effectivenessScore,
    form.safetyScore,
    form.adherenceScore,
    form.economicScore,
  ]

  if (!scoreValues.some(item => normalizeInputText(item))) {
    issues.push('至少一项评估评分')
  }

  if (!form.riskLevel) {
    issues.push('综合风险等级')
  }

  if (!parseLines(form.problemListText).length && !form.summary.trim()) {
    issues.push('问题清单或评估总结')
  }

  return issues
}

/**
 * 加载服务单详情与评估草稿，供当前表单页编辑。
 */
async function loadAssessmentForm() {
  if (!serviceCaseId.value) {
    loadError.value = '缺少服务单编号，暂时无法进入评估表单。'
    return
  }

  try {
    loading.value = true
    loadError.value = ''
    log('🔵 [MtmAssessmentFormPage] 开始加载评估表单', {
      serviceCaseId: serviceCaseId.value,
    })
    const [detail, assessmentData] = await Promise.all([
      mtmApi.getServiceCaseDetail(serviceCaseId.value),
      mtmApi.getAssessment(serviceCaseId.value),
    ])
    serviceCase.value = detail
    assessment.value = assessmentData
    syncFormFromAssessment(assessmentData)
    log('🟢 [MtmAssessmentFormPage] 评估表单加载成功', {
      detail,
      assessmentData,
    })
  } catch (error) {
    if (isRequestCancelledError(error)) {
      log('🟡 [MtmAssessmentFormPage] 评估表单请求已取消')
      return
    }

    console.error('🔴 [MtmAssessmentFormPage] 评估表单加载失败', error)
    loadError.value = error instanceof Error ? error.message : '评估内容加载失败，请稍后重试'
    showError(loadError.value)
  } finally {
    loading.value = false
  }
}

/**
 * 手动保存当前评估草稿。
 */
async function handleSaveDraft() {
  if (!serviceCaseId.value || saving.value || completing.value) {
    return
  }

  try {
    saving.value = true
    const payload = buildAssessmentPayload()
    log('🔵 [MtmAssessmentFormPage] 开始保存评估草稿', {
      serviceCaseId: serviceCaseId.value,
      payload,
    })
    assessment.value = await mtmApi.saveAssessmentDraft(serviceCaseId.value, payload)
    showSuccess('评估草稿已保存')
    log('🟢 [MtmAssessmentFormPage] 评估草稿保存成功', assessment.value)
  } catch (error) {
    console.error('🔴 [MtmAssessmentFormPage] 评估草稿保存失败', error)
    showError(error instanceof Error ? error.message : '评估草稿保存失败')
  } finally {
    saving.value = false
  }
}

/**
 * 提交当前评估内容，并标记为已完成。
 */
async function handleCompleteAssessment() {
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
    const payload = buildAssessmentPayload()
    log('🔵 [MtmAssessmentFormPage] 开始完成评估', {
      serviceCaseId: serviceCaseId.value,
      payload,
    })
    assessment.value = await mtmApi.completeAssessment(serviceCaseId.value, payload)
    showSuccess('评估已完成，当前不会自动推进服务状态')
    log('🟢 [MtmAssessmentFormPage] 评估完成成功', assessment.value)
    await router.push({
      path: `/mtm/service-cases/${serviceCaseId.value}`,
      query: { ...route.query },
    })
  } catch (error) {
    console.error('🔴 [MtmAssessmentFormPage] 完成评估失败', error)
    showError(error instanceof Error ? error.message : '完成评估失败')
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
  void loadAssessmentForm()
})
</script>
