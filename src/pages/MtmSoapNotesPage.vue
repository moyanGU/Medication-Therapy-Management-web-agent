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
          <h1 class="text-2xl font-bold text-slate-900">SOAP 结构化药历</h1>
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

      <template v-else-if="serviceCase">
        <div class="mb-6 rounded-3xl border border-violet-100 bg-violet-50 p-6 shadow-sm">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 class="text-lg font-semibold text-violet-900 flex items-center gap-2">
                <Sparkles class="h-5 w-5 text-violet-600" />
                AI 药师助理 (Copilot)
              </h2>
              <p class="mt-2 text-sm text-violet-700 max-w-xl">
                利用大模型深度分析患者的问诊纪要、评估结果和干预计划，一键为您生成标准的 SOAP 药历草稿。
              </p>
            </div>
            <button
              type="button"
              class="inline-flex items-center justify-center gap-2 self-start rounded-xl bg-violet-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-violet-700 disabled:opacity-50"
              :disabled="generating || saving"
              @click="generateSoapByAi"
            >
              <span v-if="generating" class="h-4 w-4 animate-spin rounded-full border-b-2 border-white"></span>
              <Sparkles v-else class="h-4 w-4" />
              {{ generating ? 'AI 正在分析生成中...' : '一键生成药历' }}
            </button>
          </div>
        </div>

        <form class="space-y-6" @submit.prevent="saveSoap">
          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm space-y-6">
            
            <!-- S: Subjective -->
            <div>
              <div class="flex items-center gap-2 mb-3">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-100 text-sky-700 font-bold">S</div>
                <h3 class="text-base font-semibold text-slate-900">Subjective (主观资料)</h3>
              </div>
              <textarea
                v-model="form.subjective"
                rows="4"
                class="block w-full rounded-xl border-slate-300 bg-slate-50 py-3 text-slate-900 focus:border-violet-500 focus:ring-violet-500 sm:text-sm"
                placeholder="记录患者主诉、病史、过敏史、生活习惯等主观描述..."
              ></textarea>
            </div>

            <!-- O: Objective -->
            <div>
              <div class="flex items-center gap-2 mb-3">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700 font-bold">O</div>
                <h3 class="text-base font-semibold text-slate-900">Objective (客观资料)</h3>
              </div>
              <textarea
                v-model="form.objective"
                rows="4"
                class="block w-full rounded-xl border-slate-300 bg-slate-50 py-3 text-slate-900 focus:border-violet-500 focus:ring-violet-500 sm:text-sm"
                placeholder="记录生命体征、实验室检查指标、当前实际用药记录等客观数据..."
              ></textarea>
            </div>

            <!-- A: Assessment -->
            <div>
              <div class="flex items-center gap-2 mb-3">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100 text-amber-700 font-bold">A</div>
                <h3 class="text-base font-semibold text-slate-900">Assessment (评估分析)</h3>
              </div>
              <textarea
                v-model="form.assessment"
                rows="4"
                class="block w-full rounded-xl border-slate-300 bg-slate-50 py-3 text-slate-900 focus:border-violet-500 focus:ring-violet-500 sm:text-sm"
                placeholder="记录药物治疗问题(DRPs)分析、依从性评估、疾病控制评估等..."
              ></textarea>
            </div>

            <!-- P: Plan -->
            <div>
              <div class="flex items-center gap-2 mb-3">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-rose-100 text-rose-700 font-bold">P</div>
                <h3 class="text-base font-semibold text-slate-900">Plan (干预计划)</h3>
              </div>
              <textarea
                v-model="form.plan"
                rows="4"
                class="block w-full rounded-xl border-slate-300 bg-slate-50 py-3 text-slate-900 focus:border-violet-500 focus:ring-violet-500 sm:text-sm"
                placeholder="记录具体的干预措施、药物调整建议、生活方式指导及随访安排..."
              ></textarea>
            </div>

          </article>

          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              class="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-6 py-3 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-300 transition hover:bg-slate-50 disabled:opacity-50"
              @click="goBack"
              :disabled="saving || generating"
            >
              取消
            </button>
            <button
              type="submit"
              class="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-8 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 disabled:opacity-50"
              :disabled="saving || generating"
            >
              <Save class="h-4 w-4" />
              {{ saving ? '保存中...' : '保存 SOAP 药历' }}
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
  RefreshCw,
  Save,
  Sparkles,
} from 'lucide-vue-next'
import { mtmApi } from '@/api/mtm'
import { useToast } from '@/composables/useToast'
import type { MtmServiceCase } from '@/types/mtm'

const route = useRoute()
const router = useRouter()
const { success: showSuccess, error: showError } = useToast()

const serviceCase = ref<MtmServiceCase | null>(null)
const loading = ref(false)
const saving = ref(false)
const generating = ref(false)
const loadError = ref('')

const form = reactive({
  subjective: '',
  objective: '',
  assessment: '',
  plan: '',
})

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
    const soapNotes = await mtmApi.getSoapNotes(caseId)
    
    if (soapNotes) {
      form.subjective = soapNotes.subjective || ''
      form.objective = soapNotes.objective || ''
      form.assessment = soapNotes.assessment || ''
      form.plan = soapNotes.plan || ''
    }
  } catch (error: any) {
    loadError.value = error.message || '加载数据失败'
    showError(loadError.value)
  } finally {
    loading.value = false
  }
}

const generateSoapByAi = async () => {
  if (!serviceCase.value) return
  
  try {
    generating.value = true
    const aiResult = await mtmApi.generateSoapNotesByAi(serviceCase.value.id)
    
    // Fill the form with AI results
    if (aiResult) {
      form.subjective = aiResult.subjective || form.subjective
      form.objective = aiResult.objective || form.objective
      form.assessment = aiResult.assessment || form.assessment
      form.plan = aiResult.plan || form.plan
      showSuccess('AI 药历生成成功，请人工审核并微调。')
    }
  } catch (error: any) {
    showError(error.message || 'AI 生成失败，可能是服务未启用或请求超时')
  } finally {
    generating.value = false
  }
}

const saveSoap = async () => {
  if (!serviceCase.value) return
  try {
    saving.value = true
    const payload = {
      subjective: form.subjective,
      objective: form.objective,
      assessment: form.assessment,
      plan: form.plan,
    }
    await mtmApi.saveSoapNotes(serviceCase.value.id, payload)
    showSuccess('SOAP 药历保存成功')
    setTimeout(() => {
      goBack()
    }, 1000)
  } catch (error: any) {
    showError(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  void loadData()
})
</script>
