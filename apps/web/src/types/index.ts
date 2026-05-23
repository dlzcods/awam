export interface Reference {
  title: string
  url: string
  publish_date: string
  theme: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  originalQuery?: string
  reformulatedQuery?: string
  references?: Reference[]
  executionTime?: number
}

export interface APIResponse {
  original_query: string
  reformulated_query: string
  answer: string
  references: Reference[]
  execution_time: number
}

export interface APIError {
  type: 'connection' | 'timeout' | 'http' | 'unknown'
  message: string
  statusCode?: number
}

export interface ChatState {
  messages: Message[]
  isLoading: boolean
  error: string | null
}

export type ChatAction =
  | { type: 'ADD_USER_MESSAGE'; payload: string }
  | { type: 'ADD_ASSISTANT_MESSAGE'; payload: AssistantMessageData }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_ERROR' }

export interface AssistantMessageData {
  answer: string
  originalQuery: string
  reformulatedQuery: string
  references: Reference[]
  executionTime: number
}
