import {
  getSessionMemory,
  saveSessionMemory,
  summarizeSessionMemory,
  type SessionMemoryMessage,
} from '@/services/sessionMemory'

export type AssistantMode = 'page-agent' | 'medication'

type SummaryCache = Record<string, string>

export function createAssistantEngine() {
  const summaryCache: SummaryCache = {}

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

  const buildSessionId = (pathname: string, mode: AssistantMode) => {
    return `${getSessionIdBase(pathname)}:${mode}`
  }

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
    if (!summary) return cleaned
    if (mode === 'page-agent') return `会话记忆：${summary}\n\n任务：${cleaned}`
    return `会话记忆：${summary}\n\n问题：${cleaned}`
  }

  const persist = async (sessionId: string, messages: SessionMemoryMessage[]) => {
    try {
      const summary = summaryCache[sessionId] || ''
      await saveSessionMemory(sessionId, { summary, messages })
      const shouldSummarize =
        (!summary && messages.length >= 10) || (summary && messages.length % 16 === 0)
      if (!shouldSummarize) return summary
      const result = await summarizeSessionMemory(sessionId, messages)
      summaryCache[sessionId] = result.summary || ''
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
  }
}

