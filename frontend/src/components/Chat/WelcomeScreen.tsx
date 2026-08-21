import { FileSearch, ListChecks, Scale, Sparkles } from 'lucide-react'
import { useDocuments } from '../../context/DocumentsContext'

const SUGGESTIONS = [
  { icon: Sparkles, label: 'Summarize my document', prompt: 'Summarize the uploaded document in a few sentences.' },
  { icon: FileSearch, label: 'Find key information', prompt: 'What are the key points covered in this document?' },
  { icon: ListChecks, label: 'Explain this document', prompt: 'Explain what this document is about in simple terms.' },
  { icon: Scale, label: 'Compare documents', prompt: 'Compare and contrast the uploaded documents.' },
]

export function WelcomeScreen({ onSuggestion }: { onSuggestion: (prompt: string) => void }) {
  const { documents } = useDocuments()
  const hasDocuments = documents.some((d) => d.status === 'ready')

  return (
    <div className="flex h-full flex-col items-center justify-center px-6 text-center">
      <h1 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Ask your documents anything</h1>
      <p className="mt-2 max-w-md text-sm text-neutral-500 dark:text-neutral-400">
        Upload documents and use AI to search, understand, summarize, and answer questions based on your knowledge base.
      </p>

      {!hasDocuments && (
        <p className="mt-4 rounded-lg bg-amber-50 dark:bg-amber-900/20 px-3 py-2 text-xs text-amber-700 dark:text-amber-300">
          Upload a document from the sidebar to get started.
        </p>
      )}

      <div className="mt-8 grid w-full max-w-lg grid-cols-1 gap-2 sm:grid-cols-2">
        {SUGGESTIONS.map(({ icon: Icon, label, prompt }) => (
          <button
            key={label}
            onClick={() => onSuggestion(prompt)}
            disabled={!hasDocuments}
            className="flex items-center gap-2 rounded-xl border border-neutral-200 dark:border-neutral-800
                       bg-white dark:bg-neutral-900 px-4 py-3 text-left text-sm text-neutral-700 dark:text-neutral-200
                       transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-800 disabled:opacity-40 disabled:hover:bg-white dark:disabled:hover:bg-neutral-900"
          >
            <Icon size={16} className="shrink-0 text-neutral-400" />
            {label}
          </button>
        ))}
      </div>
    </div>
  )
}
