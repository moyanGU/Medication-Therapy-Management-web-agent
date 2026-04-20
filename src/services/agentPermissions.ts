import type { PageAgentActionProposal } from '@/services/pageAgentService'
import { useAuthStore } from '@/stores/auth'

export type AgentPermissionState = 'ask' | 'allow' | 'deny'

export interface PermissionMatrix {
  [role: string]: {
    [actionType: string]: AgentPermissionState
  }
}

const STORAGE_KEY = 'mtm.agent.permission_matrix'

// Default matrix
const defaultMatrix: PermissionMatrix = {
  pharmacist: {
    navigate: 'allow', // 药师经常需要跳转，允许自动
    fill_form: 'ask',
    submit: 'ask',
  },
  patient: {
    navigate: 'ask',
    fill_form: 'ask',
    submit: 'deny', // 患者不能自动提交表单
  },
  default: {
    navigate: 'ask',
    fill_form: 'ask',
    submit: 'ask',
  },
}

export function getPermissionMatrix(): PermissionMatrix {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      return { ...defaultMatrix, ...parsed }
    }
  } catch {
    // ignore
  }
  return defaultMatrix
}

export function savePermissionMatrix(matrix: PermissionMatrix): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(matrix))
  } catch {
    // ignore
  }
}

export function getProposalPermissionState(proposal: PageAgentActionProposal): AgentPermissionState {
  const authStore = useAuthStore()
  const role = authStore.user?.role || 'default'
  const matrix = getPermissionMatrix()
  
  const roleMatrix = matrix[role] || matrix.default
  return roleMatrix[proposal.type] || 'ask'
}

export function updateAgentPermission(role: string, actionType: string, state: AgentPermissionState): void {
  const matrix = getPermissionMatrix()
  if (!matrix[role]) {
    matrix[role] = {}
  }
  matrix[role][actionType] = state
  savePermissionMatrix(matrix)
}

