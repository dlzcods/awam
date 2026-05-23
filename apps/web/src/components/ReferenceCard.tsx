import type { Reference } from '@/types/index.ts'

interface ReferenceCardProps {
  reference: Reference
}

export function ReferenceCard({ reference }: ReferenceCardProps) {
  const title = reference.title?.trim() || 'No Title'
  const date = reference.publish_date?.slice(0, 10) || ''
  const hasUrl = Boolean(reference.url?.trim())

  return (
    <div className="border border-[#e5e7eb] rounded-lg px-3 py-2.5 bg-white">
      {hasUrl ? (
        <a
          href={reference.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-medium text-[#2c5f6e] hover:underline line-clamp-2 leading-snug"
        >
          {title}
        </a>
      ) : (
        <p className="text-sm font-medium text-[#1a1a1a] line-clamp-2 leading-snug">
          {title}
        </p>
      )}
      <div className="flex items-center gap-2 text-[#6b7280] text-xs mt-1">
        {date && <span>{date}</span>}
        {date && reference.theme && <span>·</span>}
        {reference.theme && (
          <span className="truncate">{reference.theme}</span>
        )}
      </div>
    </div>
  )
}
