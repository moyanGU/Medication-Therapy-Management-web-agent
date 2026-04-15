import type {
  MtmListPresetEntry,
  MtmListQuickAction,
  MtmListPresetSource,
  MtmServiceCaseOrdering,
  MtmServiceCaseTransitionAction,
  MtmServiceStatus,
  MtmTriggerSource,
} from '@/types/mtm'
import type { RouteLocationRaw } from 'vue-router'

export const defaultMtmListOrdering: MtmServiceCaseOrdering = '-created_at'
export const mtmListPresetSources: MtmListPresetSource[] = [
  'all',
  'active_status',
  'suggested_trigger',
]

export const mtmTriggerSources: MtmTriggerSource[] = [
  'manual',
  'self_requested',
  'adherence_alert',
  'followup_due',
  'polypharmacy',
  'referral',
]

export const mtmServiceCaseOrderings: MtmServiceCaseOrdering[] = [
  '-created_at',
  'created_at',
  '-started_at',
  'started_at',
  '-completed_at',
  'completed_at',
]

/**
 * 把 MTM 服务状态转成人话文案。
 */
export const getMtmStatusText = (status: MtmServiceStatus) => {
  const mapping: Record<MtmServiceStatus, string> = {
    pending: '待开始',
    interviewing: '问诊中',
    assessing: '评估中',
    intervening: '干预中',
    following_up: '随访中',
    completed: '已完成',
  }
  return mapping[status]
}

/**
 * 返回 MTM 状态徽标样式。
 */
export const getMtmStatusBadgeClass = (status: MtmServiceStatus) => {
  const mapping: Record<MtmServiceStatus, string> = {
    pending: 'bg-slate-100 text-slate-700',
    interviewing: 'bg-sky-100 text-sky-700',
    assessing: 'bg-amber-100 text-amber-700',
    intervening: 'bg-violet-100 text-violet-700',
    following_up: 'bg-indigo-100 text-indigo-700',
    completed: 'bg-emerald-100 text-emerald-700',
  }
  return mapping[status]
}

/**
 * 把 MTM 触发来源转成人话文案。
 */
export const getMtmTriggerText = (triggerSource: MtmTriggerSource) => {
  const mapping: Record<MtmTriggerSource, string> = {
    manual: '手动发起',
    self_requested: '主动申请',
    adherence_alert: '依从性预警',
    followup_due: '复诊到期',
    polypharmacy: '多重用药',
    referral: '转介',
  }
  return mapping[triggerSource]
}

/**
 * 判断当前 MTM 服务是否仍处于进行中。
 */
export const isMtmCaseActive = (status: MtmServiceStatus) => status !== 'completed'

/**
 * 返回当前状态下可执行的最小前端推进动作。
 */
export const getMtmTransitionActions = (
  status: MtmServiceStatus
): MtmServiceCaseTransitionAction[] => {
  const mapping: Record<MtmServiceStatus, MtmServiceCaseTransitionAction[]> = {
    pending: [
      {
        targetStatus: 'interviewing',
        label: '进入问诊',
        description: '开始第一轮问诊信息收集',
        variant: 'primary',
      },
    ],
    interviewing: [
      {
        targetStatus: 'assessing',
        label: '进入评估',
        description: '转入评估阶段，整理风险与问题',
        variant: 'primary',
      },
    ],
    assessing: [
      {
        targetStatus: 'intervening',
        label: '进入干预',
        description: '开始输出干预建议和处理计划',
        variant: 'primary',
      },
    ],
    intervening: [
      {
        targetStatus: 'following_up',
        label: '进入随访',
        description: '当前干预已完成，开始后续跟进',
        variant: 'primary',
      },
      {
        targetStatus: 'completed',
        label: '直接完成',
        description: '本次服务已结束，可以直接归档完成',
        variant: 'secondary',
      },
    ],
    following_up: [
      {
        targetStatus: 'completed',
        label: '完成本次服务',
        description: '结束本次随访并完成服务单',
        variant: 'primary',
      },
    ],
    completed: [],
  }

  return mapping[status]
}

/**
 * 生成最小状态流转备注，便于后端和日志追踪。
 */
export const buildMtmTransitionNote = (
  fromStatus: MtmServiceStatus,
  targetStatus: MtmServiceStatus
) => {
  return `前端最小状态推进：${getMtmStatusText(fromStatus)} -> ${getMtmStatusText(targetStatus)}`
}

/**
 * 判断触发来源是否属于当前 MTM 最小来源集合。
 */
export const isValidMtmTriggerSource = (
  value: string
): value is MtmTriggerSource => {
  return mtmTriggerSources.includes(value as MtmTriggerSource)
}

/**
 * 判断排序值是否属于当前 MTM 列表允许的最小排序集合。
 */
export const isValidMtmServiceCaseOrdering = (
  value: string
): value is MtmServiceCaseOrdering => {
  return mtmServiceCaseOrderings.includes(value as MtmServiceCaseOrdering)
}

/**
 * 把 MTM 列表排序值转成人话文案。
 */
export const getMtmServiceCaseOrderingText = (
  ordering: MtmServiceCaseOrdering
) => {
  const mapping: Record<MtmServiceCaseOrdering, string> = {
    '-created_at': '最新创建优先',
    created_at: '最早创建优先',
    '-started_at': '最近启动优先',
    started_at: '最早启动优先',
    '-completed_at': '最近完成优先',
    completed_at: '最早完成优先',
  }
  return mapping[ordering]
}

/**
 * 构造 MTM 列表页路由，统一首页与列表页入口的 query 口径。
 */
export const buildMtmServiceCasesRoute = (options?: {
  status?: MtmServiceStatus
  triggerSource?: MtmTriggerSource
  ordering?: MtmServiceCaseOrdering
  presetSource?: MtmListPresetSource
}): RouteLocationRaw => {
  const ordering = options?.ordering || defaultMtmListOrdering
  const query: Record<string, string> = {}

  if (options?.status) {
    query.status = options.status
  }
  if (options?.triggerSource) {
    query.trigger_source = options.triggerSource
  }
  if (ordering !== defaultMtmListOrdering || !options?.status && !options?.triggerSource) {
    query.ordering = ordering
  }
  if (options?.presetSource) {
    query.preset_source = options.presetSource
  }

  return {
    path: '/mtm/service-cases',
    query,
  }
}

/**
 * 为首页生成统一的 MTM 列表快捷预设入口。
 */
export const buildMtmListPresetEntries = (options: {
  activeStatus?: MtmServiceStatus | null
  suggestedTriggerSource?: MtmTriggerSource
}): MtmListPresetEntry[] => {
  const entries: MtmListPresetEntry[] = [
    {
      key: 'all',
      title: '专业服务列表',
      shortLabel: '查看全部',
      description: '查看全部专业服务记录，默认按最近创建优先。',
      to: buildMtmServiceCasesRoute({
        presetSource: 'all',
      }),
    },
  ]

  if (options.activeStatus) {
    entries.push({
      key: 'active_status',
      title: `${getMtmStatusText(options.activeStatus)}阶段服务`,
      shortLabel: `看${getMtmStatusText(options.activeStatus)}阶段服务`,
      description: `直接查看当前处于${getMtmStatusText(options.activeStatus)}阶段的专业服务。`,
      to: buildMtmServiceCasesRoute({
        status: options.activeStatus,
        presetSource: 'active_status',
      }),
    })
  }

  entries.push({
    key: 'suggested_trigger',
    title: `${getMtmTriggerText(options.suggestedTriggerSource)}相关服务`,
    shortLabel: `看${getMtmTriggerText(options.suggestedTriggerSource)}相关服务`,
    description: `按当前首页建议原因，快速查看同类触发来源的历史服务。`,
    to: buildMtmServiceCasesRoute({
      triggerSource: options.suggestedTriggerSource,
      presetSource: 'suggested_trigger',
    }),
  })

  return entries
}

/**
 * 判断预设来源标识是否属于当前 MTM 列表允许的来源集合。
 */
export const isValidMtmListPresetSource = (
  value: string
): value is MtmListPresetSource => {
  return mtmListPresetSources.includes(value as MtmListPresetSource)
}

/**
 * 输出 MTM 列表预设来源的人话标题。
 */
export const getMtmListPresetSourceTitle = (
  source: MtmListPresetSource,
  options?: {
    status?: MtmServiceStatus | ''
    triggerSource?: MtmTriggerSource | ''
  }
) => {
  if (source === 'all') {
    return '来自首页“查看全部”'
  }
  if (source === 'active_status') {
    return options?.status
      ? `来自首页“看${getMtmStatusText(options.status)}阶段服务”`
      : '来自首页“当前阶段服务”'
  }
  return options?.triggerSource
    ? `来自首页“看${getMtmTriggerText(options.triggerSource)}相关服务”`
    : '来自首页“同类触发服务”'
}

/**
 * 输出 MTM 列表预设来源的人话说明。
 */
export const getMtmListPresetSourceDescription = (
  source: MtmListPresetSource,
  options?: {
    status?: MtmServiceStatus | ''
    triggerSource?: MtmTriggerSource | ''
  }
) => {
  if (source === 'all') {
    return '当前结果按最近创建优先展示全部专业服务记录。'
  }
  if (source === 'active_status') {
    return options?.status
      ? `你当前正在查看首页推荐的${getMtmStatusText(options.status)}阶段服务。`
      : '你当前正在查看首页推荐的当前阶段服务。'
  }
  return options?.triggerSource
    ? `你当前正在查看与“${getMtmTriggerText(options.triggerSource)}”同类触发来源的服务记录。`
    : '你当前正在查看首页推荐的同类触发服务记录。'
}

/**
 * 输出 MTM 列表页预设来源标签信息。
 */
export const getMtmListPresetSourceBadge = (
  source?: MtmListPresetSource | ''
) => {
  if (source === 'all') {
    return {
      label: '首页查看全部',
      className: 'bg-slate-100 text-slate-700',
    }
  }
  if (source === 'active_status') {
    return {
      label: '首页当前阶段',
      className: 'bg-violet-100 text-violet-700',
    }
  }
  if (source === 'suggested_trigger') {
    return {
      label: '首页同类触发',
      className: 'bg-sky-100 text-sky-700',
    }
  }
  return {
    label: '当前列表视图',
    className: 'bg-slate-100 text-slate-700',
  }
}

/**
 * 生成 MTM 列表页结果摘要说明。
 */
export const buildMtmListResultSummary = (options: {
  count: number
  presetSource?: MtmListPresetSource | ''
  hasFilters?: boolean
}) => {
  if (options.presetSource) {
    return `当前共 ${options.count} 条服务记录，已按首页预设为你准备好对应结果。`
  }

  if (options.hasFilters) {
    return `当前筛选结果共 ${options.count} 条，方便你继续查看目标服务单。`
  }

  return `当前共 ${options.count} 条服务记录，包含进行中与已完成服务。`
}

/**
 * 生成“刷新列表”动作，统一不同场景下的刷新文案。
 */
const buildMtmRefreshAction = (options?: {
  label?: string
  description?: string
  variant?: 'primary' | 'secondary'
}): MtmListQuickAction => {
  return {
    key: 'refresh',
    label: options?.label || '刷新列表',
    description: options?.description || '重新加载当前列表和摘要结果。',
    action: 'refresh',
    variant: options?.variant || 'primary',
  }
}

/**
 * 生成“重置列表”动作，复用现有清空筛选行为。
 */
const buildMtmResetListAction = (options?: {
  label?: string
  description?: string
  variant?: 'primary' | 'secondary'
}): MtmListQuickAction => {
  return {
    key: 'clear_filters',
    label: options?.label || '清空筛选',
    description: options?.description || '去掉当前搜索和筛选条件，重新看完整结果。',
    action: 'clear_filters',
    variant: options?.variant || 'primary',
  }
}

/**
 * 生成“查看全部服务”动作，统一首页预设场景的回退入口。
 */
const buildMtmViewAllAction = (options?: {
  label?: string
  description?: string
  variant?: 'primary' | 'secondary'
}): MtmListQuickAction => {
  return {
    key: 'view_all',
    label: options?.label || '看全部服务',
    description:
      options?.description || '切回完整专业服务列表，继续按最近创建优先查看。',
    to: buildMtmServiceCasesRoute(),
    variant: options?.variant || 'primary',
  }
}

/**
 * 生成“回首页查看”动作，统一列表页返回首页的表述。
 */
const buildMtmBackDashboardAction = (options?: {
  label?: string
  description?: string
  variant?: 'primary' | 'secondary'
}): MtmListQuickAction => {
  return {
    key: 'back_dashboard',
    label: options?.label || '回首页查看',
    description:
      options?.description || '返回首页继续查看其他快捷入口和提醒信息。',
    to: '/dashboard',
    variant: options?.variant || 'secondary',
  }
}

/**
 * 生成 MTM 列表页的统一快捷动作。
 */
export const buildMtmListQuickActions = (options: {
  presetSource?: MtmListPresetSource | ''
  hasSearchFilters?: boolean
  hasOrderingChanged?: boolean
}): MtmListQuickAction[] => {
  if (options.presetSource === 'all') {
    return [
      buildMtmRefreshAction({
        label: '刷新全部列表',
        description: '重新加载全部专业服务记录，继续按当前列表查看。',
        variant: 'primary',
      }),
      buildMtmBackDashboardAction({
        label: '回首页查看',
        description: '返回首页继续查看专业服务入口、提醒和快捷操作。',
        variant: 'secondary',
      }),
    ]
  }

  if (options.presetSource === 'active_status') {
    return [
      buildMtmViewAllAction({
        label: '改看全部服务',
        description: '放宽到全部专业服务记录，继续确认还有哪些服务可看。',
        variant: 'primary',
      }),
      buildMtmBackDashboardAction({
        label: '回首页查看',
        description: '返回首页继续查看当前阶段推荐和其他常用入口。',
        variant: 'secondary',
      }),
    ]
  }

  if (options.presetSource === 'suggested_trigger') {
    return [
      buildMtmBackDashboardAction({
        label: '回首页看建议',
        description: '先回首页重新看当前建议原因，再决定要不要继续放宽查看范围。',
        variant: 'primary',
      }),
      buildMtmViewAllAction({
        label: '改看全部服务',
        description: '如果不只想看当前触发来源，可以切回完整专业服务列表。',
        variant: 'secondary',
      }),
    ]
  }

  if (options.hasSearchFilters && options.hasOrderingChanged) {
    return [
      buildMtmResetListAction({
        label: '恢复默认列表',
        description: '清空当前搜索筛选并恢复默认排序，重新看完整服务列表。',
        variant: 'primary',
      }),
      buildMtmRefreshAction({
        label: '刷新当前结果',
        description: '按你现在的条件重新加载列表结果。',
        variant: 'secondary',
      }),
    ]
  }

  if (options.hasSearchFilters) {
    return [
      buildMtmResetListAction({
        label: '清空筛选',
        description: '去掉当前搜索和筛选条件，重新看完整结果。',
        variant: 'primary',
      }),
      buildMtmRefreshAction({
        label: '刷新当前结果',
        description: '按你现在的筛选条件重新加载列表结果。',
        variant: 'secondary',
      }),
    ]
  }

  if (options.hasOrderingChanged) {
    return [
      buildMtmResetListAction({
        label: '恢复默认排序',
        description: '回到默认的最近创建优先排序，继续查看完整列表。',
        variant: 'primary',
      }),
      buildMtmRefreshAction({
        label: '按当前排序刷新',
        description: '按你现在选择的排序方式重新加载列表结果。',
        variant: 'secondary',
      }),
    ]
  }

  return [
    buildMtmRefreshAction({
      label: '刷新列表',
      description: '重新加载当前专业服务列表，确认最新进度和统计结果。',
      variant: 'primary',
    }),
    buildMtmBackDashboardAction({
      label: '回首页查看',
      description: '返回首页继续查看其他快捷入口和提醒信息。',
      variant: 'secondary',
    }),
  ]
}

/**
 * 生成 MTM 列表页当前条件的人话摘要。
 */
export const buildMtmListFilterSummary = (options: {
  search?: string
  status?: MtmServiceStatus | ''
  triggerSource?: MtmTriggerSource | ''
  ordering?: MtmServiceCaseOrdering
}) => {
  const summary: string[] = []

  if (options.search?.trim()) {
    summary.push(`搜索“${options.search.trim()}”`)
  }
  if (options.status) {
    summary.push(`状态为${getMtmStatusText(options.status)}`)
  }
  if (options.triggerSource) {
    summary.push(`来源为${getMtmTriggerText(options.triggerSource)}`)
  }
  if (options.ordering) {
    summary.push(`当前按${getMtmServiceCaseOrderingText(options.ordering)}查看`)
  }

  return summary
}

/**
 * 生成 MTM 列表页空态标题与说明。
 */
export const getMtmListEmptyStateCopy = (options: {
  presetSource?: MtmListPresetSource | ''
  search?: string
  status?: MtmServiceStatus | ''
  triggerSource?: MtmTriggerSource | ''
  ordering?: MtmServiceCaseOrdering
}) => {
  const search = options.search?.trim() || ''

  if (options.presetSource === 'active_status') {
    return {
      title: options.status
        ? `${getMtmStatusText(options.status)}阶段暂时没有服务`
        : '当前阶段暂时没有服务',
      description: options.status
        ? `首页推荐你查看${getMtmStatusText(options.status)}阶段服务，但当前还没有匹配记录。可以改看全部服务或切换筛选。`
        : '首页推荐的当前阶段服务暂时没有匹配记录，可以改看全部服务或切换筛选。',
    }
  }

  if (options.presetSource === 'suggested_trigger') {
    return {
      title: options.triggerSource
        ? `${getMtmTriggerText(options.triggerSource)}相关服务暂时为空`
        : '同类触发服务暂时为空',
      description: options.triggerSource
        ? `当前首页建议你查看“${getMtmTriggerText(options.triggerSource)}”相关服务，但现在还没有匹配记录。可以切换来源或返回首页查看。`
        : '当前首页建议来源下还没有匹配服务，可以切换筛选或返回首页查看。',
    }
  }

  if (search) {
    return {
      title: `没有找到“${search}”相关服务`,
      description: '可以试着简化搜索词，或清空其他筛选条件后再看看。',
    }
  }

  if (options.status || options.triggerSource) {
    return {
      title: '当前条件下没有匹配服务',
      description: buildMtmListFilterSummary({
        status: options.status,
        triggerSource: options.triggerSource,
        ordering: options.ordering,
      }).join('，'),
    }
  }

  return {
    title: '当前还没有专业服务记录',
    description: '你可以先回到首页发起一次专业服务，之后这里会显示完整历史。',
  }
}
