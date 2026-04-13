<template>
  <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto">
    <div
      class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0"
    >
      <!-- 背景遮罩 -->
      <div
        class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
        @click="$emit('close')"
      ></div>

      <!-- 对话框 -->
      <div
        class="inline-block w-full max-w-4xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg"
      >
        <!-- 标题栏 -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-semibold text-gray-900">药品详情</h3>
          <div class="flex items-center space-x-2">
            <button
              @click="$emit('edit', medicine)"
              class="px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
            >
              <Edit class="w-4 h-4 mr-1" />
              编辑
            </button>
            <button
              @click="$emit('close')"
              class="text-gray-400 hover:text-gray-600"
            >
              <X class="w-6 h-6" />
            </button>
          </div>
        </div>

        <div v-if="medicine" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- 左侧：药品图片和基本信息 -->
          <div class="lg:col-span-1">
            <!-- 药品图片 -->
            <div class="mb-6">
              <div class="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                <img
                  v-if="medicine.image_path"
                  :src="getImageUrl(medicine.image_path)"
                  :alt="medicine.name"
                  class="w-full h-full object-cover"
                  @error="handleImageError"
                />
                <div
                  v-else
                  class="w-full h-full flex items-center justify-center"
                >
                  <Package class="w-16 h-16 text-gray-400" />
                </div>
              </div>
            </div>

            <!-- 状态标签 -->
            <div class="space-y-3">
              <div class="flex flex-wrap gap-2">
                <span
                  v-if="medicine.is_prescription"
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800"
                >
                  <Shield class="w-4 h-4 mr-1" />
                  处方药
                </span>
                <span
                  v-else
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800"
                >
                  <CheckCircle class="w-4 h-4 mr-1" />
                  非处方药
                </span>
              </div>

              <div class="flex flex-wrap gap-2">
                <span
                  v-if="medicine.is_expired"
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800"
                >
                  <AlertTriangle class="w-4 h-4 mr-1" />
                  已过期
                </span>
                <span
                  v-else-if="
                    medicine.days_until_expiry !== undefined &&
                    medicine.days_until_expiry <= 30
                  "
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800"
                >
                  <Clock class="w-4 h-4 mr-1" />
                  {{ medicine.days_until_expiry }}天后过期
                </span>
                <span
                  v-if="medicine.is_low_stock"
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800"
                >
                  <TrendingDown class="w-4 h-4 mr-1" />
                  库存不足
                </span>
              </div>
            </div>
          </div>

          <!-- 右侧：详细信息 -->
          <div class="lg:col-span-2">
            <!-- 药品名称和规格 -->
            <div class="mb-6">
              <h2 class="text-2xl font-bold text-gray-900 mb-2">
                {{ medicine.name }}
              </h2>
              <p v-if="medicine.specification" class="text-lg text-gray-600">
                {{ medicine.specification }}
              </p>
            </div>

            <!-- 详细信息表格 -->
            <div class="bg-gray-50 rounded-lg p-6 mb-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">基本信息</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="info-item">
                  <span class="info-label">生产厂商</span>
                  <span class="info-value">{{
                    medicine.manufacturer || '未设置'
                  }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">药品类型</span>
                  <span class="info-value">{{
                    getMedicineTypeLabel(medicine.medicine_type)
                  }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">当前库存</span>
                  <span class="info-value">{{ medicine.quantity }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">批号</span>
                  <span class="info-value">{{
                    medicine.batch_number || '未设置'
                  }}</span>
                </div>
              </div>
            </div>

            <!-- 日期信息 -->
            <div class="bg-gray-50 rounded-lg p-6 mb-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">日期信息</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="info-item">
                  <span class="info-label">采购日期</span>
                  <span class="info-value">{{
                    formatDate(medicine.purchase_date) || '未设置'
                  }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">有效期</span>
                  <span
                    class="info-value"
                    :class="{
                      'text-red-600': medicine.is_expired,
                      'text-yellow-600':
                        medicine.days_until_expiry !== undefined &&
                        medicine.days_until_expiry <= 30,
                    }"
                  >
                    {{ formatDate(medicine.expiry_date) || '未设置' }}
                  </span>
                </div>
                <div class="info-item">
                  <span class="info-label">添加时间</span>
                  <span class="info-value">{{
                    formatDateTime(medicine.created_at)
                  }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">更新时间</span>
                  <span class="info-value">{{
                    formatDateTime(medicine.updated_at)
                  }}</span>
                </div>
              </div>
            </div>

            <!-- 价格信息 -->
            <div
              v-if="medicine.purchase_price"
              class="bg-gray-50 rounded-lg p-6 mb-6"
            >
              <h3 class="text-lg font-semibold text-gray-900 mb-4">价格信息</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="info-item">
                  <span class="info-label">采购价格</span>
                  <span class="info-value"
                    >¥{{ medicine.purchase_price.toFixed(2) }}</span
                  >
                </div>
                <div class="info-item">
                  <span class="info-label">总价值</span>
                  <span class="info-value"
                    >¥{{
                      (medicine.purchase_price * medicine.quantity).toFixed(2)
                    }}</span
                  >
                </div>
              </div>
            </div>

            <!-- 存储条件 -->
            <div
              v-if="medicine.storage_conditions"
              class="bg-gray-50 rounded-lg p-6 mb-6"
            >
              <h3 class="text-lg font-semibold text-gray-900 mb-4">存储条件</h3>
              <p class="text-gray-700">{{ medicine.storage_conditions }}</p>
            </div>

            <!-- 药品描述 -->
            <div v-if="medicine.description" class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">药品描述</h3>
              <p class="text-gray-700 whitespace-pre-wrap">
                {{ medicine.description }}
              </p>
            </div>

            <div class="bg-gray-50 rounded-lg p-6 mt-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">用药咨询</h3>
              <div class="space-y-3">
                <textarea
                  v-model="aiQuestion"
                  rows="4"
                  placeholder="请输入与药物/用药相关的问题（如用法用量、不良反应、相互作用、禁忌、漏服处理等）"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
                <div class="flex items-center justify-end">
                  <button
                    @click="askMedicationGuidance"
                    :disabled="aiLoading || !canAsk"
                    class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                  >
                    {{ aiLoading ? '生成中...' : '咨询' }}
                  </button>
                </div>

                <div v-if="aiError" class="text-sm text-red-600">
                  {{ aiError }}
                </div>

                <div
                  v-if="aiAnswered"
                  class="border border-gray-200 rounded-lg bg-white p-4"
                >
                  <div v-if="aiBlocked" class="text-sm text-amber-700 mb-2">
                    {{ aiReason || '当前问题已被拦截，请改为具体的用药问题。' }}
                  </div>
                  <div class="whitespace-pre-wrap text-sm text-gray-800">
                    {{ aiAnswer }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div
          class="flex justify-end space-x-4 pt-6 border-t border-gray-200 mt-8"
        >
          <button
            @click="$emit('close')"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            关闭
          </button>
          <button
            @click="$emit('edit', medicine)"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            <Edit class="w-4 h-4 mr-2" />
            编辑药品
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  X,
  Edit,
  Package,
  Shield,
  CheckCircle,
  AlertTriangle,
  Clock,
  TrendingDown,
} from 'lucide-vue-next'
import type { Medicine } from '@/types/medicine'
import { api } from '@/utils/api'

// Props
interface Props {
  visible: boolean
  medicine?: Medicine | null
}

const props = withDefaults(defineProps<Props>(), {
  medicine: null,
})

// Emits
defineEmits<{
  close: []
  edit: [medicine: Medicine]
}>()

// 获取药品类型标签
const getMedicineTypeLabel = (type: string): string => {
  const typeMap: Record<string, string> = {
    tablet: '片剂',
    capsule: '胶囊',
    liquid: '液体',
    injection: '注射剂',
    ointment: '软膏',
    drops: '滴剂',
    other: '其他',
  }
  return typeMap[type] || type
}

// 格式化日期
const formatDate = (dateString?: string): string => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 格式化日期时间
const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString('zh-CN')
}

/**
 * 根据后端返回的 image_path 构建完整图片 URL
 * 若 image_path 为 http/https 开头的绝对地址则直接返回；
 * 否则拼接后端基地址 + /media + 相对路径。
 */
import { resolveMediaUrl } from '@/utils/api'
const getImageUrl = (imagePath?: string | null) => {
  return resolveMediaUrl(imagePath)
}

const aiQuestion = ref('')
const aiLoading = ref(false)
const aiAnswer = ref('')
const aiBlocked = ref(false)
const aiReason = ref('')
const aiError = ref<string | null>(null)
const aiAnswered = ref(false)

const canAsk = computed(() => !!aiQuestion.value.trim())

/**
 * 触发“用药咨询”请求：调用后端 /api/ai/medication-guidance/ 生成用药指导。
 * - 成功：展示 answer；如被拦截则展示 reason
 * - 失败：展示后端 message，并对 AI 配置类错误做更明确提示
 */
const askMedicationGuidance = async () => {
  const question = aiQuestion.value.trim()
  if (!question) return

  aiLoading.value = true
  aiError.value = null
  aiAnswered.value = false
  aiAnswer.value = ''
  aiBlocked.value = false
  aiReason.value = ''

  try {
    console.log('🔵 [AI] medication-guidance 请求', {
      medicine_id: props.medicine?.id,
      questionLength: question.length,
    })

    const resp = await api.post<{
      blocked: boolean
      answer: string
      reason?: string
    }>('/ai/medication-guidance/', {
      question,
      medicine_id: props.medicine?.id,
    })

    console.log('🟢 [AI] medication-guidance 响应', resp)

    if (!resp.success) {
      aiError.value = resp.message || '用药咨询失败'
      return
    }

    const payload = ((resp as any)?.data as any)?.data ?? (resp.data as any)
    aiAnswered.value = true
    aiBlocked.value = !!payload?.blocked
    aiReason.value = String(payload?.reason || '')
    aiAnswer.value = String(payload?.answer || '')
  } catch (e: any) {
    console.error('🔴 [AI] medication-guidance 异常', e)
    if (e?.code === 401) {
      aiError.value = '登录已过期或未登录，请重新登录后再试'
      return
    }

    const errorCode = (e as any)?.details?.error_code
    if (errorCode === 'AI_CONFIG_MISSING') {
      aiError.value =
        'AI 服务配置缺失：请在后端 .env 配置 BAICHUAN_M3_* 并重启后端'
      return
    }
    if (errorCode === 'AI_DISABLED') {
      aiError.value = 'AI 服务未启用：请开启 BAICHUAN_M3_ENABLED'
      return
    }

    aiError.value = e?.message || '用药咨询失败'
  } finally {
    aiLoading.value = false
  }
}

// 已有的错误处理函数将作为图片失败时的兜底
// function handleImageError ... 已存在，无需重复定义

// 处理图片加载错误
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}
</script>

<style scoped>
.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.875rem;
  line-height: 1.25rem;
  font-weight: 500;
  color: rgb(107 114 128);
}

.info-value {
  font-size: 0.875rem;
  line-height: 1.25rem;
  color: rgb(17 24 39);
  font-weight: 500;
}

/* 自定义滚动条 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .lg\:col-span-1,
  .lg\:col-span-2 {
    grid-column: span 1;
  }
}
</style>
