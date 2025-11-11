import { describe, it, expect, vi, beforeEach } from 'vitest'
import { CanvasSmithAPI } from './api'

describe('CanvasSmithAPI', () => {
  let api: CanvasSmithAPI

  beforeEach(() => {
    api = new CanvasSmithAPI('http://test-api.com')
    vi.clearAllMocks()
  })

  describe('healthCheck', () => {
    it('should return health status when API is healthy', async () => {
      vi.stubGlobal(
        'fetch',
        vi.fn().mockResolvedValue({
          ok: true,
          json: async () => ({ status: 'healthy', message: 'API is running' }),
        }),
      )

      const result = await api.healthCheck()

      expect(result).toEqual({
        status: 'healthy',
        message: 'API is running',
      })
      expect(fetch).toHaveBeenCalledWith('http://test-api.com/health')
    })

    it('should throw error when health check fails', async () => {
      vi.stubGlobal(
        'fetch',
        vi.fn().mockResolvedValue({
          ok: false,
          statusText: 'Internal Server Error',
        }),
      )

      await expect(api.healthCheck()).rejects.toThrow('Health check failed: Internal Server Error')
    })
  })

  describe('generateCode', () => {
    it('should send image file and return generated code', async () => {
      const mockFile = new File(['test'], 'test.png', { type: 'image/png' })
      const mockResponse = {
        success: true,
        generated_code: '<template><div>Test</div></template>',
        finish_reason: 'stop',
        token_usage: {
          prompt_tokens: 100,
          completion_tokens: 50,
          total_tokens: 150,
          estimated_cost_usd: 0.001,
        },
        component_analysis: {
          component_type: 'component',
          has_script_setup: true,
          has_typescript: false,
          interactive_elements: {},
          animations: {},
          styling: {},
          vue_features: {},
        },
        metadata: {},
        timestamp: '2024-01-01T00:00:00Z',
        processing_time_ms: 1000,
      }

      vi.stubGlobal(
        'fetch',
        vi.fn().mockResolvedValue({
          ok: true,
          json: async () => mockResponse,
        }),
      )

      const result = await api.generateCode(mockFile, 'test description')

      expect(result).toEqual(mockResponse)
      expect(fetch).toHaveBeenCalledWith(
        'http://test-api.com/api/ai/generate-code',
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData),
        }),
      )
    })

    it('should handle API errors gracefully', async () => {
      const mockFile = new File(['test'], 'test.png', { type: 'image/png' })

      vi.stubGlobal(
        'fetch',
        vi.fn().mockResolvedValue({
          ok: false,
          status: 400,
          json: async () => ({ detail: 'Invalid image format' }),
        }),
      )

      await expect(api.generateCode(mockFile)).rejects.toThrow('Invalid image format')
    })
  })

  describe('canvasToBlob', () => {
    it('should convert canvas to blob', async () => {
      const mockCanvas = {
        toBlob: vi.fn((callback) => {
          const blob = new Blob(['test'], { type: 'image/png' })
          callback(blob)
        }),
      } as unknown as HTMLCanvasElement

      const blob = await CanvasSmithAPI.canvasToBlob(mockCanvas)

      expect(blob).toBeInstanceOf(Blob)
      expect(mockCanvas.toBlob).toHaveBeenCalled()
    })

    it('should reject when blob creation fails', async () => {
      const mockCanvas = {
        toBlob: vi.fn((callback) => {
          callback(null)
        }),
      } as unknown as HTMLCanvasElement

      await expect(CanvasSmithAPI.canvasToBlob(mockCanvas)).rejects.toThrow(
        'Failed to convert canvas to blob',
      )
    })
  })

  describe('canvasToFile', () => {
    it('should convert canvas to file with correct filename', async () => {
      const mockCanvas = {
        toBlob: vi.fn((callback) => {
          const blob = new Blob(['test'], { type: 'image/png' })
          callback(blob)
        }),
      } as unknown as HTMLCanvasElement

      const file = await CanvasSmithAPI.canvasToFile(mockCanvas, 'test-canvas.png')

      expect(file).toBeInstanceOf(File)
      expect(file.name).toBe('test-canvas.png')
      expect(file.type).toBe('image/png')
    })
  })
})
