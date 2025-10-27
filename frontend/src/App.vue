<template>
  <div class="h-screen w-screen bg-gray-50 overflow-hidden flex">
    <!-- Main Canvas Area -->
    <main class="flex-1 flex flex-col">
      <!-- Top Bar -->
      <header class="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <svg class="w-6 h-6 text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
            </svg>
            <h1 class="text-lg font-semibold text-gray-900">Canvas Smith</h1>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button
            @click="clearCanvas"
            class="px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition"
          >
            Clear Canvas
          </button>
          <button
            @click="exportCanvas"
            class="px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition flex items-center gap-2"
          >
            <component :is="DownloadIcon" />
            Export
          </button>
        </div>
      </header>

      <!-- Canvas with Rulers -->
      <div class="flex-1 flex overflow-hidden relative">
        <!-- Vertical Ruler -->
        <div class="w-8 bg-gray-50 border-r border-gray-200 relative">
          <canvas ref="verticalRuler" class="absolute inset-0" width="32" :height="rulerHeight"></canvas>
        </div>

        <!-- Canvas Container -->
        <div class="flex-1 flex flex-col">
          <!-- Horizontal Ruler -->
          <div class="h-8 bg-gray-50 border-b border-gray-200 relative">
            <canvas ref="horizontalRuler" class="absolute inset-0" :width="rulerWidth" height="32"></canvas>
          </div>

          <!-- Main Canvas -->
          <div class="flex-1 relative bg-gray-100 overflow-hidden" ref="canvasContainer">
            <canvas
              ref="canvas"
              @mousedown="onMouseDown"
              @mousemove="onMouseMove"
              @mouseup="onMouseUp"
              @mouseleave="onMouseUp"
              class="cursor-crosshair"
            ></canvas>
          </div>
        </div>
      </div>
    </main>

    <!-- Right Toolbar -->
    <Transition name="slide-left">
      <aside v-if="showToolbar" class="w-20 bg-white border-l border-gray-200 flex flex-col items-center py-4 gap-2">
        <!-- Close Button -->
        <button
          @click="showToolbar = false"
          class="w-12 h-12 flex items-center justify-center rounded-lg text-gray-600 hover:bg-gray-100 transition-all mb-2"
          title="Hide toolbar"
        >
          <component :is="CloseIcon" />
        </button>

        <div class="w-10 h-px bg-gray-200 my-1"></div>

        <!-- Drawing Tools -->
        <button
          v-for="tool in drawingTools"
          :key="tool.name"
          @click="activeTool = tool.name"
          :class="[
            'w-12 h-12 flex items-center justify-center rounded-lg transition-all',
            activeTool === tool.name
              ? 'bg-gray-900 text-white'
              : 'text-gray-600 hover:bg-gray-100'
          ]"
          :title="tool.label"
        >
          <component :is="tool.icon" />
        </button>

        <div class="w-10 h-px bg-gray-200 my-2"></div>

        <!-- Color Picker Button -->
        <div class="relative">
          <button
            @click="showColorPicker = !showColorPicker"
            class="w-12 h-12 flex items-center justify-center rounded-lg border-2 transition-all shadow-sm"
            :style="{ borderColor: currentColor, backgroundColor: currentColor }"
            title="Color Picker"
          >
          </button>
          
          <!-- Enhanced Color Picker Popup -->
          <div
            v-if="showColorPicker"
            class="fixed right-24 bg-white rounded-xl shadow-2xl border border-gray-200 p-4 z-50"
            style="top: 50%; transform: translateY(-50%); width: 280px;"
          >
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-sm font-semibold text-gray-900">Color Picker</h3>
              <button
                @click="showColorPicker = false"
                class="text-gray-400 hover:text-gray-600"
              >
                <component :is="CloseIcon" />
              </button>
            </div>

            <!-- Hex Input -->
            <div class="mb-3">
              <label class="block text-xs text-gray-600 mb-1">Hex Color</label>
              <div class="flex gap-2">
                <input
                  type="text"
                  v-model="hexColor"
                  @input="updateColorFromHex"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-gray-900"
                  placeholder="#000000"
                />
                <input
                  type="color"
                  v-model="currentColor"
                  @input="updateHexFromColor"
                  class="w-12 h-10 rounded-lg cursor-pointer border border-gray-300"
                />
              </div>
            </div>

            <!-- Preset Colors -->
            <div>
              <label class="block text-xs text-gray-600 mb-2">Preset Colors</label>
              <div class="grid grid-cols-6 gap-2">
                <button
                  v-for="color in presetColors"
                  :key="color"
                  @click="selectColor(color)"
                  class="w-10 h-10 rounded-lg border-2 hover:scale-110 transition-transform"
                  :style="{ 
                    backgroundColor: color, 
                    borderColor: currentColor === color ? '#000' : '#e5e7eb' 
                  }"
                  :title="color"
                ></button>
              </div>
            </div>

            <!-- Recent Colors -->
            <div v-if="recentColors.length > 0" class="mt-3">
              <label class="block text-xs text-gray-600 mb-2">Recent</label>
              <div class="flex gap-2 flex-wrap">
                <button
                  v-for="(color, index) in recentColors"
                  :key="index"
                  @click="selectColor(color)"
                  class="w-8 h-8 rounded border-2 hover:scale-110 transition-transform"
                  :style="{ 
                    backgroundColor: color, 
                    borderColor: currentColor === color ? '#000' : '#e5e7eb' 
                  }"
                ></button>
              </div>
            </div>
          </div>
        </div>

        <!-- Stroke Width -->
        <div class="flex flex-col gap-2 items-center mt-2">
          <button
            v-for="width in strokeWidths"
            :key="width"
            @click="currentStrokeWidth = width"
            :class="[
              'rounded-full bg-gray-900 transition-all',
              currentStrokeWidth === width ? 'ring-2 ring-gray-400 ring-offset-2' : ''
            ]"
            :style="{ width: (width * 3 + 8) + 'px', height: (width * 3 + 8) + 'px' }"
            :title="`${width}px`"
          ></button>
        </div>
      </aside>
    </Transition>

    <!-- Toggle Toolbar Button -->
    <button
      v-if="!showToolbar"
      @click="showToolbar = true"
      class="fixed right-4 top-20 w-12 h-12 bg-gray-900 hover:bg-gray-800 text-white rounded-full shadow-xl flex items-center justify-center transition-all z-50"
      title="Show toolbar"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
    </button>

    <!-- Right Sidebar with Tabs -->
    <Transition name="slide-right">
      <aside v-if="showRightPanel" class="w-96 bg-white border-l border-gray-200 flex flex-col">
        <!-- Tabs -->
        <div class="flex border-b border-gray-200">
          <button
            @click="activeTab = 'code'"
            :class="[
              'flex-1 px-4 py-3 text-sm font-medium transition-all',
              activeTab === 'code'
                ? 'text-gray-900 border-b-2 border-gray-900'
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            <component :is="CodeIcon" class="inline mr-2" />
            Code
          </button>
          <button
            @click="activeTab = 'preview'"
            :class="[
              'flex-1 px-4 py-3 text-sm font-medium transition-all',
              activeTab === 'preview'
                ? 'text-gray-900 border-b-2 border-gray-900'
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            <component :is="PreviewIcon" class="inline mr-2" />
            Preview
          </button>
          <button
            @click="showRightPanel = false"
            class="px-4 py-3 text-gray-500 hover:text-gray-700 transition"
            title="Close panel"
          >
            <component :is="CloseIcon" />
          </button>
        </div>

        <!-- Tab Content -->
        <div class="flex-1 overflow-auto p-4">
          <div v-if="activeTab === 'code'">
            <div v-if="generatedCode">
              <CodeViewer :code="generatedCode.generated_code" :metadata="generatedCode" />
            </div>
            <div v-else class="text-center py-12 text-gray-500">
              <component :is="CodeIcon" class="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p class="text-sm">Draw something to generate code</p>
            </div>
          </div>

          <div v-if="activeTab === 'preview'">
            <div v-if="generatedCode" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <p class="text-sm text-gray-600">Live preview coming soon...</p>
            </div>
            <div v-else class="text-center py-12 text-gray-500">
              <component :is="PreviewIcon" class="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p class="text-sm">Preview will appear here</p>
            </div>
          </div>
        </div>

        <!-- Generate Button -->
        <div class="p-4 border-t border-gray-200">
          <button
            @click="generateCode"
            :disabled="isGenerating"
            class="w-full px-4 py-3 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-300 text-white rounded-lg font-medium transition-all flex items-center justify-center gap-2"
          >
            <component :is="SparklesIcon" />
            {{ isGenerating ? 'Generating...' : 'Generate Code' }}
          </button>
        </div>
      </aside>
    </Transition>

    <!-- Toggle Right Panel Button -->
    <button
      v-if="!showRightPanel"
      @click="showRightPanel = true"
      class="fixed right-4 bottom-4 w-12 h-12 bg-gray-900 hover:bg-gray-800 text-white rounded-full shadow-xl flex items-center justify-center transition-all z-50"
      title="Show code panel"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, h } from 'vue'
import CodeViewer from './components/CodeViewer.vue'

// Icon components
const createIcon = (path: string) => {
  return () => h('svg', {
    fill: 'none',
    stroke: 'currentColor',
    viewBox: '0 0 24 24',
    class: 'w-5 h-5'
  }, [
    h('path', {
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
      'stroke-width': '2',
      d: path
    })
  ])
}

const PenIcon = createIcon('M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z')
const RectangleIcon = createIcon('M4 5a1 1 0 011-1h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5z')
const CircleIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-5 h-5' }, [
  h('circle', { cx: '12', cy: '12', r: '9', 'stroke-width': '2' })
])
const LineIcon = createIcon('M5 19L19 5')
const TextIcon = createIcon('M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z')
const EraserIcon = createIcon('M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16')
const SelectIcon = createIcon('M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122')
const DownloadIcon = createIcon('M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4')
const CodeIcon = createIcon('M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4')
const PreviewIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24', class: 'w-4 h-4' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z' }),
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z' })
])
const SparklesIcon = createIcon('M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z')
const CloseIcon = createIcon('M6 18L18 6M6 6l12 12')

// State
const canvas = ref<HTMLCanvasElement | null>(null)
const canvasContainer = ref<HTMLDivElement | null>(null)
const horizontalRuler = ref<HTMLCanvasElement | null>(null)
const verticalRuler = ref<HTMLCanvasElement | null>(null)

const activeTool = ref('pen')
const activeTab = ref('code')
const showToolbar = ref(true)
const showRightPanel = ref(true)
const showColorPicker = ref(false)

const isDrawing = ref(false)
const isGenerating = ref(false)
const lastPos = ref({ x: 0, y: 0 })
const startPos = ref({ x: 0, y: 0 })
const currentPath = ref<{ x: number; y: number }[]>([])

const generatedCode = ref<any>(null)
const drawingHistory = ref<ImageData[]>([])
const historyIndex = ref(-1)

const rulerWidth = ref(1000)
const rulerHeight = ref(600)

const currentColor = ref('#000000')
const hexColor = ref('#000000')
const currentStrokeWidth = ref(2)
const recentColors = ref<string[]>([])

const presetColors = [
  '#000000', '#ffffff', '#ef4444', '#f59e0b',
  '#22c55e', '#3b82f6', '#a855f7', '#ec4899',
  '#64748b', '#f97316', '#14b8a6', '#8b5cf6'
]

const strokeWidths = [1, 2, 4, 8]

// Drawing tools configuration
const drawingTools = [
  { name: 'pen', label: 'Pen Tool (P)', icon: PenIcon },
  { name: 'rectangle', label: 'Rectangle (R)', icon: RectangleIcon },
  { name: 'circle', label: 'Circle (C)', icon: CircleIcon },
  { name: 'line', label: 'Line (L)', icon: LineIcon },
  { name: 'text', label: 'Text (T)', icon: TextIcon },
  { name: 'eraser', label: 'Eraser (E)', icon: EraserIcon },
  { name: 'select', label: 'Select/Pan (V)', icon: SelectIcon }
]

// Initialize canvas
onMounted(() => {
  if (!canvas.value || !canvasContainer.value) return

  const container = canvasContainer.value
  canvas.value.width = container.clientWidth
  canvas.value.height = container.clientHeight
  
  rulerWidth.value = container.clientWidth
  rulerHeight.value = container.clientHeight

  // Fill canvas with white background
  const ctx = getContext()
  if (ctx) {
    ensureQualitySettings(ctx)
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.value.width, canvas.value.height)
    saveState()
  }

  drawRulers()
  
  window.addEventListener('keydown', handleKeyboard)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboard)
  window.removeEventListener('resize', handleResize)
})

// Canvas drawing functions
function getContext() {
  return canvas.value?.getContext('2d')
}

function ensureQualitySettings(ctx: CanvasRenderingContext2D) {
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'
}

function saveState() {
  const ctx = getContext()
  if (!ctx || !canvas.value) return
  
  const imageData = ctx.getImageData(0, 0, canvas.value.width, canvas.value.height)
  historyIndex.value++
  drawingHistory.value = drawingHistory.value.slice(0, historyIndex.value)
  drawingHistory.value.push(imageData)
}

function restoreState(index: number) {
  const ctx = getContext()
  if (!ctx || !canvas.value || index < 0 || index >= drawingHistory.value.length) return
  
  ctx.putImageData(drawingHistory.value[index], 0, 0)
  historyIndex.value = index
}

function drawRulers() {
  // Horizontal ruler
  const hCtx = horizontalRuler.value?.getContext('2d')
  if (hCtx && horizontalRuler.value) {
    hCtx.clearRect(0, 0, horizontalRuler.value.width, horizontalRuler.value.height)
    hCtx.fillStyle = '#f9fafb'
    hCtx.fillRect(0, 0, horizontalRuler.value.width, horizontalRuler.value.height)
    
    hCtx.strokeStyle = '#d1d5db'
    hCtx.fillStyle = '#6b7280'
    hCtx.font = '10px sans-serif'
    
    const step = 50
    for (let i = 0; i < horizontalRuler.value.width; i += step) {
      hCtx.beginPath()
      hCtx.moveTo(i, 24)
      hCtx.lineTo(i, 32)
      hCtx.stroke()
      if (i % 100 === 0) {
        hCtx.fillText(i.toString(), i + 2, 20)
      }
    }
  }

  // Vertical ruler
  const vCtx = verticalRuler.value?.getContext('2d')
  if (vCtx && verticalRuler.value) {
    vCtx.clearRect(0, 0, verticalRuler.value.width, verticalRuler.value.height)
    vCtx.fillStyle = '#f9fafb'
    vCtx.fillRect(0, 0, verticalRuler.value.width, verticalRuler.value.height)
    
    vCtx.strokeStyle = '#d1d5db'
    vCtx.fillStyle = '#6b7280'
    vCtx.font = '10px sans-serif'
    
    const step = 50
    for (let i = 0; i < verticalRuler.value.height; i += step) {
      vCtx.beginPath()
      vCtx.moveTo(24, i)
      vCtx.lineTo(32, i)
      vCtx.stroke()
      if (i % 100 === 0) {
        vCtx.save()
        vCtx.translate(10, i - 2)
        vCtx.rotate(-Math.PI / 2)
        vCtx.fillText(i.toString(), 0, 0)
        vCtx.restore()
      }
    }
  }
}

function redraw() {
  const ctx = getContext()
  if (!ctx || !canvas.value) return
  
  // Restore the current drawing state without transformations
  if (historyIndex.value >= 0) {
    ctx.putImageData(drawingHistory.value[historyIndex.value], 0, 0)
  } else {
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.value.width, canvas.value.height)
  }
  
  // Update rulers
  drawRulers()
}

// Convert screen coordinates to canvas coordinates (accounting for pan/zoom)
function screenToCanvas(screenX: number, screenY: number) {
  return {
    x: screenX,
    y: screenY
  }
}

// Mouse event handlers
function onMouseDown(e: MouseEvent) {
  const rect = canvas.value?.getBoundingClientRect()
  if (!rect) return
  
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  isDrawing.value = true
  startPos.value = { x, y }
  lastPos.value = { x, y }
  currentPath.value = [{ x, y }]
  
  // Start drawing for pen immediately with proper styles
  if (activeTool.value === 'pen') {
    const ctx = getContext()
    if (ctx) {
      ensureQualitySettings(ctx)
      ctx.strokeStyle = currentColor.value
      ctx.lineWidth = currentStrokeWidth.value
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      ctx.beginPath()
      ctx.moveTo(x, y)
    }
  }
  
  // For eraser, also set up the context
  if (activeTool.value === 'eraser') {
    const ctx = getContext()
    if (ctx) {
      ctx.save()
      ctx.globalCompositeOperation = 'destination-out'
      ctx.lineWidth = 20
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      ctx.beginPath()
      ctx.moveTo(x, y)
    }
  }
}

function onMouseMove(e: MouseEvent) {
  const rect = canvas.value?.getBoundingClientRect()
  if (!rect) return
  
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  if (isDrawing.value) {
    const ctx = getContext()
    if (!ctx) return

    if (activeTool.value === 'pen') {
      // Use quadratic curves for smoother lines
      if (currentPath.value.length > 0) {
        const lastPoint = currentPath.value[currentPath.value.length - 1]
        const midX = (lastPoint.x + x) / 2
        const midY = (lastPoint.y + y) / 2
        ctx.quadraticCurveTo(lastPoint.x, lastPoint.y, midX, midY)
        ctx.stroke()
      }
      currentPath.value.push({ x, y })
    } else if (activeTool.value === 'eraser') {
      // Use quadratic curves for smoother erasing
      if (currentPath.value.length > 0) {
        const lastPoint = currentPath.value[currentPath.value.length - 1]
        const midX = (lastPoint.x + x) / 2
        const midY = (lastPoint.y + y) / 2
        ctx.quadraticCurveTo(lastPoint.x, lastPoint.y, midX, midY)
        ctx.stroke()
      }
      currentPath.value.push({ x, y })
    } else if (activeTool.value === 'rectangle' || activeTool.value === 'circle' || activeTool.value === 'line') {
      // Clear and redraw from last saved state for preview
      if (historyIndex.value >= 0) {
        ctx.putImageData(drawingHistory.value[historyIndex.value], 0, 0)
      }
      
      ensureQualitySettings(ctx)
      ctx.strokeStyle = currentColor.value
      ctx.lineWidth = currentStrokeWidth.value
      
      if (activeTool.value === 'rectangle') {
        const width = x - startPos.value.x
        const height = y - startPos.value.y
        ctx.strokeRect(startPos.value.x, startPos.value.y, width, height)
      } else if (activeTool.value === 'circle') {
        const radius = Math.sqrt(
          Math.pow(x - startPos.value.x, 2) + Math.pow(y - startPos.value.y, 2)
        )
        ctx.beginPath()
        ctx.arc(startPos.value.x, startPos.value.y, radius, 0, 2 * Math.PI)
        ctx.stroke()
      } else if (activeTool.value === 'line') {
        ctx.beginPath()
        ctx.moveTo(startPos.value.x, startPos.value.y)
        ctx.lineTo(x, y)
        ctx.stroke()
      }
    }

    lastPos.value = { x, y }
  }
}

function onMouseUp(e: MouseEvent) {
  if (isDrawing.value) {
    const rect = canvas.value?.getBoundingClientRect()
    if (!rect) return
    
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const ctx = getContext()
    if (!ctx) return

    ensureQualitySettings(ctx)
    ctx.strokeStyle = currentColor.value
    ctx.fillStyle = currentColor.value
    ctx.lineWidth = currentStrokeWidth.value
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'

    // Finalize shape drawings
    if (activeTool.value === 'rectangle') {
      const width = x - startPos.value.x
      const height = y - startPos.value.y
      ctx.strokeRect(startPos.value.x, startPos.value.y, width, height)
    } else if (activeTool.value === 'circle') {
      const radius = Math.sqrt(
        Math.pow(x - startPos.value.x, 2) + Math.pow(y - startPos.value.y, 2)
      )
      ctx.beginPath()
      ctx.arc(startPos.value.x, startPos.value.y, radius, 0, 2 * Math.PI)
      ctx.stroke()
    } else if (activeTool.value === 'line') {
      ctx.beginPath()
      ctx.moveTo(startPos.value.x, startPos.value.y)
      ctx.lineTo(x, y)
      ctx.stroke()
    } else if (activeTool.value === 'text') {
      const text = prompt('Enter text:')
      if (text) {
        ctx.font = `${currentStrokeWidth.value * 8}px sans-serif`
        ctx.fillStyle = currentColor.value
        ctx.fillText(text, x, y)
      }
    } else if (activeTool.value === 'eraser') {
      // Restore context after eraser
      ctx.restore()
    }

    saveState()
  }

  isDrawing.value = false
  currentPath.value = []
}

// Color picker functions
function selectColor(color: string) {
  currentColor.value = color
  hexColor.value = color
  showColorPicker.value = false
  
  // Add to recent colors if not already there
  if (!recentColors.value.includes(color)) {
    recentColors.value.unshift(color)
    if (recentColors.value.length > 8) {
      recentColors.value = recentColors.value.slice(0, 8)
    }
  }
}

function updateColorFromHex() {
  // Validate and update color from hex input
  const hex = hexColor.value.trim()
  if (/^#[0-9A-Fa-f]{6}$/.test(hex)) {
    currentColor.value = hex
  }
}

function updateHexFromColor() {
  hexColor.value = currentColor.value
}

function clearCanvas() {
  const ctx = getContext()
  if (!ctx || !canvas.value) return
  
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvas.value.width, canvas.value.height)
  
  saveState()
}

function exportCanvas() {
  if (canvas.value) {
    const link = document.createElement('a')
    link.download = 'canvas-sketch.png'
    link.href = canvas.value.toDataURL()
    link.click()
  }
}

async function generateCode() {
  if (!canvas.value) return
  
  isGenerating.value = true
  activeTab.value = 'code'
  
  try {
    canvas.value.toBlob(async (blob) => {
      if (!blob) return
      
      const formData = new FormData()
      formData.append('image', blob, 'sketch.png')
      
      const response = await fetch('http://localhost:8000/api/ai/generate-code', {
        method: 'POST',
        body: formData
      })
      
      const data = await response.json()
      generatedCode.value = data
      isGenerating.value = false
    })
  } catch (error) {
    console.error('Generation failed:', error)
    isGenerating.value = false
  }
}

function handleKeyboard(e: KeyboardEvent) {
  // Prevent default for tool shortcuts
  const keyMap: Record<string, string> = {
    'p': 'pen',
    'r': 'rectangle',
    'c': 'circle',
    'l': 'line',
    't': 'text',
    'e': 'eraser',
    'v': 'select'
  }
  
  const key = e.key.toLowerCase()
  
  if (keyMap[key]) {
    e.preventDefault()
    activeTool.value = keyMap[key]
    console.log('Tool changed to:', activeTool.value)
  }
  
  if (key === ' ') {
    e.preventDefault()
    activeTool.value = 'select'
  }
}

function handleResize() {
  if (!canvas.value || !canvasContainer.value) return
  
  const oldWidth = canvas.value.width
  const oldHeight = canvas.value.height
  
  const newWidth = canvasContainer.value.clientWidth
  const newHeight = canvasContainer.value.clientHeight
  
  // Save current canvas content
  const tempCanvas = document.createElement('canvas')
  tempCanvas.width = oldWidth
  tempCanvas.height = oldHeight
  const tempCtx = tempCanvas.getContext('2d')
  if (tempCtx) {
    tempCtx.drawImage(canvas.value, 0, 0)
  }
  
  // Resize canvas
  canvas.value.width = newWidth
  canvas.value.height = newHeight
  rulerWidth.value = newWidth
  rulerHeight.value = newHeight
  
  // Restore content
  const ctx = getContext()
  if (ctx && tempCtx) {
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, newWidth, newHeight)
    ctx.drawImage(tempCanvas, 0, 0)
  }
  
  redraw()
}
</script>

<style scoped>
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-right-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-right-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-left-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>

