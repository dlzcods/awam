import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Message, Reference } from '@/types/index.ts'
import { QueryReformulationDisplay } from './QueryReformulationDisplay.tsx'
import { ReferenceCard } from './ReferenceCard.tsx'
import { CitationMark } from './CitationMark.tsx'
import { useTypewriter } from '@/lib/use-typewriter.ts'

interface MessageBubbleProps {
  message: Message
  isLatest?: boolean
}

function cleanMarkdown(raw: string): string {
  let text = raw.replace(/\r\n/g, '\n')
  text = text.replace(/([^\n])\n(#{1,6}\s)/g, '$1\n\n$2')
  text = text.replace(/([^\n])\n(\d+\.\s)/g, '$1\n\n$2')
  text = text.replace(/([^\n])\n([-*]\s)/g, '$1\n\n$2')
  text = text.replace(/\\\*\\\*/g, '**')
  return text
}

function renderTextWithCitations(text: string, references: Reference[]) {
  const parts = text.split(/(\[\d+\])/)
  if (parts.length === 1) return text

  return parts.map((part, i) => {
    const match = part.match(/^\[(\d+)\]$/)
    if (match) {
      const num = parseInt(match[1], 10)
      const ref = references[num - 1]
      return <CitationMark key={i} number={num} reference={ref} />
    }
    return part
  })
}

function processChildren(children: React.ReactNode, references: Reference[]): React.ReactNode {
  if (!children) return children
  const childArray = Array.isArray(children) ? children : [children]
  return childArray.map((child, i) => {
    if (typeof child === 'string') {
      return <span key={i}>{renderTextWithCitations(child, references)}</span>
    }
    return child
  })
}

export function MessageBubble({ message, isLatest = false }: MessageBubbleProps) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end animate-slide-up">
        <div className="bg-brand text-brand-foreground rounded-2xl rounded-br-md
                        px-4 py-3 max-w-[90%] sm:max-w-[85%]
                        shadow-sm">
          <p className="text-[15px] leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
      </div>
    )
  }

  const fullContent = message.content || 'Hmm, gak ketemu jawaban yang pas. Coba tanya dengan cara lain?'
  const references = (message.references ?? []).slice(0, 8)

  const { displayedText, isTyping, skip } = useTypewriter({
    text: fullContent,
    speed: 12,
    enabled: isLatest,
  })

  const contentToRender = cleanMarkdown(displayedText)

  return (
    <div className="flex justify-start animate-slide-up">
      <div className="bg-card border border-border rounded-2xl rounded-bl-md
                      px-5 py-4 max-w-[90%] sm:max-w-[85%]
                      shadow-sm">
        {/* Markdown content with inline citations */}
        <div
          className={[
            '[&_p]:mb-5 [&_p]:leading-7',
            '[&_h1]:mt-8 [&_h1]:mb-4 [&_h1]:text-xl [&_h1]:font-bold',
            '[&_h2]:mt-7 [&_h2]:mb-3 [&_h2]:text-lg [&_h2]:font-semibold',
            '[&_h3]:mt-6 [&_h3]:mb-3 [&_h3]:font-semibold',
            '[&_ul]:my-4 [&_ul]:pl-5 [&_ul]:list-disc',
            '[&_ol]:my-4 [&_ol]:pl-5 [&_ol]:list-decimal',
            '[&_li]:mb-2 [&_li]:leading-7',
            '[&_strong]:font-semibold',
            '[&_a]:text-brand [&_a]:underline',
            'text-[15px] text-foreground [&_p:last-child]:mb-0',
          ].join(' ')}
        >
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ children }) => (
                <p>{processChildren(children, references)}</p>
              ),
              li: ({ children }) => (
                <li>{processChildren(children, references)}</li>
              ),
            }}
          >
            {contentToRender}
          </ReactMarkdown>
        </div>

        {/* Skip button while typing */}
        {isTyping && (
          <button
            type="button"
            onClick={skip}
            className="text-xs text-muted hover:text-foreground mt-2
                       transition-colors cursor-pointer"
          >
            Tampilkan semua
          </button>
        )}

        {/* Show metadata only after typing is done */}
        {!isTyping && (
          <>
            {/* Query reformulation */}
            {message.originalQuery && message.reformulatedQuery && (
              <div className="border-t border-border mt-4 pt-3">
                <QueryReformulationDisplay
                  originalQuery={message.originalQuery}
                  reformulatedQuery={message.reformulatedQuery}
                />
              </div>
            )}

            {/* Execution time */}
            {message.executionTime != null && message.executionTime > 0 && (
              <div className="border-t border-border mt-4 pt-3">
                <p className="text-xs text-muted">
                  Waktu proses: {message.executionTime.toFixed(2)} detik
                </p>
              </div>
            )}

            {/* References */}
            {references.length > 0 && (
              <div className="border-t border-border mt-4 pt-3">
                <p className="text-xs font-semibold text-muted mb-2.5 uppercase tracking-wide">
                  Referensi
                </p>
                <div className="grid grid-cols-1 gap-2">
                  {references.map((ref, idx) => (
                    <ReferenceCard key={idx} reference={ref} index={idx + 1} />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}