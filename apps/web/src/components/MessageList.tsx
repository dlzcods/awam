import { useEffect, useRef, useCallback } from 'react'
import type { Message } from '@/types/index.ts'
import { MessageBubble } from './MessageBubble.tsx'
import { LoadingIndicator } from './LoadingIndicator.tsx'

interface MessageListProps {
  messages: Message[]
  isLoading: boolean
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const isNearBottomRef = useRef(true)

  const handleScroll = useCallback(() => {
    const el = containerRef.current
    if (!el) return
    const threshold = 150
    isNearBottomRef.current =
      el.scrollHeight - el.scrollTop - el.clientHeight < threshold
  }, [])

  useEffect(() => {
    const el = containerRef.current
    if (!el || !isNearBottomRef.current) return

    el.scrollTo({
      top: el.scrollHeight,
      behavior: 'smooth',
    })
  })

  const lastAssistantIdx = messages.reduce(
    (acc, msg, idx) => (msg.role === 'assistant' ? idx : acc),
    -1
  )

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      role="log"
      aria-live="polite"
      aria-label="Percakapan"
      className="flex-1 overflow-y-auto max-w-3xl mx-auto w-full px-6 sm:px-8 py-6 space-y-4 overscroll-contain"
    >
      {messages.map((message, idx) => (
        <MessageBubble
          key={message.id}
          message={message}
          isLatest={idx === lastAssistantIdx}
        />
      ))}
      {isLoading && <LoadingIndicator />}
    </div>
  )
}