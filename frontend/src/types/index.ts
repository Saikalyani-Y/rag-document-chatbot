export type DocumentStatus = 'processing' | 'ready' | 'failed'

export interface DocumentItem {
  id: string
  filename: string
  file_type: string
  status: DocumentStatus
  error_message: string | null
  chunk_count: number
  uploaded_at: string
}

export interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export interface Source {
  document_id: string
  filename: string
  label: string
  chunk_id: number
  score: number
}

export type MessageRole = 'user' | 'assistant'

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  sources?: Source[] | null
  created_at: string
  pending?: boolean
}
