import re

with open("src/pages/MtmServiceCaseDetailPage.vue", "r") as f:
    content = f.read()

old_plan_ui = """          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <div class="flex items-center gap-2">
              <Stethoscope class="h-5 w-5 text-emerald-600" />
              <h2 class="text-lg font-semibold text-slate-900">干预计划</h2>
            </div>

            <template v-if="serviceCase.plan">
              <div class="mt-5 space-y-3">
                <div class="rounded-2xl bg-slate-50 p-4">
                  <p class="text-sm text-slate-500">优先级</p>
                  <p class="mt-2 text-base font-medium text-slate-900">
                    {{ planPriorityText(serviceCase.plan.priority) }}
                  </p>
                </div>
                <div class="rounded-2xl bg-slate-50 p-4">
                  <p class="text-sm text-slate-500">患者确认状态</p>
                  <p class="mt-2 text-base font-medium text-slate-900">
                    {{ planConfirmationText(serviceCase.plan.patient_confirmation_status) }}
                  </p>
                </div>
              </div>

              <div class="mt-5 rounded-2xl bg-slate-50 p-4">
                <p class="text-sm font-medium text-slate-900">计划措施</p>
                <ul v-if="planInterventionLines.length" class="mt-2 space-y-2 text-sm text-slate-600">
                  <li v-for="item in planInterventionLines" :key="item" class="flex items-start gap-2">
                    <span class="mt-1 h-2 w-2 rounded-full bg-emerald-500"></span>
                    <span>{{ item }}</span>
                  </li>
                </ul>
                <p v-else class="mt-2 text-sm text-slate-500">当前还没有记录具体干预措施。</p>
              </div>

              <p class="mt-5 rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
                {{ serviceCase.plan.patient_confirmation_notes || '当前还没有补充患者确认说明。' }}
              </p>
            </template>

            <div
              v-else
              class="mt-5 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-5 text-sm text-slate-500"
            >
              当前还没有干预计划摘要。
            </div>
          </article>"""

new_plan_ui = """          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div class="flex items-center gap-2">
                <Stethoscope class="h-5 w-5 text-emerald-600" />
                <h2 class="text-lg font-semibold text-slate-900">干预计划</h2>
              </div>
              <span
                class="inline-flex items-center self-start rounded-full px-3 py-1 text-xs font-medium"
                :class="planEntryMeta.badgeClass"
              >
                {{ planEntryMeta.badgeText }}
              </span>
            </div>

            <div class="mt-5 rounded-2xl border border-emerald-100 bg-emerald-50 p-4">
              <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p class="text-sm font-medium text-slate-900">干预计划入口</p>
                  <p class="mt-2 text-sm leading-6 text-slate-600">
                    {{ planEntryMeta.description }}
                  </p>
                </div>
                <button
                  type="button"
                  class="inline-flex items-center gap-2 self-start rounded-xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-emerald-300"
                  :disabled="loading || transitioning || planEntryMeta.disabled"
                  @click="goToPlanForm"
                >
                  <ArrowRight class="h-4 w-4" />
                  {{ planEntryMeta.buttonText }}
                </button>
              </div>
            </div>

            <template v-if="serviceCase.plan">
              <p
                v-if="serviceCase.plan.confirmed_at"
                class="mt-5 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
              >
                计划已于 {{ formatDateTime(serviceCase.plan.confirmed_at) }} 完成制定。
              </p>

              <div class="mt-5 space-y-3">
                <div class="rounded-2xl bg-slate-50 p-4">
                  <p class="text-sm text-slate-500">优先级</p>
                  <p class="mt-2 text-base font-medium text-slate-900">
                    {{ planPriorityText(serviceCase.plan.priority) }}
                  </p>
                </div>
                <div class="rounded-2xl bg-slate-50 p-4">
                  <p class="text-sm text-slate-500">患者确认状态</p>
                  <p class="mt-2 text-base font-medium text-slate-900">
                    {{ planConfirmationText(serviceCase.plan.patient_confirmation_status) }}
                  </p>
                </div>
              </div>

              <div class="mt-5 rounded-2xl bg-slate-50 p-4">
                <p class="text-sm font-medium text-slate-900">计划措施</p>
                <ul v-if="planInterventionLines.length" class="mt-2 space-y-2 text-sm text-slate-600">
                  <li v-for="item in planInterventionLines" :key="item" class="flex items-start gap-2">
                    <span class="mt-1 h-2 w-2 rounded-full bg-emerald-500"></span>
                    <span>{{ item }}</span>
                  </li>
                </ul>
                <p v-else class="mt-2 text-sm text-slate-500">当前还没有记录具体干预措施。</p>
              </div>

              <p class="mt-5 rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
                {{ serviceCase.plan.patient_confirmation_notes || '当前还没有补充患者确认说明。' }}
              </p>
            </template>
          </article>"""

if "干预计划入口" not in content:
    content = content.replace(old_plan_ui, new_plan_ui)
    with open("src/pages/MtmServiceCaseDetailPage.vue", "w") as f:
        f.write(content)
