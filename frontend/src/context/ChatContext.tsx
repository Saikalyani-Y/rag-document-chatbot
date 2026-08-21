import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import {
  ApiError,
  createConversation,
  deleteConversation,
  listConversations,
  listMessages,
  sendMessage,
} from '../api/client'
import type { ChatMessage, Conversation } from '../types'

interface ChatContextValue {
  conversations: Conversation[]
  activeId: string | null
  messages: ChatMessage[]
  sending: boolean
  error: string | null
  selectConversation: (id: string) => Promise<void>
  newChat: () => void
  removeConversation: (id: string) => Promise<void>
  ask: (content: string) => Promise<void>
  dismissError: () => void
}

const ChatContext = createContext<ChatContextValue | null>(null)

export function ChatProvider({ children }: { children: ReactNode }) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshConversations = useCallback(async () => {
    try {
      const convos = await listConversations()
      setConversations(convos)
    } catch {
      // conversation history is non-critical; fail silently and let the user keep chatting
    }
  }, [])

  useEffect(() => {
    refreshConversations()
  }, [refreshConversations])

  const selectConversation = useCallback(async (id: string) => {
    setActiveId(id)
    setError(null)
    try {
      const msgs = await listMessages(id)
      setMessages(msgs)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to load this conversation.')
    }
  }, [])

  const newChat = useCallback(() => {
    setActiveId(null)
    setMessages([])
    setError(null)
  }, [])

  const removeConversation = useCallback(
    async (id: string) => {
      try {
        await deleteConversation(id)
        setConversations((prev) => prev.filter((c) => c.id !== id))
        if (activeId === id) newChat()
      } catch (err) {
        setError(err instanceof ApiError ? err.message : 'Failed to delete conversation.')
      }
    },
    [activeId, newChat],
  )

  const ask = useCallback(
    async (content: string) => {
      setError(null)
      let conversationId = activeId
      if (!conversationId) {
        try {
          const convo = await createConversation()
          conversationId = convo.id
          setActiveId(convo.id)
          setConversations((prev) => [convo, ...prev])
        } catch (err) {
          setError(err instanceof ApiError ? err.message : 'Failed to start a new conversation.')
          return
        }
      }

      const userMessage: ChatMessage = {
        id: `local-${Date.now()}`,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      }
      const pendingMessage: ChatMessage = {
        id: 'pending',
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
        pending: true,
      }
      setMessages((prev) => [...prev, userMessage, pendingMessage])
      setSending(true)

      try {
        const result = await sendMessage(conversationId, content)
        setMessages((prev) => [
          ...prev.filter((m) => m.id !== 'pending'),
          {
            id: result.message_id,
            role: 'assistant',
            content: result.answer,
            sources: result.sources,
            created_at: new Date().toISOString(),
          },
        ])
        refreshConversations()
      } catch (err) {
        setMessages((prev) => prev.filter((m) => m.id !== 'pending'))
        setError(err instanceof ApiError ? err.message : 'Failed to get a response. Please try again.')
      } finally {
        setSending(false)
      }
    },
    [activeId, refreshConversations],
  )

  const dismissError = useCallback(() => setError(null), [])

  return (
    <ChatContext.Provider
      value={{
        conversations,
        activeId,
        messages,
        sending,
        error,
        selectConversation,
        newChat,
        removeConversation,
        ask,
        dismissError,
      }}
    >
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const ctx = useContext(ChatContext)
  if (!ctx) throw new Error('useChat must be used within ChatProvider')
  return ctx
}
