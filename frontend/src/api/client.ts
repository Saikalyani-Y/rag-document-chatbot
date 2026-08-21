import type { ChatMessage, Conversation, DocumentItem, Source } from '../types'

const BASE = '/api'

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${BASE}${path}`, init)
  } catch {
    throw new ApiError('Cannot reach the server. Is the backend running?', 0)
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try {
      const body = await response.json()
      if (body?.error) message = body.error
    } catch {
      // response had no JSON body; keep the generic message
    }
    throw new ApiError(message, response.status)
  }

  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export function getHealth() {
  return request<{ status: string; detail: string }>('/health')
}

export function listDocuments() {
  return request<DocumentItem[]>('/documents')
}

export function uploadDocument(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request<DocumentItem>('/documents', { method: 'POST', body: formData })
}

export function deleteDocument(id: string) {
  return request<void>(`/documents/${id}`, { method: 'DELETE' })
}

export function listConversations() {
  return request<Conversation[]>('/conversations')
}

export function createConversation() {
  return request<Conversation>('/conversations', { method: 'POST' })
}

export function deleteConversation(id: string) {
  return request<void>(`/conversations/${id}`, { method: 'DELETE' })
}

export function listMessages(conversationId: string) {
  return request<ChatMessage[]>(`/conversations/${conversationId}/messages`)
}

export function sendMessage(conversationId: string, content: string, allowGeneralKnowledge: boolean) {
  return request<{ message_id: string; answer: string; sources: Source[]; grounded: boolean }>(
    `/conversations/${conversationId}/messages`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, allow_general_knowledge: allowGeneralKnowledge }),
    },
  )
}
