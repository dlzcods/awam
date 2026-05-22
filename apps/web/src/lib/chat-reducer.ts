import type { ChatState, ChatAction } from '@/types/index.ts'

export const initialState: ChatState = {
  messages: [],
  isLoading: false,
  error: null,
}

export function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'ADD_USER_MESSAGE':
      return {
        ...state,
        messages: [
          ...state.messages,
          {
            id: crypto.randomUUID(),
            role: 'user',
            content: action.payload,
            timestamp: Date.now(),
          },
        ],
        error: null,
      }

    case 'ADD_ASSISTANT_MESSAGE':
      return {
        ...state,
        messages: [
          ...state.messages,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: action.payload.answer,
            timestamp: Date.now(),
            originalQuery: action.payload.originalQuery,
            reformulatedQuery: action.payload.reformulatedQuery,
            references: action.payload.references,
            executionTime: action.payload.executionTime,
          },
        ],
        isLoading: false,
      }

    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }

    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false }

    case 'CLEAR_ERROR':
      return { ...state, error: null }

    default:
      return state
  }
}
