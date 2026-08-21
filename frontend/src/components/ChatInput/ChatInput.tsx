import { useRef, useState, type KeyboardEvent } from 'react'
import { ArrowUp } from 'lucide-react'

export function ChatInput({ onSend, disabled }: { onSend: (content: string) => void; disabled: boolean }) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }

  return (
    <div className="flex items-end gap-2 rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-2 shadow-sm">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => {
          setValue(e.target.value)
          handleInput()
        }}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        rows={1}
        placeholder="Ask a question about your documents..."
        className="max-h-[200px] flex-1 resize-none bg-transparent px-2 py-1.5 text-[15px] outline-none
                   placeholder:text-neutral-400 disabled:opacity-60"
      />
      <button
        onClick={submit}
        disabled={disabled || !value.trim()}
        aria-label="Send message"
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white
                   transition-opacity hover:bg-blue-700 disabled:opacity-30 disabled:hover:bg-blue-600"
      >
        <ArrowUp size={18} />
      </button>
    </div>
  )
}
