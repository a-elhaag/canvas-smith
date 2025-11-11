<template>
  <div class="flex flex-col items-center justify-center py-8">
    <div class="relative">
      <!-- Spinner -->
      <div class="w-16 h-16 border-4 border-gray-200 border-t-gray-900 rounded-full animate-spin"></div>
      
      <!-- Sparkle icon in center -->
      <div class="absolute inset-0 flex items-center justify-center">
        <svg
          class="w-6 h-6 text-gray-900 animate-pulse"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
          />
        </svg>
      </div>
    </div>

    <p class="mt-4 text-sm font-medium text-gray-900">{{ message }}</p>
    <p v-if="subMessage" class="mt-1 text-xs text-gray-500">{{ subMessage }}</p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  message?: string
  subMessage?: string
}

withDefaults(defineProps<Props>(), {
  message: 'Generating code...',
  subMessage: 'This may take a few moments',
})
</script>
