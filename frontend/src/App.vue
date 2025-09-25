<script setup lang="ts">
import Button from './componenets/Button.vue'
</script>

<template>
  <div class="min-h-screen bg-canvas-bg p-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold text-canvas-text mb-8">Canvas Smith</h1>

      <div class="space-y-4">
        <Button variant="primary" size="md" @click="() => console.log('Primary clicked')">
          Primary Button
        </Button>

        <Button variant="secondary" size="md" @click="() => console.log('Secondary clicked')">
          Secondary Button
        </Button>

        <Button variant="primary" size="lg" @click="() => console.log('Large clicked')">
          Large Button
        </Button>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
