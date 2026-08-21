import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { ApiError, deleteDocument, listDocuments, uploadDocument } from '../api/client'
import type { DocumentItem } from '../types'

interface DocumentsContextValue {
  documents: DocumentItem[]
  loading: boolean
  uploading: boolean
  error: string | null
  upload: (file: File) => Promise<void>
  remove: (id: string) => Promise<void>
  refresh: () => Promise<void>
  dismissError: () => void
}

const DocumentsContext = createContext<DocumentsContextValue | null>(null)

export function DocumentsProvider({ children }: { children: ReactNode }) {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      const docs = await listDocuments()
      setDocuments(docs)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to load documents.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const upload = useCallback(
    async (file: File) => {
      setUploading(true)
      setError(null)
      try {
        await uploadDocument(file)
        await refresh()
      } catch (err) {
        setError(err instanceof ApiError ? err.message : 'Upload failed. Please try again.')
        throw err
      } finally {
        setUploading(false)
      }
    },
    [refresh],
  )

  const remove = useCallback(async (id: string) => {
    setError(null)
    try {
      await deleteDocument(id)
      setDocuments((prev) => prev.filter((d) => d.id !== id))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to delete document.')
      throw err
    }
  }, [])

  const dismissError = useCallback(() => setError(null), [])

  return (
    <DocumentsContext.Provider value={{ documents, loading, uploading, error, upload, remove, refresh, dismissError }}>
      {children}
    </DocumentsContext.Provider>
  )
}

export function useDocuments() {
  const ctx = useContext(DocumentsContext)
  if (!ctx) throw new Error('useDocuments must be used within DocumentsProvider')
  return ctx
}
