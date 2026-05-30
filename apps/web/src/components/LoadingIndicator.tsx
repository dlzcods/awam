export function LoadingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-5 py-4 max-w-[85%] mr-auto" role="status" aria-label="Memuat jawaban">
      <span className="sr-only">Memuat jawaban...</span>
      <span className="size-2 rounded-full bg-dimmed animate-bounce [animation-delay:0ms]" aria-hidden="true" />
      <span className="size-2 rounded-full bg-dimmed animate-bounce [animation-delay:150ms]" aria-hidden="true" />
      <span className="size-2 rounded-full bg-dimmed animate-bounce [animation-delay:300ms]" aria-hidden="true" />
    </div>
  )
}