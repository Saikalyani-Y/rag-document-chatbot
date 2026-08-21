import { AlertCircle, X } from 'lucide-react'
import { useChat } from '../../context/ChatContext'
import { ChatInput } from '../ChatInput/ChatInput'
import { MessageList } from './MessageList'
import { WelcomeScreen } from './WelcomeScreen'

export function ChatWindow() {
  const { messages, sending, ask, error, dismissError } = useChat()

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? <WelcomeScreen onSuggestion={ask} /> : <MessageList messages={messages} />}
      </div>

      <div className="mx-auto w-full max-w-3xl px-4 pb-4">
        {error && (
          <div className="mb-2 flex items-center justify-between gap-2 rounded-lg bg-red-50 dark:bg-red-900/20 px-3 py-2 text-sm text-red-700 dark:text-red-300">
            <span className="flex items-center gap-2">
              <AlertCircle size={14} className="shrink-0" />
              {error}
            </span>
            <button onClick={dismissError} aria-label="Dismiss error">
              <X size={14} />
            </button>
          </div>
        )}
        <ChatInput onSend={ask} disabled={sending} />
        <p className="mt-2 text-center text-xs text-neutral-400 dark:text-neutral-600">
          Answers are grounded in your uploaded documents and may be incomplete.
        </p>
      </div>
    </div>
  )
}
