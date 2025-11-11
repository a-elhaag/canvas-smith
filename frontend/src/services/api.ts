/**
 * API Service for Canvas Smith
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface TokenUsage {
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  estimated_cost_usd: number
}

export interface ComponentAnalysis {
  component_type: string
  has_script_setup: boolean
  has_typescript: boolean
  interactive_elements: Record<string, number>
  animations: Record<string, number>
  styling: Record<string, boolean>
  vue_features: Record<string, boolean>
}

export interface CodeGenerationResponse {
  success: boolean
  generated_code: string
  finish_reason: string
  token_usage: TokenUsage
  component_analysis: ComponentAnalysis
  metadata: Record<string, any>
  timestamp: string
  processing_time_ms: number
}

export interface ApiError {
  detail: string
  status?: number
}

export class CanvasSmithAPI {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/health`)
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Generate Vue.js code from canvas image
   */
  async generateCode(
    imageFile: File,
    description?: string,
  ): Promise<CodeGenerationResponse> {
    const formData = new FormData()
    formData.append('image', imageFile)
    if (description) {
      formData.append('description', description)
    }

    const response = await fetch(`${this.baseUrl}/api/ai/generate-code`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: response.statusText,
        status: response.status,
      }))
      throw new Error(error.detail || 'Failed to generate code')
    }

    return response.json()
  }

  /**
   * Generate code with streaming support
   */
  async generateCodeStreaming(
    imageFile: File,
    description?: string,
    onChunk?: (chunk: string) => void,
  ): Promise<string> {
    const formData = new FormData()
    formData.append('image', imageFile)
    if (description) {
      formData.append('description', description)
    }

    const response = await fetch(`${this.baseUrl}/api/ai/generate-code-streaming`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: response.statusText,
        status: response.status,
      }))
      throw new Error(error.detail || 'Failed to generate code')
    }

    if (!response.body) {
      throw new Error('Response body is null')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let fullCode = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        fullCode += chunk

        if (onChunk) {
          onChunk(chunk)
        }
      }

      return fullCode
    } finally {
      reader.releaseLock()
    }
  }

  /**
   * Convert canvas to blob
   */
  static canvasToBlob(canvas: HTMLCanvasElement): Promise<Blob> {
    return new Promise((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob)
        } else {
          reject(new Error('Failed to convert canvas to blob'))
        }
      }, 'image/png')
    })
  }

  /**
   * Convert canvas to file
   */
  static async canvasToFile(canvas: HTMLCanvasElement, filename = 'canvas.png'): Promise<File> {
    const blob = await CanvasSmithAPI.canvasToBlob(canvas)
    return new File([blob], filename, { type: 'image/png' })
  }
}

// Export singleton instance
export const api = new CanvasSmithAPI()
