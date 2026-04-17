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

        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-full bg-sky-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-sky-300"
          :disabled="loading || saving"
          @click="handleSave"
        >
          <RefreshCw v-if="saving" class="h-4 w-4 animate-spin" />
          <Save v-else class="h-4 w-4" />
          {{ saving ? '保存中...' : '保存随访记录' }}
        </button>
      </div>

      <section class="mt-6 rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
        <div class="flex items-start gap-3">
          <CalendarClock class="mt-1 h-5 w-5 text-indigo-600" />
          <div>
            <h1 class="text-2xl font-semibold text-slate-900">
              {{ isEditMode ? '编辑随访记录' : '新增随访记录' }}
            </h1>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              记录每次与患者沟通的执行情况、风险变化和随访总结。
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
        正在加载...
      </div>

      <template v-else-if="serviceCase">
        <section class="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">
          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900">随访基础信息</h2>
            
            <div class="mt-5 space-y-4">
              <label class="block">
                <span class="text-sm font-medium text-slate-700">
                  随访时间 <span class="text-rose-500">*</span>
                </span>
                <input
                  v-model="form.followUpTime"
                  type="datetime-local"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-indigo-400"
                />
              </label>

              <label class="block">
                <span class="text-sm font-medium text-slate-700">随访方式</span>
                <select
                  v-model="form.followUpMethod"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-indigo-400"
                >
                  <option value="phone">电话</option>
                  <option value="in_person">面谈</option>
                  <option value="video">视频</option>
                  <option value="wechat">微信</option>
                  <option value="other">其他</option>
                </select>
              </label>

              <label class="block">
                <span class="text-sm font-medium text-slate-700">执行情况</span>
                <select
                  v-model="form.executionStatus"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-indigo-400"
                >
                  <option value="pending">待执行</option>
                  <option value="completed">已完成</option>
                  <option value="missed">未完成</option>
                  <option value="cancelled">已取消</option>
                </select>
              </label>
            </div>
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm xl:row-span-2">
            <h2 class="text-lg font-semibold text-slate-900">随访结论</h2>

            <div class="mt-5 space-y-4">
              <label class="block">
                <span class="text-sm font-medium text-slate-700">风险变化</span>
                <select
                  v-model="form.riskChange"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-indigo-400"
                >
                  <option value="unknown">暂未判断 / 未知</option>
                  <option value="improved">已有改善</option>
                  <option value="stable">基本稳定</option>
                  <option value="worsened">风险加重</option>
                </select>
              </label>

              <label class="block">
                <span class="text-sm font-medium text-slate-700">随访总结</span>
                <textarea
                  v-model="form.summary"
                  rows="6"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-indigo-400"
                  placeholder="记录本次沟通的主要内容、患者的用药反馈以及下一步建议等。"
                />
              </label>

              <label class="block">
                <span class="text-sm font-medium text-slate-700">建议下次随访时间</span>
                <input
                  v-model="form.nextFollowUpTime"
                  type="datetime-local"
                  class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-indigo-400"
                />
              </label>
            </div>
          </article>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, CalendarClock, RefreshCw, Save } from 'lucide-vue-next'
import { mtmApi } from '@/api/mtm'
import { useToast } from '@/composables/useToast'
import type { MtmFollowUpPayload, MtmFollowUpSummary, MtmServiceCase } from '@/types/mtm'
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
const followUp = ref<MtmFollowUpSummary | null>(null)
const loading = ref(false)
const saving = ref(false)
const loadError = ref('')

const serviceCaseId = computed(() => String(route.params.caseId || '').trim())
const followUpId = computed(() => String(route.params.followUpId || '').trim())
const isEditMode = computed(() => followUpId.value && followUpId.value !== 'new')

const statusText = computed(() =>
  serviceCase.value ? getMtmStatusText(serviceCase.value.status) : '未开始'
)

// 格式化时间以适应 datetime-local input
const toLocalISOString = (isoString?: string | null) => {
  if (!isoString) return ''
  const date = new Date(isoString)
  if (Number.isNaN(date.getTime())) return ''
  // 补齐到 16 位，截掉秒和毫秒，例如: 2026-04-18T10:00
  const tzOffset = date.getTimezoneOffset() * 60000
  const localISOTime = new Date(date.getTime() - tzOffset).toISOString().slice(0, 16)
  return localISOTime
}

const toUTCISOString = (localString?: string) => {
  if (!localString) return null
  const date = new Date(localString)
  if (Number.isNaN(date.getTime())) return null
  return date.toISOString()
}

const form = reactive({
  followUpTime: '',
  followUpMethod: 'phone',
  executionStatus: 'pending',
  riskChange: 'unknown',
  summary: '',
  nextFollowUpTime: '',
})

async function loadData() {
  if (!serviceCaseId.value) {
    loadError.value = '缺少服务单编号，暂时无法进入随访表单。'
    return
  }

  try {
    loading.value = true
    loadError.value = ''
    log('🔵 [MtmFollowUpFormPage] 开始加载数据', {
      serviceCaseId: serviceCaseId.value,
      followUpId: followUpId.value,
    })

    const detail = await mtmApi.getServiceCaseDetail(serviceCaseId.value)
    serviceCase.value = detail

    if (isEditMode.value) {
      const followUpRes = await mtmApi.getFollowUp(followUpId.value)
      followUp.value = followUpRes
      
      // 同步到表单
      if (followUp.value) {
        form.followUpTime = toLocalISOString(followUp.value.follow_up_time)
        form.followUpMethod = followUp.value.follow_up_method || 'phone'
        form.executionStatus = followUp.value.execution_status || 'pending'
        form.riskChange = followUp.value.risk_change || 'unknown'
        form.summary = followUp.value.summary || ''
        form.nextFollowUpTime = toLocalISOString(followUp.value.next_follow_up_time)
      }
    } else {
      // 新增时默认时间为当前
      form.followUpTime = toLocalISOString(new Date().toISOString())
    }

    log('🟢 [MtmFollowUpFormPage] 数据加载成功')
  } catch (error) {
    if (isRequestCancelledError(error)) return
    console.error('🔴 [MtmFollowUpFormPage] 数据加载失败', error)
    loadError.value = error instanceof Error ? error.message : '内容加载失败，请稍后重试'
    showError(loadError.value)
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!serviceCaseId.value || saving.value) return

  if (!form.followUpTime) {
    showError('随访时间不能为空')
    return
  }

  try {
    saving.value = true
    const payload: MtmFollowUpPayload = {
      service_case: serviceCaseId.value,
      follow_up_time: toUTCISOString(form.followUpTime)!,
      follow_up_method: form.followUpMethod,
      execution_status: form.executionStatus,
      risk_change: form.riskChange,
      summary: form.summary.trim(),
      next_follow_up_time: toUTCISOString(form.nextFollowUpTime),
    }

    log('🔵 [MtmFollowUpFormPage] 开始保存随访', payload)
    
    if (isEditMode.value) {
      await mtmApi.updateFollowUp(followUpId.value, payload)
    } else {
      await mtmApi.createFollowUp(payload)
    }

    showSuccess('随访记录保存成功')
    goBack()
  } catch (error) {
    console.error('🔴 [MtmFollowUpFormPage] 随访保存失败', error)
    showError(error instanceof Error ? error.message : '随访保存失败')
  } finally {
    saving.value = false
  }
}

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
  void loadData()
})
</script>