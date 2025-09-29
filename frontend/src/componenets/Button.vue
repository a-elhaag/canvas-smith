<script setup lang="ts">
import { ref, computed } from 'vue'

// Props interface
interface ButtonProps {
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
}

// Props with defaults
const props = withDefaults(defineProps<ButtonProps>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
})

// Emits
const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

// Reactive state
const isHovered = ref(false)
const isPressed = ref(false)

const handleClick = (event: MouseEvent) => {
  if (!props.disabled) {
    emit('click', event)
  }
}

const handleMouseLeave = () => {
  isHovered.value = false
  isPressed.value = false
}
// Computed classes
const buttonClasses = computed(() => {
  const baseClasses = [
    'inline-flex',
    'items-center',
    'justify-center',
    'font-medium',
    'transition-all',
    'duration-300',
    'ease-out',
    'outline-none',
    'select-none',
    'relative',
    'overflow-hidden',
  ]

  // Size classes
  const sizeClasses = {
    sm: ['w-20', 'h-8', 'text-xs', isHovered.value ? 'rounded-md' : 'rounded-xl'],
    md: ['w-30', 'h-10', 'text-sm', isHovered.value ? 'rounded-lg' : 'rounded-2xl'],
    lg: ['w-40', 'h-12', 'text-base', isHovered.value ? 'rounded-xl' : 'rounded-3xl'],
  }

  // Variant classes
  const variantClasses = {
    primary: [
      props.disabled
        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
        : 'bg-canvas-accent text-white cursor-pointer',
      !props.disabled && isHovered.value && 'shadow-lg shadow-canvas-accent/30',
      !props.disabled && isPressed.value && 'scale-95',
      !props.disabled && isHovered.value && !isPressed.value && 'scale-102 -translate-y-0.5',
    ],
    secondary: [
      props.disabled
        ? 'bg-gray-100 text-gray-400 border border-gray-200 cursor-not-allowed'
        : 'bg-canvas-surface text-canvas-text border border-gray-200 cursor-pointer hover:border-gray-300',
      !props.disabled && isHovered.value && 'shadow-lg shadow-black/10',
      !props.disabled && isPressed.value && 'scale-95',
      !props.disabled && isHovered.value && !isPressed.value && 'scale-101 -translate-y-0.5',
    ],
  }

  return [...baseClasses, ...sizeClasses[props.size], ...variantClasses[props.variant]].filter(
    Boolean,
  )
})
</script>

<template>
  <button
    :class="buttonClasses"
    :disabled="disabled"
    @click="handleClick"
    @mouseenter="isHovered = true"
    @mouseleave="handleMouseLeave"
    @mousedown="isPressed = true"
    @mouseup="isPressed = false"
    type="button"
  >
    <slot />
  </button>
</template>

<style scoped>
/* Additional custom styles if needed */
.w-30 {
  width: 7.5rem; /* 120px */
}

/* Ensure smooth transitions for dynamic classes */
button {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
