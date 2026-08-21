import { FileText } from 'lucide-react'
import type { Source } from '../../types'

export function SourceCitation({ sources }: { sources: Source[] }) {
  if (!sources.length) return null

  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {sources.map((source) => (
        <div
          key={`${source.document_id}-${source.chunk_id}`}
          title={`Similarity: ${source.score.toFixed(2)}`}
          className="inline-flex items-center gap-1 rounded-full border border-neutral-200 dark:border-neutral-700
                     bg-neutral-50 dark:bg-neutral-900 px-2.5 py-1 text-xs text-neutral-600 dark:text-neutral-300"
        >
          <FileText size={12} className="shrink-0" />
          <span className="max-w-[14rem] truncate">{source.filename}</span>
          <span className="text-neutral-400 dark:text-neutral-500">· {source.label}</span>
        </div>
      ))}
    </div>
  )
}
