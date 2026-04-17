<template>
  <div class="min-h-screen bg-slate-50">
    <main class="mx-auto max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
      <button
        type="button"
        class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
        @click="goBack"
      >
        <ArrowLeft class="h-4 w-4" />
        返回详情
      </button>

      <section class="mt-6 rounded-3xl border border-slate-100 bg-white p-6 shadow-sm sm:p-8">
        <div class="flex items-start gap-3">
          <ClipboardCheck class="mt-1 h-6 w-6 text-indigo-600" />
          <div>
            <h1 class="text-2xl font-semibold text-slate-900">干预计划确认</h1>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              药师已为您起草了用药干预计划。请仔细阅读以下措施，并反馈您的执行意愿。
            </p>
          </div>
        </div>

        <div
          v-if="loadError"
          class="mt-6 rounded-2xl border border-rose-100 bg-rose-50 px-5 py-4 text-sm leading-6 text-rose-700"
        >
          {{ loadError }}
        </div>

        <div
          v-if="loading"
          class="mt-6 rounded-3xl border border-slate-100 bg-white px-5 py-10 text-center text-sm text-slate-500 shadow-sm"
        >
          正在加载干预计划内容...
        </div>

        <template v-else-if="plan">
          <div class="mt-8 rounded-2xl border border-indigo-100 bg-indigo-50/50 p-6">
            <h3 class="text-base font-semibold text-slate-900">
              药师制定的干预措施
            </h3>
            <ul class="mt-4 list-inside list-disc space-y-3 pl-2 text-sm leading-6 text-slate-700">
              <li v-for="(item, index) in interventionLines" :key="index">
                {{ item }}
              </li>
            </ul>
            <div class="mt-6 border-t border-indigo-100/60 pt-4">
              <p class="text-xs font-medium text-indigo-800">
                优先级：{{ priorityText }}
              </p>
            </div>
          </div>

          <form @submit.prevent="handleSubmit" class="mt-10 border-t border-slate-100 pt-8">
            <h3 class="text-base font-semibold text-slate-900">请确认您的执行意愿</h3>

            <div class="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label
                class="relative flex cursor-pointer rounded-2xl border bg-white p-5 transition focus-within:ring-2 focus-within:ring-indigo-600"
                :class="
                  form.status === 'confirmed'
                    ? 'border-indigo-600 bg-indigo-50/30'
                    : 'border-slate-200 hover:border-slate-300'
                "
              >
                <div class="flex w-full items-center justify-between">
                  <div class="flex items-center">
                    <div class="text-sm">
                      <p class="font-medium text-slate-900">同意执行</p>
                      <p class="text-slate-500">我已了解并同意按照以上建议执行</p>
                    </div>
                  </div>
                  <input
                    v-model="form.status"
                    type="radio"
                    name="confirm_status"
                    value="confirmed"
                    class="h-4 w-4 border-slate-300 text-indigo-600 focus:ring-indigo-600"
                  />
                </div>
              </label>

              <label
                class="relative flex cursor-pointer rounded-2xl border bg-white p-5 transition focus-within:ring-2 focus-within:ring-rose-600"
                :class="
                  form.status === 'declined'
                    ? 'border-rose-600 bg-rose-50/30'
                    : 'border-slate-200 hover:border-slate-300'
                "
              >
                <div class="flex w-full items-center justify-between">
                  <div class="flex items-center">
                    <div class="text-sm">
                      <p class="font-medium text-slate-900">暂不执行</p>
                      <p class="text-slate-500">我有其他顾虑或无法执行该建议</p>
                    </div>
                  </div>
                  <input
                    v-model="form.status"
                    type="radio"
                    name="confirm_status"
                    value="declined"
                    class="h-4 w-4 border-slate-300 text-rose-600 focus:ring-rose-600"
                  />
                </div>
              </label>
            </div>

            <div class="mt-6">
              <label class="block text-sm font-medium text-slate-700">补充说明（选填）</label>
              <textarea
                v-model="form.notes"
                rows="4"
                class="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-indigo-400"
                placeholder="如果您选择了暂不执行，或者有其他疑问，请在此补充说明..."
              ></textarea>
            </div>

            <div class="mt-8 flex items-center justify-end gap-4">
              <button
                type="button"
                class="rounded-full px-5 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-slate-100"
                @click="goBack"
                :disabled="submitting"
              >
                取消
              </button>
              <button
                type="submit"
                class="inline-flex items-center gap-2 rounded-full bg-indigo-600 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-indigo-300"
                :disabled="submitting || !form.status"
              >
                <RefreshCw v-if="submitting" class="h-4 w-4 animate-spin" />
                提交确认
              </button>
            </div>
          </form>
        </template>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, ClipboardCheck, RefreshCw } from 'lucide-vue-next'
import { mtmApi } from '@/api/mtm'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import type { MtmPlanSummary, MtmServiceCase } from '@/types/mtm'

const route = useRoute()
const router = useRouter()
const { success: showSuccess, error: showError } = useToast()
const authStore = useAuthStore()

const serviceCaseId = computed(() => String(route.params.id || '').trim())
const serviceCase = ref<MtmServiceCase | null>(null)
const plan = ref<MtmPlanSummary | null>(null)

const loading = ref(false)
const submitting = ref(false)
const loadError = ref('')

const form = reactive({
  status: '' as 'confirmed' | 'declined' | '',
  notes: '',
})

const interventionLines = computed(() => {
  const items = plan.value?.interventions
  if (!Array.isArray(items)) return []
  return items.map(item => {
    if (typeof item === 'string') return item.trim()
    if (item && typeof item === 'object') {
      const record = item as Record<string, unknown>
      return String(record.item || record.summary || record.title || '').trim()
    }
    return ''
  }).filter(Boolean)
})

const priorityText = computed(() => {
  const map: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急',
  }
  return plan.value?.priority ? map[plan.value.priority] || '未知' : '未知'
})

async function loadData() {
  if (!serviceCaseId.value) {
    loadError.value = '缺少服务单编号。'
    return
  }

  try {
    loading.value = true
    loadError.value = ''
    const detail = await mtmApi.getServiceCaseDetail(serviceCaseId.value)
    serviceCase.value = detail

    if (detail.patient.id !== authStore.user?.id) {
      loadError.value = '只有患者本人可以确认干预计划。'
      return
    }

    if (!detail.plan || !detail.plan.completed_at) {
      loadError.value = '干预计划尚未起草完成，暂时无法确认。'
      return
    }

    plan.value = detail.plan
    if (plan.value.patient_confirmation_status !== 'pending') {
      form.status = plan.value.patient_confirmation_status
      form.notes = plan.value.patient_confirmation_notes || ''
    }
  } catch (error) {
    console.error('🔴 [MtmPlanConfirmationPage] 加载失败', error)
    loadError.value = error instanceof Error ? error.message : '内容加载失败'
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!serviceCaseId.value || submitting.value || !form.status) return

  try {
    submitting.value = true
    await mtmApi.confirmPlan(serviceCaseId.value, {
      status: form.status,
      notes: form.notes.trim(),
    })
    showSuccess('干预计划确认成功')
    goBack()
  } catch (error) {
    console.error('🔴 [MtmPlanConfirmationPage] 确认失败', error)
    showError(error instanceof Error ? error.message : '确认失败，请稍后重试')
  } finally {
    submitting.value = false
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