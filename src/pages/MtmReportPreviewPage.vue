<template>
  <div class="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
    <header class="mb-8 print:hidden">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-4">
          <button
            type="button"
            class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-500 transition hover:bg-slate-200 hover:text-slate-900"
            @click="goBack"
          >
            <ArrowLeft class="h-5 w-5" />
          </button>
          <div>
            <h1 class="text-2xl font-bold text-slate-900">MTM 服务报告 (PMR & MAP)</h1>
            <p class="mt-1 text-sm text-slate-500">
              服务单号：{{ report?.case_info?.case_number || '加载中...' }}
            </p>
          </div>
        </div>
        
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-300 transition hover:bg-slate-50 disabled:opacity-50"
            :disabled="loading || exporting"
            @click="printReport"
          >
            <Printer class="h-4 w-4" />
            网页打印
          </button>
          <button
            type="button"
            class="inline-flex items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-violet-700 disabled:opacity-50"
            :disabled="loading || exporting"
            @click="exportPdf"
          >
            <span v-if="exporting" class="h-4 w-4 animate-spin rounded-full border-b-2 border-white"></span>
            <Download v-else class="h-4 w-4" />
            导出 PDF
          </button>
        </div>
      </div>
    </header>

    <main>
      <section v-if="loading && !report" class="space-y-6">
        <div class="h-96 animate-pulse rounded-3xl bg-white shadow-sm"></div>
      </section>

      <section v-else-if="loadError" class="rounded-3xl border border-red-100 bg-red-50 p-6 text-center print:hidden">
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

      <!-- 报告主体，用于打印和 PDF 截图 -->
      <div v-if="report" id="mtm-report-container" class="rounded-3xl bg-white p-8 shadow-sm print:shadow-none print:p-0">
        <!-- 报头 -->
        <div class="border-b-2 border-slate-900 pb-6 mb-8 text-center">
          <h1 class="text-3xl font-bold tracking-tight text-slate-900">药物治疗管理 (MTM) 综合报告</h1>
          <p class="mt-3 text-sm text-slate-500">
            生成日期：{{ formatDateTime(new Date().toISOString()) }} | 服务单号：{{ report.case_info.case_number }}
          </p>
        </div>

        <!-- 1. 患者基本信息 -->
        <div class="mb-10">
          <div class="flex items-center gap-2 mb-4 border-b border-slate-200 pb-2">
            <User class="h-5 w-5 text-violet-600" />
            <h2 class="text-xl font-bold text-slate-800">一、 患者基本信息</h2>
          </div>
          <div class="grid grid-cols-2 gap-4 text-sm sm:grid-cols-4 bg-slate-50 p-4 rounded-xl">
            <div>
              <span class="block text-slate-500">姓名</span>
              <span class="block font-medium text-slate-900 mt-1">{{ report.patient_info?.username || '未知' }}</span>
            </div>
            <div>
              <span class="block text-slate-500">年龄</span>
              <span class="block font-medium text-slate-900 mt-1">{{ report.patient_info?.age || '未知' }} 岁</span>
            </div>
            <div>
              <span class="block text-slate-500">性别</span>
              <span class="block font-medium text-slate-900 mt-1">{{ report.patient_info?.gender || '未知' }}</span>
            </div>
            <div>
              <span class="block text-slate-500">联系电话</span>
              <span class="block font-medium text-slate-900 mt-1">{{ report.patient_info?.phone || '未知' }}</span>
            </div>
          </div>
        </div>

        <!-- 2. PMR (个人用药记录) -->
        <div class="mb-10">
          <div class="flex items-center gap-2 mb-4 border-b border-slate-200 pb-2">
            <FileText class="h-5 w-5 text-violet-600" />
            <h2 class="text-xl font-bold text-slate-800">二、 个人用药记录 (PMR)</h2>
          </div>

          <div class="space-y-6">
            <!-- 过敏史 -->
            <div v-if="report.pmr.allergies?.length">
              <h3 class="text-base font-semibold text-slate-700 mb-2">过敏史</h3>
              <ul class="list-disc pl-5 text-sm text-rose-600 font-medium">
                <li v-for="(item, idx) in report.pmr.allergies" :key="idx">{{ item }}</li>
              </ul>
            </div>
            
            <!-- 历史用药记录 -->
            <div>
              <h3 class="text-base font-semibold text-slate-700 mb-3">当前/历史处方用药</h3>
              <div v-if="report.pmr.medical_records?.length" class="space-y-4">
                <div 
                  v-for="record in report.pmr.medical_records" 
                  :key="record.record_id"
                  class="rounded-xl border border-slate-200 p-4"
                >
                  <div class="flex justify-between items-start mb-3">
                    <div>
                      <span class="font-medium text-slate-900">{{ record.diagnosis }}</span>
                      <span class="text-xs text-slate-500 ml-2">@ {{ record.hospital }} - {{ record.department }}</span>
                    </div>
                    <span class="text-xs text-slate-500">{{ formatDate(record.visit_date) }}</span>
                  </div>
                  
                  <table class="min-w-full divide-y divide-slate-200 text-sm">
                    <thead>
                      <tr class="text-left text-slate-500">
                        <th class="pb-2 font-medium">药品名称</th>
                        <th class="pb-2 font-medium">单次剂量</th>
                        <th class="pb-2 font-medium">频次</th>
                        <th class="pb-2 font-medium">用药指导</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
                      <tr v-for="(med, idx) in record.medicines" :key="idx" class="text-slate-700">
                        <td class="py-2">{{ med.name }}</td>
                        <td class="py-2">{{ med.dosage }}</td>
                        <td class="py-2">{{ med.frequency }}</td>
                        <td class="py-2">{{ med.instructions }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <p v-else class="text-sm text-slate-500 italic">暂无处方用药记录。</p>
            </div>
          </div>
        </div>

        <!-- 3. 五维评估与问题清单 -->
        <div class="mb-10">
          <div class="flex items-center gap-2 mb-4 border-b border-slate-200 pb-2">
            <HeartPulse class="h-5 w-5 text-violet-600" />
            <h2 class="text-xl font-bold text-slate-800">三、 药物治疗评估摘要</h2>
          </div>
          
          <div v-if="report.assessment" class="space-y-6">
            <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div class="rounded-lg bg-slate-50 p-3 text-center border border-slate-100">
                <span class="block text-xs text-slate-500 mb-1">适宜性</span>
                <span class="block text-lg font-bold text-indigo-600">{{ report.assessment.appropriateness_score || '--' }}</span>
              </div>
              <div class="rounded-lg bg-slate-50 p-3 text-center border border-slate-100">
                <span class="block text-xs text-slate-500 mb-1">有效性</span>
                <span class="block text-lg font-bold text-indigo-600">{{ report.assessment.effectiveness_score || '--' }}</span>
              </div>
              <div class="rounded-lg bg-slate-50 p-3 text-center border border-slate-100">
                <span class="block text-xs text-slate-500 mb-1">安全性</span>
                <span class="block text-lg font-bold text-rose-600">{{ report.assessment.safety_score || '--' }}</span>
              </div>
              <div class="rounded-lg bg-slate-50 p-3 text-center border border-slate-100">
                <span class="block text-xs text-slate-500 mb-1">依从性</span>
                <span class="block text-lg font-bold text-indigo-600">{{ report.assessment.adherence_score || '--' }}</span>
              </div>
              <div class="rounded-lg bg-slate-50 p-3 text-center border border-slate-100">
                <span class="block text-xs text-slate-500 mb-1">综合风险</span>
                <span class="block text-sm font-bold text-amber-600 mt-1 uppercase">{{ report.assessment.risk_level }}</span>
              </div>
            </div>

            <div v-if="report.assessment.problem_list?.length">
              <h3 class="text-base font-semibold text-slate-700 mb-2">药物治疗问题清单 (DRPs)</h3>
              <ul class="list-decimal pl-5 text-sm text-slate-700 space-y-1">
                <li v-for="(item, idx) in report.assessment.problem_list" :key="idx">{{ item }}</li>
              </ul>
            </div>
            
            <div v-if="report.assessment.summary">
              <h3 class="text-base font-semibold text-slate-700 mb-2">评估总结</h3>
              <p class="text-sm text-slate-600 bg-slate-50 p-4 rounded-xl leading-relaxed">
                {{ report.assessment.summary }}
              </p>
            </div>
          </div>
          <p v-else class="text-sm text-slate-500 italic">尚未完成药物治疗评估。</p>
        </div>

        <!-- 4. MAP (药物行动计划) -->
        <div class="mb-10">
          <div class="flex items-center gap-2 mb-4 border-b border-slate-200 pb-2">
            <ClipboardCheck class="h-5 w-5 text-violet-600" />
            <h2 class="text-xl font-bold text-slate-800">四、 药物行动计划 (MAP)</h2>
          </div>
          
          <div v-if="report.map?.interventions?.length" class="space-y-4">
            <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
              <h3 class="text-base font-semibold text-emerald-900 mb-3">药师建议的行动措施</h3>
              <ul class="space-y-2 text-sm text-emerald-800">
                <li v-for="(item, idx) in report.map.interventions" :key="idx" class="flex items-start gap-2">
                  <span class="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-emerald-500"></span>
                  <span>{{ item }}</span>
                </li>
              </ul>
            </div>
            
            <div class="flex justify-between text-sm text-slate-500 px-2">
              <span>患者确认状态: <strong class="text-slate-700 uppercase">{{ report.map.patient_confirmation_status }}</strong></span>
              <span v-if="report.map.confirmed_at">确认时间: {{ formatDateTime(report.map.confirmed_at) }}</span>
            </div>
          </div>
          <p v-else class="text-sm text-slate-500 italic">尚未制定具体的药物行动计划。</p>
        </div>
        
        <!-- 签名区 -->
        <div class="mt-16 pt-8 border-t border-slate-200 flex justify-between px-8">
          <div class="text-center">
            <p class="text-sm text-slate-500 mb-8">负责药师签名 / 日期</p>
            <p class="text-base font-medium text-slate-900 border-b border-slate-300 pb-1 px-8 min-w-[200px]">
              {{ report.pharmacist_info?.username || '' }}
            </p>
          </div>
          <div class="text-center">
            <p class="text-sm text-slate-500 mb-8">患者或家属签名 / 日期</p>
            <p class="text-base font-medium text-slate-900 border-b border-slate-300 pb-1 px-8 min-w-[200px]"></p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  AlertTriangle,
  ArrowLeft,
  ClipboardCheck,
  Download,
  FileText,
  HeartPulse,
  Printer,
  RefreshCw,
  User,
} from 'lucide-vue-next'
import { mtmApi } from '@/api/mtm'
import { useToast } from '@/composables/useToast'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

const route = useRoute()
const router = useRouter()
const { success: showSuccess, error: showError } = useToast()

const report = ref<any>(null)
const loading = ref(false)
const exporting = ref(false)
const loadError = ref('')

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

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
    report.value = await mtmApi.getReport(caseId)
  } catch (error: any) {
    loadError.value = error.message || '加载报告数据失败'
    showError(loadError.value)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const printReport = () => {
  window.print()
}

const exportPdf = async () => {
  const container = document.getElementById('mtm-report-container')
  if (!container) return

  try {
    exporting.value = true
    
    // 隐藏一些可能影响打印的样式
    container.classList.remove('shadow-sm')
    
    const canvas = await html2canvas(container, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff'
    })
    
    // 恢复样式
    container.classList.add('shadow-sm')

    const imgData = canvas.toDataURL('image/jpeg', 1.0)
    
    // A4 尺寸 (210 x 297 mm)
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width
    
    // 如果高度超过一页，支持多页导出（简单切分，可能会切断文字，复杂场景建议使用服务端 PDF 生成）
    let position = 0
    const pageHeight = pdf.internal.pageSize.getHeight()
    
    pdf.addImage(imgData, 'JPEG', 0, position, pdfWidth, pdfHeight)
    
    let heightLeft = pdfHeight - pageHeight
    while (heightLeft >= 0) {
      position = heightLeft - pdfHeight
      pdf.addPage()
      pdf.addImage(imgData, 'JPEG', 0, position, pdfWidth, pdfHeight)
      heightLeft -= pageHeight
    }
    
    pdf.save(`MTM_Report_${report.value?.case_info?.case_number || 'export'}.pdf`)
    showSuccess('PDF 导出成功')
  } catch (error: any) {
    showError('导出 PDF 失败，请稍后重试')
    console.error('PDF Export error:', error)
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  void loadData()
})
</script>

<style>
@media print {
  body {
    background-color: white;
  }
  @page {
    margin: 1cm;
  }
}
</style>
