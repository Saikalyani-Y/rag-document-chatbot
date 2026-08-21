import { FileText, Globe } from 'lucide-react'
import type { Source } from '../../types'

export function SourceCitation({ sources }: { sources: Source[] }) {
  if (!sources.length) return null

  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {sources.map((source) => {
        const key = `${source.kind}-${source.document_id ?? source.url}-${source.chunk_id}`
        const pillClasses =
          'inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs transition-colors ' +
          (source.kind === 'web'
            ? 'border-blue-200 dark:border-blue-900 bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/40'
            : 'border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900 text-neutral-600 dark:text-neutral-300')

        const content = (
          <>
            {source.kind === 'web' ? <Globe size={12} className="shrink-0" /> : <FileText size={12} className="shrink-0" />}
            <span className="max-w-[14rem] truncate">{source.filename}</span>
            <span className="opacity-60">· {source.label}</span>
          </>
        )

        if (source.kind === 'web' && source.url) {
          return (
            <a key={key} href={source.url} target="_blank" rel="noreferrer" className={pillClasses}>
              {content}
            </a>
          )
        }

        return (
          <div key={key} title={`Similarity: ${source.score.toFixed(2)}`} className={pillClasses}>
            {content}
          </div>
        )
      })}
    </div>
  )
}
