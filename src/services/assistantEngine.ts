import {
  getSessionMemory,
  saveSessionMemory,
  summarizeSessionMemory,
  type SessionMemoryMessage,
} from '@/services/sessionMemory'

export type AssistantMode = 'page-agent' | 'medication'

type SummaryCache = Record<string, string>

const MAX_CONTEXT_CHARS = 240

function trimContext(value: string, limit = MAX_CONTEXT_CHARS) {
  const text = (value || '').trim()
  if (!text || text.length <= limit) return text
  return `${text.slice(0, limit)}...`
}

export function createAssistantEngine() {
  const summaryCache: SummaryCache = {}
  let globalContextMemory = ''

  const getSessionIdBase = (pathname: string) => {
    const normalized = pathname || '/'
    const mtmMatch = normalized.match(/^\/mtm\/service-cases\/(\d+)(?:\/|$)/)
    if (mtmMatch) return `mtm:${mtmMatch[1]}`
    if (/^\/dashboard(?:\/|$)/.test(normalized)) return 'app:dashboard'
    if (/^\/reminders(?:\/|$)/.test(normalized)) return 'app:reminders'
    if (/^\/medicines(?:\/|$)/.test(normalized)) return 'app:medicines'
    if (/^\/medical-records(?:\/|$)/.test(normalized)) return 'app:medical-records'
    return 'app:default'
  }

  const buildSessionId = (pathname: string, mode: AssistantMode) =>
    `${getSessionIdBase(pathname)}:${mode}`

  const ensureSummary = async (sessionId: string) => {
    if (summaryCache[sessionId] !== undefined) return summaryCache[sessionId]
    try {
      const payload = await getSessionMemory(sessionId)
      summaryCache[sessionId] = payload.summary || ''
      return summaryCache[sessionId]
    } catch {
      summaryCache[sessionId] = ''
      return ''
    }
  }

  const augmentUserText = (mode: AssistantMode, text: string, summary: string) => {
    const cleaned = (text || '').trim()
    const parts: string[] = []

    const globalSummary = trimContext(globalContextMemory)
    if (globalSummary) parts.push(`[GLOBAL]\n${globalSummary}`)

    const pageSummary = trimContext(summary)
    if (pageSummary) parts.push(`[PAGE]\n${pageSummary}`)

    if (!parts.length) return cleaned

    const prefix = trimContext(parts.join('\n\n'), 500)
    return mode === 'page-agent'
      ? `${prefix}\n\nTASK: ${cleaned}`
      : `${prefix}\n\nQUESTION: ${cleaned}`
  }

  const syncGlobalContext = (newContext: string) => {
    if (newContext) globalContextMemory = trimContext(newContext, 320)
  }

  const persist = async (sessionId: string, messages: SessionMemoryMessage[]) => {
    try {
      const summary = summaryCache[sessionId] || ''
      await saveSessionMemory(sessionId, { summary, messages })
      const shouldSummarize =
        (!summary && messages.length >= 10) || (summary && messages.length % 16 === 0)
      if (!shouldSummarize) return summary

      try {
        const result = await summarizeSessionMemory(sessionId, messages)
        summaryCache[sessionId] = result.summary || ''
        syncGlobalContext(result.summary || '')
      } catch {
        // keep current summary if summarization fails
      }

      return summaryCache[sessionId]
    } catch {
      return summaryCache[sessionId] || ''
    }
  }

  return {
    buildSessionId,
    ensureSummary,
    augmentUserText,
    persist,
    syncGlobalContext,
  }
}
