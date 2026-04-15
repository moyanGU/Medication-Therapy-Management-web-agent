<template>
  <div class="relative min-h-screen overflow-hidden bg-slate-50">
    <div
      class="absolute inset-0 pointer-events-none scale-125 bg-center bg-cover opacity-20 blur-xl"
      style="background-image: url('/images/mtm-cover-logo.svg')"
    ></div>
    <div class="absolute inset-0 pointer-events-none bg-slate-50/75"></div>

    <main class="relative z-10 mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <section
        class="mb-6 rounded-3xl border border-blue-100 bg-gradient-to-r from-blue-600 via-sky-600 to-cyan-600 p-6 text-white shadow-lg"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p class="mb-2 text-sm text-blue-100">{{ currentDate }}</p>
            <h1 class="text-2xl font-bold sm:text-3xl">今天先把该做的事处理掉</h1>
            <p class="mt-3 max-w-2xl text-sm text-blue-50 sm:text-base">
              {{ welcomeDescription }}
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-3">
            <span
              class="inline-flex items-center rounded-full bg-white/15 px-3 py-1 text-sm text-white"
            >
              今日待处理 {{ dashboard.today_tasks.pending }} 项
            </span>
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-medium text-sky-700 shadow-sm transition hover:bg-sky-50"
              :disabled="loading"
              @click="fetchDashboardSummary"
            >
              <RefreshCw class="h-4 w-4" :class="loading ? 'animate-spin' : ''" />
              刷新首页
            </button>
          </div>
        </div>
      </section>

      <section v-if="showInitialLoading" class="space-y-6">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div
            v-for="index in 4"
            :key="index"
            class="h-28 animate-pulse rounded-2xl bg-white/80 shadow-sm"
          ></div>
        </div>
        <div class="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div class="xl:col-span-2 h-96 animate-pulse rounded-2xl bg-white/80 shadow-sm"></div>
          <div class="h-96 animate-pulse rounded-2xl bg-white/80 shadow-sm"></div>
        </div>
      </section>

      <section
        v-else-if="showInitialError"
        class="rounded-2xl border border-red-100 bg-white p-8 text-center shadow-sm"
      >
        <div
          class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-50"
        >
          <AlertTriangle class="h-6 w-6 text-red-500" />
        </div>
        <h2 class="text-lg font-semibold text-slate-900">首页数据暂时没加载成功</h2>
        <p class="mt-2 text-sm text-slate-600">
          {{ loadError || '请稍后重试，或者刷新页面看看。' }}
        </p>
        <button
          type="button"
          class="mt-4 inline-flex items-center gap-2 rounded-xl bg-sky-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-700"
          @click="fetchDashboardSummary"
        >
          <RefreshCw class="h-4 w-4" />
          重新加载
        </button>
      </section>

      <template v-else>
        <section class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <article
            v-for="item in summaryCards"
            :key="item.title"
            class="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm text-slate-500">{{ item.title }}</p>
                <p class="mt-2 text-3xl font-semibold text-slate-900">{{ item.value }}</p>
                <p class="mt-2 text-sm text-slate-500">{{ item.description }}</p>
              </div>
              <div :class="['rounded-2xl p-3', item.iconWrapperClass]">
                <component :is="item.icon" class="h-5 w-5" :class="item.iconClass" />
              </div>
            </div>
          </article>
        </section>

        <section class="mb-6 grid grid-cols-1 gap-6 xl:grid-cols-3">
          <article class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm xl:col-span-2">
            <div class="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 class="text-lg font-semibold text-slate-900">今天要做的事</h2>
                <p class="mt-1 text-sm text-slate-500">
                  已处理 {{ dashboard.today_tasks.completed }} 项，还剩
                  {{ dashboard.today_tasks.pending }} 项需要你留意。
                </p>
              </div>
              <router-link
                to="/reminders"
                class="inline-flex items-center gap-2 text-sm font-medium text-sky-700 transition hover:text-sky-800"
              >
                去处理提醒
                <ChevronRight class="h-4 w-4" />
              </router-link>
            </div>

            <div
              v-if="visibleTasks.length"
              class="space-y-3"
            >
              <div
                v-for="item in visibleTasks"
                :key="item.reminder_id"
                class="flex flex-col gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div class="min-w-0">
                  <div class="flex flex-wrap items-center gap-2">
                    <p class="font-medium text-slate-900">{{ item.medicine_name }}</p>
                    <span class="rounded-full bg-sky-100 px-2 py-0.5 text-xs text-sky-700">
                      {{ item.reminder_time }}
                    </span>
                  </div>
                  <p class="mt-1 text-sm text-slate-600">
                    {{ item.title }}，{{ item.dosage }} {{ item.dosage_unit }}
                    <span v-if="item.meal_timing && item.meal_timing !== 'none'">
                      ，{{ mealTimingText(item.meal_timing) }}
                    </span>
                  </p>
                </div>

                <div class="flex items-center gap-3">
                  <span
                    class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium"
                    :class="taskStatusClass(item)"
                  >
                    {{ taskStatusText(item) }}
                  </span>
                  <router-link
                    to="/reminders"
                    class="inline-flex items-center gap-1 text-sm font-medium text-sky-700 transition hover:text-sky-800"
                  >
                    去查看
                    <ChevronRight class="h-4 w-4" />
                  </router-link>
                </div>
              </div>
            </div>

            <div
              v-else
              class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center"
            >
              <p class="text-base font-medium text-slate-900">今天暂时没有待处理任务</p>
              <p class="mt-2 text-sm text-slate-500">
                你可以去看看提醒设置，或者补充新的药品和提醒计划。
              </p>
              <div class="mt-4 flex flex-wrap justify-center gap-3">
                <router-link
                  to="/reminders/create"
                  class="rounded-xl bg-sky-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-700"
                >
                  新建提醒
                </router-link>
                <router-link
                  to="/medicines"
                  class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
                >
                  去看药品
                </router-link>
              </div>
            </div>
          </article>

          <article class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
            <div class="mb-5 flex items-center justify-between">
              <div>
                <h2 class="text-lg font-semibold text-slate-900">当前需要留意</h2>
                <p class="mt-1 text-sm text-slate-500">
                  先处理最影响今天用药安排的事项。
                </p>
              </div>
              <ShieldAlert class="h-5 w-5 text-amber-500" />
            </div>

            <div v-if="dashboard.risk_alerts.length" class="space-y-3">
              <div
                v-for="risk in dashboard.risk_alerts"
                :key="risk.type"
                class="rounded-2xl border p-4"
                :class="riskCardClass(risk.level)"
              >
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <div class="flex items-center gap-2">
                      <p class="font-medium text-slate-900">{{ risk.title }}</p>
                      <span
                        class="rounded-full px-2 py-0.5 text-xs font-medium"
                        :class="riskBadgeClass(risk.level)"
                      >
                        {{ risk.count }} 项
                      </span>
                    </div>
                    <p class="mt-2 text-sm text-slate-600">{{ risk.message }}</p>
                  </div>
                </div>
                <router-link
                  :to="riskTarget(risk.type)"
                  class="mt-3 inline-flex items-center gap-1 text-sm font-medium text-sky-700 transition hover:text-sky-800"
                >
                  {{ riskActionText(risk.type) }}
                  <ChevronRight class="h-4 w-4" />
                </router-link>
              </div>
            </div>

            <div
              v-else
              class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500"
            >
              目前没有明显风险，今天可以按计划安心管理。
            </div>
          </article>
        </section>

        <section class="mb-6 grid grid-cols-1 gap-6 xl:grid-cols-3">
          <article class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
            <div class="mb-5 flex items-center justify-between">
              <div>
                <h2 class="text-lg font-semibold text-slate-900">药品概览</h2>
                <p class="mt-1 text-sm text-slate-500">库存和临期情况一眼看清。</p>
              </div>
              <Pill class="h-5 w-5 text-sky-600" />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-sm text-slate-500">药品总数</p>
                <p class="mt-2 text-2xl font-semibold text-slate-900">
                  {{ dashboard.medication_summary.total_medicines }}
                </p>
              </div>
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-sm text-slate-500">活跃提醒</p>
                <p class="mt-2 text-2xl font-semibold text-slate-900">
                  {{ dashboard.medication_summary.active_reminders }}
                </p>
              </div>
            </div>

            <div class="mt-5 space-y-4">
              <div>
                <div class="flex items-center justify-between">
                  <p class="text-sm font-medium text-slate-700">低库存</p>
                  <router-link to="/medicines" class="text-sm text-sky-700 hover:text-sky-800">
                    去补充
                  </router-link>
                </div>
                <div v-if="dashboard.medication_summary.low_stock_items.length" class="mt-2 space-y-2">
                  <div
                    v-for="item in dashboard.medication_summary.low_stock_items"
                    :key="`low-${item.id}`"
                    class="flex items-center justify-between rounded-xl bg-rose-50 px-3 py-2"
                  >
                    <span class="text-sm text-slate-700">{{ item.name }}</span>
                    <span class="text-sm font-medium text-rose-600">{{ item.quantity }} 份</span>
                  </div>
                </div>
                <p v-else class="mt-2 text-sm text-slate-500">目前没有低库存药品。</p>
              </div>

              <div>
                <div class="flex items-center justify-between">
                  <p class="text-sm font-medium text-slate-700">即将临期</p>
                  <router-link to="/medicines" class="text-sm text-sky-700 hover:text-sky-800">
                    去查看
                  </router-link>
                </div>
                <div
                  v-if="dashboard.medication_summary.expiring_soon_items.length"
                  class="mt-2 space-y-2"
                >
                  <div
                    v-for="item in dashboard.medication_summary.expiring_soon_items"
                    :key="`expiring-${item.id}`"
                    class="flex items-center justify-between rounded-xl bg-amber-50 px-3 py-2"
                  >
                    <span class="text-sm text-slate-700">{{ item.name }}</span>
                    <span class="text-sm font-medium text-amber-700">
                      {{ expiryText(item.days_until_expiry) }}
                    </span>
                  </div>
                </div>
                <p v-else class="mt-2 text-sm text-slate-500">目前没有即将临期的药品。</p>
              </div>
            </div>
          </article>

          <article class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
            <div class="mb-5 flex items-center justify-between">
              <div>
                <h2 class="text-lg font-semibold text-slate-900">复诊提醒</h2>
                <p class="mt-1 text-sm text-slate-500">别让复诊安排影响现在的用药节奏。</p>
              </div>
              <Stethoscope class="h-5 w-5 text-indigo-600" />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-sm text-slate-500">已到期</p>
                <p class="mt-2 text-2xl font-semibold text-slate-900">
                  {{ dashboard.followup_summary.due_count }}
                </p>
              </div>
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-sm text-slate-500">7天内</p>
                <p class="mt-2 text-2xl font-semibold text-slate-900">
                  {{ dashboard.followup_summary.upcoming_count }}
                </p>
              </div>
            </div>

            <div class="mt-5 rounded-2xl bg-indigo-50 p-4">
              <p class="text-sm font-medium text-indigo-700">最近一条复诊安排</p>
              <div v-if="dashboard.followup_summary.next_followup" class="mt-2">
                <p class="font-medium text-slate-900">
                  {{ dashboard.followup_summary.next_followup.hospital }}
                </p>
                <p class="mt-1 text-sm text-slate-600">
                  {{ dashboard.followup_summary.next_followup.department }} ·
                  {{ dashboard.followup_summary.next_followup.doctor }}
                </p>
                <p class="mt-1 text-sm text-indigo-700">
                  {{ followupText(dashboard.followup_summary.next_followup.days_until_follow_up) }}
                </p>
              </div>
              <p v-else class="mt-2 text-sm text-slate-500">暂时没有新的复诊安排。</p>
            </div>

            <router-link
              to="/medical-records"
              class="mt-4 inline-flex items-center gap-1 text-sm font-medium text-sky-700 transition hover:text-sky-800"
            >
              去看就医记录
              <ChevronRight class="h-4 w-4" />
            </router-link>
          </article>

          <article class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
            <div class="mb-5 flex items-center justify-between">
              <div>
                <h2 class="text-lg font-semibold text-slate-900">近 7 天依从性</h2>
                <p class="mt-1 text-sm text-slate-500">这能帮你快速判断最近执行得稳不稳。</p>
              </div>
              <HeartPulse class="h-5 w-5 text-emerald-600" />
            </div>

            <div class="rounded-2xl bg-emerald-50 p-4">
              <div class="flex items-end justify-between gap-4">
                <div>
                  <p class="text-sm text-emerald-700">完成用药率</p>
                  <p class="mt-2 text-3xl font-semibold text-slate-900">
                    {{ rateText(dashboard.adherence_summary.summary_7d.adherence_rate) }}
                  </p>
                </div>
                <div class="text-right">
                  <p class="text-sm text-slate-500">按时服药率</p>
                  <p class="mt-2 text-xl font-semibold text-slate-900">
                    {{ rateText(dashboard.adherence_summary.summary_7d.on_time_rate) }}
                  </p>
                </div>
              </div>
            </div>

            <div class="mt-4 space-y-4">
              <div
                v-for="item in adherenceComparisonCards"
                :key="item.title"
                class="rounded-2xl bg-slate-50 p-4"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-slate-700">{{ item.title }}</p>
                    <p class="mt-1 text-xs text-slate-500">{{ item.description }}</p>
                  </div>
                  <span class="text-sm font-semibold text-slate-900">{{ item.value }}</span>
                </div>
                <div class="mt-3 h-2 rounded-full bg-slate-200">
                  <div
                    class="h-2 rounded-full transition-all"
                    :class="item.barClass"
                    :style="{ width: `${item.rate}%` }"
                  ></div>
                </div>
              </div>
            </div>

            <div class="mt-4 space-y-2">
              <div class="rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-600">
                提醒响应率：{{
                  rateText(dashboard.adherence_summary.summary_7d.response_summary.response_rate)
                }}
                ，未响应
                {{ dashboard.adherence_summary.summary_7d.response_summary.unresponded_count }} 次
              </div>
              <p
                v-for="flag in dashboard.adherence_summary.summary_7d.risk_flags"
                :key="flag"
                class="rounded-xl bg-amber-50 px-3 py-2 text-sm text-amber-700"
              >
                {{ flag }}
              </p>
              <p
                v-if="!dashboard.adherence_summary.summary_7d.risk_flags.length"
                class="rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-500"
              >
                最近 7 天整体执行比较稳定。
              </p>
            </div>

            <router-link
              to="/records/stats"
              class="mt-4 inline-flex items-center gap-1 text-sm font-medium text-sky-700 transition hover:text-sky-800"
            >
              去看详细统计
              <ChevronRight class="h-4 w-4" />
            </router-link>
          </article>
        </section>

        <section
          class="mb-6 rounded-2xl border p-6 shadow-sm"
          :class="
            dashboard.mtm_entry_hint.recommended
              ? 'border-violet-200 bg-gradient-to-r from-violet-50 via-fuchsia-50 to-sky-50'
              : 'border-slate-100 bg-white'
          "
        >
          <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div class="max-w-2xl">
              <div class="flex items-center gap-2">
                <Activity class="h-5 w-5 text-violet-600" />
                <h2 class="text-lg font-semibold text-slate-900">专业用药指导建议</h2>
              </div>
              <p class="mt-2 text-sm text-slate-600">{{ dashboard.mtm_entry_hint.message }}</p>

              <div class="mt-4 flex flex-wrap gap-2">
                <span
                  class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium"
                  :class="
                    dashboard.mtm_entry_hint.recommended
                      ? 'bg-violet-100 text-violet-700'
                      : 'bg-slate-100 text-slate-700'
                  "
                >
                  {{ dashboard.mtm_entry_hint.recommended ? '建议优先处理' : '可按需发起' }}
                </span>
                <span
                  class="inline-flex items-center rounded-full bg-white/80 px-3 py-1 text-xs font-medium text-slate-700"
                >
                  触发原因 {{ dashboard.mtm_entry_hint.reason_count }} 条
                </span>
                <span
                  v-if="activeMtmCase"
                  class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium"
                  :class="getMtmStatusBadgeClass(activeMtmCase.status)"
                >
                  当前进度：{{ getMtmStatusText(activeMtmCase.status) }}
                </span>
              </div>

              <ul
                v-if="dashboard.mtm_entry_hint.reasons.length"
                class="mt-4 space-y-2 text-sm text-slate-600"
              >
                <li
                  v-for="reason in dashboard.mtm_entry_hint.reasons"
                  :key="reason"
                  class="flex items-start gap-2"
                >
                  <span class="mt-1 h-2 w-2 rounded-full bg-violet-500"></span>
                  <span>{{ reason }}</span>
                </li>
              </ul>

              <div
                v-if="mtmShortcutPresetEntries.length"
                class="mt-4 flex flex-wrap gap-2"
              >
                <router-link
                  v-for="entry in mtmShortcutPresetEntries"
                  :key="entry.key"
                  :to="entry.to"
                  class="inline-flex items-center rounded-full border bg-white/80 px-3 py-1.5 text-xs font-medium transition"
                  :class="
                    entry.key === 'active_status'
                      ? 'border-violet-200 text-violet-700 hover:bg-violet-50'
                      : 'border-sky-200 text-sky-700 hover:bg-sky-50'
                  "
                >
                  {{ entry.shortLabel }}
                </router-link>
              </div>
            </div>

            <div class="flex flex-wrap gap-3 lg:max-w-sm lg:justify-end">
              <button
                type="button"
                class="rounded-xl px-4 py-2 text-sm font-medium text-white transition"
                :class="
                  mtmCreating || activeMtmCase
                    ? 'cursor-not-allowed bg-slate-400'
                    : 'bg-violet-600 hover:bg-violet-700'
                "
                :disabled="mtmCreating || !!activeMtmCase"
                @click="handleCreateMtmService"
              >
                {{
                  mtmCreating
                    ? '正在发起专业服务...'
                    : activeMtmCase
                      ? '当前已有进行中的专业服务'
                      : dashboard.mtm_entry_hint.recommended
                        ? '立即发起专业服务'
                        : '手动发起专业服务'
                }}
              </button>
              <button
                type="button"
                class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                :disabled="mtmLoading"
                @click="fetchMtmServiceCases"
              >
                {{ mtmLoading ? '正在刷新状态...' : '刷新服务状态' }}
              </button>
              <router-link
                :to="allMtmListRoute"
                class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
              >
                查看全部
              </router-link>
              <router-link
                v-if="activeMtmCase"
                :to="`/mtm/service-cases/${activeMtmCase.id}`"
                class="rounded-xl border border-violet-200 bg-white px-4 py-2 text-sm font-medium text-violet-700 transition hover:bg-violet-50"
              >
                查看当前详情
              </router-link>
              <router-link
                to="/records/stats"
                class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
              >
                看看依从性统计
              </router-link>
            </div>
          </div>

          <div class="mt-5 rounded-2xl border border-white/70 bg-white/70 p-4">
            <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h3 class="text-sm font-medium text-slate-900">最近专业服务状态</h3>
                <p class="mt-1 text-sm text-slate-500">
                  {{
                    activeMtmCase
                      ? '你当前已有进行中的专业服务，可以先看现在的处理进度。'
                      : '发起后会在这里显示最新状态，方便你随时确认。'
                  }}
                </p>
              </div>
              <span
                v-if="activeMtmCase"
                class="inline-flex items-center self-start rounded-full px-3 py-1 text-xs font-medium sm:self-auto"
                :class="getMtmStatusBadgeClass(activeMtmCase.status)"
              >
                {{ getMtmStatusText(activeMtmCase.status) }}
              </span>
              <router-link
                v-if="recentMtmCases.length"
                :to="allMtmListRoute"
                class="inline-flex items-center self-start text-sm font-medium text-violet-700 transition hover:text-violet-800 sm:self-auto"
              >
                查看全部
              </router-link>
            </div>

            <div
              v-if="mtmLoading"
              class="mt-4 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-5 text-sm text-slate-500"
            >
              正在读取专业服务状态...
            </div>

            <div v-else-if="recentMtmCases.length" class="mt-4 space-y-3">
              <div
                v-for="item in recentMtmCases"
                :key="item.id"
                class="rounded-2xl border border-slate-100 bg-white px-4 py-3"
              >
                <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                  <div class="min-w-0">
                    <div class="flex flex-wrap items-center gap-2">
                      <p class="font-medium text-slate-900">{{ item.case_number }}</p>
                      <span
                        class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium"
                        :class="getMtmStatusBadgeClass(item.status)"
                      >
                        {{ getMtmStatusText(item.status) }}
                      </span>
                    </div>
                    <p class="mt-1 text-sm text-slate-600">
                      {{ item.service_goal || `${getMtmTriggerText(item.trigger_source)}发起的专业服务` }}
                    </p>
                    <p class="mt-1 text-xs text-slate-500">
                      {{ getMtmTriggerText(item.trigger_source) }} · {{ formatDateTime(item.created_at) }}
                    </p>
                  </div>
                  <div class="flex flex-col items-start gap-2 lg:items-end">
                    <p class="text-sm text-slate-500">
                      {{ mtmCaseProgressText(item) }}
                    </p>
                    <router-link
                      :to="`/mtm/service-cases/${item.id}`"
                      class="inline-flex items-center gap-1 text-sm font-medium text-violet-700 transition hover:text-violet-800"
                    >
                      查看详情
                      <ChevronRight class="h-4 w-4" />
                    </router-link>
                  </div>
                </div>
              </div>
            </div>

            <div
              v-else
              class="mt-4 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-5 text-sm text-slate-500"
            >
              你还没有发起过专业服务。如需更系统地梳理当前用药，可以直接在这里开始。
            </div>
          </div>
        </section>

        <section class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
          <div class="mb-5 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">常用入口</h2>
              <p class="mt-1 text-sm text-slate-500">需要时可以直接从这里进入常用页面。</p>
            </div>
            <ListChecks class="h-5 w-5 text-slate-500" />
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            <router-link
              v-for="action in quickActions"
              :key="action.title"
              :to="action.to"
              class="group rounded-2xl border border-slate-100 bg-slate-50 p-4 transition hover:border-sky-200 hover:bg-sky-50"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <div :class="['inline-flex rounded-2xl p-3', action.iconWrapperClass]">
                    <component :is="action.icon" class="h-5 w-5" :class="action.iconClass" />
                  </div>
                  <h3 class="mt-4 font-medium text-slate-900">{{ action.title }}</h3>
                  <p class="mt-2 text-sm text-slate-500">{{ action.description }}</p>
                </div>
                <ChevronRight class="h-5 w-5 text-slate-400 transition group-hover:text-sky-600" />
              </div>
            </router-link>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  Activity,
  AlertTriangle,
  Box,
  CalendarClock,
  ChevronRight,
  ClipboardList,
  HeartPulse,
  ListChecks,
  Pill,
  RefreshCw,
  ShieldAlert,
  Stethoscope,
} from 'lucide-vue-next'
import { dashboardApi } from '@/api/dashboard'
import { mtmApi } from '@/api/mtm'
import { useToast } from '@/composables/useToast'
import type {
  DashboardRiskAlert,
  DashboardRiskLevel,
  DashboardRiskType,
  DashboardSummaryData,
  DashboardTaskItem,
} from '@/types/dashboard'
import type {
  MtmServiceCase,
  MtmTriggerSource,
} from '@/types/mtm'
import { isRequestCancelledError } from '@/utils/api'
import {
  buildMtmListPresetEntries,
  buildMtmServiceCasesRoute,
  defaultMtmListOrdering,
  getMtmStatusBadgeClass,
  getMtmStatusText,
  getMtmTriggerText,
  isMtmCaseActive,
} from '@/utils/mtm'

const isDebug = import.meta.env.MODE !== 'production'
const log = (...args: unknown[]) => {
  if (isDebug) console.log(...args)
}

/**
 * 创建首页空态数据，保证页面在空数据时也能稳定渲染。
 */
const createEmptyDashboardData = (): DashboardSummaryData => ({
  today_tasks: {
    date: '',
    total: 0,
    completed: 0,
    pending: 0,
    items: [],
  },
  risk_alerts: [],
  medication_summary: {
    total_medicines: 0,
    active_reminders: 0,
    low_stock_count: 0,
    expiring_soon_count: 0,
    low_stock_items: [],
    expiring_soon_items: [],
  },
  followup_summary: {
    due_count: 0,
    upcoming_count: 0,
    next_followup: null,
    due_items: [],
    upcoming_items: [],
  },
  adherence_summary: {
    summary_7d: {
      total_records: 0,
      taken_count: 0,
      missed_count: 0,
      delayed_count: 0,
      partial_count: 0,
      completed_count: 0,
      adherence_rate: 0,
      on_time_rate: 0,
      avg_delay_minutes: 0,
      risk_level: 'low',
      risk_flags: [],
      response_summary: {
        scheduled_count: 0,
        responded_count: 0,
        unresponded_count: 0,
        response_rate: 0,
      },
    },
    summary_30d: {
      total_records: 0,
      taken_count: 0,
      missed_count: 0,
      delayed_count: 0,
      partial_count: 0,
      completed_count: 0,
      adherence_rate: 0,
      on_time_rate: 0,
      avg_delay_minutes: 0,
      risk_level: 'low',
      risk_flags: [],
      response_summary: {
        scheduled_count: 0,
        responded_count: 0,
        unresponded_count: 0,
        response_rate: 0,
      },
    },
    current_period: {
      total_records: 0,
      taken_count: 0,
      missed_count: 0,
      delayed_count: 0,
      partial_count: 0,
      completed_count: 0,
      adherence_rate: 0,
      on_time_rate: 0,
      avg_delay_minutes: 0,
      risk_level: 'low',
      risk_flags: [],
      response_summary: {
        scheduled_count: 0,
        responded_count: 0,
        unresponded_count: 0,
        response_rate: 0,
      },
    },
  },
  mtm_entry_hint: {
    recommended: false,
    reason_count: 0,
    reasons: [],
    message: '',
  },
})

const { success: showSuccess, error: showError, info: showInfo } = useToast()
const dashboard = ref<DashboardSummaryData>(createEmptyDashboardData())
const loading = ref(false)
const loadError = ref('')
const hasLoaded = ref(false)
const mtmCases = ref<MtmServiceCase[]>([])
const mtmLoading = ref(false)
const mtmCreating = ref(false)

const currentDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  })
})

const showInitialLoading = computed(() => loading.value && !hasLoaded.value)
const showInitialError = computed(() => !loading.value && !!loadError.value && !hasLoaded.value)

const welcomeDescription = computed(() => {
  if (dashboard.value.today_tasks.pending > 0) {
    return `今天还有 ${dashboard.value.today_tasks.pending} 项用药相关事项要处理，先把最重要的几件事完成。`
  }
  if (dashboard.value.risk_alerts.length > 0) {
    return '今天没有待处理任务，但有几项风险值得顺手看一眼。'
  }
  return '今天整体节奏比较稳，你可以快速检查一下近期依从性、库存和复诊安排。'
})

const visibleTasks = computed(() => dashboard.value.today_tasks.items.slice(0, 6))
const activeMtmCase = computed(
  () => mtmCases.value.find(item => isMtmCaseActive(item.status)) || null
)
const recentMtmCases = computed(() => mtmCases.value.slice(0, 3))
const suggestedTriggerSource = computed(() => buildMtmTriggerSource())
const mtmListPresetEntries = computed(() =>
  buildMtmListPresetEntries({
    activeStatus: activeMtmCase.value?.status || null,
    suggestedTriggerSource: suggestedTriggerSource.value,
  })
)
const allMtmListRoute = computed(
  () => mtmListPresetEntries.value.find(item => item.key === 'all')?.to
)
const activeMtmPresetEntry = computed(
  () => mtmListPresetEntries.value.find(item => item.key === 'active_status') || null
)
const suggestedTriggerPresetEntry = computed(
  () => mtmListPresetEntries.value.find(item => item.key === 'suggested_trigger') || null
)
const mtmShortcutPresetEntries = computed(() =>
  mtmListPresetEntries.value.filter(item => item.key !== 'all')
)

const adherenceComparisonCards = computed(() => [
  {
    title: '近 7 天完成率',
    description: `漏服 ${dashboard.value.adherence_summary.summary_7d.missed_count} 次，延迟 ${dashboard.value.adherence_summary.summary_7d.delayed_count} 次`,
    value: rateText(dashboard.value.adherence_summary.summary_7d.adherence_rate),
    rate: dashboard.value.adherence_summary.summary_7d.adherence_rate,
    barClass: 'bg-emerald-500',
  },
  {
    title: '近 30 天完成率',
    description: `按时率 ${rateText(dashboard.value.adherence_summary.summary_30d.on_time_rate)}`,
    value: rateText(dashboard.value.adherence_summary.summary_30d.adherence_rate),
    rate: dashboard.value.adherence_summary.summary_30d.adherence_rate,
    barClass: 'bg-sky-500',
  },
])

const summaryCards = computed(() => [
  {
    title: '今日待处理',
    value: dashboard.value.today_tasks.pending,
    description: `${dashboard.value.today_tasks.completed} 项已处理`,
    icon: ClipboardList,
    iconWrapperClass: 'bg-sky-100',
    iconClass: 'text-sky-700',
  },
  {
    title: '药品总数',
    value: dashboard.value.medication_summary.total_medicines,
    description: `${dashboard.value.medication_summary.active_reminders} 条活跃提醒`,
    icon: Pill,
    iconWrapperClass: 'bg-blue-100',
    iconClass: 'text-blue-700',
  },
  {
    title: '低库存药品',
    value: dashboard.value.medication_summary.low_stock_count,
    description: '建议优先处理库存不足的药品',
    icon: Box,
    iconWrapperClass: 'bg-rose-100',
    iconClass: 'text-rose-700',
  },
  {
    title: '近7天依从性',
    value: `${Math.round(dashboard.value.adherence_summary.summary_7d.adherence_rate)}%`,
    description: `按时服药率 ${Math.round(
      dashboard.value.adherence_summary.summary_7d.on_time_rate
    )}%`,
    icon: CalendarClock,
    iconWrapperClass: 'bg-emerald-100',
    iconClass: 'text-emerald-700',
  },
])

const quickActions = computed(() => [
  {
    title: '专业服务',
    description:
      activeMtmPresetEntry.value?.description ||
      suggestedTriggerPresetEntry.value?.description ||
      '查看专业服务记录，并按首页当前上下文快速筛选。',
    to:
      activeMtmPresetEntry.value?.to ||
      suggestedTriggerPresetEntry.value?.to ||
      buildMtmServiceCasesRoute({ ordering: defaultMtmListOrdering }),
    icon: Activity,
    iconWrapperClass: 'bg-violet-100',
    iconClass: 'text-violet-700',
  },
  {
    title: '药品管理',
    description: '添加药品、看库存、检查临期情况。',
    to: '/medicines',
    icon: Pill,
    iconWrapperClass: 'bg-blue-100',
    iconClass: 'text-blue-700',
  },
  {
    title: '用药提醒',
    description: '设置提醒，处理今天的待办事项。',
    to: '/reminders',
    icon: CalendarClock,
    iconWrapperClass: 'bg-amber-100',
    iconClass: 'text-amber-700',
  },
  {
    title: '用药记录',
    description: '查看最近的执行情况和补录记录。',
    to: '/records',
    icon: ClipboardList,
    iconWrapperClass: 'bg-emerald-100',
    iconClass: 'text-emerald-700',
  },
  {
    title: '就医记录',
    description: '查看复诊安排和历史就诊信息。',
    to: '/medical-records',
    icon: Stethoscope,
    iconWrapperClass: 'bg-indigo-100',
    iconClass: 'text-indigo-700',
  },
  {
    title: '统计查看',
    description: '看依从性趋势和近期用药表现。',
    to: '/records/stats',
    icon: HeartPulse,
    iconWrapperClass: 'bg-fuchsia-100',
    iconClass: 'text-fuchsia-700',
  },
  {
    title: '用药计划',
    description: '整理长期方案和需要重点关注的药。',
    to: '/plans',
    icon: Activity,
    iconWrapperClass: 'bg-violet-100',
    iconClass: 'text-violet-700',
  },
])

/**
 * 拉取首页聚合数据。
 */
const fetchDashboardSummary = async () => {
  try {
    loading.value = true
    loadError.value = ''
    log('🔵 [DashboardPage] 开始获取首页聚合数据')
    const response = await dashboardApi.getSummary()

    if (!response?.success || !response.data) {
      throw new Error(response?.message || '首页数据格式不正确')
    }

    dashboard.value = response.data
    hasLoaded.value = true
    log('🟢 [DashboardPage] 首页聚合数据获取成功', response.data)
  } catch (error) {
    if (isRequestCancelledError(error)) {
      log('🟡 [DashboardPage] 首页聚合请求已取消')
      return
    }

    console.error('🔴 [DashboardPage] 获取首页聚合数据失败', error)
    loadError.value = error instanceof Error ? error.message : '获取首页数据失败'
    showError('获取首页数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

/**
 * 拉取当前用户最近的 MTM 服务单，用于首页状态展示。
 */
const fetchMtmServiceCases = async () => {
  try {
    mtmLoading.value = true
    log('🔵 [DashboardPage] 开始获取 MTM 服务单列表')
    const payload = await mtmApi.getServiceCases({ page: 1, page_size: 3 })
    mtmCases.value = payload.results || []
    log('🟢 [DashboardPage] MTM 服务单列表获取成功', mtmCases.value)
  } catch (error) {
    if (isRequestCancelledError(error)) {
      log('🟡 [DashboardPage] MTM 服务单列表请求已取消')
      return
    }

    console.error('🔴 [DashboardPage] 获取 MTM 服务单列表失败', error)
    mtmCases.value = []
  } finally {
    mtmLoading.value = false
  }
}

/**
 * 根据首页当前上下文推断本次发起使用的触发来源。
 */
const buildMtmTriggerSource = (): MtmTriggerSource => {
  const summary7d = dashboard.value.adherence_summary.summary_7d

  if (summary7d.total_records > 0 && summary7d.adherence_rate < 70) {
    return 'adherence_alert'
  }
  if (dashboard.value.followup_summary.due_count > 0) {
    return 'followup_due'
  }
  if (dashboard.value.medication_summary.total_medicines >= 5) {
    return 'polypharmacy'
  }

  return 'self_requested'
}

/**
 * 生成本次发起 MTM 服务的最小目标描述。
 */
const buildMtmServiceGoal = () => {
  if (dashboard.value.mtm_entry_hint.recommended) {
    return '希望针对当前用药风险做一次专业梳理'
  }
  return '希望系统性梳理当前用药情况并获得专业建议'
}

/**
 * 生成本次发起 MTM 服务的备注说明。
 */
const buildMtmNotes = () => {
  if (dashboard.value.mtm_entry_hint.reasons.length > 0) {
    return `首页触发原因：${dashboard.value.mtm_entry_hint.reasons.join('；')}`
  }
  return '用户从首页手动发起专业用药指导'
}

/**
 * 从首页直接发起第一条或下一条 MTM 服务单。
 */
const handleCreateMtmService = async () => {
  if (mtmCreating.value) return

  if (activeMtmCase.value) {
    showInfo('当前已有进行中的专业服务，先看看现在的处理进度')
    return
  }

  try {
    mtmCreating.value = true
    const payload = {
      trigger_source: buildMtmTriggerSource(),
      service_goal: buildMtmServiceGoal(),
      notes: buildMtmNotes(),
    }
    log('🔵 [DashboardPage] 开始发起 MTM 服务', payload)
    const created = await mtmApi.createServiceCase(payload)
    showSuccess(`已发起专业服务，服务编号 ${created.case_number}`)
    log('🟢 [DashboardPage] MTM 服务发起成功', created)
    await Promise.all([fetchMtmServiceCases(), fetchDashboardSummary()])
  } catch (error) {
    console.error('🔴 [DashboardPage] 发起 MTM 服务失败', error)
    showError(error instanceof Error ? error.message : '发起专业服务失败，请稍后重试')
  } finally {
    mtmCreating.value = false
  }
}

/**
 * 将提醒任务状态转成人话文案。
 */
const taskStatusText = (item: DashboardTaskItem) => {
  if (!item.is_completed) return '待处理'

  switch (item.record_status) {
    case 'taken':
      return '已服药'
    case 'missed':
      return '已标记漏服'
    case 'delayed':
      return '已延迟服用'
    case 'partial':
      return '已部分服用'
    default:
      return '已处理'
  }
}

/**
 * 根据提醒任务状态返回徽标样式。
 */
const taskStatusClass = (item: DashboardTaskItem) => {
  if (!item.is_completed) {
    return 'bg-amber-100 text-amber-700'
  }

  switch (item.record_status) {
    case 'taken':
      return 'bg-emerald-100 text-emerald-700'
    case 'missed':
      return 'bg-rose-100 text-rose-700'
    case 'delayed':
      return 'bg-orange-100 text-orange-700'
    case 'partial':
      return 'bg-sky-100 text-sky-700'
    default:
      return 'bg-slate-100 text-slate-700'
  }
}

/**
 * 把进餐时机转成人话。
 */
const mealTimingText = (value: string) => {
  const mapping: Record<string, string> = {
    before_meal: '饭前',
    with_meal: '随餐',
    after_meal: '饭后',
    bedtime: '睡前',
    none: '不限',
  }
  return mapping[value] || '按时服用'
}

/**
 * 返回风险卡片背景样式。
 */
const riskCardClass = (level: DashboardRiskLevel) => {
  if (level === 'high') return 'border-rose-200 bg-rose-50'
  if (level === 'medium') return 'border-amber-200 bg-amber-50'
  return 'border-emerald-200 bg-emerald-50'
}

/**
 * 返回风险数量徽标样式。
 */
const riskBadgeClass = (level: DashboardRiskLevel) => {
  if (level === 'high') return 'bg-rose-100 text-rose-700'
  if (level === 'medium') return 'bg-amber-100 text-amber-700'
  return 'bg-emerald-100 text-emerald-700'
}

/**
 * 根据风险类型返回跳转路径。
 */
const riskTarget = (type: DashboardRiskType) => {
  const mapping: Record<DashboardRiskType, string> = {
    low_stock: '/medicines',
    expiring_soon: '/medicines',
    adherence_risk: '/records/stats',
    followup_due: '/medical-records',
  }
  return mapping[type]
}

/**
 * 根据风险类型返回动作文案。
 */
const riskActionText = (type: DashboardRiskType) => {
  const mapping: Record<DashboardRiskType, string> = {
    low_stock: '去看库存',
    expiring_soon: '去看临期药品',
    adherence_risk: '去看依从性统计',
    followup_due: '去看复诊安排',
  }
  return mapping[type]
}

/**
 * 把 MTM 服务状态转成人话文案。
 */
const formatDateTime = (value: string) => {
  return new Date(value).toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * 根据服务单判断首页应该显示“进行中”还是“已结束”。
 */
const mtmCaseProgressText = (item: MtmServiceCase) => {
  if (item.status === 'completed' && item.completed_at) {
    return `已于 ${formatDateTime(item.completed_at)} 完成`
  }
  return '当前仍在处理中'
}

/**
 * 格式化百分比显示。
 */
const rateText = (value: number) => `${Math.round(value)}%`

/**
 * 输出药品临期提示。
 */
const expiryText = (daysUntilExpiry: number | null) => {
  if (daysUntilExpiry === null) return '未填写有效期'
  if (daysUntilExpiry <= 0) return '已到期'
  return `${daysUntilExpiry} 天后到期`
}

/**
 * 输出复诊时间的人话文案。
 */
const followupText = (daysUntilFollowUp: number | null) => {
  if (daysUntilFollowUp === null) return '暂未安排复诊时间'
  if (daysUntilFollowUp < 0) return `已逾期 ${Math.abs(daysUntilFollowUp)} 天`
  if (daysUntilFollowUp === 0) return '今天需要复诊'
  return `${daysUntilFollowUp} 天后复诊`
}

onMounted(() => {
  fetchDashboardSummary()
  fetchMtmServiceCases()
})
</script>
