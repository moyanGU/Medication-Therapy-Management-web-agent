<template>
  <div class="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
    <header class="mb-8">
      <div class="flex items-center gap-4">
        <button
          type="button"
          class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-500 transition hover:bg-slate-200 hover:text-slate-900"
          @click="goBack"
        >
          <ArrowLeft class="h-5 w-5" />
        </button>
        <div>
          <h1 class="text-2xl font-bold text-slate-900">MTM 干预计划</h1>
          <p class="mt-1 text-sm text-slate-500">
            服务单：{{ serviceCase?.case_number || '加载中...' }}
          </p>
        </div>
      </div>
    </header>

    <main>
      <section v-if="loading && !serviceCase" class="space-y-6">
        <div class="h-48 animate-pulse rounded-3xl bg-white shadow-sm"></div>
      </section>

      <section v-else-if="loadError" class="rounded-3xl border border-red-100 bg-red-50 p-6 text-center">
        <AlertTriangle class="mx-auto h-8 w-8 text-red-500" />
        <h3 class="mt-4 text-sm font-medium text-red-800">{{ loadError }}</h3>
        <button
          type="button"
          class="mt-4 inline-flex items-center gap-2 rounded-xl bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
          @click="loadData"
        >
          <RefreshCw class="h-4 w-4" />
          重新加载
        </button>
      </section>

      <template v-else-if="serviceCase && plan">
        <div v-if="plan.confirmed_at" class="mb-6 rounded-2xl border border-emerald-100 bg-emerald-50 p-4">
          <p class="text-sm font-medium text-emerald-800">
            干预计划已制定完成
          </p>
          <p class="mt-1 text-xs text-emerald-600">
            患者已确认于 {{ formatDateTime(plan.confirmed_at) }}
          </p>
        </div>

        <form class="space-y-6" @submit.prevent="submitPlan">
          <!-- 基础信息 -->
          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900 mb-5">计划概要</h2>
            
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">优先级</label>
                <select
                  v-model="form.priority"
                  class="block w-full rounded-xl border-slate-300 bg-slate-50 py-2.5 text-slate-900 focus:border-violet-500 focus:ring-violet-500 sm:text-sm"
                  :disabled="!!plan.confirmed_at"
                >
                  <option value="low">低 (Low)</option>
                  <option value="medium">中 (Medium)</option>
                  <option value="high">高 (High)</option>
                  <option value="urgent">紧急 (Urgent)</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">确认状态</label>
                <select
                  v-model="form.patient_confirmation_status"
                  class="block w-full rounded-xl border-slate-300 bg-slate-50 py-2.5 text-slate-900 focus:border-violet-500 focus:ring-violet-500 sm:text-sm"
                  :disabled="!!plan.confirmed_at"
                >
                  <option value="pending">待确认 (Pending)</option>
                  <option value="confirmed">已确认 (Confirmed)</option>
                  <option value="declined">已拒绝 (Declined)</option>
                </select>
              </div>
            </div>
          </article>

          <!-- 干预措施 -->
          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900 mb-5">干预措施清单</h2>
            <p class="mb-4 text-sm text-slate-500">
              请列出具体的干预措施和行动计划，每行一条。
            </p>
            <textarea
              v-model="form.interventionsText"
              rows="6"
              class="block w-full rounded-xl border-slate-300 bg-slate-50 py-3 text-slate-900 focus:border-violet-500 focus:ring-violet-500 sm:text-sm"
              placeholder="例如：
1. 建议停用可能导致不良反应的药物A
2. 建议调整药物B的服用时间为饭后
3. 增加生活方式干预：每日30分钟有氧运动"
              :disabled="!!plan.confirmed_at"
            ></textarea>
          </article>

          <!-- 补充说明 -->
          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 class="text-lg font-semibold text-slate-900 mb-5">患者反馈与补充说明</h2>
            <textarea
              v-model="form.patientConfirmationNotes"
              rows="4"
              class="block w-full rounded-xl border-slate-300 bg-slate-50 py-3 text-slate-900 focus:border-violet-500 focus:ring-violet-500 sm:text-sm"
              placeholder="记录患者对计划的反馈意见或补充说明..."
              :disabled="!!plan.confirmed_at"
            ></textarea>
          </article>

          <!-- 操作区 -->
          <div v-if="!plan.confirmed_at" class="flex flex-col-reverse justify-end gap-3 sm:flex-row border-t border-slate-100 pt-6">
            <button
              type="button"
              class="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-6 py-3 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-300 transition hover:bg-slate-50 disabled:opacity-50"
              :disabled="saving || completing"
              @click="saveDraft"
            >
              <Save class="h-4 w-4" />
              {{ saving ? '保存中...' : '保存草稿' }}
            </button>
            <button
              type="submit"
              class="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-emerald-700 disabled:opacity-50"
              :disabled="saving || completing"
            >
              <ClipboardCheck class="h-4 w-4" />
              {{ completing ? '提交中...' : '完成计划制定' }}
            </button>
          </div>
        </form>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  AlertTriangle,
  ArrowLeft,
  ClipboardCheck,
  RefreshCw,
  Save,
} from 'lucide-vue-next'
import { mtmApi } from '@/api/mtm'
import { useToast } from '@/composables/useToast'
import type { MtmServiceCase, MtmPlanSummary } from '@/types/mtm'

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
  priority: 'medium',
  patient_confirmation_status: 'pending',
  interventionsText: '',
  patientConfirmationNotes: '',
})

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

const loadData = async () => {
  const caseId = route.params.id as string
  if (!caseId) {
    loadError.value = '未提供服务单ID'
    return
  }

  try {
    loading.value = true
    loadError.value = ''
    serviceCase.value = await mtmApi.getServiceCaseDetail(caseId)
    plan.value = await mtmApi.getPlan(caseId)
    
    // 初始化表单
    form.priority = plan.value.priority || 'medium'
    form.patient_confirmation_status = plan.value.patient_confirmation_status || 'pending'
    form.patientConfirmationNotes = plan.value.patient_confirmation_notes || ''
    
    if (Array.isArray(plan.value.interventions)) {
      form.interventionsText = plan.value.interventions.join('\n')
    } else {
      form.interventionsText = ''
    }
  } catch (error: any) {
    loadError.value = error.message || '加载计划数据失败'
    showError(loadError.value)
  } finally {
    loading.value = false
  }
}

const buildPayload = () => {
  return {
    priority: form.priority as 'low' | 'medium' | 'high' | 'urgent',
    patient_confirmation_status: form.patient_confirmation_status as 'pending' | 'confirmed' | 'declined',
    patient_confirmation_notes: form.patientConfirmationNotes,
    interventions: form.interventionsText
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0),
  }
}

const saveDraft = async () => {
  if (!serviceCase.value) return
  try {
    saving.value = true
    const payload = buildPayload()
    plan.value = await mtmApi.savePlanDraft(serviceCase.value.id, payload)
    showSuccess('草稿保存成功')
  } catch (error: any) {
    showError(error.message || '保存草稿失败')
  } finally {
    saving.value = false
  }
}

const submitPlan = async () => {
  if (!serviceCase.value) return
  
  const payload = buildPayload()
  if (!payload.interventions.length) {
    showError('干预措施列表不能为空')
    return
  }

  if (!confirm('完成计划后，服务单状态将进入干预阶段，确认提交吗？')) {
    return
  }

  try {
    completing.value = true
    plan.value = await mtmApi.completePlan(serviceCase.value.id, payload)
    showSuccess('干预计划制定完成！')
    setTimeout(() => {
      goBack()
    }, 1000)
  } catch (error: any) {
    showError(error.message || '提交失败')
  } finally {
    completing.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  void loadData()
})
</script>
