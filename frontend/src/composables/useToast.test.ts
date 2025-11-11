import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { useToast } from './useToast'

describe('useToast', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    // Clear all toasts before each test
    const { toasts } = useToast()
    toasts.value = []
  })
  
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should add a toast message', () => {
    const { toasts, show } = useToast()
    
    show('Test message', 'info', 3000)
    
    expect(toasts.value).toHaveLength(1)
    expect(toasts.value[0].message).toBe('Test message')
    expect(toasts.value[0].type).toBe('info')
  })

  it('should remove toast after duration', () => {
    const { toasts, show } = useToast()
    
    show('Test message', 'info', 1000)
    expect(toasts.value).toHaveLength(1)
    
    vi.advanceTimersByTime(1000)
    expect(toasts.value).toHaveLength(0)
  })

  it('should add success toast', () => {
    const { toasts, success } = useToast()
    
    success('Success message')
    
    expect(toasts.value).toHaveLength(1)
    expect(toasts.value[0].type).toBe('success')
    expect(toasts.value[0].message).toBe('Success message')
  })

  it('should add error toast', () => {
    const { toasts, error } = useToast()
    
    error('Error message')
    
    expect(toasts.value).toHaveLength(1)
    expect(toasts.value[0].type).toBe('error')
    expect(toasts.value[0].message).toBe('Error message')
  })

  it('should manually remove toast', () => {
    const { toasts, show, remove } = useToast()
    
    const id = show('Test message', 'info', 0) // 0 duration = no auto-remove
    expect(toasts.value).toHaveLength(1)
    
    remove(id)
    expect(toasts.value).toHaveLength(0)
  })

  it('should handle multiple toasts', () => {
    const { toasts, success, error, info } = useToast()
    
    success('Success')
    error('Error')
    info('Info')
    
    expect(toasts.value).toHaveLength(3)
    expect(toasts.value[0].type).toBe('success')
    expect(toasts.value[1].type).toBe('error')
    expect(toasts.value[2].type).toBe('info')
  })
})
