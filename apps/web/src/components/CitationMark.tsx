import { useState, useRef } from 'react'
import type { Reference } from '@/types/index.ts'

interface CitationMarkProps {
  number: number
  reference?: Reference
}

export function CitationMark({ number, reference }: CitationMarkProps) {
  const [showTooltip, setShowTooltip] = useState(false)
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>(null)

  function openTooltip() {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    setShowTooltip(true)
  }

  function closeTooltip() {
    timeoutRef.current = setTimeout(() => setShowTooltip(false), 200)
  }

  function handleClick() {
    if (reference?.url && reference.url !== '#') {
      window.open(reference.url, '_blank', 'noopener,noreferrer')
    }
  }

  const title = reference?.title || `Sumber ${number}`

  return (
    <span className="relative inline-block">
      <sup
        onMouseEnter={openTooltip}
        onMouseLeave={closeTooltip}
        onFocus={openTooltip}
        onBlur={closeTooltip}
        onClick={handleClick}
        tabIndex={reference ? 0 : -1}
        role={reference ? 'button' : undefined}
        aria-label={`Sumber ${number}: ${title}`}
        className={`text-[11px] font-medium ml-0.5 ${
          reference
            ? 'text-brand cursor-pointer hover:underline focus:outline-2 focus:outline-brand rounded'
            : 'text-dimmed cursor-default'
        }`}
      >
        [{number}]
      </sup>
      {showTooltip && reference && (
        <span
          role="tooltip"
          onMouseEnter={openTooltip}
          onMouseLeave={closeTooltip}
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 z-50
                     w-64 px-3 py-2 text-xs text-foreground bg-popover
                     border border-popover-border rounded-lg shadow-popover
                     pointer-events-auto animate-fade-in"
        >
          <span className="font-medium line-clamp-2">{title}</span>
          {reference.publish_date && (
            <span className="block text-muted mt-0.5">
              {reference.publish_date.slice(0, 10)}
            </span>
          )}
          {reference.url && (
            <span className="block text-brand mt-0.5 truncate">
              Klik untuk buka sumber
            </span>
          )}
        </span>
      )}
    </span>
  )
}