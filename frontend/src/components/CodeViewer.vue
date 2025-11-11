<template>
  <div class="w-full bg-white rounded-lg border border-gray-200 overflow-hidden">
    <div class="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 class="text-sm font-semibold text-gray-900">Generated Vue Component</h3>
      </div>
      <div class="flex gap-2">
        <button
          @click="copyCode"
          class="px-3 py-1.5 text-xs font-medium bg-gray-900 text-white rounded-md hover:bg-gray-800 transition flex items-center gap-1"
        >
          <svg
            v-if="!copied"
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
          {{ copied ? 'Copied!' : 'Copy' }}
        </button>
        <button
          @click="downloadCode"
          class="px-3 py-1.5 text-xs font-medium bg-gray-100 text-gray-900 rounded-md hover:bg-gray-200 transition flex items-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
          Download
        </button>
      </div>
    </div>

    <div class="bg-gray-900 text-gray-100 p-4 overflow-x-auto max-h-[500px] overflow-y-auto">
      <pre class="text-sm font-mono leading-relaxed"><code>{{ code }}</code></pre>
    </div>

    <div v-if="metadata" class="px-4 py-3 bg-gray-50 border-t border-gray-200">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div class="flex flex-col">
          <span class="text-gray-500 font-medium">Tokens</span>
          <span class="text-gray-900 font-semibold mt-0.5">{{
            metadata.token_usage?.total_tokens || 0
          }}</span>
        </div>
        <div class="flex flex-col">
          <span class="text-gray-500 font-medium">Cost</span>
          <span class="text-gray-900 font-semibold mt-0.5"
            >${{ (metadata.token_usage?.estimated_cost_usd || 0).toFixed(4) }}</span
          >
        </div>
        <div class="flex flex-col">
          <span class="text-gray-500 font-medium">Time</span>
          <span class="text-gray-900 font-semibold mt-0.5"
            >{{ metadata.processing_time_ms || 0 }}ms</span
          >
        </div>
        <div class="flex flex-col">
          <span class="text-gray-500 font-medium">Type</span>
          <span class="text-gray-900 font-semibold mt-0.5">{{
            metadata.component_analysis?.component_type || 'vue'
          }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from '../composables/useToast'

interface Props {
  code: string
  metadata?: any
}

const props = defineProps<Props>()
const copied = ref(false)
const toast = useToast()

function copyCode() {
  navigator.clipboard.writeText(props.code).then(() => {
    copied.value = true
    toast.success('Code copied to clipboard!')
    setTimeout(() => {
      copied.value = false
    }, 2000)
  }).catch(() => {
    toast.error('Failed to copy code')
  })
}

function downloadCode() {
  const blob = new Blob([props.code], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'GeneratedComponent.vue'
  a.click()
  URL.revokeObjectURL(url)
  toast.success('Component downloaded successfully!')
}
</script>
