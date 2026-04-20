import type { PageAgentActionProposal } from '@/services/pageAgentService'

const STORAGE_PREFIX = 'mtm.agent.permission'
const AUTO_CONFIRM_THRESHOLD = 2

function buildKey(proposal: PageAgentActionProposal): string {
  return `${STORAGE_PREFIX}:${proposal.type}:${proposal.targetPath}`
}

export function shouldAutoConfirmProposal(proposal: PageAgentActionProposal): boolean {
  try {
    const key = buildKey(proposal)
    const raw = localStorage.getItem(key)
    const count = raw ? Number(raw) : 0
    return Number.isFinite(count) && count >= AUTO_CONFIRM_THRESHOLD
  } catch {
    return false
  }
}

export function recordConfirmedProposal(proposal: PageAgentActionProposal): void {
  try {
    const key = buildKey(proposal)
    const raw = localStorage.getItem(key)
    const count = raw ? Number(raw) : 0
    const next = (Number.isFinite(count) ? count : 0) + 1
    localStorage.setItem(key, String(next))
  } catch {
    return
  }
}

