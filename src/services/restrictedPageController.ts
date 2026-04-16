import { getCurrentPageAgentScopeDescription, getCurrentPageKey } from '@/services/pageAgentShared'

export interface RestrictedBrowserState {
  url: string
  title: string
  header: string
  content: string
  footer: string
}

interface ActionResult {
  success: boolean
  message: string
}

interface ScrollOptions {
  down?: boolean
  numPages?: number
  pixels?: number
  index?: number
}

interface HorizontalScrollOptions {
  right?: boolean
  pixels: number
  index?: number
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
export function normalizeText(text: string, maxLength = 120): string {
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
export function buildCommonPageSnapshot() {
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
export function buildReminderSnapshot() {
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
export function buildMedicineSnapshot() {
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
export function buildDashboardSnapshot() {
  return {
    ...buildCommonPageSnapshot(),
    sections: collectVisibleTexts('p, a, h1, h2, h3', 18, 80).filter((text) =>
      /(药品总数|今日提醒|库存预警|用药计划|药品管理|提醒管理|就医记录|统计分析)/.test(text)
    ),
    navigation: collectVisibleTexts('a', 12, 80),
  }
}

/**
 * 根据当前页面构建统一的受限 BrowserState 文本。
 */
function buildRestrictedBrowserState(): RestrictedBrowserState {
  const snapshot = buildCommonPageSnapshot()
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0
  const pageHeight = Math.max(
    document.body?.scrollHeight || 0,
    document.documentElement.scrollHeight || 0,
    viewportHeight
  )
  const scrollTop =
    window.scrollY ||
    document.documentElement.scrollTop ||
    document.body?.scrollTop ||
    0
  const pixelsAbove = Math.max(Math.round(scrollTop), 0)
  const pixelsBelow = Math.max(Math.round(pageHeight - (scrollTop + viewportHeight)), 0)
  const progress = pageHeight > 0 ? Math.min(((scrollTop + viewportHeight) / pageHeight) * 100, 100) : 100
  const url = window.location.href
  const title = document.title || '未知页面'

  const header = [
    `Current Page: [${title}](${url})`,
    `Page info: ${window.innerWidth}x${viewportHeight}px viewport, ${pageHeight}px total page height, at ${progress.toFixed(0)}% of page`,
    '',
    `Page scope: ${snapshot.scope}`,
    pixelsAbove > 4 ? `... ${pixelsAbove} pixels above - scroll to see more ...` : '[Start of page]',
  ].join('\n')

  const contentBlocks = [
    snapshot.headings.length ? `Headings:\n- ${snapshot.headings.join('\n- ')}` : '',
    snapshot.metrics.length
      ? `Metrics:\n- ${snapshot.metrics.map((item) => `${item.label}: ${item.value}`).join('\n- ')}`
      : '',
    snapshot.table_preview.length ? `Table Preview:\n- ${snapshot.table_preview.join('\n- ')}` : '',
    snapshot.block_preview.length ? `Block Preview:\n- ${snapshot.block_preview.join('\n- ')}` : '',
    snapshot.attention_signals.length
      ? `Attention Signals:\n- ${snapshot.attention_signals.join('\n- ')}`
      : '',
  ].filter(Boolean)

  const content =
    contentBlocks.join('\n\n') ||
    '(empty page snapshot. no visible headings, metrics, tables, or blocks were collected.)'

  const footer =
    pixelsBelow > 4
      ? `... ${pixelsBelow} pixels below - scroll to see more ...`
      : '[End of page]'

  return {
    url,
    title,
    header,
    content,
    footer,
  }
}

/**
 * 受限版页面控制器，只保留当前业务主路径实际需要的观察能力。
 */
export class RestrictedPageController {
  private lastTimeUpdate = 0

  /**
   * 返回最近一次页面状态刷新的时间戳。
   */
  async getLastUpdateTime(): Promise<number> {
    return this.lastTimeUpdate
  }

  /**
   * 返回当前页面的受限 BrowserState。
   */
  async getBrowserState(): Promise<RestrictedBrowserState> {
    this.lastTimeUpdate = Date.now()
    return buildRestrictedBrowserState()
  }

  /**
   * 执行页面级垂直滚动，并更新最后刷新时间。
   */
  async scroll(options: ScrollOptions = {}): Promise<ActionResult> {
    if (typeof options.index === 'number') {
      return {
        success: false,
        message: '当前页面助手暂不支持按元素索引滚动，请改用页面级滚动。',
      }
    }

    const direction = options.down === false ? -1 : 1
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 800
    const distance =
      typeof options.pixels === 'number'
        ? Math.max(options.pixels, 0)
        : Math.max(Math.round((options.numPages ?? 0.1) * viewportHeight), 0)

    window.scrollBy({
      top: direction * distance,
      left: 0,
      behavior: 'auto',
    })
    this.lastTimeUpdate = Date.now()

    return {
      success: true,
      message: `已${direction > 0 ? '向下' : '向上'}滚动 ${distance} 像素。`,
    }
  }

  /**
   * 禁用水平滚动，避免引入当前主路径不需要的复杂能力。
   */
  async scrollHorizontally(_options: HorizontalScrollOptions): Promise<ActionResult> {
    return {
      success: false,
      message: '当前页面助手已禁用水平滚动能力。',
    }
  }

  /**
   * 禁用点击交互，保持页面助手为保守分析模式。
   */
  async clickElement(_index: number): Promise<ActionResult> {
    return {
      success: false,
      message: '当前页面助手已禁用点击交互能力。',
    }
  }

  /**
   * 禁用输入交互，避免自动填写页面元素。
   */
  async inputText(_index: number, _text: string): Promise<ActionResult> {
    return {
      success: false,
      message: '当前页面助手已禁用文本输入能力。',
    }
  }

  /**
   * 禁用下拉选择交互，避免自动修改表单状态。
   */
  async selectOption(_index: number, _text: string): Promise<ActionResult> {
    return {
      success: false,
      message: '当前页面助手已禁用下拉选择能力。',
    }
  }

  /**
   * 禁用脚本执行能力，避免引入 eval 相关风险。
   */
  async executeJavascript(_script: string): Promise<ActionResult> {
    return {
      success: false,
      message: '当前页面助手已禁用脚本执行能力。',
    }
  }

  /**
   * 保留遮罩接口为 no-op，兼容 PageAgentCore 生命周期调用。
   */
  async showMask(): Promise<void> {}

  /**
   * 保留遮罩接口为 no-op，兼容 PageAgentCore 生命周期调用。
   */
  async hideMask(): Promise<void> {}

  /**
   * 保留高亮清理接口为 no-op，兼容 PageAgentCore 生命周期调用。
   */
  async cleanUpHighlights(): Promise<void> {}

  /**
   * 清理本地状态，兼容 PageAgentCore 的释放流程。
   */
  dispose(): void {
    this.lastTimeUpdate = 0
  }
}
