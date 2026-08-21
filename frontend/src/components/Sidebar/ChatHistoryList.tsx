import { MessageSquare, Trash2 } from 'lucide-react'
import { useChat } from '../../context/ChatContext'

export function ChatHistoryList() {
  const { conversations, activeId, selectConversation, removeConversation } = useChat()

  if (conversations.length === 0) {
    return <p className="px-1 text-xs text-neutral-400">No conversations yet.</p>
  }

  return (
    <ul className="flex flex-col gap-0.5">
      {conversations.map((c) => (
        <li key={c.id}>
          <button
            onClick={() => selectConversation(c.id)}
            className={`group flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm transition-colors ${
              activeId === c.id
                ? 'bg-neutral-200/70 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100'
                : 'text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800/60'
            }`}
          >
            <MessageSquare size={14} className="shrink-0 text-neutral-400" />
            <span className="flex-1 truncate">{c.title}</span>
            <span
              role="button"
              tabIndex={-1}
              onClick={(e) => {
                e.stopPropagation()
                removeConversation(c.id)
              }}
              aria-label={`Delete conversation ${c.title}`}
              className="shrink-0 rounded p-0.5 text-neutral-300 opacity-0 hover:text-red-500 group-hover:opacity-100"
            >
              <Trash2 size={12} />
            </span>
          </button>
        </li>
      ))}
    </ul>
  )
}
