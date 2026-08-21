import { useRef, useState, type DragEvent } from 'react'
import { CheckCircle2, Loader2, UploadCloud } from 'lucide-react'
import { useDocuments } from '../../context/DocumentsContext'

const ALLOWED = ['.pdf', '.txt', '.docx']
const MAX_SIZE_MB = 20

export function DocumentUploader() {
  const { upload, uploading } = useDocuments()
  const [dragging, setDragging] = useState(false)
  const [justUploaded, setJustUploaded] = useState<string | null>(null)
  const [localError, setLocalError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = async (file: File) => {
    setLocalError(null)
    const ext = `.${file.name.split('.').pop()?.toLowerCase()}`
    if (!ALLOWED.includes(ext)) {
      setLocalError(`Unsupported file type. Allowed: ${ALLOWED.join(', ')}`)
      return
    }
    if (file.size === 0) {
      setLocalError('This file is empty.')
      return
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setLocalError(`File exceeds the ${MAX_SIZE_MB}MB limit.`)
      return
    }

    try {
      await upload(file)
      setJustUploaded(file.name)
      setTimeout(() => setJustUploaded(null), 2500)
    } catch {
      // upload() already records the server-side error in DocumentsContext
    }
  }

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center gap-1.5 rounded-xl border-2 border-dashed px-3 py-5 text-center transition-colors ${
          dragging
            ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
            : 'border-neutral-200 dark:border-neutral-700 hover:border-neutral-300 dark:hover:border-neutral-600'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ALLOWED.join(',')}
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleFile(file)
            e.target.value = ''
          }}
        />
        {uploading ? (
          <>
            <Loader2 size={18} className="animate-spin text-blue-500" />
            <span className="text-xs text-neutral-500">Uploading and indexing...</span>
          </>
        ) : justUploaded ? (
          <>
            <CheckCircle2 size={18} className="text-green-500" />
            <span className="text-xs text-neutral-500">"{justUploaded}" is ready</span>
          </>
        ) : (
          <>
            <UploadCloud size={18} className="text-neutral-400" />
            <span className="text-xs text-neutral-500">Drag & drop or click to upload</span>
            <span className="text-[11px] text-neutral-400">PDF, TXT, DOCX · up to {MAX_SIZE_MB}MB</span>
          </>
        )}
      </div>
      {localError && <p className="mt-1.5 text-xs text-red-500">{localError}</p>}
    </div>
  )
}
