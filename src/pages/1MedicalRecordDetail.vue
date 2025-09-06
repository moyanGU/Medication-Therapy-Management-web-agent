<template>
  <div class="medical-record-detail-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button
            @click="goBack"
            class="btn-secondary"
          >
            <ArrowLeft class="w-4 h-4 mr-2" />
            返回
          </button>
          <div>
            <h1 class="text-2xl font-bold text-gray-900">病历详情</h1>
            <p class="text-gray-600 mt-1">查看完整的病历信息</p>
          </div>
        </div>
        <div class="flex items-center space-x-3">
          <router-link
            :to="`/medical-records/${recordId}/edit`"
            class="btn-secondary"
          >
            <Edit class="w-4 h-4 mr-2" />
            编辑
          </router-link>
          <button
            @click="exportToPDF"
            class="btn-primary"
          >
            <Download class="w-4 h-4 mr-2" />
            导出PDF
          </button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span class="ml-3 text-gray-600">加载中...</span>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <div class="text-center py-12">
        <AlertCircle class="mx-auto h-12 w-12 text-red-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">加载失败</h3>
        <p class="mt-1 text-sm text-gray-500">{{ error }}</p>
        <div class="mt-6">
          <button @click="fetchRecord" class="btn-primary">
            重试
          </button>
        </div>
      </div>
    </div>

    <!-- 病历内容 -->
    <div v-else-if="record" class="record-content">
      <!-- 基本信息卡片 -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <User class="w-5 h-5 mr-2" />
            基本信息
          </h2>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div class="info-item">
              <label class="info-label">患者姓名</label>
              <p class="info-value">{{ record.patient_name }}</p>
            </div>
            <div class="info-item">
              <label class="info-label">就诊日期</label>
              <p class="info-value">{{ formatDate(record.visit_date) }}</p>
            </div>
            <div class="info-item">
              <label class="info-label">医院</label>
              <p class="info-value">{{ record.hospital }}</p>
            </div>
            <div class="info-item">
              <label class="info-label">科室</label>
              <p class="info-value">{{ record.department }}</p>
            </div>
            <div class="info-item">
              <label class="info-label">医生</label>
              <p class="info-value">{{ record.doctor }}</p>
            </div>
            <div class="info-item">
              <label class="info-label">病历类型</label>
              <p class="info-value">
                <span :class="getTypeClass(record.record_type)">{{ getTypeLabel(record.record_type) }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 诊断信息 -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <Stethoscope class="w-5 h-5 mr-2" />
            诊断信息
          </h2>
        </div>
        <div class="card-body">
          <div class="space-y-4">
            <div class="info-item">
              <label class="info-label">主要症状</label>
              <p class="info-value whitespace-pre-wrap">{{ record.symptoms || '无' }}</p>
            </div>
            <div class="info-item">
              <label class="info-label">诊断结果</label>
              <p class="info-value whitespace-pre-wrap">{{ record.diagnosis || '无' }}</p>
            </div>
            <div class="info-item">
              <label class="info-label">治疗方案</label>
              <p class="info-value whitespace-pre-wrap">{{ record.treatment || '无' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 处方信息 -->
      <div v-if="record.prescription" class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <Pill class="w-5 h-5 mr-2" />
            处方信息
          </h2>
        </div>
        <div class="card-body">
          <div class="info-item">
            <p class="info-value whitespace-pre-wrap">{{ record.prescription }}</p>
          </div>
        </div>
      </div>

      <!-- 费用信息 -->
      <div v-if="record.cost" class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <DollarSign class="w-5 h-5 mr-2" />
            费用信息
          </h2>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="info-item">
              <label class="info-label">总费用</label>
              <p class="info-value text-lg font-semibold text-green-600">¥{{ record.cost }}</p>
            </div>
            <div v-if="record.insurance_coverage" class="info-item">
              <label class="info-label">医保报销</label>
              <p class="info-value">¥{{ record.insurance_coverage }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 附件信息 -->
      <div v-if="record.attachments && record.attachments.length > 0" class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <Paperclip class="w-5 h-5 mr-2" />
            附件文件
          </h2>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="attachment in record.attachments"
              :key="attachment.id"
              class="attachment-item"
            >
              <div class="flex items-center space-x-3">
                <div class="attachment-icon">
                  <FileText class="w-6 h-6" />
                </div>
                <div class="flex-1">
                  <p class="text-sm font-medium text-gray-900">{{ attachment.name }}</p>
                  <p class="text-xs text-gray-500">{{ formatFileSize(attachment.size) }}</p>
                </div>
                <button
                  @click="downloadAttachment(attachment)"
                  class="btn-sm btn-secondary"
                >
                  <Download class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 备注信息 -->
      <div v-if="record.notes" class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <FileText class="w-5 h-5 mr-2" />
            备注信息
          </h2>
        </div>
        <div class="card-body">
          <div class="info-item">
            <p class="info-value whitespace-pre-wrap">{{ record.notes }}</p>
          </div>
        </div>
      </div>

      <!-- 满意度评价 -->
      <div v-if="record.satisfaction_rating" class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <Star class="w-5 h-5 mr-2" />
            满意度评价
          </h2>
        </div>
        <div class="card-body">
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-1">
              <Star
                v-for="i in 5"
                :key="i"
                :class="[
                  'w-5 h-5',
                  i <= record.satisfaction_rating
                    ? 'text-yellow-400 fill-current'
                    : 'text-gray-300'
                ]"
              />
            </div>
            <span class="text-sm text-gray-600">
              {{ record.satisfaction_rating }}/5 分
            </span>
          </div>
          <div v-if="record.satisfaction_comment" class="mt-3">
            <label class="info-label">评价内容</label>
            <p class="info-value whitespace-pre-wrap">{{ record.satisfaction_comment }}</p>
          </div>
        </div>
      </div>

      <!-- 创建和更新时间 -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">
            <Clock class="w-5 h-5 mr-2" />
            记录信息
          </h2>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="info-item">
              <label class="info-label">创建时间</label>
              <p class="info-value">{{ formatDateTime(record.created_at) }}</p>
            </div>
            <div class="info-item">
              <label class="info-label">更新时间</label>
              <p class="info-value">{{ formatDateTime(record.updated_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import {
  ArrowLeft,
  Edit,
  Download,
  AlertCircle,
  User,
  Stethoscope,
  Pill,
  DollarSign,
  Paperclip,
  FileText,
  Star,
  Clock
} from 'lucide-vue-next'
import { http } from '@/utils/http'

// 接口类型定义
interface Attachment {
  id: number
  name: string
  file_url: string
  size: number
  file_type: string
}

interface MedicalRecord {
  id: number
  patient_name: string
  visit_date: string
  hospital: string
  department: string
  doctor: string
  record_type: string
  symptoms?: string
  diagnosis?: string
  treatment?: string
  prescription?: string
  cost?: number
  insurance_coverage?: number
  attachments?: Attachment[]
  notes?: string
  satisfaction_rating?: number
  satisfaction_comment?: string
  created_at: string
  updated_at: string
}

// 响应式数据
const router = useRouter()
const route = useRoute()
const { success: showSuccess, error: showError } = useToast()

const loading = ref(false)
const error = ref('')
const record = ref<MedicalRecord | null>(null)

// 计算属性
const recordId = computed(() => route.params.id as string)

// 方法
const fetchRecord = async () => {
  try {
    loading.value = true
    error.value = ''

    console.log('[MedicalRecordDetail] 开始获取病历详情', { id: recordId.value })
    const { data } = await http.get(`/api/medical-records/${recordId.value}/`)
    console.log('[MedicalRecordDetail] 响应', data)

    if (data?.success) {
      record.value = data.data
    } else {
      error.value = data?.message || '获取病历详情失败'
    }
  } catch (err) {
    console.error('获取病历详情失败:', err)
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const exportToPDF = async () => {
  try {
    console.log('[MedicalRecordDetail] 请求导出PDF', { id: recordId.value })
    const response = await http.post(`/api/medical-records/${recordId.value}/export/`, undefined, { responseType: 'blob' })

    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `病历_${record.value?.patient_name}_${record.value?.visit_date}.pdf`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    showSuccess('PDF导出成功')
  } catch (error) {
    console.error('PDF导出失败:', error)
    showError('PDF导出失败')
  }
}

const downloadAttachment = async (attachment: Attachment) => {
  try {
    const response = await fetch(attachment.file_url)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = attachment.name
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    console.error('下载附件失败:', error)
    showError('下载附件失败')
  }
}

// 格式化函数
const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatDateTime = (datetime: string) => {
  return new Date(datetime).toLocaleString('zh-CN')
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    outpatient: '门诊',
    inpatient: '住院',
    emergency: '急诊',
    physical_exam: '体检',
    follow_up: '复诊'
  }
  return labels[type] || type
}

const getTypeClass = (type: string) => {
  const classes: Record<string, string> = {
    outpatient: 'bg-blue-100 text-blue-800',
    inpatient: 'bg-red-100 text-red-800',
    emergency: 'bg-orange-100 text-orange-800',
    physical_exam: 'bg-green-100 text-green-800',
    follow_up: 'bg-purple-100 text-purple-800'
  }
  return `px-2 py-1 text-xs font-medium rounded-full ${classes[type] || 'bg-gray-100 text-gray-800'}`
}

// 生命周期
onMounted(() => {
  fetchRecord()
})
</script>

<style scoped>
.medical-record-detail-page {
  @apply p-6 max-w-6xl mx-auto;
}

.page-header {
  @apply mb-6;
}

.loading-state,
.error-state {
  @apply bg-white rounded-lg shadow;
}

.record-content {
  @apply space-y-6;
}

.info-card {
  @apply bg-white rounded-lg shadow overflow-hidden;
}

.card-header {
  @apply px-6 py-4 bg-gray-50 border-b border-gray-200;
}

.card-title {
  @apply text-lg font-semibold text-gray-900 flex items-center;
}

.card-body {
  @apply p-6;
}

.info-item {
  @apply space-y-1;
}

.info-label {
  @apply text-sm font-medium text-gray-500;
}

.info-value {
  @apply text-sm text-gray-900;
}

.attachment-item {
  @apply p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors;
}

.attachment-icon {
  @apply w-10 h-10 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center;
}

.btn-primary {
  @apply bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center;
}

.btn-secondary {
  @apply bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors flex items-center;
}

.btn-sm {
  @apply px-3 py-1 text-sm;
}
</style>