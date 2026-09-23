<template>
  <div v-if="show" class="pdf-modal-backdrop" @click.self="close">
    <div class="pdf-modal-container glass-card">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-info">
          <div class="header-badges">
            <span class="badge-form">CS Form No. 212</span>
            <span class="badge-year">Revised 2026</span>
          </div>
          <h3 class="modal-title">{{ teacherName ? `${teacherName} — PDS Document Preview` : 'Personal Data Sheet Preview' }}</h3>
        </div>

        <div class="modal-actions">
          <button v-if="pdfUrl" @click="printPdf" class="btn-action btn-print" title="Print Document">
            🖨️ Print
          </button>
          <button v-if="pdfUrl" @click="downloadPdf" class="btn-action btn-download" title="Download PDF">
            ⬇️ PDF
          </button>
          <button @click="downloadExcel" class="btn-action btn-excel-modal" title="Download Official CS Form 212 (.xlsx)">
            📊 Excel (.xlsx)
          </button>
          <button v-if="pdfUrl" @click="openExternal" class="btn-action btn-external" title="Open in New Tab">
            ↗️ New Tab
          </button>
          <button @click="close" class="btn-close" title="Close Preview">
            ✕
          </button>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <div v-if="loading" class="pdf-loading-state">
          <div class="spinner"></div>
          <h4>Generating CS Form 212 Document</h4>
          <p>Compiling all 8 sections, eligibility records, and work history...</p>
        </div>

        <div v-else-if="error" class="pdf-error-state">
          <div class="error-icon">⚠️</div>
          <h4>Unable to generate PDF preview</h4>
          <p class="error-msg">{{ error }}</p>
          <button @click="loadPdf" class="btn-retry">Try Again</button>
        </div>

        <div v-else-if="pdfUrl" class="pdf-viewer-wrapper">
          <iframe
            :src="pdfUrl"
            class="pdf-frame"
            title="CS Form 212 PDF Preview"
          ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'
import api from '@/api'
import { usePDSStore } from '@/stores/pds'

const pdsStore = usePDSStore()

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  teacherId: {
    type: [Number, String],
    default: null
  },
  teacherName: {
    type: String,
    default: 'Teacher'
  }
})

const emit = defineEmits(['close'])

const loading = ref(false)
const error = ref(null)
const pdfUrl = ref(null)

const cleanUpUrl = () => {
  if (pdfUrl.value) {
    window.URL.revokeObjectURL(pdfUrl.value)
    pdfUrl.value = null
  }
}

const loadPdf = async () => {
  if (!props.teacherId) return
  loading.value = true
  error.value = null
  cleanUpUrl()

  try {
    const response = await api.get(`/teachers/${props.teacherId}/export-pdf/`, {
      responseType: 'blob'
    })
    const blob = new Blob([response.data], { type: 'application/pdf' })
    pdfUrl.value = window.URL.createObjectURL(blob)
  } catch (err) {
    let msg = 'Failed to load PDF preview from server.'
    if (err.response?.data instanceof Blob) {
      try {
        const text = await err.response.data.text()
        const parsed = JSON.parse(text)
        if (parsed.error) msg = parsed.error
        else if (parsed.detail) msg = parsed.detail
      } catch (_) {}
    } else if (err.response?.data?.error) {
      msg = err.response.data.error
    }
    error.value = msg
    console.error('PDF preview loading failed:', err)
  } finally {
    loading.value = false
  }
}

watch(() => props.show, (newVal) => {
  if (newVal && props.teacherId) {
    loadPdf()
  } else {
    cleanUpUrl()
  }
})

watch(() => props.teacherId, (newId) => {
  if (props.show && newId) {
    loadPdf()
  }
})

const close = () => {
  cleanUpUrl()
  emit('close')
}

const downloadPdf = () => {
  if (!pdfUrl.value) return
  const link = document.createElement('a')
  link.href = pdfUrl.value
  const cleanName = (props.teacherName || 'Teacher').replace(/\s+/g, '_')
  link.setAttribute('download', `CS_Form_212_${cleanName}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
}

const downloadExcel = () => {
  if (props.teacherId) {
    pdsStore.exportExcel(props.teacherId, props.teacherName)
  }
}

const printPdf = () => {
  if (!pdfUrl.value) return
  const iframe = document.querySelector('.pdf-frame')
  if (iframe && iframe.contentWindow) {
    try {
      iframe.contentWindow.focus()
      iframe.contentWindow.print()
      return
    } catch (_) {}
  }
  // Fallback: open in new window and invoke print
  const w = window.open(pdfUrl.value, '_blank')
  if (w) {
    w.focus()
    setTimeout(() => { w.print() }, 1000)
  }
}

const openExternal = () => {
  if (pdfUrl.value) {
    window.open(pdfUrl.value, '_blank')
  }
}

onBeforeUnmount(() => {
  cleanUpUrl()
})
</script>

<style scoped>
.pdf-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(4, 9, 23, 0.85);
  backdrop-filter: blur(10px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  animation: fadeIn 0.2s ease-out;
}

.pdf-modal-container {
  width: 95vw;
  max-width: 1100px;
  height: 90vh;
  display: flex;
  flex-direction: column;
  background: #111a33;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-lg);
  box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.7);
  overflow: hidden;
}

.modal-header {
  padding: 1rem 1.5rem;
  background: rgba(19, 31, 61, 0.95);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.header-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.badge-form {
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.badge-year {
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.08);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.modal-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.modal-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-action {
  padding: 0.45rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--bg-surface-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-action:hover {
  background: var(--accent-gold-subtle);
  border-color: var(--accent-gold);
  color: var(--accent-gold);
}

.btn-download {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  border: 1px solid var(--accent-gold);
}

.btn-download:hover {
  background: var(--accent-gold-hover);
  color: var(--text-on-accent, #24120a);
}

.btn-excel-modal {
  background: rgba(16, 185, 129, 0.18);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.35);
}

.btn-excel-modal:hover {
  background: #10b981;
  color: #ffffff;
}

.btn-close {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  width: 34px;
  height: 34px;
  border-radius: 50%;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  background: rgba(244, 63, 94, 0.2);
  color: #fda4af;
  border-color: var(--accent-rose);
}

.modal-body {
  flex: 1;
  display: flex;
  position: relative;
  background: #0d1424;
  overflow: hidden;
}

.pdf-loading-state,
.pdf-error-state {
  margin: auto;
  text-align: center;
  padding: 2rem;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(245, 158, 11, 0.15);
  border-top-color: var(--accent-gold);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1.25rem;
}

.pdf-loading-state h4 {
  font-size: 1.15rem;
  margin-bottom: 0.5rem;
}

.pdf-loading-state p {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.pdf-error-state .error-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.pdf-error-state h4 {
  font-size: 1.15rem;
  color: #fda4af;
  margin-bottom: 0.5rem;
}

.error-msg {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-bottom: 1.25rem;
  max-width: 420px;
}

.btn-retry {
  padding: 0.55rem 1.25rem;
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  border-radius: var(--radius-sm);
}

.pdf-viewer-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
}

.pdf-frame {
  width: 100%;
  height: 100%;
  border: none;
  background: #ffffff;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
