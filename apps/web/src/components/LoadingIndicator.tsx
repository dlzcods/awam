export function LoadingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-5 py-4 max-w-[85%] mr-auto" aria-label="Memuat jawaban">
      <span className="size-2 rounded-full bg-[#9ca3af] animate-bounce [animation-delay:0ms]" />
      <span className="size-2 rounded-full bg-[#9ca3af] animate-bounce [animation-delay:150ms]" />
      <span className="size-2 rounded-full bg-[#9ca3af] animate-bounce [animation-delay:300ms]" />
    </div>
  )
}
