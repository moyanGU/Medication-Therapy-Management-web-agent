import { api } from '@/utils/api'

export type SessionMemoryMessage = {
  role: 'user' | 'ai'
  content: string
}

export type SessionMemoryPayload = {
  session_id: string
  summary: string
  messages: SessionMemoryMessage[]
  updated_at?: string
}

export async function getSessionMemory(
  sessionId: string
): Promise<SessionMemoryPayload> {
  const response = await api.get<any>('/ai/session-memory/', {
    params: { session_id: sessionId },
  })
  return response.data as SessionMemoryPayload
}

export async function saveSessionMemory(
  sessionId: string,
  payload: { summary?: string; messages?: SessionMemoryMessage[] }
): Promise<{ session_id: string; updated_at: string }> {
  const response = await api.post<any>('/ai/session-memory/', {
    session_id: sessionId,
    summary: payload.summary ?? '',
    messages: payload.messages ?? [],
  })
  return response.data as { session_id: string; updated_at: string }
}

export async function summarizeSessionMemory(
  sessionId: string,
  messages?: SessionMemoryMessage[]
): Promise<{ session_id: string; summary: string; updated_at: string }> {
  const response = await api.post<any>('/ai/session-memory/summarize/', {
    session_id: sessionId,
    messages: messages ?? [],
  })
  return response.data as { session_id: string; summary: string; updated_at: string }
}

