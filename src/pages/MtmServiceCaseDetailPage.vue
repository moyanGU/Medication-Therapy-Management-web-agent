<template>
  <div class="min-h-screen bg-slate-50">
    <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <section class="mb-6 rounded-3xl border border-violet-100 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div class="flex items-start gap-3">
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
              @click="goBack"
            >
              <ArrowLeft class="h-4 w-4" />
              返回
            </button>
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <span class="inline-flex items-center rounded-full bg-violet-100 px-3 py-1 text-xs font-medium text-violet-700">
                  MTM 专业服务
                </span>
                <span
                  v-if="serviceCase"
                  class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium"
                  :class="getMtmStatusBadgeClass(serviceCase.status)"
                >
                  {{ getMtmStatusText(serviceCase.status) }}
                </span>
              </div>
              <h1 class="mt-3 text-2xl font-bold text-slate-900">
                {{ serviceCase?.case_number || '专业服务详情' }}
              </h1>
              <p class="mt-2 max-w-2xl text-sm text-slate-600">
                {{ pageDescription }}
              </p>
            </div>
          </div>

          <div class="flex flex-wrap items-center gap-3 self-start">
            <button
              v-if="serviceCase?.status === 'completed' || serviceCase?.status === 'intervening' || serviceCase?.status === 'following_up'"
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-medium text-amber-700 shadow-sm ring-1 ring-inset ring-amber-200 transition hover:bg-amber-50"
              @click="goToSoapNotes"
            >
              <Sparkles class="h-4 w-4" />
              撰写/查看 SOAP 药历
            </button>
            <button
              v-if="serviceCase?.status === 'completed'"
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-medium text-violet-700 shadow-sm ring-1 ring-inset ring-violet-200 transition hover:bg-violet-50"
              @click="goToReport"
            >
              <FileText class="h-4 w-4" />
              查看专业报告 (PMR/MAP)
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-700"
              :disabled="loading || transitioning"
              @click="fetchServiceCaseDetail"
            >
              <RefreshCw class="h-4 w-4" :class="loading ? 'animate-spin' : ''" />
              刷新详情
            </button>
          </div>
        </div>
      </section>

      <section v-if="loading && !serviceCase" class="space-y-6">
        <div class="h-48 animate-pulse rounded-3xl bg-white shadow-sm"></div>
        <div class="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div class="h-80 animate-pulse rounded-3xl bg-white shadow-sm"></div>
          <div class="h-80 animate-pulse rounded-3xl bg-white shadow-sm"></div>
          <div class="h-80 animate-pulse rounded-3xl bg-white shadow-sm"></div>
        </div>
      </section>

      <section
        v-else-if="loadError && !serviceCase"
        class="rounded-3xl border border-red-100 bg-white p-8 text-center shadow-sm"
      >
        <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-50">
          <AlertTriangle class="h-6 w-6 text-red-500" />
        </div>
        <h2 class="text-lg font-semibold text-slate-900">详情暂时没加载成功</h2>
        <p class="mt-2 text-sm text-slate-600">{{ loadError }}</p>
        <button
          type="button"
          class="mt-4 inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-violet-700"
          @click="fetchServiceCaseDetail"
        >
          <RefreshCw class="h-4 w-4" />
          重新加载
        </button>
      </section>

      <template v-else-if="serviceCase">
        <section class="mb-6 grid grid-cols-1 gap-6 xl:grid-cols-3">
          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm xl:col-span-2">
            <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <span
                    class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium"
                    :class="getMtmStatusBadgeClass(serviceCase.status)"
                  >
                    {{ getMtmStatusText(serviceCase.status) }}
                  </span>
                  <span class="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                    {{ getMtmTriggerText(serviceCase.trigger_source) }}
                  </span>
                </div>
                <h2 class="mt-4 text-lg font-semibold text-slate-900">本次服务概览</h2>
                <p class="mt-2 text-sm text-slate-600">
                  {{ serviceCase.service_goal || '当前还没有填写明确的服务目标。' }}
                </p>
              </div>
              <div class="rounded-2xl bg-violet-50 px-4 py-3 text-sm text-violet-700">
                {{ progressDescription }}
              </div>
            </div>

            <div class="mt-5 rounded-2xl border border-violet-100 bg-violet-50/70 p-4">
              <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <h3 class="text-sm font-medium text-slate-900">当前可执行动作</h3>
                  <p class="mt-1 text-sm text-slate-600">
                    {{ transitionHintText }}
                  </p>
                </div>
                <span
                  v-if="transitioning"
                  class="inline-flex items-center rounded-full bg-white px-3 py-1 text-xs font-medium text-violet-700"
                >
                  正在更新状态...
                </span>
              </div>

              <div v-if="visibleTransitionActions.length" class="mt-4 flex flex-wrap gap-3">
                <button
                  v-for="action in visibleTransitionActions"
                  :key="action.targetStatus"
                  type="button"
                  class="rounded-xl px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-60"
                  :class="
                    action.variant === 'secondary'
                      ? 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                      : 'bg-violet-600 text-white hover:bg-violet-700'
                  "
                  :disabled="transitioning"
                  @click="handleTransition(action.targetStatus)"
                >
                  {{ transitioning ? '正在提交...' : action.label }}
                </button>
              </div>

              <ul v-if="visibleTransitionActions.length" class="mt-4 space-y-2 text-sm text-slate-600">
                <li
                  v-for="action in visibleTransitionActions"
                  :key="`hint-${action.targetStatus}`"
                  class="flex items-start gap-2"
                >
                  <span class="mt-1 h-2 w-2 rounded-full bg-violet-500"></span>
                  <span>{{ action.description }}</span>
                </li>
              </ul>

              <p
                v-else
                class="mt-4 rounded-2xl border border-dashed border-slate-200 bg-white px-4 py-3 text-sm text-slate-500"
              >
                当前阶段已经没有可继续推进的动作。
              </p>
            </div>

            <div class="mt-5 grid grid-cols-1 gap-4 md:grid-cols-3">
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-sm text-slate-500">创建时间</p>
                <p class="mt-2 text-base font-medium text-slate-900">
                  {{ formatDateTime(serviceCase.created_at) }}
                </p>
              </div>
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-sm text-slate-500">启动时间</p>
                <p class="mt-2 text-base font-medium text-slate-900">
                  {{ formatDateTime(serviceCase.started_at) }}
                </p>
              </div>
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-sm text-slate-500">完成时间</p>
                <p class="mt-2 text-base font-medium text-slate-900">
                  {{ formatDateTime(serviceCase.completed_at) }}
                </p>
              </div>
            </div>

            <div class="mt-5 rounded-2xl border border-slate-100 bg-slate-50 p-4">
              <h3 class="text-sm font-medium text-slate-900">备注说明</h3>
              <p class="mt-2 whitespace-pre-line text-sm leading-6 text-slate-600">
                {{ serviceCase.notes || '当前还没有补充备注。' }}
              </p>
            </div>
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <div class="flex items-center gap-2">
              <User class="h-5 w-5 text-sky-600" />
              <h2 class="text-lg font-semibold text-slate-900">参与者信息</h2>
            </div>

            <div class="mt-5 space-y-4">
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-sm text-slate-500">患者</p>
                <p class="mt-2 text-base font-medium text-slate-900">
                  {{ serviceCase.patient.username }}
                </p>
                <p class="mt-1 text-sm text-slate-500">
                  {{ serviceCase.patient.phone || '未记录手机号' }}
                </p>
              </div>

              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-sm text-slate-500">主责药师</p>
                <p class="mt-2 text-base font-medium text-slate-900">
                  {{ serviceCase.assigned_pharmacist?.username || '暂未分配' }}
                </p>
                <p class="mt-1 text-sm text-slate-500">
                  {{ serviceCase.assigned_pharmacist?.phone || '当前还没有药师联系方式' }}
                </p>
              </div>
            </div>
          </article>
        </section>

        <section class="mb-6 grid grid-cols-1 gap-6 xl:grid-cols-3">
          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div class="flex items-center gap-2">
                <ClipboardList class="h-5 w-5 text-sky-600" />
                <h2 class="text-lg font-semibold text-slate-900">问诊摘要</h2>
              </div>
              <span
                class="inline-flex items-center self-start rounded-full px-3 py-1 text-xs font-medium"
                :class="interviewEntryMeta.badgeClass"
              >
                {{ interviewEntryMeta.badgeText }}
              </span>
            </div>

            <div class="mt-5 rounded-2xl border border-sky-100 bg-sky-50 p-4">
              <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p class="text-sm font-medium text-slate-900">问诊填写入口</p>
                  <p class="mt-2 text-sm leading-6 text-slate-600">
                    {{ interviewEntryMeta.description }}
                  </p>
                  <p class="mt-2 text-xs leading-5 text-slate-500">
                    问诊完成后只会记录完成时间，不会自动推进当前服务状态。
                  </p>
                </div>
                <button
                  type="button"
                  class="inline-flex items-center gap-2 self-start rounded-xl bg-sky-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-sky-300"
                  :disabled="loading || transitioning"
                  @click="goToInterviewForm"
                >
                  <ArrowRight class="h-4 w-4" />
                  {{ interviewEntryMeta.buttonText }}
                </button>
              </div>
            </div>

            <template v-if="serviceCase.interview">
              <p
                v-if="serviceCase.interview.completed_at"
                class="mt-5 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
              >
                问诊已于 {{ formatDateTime(serviceCase.interview.completed_at) }} 标记完成。
              </p>
              <div v-if="interviewBasicInfoLines.length" class="mt-5 space-y-3">
                <div
                  v-for="item in interviewBasicInfoLines"
                  :key="item.label"
                  class="flex items-center justify-between gap-4 rounded-2xl bg-slate-50 px-4 py-3"
                >
                  <span class="text-sm text-slate-500">{{ item.label }}</span>
                  <span class="text-sm font-medium text-slate-900">{{ item.value }}</span>
                </div>
              </div>
              <p v-else class="mt-5 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-500">
                当前还没有结构化的基础问诊信息。
              </p>

              <div class="mt-5 space-y-3">
                <div class="rounded-2xl bg-slate-50 p-4">
                  <p class="text-sm font-medium text-slate-900">当前用药信息</p>
                  <ul v-if="interviewMedicationLines.length" class="mt-2 space-y-2 text-sm text-slate-600">
                    <li v-for="item in interviewMedicationLines" :key="item" class="flex items-start gap-2">
                      <span class="mt-1 h-2 w-2 rounded-full bg-sky-500"></span>
                      <span>{{ item }}</span>
                    </li>
                  </ul>
                  <p v-else class="mt-2 text-sm text-slate-500">暂未记录当前用药细节。</p>
                </div>

                <div class="rounded-2xl bg-slate-50 p-4">
                  <p class="text-sm font-medium text-slate-900">生活方式与补充说明</p>
                  <ul v-if="interviewLifestyleLines.length" class="mt-2 space-y-2 text-sm text-slate-600">
                    <li v-for="item in interviewLifestyleLines" :key="item" class="flex items-start gap-2">
                      <span class="mt-1 h-2 w-2 rounded-full bg-violet-500"></span>
                      <span>{{ item }}</span>
                    </li>
                  </ul>
                  <p v-else class="mt-2 text-sm text-slate-500">暂未记录生活方式信息。</p>
                  <p class="mt-3 text-sm text-slate-600">
                    {{ serviceCase.interview.notes || serviceCase.interview.health_expectations || '当前没有额外补充说明。' }}
                  </p>
                </div>
              </div>
            </template>

            <div
              v-else
              class="mt-5 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-5 text-sm text-slate-500"
            >
              当前还没有问诊摘要。
            </div>
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div class="flex items-center gap-2">
                <HeartPulse class="h-5 w-5 text-rose-600" />
                <h2 class="text-lg font-semibold text-slate-900">评估摘要</h2>
              </div>
              <span
                class="inline-flex items-center self-start rounded-full px-3 py-1 text-xs font-medium"
                :class="assessmentEntryMeta.badgeClass"
              >
                {{ assessmentEntryMeta.badgeText }}
              </span>
            </div>

            <div class="mt-5 rounded-2xl border border-rose-100 bg-rose-50 p-4">
              <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p class="text-sm font-medium text-slate-900">评估填写入口</p>
                  <p class="mt-2 text-sm leading-6 text-slate-600">
                    {{ assessmentEntryMeta.description }}
                  </p>
                  <p class="mt-2 text-xs leading-5 text-slate-500">
                    评估完成后只会记录完成时间，不会自动推进当前服务状态。
                  </p>
                </div>
                <button
                  type="button"
                  class="inline-flex items-center gap-2 self-start rounded-xl bg-rose-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-rose-700 disabled:cursor-not-allowed disabled:bg-rose-300"
                  :disabled="loading || transitioning || assessmentEntryMeta.disabled"
                  @click="goToAssessmentForm"
                >
                  <ArrowRight class="h-4 w-4" />
                  {{ assessmentEntryMeta.buttonText }}
                </button>
              </div>
            </div>

            <template v-if="serviceCase.assessment">
              <p
                v-if="serviceCase.assessment.completed_at"
                class="mt-5 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
              >
                评估已于 {{ formatDateTime(serviceCase.assessment.completed_at) }} 标记完成。
              </p>
              <div class="mt-5 flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                <div>
                  <p class="text-sm text-slate-500">综合风险等级</p>
                  <p class="mt-1 text-base font-medium text-slate-900">
                    {{ assessmentRiskText(serviceCase.assessment.risk_level) }}
                  </p>
                </div>
                <span
                  class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium"
                  :class="assessmentRiskClass(serviceCase.assessment.risk_level)"
                >
                  {{ assessmentRiskText(serviceCase.assessment.risk_level) }}
                </span>
              </div>

              <div class="mt-5 space-y-3">
                <div
                  v-for="item in assessmentScoreCards"
                  :key="item.label"
                  class="rounded-2xl bg-slate-50 p-4"
                >
                  <div class="flex items-center justify-between gap-4">
                    <span class="text-sm text-slate-500">{{ item.label }}</span>
                    <span class="text-sm font-medium text-slate-900">{{ item.value }}</span>
                  </div>
                </div>
              </div>

              <div class="mt-5 rounded-2xl bg-slate-50 p-4">
                <p class="text-sm font-medium text-slate-900">问题清单</p>
                <ul v-if="assessmentProblemLines.length" class="mt-2 space-y-2 text-sm text-slate-600">
                  <li v-for="item in assessmentProblemLines" :key="item" class="flex items-start gap-2">
                    <span class="mt-1 h-2 w-2 rounded-full bg-rose-500"></span>
                    <span>{{ item }}</span>
                  </li>
                </ul>
                <p v-else class="mt-2 text-sm text-slate-500">当前还没有结构化问题清单。</p>
              </div>

              <p class="mt-5 rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
                {{ serviceCase.assessment.summary || '当前还没有补充评估总结。' }}
              </p>
            </template>

            <div
              v-else
              class="mt-5 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-5 text-sm text-slate-500"
            >
              当前还没有评估摘要。
            </div>
          </article>

          <article class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
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
          </article>
        </section>

        <section class="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div class="flex items-center gap-2">
              <CalendarClock class="h-5 w-5 text-indigo-600" />
              <h2 class="text-lg font-semibold text-slate-900">随访记录</h2>
            </div>
            <button
              type="button"
              class="inline-flex items-center gap-2 self-start rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-indigo-300"
              :disabled="loading || transitioning"
              @click="showFollowUpModal = true"
            >
              <span class="h-4 w-4 flex items-center justify-center font-bold text-lg leading-none">+</span>
              新增随访记录
            </button>
          </div>

          <div v-if="followUpCards.length" class="mt-5 grid grid-cols-1 gap-4 xl:grid-cols-2">
            <article
              v-for="item in followUpCards"
              :key="item.id"
              class="rounded-2xl border border-slate-100 bg-slate-50 p-4"
            >
              <div class="flex flex-wrap items-center gap-2">
                <span class="inline-flex items-center rounded-full bg-indigo-100 px-3 py-1 text-xs font-medium text-indigo-700">
                  {{ followUpStatusText(item.execution_status) }}
                </span>
                <span class="inline-flex items-center rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700">
                  {{ followUpMethodText(item.follow_up_method) }}
                </span>
              </div>
              <p class="mt-3 text-sm font-medium text-slate-900">
                随访时间：{{ formatDateTime(item.follow_up_time) }}
              </p>
              <p class="mt-2 text-sm text-slate-600">
                风险变化：{{ followUpRiskText(item.risk_change) }}
              </p>
              <p class="mt-2 text-sm leading-6 text-slate-600">
                {{ item.summary || '当前还没有填写随访总结。' }}
              </p>
              <p class="mt-2 text-xs text-slate-500">
                下次随访：{{ formatDateTime(item.next_follow_up_time) }}
              </p>
            </article>
          </div>

          <div
            v-else
            class="mt-5 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-5 text-sm text-slate-500"
          >
            当前还没有随访记录，后续有新的跟进安排时会展示在这里。
          </div>
        </section>
      </template>

    </main>
    <MtmFollowUpModal
      v-model="showFollowUpModal"
      :service-case-id="serviceCaseId"
      @success="fetchServiceCaseDetail"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter, type LocationQueryRaw } from 'vue-router'
import {
  AlertTriangle,
  ArrowRight,
  ArrowLeft,
  CalendarClock,
  ClipboardList,
  FileText,
  HeartPulse,
  RefreshCw,
  Sparkles,
  Stethoscope,
  User,
} from 'lucide-vue-next'
import { mtmApi } from '@/api/mtm'
import { useToast } from '@/composables/useToast'
import MtmFollowUpModal from '@/components/mtm/MtmFollowUpModal.vue'
import type {
  MtmFollowUpSummary,
  MtmServiceCase,
  MtmServiceCaseOrdering,
  MtmListPresetSource,
  MtmServiceStatus,
} from '@/types/mtm'
import { isRequestCancelledError } from '@/utils/api'
import {
  buildMtmTransitionNote,
  getMtmStatusBadgeClass,
  getMtmStatusText,
  getMtmTransitionActions,
  getMtmTriggerText,
  isValidMtmListPresetSource,
  isValidMtmServiceCaseOrdering,
  isValidMtmTriggerSource,
  isMtmCaseActive,
} from '@/utils/mtm'

const isDebug = import.meta.env.MODE !== 'production'
const log = (...args: unknown[]) => {
  if (isDebug) console.log(...args)
}

const props = defineProps<{
  id?: string
}>()

const route = useRoute()
const router = useRouter()
const { success: showSuccess, error: showError } = useToast()

const serviceCase = ref<MtmServiceCase | null>(null)
const loading = ref(false)
const transitioning = ref(false)
const loadError = ref('')
const showFollowUpModal = ref(false)

const serviceCaseId = computed(() => {
  const rawId = props.id || String(route.params.id || '')
  return rawId.trim()
})

const validStatuses: MtmServiceStatus[] = [
  'pending',
  'interviewing',
  'assessing',
  'intervening',
  'following_up',
  'completed',
]
const defaultOrdering: MtmServiceCaseOrdering = '-created_at'
const validPresetSources: MtmListPresetSource[] = ['all', 'active_status', 'suggested_trigger']

const cameFromMtmList = computed(() => getRouteQueryValue('from') === 'mtm-list')

const pageDescription = computed(() => {
  if (!serviceCase.value) {
    return '查看专业用药指导服务的当前状态、处理进度和已经沉淀下来的摘要信息。'
  }

  if (isMtmCaseActive(serviceCase.value.status)) {
    return '当前服务仍在处理中，你可以先在这里查看进度、问诊摘要和后续跟进情况。'
  }

  return '当前服务已经完成，你可以在这里回看本次专业服务的主要过程和结果。'
})

const progressDescription = computed(() => {
  if (!serviceCase.value) {
    return '正在加载当前服务进度'
  }

  if (serviceCase.value.completed_at) {
    return `本次服务已于 ${formatDateTime(serviceCase.value.completed_at)} 完成`
  }

  return `当前处于 ${getMtmStatusText(serviceCase.value.status)} 阶段`
})

const transitionActions = computed(() => {
  if (!serviceCase.value) {
    return []
  }
  return getMtmTransitionActions(serviceCase.value.status)
})

const visibleTransitionActions = computed(() => {
  if (!serviceCase.value) {
    return []
  }

  if (serviceCase.value.status === 'pending') {
    if (!serviceCase.value.interview) {
      return []
    }

    return transitionActions.value.map(action => {
      if (action.targetStatus !== 'interviewing') {
        return action
      }

      return {
        ...action,
        label: '标记为问诊中',
        description: '问诊已经开始后，再把当前服务状态同步为问诊中。',
      }
    })
  }

  if (serviceCase.value.status === 'interviewing') {
    if (!serviceCase.value.assessment) {
      return []
    }

    return transitionActions.value.map(action => {
      if (action.targetStatus !== 'assessing') {
        return action
      }

      return {
        ...action,
        label: '标记为评估中',
        description: '评估已经开始后，再把当前服务状态同步为评估中。',
      }
    })
  }

  return transitionActions.value
})

const transitionHintText = computed(() => {
  if (!serviceCase.value) {
    return '正在读取当前阶段可执行动作。'
  }

  if (!visibleTransitionActions.value.length) {
    if (serviceCase.value.status === 'pending' && !serviceCase.value.interview) {
      return '先从下方问诊入口开始填写，等问诊真正开始后再同步服务状态。'
    }
    if (serviceCase.value.status === 'interviewing' && !serviceCase.value.assessment) {
      return '先从下方评估入口开始填写，等评估真正开始后再同步服务状态。'
    }
    return '当前服务已经处于最终阶段，不需要继续推进。'
  }

  return '点击下面的动作按钮后，会直接调用真实接口推进到下一合法阶段。'
})

const interviewBasicInfoLines = computed(() => {
  if (!serviceCase.value?.interview) {
    return []
  }
  return buildObjectLines(serviceCase.value.interview.basic_info_snapshot)
})

const interviewMedicationLines = computed(() => {
  if (!serviceCase.value?.interview) {
    return []
  }
  return buildUnknownListLines(serviceCase.value.interview.medication_history)
})

const interviewEntryMeta = computed(() => {
  const currentInterview = serviceCase.value?.interview

  if (!currentInterview) {
    return {
      badgeText: '未开始',
      badgeClass: 'bg-slate-100 text-slate-700',
      buttonText: '开始问诊',
      description: '当前还没有问诊内容，可以先进入问诊页补充基础情况、当前用药和本次目标。',
    }
  }

  if (currentInterview.completed_at) {
    return {
      badgeText: '已完成',
      badgeClass: 'bg-emerald-100 text-emerald-700',
      buttonText: '查看已填问诊',
      description: '当前问诊已经填写完成；如果需要回看或继续补充，可以直接从这里进入。',
    }
  }

  return {
    badgeText: '草稿中',
    badgeClass: 'bg-amber-100 text-amber-700',
    buttonText: '继续问诊',
    description: '上次填写的问诊草稿已经保留，可以继续补充后再手动标记完成。',
  }
})

const interviewLifestyleLines = computed(() => {
  if (!serviceCase.value?.interview) {
    return []
  }

  const allergyLines = buildUnknownListLines(serviceCase.value.interview.allergy_history).map(
    item => `过敏史：${item}`
  )
  return [
    ...buildObjectLines(serviceCase.value.interview.lifestyle_info).map(
      item => `${item.label}：${item.value}`
    ),
    ...allergyLines,
    ...(serviceCase.value.interview.economic_context
      ? [`经济情况：${serviceCase.value.interview.economic_context}`]
      : []),
  ]
})

const assessmentEntryMeta = computed(() => {
  const currentInterview = serviceCase.value?.interview
  const currentAssessment = serviceCase.value?.assessment

  if (!currentInterview?.completed_at) {
    return {
      badgeText: '待问诊完成',
      badgeClass: 'bg-slate-100 text-slate-700',
      buttonText: '暂不能评估',
      description: '建议先完成问诊，再进入评估页整理风险等级、问题清单和综合判断。',
      disabled: true,
    }
  }

  if (!currentAssessment) {
    return {
      badgeText: '未开始',
      badgeClass: 'bg-slate-100 text-slate-700',
      buttonText: '开始评估',
      description: '问诊已经完成，可以继续进入评估页补充五维评分、问题清单和评估总结。',
      disabled: false,
    }
  }

  if (currentAssessment.completed_at) {
    return {
      badgeText: '已完成',
      badgeClass: 'bg-emerald-100 text-emerald-700',
      buttonText: '查看已填评估',
      description: '当前评估已经填写完成；如果需要回看或继续补充，可以直接从这里进入。',
      disabled: false,
    }
  }

  return {
    badgeText: '草稿中',
    badgeClass: 'bg-amber-100 text-amber-700',
    buttonText: '继续评估',
    description: '上次填写的评估草稿已经保留，可以继续补充后再手动标记完成。',
    disabled: false,
  }
})

const assessmentScoreCards = computed(() => {
  if (!serviceCase.value?.assessment) {
    return []
  }

  return [
    {
      label: '适宜性评分',
      value: scoreText(serviceCase.value.assessment.appropriateness_score),
    },
    {
      label: '有效性评分',
      value: scoreText(serviceCase.value.assessment.effectiveness_score),
    },
    {
      label: '安全性评分',
      value: scoreText(serviceCase.value.assessment.safety_score),
    },
    {
      label: '依从性评分',
      value: scoreText(serviceCase.value.assessment.adherence_score),
    },
    {
      label: '经济性评分',
      value: scoreText(serviceCase.value.assessment.economic_score),
    },
  ]
})

const assessmentProblemLines = computed(() => {
  if (!serviceCase.value?.assessment) {
    return []
  }
  return buildUnknownListLines(serviceCase.value.assessment.problem_list)
})

const planInterventionLines = computed(() => {
  if (!serviceCase.value?.plan) {
    return []
  }
  return buildUnknownListLines(serviceCase.value.plan.interventions)
})

const followUpCards = computed<MtmFollowUpSummary[]>(() => {
  return serviceCase.value?.follow_ups || []
})

/**
 * 拉取单条 MTM 服务单详情。
 */
const fetchServiceCaseDetail = async () => {
  if (!serviceCaseId.value) {
    loadError.value = '缺少服务单编号，暂时无法查看详情'
    return
  }

  try {
    loading.value = true
    loadError.value = ''
    log('🔵 [MtmServiceCaseDetailPage] 开始获取服务详情', {
      serviceCaseId: serviceCaseId.value,
    })
    const detail = await mtmApi.getServiceCaseDetail(serviceCaseId.value)
    serviceCase.value = detail
    log('🟢 [MtmServiceCaseDetailPage] 服务详情获取成功', detail)
  } catch (error) {
    if (isRequestCancelledError(error)) {
      log('🟡 [MtmServiceCaseDetailPage] 服务详情请求已取消')
      return
    }

    console.error('🔴 [MtmServiceCaseDetailPage] 获取服务详情失败', error)
    loadError.value = error instanceof Error ? error.message : '获取服务详情失败'
    if (!serviceCase.value) {
      showError(loadError.value)
    }
  } finally {
    loading.value = false
  }
}

/**
 * 执行服务单状态推进，并在成功后刷新详情。
 */
const handleTransition = async (targetStatus: MtmServiceStatus) => {
  if (!serviceCase.value || transitioning.value) {
    return
  }

  try {
    transitioning.value = true
    const payload = {
      target_status: targetStatus,
      notes: buildMtmTransitionNote(serviceCase.value.status, targetStatus),
    }
    log('🔵 [MtmServiceCaseDetailPage] 开始推进服务状态', {
      serviceCaseId: serviceCase.value.id,
      payload,
    })
    const updated = await mtmApi.transitionServiceCase(serviceCase.value.id, payload)
    serviceCase.value = updated
    showSuccess(`当前已更新为${getMtmStatusText(updated.status)}`)
    log('🟢 [MtmServiceCaseDetailPage] 服务状态推进成功', updated)
    await fetchServiceCaseDetail()
  } catch (error) {
    console.error('🔴 [MtmServiceCaseDetailPage] 服务状态推进失败', error)
    showError(error instanceof Error ? error.message : '更新服务状态失败，请稍后重试')
  } finally {
    transitioning.value = false
  }
}

/**
 * 返回上一页；如果没有可回退历史，则回到首页仪表板。
 */


const goToSoapNotes = () => {
  if (!serviceCase.value) return
  router.push({
    name: 'MtmSoapNotes',
    params: { id: serviceCase.value.id.toString() },
  })
}

const goToReport = () => {
  if (!serviceCase.value) return
  router.push({
    name: 'MtmReportPreview',
    params: { id: serviceCase.value.id.toString() },
  })
}



const goBack = () => {
  if (cameFromMtmList.value) {
    const query = buildListReturnQuery()
    log('🔵 [MtmServiceCaseDetailPage] 返回列表页并恢复查询上下文', query)
    router.push({
      path: '/mtm/service-cases',
      query,
    })
    return
  }

  if (window.history.length > 1) {
    router.back()
    return
  }
  router.push('/dashboard')
}

/**
 * 进入问诊表单页，并尽量保留当前详情页上下文。
 */
const goToInterviewForm = () => {
  if (!serviceCaseId.value) {
    return
  }

  router.push({
    path: `/mtm/service-cases/${serviceCaseId.value}/interview`,
    query: { ...route.query },
  })
}

/**
 * 进入评估表单页，并尽量保留当前详情页上下文。
 */

const planEntryMeta = computed(() => {
  const currentAssessment = serviceCase.value?.assessment
  const currentPlan = serviceCase.value?.plan

  if (!currentAssessment?.completed_at) {
    return {
      badgeText: '待评估完成',
      badgeClass: 'bg-slate-100 text-slate-700',
      buttonText: '暂不能制定计划',
      description: '建议先完成评估，再进入计划页制定具体的干预措施。',
      disabled: true,
    }
  }

  if (!currentPlan) {
    return {
      badgeText: '未开始',
      badgeClass: 'bg-slate-100 text-slate-700',
      buttonText: '开始制定计划',
      description: '评估已经完成，可以进入计划页制定干预措施和行动计划。',
      disabled: false,
    }
  }

  if (!currentPlan.confirmed_at) {
    return {
      badgeText: '草稿',
      badgeClass: 'bg-amber-100 text-amber-700',
      buttonText: '继续制定计划',
      description: '干预计划草稿已保存，可以继续编辑或完成确认。',
      disabled: false,
    }
  }

  return {
    badgeText: '已完成',
    badgeClass: 'bg-emerald-100 text-emerald-700',
    buttonText: '查看计划',
    description: '干预计划已完成制定，可以随时回看详情。',
    disabled: false,
  }
})

const goToPlanForm = () => {
  if (!serviceCase.value) return
  router.push({
    name: 'MtmPlanForm',
    params: { id: serviceCase.value.id.toString() },
  })
}

const goToAssessmentForm = () => {
  if (!serviceCaseId.value || assessmentEntryMeta.value.disabled) {
    return
  }

  router.push({
    path: `/mtm/service-cases/${serviceCaseId.value}/assessment`,
    query: { ...route.query },
  })
}

/**
 * 读取详情页 query 中的单个字符串值。
 */
const getRouteQueryValue = (key: string) => {
  const value = route.query[key]
  return Array.isArray(value) ? value[0] || '' : value || ''
}

/**
 * 判断详情页 query 中的状态值是否合法。
 */
const isValidStatus = (value: string): value is MtmServiceStatus => {
  return validStatuses.includes(value as MtmServiceStatus)
}
/**
 * 判断详情页 query 中的预设来源值是否合法。
 */
const isValidPresetSource = (value: string): value is MtmListPresetSource => {
  return validPresetSources.includes(value as MtmListPresetSource) && isValidMtmListPresetSource(value)
}
/**
 * 从详情页 query 中构造返回列表页需要恢复的最小查询参数。
 */
const buildListReturnQuery = (): LocationQueryRaw => {
  const query: LocationQueryRaw = {}
  const pageValue = getRouteQueryValue('page')
  const searchValue = getRouteQueryValue('search').trim()
  const statusValue = getRouteQueryValue('status')
  const triggerSourceValue = getRouteQueryValue('trigger_source')
  const orderingValue = getRouteQueryValue('ordering')
  const presetSourceValue = getRouteQueryValue('preset_source')
  const parsedPage = Number.parseInt(pageValue, 10)

  if (Number.isFinite(parsedPage) && parsedPage > 1) {
    query.page = String(parsedPage)
  }
  if (searchValue) {
    query.search = searchValue
  }
  if (isValidStatus(statusValue)) {
    query.status = statusValue
  }
  if (isValidMtmTriggerSource(triggerSourceValue)) {
    query.trigger_source = triggerSourceValue
  }
  if (isValidMtmServiceCaseOrdering(orderingValue) && orderingValue !== defaultOrdering) {
    query.ordering = orderingValue
  }
  if (isValidPresetSource(presetSourceValue)) {
    query.preset_source = presetSourceValue
  }

  return query
}

/**
 * 把服务端返回的对象整理成适合展示的键值对。
 */
const buildObjectLines = (value: Record<string, unknown> | null | undefined) => {
  if (!value || typeof value !== 'object') {
    return []
  }

  return Object.entries(value)
    .filter(([, item]) => item !== null && item !== undefined && item !== '')
    .slice(0, 6)
    .map(([key, item]) => ({
      label: formatFieldLabel(key),
      value: formatUnknownValue(item),
    }))
}

/**
 * 把列表型未知结构整理成适合页面展示的人话列表。
 */
const buildUnknownListLines = (items: unknown[] | null | undefined) => {
  if (!Array.isArray(items)) {
    return []
  }

  return items
    .map(item => formatUnknownValue(item))
    .filter(item => item !== '未记录')
    .slice(0, 6)
}

/**
 * 将未知值整理成可读文本，尽量避免直接展示 JSON。
 */
const formatUnknownValue = (value: unknown): string => {
  if (value === null || value === undefined || value === '') {
    return '未记录'
  }

  if (typeof value === 'string') {
    return value.trim() || '未记录'
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }

  if (Array.isArray(value)) {
    const lines = value
      .map(item => formatUnknownValue(item))
      .filter(item => item !== '未记录')
      .slice(0, 3)
    return lines.length ? lines.join('、') : '未记录'
  }

  if (typeof value === 'object') {
    const record = value as Record<string, unknown>
    const preferredKeys = ['title', 'name', 'item', 'drug_name', 'summary', 'type', 'label']

    for (const key of preferredKeys) {
      const candidate = record[key]
      if (typeof candidate === 'string' && candidate.trim()) {
        const extra =
          key !== 'type' && typeof record.type === 'string' && record.type.trim()
            ? `（${record.type.trim()}）`
            : ''
        return `${candidate.trim()}${extra}`
      }
    }

    const compactLines = Object.entries(record)
      .filter(([, item]) => ['string', 'number', 'boolean'].includes(typeof item))
      .slice(0, 3)
      .map(([key, item]) => `${formatFieldLabel(key)}：${String(item)}`)

    return compactLines.length ? compactLines.join('；') : '已记录'
  }

  return '未记录'
}

/**
 * 把接口字段名转成更容易理解的中文标签。
 */
const formatFieldLabel = (field: string) => {
  const mapping: Record<string, string> = {
    patient_name: '患者姓名',
    age: '年龄',
    gender: '性别',
    contact_phone: '联系电话',
    main_diagnosis: '主要问题',
    weight: '体重',
    height: '身高',
    diagnosis: '诊断',
    blood_pressure: '血压',
    blood_sugar: '血糖',
    smoking: '吸烟情况',
    drinking: '饮酒情况',
    exercise: '运动情况',
    sleep: '睡眠情况',
  }
  return mapping[field] || field.replace(/_/g, ' ')
}

/**
 * 格式化时间，空值时返回统一空态。
 */
const formatDateTime = (value?: string | null) => {
  if (!value) {
    return '未记录'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return '未记录'
  }

  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * 把分值格式化为统一文案。
 */
const scoreText = (score: number | null) => {
  if (score === null || score === undefined) {
    return '未评分'
  }
  return `${score} 分`
}

/**
 * 把评估风险等级转成人话。
 */
const assessmentRiskText = (riskLevel: 'low' | 'medium' | 'high') => {
  const mapping = {
    low: '低风险',
    medium: '中风险',
    high: '高风险',
  }
  return mapping[riskLevel]
}

/**
 * 返回评估风险等级的样式。
 */
const assessmentRiskClass = (riskLevel: 'low' | 'medium' | 'high') => {
  const mapping = {
    low: 'bg-emerald-100 text-emerald-700',
    medium: 'bg-amber-100 text-amber-700',
    high: 'bg-rose-100 text-rose-700',
  }
  return mapping[riskLevel]
}

/**
 * 把计划优先级转成人话。
 */
const planPriorityText = (priority: 'low' | 'medium' | 'high' | 'urgent') => {
  const mapping = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急',
  }
  return mapping[priority]
}

/**
 * 把患者确认状态转成人话。
 */
const planConfirmationText = (
  status: 'pending' | 'confirmed' | 'declined'
) => {
  const mapping = {
    pending: '待确认',
    confirmed: '已确认',
    declined: '已拒绝',
  }
  return mapping[status]
}

/**
 * 把随访方式转成人话。
 */
const followUpMethodText = (method: string) => {
  const mapping: Record<string, string> = {
    phone: '电话',
    in_person: '面谈',
    video: '视频',
    wechat: '微信',
    other: '其他',
  }
  return mapping[method] || '其他'
}

/**
 * 把随访执行状态转成人话。
 */
const followUpStatusText = (status: string) => {
  const mapping: Record<string, string> = {
    pending: '待执行',
    completed: '已完成',
    missed: '未完成',
    cancelled: '已取消',
  }
  return mapping[status] || '未记录'
}

/**
 * 把随访后的风险变化转成人话。
 */
const followUpRiskText = (riskChange: string) => {
  const mapping: Record<string, string> = {
    improved: '已有改善',
    stable: '基本稳定',
    worsened: '风险加重',
    unknown: '暂未判断',
  }
  return mapping[riskChange] || '暂未判断'
}

watch(serviceCaseId, () => {
  fetchServiceCaseDetail()
})

onMounted(() => {
  fetchServiceCaseDetail()
})
</script>
