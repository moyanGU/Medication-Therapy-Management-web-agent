import {
  PageAgentCore,
  type ExecutionResult,
  type HistoricalEvent,
  type PageAgentCoreConfig,
  tool,
} from '@page-agent/core'
import { PageController } from '@page-agent/page-controller'
import { z } from 'zod/v4'
import {
  buildMedicineDraftPayload,
  buildReminderDraftPayload,
} from '@/services/pageAgentDraftParser'
import { resolveApiBaseURL } from '@/utils/api'

export type PageAgentMode = 'medication' | 'page-agent'

export interface PageAgentTaskResult {
  success: boolean
  answer: string
  steps: string[]
  proposal?: PageAgentActionProposal | null
}

type PageAgentPageKey =
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
const CONTROLLED_NAVIGATION_TARGETS = [
  {
    matcher: /(仪表板|总览|首页|概览)/,
    path: '/dashboard',
    label: '仪表板',
  },
  {
    matcher: /(药品页|药品列表|药品管理)/,
    path: '/medicines',
    label: '药品页',
  },
  {
    matcher: /(提醒页|提醒列表|提醒管理)/,
    path: '/reminders',
    label: '提醒页',
  },
  {
    matcher: /(提醒创建页|提醒表单)/,
    path: '/reminders/create',
    label: '提醒创建页',
  },
  {
    matcher: /(病历页|病历列表|就医记录|病历管理)/,
    path: '/medical-records',
    label: '病历列表页',
  },
  {
    matcher: /(新增病历页|病历创建页|病历表单|就医记录表单)/,
    path: '/medical-records/create',
    label: '新增病历页',
  },
] as const
const NAVIGATION_TRIGGER = /(打开|进入|跳转|前往|去|带我去|切换到|导航到|查看)/

let pageAgentInstance: PageAgentCore | null = null

/**
 * 解析 Page Agent 使用的后端代理地址。
 */
function resolvePageAgentProxyBaseURL(): string {
  const fromEnv = import.meta.env.VITE_API_BASE_URL?.trim()
  if (fromEnv) {
    return `${fromEnv.replace(/\/+$/, '')}/ai/page-agent`
  }
  const apiBase = resolveApiBaseURL().replace(/\/+$/, '')
  if (apiBase.endsWith('/api')) {
    return `${apiBase}/ai/page-agent`
  }
  return `${apiBase}/api/ai/page-agent`
}

/**
 * 判断当前路由是否允许执行只读页面分析。
 */
export function canUsePageAgentOnCurrentPage(pathname: string): boolean {
  return READ_ONLY_ROUTE_PATTERNS.some((pattern) => pattern.test(pathname))
}

/**
 * 识别当前页面对应的业务分区。
 */
function getCurrentPageKey(pathname: string = window.location.pathname): PageAgentPageKey {
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
 * 为页面助手构造认证请求函数，统一透传登录令牌。
 */
function createAuthenticatedFetch(): typeof fetch {
  return async (input, init) => {
    const headers = new Headers(init?.headers)
    const token =
      window.localStorage.getItem('access_token') ||
      window.localStorage.getItem('token')

    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }

    return fetch(input, {
      ...init,
      headers,
      credentials: 'same-origin',
    })
  }
}

/**
 * 生成面向 mtm-helper 的页面级指令。
 */
function getPageInstructions(url: string): string {
  const scope = getCurrentPageAgentScopeDescription()
  const pageKey = getCurrentPageKey()
  const routeSpecificInstructions: Record<PageAgentPageKey, string> = {
    dashboard:
      '当前为仪表板。优先关注概览卡片、今日提醒数量、药品总数、库存风险和导航卡片中最值得进入的模块。',
    reminders:
      '当前为提醒页。优先关注待确认事项、今日提醒、响应率、待发送数量、活跃提醒与停用提醒，不要忽略高风险未响应项。',
    'reminder-form':
      '当前为提醒表单页。可以识别用户想填写的提醒草稿，帮助补齐药品、剂量、频率、时间和开始日期，但不要自动提交。',
    medicines:
      '当前为药品页。优先关注已过期、即将过期、库存不足、药品列表缺失项以及搜索筛选后的可见结果。若用户要新增药品，可整理待确认草稿并打开新增表单，但不要自动保存。',
    'medical-records':
      '当前为病历列表页。优先关注最近就诊、复诊计划、缺失信息和高风险记录，也可以帮助整理新增病历草稿。',
    'medical-record-form':
      '当前为病历表单页。可以帮助识别必填项，并根据用户描述整理就诊日期、医院、就诊类型、状态和紧急程度等草稿，但不要自动提交。',
    unknown: '当前页无专属业务说明，请仅基于可见信息给出保守分析。',
  }
  return [
    '你正在 mtm-helper 中工作。',
    '你的职责是根据当前页面内容给出保守分析结果。',
    '禁止要求用户执行危险操作，禁止编造页面中不存在的信息。',
    '除提醒表单页、病历表单页和药品页新增表单场景外，不要点击、填写、提交或跳转。',
    '在提醒表单页、病历表单页和药品页新增表单场景，你可以整理待确认草稿并引导用户应用预填内容，但绝不能自动提交。',
    '优先总结页面上的关键信息、异常状态、缺失项、必填项与下一步建议。',
    '如果存在业务专用工具，优先调用对应工具再给出结论。',
    `当前页面标题：${document.title || '未知页面'}`,
    `当前页面地址：${url}`,
    `当前页面范围：${scope}`,
    `页面专项要求：${routeSpecificInstructions[pageKey]}`,
  ].join('\n')
}

/**
 * 判断元素是否对用户可见。
 */
function isElementVisible(element: Element | null): element is HTMLElement {
  if (!(element instanceof HTMLElement)) {
    return false
  }
  const style = window.getComputedStyle(element)
  if (style.display === 'none' || style.visibility === 'hidden') {
    return false
  }
  return Boolean(element.offsetWidth || element.offsetHeight || element.getClientRects().length)
}

/**
 * 清洗节点文本，避免输出过长噪音。
 */
function normalizeText(text: string, maxLength = 120): string {
  const normalized = text.replace(/\s+/g, ' ').trim()
  if (!normalized) {
    return ''
  }
  return normalized.length > maxLength
    ? `${normalized.slice(0, maxLength).trim()}...`
    : normalized
}

/**
 * 采集页面中符合条件的可见文本。
 */
function collectVisibleTexts(selector: string, limit = 6, maxLength = 120): string[] {
  const values = Array.from(document.querySelectorAll(selector))
    .filter(isElementVisible)
    .map((element) => normalizeText(element.textContent || '', maxLength))
    .filter(Boolean)

  return Array.from(new Set(values)).slice(0, limit)
}

/**
 * 从常见卡片布局中提取标签和值。
 */
function collectMetricPairs(limit = 8): Array<{ label: string; value: string }> {
  const pairs: Array<{ label: string; value: string }> = []
  const candidates = Array.from(document.querySelectorAll('div, section, article'))

  for (const candidate of candidates) {
    if (!isElementVisible(candidate)) {
      continue
    }

    const children = Array.from(candidate.children).filter(isElementVisible)
    if (children.length < 2 || children.length > 6) {
      continue
    }

    const texts = children
      .map((child) => normalizeText(child.textContent || '', 80))
      .filter(Boolean)

    if (texts.length < 2) {
      continue
    }

    const maybeValue = texts[0]
    const maybeLabel = texts[1]

    const valueLooksNumeric = /[\d%]+/.test(maybeValue)
    const labelLooksShort = maybeLabel.length <= 24

    if (valueLooksNumeric && labelLooksShort) {
      pairs.push({ label: maybeLabel, value: maybeValue })
    }

    if (pairs.length >= limit) {
      break
    }
  }

  return pairs
}

/**
 * 提取可见表格前几行，便于页面助手判断列表信息。
 */
function collectTablePreview(rowLimit = 4, columnLimit = 4): string[] {
  const rows = Array.from(document.querySelectorAll('table tr'))
    .filter(isElementVisible)
    .slice(0, rowLimit)

  return rows
    .map((row) => {
      const cells = Array.from(row.querySelectorAll('th, td'))
        .filter(isElementVisible)
        .slice(0, columnLimit)
        .map((cell) => normalizeText(cell.textContent || '', 48))
        .filter(Boolean)
      return cells.join(' | ')
    })
    .filter(Boolean)
}

/**
 * 提取卡片、列表项等可见块文本，用于快速理解页面主体内容。
 */
function collectBlockPreview(limit = 6): string[] {
  const selectors = [
    '[class*="rounded"]',
    '[class*="card"]',
    '[class*="item"]',
    'li',
    '[role="listitem"]',
  ]

  const blocks = selectors.flatMap((selector) =>
    collectVisibleTexts(selector, limit, 140)
  )

  return Array.from(new Set(blocks)).slice(0, limit)
}

/**
 * 提取页面中的风险信号关键词，帮助模型优先关注异常。
 */
function collectAttentionSignals(limit = 10): string[] {
  const keywords = [
    '待确认',
    '未响应',
    '待发送',
    '已过期',
    '即将过期',
    '库存不足',
    '停用',
    '失败',
    '响应率',
    '延迟',
  ]

  const pageText = normalizeText(document.body?.innerText || '', 20000)
  return keywords.filter((keyword) => pageText.includes(keyword)).slice(0, limit)
}

/**
 * 生成通用页面结构摘要。
 */
function buildCommonPageSnapshot() {
  return {
    page_key: getCurrentPageKey(),
    title: document.title,
    pathname: window.location.pathname,
    scope: getCurrentPageAgentScopeDescription(),
    headings: collectVisibleTexts('h1, h2, h3', 8, 80),
    metrics: collectMetricPairs(),
    table_preview: collectTablePreview(),
    block_preview: collectBlockPreview(),
    attention_signals: collectAttentionSignals(),
  }
}

/**
 * 生成提醒页业务摘要。
 */
function buildReminderSnapshot() {
  return {
    ...buildCommonPageSnapshot(),
    sections: collectVisibleTexts('button, .text-sm, .text-lg, .text-xs', 16, 80).filter(
      (text) =>
        /(今日提醒|待确认|活跃提醒|停用提醒|响应率|总记录|已发送|待发送|平均延迟|提醒时间|状态)/.test(
          text
        )
    ),
    actions: collectVisibleTexts('button', 12, 40),
  }
}

/**
 * 生成药品页业务摘要。
 */
function buildMedicineSnapshot() {
  return {
    ...buildCommonPageSnapshot(),
    sections: collectVisibleTexts('label, th, td, .text-sm, .text-lg', 20, 80).filter(
      (text) =>
        /(药品管理|总药品数|已过期|即将过期|库存不足|搜索药品|生产厂商|药品类型|当前库存|批号|有效期|药品描述)/.test(
          text
        )
    ),
    actions: collectVisibleTexts('button', 10, 40),
  }
}

/**
 * 生成仪表板业务摘要。
 */
function buildDashboardSnapshot() {
  return {
    ...buildCommonPageSnapshot(),
    sections: collectVisibleTexts('p, a, h1, h2, h3', 18, 80).filter((text) =>
      /(药品总数|今日提醒|库存预警|用药计划|药品管理|提醒管理|就医记录|统计分析)/.test(text)
    ),
    navigation: collectVisibleTexts('a', 12, 80),
  }
}

function isReminderFormPath(pathname: string) {
  return /^\/reminders\/(?:create|\d+\/edit)(?:\/|$)/.test(pathname)
}

function isMedicalRecordFormPath(pathname: string) {
  return /^\/medical-records\/(?:create|\d+\/edit)(?:\/|$)/.test(pathname)
}

function normalizeDateString(raw: string): string {
  const trimmed = raw.trim()
  if (!trimmed) {
    return ''
  }

  if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
    return trimmed
  }

  const match = trimmed.match(/^(\d{4})[年/.-](\d{1,2})[月/.-](\d{1,2})日?$/)
  if (!match) {
    return ''
  }

  const [, year, month, day] = match
  return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
}

function offsetDate(baseDate: string, offsetDays: number): string {
  const next = new Date(`${baseDate}T00:00:00`)
  next.setDate(next.getDate() + offsetDays)
  const year = next.getFullYear()
  const month = String(next.getMonth() + 1).padStart(2, '0')
  const day = String(next.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function resolveRelativeDate(raw: string, today: string): string {
  if (!raw) {
    return ''
  }

  if (raw === '今天' || raw === '今日') {
    return today
  }
  if (raw === '昨天') {
    return offsetDate(today, -1)
  }
  if (raw === '前天') {
    return offsetDate(today, -2)
  }
  if (raw === '明天') {
    return offsetDate(today, 1)
  }
  if (raw === '后天') {
    return offsetDate(today, 2)
  }

  return normalizeDateString(raw)
}

function normalizeTimeString(raw: string): string {
  const match = raw.match(/(\d{1,2})(?:[:：点时](\d{1,2}))?/)
  if (!match) {
    return ''
  }

  const hour = Number(match[1])
  const minute = Number(match[2] ?? 0)
  if (!Number.isInteger(hour) || hour < 0 || hour > 23) {
    return ''
  }
  if (!Number.isInteger(minute) || minute < 0 || minute > 59) {
    return ''
  }

  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
}

function parseMedicalRecordDraftPayload(task: string, today: string) {
  const normalized = task.replace(/\s+/g, ' ').trim()
  if (
    !/(病历|就诊|看病|复诊|门诊|急诊|住院|体检|医院)/.test(normalized) ||
    !/(创建|新建|新增|记录|填写|填好|整理|准备|帮我填|帮我写|代填)/.test(normalized)
  ) {
    return null
  }

  const query: Record<string, string> = {
    source: 'page-agent',
  }
  const summary: string[] = []

  const dateMatch = normalized.match(
    /(今天|今日|昨天|前天|明天|后天|\d{4}[年/.-]\d{1,2}[月/.-]\d{1,2}日?|\d{4}-\d{2}-\d{2})/
  )
  const visitDate = resolveRelativeDate(dateMatch?.[1] ?? '', today)
  if (visitDate) {
    query.visit_date = visitDate
    summary.push(`就诊日期：${visitDate}`)
  }

  const timeMatch = normalized.match(/(?:上午|中午|下午|晚上|凌晨)?(\d{1,2}(?:[:：点时]\d{0,2})?)/)
  const visitTime = normalizeTimeString(timeMatch?.[1] ?? '')
  if (visitTime) {
    query.visit_time = visitTime
    summary.push(`就诊时间：${visitTime}`)
  }

  const hospitalMatch = normalized.match(
    /(?:在|去|到)([^，。；,、\s]{2,40}?(?:医院|卫生院|门诊部|诊所|医学院附属医院))/
  )
  if (hospitalMatch?.[1]) {
    query.hospital = hospitalMatch[1]
    summary.push(`医院：${hospitalMatch[1]}`)
  }

  const departmentMatch = normalized.match(
    /(心内科|心血管内科|呼吸科|呼吸内科|消化科|消化内科|神经内科|内分泌科|肾内科|肿瘤科|老年科|全科|内科|外科|骨科|妇科|儿科|耳鼻喉科|眼科|口腔科|皮肤科|康复科|中医科)/
  )
  if (departmentMatch?.[1]) {
    query.department = departmentMatch[1]
    summary.push(`科室：${departmentMatch[1]}`)
  }

  const doctorMatch =
    normalized.match(/([\u4e00-\u9fa5]{2,8})(?:医生|大夫)/) ||
    normalized.match(/(?:医生|大夫)([\u4e00-\u9fa5]{2,8})/)
  if (doctorMatch?.[1]) {
    query.doctor = doctorMatch[1]
    summary.push(`医生：${doctorMatch[1]}`)
  }

  const visitTypeMappings = [
    ['住院', 'inpatient'],
    ['急诊', 'emergency'],
    ['复诊', 'follow_up'],
    ['会诊', 'consultation'],
    ['体检', 'physical_exam'],
    ['疫苗', 'vaccination'],
    ['门诊', 'outpatient'],
  ] as const
  const visitType = visitTypeMappings.find(([keyword]) => normalized.includes(keyword))?.[1]
  if (visitType) {
    query.visit_type = visitType
    const visitTypeLabel = visitTypeMappings.find(([, value]) => value === visitType)?.[0]
    if (visitTypeLabel) {
      summary.push(`就诊类型：${visitTypeLabel}`)
    }
  }

  const statusMappings = [
    ['改期', 'rescheduled', '已改期'],
    ['取消', 'cancelled', '已取消'],
    ['未到诊', 'no_show', '未到诊'],
    ['预约', 'scheduled', '已预约'],
  ] as const
  const matchedStatus = statusMappings.find(([keyword]) => normalized.includes(keyword))
  if (matchedStatus) {
    query.status = matchedStatus[1]
    summary.push(`就医状态：${matchedStatus[2]}`)
  } else if (visitDate && visitDate <= today) {
    query.status = 'completed'
    summary.push('就医状态：已完成')
  }

  const urgencyMappings = [
    ['危重', 'critical', '危重'],
    ['急诊', 'emergency', '急诊'],
    ['紧急', 'urgent', '紧急'],
  ] as const
  const matchedUrgency = urgencyMappings.find(([keyword]) => normalized.includes(keyword))
  if (matchedUrgency) {
    query.urgency = matchedUrgency[1]
    summary.push(`紧急程度：${matchedUrgency[2]}`)
  } else {
    query.urgency = 'routine'
    summary.push('紧急程度：常规')
  }

  const diagnosisMatch = normalized.match(/(?:诊断(?:为|是)?|确诊(?:为|是)?)([^，。；,]+)/)
  if (diagnosisMatch?.[1]) {
    query.diagnosis = diagnosisMatch[1].trim()
    summary.push(`诊断：${query.diagnosis}`)
  }

  const complaintMatch =
    normalized.match(/(?:主诉|因为)([^，。；,]+)/) ||
    normalized.match(/(?:症状是|症状为)([^，。；,]+)/)
  if (complaintMatch?.[1]) {
    query.chief_complaint = complaintMatch[1].trim()
    summary.push(`主诉：${query.chief_complaint}`)
  }

  const orderMatch = normalized.match(/(?:医嘱|医生建议|建议)([^。；;]+)/)
  if (orderMatch?.[1]) {
    query.medical_orders = orderMatch[1].trim()
    summary.push(`医生建议：${query.medical_orders}`)
  }

  const followUpMatch = normalized.match(
    /(?:复诊|随访)(?:时间|日期)?(?:在|为|是)?(今天|今日|昨天|前天|明天|后天|\d{4}[年/.-]\d{1,2}[月/.-]\d{1,2}日?|\d{4}-\d{2}-\d{2})/
  )
  const followUpDate = resolveRelativeDate(followUpMatch?.[1] ?? '', today)
  if (followUpDate) {
    query.follow_up_date = followUpDate
    summary.push(`复诊日期：${followUpDate}`)
  }

  const medicineMatch = normalized.match(/(?:开了|处方|药物包括|用药有)([^。；;]+)/)
  if (medicineMatch?.[1]) {
    const medicineNames = Array.from(
      new Set(
        medicineMatch[1]
          .split(/[、，,和及]/)
          .map((item) => item.trim())
          .filter((item) => item.length >= 2)
      )
    )
    if (medicineNames.length > 0) {
      query.prescribed_medicines = medicineNames.join(',')
      summary.push(`处方药：${medicineNames.join('、')}`)
    }
  }

  const examinationMatch = normalized.match(/(?:做了|检查项目有|检查包括)([^。；;]+)/)
  if (examinationMatch?.[1]) {
    const examinationNames = Array.from(
      new Set(
        examinationMatch[1]
          .split(/[、，,和及]/)
          .map((item) => item.trim())
          .filter((item) => item.length >= 2)
      )
    )
    if (examinationNames.length > 0) {
      query.examinations = examinationNames.join(',')
      summary.push(`检查项目：${examinationNames.join('、')}`)
    }
  }

  if (
    !query.visit_date &&
    !query.hospital &&
    !query.visit_type &&
    !query.diagnosis &&
    !query.chief_complaint
  ) {
    return null
  }

  return {
    query,
    summary,
  }
}

function buildReminderDraftProposal(task: string): PageAgentActionProposal | null {
  const today = new Date().toISOString().split('T')[0]
  const payload = buildReminderDraftPayload(task, today)
  if (!payload) {
    return null
  }

  const targetPath = isReminderFormPath(window.location.pathname)
    ? window.location.pathname
    : '/reminders/create'
  const targetLabel = isReminderFormPath(window.location.pathname)
    ? '当前提醒表单'
    : '提醒创建页'

  return {
    type: 'reminder-draft',
    targetPath,
    targetLabel,
    reason: '我已识别到你想新建提醒，并整理出一个待确认草稿，不会自动提交。',
    buttonLabel: isReminderFormPath(window.location.pathname)
      ? '确认填入当前提醒表单'
      : '确认前往提醒创建页',
    query: payload.query,
    summary: payload.summary,
  }
}

function buildMedicalRecordDraftProposal(task: string): PageAgentActionProposal | null {
  const today = new Date().toISOString().split('T')[0]
  const payload = parseMedicalRecordDraftPayload(task, today)
  if (!payload) {
    return null
  }

  const targetPath = isMedicalRecordFormPath(window.location.pathname)
    ? window.location.pathname
    : '/medical-records/create'
  const targetLabel = isMedicalRecordFormPath(window.location.pathname)
    ? '当前病历表单'
    : '新增病历页'

  return {
    type: 'medical-record-draft',
    targetPath,
    targetLabel,
    reason: '我已识别到你想整理一份病历草稿，并提取了可预填的关键信息，不会自动提交。',
    buttonLabel: isMedicalRecordFormPath(window.location.pathname)
      ? '确认填入当前病历表单'
      : '确认前往新增病历页',
    query: payload.query,
    summary: payload.summary,
  }
}

function buildMedicineDraftProposal(task: string): PageAgentActionProposal | null {
  const today = new Date().toISOString().split('T')[0]
  const payload = buildMedicineDraftPayload(task, today)
  if (!payload) {
    return null
  }

  return {
    type: 'medicine-draft',
    targetPath: '/medicines',
    targetLabel: '药品页',
    reason: '我已识别到你想新增药品，并整理出一个待确认草稿，会先帮你打开药品表单，不会自动保存。',
    buttonLabel: '确认打开药品表单',
    query: payload.query,
    summary: payload.summary,
  }
}

function buildNavigationProposal(task: string): PageAgentActionProposal | null {
  if (!NAVIGATION_TRIGGER.test(task)) {
    return null
  }

  const currentPath = window.location.pathname
  const target = CONTROLLED_NAVIGATION_TARGETS.find((item) => item.matcher.test(task))
  if (!target || currentPath === target.path) {
    return null
  }

  return {
    type: 'navigate',
    targetPath: target.path,
    targetLabel: target.label,
    reason: `我已识别到你想切换到${target.label}，但跳转前仍需要你手动确认。`,
    buttonLabel: `确认前往${target.label}`,
  }
}

function buildActionProposal(task: string): PageAgentActionProposal | null {
  return (
    buildReminderDraftProposal(task) ||
    buildMedicalRecordDraftProposal(task) ||
    buildMedicineDraftProposal(task) ||
    buildNavigationProposal(task)
  )
}

function buildActionProposalAnswer(proposal: PageAgentActionProposal): string {
  const lines = ['已识别到一个待确认操作。', '', proposal.reason]

  if (proposal.summary?.length) {
    lines.push('', '草稿内容：', ...proposal.summary.map((item) => `- ${item}`))
  }

  lines.push('', '如需继续，请点击消息下方的确认按钮。')
  return lines.join('\n')
}

/**
 * 构造 Page Agent 的共享配置。
 */
function buildPageAgentConfig(): PageAgentCoreConfig {
  const pageController = new PageController({
    enableMask: false,
    viewportExpansion: -1,
    includeAttributes: ['data-*', 'aria-*', 'placeholder', 'title'],
  })

  return {
    pageController,
    baseURL: resolvePageAgentProxyBaseURL(),
    apiKey: 'NA',
    model: 'page-agent-proxy',
    language: 'zh-CN',
    maxSteps: 8,
    customFetch: createAuthenticatedFetch(),
    instructions: {
      system: [
        '你是 mtm-helper 的页面助手。',
        '当前版本以保守分析为主，仅允许生成待确认的辅助填写草稿。',
        '禁止调用任何会自动提交或自动保存的动作。',
        '回答必须使用中文，并给出明确、可执行的结论。',
      ].join('\n'),
      getPageInstructions,
    },
    customTools: {
      ask_user: null,
      click_element_by_index: null,
      input_text: null,
      select_dropdown_option: null,
      execute_javascript: null,
      get_mtm_runtime_context: tool({
        description: '获取 mtm-helper 当前页面的运行时上下文信息。',
        inputSchema: z.object({}),
        execute: async () => {
          return JSON.stringify(
            {
              pathname: window.location.pathname,
              search: window.location.search,
              title: document.title,
              scope: getCurrentPageAgentScopeDescription(),
            },
            null,
            2
          )
        },
      }),
      get_mtm_page_snapshot: tool({
        description:
          '获取当前页面的通用结构快照，包括标题、标题层级、指标卡、表格预览和风险关键词。',
        inputSchema: z.object({}),
        execute: async () => {
          return JSON.stringify(buildCommonPageSnapshot(), null, 2)
        },
      }),
      get_mtm_reminder_snapshot: tool({
        description:
          '当页面是提醒页时，获取提醒业务摘要，包括待确认、活跃提醒、发送统计和风险信号。',
        inputSchema: z.object({}),
        execute: async () => {
          return JSON.stringify(buildReminderSnapshot(), null, 2)
        },
      }),
      get_mtm_medicine_snapshot: tool({
        description:
          '当页面是药品页时，获取药品业务摘要，包括统计卡、列表预览、关键字段和库存/效期风险。',
        inputSchema: z.object({}),
        execute: async () => {
          return JSON.stringify(buildMedicineSnapshot(), null, 2)
        },
      }),
      get_mtm_dashboard_snapshot: tool({
        description:
          '当页面是仪表板时，获取概览卡片和导航摘要，帮助识别最值得关注的业务入口与异常趋势。',
        inputSchema: z.object({}),
        execute: async () => {
          return JSON.stringify(buildDashboardSnapshot(), null, 2)
        },
      }),
    },
    onBeforeTask: () => {
      console.log('[PageAgent] 开始执行页面任务', {
        path: window.location.pathname,
      })
    },
    onAfterTask: (_agent, result) => {
      console.log('[PageAgent] 页面任务完成', {
        success: result.success,
        path: window.location.pathname,
      })
    },
  }
}

/**
 * 获取页面助手单例实例。
 */
function getPageAgent(): PageAgentCore {
  if (!pageAgentInstance) {
    pageAgentInstance = new PageAgentCore(buildPageAgentConfig())
  }
  return pageAgentInstance
}

/**
 * 将执行历史压缩为便于展示的任务轨迹。
 */
function summarizeHistory(history: HistoricalEvent[]): string[] {
  return history
    .filter((item): item is Extract<HistoricalEvent, { type: 'step' }> => {
      return item.type === 'step'
    })
    .slice(0, 6)
    .map((step) => {
      const toolName = step.action.name
      const output = String(step.action.output || '').replace(/\s+/g, ' ').trim()
      const briefOutput = output.length > 72 ? `${output.slice(0, 72)}...` : output
      return `步骤 ${step.stepIndex + 1}：${toolName}${briefOutput ? ` - ${briefOutput}` : ''}`
    })
}

function extractLowStockMedicineNames(limit = 8): string[] {
  const badges = Array.from(document.querySelectorAll('span,div,p')).filter(
    (node) => normalizeText(node.textContent || '', 16) === '库存不足'
  )

  const names = badges
    .map((badge) => {
      const container = badge.closest(
        'div[class*="rounded"], div[class*="shadow"], article, li, section'
      )
      const name = normalizeText(
        container?.querySelector('h1, h2, h3, h4, [data-medicine-name]')?.textContent || '',
        40
      )
      return name
    })
    .filter(Boolean)

  return Array.from(new Set(names)).slice(0, limit)
}

function buildLowStockMedicineAnswer(): string {
  const medicineNames = extractLowStockMedicineNames()
  if (!medicineNames.length) {
    return '当前页面没有识别到“库存不足”的药品。若你刚修改过筛选条件，请先清空筛选后再问我一次。\n\n执行来源：页面规则'
  }
  return `库存不足的药品有：${medicineNames.join('、')}。建议优先补货，避免断药影响用药连续性。\n\n执行来源：页面规则`
}

/**
 * 组装页面助手最终返回给 UI 的 Markdown 文本。
 */
function buildPageAgentAnswer(result: ExecutionResult): string {
  const lines = [result.data || '页面助手未返回结果。', '', '执行来源：模型']

  return lines.join('\n')
}

/**
 * 执行当前页面的分析或辅助填写任务。
 */
export async function executePageAgentTask(
  task: string
): Promise<PageAgentTaskResult> {
  const pathname = window.location.pathname
  const normalizedTask = task.trim()
  console.log('[PageAgent] 开始处理任务', {
    task: normalizedTask,
    pathname,
  })

  if (!canUsePageAgentOnCurrentPage(pathname)) {
    throw new Error(
      '当前页面暂未开放页面助手，请在仪表板、药品页、提醒页、提醒表单或病历页面中使用。'
    )
  }

  if (
    /^\/medicines(?:\/|$)/.test(pathname) &&
    /(哪个药|哪些药|什么药|哪种药|库存).*(不够|不足|快没|缺|告急)|库存(不足|不够|告急)/.test(
      normalizedTask
    )
  ) {
    console.log('[PageAgent] 命中库存规则直答', { task: normalizedTask })
    const answer = buildLowStockMedicineAnswer()
    return {
      success: true,
      answer,
      steps: ['步骤 1：规则命中 - 库存不足查询', '步骤 2：读取当前页面可见药品状态'],
      proposal: null,
    }
  }

  const proposal = buildActionProposal(task)
  if (proposal) {
    console.log('[PageAgent] 命中待确认操作提案', proposal)
    return {
      success: true,
      answer: buildActionProposalAnswer(proposal),
      steps: [],
      proposal,
    }
  }

  const agent = getPageAgent()
  const normalizedPrompt = [
    '请基于当前 mtm-helper 页面完成保守分析或辅助填写任务。',
    '不要自动提交，也不要假设隐藏数据存在。',
    `用户任务：${normalizedTask}`,
  ].join('\n')

  const result = await agent.execute(normalizedPrompt)
  console.log('[PageAgent] 模型执行完成', {
    success: result.success,
    historyLength: Array.isArray(result.history) ? result.history.length : 0,
  })
  return {
    success: result.success,
    answer: buildPageAgentAnswer(result),
    steps: summarizeHistory(result.history),
    proposal: null,
  }
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
