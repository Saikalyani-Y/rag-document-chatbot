import { AlertTriangle, CheckCircle2, FileText, Loader2, Trash2 } from 'lucide-react'
import { useDocuments } from '../../context/DocumentsContext'
import type { DocumentItem } from '../../types'

function StatusBadge({ status }: { status: DocumentItem['status'] }) {
  if (status === 'ready') {
    return (
      <span className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
        <CheckCircle2 size={12} /> Ready
      </span>
    )
  }
  if (status === 'failed') {
    return (
      <span className="flex items-center gap-1 text-xs text-red-500">
        <AlertTriangle size={12} /> Failed
      </span>
    )
  }
  return (
    <span className="flex items-center gap-1 text-xs text-amber-500">
      <Loader2 size={12} className="animate-spin" /> Processing
    </span>
  )
}

export function DocumentManager() {
  const { documents, loading, remove } = useDocuments()

  if (loading) {
    return <p className="px-1 text-xs text-neutral-400">Loading documents...</p>
  }

  if (documents.length === 0) {
    return <p className="px-1 text-xs text-neutral-400">No documents uploaded yet.</p>
  }

  return (
    <ul className="flex flex-col gap-1.5">
      {documents.map((doc) => (
        <li
          key={doc.id}
          className="group flex items-start gap-2 rounded-lg px-1.5 py-1.5 hover:bg-neutral-100 dark:hover:bg-neutral-800/60"
        >
          <FileText size={14} className="mt-0.5 shrink-0 text-neutral-400" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-medium text-neutral-700 dark:text-neutral-200" title={doc.filename}>
              {doc.filename}
            </p>
            <div className="mt-0.5 flex items-center gap-2 text-[11px] text-neutral-400">
              <StatusBadge status={doc.status} />
              <span>·</span>
              <span>{doc.file_type.toUpperCase()}</span>
              {doc.status === 'ready' && (
                <>
                  <span>·</span>
                  <span>{doc.chunk_count} chunks</span>
                </>
              )}
            </div>
            {doc.status === 'failed' && doc.error_message && (
              <p className="mt-0.5 text-[11px] text-red-500">{doc.error_message}</p>
            )}
          </div>
          <button
            onClick={() => remove(doc.id)}
            aria-label={`Delete ${doc.filename}`}
            className="shrink-0 rounded p-1 text-neutral-300 opacity-0 transition-opacity hover:text-red-500 group-hover:opacity-100"
          >
            <Trash2 size={13} />
          </button>
        </li>
      ))}
    </ul>
  )
}
