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
  
</template>

<style scoped></style>
