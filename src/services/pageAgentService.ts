import {
  canUsePageAgentOnCurrentPage,
  getCurrentPageAgentScopeDescription,
  getPageAgentQuickActions,
  type PageAgentActionProposal,
  type PageAgentMode,
  type PageAgentTaskResult,
} from '@/services/pageAgentShared'

export {
  canUsePageAgentOnCurrentPage,
  getCurrentPageAgentScopeDescription,
  getPageAgentQuickActions,
}

export type {
  PageAgentActionProposal,
  PageAgentMode,
  PageAgentTaskResult,
}

/**
 * 按需加载页面助手运行时，避免默认路径静态带入重依赖。
 */
export async function executePageAgentTask(
  task: string
): Promise<PageAgentTaskResult> {
  const runtimeModule = await import('@/services/pageAgentRuntime')
  return runtimeModule.executePageAgentTask(task)
}
