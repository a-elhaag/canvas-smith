<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Button from './componenets/Button.vue'

// Backend connection state
const backendStatus = ref<string>('checking...')
const backendMessage = ref<string>('Connecting to backend...')
const isConnected = ref<boolean>(false)
const isLoading = ref<boolean>(true)

// API base URL - change this for production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Function to test backend connection
const testBackendConnection = async () => {
  try {
    isLoading.value = true
    const response = await fetch(`${API_BASE_URL}/api/status`)

    if (response.ok) {
      const data = await response.json()
      backendStatus.value = data.backend_status
      backendMessage.value = data.message
      isConnected.value = true
    } else {
      throw new Error(`HTTP ${response.status}`)
    }
  } catch (error) {
    console.error('Backend connection failed:', error)
    backendStatus.value = 'disconnected'
    backendMessage.value = 'Failed to connect to backend'
    isConnected.value = false
  } finally {
    isLoading.value = false
  }
}

// Function to open API docs
const openApiDocs = () => {
  if (typeof window !== 'undefined') {
    window.open(`${API_BASE_URL}/docs`, '_blank')
  }
}

// Test connection on component mount
onMounted(() => {
  testBackendConnection()
})
</script>

<template>
  <div class="min-h-screen bg-canvas-bg p-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold text-canvas-text mb-8">Canvas Smith</h1>

      <!-- Backend Connection Status -->
      <div
        class="mb-8 p-4 rounded-lg border-2"
        :class="{
          'bg-green-50 border-green-200': isConnected,
          'bg-red-50 border-red-200': !isConnected && !isLoading,
          'bg-yellow-50 border-yellow-200': isLoading,
        }"
      >
        <h2
          class="text-lg font-semibold mb-2"
          :class="{
            'text-green-800': isConnected,
            'text-red-800': !isConnected && !isLoading,
            'text-yellow-800': isLoading,
          }"
        >
          Backend Connection Status
        </h2>

        <div class="flex items-center gap-2">
          <div
            class="w-3 h-3 rounded-full"
            :class="{
              'bg-green-500': isConnected,
              'bg-red-500': !isConnected && !isLoading,
              'bg-yellow-500 animate-pulse': isLoading,
            }"
          ></div>

          <span
            :class="{
              'text-green-700': isConnected,
              'text-red-700': !isConnected && !isLoading,
              'text-yellow-700': isLoading,
            }"
          >
            {{ backendMessage }}
          </span>
        </div>

        <p class="text-sm text-gray-600 mt-1">
          Status: {{ backendStatus }} | API: {{ API_BASE_URL }}
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="space-y-4">
        <Button variant="primary" size="md" @click="testBackendConnection" :disabled="isLoading">
          {{ isLoading ? 'Testing...' : 'Test Backend Connection' }}
        </Button>

        <Button variant="secondary" size="md" @click="() => console.log('Secondary clicked')">
          Secondary Button
        </Button>

        <Button variant="primary" size="lg" @click="openApiDocs"> Open API Documentation </Button>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
