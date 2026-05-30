import { useState, type KeyboardEvent } from 'react'
import { ArrowUp, Loader2 } from 'lucide-react'

interface InputBarProps {
  onSubmit: (query: string) => void
  disabled: boolean
}

export function InputBar({ onSubmit, disabled }: InputBarProps) {
  const [value, setValue] = useState('')

  function handleSubmit() {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSubmit(trimmed)
    setValue('')
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="border-t border-border px-6 sm:px-8 py-4 bg-background safe-bottom">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-end gap-2 bg-white dark:bg-input border border-border rounded-2xl px-4 py-2
                        focus-within:border-brand focus-within:ring-2 focus-within:ring-brand/20
                        transition-all shadow-sm">
          <textarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Tanya apa aja soal hukum..."
            disabled={disabled}
            rows={1}
            maxLength={1000}
            aria-label="Ketik pertanyaan hukum"
            className="flex-1 resize-none bg-transparent text-[15px] text-foreground
                       placeholder:text-dimmed outline-none py-2 min-h-0
                       disabled:opacity-60"
          />
          <button
            type="button"
            onClick={handleSubmit}
            disabled={disabled || !value.trim()}
            aria-label="Kirim pertanyaan"
            className="shrink-0 size-10 flex items-center justify-center rounded-full
                       bg-brand text-brand-foreground
                       disabled:opacity-40 transition-all cursor-pointer
                       disabled:cursor-not-allowed hover:bg-brand-hover
                       active:scale-95"
          >
            {disabled ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <ArrowUp className="size-4" />
            )}
          </button>
        </div>
        <p className="text-xs text-center text-dimmed mt-2">
          AWAM bisa membuat kesalahan. Verifikasi informasi penting dengan sumber resmi.
        </p>
      </div>
    </div>
  )
}