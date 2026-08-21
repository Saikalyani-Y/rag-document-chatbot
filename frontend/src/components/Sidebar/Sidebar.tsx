import { FileStack, MessageSquarePlus, Sparkles } from 'lucide-react'
import { useChat } from '../../context/ChatContext'
import { DocumentUploader } from '../DocumentUploader/DocumentUploader'
import { DocumentManager } from '../DocumentManager/DocumentManager'
import { ChatHistoryList } from './ChatHistoryList'

export function Sidebar() {
  const { newChat } = useChat()

  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-950">
      <div className="flex items-center gap-2 px-4 py-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600 text-white">
          <Sparkles size={16} />
        </div>
        <span className="font-semibold text-neutral-900 dark:text-neutral-50">DocuMind</span>
      </div>

      <div className="px-3">
        <button
          onClick={newChat}
          className="flex w-full items-center gap-2 rounded-lg border border-neutral-200 dark:border-neutral-800
                     bg-white dark:bg-neutral-900 px-3 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-200
                     transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800"
        >
          <MessageSquarePlus size={15} />
          New chat
        </button>
      </div>

      <div className="mt-5 flex-1 overflow-y-auto px-3">
        <p className="mb-1.5 px-1 text-xs font-medium uppercase tracking-wide text-neutral-400">Chats</p>
        <ChatHistoryList />
      </div>

      <div className="border-t border-neutral-200 dark:border-neutral-800 px-3 py-4">
        <p className="mb-2 flex items-center gap-1.5 px-1 text-xs font-medium uppercase tracking-wide text-neutral-400">
          <FileStack size={12} /> Documents
        </p>
        <DocumentUploader />
        <div className="mt-3 max-h-56 overflow-y-auto">
          <DocumentManager />
        </div>
      </div>
    </aside>
  )
}
