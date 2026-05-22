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
        <div className="flex-1 flex flex-col items-center justify-center gap-8 px-4 py-12">
          <div className="text-center max-w-md space-y-2">
            <h2 className="text-xl font-semibold text-[#1a1a1a] leading-snug">
              Bebas curhat urusan legal, tanpa pusing susun kata formal.
            </h2>
            <p className="text-sm text-[#6b7280] leading-relaxed">
              Takut bingung nanya soal hukum? Curhatin dulu aja keluhanmu di sini, nanti kami bantu jelaskan dan carikan landasan aturannya.
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
