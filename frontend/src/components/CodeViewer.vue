<template>
  <div class="w-full bg-surface rounded-lg shadow-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold">Generated Vue Component</h3>
      <div class="flex gap-2">
        <button
          @click="copyCode"
          class="px-3 py-1 text-sm bg-primary text-white rounded hover:bg-primary-dark transition"
        >
          {{ copied ? '✓ Copied!' : 'Copy' }}
        </button>
        <button
          @click="downloadCode"
          class="px-3 py-1 text-sm bg-accent text-white rounded hover:bg-accent-dark transition"
        >
          Download
        </button>
      </div>
    </div>

    <div class="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto max-h-96 overflow-y-auto">
      <pre class="text-sm"><code>{{ code }}</code></pre>
    </div>

    <div v-if="metadata" class="mt-4 grid grid-cols-2 gap-4 text-sm">
      <div class="bg-gray-50 p-3 rounded">
        <span class="font-medium">Tokens:</span> {{ metadata.token_usage?.total_tokens || 0 }}
      </div>
      <div class="bg-gray-50 p-3 rounded">
        <span class="font-medium">Cost:</span> ${{
          (metadata.token_usage?.estimated_cost_usd || 0).toFixed(4)
        }}
      </div>
      <div class="bg-gray-50 p-3 rounded">
        <span class="font-medium">Processing:</span> {{ metadata.processing_time_ms || 0 }}ms
      </div>
      <div class="bg-gray-50 p-3 rounded">
        <span class="font-medium">Type:</span>
        {{ metadata.component_analysis?.component_type || 'vue' }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  code: string
  metadata?: any
}

const props = defineProps<Props>()
const copied = ref(false)

function copyCode() {
  navigator.clipboard.writeText(props.code)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

function downloadCode() {
  const blob = new Blob([props.code], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'Component.vue'
  a.click()
  URL.revokeObjectURL(url)
}
</script>
