import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingSpinner from './LoadingSpinner.vue'

describe('LoadingSpinner', () => {
  it('should render with default message', () => {
    const wrapper = mount(LoadingSpinner)
    
    expect(wrapper.text()).toContain('Generating code...')
    expect(wrapper.text()).toContain('This may take a few moments')
  })

  it('should render with custom message', () => {
    const wrapper = mount(LoadingSpinner, {
      props: {
        message: 'Processing...',
        subMessage: 'Please wait',
      },
    })
    
    expect(wrapper.text()).toContain('Processing...')
    expect(wrapper.text()).toContain('Please wait')
  })

  it('should render spinner animation', () => {
    const wrapper = mount(LoadingSpinner)
    
    expect(wrapper.find('.animate-spin').exists()).toBe(true)
    expect(wrapper.find('.animate-pulse').exists()).toBe(true)
  })
})
