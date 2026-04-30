<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-0">
    <div class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity" @click="close"></div>
    <div class="relative w-full max-w-lg transform overflow-hidden rounded-3xl bg-white p-6 text-left shadow-xl transition-all sm:p-8">
      <div class="mb-6 flex items-center justify-between">
        <h3 class="text-xl font-bold text-slate-900">新增随访记录</h3>
        <button
          type="button"
          class="rounded-full p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          @click="close"
        >
          <X class="h-5 w-5" />
        </button>
      </div>

      <form @submit.prevent="submit" class="space-y-5">
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">随访方式</label>
            <select
              v-model="form.follow_up_method"
              class="block w-full rounded-xl border-slate-300 bg-slate-50 py-2.5 text-slate-900 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              required
            >
              <option value="phone">电话 (Phone)</option>
              <option value="in_person">面谈 (In Person)</option>
              <option value="video">视频 (Video)</option>
              <option value="wechat">微信 (WeChat)</option>
              <option value="other">其他 (Other)</option>
            </select>
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">执行状态</label>
            <select
              v-model="form.execution_status"
              class="block w-full rounded-xl border-slate-300 bg-slate-50 py-2.5 text-slate-900 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              required
            >
              <option value="completed">已完成 (Completed)</option>
              <option value="pending">待执行 (Pending)</option>
              <option value="missed">未完成 (Missed)</option>
              <option value="cancelled">已取消 (Cancelled)</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">随访时间</label>
            <input
              type="datetime-local"
              v-model="form.follow_up_time"
              class="block w-full rounded-xl border-slate-300 bg-slate-50 py-2.5 text-slate-900 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              required
            />
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">风险变化评估</label>
            <select
              v-model="form.risk_change"
              class="block w-full rounded-xl border-slate-300 bg-slate-50 py-2.5 text-slate-900 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              required
            >
              <option value="improved">改善 (Improved)</option>
              <option value="stable">稳定 (Stable)</option>
              <option value="worsened">恶化 (Worsened)</option>
              <option value="unknown">未知 (Unknown)</option>
            </select>
          </div>
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-slate-700">随访总结</label>
          <textarea
            v-model="form.summary"
            rows="3"
            class="block w-full rounded-xl border-slate-300 bg-slate-50 py-3 text-slate-900 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="简要记录本次随访的核心情况、患者主诉或依从性变化..."
          ></textarea>
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-slate-700">下次随访时间 (可选)</label>
          <input
            type="datetime-local"
            v-model="form.next_follow_up_time"
            class="block w-full rounded-xl border-slate-300 bg-slate-50 py-2.5 text-slate-900 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>

        <div class="mt-8 flex flex-col-reverse justify-end gap-3 sm:flex-row border-t border-slate-100 pt-6">
          <button
            type="button"
            class="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-6 py-2.5 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-300 transition hover:bg-slate-50"
            @click="close"
            :disabled="submitting"
          >
            取消
          </button>
          <button
            type="submit"
            class="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-700 disabled:opacity-50"
            :disabled="submitting"
          >
            <span v-if="submitting" class="h-4 w-4 animate-spin rounded-full border-b-2 border-white"></span>
            保存记录
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { X } from 'lucide-vue-next'
import { mtmApi } from '@/api/mtm'
import { useToast } from '@/composables/useToast'

const props = defineProps<{
  modelValue: boolean
  serviceCaseId: number | string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}>()

const { success: showSuccess, error: showError } = useToast()
const submitting = ref(false)

const form = reactive({
  follow_up_time: '',
  follow_up_method: 'phone',
  execution_status: 'completed',
  risk_change: 'stable',
  summary: '',
  next_follow_up_time: '',
})

watch(() => props.modelValue, (val) => {
  if (val) {
    const now = new Date()
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
    form.follow_up_time = now.toISOString().slice(0, 16)
    form.follow_up_method = 'phone'
    form.execution_status = 'completed'
    form.risk_change = 'stable'
    form.summary = ''
    form.next_follow_up_time = ''
  }
})

const close = () => {
  if (submitting.value) return
  emit('update:modelValue', false)
}

const submit = async () => {
  try {
    submitting.value = true
    const payload = {
      follow_up_time: new Date(form.follow_up_time).toISOString(),
      follow_up_method: form.follow_up_method,
      execution_status: form.execution_status,
      risk_change: form.risk_change,
      summary: form.summary || null,
      next_follow_up_time: form.next_follow_up_time ? new Date(form.next_follow_up_time).toISOString() : null,
    }
    await mtmApi.addFollowUp(props.serviceCaseId, payload)
    showSuccess('随访记录已保存')
    emit('success')
    close()
  } catch (error: any) {
    showError(error.message || '保存失败')
  } finally {
    submitting.value = false
  }
}
</script>
