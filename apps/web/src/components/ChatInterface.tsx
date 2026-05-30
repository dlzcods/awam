import { useReducer, useCallback } from 'react'
import { chatReducer, initialState } from '@/lib/chat-reducer.ts'
import { sendQuery } from '@/lib/api-client.ts'
import { MessageList } from './MessageList.tsx'
import { InputBar } from './InputBar.tsx'
import { SampleQuestions } from './SampleQuestions.tsx'
import { ErrorBanner } from './ErrorBanner.tsx'

export function ChatInterface() {
  const [state, dispatch] = useReducer(chatReducer, initialState)

  const handleSubmit = useCallback(async (query: string) => {
    dispatch({ type: 'ADD_USER_MESSAGE', payload: query })
    dispatch({ type: 'SET_LOADING', payload: true })

    const result = await sendQuery(query)

    if (result.success === false) {
      dispatch({ type: 'SET_ERROR', payload: result.error.message })
      return
    }

    dispatch({
      type: 'ADD_ASSISTANT_MESSAGE',
      payload: {
        answer: result.data.answer,
        originalQuery: result.data.original_query,
        reformulatedQuery: result.data.reformulated_query,
        references: result.data.references,
        executionTime: result.data.execution_time,
      },
    })
  }, [])

  const isEmpty = state.messages.length === 0

  return (
    <div className="flex flex-col flex-1 min-h-0">
      {isEmpty ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-6 px-6 sm:px-8 py-10
                        sm:py-16">
          {/* Hero area */}
          <div className="text-center max-w-ml space-y-3 animate-fade-in">
            {/* <div className="inline-flex size-16 items-center justify-center rounded-2xl
                            bg-brand-muted mb-2">
              <svg className="size-8 text-brand" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"
                   strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
            </div> */}
            <h2 className="text-2xl font-bold text-foreground leading-snug">
              Bebas curhat urusan legal, tanpa pusing susun kata formal.
            </h2>
            <p className="text-sm text-muted leading-relaxed">
              Takut bingung nanya soal hukum? Curhatin dulu aja keluhanmu di sini,
              nanti kami bantu jelaskan dan carikan landasan aturannya.
            </p>
          </div>

          <SampleQuestions onSelect={handleSubmit} />
        </div>
      ) : (
        <MessageList messages={state.messages} isLoading={state.isLoading} />
      )}

      {state.error && (
        <ErrorBanner
          message={state.error}
          onDismiss={() => dispatch({ type: 'CLEAR_ERROR' })}
        />
      )}

      <InputBar onSubmit={handleSubmit} disabled={state.isLoading} />
    </div>
  )
}