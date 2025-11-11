<template>
  <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="[
          'pointer-events-auto px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 min-w-[300px] max-w-md',
          toastClasses[toast.type],
        ]"
      >
        <component :is="getIcon(toast.type)" class="w-5 h-5 flex-shrink-0" />
        <p class="flex-1 text-sm font-medium">{{ toast.message }}</p>
        <button
          @click="remove(toast.id)"
          class="flex-shrink-0 hover:opacity-70 transition"
          aria-label="Close"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue'
import { useToast, type ToastType } from '../composables/useToast'

const { toasts, remove } = useToast()

const toastClasses: Record<ToastType, string> = {
  success: 'bg-green-50 text-green-900 border border-green-200',
  error: 'bg-red-50 text-red-900 border border-red-200',
  warning: 'bg-yellow-50 text-yellow-900 border border-yellow-200',
  info: 'bg-blue-50 text-blue-900 border border-blue-200',
}

const getIcon = (type: ToastType) => {
  const icons: Record<ToastType, string> = {
    success:
      'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    error:
      'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
    warning:
      'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
    info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  }

  return () =>
    h(
      'svg',
      {
        fill: 'none',
        stroke: 'currentColor',
        viewBox: '0 0 24 24',
        class: 'w-5 h-5',
      },
      [
        h('path', {
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          'stroke-width': '2',
          d: icons[type],
        }),
      ],
    )
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100px) scale(0.9);
}
</style>
