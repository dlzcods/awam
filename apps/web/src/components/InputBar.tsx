import { useState, type KeyboardEvent } from 'react'
import { ArrowUp } from 'lucide-react'

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

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="border-t border-[#e5e7eb] px-4 py-11 bg-white">
      <div className="max-w-3xl mx-auto flex items-center gap-2">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Tanya apa aja soal hukum..."
          disabled={disabled}
          maxLength={1000}
          aria-label="Ketik pertanyaan hukum"
          className="flex-1 h-10 px-4 text-[15px] text-[#1a1a1a] placeholder:text-[#9ca3af] border border-[#d1d5db] rounded-lg bg-white outline-none focus:border-[#2c5f6e] transition-colors disabled:opacity-60"
        />
        <button
          type="button"
          onClick={handleSubmit}
          disabled={disabled || !value.trim()}
          aria-label="Kirim pertanyaan"
          className="size-10 flex items-center justify-center rounded-full bg-[#2c5f6e] text-white disabled:opacity-40 transition-opacity cursor-pointer disabled:cursor-not-allowed"
        >
          <ArrowUp className="size-4" />
        </button>
      </div>
    </div>
  )
}
