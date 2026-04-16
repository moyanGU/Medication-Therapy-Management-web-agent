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
            @click="handleCompleteInterview"
          >
            <RefreshCw v-if="completing" class="h-4 w-4 animate-spin" />
            <CheckCircle2 v-else class="h-4 w-4" />
            {{ completing ? '提交中...' : '完成问诊' }}
          </button>
        </div>
      </div>

      <section class="mt-6 rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
        <div class="flex items-start gap-3">
          <ClipboardList class="mt-1 h-5 w-5 text-sky-600" />
          <div>
            <h1 class="text-2xl font-semibold text-slate-900">药学问诊表单</h1>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              先把基础情况、当前用药和本次关注点整理清楚。你可以先手动保存草稿，确认没问题后再标记完成。
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
          v-if="serviceCase?.service_goal"
          class="mt-5 rounded-2xl border border-sky-100 bg-sky-50 px-4 py-3 text-sm leading-6 text-sky-800"
        >
          本次服务目标：{{ serviceCase.service_goal }}
        </p>

        <p
          v-if="completionHint"
          class="mt-5 rounded-2xl border border-amber-100 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-800"
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
        正在加载问诊内容...
      </div>

      <template v-else-if="serviceCase">
        <section class="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">
          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">基础信息</h2>
            <div class="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
              <label class="block">
                <span class="text-sm font-medium text-slate-700">患者姓名</span>
                <input
                  v-model="form.patientName"
                  type="text"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
                  placeholder="例如：张阿姨"
                />
              </label>
              <label class="block">
                <span class="text-sm font-medium text-slate-700">年龄</span>
                <input
                  v-model="form.age"
                  type="text"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
                  placeholder="例如：72"
                />
              </label>
              <label class="block">
                <span class="text-sm font-medium text-slate-700">性别</span>
                <select
                  v-model="form.gender"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
                >
                  <option value="">请选择</option>
                  <option value="男">男</option>
                  <option value="女">女</option>
                  <option value="其他">其他</option>
                </select>
              </label>
              <label class="block">
                <span class="text-sm font-medium text-slate-700">联系电话</span>
                <input
                  v-model="form.contactPhone"
                  type="text"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
                  placeholder="例如：13800000000"
                />
              </label>
            </div>

            <label class="mt-4 block">
              <span class="text-sm font-medium text-slate-700">主要诊断或本次问题</span>
              <textarea
                v-model="form.mainDiagnosis"
                rows="3"
                class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-sky-400"
                placeholder="例如：高血压复诊，最近偶发头晕"
              />
            </label>
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">当前与既往用药</h2>
            <p class="mt-2 text-sm leading-6 text-slate-500">
              一行写一项，尽量写成“药名 + 用法用量”。
            </p>
            <textarea
              v-model="form.medicationHistoryText"
              rows="8"
              class="mt-4 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-sky-400"
              placeholder="例如：&#10;缬沙坦 80mg 每日一次&#10;二甲双胍 0.5g 每日两次"
            />
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">过敏与不良反应</h2>
            <p class="mt-2 text-sm leading-6 text-slate-500">
              一行写一项；如果没有，也可以先留空，后续再补。
            </p>
            <textarea
              v-model="form.allergyHistoryText"
              rows="6"
              class="mt-4 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-sky-400"
              placeholder="例如：&#10;青霉素过敏&#10;服用某药后胃部不适"
            />
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">生活方式</h2>
            <div class="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
              <label class="block">
                <span class="text-sm font-medium text-slate-700">吸烟情况</span>
                <input
                  v-model="form.smoking"
                  type="text"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
                  placeholder="例如：不吸烟"
                />
              </label>
              <label class="block">
                <span class="text-sm font-medium text-slate-700">饮酒情况</span>
                <input
                  v-model="form.drinking"
                  type="text"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
                  placeholder="例如：偶尔饮酒"
                />
              </label>
              <label class="block">
                <span class="text-sm font-medium text-slate-700">运动情况</span>
                <input
                  v-model="form.exercise"
                  type="text"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
                  placeholder="例如：每周散步三次"
                />
              </label>
              <label class="block">
                <span class="text-sm font-medium text-slate-700">睡眠情况</span>
                <input
                  v-model="form.sleep"
                  type="text"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400"
                  placeholder="例如：入睡困难，夜间易醒"
                />
              </label>
            </div>
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">经济与依从性背景</h2>
            <textarea
              v-model="form.economicContext"
              rows="5"
              class="mt-4 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-sky-400"
              placeholder="例如：希望尽量控制长期药费，平时由家属提醒服药"
            />
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">本次目标</h2>
            <textarea
              v-model="form.healthExpectations"
              rows="5"
              class="mt-4 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-sky-400"
              placeholder="例如：希望先梳理当前联合用药，减少头晕和漏服"
            />
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm xl:col-span-2">
            <h2 class="text-lg font-semibold text-slate-900">补充说明</h2>
            <textarea
              v-model="form.notes"
              rows="6"
              class="mt-4 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-sky-400"
              placeholder="例如：家属反馈最近记忆力下降，服药时间容易混乱"
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
import { ArrowLeft, CheckCircle2, ClipboardList, RefreshCw, Save } from 'lucide-vue-next'
import { mtmApi } from '@/api/mtm'
import { useToast } from '@/composables/useToast'
import type {
  MtmInterviewDraftPayload,
  MtmInterviewSummary,
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
const interview = ref<MtmInterviewSummary | null>(null)
const loading = ref(false)
const saving = ref(false)
const completing = ref(false)
const loadError = ref('')

const form = reactive({
  patientName: '',
  age: '',
  gender: '',
  contactPhone: '',
  mainDiagnosis: '',
  medicationHistoryText: '',
  allergyHistoryText: '',
  smoking: '',
  drinking: '',
  exercise: '',
  sleep: '',
  economicContext: '',
  healthExpectations: '',
  notes: '',
})

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
function extractLineText(items: unknown, preferredKeys: string[]): string {
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
        for (const key of preferredKeys) {
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
 * 把后端问诊摘要同步到页面表单状态。
 */
function syncFormFromInterview(detail: MtmServiceCase, currentInterview: MtmInterviewSummary) {
  const basicInfo = currentInterview.basic_info_snapshot || {}
  const lifestyle = currentInterview.lifestyle_info || {}

  form.patientName =
    asText((basicInfo as Record<string, unknown>).patient_name) || detail.patient.username
  form.age = asText((basicInfo as Record<string, unknown>).age)
  form.gender = asText((basicInfo as Record<string, unknown>).gender)
  form.contactPhone =
    asText((basicInfo as Record<string, unknown>).contact_phone) || detail.patient.phone || ''
  form.mainDiagnosis = asText((basicInfo as Record<string, unknown>).main_diagnosis)
  form.medicationHistoryText = extractLineText(currentInterview.medication_history, [
    'name',
    'drug_name',
    'title',
    'summary',
  ])
  form.allergyHistoryText = extractLineText(currentInterview.allergy_history, [
    'item',
    'name',
    'title',
    'summary',
  ])
  form.smoking = asText((lifestyle as Record<string, unknown>).smoking)
  form.drinking = asText((lifestyle as Record<string, unknown>).drinking)
  form.exercise = asText((lifestyle as Record<string, unknown>).exercise)
  form.sleep = asText((lifestyle as Record<string, unknown>).sleep)
  form.economicContext = currentInterview.economic_context || ''
  form.healthExpectations = currentInterview.health_expectations || ''
  form.notes = currentInterview.notes || ''
}

/**
 * 将页面表单状态整理为问诊接口需要的最小 payload。
 */
function buildInterviewPayload(): MtmInterviewDraftPayload {
  return {
    basic_info_snapshot: {
      patient_name: form.patientName.trim(),
      age: form.age.trim(),
      gender: form.gender.trim(),
      contact_phone: form.contactPhone.trim(),
      main_diagnosis: form.mainDiagnosis.trim(),
    },
    medication_history: parseLines(form.medicationHistoryText).map(item => ({
      name: item,
    })),
    allergy_history: parseLines(form.allergyHistoryText).map(item => ({
      item,
    })),
    lifestyle_info: {
      smoking: form.smoking.trim(),
      drinking: form.drinking.trim(),
      exercise: form.exercise.trim(),
      sleep: form.sleep.trim(),
    },
    economic_context: form.economicContext.trim(),
    health_expectations: form.healthExpectations.trim(),
    notes: form.notes.trim(),
  }
}

/**
 * 在前端先做一层最小完成校验，减少无效提交。
 */
function buildCompletionIssues(): string[] {
  const issues: string[] = []
  const hasBasicInfo = [
    form.patientName,
    form.age,
    form.gender,
    form.contactPhone,
    form.mainDiagnosis,
  ].some(item => item.trim())

  if (!hasBasicInfo) {
    issues.push('至少一项基础信息')
  }

  if (!parseLines(form.medicationHistoryText).length) {
    issues.push('当前或既往用药')
  }

  if (!form.healthExpectations.trim() && !form.notes.trim()) {
    issues.push('本次目标或补充说明')
  }

  return issues
}

/**
 * 加载服务单详情与问诊草稿，供当前表单页编辑。
 */
async function loadInterviewForm() {
  if (!serviceCaseId.value) {
    loadError.value = '缺少服务单编号，暂时无法进入问诊表单。'
    return
  }

  try {
    loading.value = true
    loadError.value = ''
    log('🔵 [MtmInterviewFormPage] 开始加载问诊表单', {
      serviceCaseId: serviceCaseId.value,
    })
    const [detail, interviewData] = await Promise.all([
      mtmApi.getServiceCaseDetail(serviceCaseId.value),
      mtmApi.getInterview(serviceCaseId.value),
    ])
    serviceCase.value = detail
    interview.value = interviewData
    syncFormFromInterview(detail, interviewData)
    log('🟢 [MtmInterviewFormPage] 问诊表单加载成功', {
      detail,
      interviewData,
    })
  } catch (error) {
    if (isRequestCancelledError(error)) {
      log('🟡 [MtmInterviewFormPage] 问诊表单请求已取消')
      return
    }

    console.error('🔴 [MtmInterviewFormPage] 问诊表单加载失败', error)
    loadError.value = error instanceof Error ? error.message : '问诊内容加载失败，请稍后重试'
    showError(loadError.value)
  } finally {
    loading.value = false
  }
}

/**
 * 手动保存当前问诊草稿。
 */
async function handleSaveDraft() {
  if (!serviceCaseId.value || saving.value || completing.value) {
    return
  }

  try {
    saving.value = true
    const payload = buildInterviewPayload()
    log('🔵 [MtmInterviewFormPage] 开始保存问诊草稿', {
      serviceCaseId: serviceCaseId.value,
      payload,
    })
    interview.value = await mtmApi.saveInterviewDraft(serviceCaseId.value, payload)
    showSuccess('问诊草稿已保存')
    log('🟢 [MtmInterviewFormPage] 问诊草稿保存成功', interview.value)
  } catch (error) {
    console.error('🔴 [MtmInterviewFormPage] 问诊草稿保存失败', error)
    showError(error instanceof Error ? error.message : '草稿保存失败')
  } finally {
    saving.value = false
  }
}

/**
 * 提交当前问诊内容，并标记为已完成。
 */
async function handleCompleteInterview() {
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
    const payload = buildInterviewPayload()
    log('🔵 [MtmInterviewFormPage] 开始完成问诊', {
      serviceCaseId: serviceCaseId.value,
      payload,
    })
    interview.value = await mtmApi.completeInterview(serviceCaseId.value, payload)
    showSuccess('问诊已完成，当前不会自动推进服务状态')
    log('🟢 [MtmInterviewFormPage] 问诊完成成功', interview.value)
    await router.push({
      path: `/mtm/service-cases/${serviceCaseId.value}`,
      query: { ...route.query },
    })
  } catch (error) {
    console.error('🔴 [MtmInterviewFormPage] 完成问诊失败', error)
    showError(error instanceof Error ? error.message : '完成问诊失败')
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
  void loadInterviewForm()
})
</script>
