import { AlertCircle, Globe, X } from 'lucide-react'
import { useChat } from '../../context/ChatContext'
import { ChatInput } from '../ChatInput/ChatInput'
import { MessageList } from './MessageList'
import { WelcomeScreen } from './WelcomeScreen'

export function ChatWindow() {
  const { messages, sending, ask, error, dismissError, allowGeneralKnowledge, setAllowGeneralKnowledge } = useChat()

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

        <label className="mb-2 flex w-fit cursor-pointer items-center gap-2 select-none text-xs text-neutral-500 dark:text-neutral-400">
          <span className="relative inline-flex h-4 w-7 items-center">
            <input
              type="checkbox"
              checked={allowGeneralKnowledge}
              onChange={(e) => setAllowGeneralKnowledge(e.target.checked)}
              className="peer sr-only"
            />
            <span className="absolute inset-0 rounded-full bg-neutral-300 transition-colors peer-checked:bg-blue-600 dark:bg-neutral-700" />
            <span className="absolute left-0.5 h-3 w-3 rounded-full bg-white transition-transform peer-checked:translate-x-3" />
          </span>
          <Globe size={12} />
          Also search the web when documents don't have the answer
        </label>

        <ChatInput onSend={ask} disabled={sending} />
        <p className="mt-2 text-center text-xs text-neutral-400 dark:text-neutral-600">
          {allowGeneralKnowledge
            ? 'Answers use your documents first, falling back to live web search — check the badge on each answer.'
            : 'Answers are grounded in your uploaded documents and may be incomplete.'}
        </p>
      </div>
    </div>
  )
}
