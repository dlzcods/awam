import type { Reference } from '@/types/index.ts'

interface ReferenceCardProps {
  reference: Reference
  index?: number
}

export function ReferenceCard({ reference, index }: ReferenceCardProps) {
  const title = reference.title?.trim() || 'No Title'
  const date = reference.publish_date?.slice(0, 10) || ''
  const hasUrl = Boolean(reference.url?.trim())

  return (
    <div className="flex items-start gap-3 rounded-xl border border-border bg-card
                    p-3 hover:shadow-card hover:border-brand/30 transition-all
                    group animate-slide-up">
      {/* Accent bar */}
      <div className="w-1 self-stretch rounded-full bg-brand shrink-0" />

      {index != null && (
        <span className="text-xs font-semibold text-brand mt-0.5 shrink-0 tabular-nums min-w-[1.25rem]">
          [{index}]
        </span>
      )}
      <div className="min-w-0 flex-1">
        {hasUrl ? (
          <a
            href={reference.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-semibold text-foreground group-hover:text-brand
                       line-clamp-2 leading-snug transition-colors"
          >
            {title}
          </a>
        ) : (
          <p className="text-sm font-semibold text-foreground line-clamp-2 leading-snug">
            {title}
          </p>
        )}
        <div className="flex items-center gap-2 text-muted text-xs mt-1">
          {date && <span>{date}</span>}
          {date && reference.theme && <span>·</span>}
          {reference.theme && (
            <span className="inline-flex items-center px-1.5 py-0.5 rounded-md
                             bg-brand-muted text-brand text-xs truncate max-w-[160px]">
              {reference.theme}
            </span>
          )}
        </div>
      </div>
      {hasUrl && (
        <svg className="size-4 text-dimmed group-hover:text-brand shrink-0 mt-1 transition-colors"
             viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
             strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
          <polyline points="15 3 21 3 21 9" />
          <line x1="10" y1="14" x2="21" y2="3" />
        </svg>
      )}
    </div>
  )
}