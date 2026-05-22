import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Message } from '@/types/index.ts'
import { QueryReformulationDisplay } from './QueryReformulationDisplay.tsx'
import { ReferenceCard } from './ReferenceCard.tsx'

interface MessageBubbleProps {
  message: Message
}

function cleanMarkdown(raw: string): string {
  let text = raw.replace(/\r\n/g, '\n')
  text = text.replace(/([^\n])\n(#{1,6}\s)/g, '$1\n\n$2')
  text = text.replace(/([^\n])\n(\d+\.\s)/g, '$1\n\n$2')
  text = text.replace(/([^\n])\n([-*]\s)/g, '$1\n\n$2')
  text = text.replace(/\\\*\\\*/g, '**')
  return text
}

export function MessageBubble({ message }: MessageBubbleProps) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="bg-[#2c5f6e] text-white rounded-xl rounded-br-sm px-4 py-3 max-w-[80%]">
          <p className="text-[15px] leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
      </div>
    )
  }

  const displayContent = message.content || 'Hmm, gak ketemu jawaban yang pas. Coba tanya dengan cara lain?'
  const references = (message.references ?? []).slice(0, 8)

  return (
    <div className="flex justify-start">
      <div className="bg-white border border-[#e5e7eb] rounded-xl rounded-bl-sm px-5 py-4 max-w-[85%]">
        {/* Markdown content */}
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
            '[&_a]:text-[#2c5f6e] [&_a]:underline',
            'text-[15px] text-[#1a1a1a] [&_p:last-child]:mb-0',
          ].join(' ')}
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {cleanMarkdown(displayContent)}
          </ReactMarkdown>
        </div>

        {/* Query reformulation */}
        {message.originalQuery && message.reformulatedQuery && (
          <div className="border-t border-[#f0f0f0] mt-4 pt-3">
            <QueryReformulationDisplay
              originalQuery={message.originalQuery}
              reformulatedQuery={message.reformulatedQuery}
            />
          </div>
        )}

        {/* Execution time */}
        {message.executionTime != null && message.executionTime > 0 && (
          <div className="border-t border-[#f0f0f0] mt-4 pt-3">
            <p className="text-xs text-[#6b7280]">
              Waktu proses: {message.executionTime.toFixed(2)} detik
            </p>
          </div>
        )}

        {/* References */}
        {references.length > 0 && (
          <div className="border-t border-[#f0f0f0] mt-4 pt-3">
            <p className="text-xs font-medium text-[#6b7280] mb-2">Referensi:</p>
            <div className="grid grid-cols-1 gap-2">
              {references.map((ref, idx) => (
                <ReferenceCard key={idx} reference={ref} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
