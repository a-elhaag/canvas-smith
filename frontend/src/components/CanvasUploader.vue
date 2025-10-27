<template>
  <div class="flex flex-col items-center gap-6 w-full">
    <!-- Canvas Container with Floating Toolbar -->
    <div class="relative w-full">
      <!-- Floating Toolbar -->
      <div class="floating-toolbar">
        <!-- Tools Section -->
        <div class="flex gap-1">
          <button
            v-for="tool in tools"
            :key="tool.id"
            @click="currentTool = tool.id"
            :class="['tool-btn-modern', currentTool === tool.id ? 'tool-btn-active' : '']"
            :title="tool.label"
          >
            <span class="text-xl">{{ tool.icon }}</span>
          </button>
        </div>

        <div class="toolbar-divider"></div>

        <!-- Stroke Color -->
        <div class="relative">
          <button
            @click="showColorPicker = !showColorPicker"
            class="tool-btn-modern"
            title="Stroke color"
          >
            <div class="w-5 h-5 rounded border-2 border-gray-300" :style="{ backgroundColor: currentColor }"></div>
          </button>
          <div v-if="showColorPicker" class="color-picker-panel">
            <div class="grid grid-cols-5 gap-2 mb-2">
              <button
                v-for="color in presetColors"
                :key="color"
                @click="selectColor(color)"
                class="w-8 h-8 rounded border-2 hover:scale-110 transition"
                :class="currentColor === color ? 'border-primary ring-2 ring-primary/20' : 'border-gray-300'"
                :style="{ backgroundColor: color }"
              ></button>
            </div>
            <input type="color" v-model="currentColor" @input="showColorPicker = false" class="w-full h-8 rounded cursor-pointer" />
          </div>
        </div>

        <!-- Grid Toggle -->
        <button
          @click="showGrid = !showGrid"
          class="tool-btn-modern"
          :class="{ 'tool-btn-active': showGrid }"
          :title="showGrid ? 'Hide grid' : 'Show grid'"
        >
          <span class="text-xl">⊞</span>
        </button>

        <div class="toolbar-divider"></div>

        <!-- Stroke Width -->
        <div class="flex items-center gap-2 px-2">
          <button
            v-for="width in strokeWidths"
            :key="width"
            @click="lineWidth = width"
            :class="['stroke-btn', lineWidth === width ? 'stroke-btn-active' : '']"
            :title="`${width}px stroke`"
          >
            <div class="stroke-preview" :style="{ height: `${width}px` }"></div>
          </button>
        </div>

        <div class="toolbar-divider"></div>

        <!-- Undo/Redo -->
        <button class="tool-btn-modern" @click="undo" title="Undo (Ctrl+Z)" :disabled="historyIndex < 0">
          <span class="text-lg">↶</span>
        </button>
        <button class="tool-btn-modern" @click="redo" title="Redo (Ctrl+Shift+Z)" :disabled="historyIndex >= history.length - 1">
          <span class="text-lg">↷</span>
        </button>

        <div class="toolbar-divider"></div>

        <!-- Clear -->
        <button class="tool-btn-modern" @click="clearCanvas" title="Clear canvas">
          <span class="text-lg">🗑️</span>
        </button>
      </div>

      <!-- Canvas -->
      <div class="canvas-wrapper" :class="{ 'grid-bg': showGrid }">
        <canvas
          ref="canvasRef"
          :width="width"
          :height="height"
          class="canvas-main"
          :class="{  'cursor-crosshair': currentTool !== 'text', 'cursor-text': currentTool === 'text' }"
          @mousedown="onMouseDown"
          @mousemove="onMouseMove"
          @mouseup="onMouseUp"
          @mouseleave="onMouseUp"
        ></canvas>
        
        <!-- Helper Text -->
        <div v-if="!hasDrawn" class="canvas-help-text">
          <div class="text-center text-gray-400">
            <p class="text-lg mb-2">Pick a tool & start drawing!</p>
            <p class="text-sm">Draw your UI wireframe using shapes and lines</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Actions -->
    <div class="flex items-center gap-3">
      <input type="file" accept="image/*" @change="onFileChange" class="hidden" ref="fileInputRef" />
      <button class="btn-secondary" @click="triggerFileInput">
        <span class="text-lg mr-2">📁</span>
        Upload Image
      </button>
      <button class="btn-primary-modern" :disabled="isUploading || !hasDrawn" @click="submitCanvas">
        <span v-if="!isUploading" class="text-lg mr-2">✨</span>
        <div v-else class="spinner-small mr-2"></div>
        {{ isUploading ? 'Generating...' : 'Generate Code' }}
      </button>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="error-box">
      <strong>Error:</strong> {{ error }}
    </div>

    <!-- Processing Status -->
    <div v-if="isUploading" class="status-box">
      <div class="spinner"></div>
      <div>
        <p class="font-medium">Processing your sketch...</p>
        <p class="text-xs text-blue-600">AI is analyzing your wireframe and generating Vue components</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const emit = defineEmits<{
  (e: 'code-generated', data: any): void
}>()

const width = 1000
const height = 600

type Tool = 'pen' | 'rectangle' | 'circle' | 'line' | 'text' | 'eraser'

interface ToolDef {
  id: Tool
  label: string
  icon: string
}

const tools: ToolDef[] = [
  { id: 'pen', label: 'Pen', icon: '✏️' },
  { id: 'rectangle', label: 'Rectangle', icon: '▭' },
  { id: 'circle', label: 'Circle', icon: '○' },
  { id: 'line', label: 'Line', icon: '/' },
  { id: 'text', label: 'Text', icon: 'T' },
  { id: 'eraser', label: 'Eraser', icon: '🧹' },
]

const canvasRef = ref<HTMLCanvasElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const currentTool = ref<Tool>('pen')
const currentColor = ref('#1e293b')
const lineWidth = ref(2)
const showColorPicker = ref(false)
const showGrid = ref(true)
const isDrawing = ref(false)
const startPoint = ref<{ x: number; y: number } | null>(null)
const lastPoint = ref<{ x: number; y: number } | null>(null)
const isUploading = ref(false)
const error = ref<string | null>(null)
const hasDrawn = ref(false)

const presetColors = [
  '#1e293b', // slate-800
  '#ef4444', // red-500
  '#f59e0b', // amber-500
  '#10b981', // emerald-500
  '#3b82f6', // blue-500
  '#8b5cf6', // violet-500
  '#ec4899', // pink-500
  '#64748b', // slate-500
  '#ffffff', // white
  '#000000', // black
]

const strokeWidths = [1, 2, 4, 8]

// History for undo/redo
const history = ref<string[]>([])
const historyIndex = ref(-1)

function getCanvasCtx() {
  return canvasRef.value?.getContext('2d') ?? null
}

function selectColor(color: string) {
  currentColor.value = color
  showColorPicker.value = false
}

function saveState() {
  const canvas = canvasRef.value
  if (!canvas) return
  const dataUrl = canvas.toDataURL()
  // Remove any states after current index (when drawing after undo)
  history.value = history.value.slice(0, historyIndex.value + 1)
  history.value.push(dataUrl)
  historyIndex.value = history.value.length - 1
  hasDrawn.value = true
}

function restoreState(index: number) {
  if (index < 0 || index >= history.value.length) return
  const canvas = canvasRef.value
  const ctx = getCanvasCtx()
  if (!canvas || !ctx) return
  const img = new Image()
  img.onload = () => {
    ctx.clearRect(0, 0, width, height)
    ctx.drawImage(img, 0, 0)
  }
  img.src = history.value[index]
  historyIndex.value = index
}

function undo() {
  if (historyIndex.value > 0) {
    restoreState(historyIndex.value - 1)
  } else if (historyIndex.value === 0) {
    const ctx = getCanvasCtx()
    if (ctx) ctx.clearRect(0, 0, width, height)
    historyIndex.value = -1
    hasDrawn.value = false
  }
}

function redo() {
  if (historyIndex.value < history.value.length - 1) {
    restoreState(historyIndex.value + 1)
  }
}

function onMouseDown(e: MouseEvent) {
  isDrawing.value = true
  startPoint.value = { x: e.offsetX, y: e.offsetY }
  lastPoint.value = { x: e.offsetX, y: e.offsetY }

  if (currentTool.value === 'pen' || currentTool.value === 'eraser') {
    const ctx = getCanvasCtx()
    if (!ctx) return
    ctx.beginPath()
    ctx.moveTo(e.offsetX, e.offsetY)
  } else if (currentTool.value === 'text') {
    const text = prompt('Enter text:')
    if (text) {
      const ctx = getCanvasCtx()
      if (!ctx) return
      ctx.font = `${lineWidth.value * 8}px sans-serif`
      ctx.fillStyle = currentColor.value
      ctx.fillText(text, e.offsetX, e.offsetY)
      saveState()
    }
    isDrawing.value = false
  }
}

function onMouseMove(e: MouseEvent) {
  if (!isDrawing.value || !startPoint.value) return
  const ctx = getCanvasCtx()
  if (!ctx) return

  if (currentTool.value === 'pen') {
    ctx.strokeStyle = currentColor.value
    ctx.lineWidth = lineWidth.value
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    ctx.lineTo(e.offsetX, e.offsetY)
    ctx.stroke()
  } else if (currentTool.value === 'eraser') {
    ctx.globalCompositeOperation = 'destination-out'
    ctx.lineWidth = lineWidth.value * 4
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    ctx.lineTo(e.offsetX, e.offsetY)
    ctx.stroke()
  } else if (
    currentTool.value === 'rectangle' ||
    currentTool.value === 'circle' ||
    currentTool.value === 'line'
  ) {
    // Preview shape (redraw from saved state)
    if (historyIndex.value >= 0) {
      const img = new Image()
      img.src = history.value[historyIndex.value]
      ctx.clearRect(0, 0, width, height)
      ctx.drawImage(img, 0, 0)
    } else {
      ctx.clearRect(0, 0, width, height)
    }
    drawShape(ctx, startPoint.value, { x: e.offsetX, y: e.offsetY })
  }
}

function onMouseUp(e: MouseEvent) {
  if (!isDrawing.value) return
  isDrawing.value = false

  const ctx = getCanvasCtx()
  if (!ctx || !startPoint.value) return

  // Reset composite operation for eraser
  ctx.globalCompositeOperation = 'source-over'

  if (
    currentTool.value === 'rectangle' ||
    currentTool.value === 'circle' ||
    currentTool.value === 'line'
  ) {
    drawShape(ctx, startPoint.value, { x: e.offsetX, y: e.offsetY })
  }

  if (currentTool.value !== 'text') {
    saveState()
  }

  startPoint.value = null
  lastPoint.value = null
}

function drawShape(
  ctx: CanvasRenderingContext2D,
  start: { x: number; y: number },
  end: { x: number; y: number },
) {
  ctx.strokeStyle = currentColor.value
  ctx.lineWidth = lineWidth.value
  ctx.lineCap = 'round'

  if (currentTool.value === 'rectangle') {
    const w = end.x - start.x
    const h = end.y - start.y
    ctx.strokeRect(start.x, start.y, w, h)
  } else if (currentTool.value === 'circle') {
    const radius = Math.sqrt(Math.pow(end.x - start.x, 2) + Math.pow(end.y - start.y, 2))
    ctx.beginPath()
    ctx.arc(start.x, start.y, radius, 0, 2 * Math.PI)
    ctx.stroke()
  } else if (currentTool.value === 'line') {
    ctx.beginPath()
    ctx.moveTo(start.x, start.y)
    ctx.lineTo(end.x, end.y)
    ctx.stroke()
  }
}

function clearCanvas() {
  const ctx = getCanvasCtx()
  if (ctx) {
    ctx.clearRect(0, 0, width, height)
    saveState()
  }
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function onFileChange(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files || !files[0]) return
  const reader = new FileReader()
  reader.onload = function (evt) {
    const img = new window.Image()
    img.onload = function () {
      const ctx = getCanvasCtx()
      if (ctx) {
        ctx.clearRect(0, 0, width, height)
        ctx.drawImage(img, 0, 0, width, height)
        saveState()
      }
    }
    if (evt.target?.result) img.src = evt.target.result as string
  }
  reader.readAsDataURL(files[0])
}

async function submitCanvas() {
  error.value = null
  isUploading.value = true
  try {
    const canvas = canvasRef.value
    if (!canvas) throw new Error('Canvas not found')
    const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/png'))
    if (!blob) throw new Error('Failed to export canvas')
    const formData = new FormData()
    formData.append('image', blob, 'sketch.png')

    const res = await fetch('/api/ai/generate-code', {
      method: 'POST',
      body: formData,
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: 'Upload failed' }))
      throw new Error(errData.detail || 'Upload failed')
    }

    const data = await res.json()
    console.log('Generated code:', data)

    // Emit the generated code to parent
    emit('code-generated', data)
  } catch (e: any) {
    error.value = e.message || 'Unknown error'
  } finally {
    isUploading.value = false
  }
}

onMounted(() => {
  // Initialize with blank canvas state
  saveState()
})
</script>

<style scoped>
.floating-toolbar {
  position: absolute;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  border: 1px solid #e2e8f0;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.toolbar-divider {
  width: 1px;
  height: 2rem;
  background-color: #e2e8f0;
  margin: 0 0.25rem;
}

.canvas-wrapper {
  position: relative;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}

.canvas-main {
  display: block;
  background: #ffffff;
}

.grid-bg {
  background-image: 
    linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
  background-size: 20px 20px;
  background-color: #fafafa;
}

.canvas-help-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.tool-btn-modern {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background-color: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
  color: #475569;
}

.tool-btn-modern:hover:not(:disabled) {
  background-color: #f1f5f9;
}

.tool-btn-active {
  background-color: #dbeafe;
  color: #2563eb;
}

.tool-btn-modern:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.color-picker-panel {
  position: absolute;
  top: 3rem;
  left: 0;
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  border: 1px solid #e2e8f0;
  padding: 0.75rem;
  z-index: 20;
}

.stroke-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  background-color: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
}

.stroke-btn:hover {
  background-color: #f1f5f9;
}

.stroke-btn-active {
  background-color: #dbeafe;
}

.stroke-preview {
  width: 1.25rem;
  background-color: #1e293b;
  border-radius: 999px;
}

.btn-primary-modern {
  padding: 0.625rem 1.5rem;
  border-radius: 0.5rem;
  background-color: #2563eb;
  color: white;
  border: none;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}

.btn-primary-modern:hover:not(:disabled) {
  background-color: #1d4ed8;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  transform: translateY(-1px);
}

.btn-primary-modern:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.625rem 1.5rem;
  border-radius: 0.5rem;
  background-color: white;
  color: #475569;
  border: 1px solid #e2e8f0;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-secondary:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
}

.error-box {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  max-width: 42rem;
}

.status-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background-color: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  max-width: 42rem;
}

.spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid #2563eb;
  border-top-color: transparent;
  border-radius: 9999px;
  animation: spin 1s linear infinite;
}

.spinner-small {
  width: 1rem;
  height: 1rem;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 9999px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.cursor-crosshair {
  cursor: crosshair;
}

.cursor-text {
  cursor: text;
}
</style>
