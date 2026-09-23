<template>
  <div v-if="show" class="sig-modal-backdrop" @click.self="$emit('close')">
    <div class="sig-modal-card glass-panel">
      <div class="sig-modal-header">
        <div>
          <h3>✍️ Draw Electronic Signature</h3>
          <p class="sig-sub">Sign inside the canvas with your mouse, stylus, or touch. RA 8792 Compliant.</p>
        </div>
        <button @click="$emit('close')" class="btn-close-sig" title="Close">✕</button>
      </div>

      <!-- Canvas Area -->
      <div class="sig-canvas-container">
        <canvas
          ref="canvasRef"
          class="signature-canvas"
          @mousedown="startDrawing"
          @mousemove="draw"
          @mouseup="stopDrawing"
          @mouseleave="stopDrawing"
          @touchstart.prevent="startTouchDrawing"
          @touchmove.prevent="touchDraw"
          @touchend.prevent="stopDrawing"
        ></canvas>
        <div class="canvas-sign-line">
          <span>Sign above this line</span>
        </div>
      </div>

      <!-- Controls & Tools -->
      <div class="sig-toolbar">
        <div class="tool-group">
          <label>Ink Color:</label>
          <div class="color-options">
            <button
              v-for="c in inkColors"
              :key="c.value"
              :class="['color-btn', { active: selectedColor === c.value }]"
              :style="{ backgroundColor: c.value }"
              :title="c.label"
              @click="selectedColor = c.value"
            ></button>
          </div>
        </div>

        <div class="tool-group">
          <label>Thickness:</label>
          <div class="size-options">
            <button
              v-for="s in strokeSizes"
              :key="s.value"
              :class="['size-btn', { active: selectedSize === s.value }]"
              @click="selectedSize = s.value"
            >
              {{ s.label }}
            </button>
          </div>
        </div>

        <div class="tool-actions">
          <button type="button" @click="clearCanvas" class="btn-clear-sig">
            🗑️ Clear
          </button>
        </div>
      </div>

      <div class="sig-modal-footer">
        <button type="button" @click="$emit('close')" class="btn-cancel-sig">
          Cancel
        </button>
        <button type="button" @click="saveSignature" class="btn-attach-sig" :disabled="isSaving || !hasDrawn">
          {{ isSaving ? 'Saving E-Signature...' : '💾 Attach E-Signature to PDS' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps({
  show: Boolean,
  teacherId: [Number, String]
})

const emit = defineEmits(['close', 'saved'])

const canvasRef = ref(null)
const isDrawing = ref(false)
const hasDrawn = ref(false)
const isSaving = ref(false)

const inkColors = [
  { label: 'Deep Blue', value: '#0f3a8a' },
  { label: 'Black', value: '#111827' },
  { label: 'Dark Navy', value: '#1e293b' },
]
const selectedColor = ref('#0f3a8a')

const strokeSizes = [
  { label: 'Fine', value: 2 },
  { label: 'Medium', value: 3 },
  { label: 'Bold', value: 4.5 },
]
const selectedSize = ref(3)

let ctx = null

const initCanvas = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  ctx = canvas.getContext('2d')
  
  // Set real canvas pixel resolution
  const rect = canvas.getBoundingClientRect()
  const dpr = window.devicePixelRatio || 1
  canvas.width = (rect.width || 540) * dpr
  canvas.height = (rect.height || 200) * dpr
  ctx.scale(dpr, dpr)

  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  clearCanvas()
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    nextTick(() => {
      initCanvas()
      hasDrawn.value = false
    })
  }
})

const getCanvasPos = (e) => {
  const canvas = canvasRef.value
  const rect = canvas.getBoundingClientRect()
  return {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
}

const startDrawing = (e) => {
  isDrawing.value = true
  hasDrawn.value = true
  const pos = getCanvasPos(e)
  ctx.beginPath()
  ctx.strokeStyle = selectedColor.value
  ctx.lineWidth = selectedSize.value
  ctx.moveTo(pos.x, pos.y)
}

const draw = (e) => {
  if (!isDrawing.value) return
  const pos = getCanvasPos(e)
  ctx.lineTo(pos.x, pos.y)
  ctx.stroke()
}

const stopDrawing = () => {
  if (isDrawing.value) {
    ctx.closePath()
    isDrawing.value = false
  }
}

// Touch support for tablets/mobile devices
const getTouchPos = (e) => {
  const touch = e.touches[0]
  const canvas = canvasRef.value
  const rect = canvas.getBoundingClientRect()
  return {
    x: touch.clientX - rect.left,
    y: touch.clientY - rect.top
  }
}

const startTouchDrawing = (e) => {
  isDrawing.value = true
  hasDrawn.value = true
  const pos = getTouchPos(e)
  ctx.beginPath()
  ctx.strokeStyle = selectedColor.value
  ctx.lineWidth = selectedSize.value
  ctx.moveTo(pos.x, pos.y)
}

const touchDraw = (e) => {
  if (!isDrawing.value) return
  const pos = getTouchPos(e)
  ctx.lineTo(pos.x, pos.y)
  ctx.stroke()
}

const clearCanvas = () => {
  if (!ctx || !canvasRef.value) return
  const canvas = canvasRef.value
  const dpr = window.devicePixelRatio || 1
  ctx.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr)
  hasDrawn.value = false
}

const saveSignature = () => {
  if (!canvasRef.value || !hasDrawn.value) return
  isSaving.value = true
  
  canvasRef.value.toBlob((blob) => {
    isSaving.value = false
    if (blob) {
      emit('saved', blob)
      emit('close')
    }
  }, 'image/png')
}
</script>

<style scoped>
.sig-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(4, 9, 23, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
  padding: 1.5rem;
}

.sig-modal-card {
  width: 100%;
  max-width: 620px;
  background: #111a33;
  border: 1px solid rgba(245, 158, 11, 0.35);
  border-radius: var(--radius-md);
  padding: 1.75rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
}

.sig-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 0.75rem;
}

.sig-modal-header h3 {
  color: var(--accent-gold);
  font-size: 1.15rem;
  font-weight: 700;
}

.sig-sub {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 0.2rem;
}

.btn-close-sig {
  background: transparent;
  color: var(--text-muted);
  font-size: 1.2rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.btn-close-sig:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.sig-canvas-container {
  position: relative;
  width: 100%;
  height: 220px;
  background: #ffffff;
  border-radius: 8px;
  border: 2px dashed rgba(245, 158, 11, 0.5);
  overflow: hidden;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.1);
}

.signature-canvas {
  width: 100%;
  height: 100%;
  cursor: crosshair;
  touch-action: none;
}

.canvas-sign-line {
  position: absolute;
  bottom: 35px;
  left: 30px;
  right: 30px;
  border-bottom: 1px dashed #94a3b8;
  pointer-events: none;
  text-align: center;
}

.canvas-sign-line span {
  position: relative;
  top: 18px;
  font-size: 0.68rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sig-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 6px;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.tool-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  color: var(--text-secondary);
}

.color-options {
  display: flex;
  gap: 0.4rem;
}

.color-btn {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform 0.15s;
}

.color-btn.active {
  border-color: #f59e0b;
  transform: scale(1.15);
}

.size-options {
  display: flex;
  gap: 0.35rem;
}

.size-btn {
  font-size: 0.72rem;
  padding: 0.2rem 0.55rem;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-secondary);
  border-radius: 4px;
}

.size-btn.active {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
}

.btn-clear-sig {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 4px;
}

.btn-clear-sig:hover {
  background: rgba(239, 68, 68, 0.3);
}

.sig-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 1rem;
}

.btn-cancel-sig {
  background: var(--bg-surface-elevated);
  color: var(--text-secondary);
  padding: 0.6rem 1.25rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

.btn-attach-sig {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  padding: 0.6rem 1.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-attach-sig:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-attach-sig:not(:disabled):hover {
  background: var(--accent-gold-hover);
}
</style>
