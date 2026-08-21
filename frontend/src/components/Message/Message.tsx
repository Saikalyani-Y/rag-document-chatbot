import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Check, Copy, User, Sparkles } from 'lucide-react'
import type { ChatMessage } from '../../types'
import { SourceCitation } from '../SourceCitation/SourceCitation'
import { LoadingIndicator } from '../LoadingIndicator/LoadingIndicator'

export function Message({ message }: { message: ChatMessage }) {
  const [copied, setCopied] = useState(false)
  const isUser = message.role === 'user'

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      // clipboard access can fail (permissions/insecure context); not worth surfacing an error for
    }
  }

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${
          isUser ? 'bg-blue-600 text-white' : 'bg-neutral-200 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-200'
        }`}
      >
        {isUser ? <User size={14} /> : <Sparkles size={14} />}
      </div>

      <div className={`group max-w-[75ch] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div
          className={`rounded-2xl px-4 py-2.5 text-[15px] leading-relaxed ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-neutral-900 dark:text-neutral-100'
          }`}
        >
          {message.pending ? (
            <LoadingIndicator />
          ) : isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="markdown-body">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {!isUser && !message.pending && message.sources && <SourceCitation sources={message.sources} />}

        {!message.pending && (
          <button
            onClick={copy}
            className="mt-1 flex items-center gap-1 rounded px-1.5 py-0.5 text-xs text-neutral-400 opacity-0
                       transition-opacity hover:text-neutral-600 group-hover:opacity-100 dark:hover:text-neutral-300"
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        )}
      </div>
    </div>
  )
}
