import type { APIResponse, APIError } from '@/types/index.ts'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const REQUEST_TIMEOUT_MS = 120_000

export interface SendQueryResult {
  success: true
  data: APIResponse
}

export interface SendQueryError {
  success: false
  error: APIError
}

export type SendQueryResponse = SendQueryResult | SendQueryError

export async function sendQuery(query: string): Promise<SendQueryResponse> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  try {
    const response = await fetch(API_BASE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      const errorBody = await response.text()
      return {
        success: false,
        error: {
          type: 'http',
          message: `Ada yang error nih: ${errorBody}. Coba ulangi pertanyaannya.`,
          statusCode: response.status,
        },
      }
    }

    const data = await response.json()

    const parsed: APIResponse = {
      original_query: data.original_query ?? '',
      reformulated_query: data.reformulated_query ?? '',
      answer: data.answer ?? '',
      references: data.references ?? [],
      execution_time: data.execution_time ?? 0,
    }

    return { success: true, data: parsed }
  } catch (err: unknown) {
    clearTimeout(timeoutId)

    if (err instanceof DOMException && err.name === 'AbortError') {
      return {
        success: false,
        error: {
          type: 'timeout',
          message: 'Jawabannya lama banget nih, kayaknya server lagi sibuk. Coba lagi ya.',
        },
      }
    }

    if (err instanceof TypeError) {
      return {
        success: false,
        error: {
          type: 'connection',
          message: 'Waduh, server lagi gak bisa dihubungi. Coba lagi sebentar ya.',
        },
      }
    }

    return {
      success: false,
      error: {
        type: 'unknown',
        message: `Ada yang error nih: ${(err as Error).message ?? 'Unknown error'}. Coba ulangi pertanyaannya.`,
      },
    }
  }
}

export { API_BASE_URL }
