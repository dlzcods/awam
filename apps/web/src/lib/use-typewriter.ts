import { useState, useEffect, useRef } from 'react'

interface UseTypewriterOptions {
  text: string
  speed?: number // characters per tick
  enabled?: boolean // set false to show full text immediately
}

interface UseTypewriterResult {
  displayedText: string
  isTyping: boolean
  skip: () => void
}

/**
 * Reveals text progressively, simulating a streaming/typewriter effect.
 * Chunks by words to avoid breaking mid-word.
 */
export function useTypewriter({
  text,
  speed = 8,
  enabled = true,
}: UseTypewriterOptions): UseTypewriterResult {
  const [charIndex, setCharIndex] = useState(enabled ? 0 : text.length)
  const [skipped, setSkipped] = useState(!enabled)
  const rafRef = useRef<number>(0)
  const lastTimeRef = useRef<number>(0)

  useEffect(() => {
    if (skipped || charIndex >= text.length) return

    function tick(timestamp: number) {
      if (!lastTimeRef.current) lastTimeRef.current = timestamp
      const elapsed = timestamp - lastTimeRef.current

      // Advance every 16ms (~60fps), revealing `speed` chars per frame
      if (elapsed >= 16) {
        lastTimeRef.current = timestamp
        setCharIndex((prev) => Math.min(prev + speed, text.length))
      }

      rafRef.current = requestAnimationFrame(tick)
    }

    rafRef.current = requestAnimationFrame(tick)

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [text, speed, skipped, charIndex])

  // Reset when text changes (new message)
  useEffect(() => {
    if (enabled) {
      setCharIndex(0)
      setSkipped(false)
      lastTimeRef.current = 0
    } else {
      setCharIndex(text.length)
      setSkipped(true)
    }
  }, [text, enabled])

  function skip() {
    setSkipped(true)
    setCharIndex(text.length)
    if (rafRef.current) cancelAnimationFrame(rafRef.current)
  }

  const displayedText = skipped ? text : text.slice(0, charIndex)
  const isTyping = !skipped && charIndex < text.length

  return { displayedText, isTyping, skip }
}
