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

  // 跨页面共享上下文 (Global cross-route reasoning)
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
    
    // 合并跨路由全局记忆和当前页面记忆
    let combinedContext = ''
    if (globalContextMemory) {
      combinedContext += `【全局跨页面记忆】\n${globalContextMemory}\n\n`
    }
    if (summary) {
      combinedContext += `【当前页面记忆】\n${summary}\n\n`
    }
    
    if (!combinedContext) return cleaned

    if (mode === 'page-agent') {
      return `${combinedContext.trim()}\n\n任务：${cleaned}`
    }
    return `${combinedContext.trim()}\n\n问题：${cleaned}`
  }

  const syncGlobalContext = (newContext: string) => {
    if (newContext) {
      globalContextMemory = newContext
    }
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
      
      // 更新跨路由记忆 (保持全局感知)
      syncGlobalContext(result.summary || '')
      
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

