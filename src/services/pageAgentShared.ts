export type PageAgentMode = 'medication' | 'page-agent'

export interface PageAgentTaskResult {
  success: boolean
  answer: string
  steps: string[]
  proposal?: PageAgentActionProposal | null
}

export type PageAgentPageKey =
  | 'dashboard'
  | 'medicines'
  | 'reminders'
  | 'reminder-form'
  | 'medical-records'
  | 'medical-record-form'
  | 'unknown'

type PageAgentActionType =
  | 'navigate'
  | 'reminder-draft'
  | 'medical-record-draft'
  | 'medicine-draft'

export interface PageAgentActionProposal {
  type: PageAgentActionType
  targetPath: string
  targetLabel: string
  reason: string
  buttonLabel: string
  query?: Record<string, string>
  summary?: string[]
}

const READ_ONLY_ROUTE_PATTERNS = [
  /^\/dashboard(?:\/|$)/,
  /^\/medicines(?:\/|$)/,
  /^\/reminders(?:\/|$)/,
  /^\/medical-records(?:\/|$)/,
]

/**
 * 判断当前路由是否允许执行只读页面分析。
 */
export function canUsePageAgentOnCurrentPage(pathname: string): boolean {
  return READ_ONLY_ROUTE_PATTERNS.some((pattern) => pattern.test(pathname))
}

/**
 * 识别当前页面对应的业务分区。
 */
export function getCurrentPageKey(
  pathname: string = window.location.pathname
): PageAgentPageKey {
  if (/^\/reminders\/(?:create|\d+\/edit)(?:\/|$)/.test(pathname)) {
    return 'reminder-form'
  }
  if (/^\/dashboard(?:\/|$)/.test(pathname)) {
    return 'dashboard'
  }
  if (/^\/medicines(?:\/|$)/.test(pathname)) {
    return 'medicines'
  }
  if (/^\/reminders(?:\/|$)/.test(pathname)) {
    return 'reminders'
  }
  if (/^\/medical-records\/(?:create|\d+\/edit)(?:\/|$)/.test(pathname)) {
    return 'medical-record-form'
  }
  if (/^\/medical-records(?:\/|$)/.test(pathname)) {
    return 'medical-records'
  }
  return 'unknown'
}

/**
 * 生成当前页面的业务上下文描述。
 */
export function getCurrentPageAgentScopeDescription(): string {
  const pageKey = getCurrentPageKey()
  if (pageKey === 'reminder-form') {
    return '提醒表单页：可帮助梳理必填项、整理提醒草稿并预填待确认内容。'
  }
  if (pageKey === 'reminders') {
    return '提醒页：可总结提醒状态、频率、风险项与待处理问题。'
  }
  if (pageKey === 'medicines') {
    return '药品页：可总结药品列表、缺失项与风险提示，也可整理新增药品草稿。'
  }
  if (pageKey === 'dashboard') {
    return '仪表板页：可总结概览卡片、趋势信息与异常提醒。'
  }
  if (pageKey === 'medical-record-form') {
    return '病历表单页：可帮助识别必填项、整理病历草稿并预填待确认内容。'
  }
  if (pageKey === 'medical-records') {
    return '病历列表页：可总结就医记录、风险项、复诊线索与待补全信息。'
  }
  return '当前页面暂未开放页面助手。'
}

/**
 * 页面助手示例问题，根据当前页面范围动态返回。
 */
export function getPageAgentQuickActions(): string[] {
  const pathname = window.location.pathname

  if (/^\/reminders(?:\/|$)/.test(pathname)) {
    return [
      /^\/reminders\/(?:create|\d+\/edit)(?:\/|$)/.test(pathname)
        ? '帮我把这个提醒表单还缺的必填项说清楚'
        : '总结当前提醒页的异常状态和待处理项',
      /^\/reminders\/(?:create|\d+\/edit)(?:\/|$)/.test(pathname)
        ? '帮我生成一个二甲双胍每天早晚饭后各1片的提醒草稿'
        : '根据当前提醒列表给出风险优先级建议',
      /^\/reminders\/(?:create|\d+\/edit)(?:\/|$)/.test(pathname)
        ? '告诉我这个提醒表单还差哪些内容'
        : '解释这个页面上最值得关注的提醒信息',
    ]
  }

  if (/^\/medicines(?:\/|$)/.test(pathname)) {
    return [
      '帮我生成一个阿司匹林30片的药品草稿',
      '总结当前药品页的关键信息和缺失项',
      '指出这个药品页面里最需要补全的字段',
    ]
  }

  if (/^\/medical-records(?:\/|$)/.test(pathname)) {
    return /^\/medical-records\/(?:create|\d+\/edit)(?:\/|$)/.test(pathname)
      ? [
          '帮我把这个病历表单还缺的必填项说清楚',
          '帮我生成一份昨天去人民医院复诊的病历草稿',
          '告诉我这个病历表单还差哪些内容',
        ]
      : [
          '总结当前病历页最值得关注的信息',
          '指出当前病历记录里最需要补全的字段',
          '根据当前病历内容给出复诊和整理建议',
        ]
  }

  return [
    '总结当前页面最重要的信息',
    '指出当前页面里最值得关注的异常状态',
    '根据当前页面内容给出下一步建议',
  ]
}
