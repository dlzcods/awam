import { X } from 'lucide-react'

interface ErrorBannerProps {
  message: string
  onDismiss?: () => void
}

export function ErrorBanner({ message, onDismiss }: ErrorBannerProps) {
  return (
    <div
      role="alert"
      className="mx-6 sm:mx-8 mb-3 flex items-start gap-3 rounded-xl border border-danger/30
                 bg-danger/5 px-4 py-3 text-sm text-danger animate-slide-up"
    >
      <span className="flex-1">{message}</span>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Tutup pesan error"
          className="shrink-0 size-6 flex items-center justify-center rounded
                     text-danger/60 hover:text-danger hover:bg-danger/10
                     transition-colors cursor-pointer"
        >
          <X className="size-3.5" />
        </button>
      )}
    </div>
  )
}