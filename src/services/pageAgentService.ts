import {
  canUsePageAgentOnCurrentPage,
  getCurrentPageAgentScopeDescription,
  getPageAgentQuickActions,
  type PageAgentActionProposal,
  type PageAgentMode,
  type PageAgentTaskResult,
  type OnStepCallback,
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
  OnStepCallback,
}

/**
 * 按需加载页面助手运行时，避免默认路径静态带入重依赖。
 */
export async function executePageAgentTask(
  task: string,
  onStep?: OnStepCallback
): Promise<PageAgentTaskResult> {
  const runtimeModule = await import('@/services/pageAgentRuntime')
  return runtimeModule.executePageAgentTask(task, onStep)
}
