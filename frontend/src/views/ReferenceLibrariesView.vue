<template>
  <div class="libraries-view">
    <!-- Header -->
    <div class="view-header glass-panel">
      <div class="header-left">
        <h2>📚 PDS Reference Libraries</h2>
        <p class="subtitle">Standard dropdown sources for CS Form 212 (Revised 2026) — CES / DepEd</p>
      </div>
      <div class="header-right">
        <button @click="openAddModal" class="btn-primary">
          <span class="btn-icon">➕</span> Add New {{ activeTabLabel }}
        </button>
      </div>
    </div>

    <!-- Tab navigation -->
    <div class="tabs-container glass-panel">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span>{{ tab.label }}</span>
        <span class="tab-badge">{{ getTabCount(tab.id) }}</span>
      </button>
    </div>

    <!-- Search & Filters -->
    <div class="filter-bar glass-panel">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="`Search ${activeTabLabel.toLowerCase()}s...`"
          class="search-input"
        />
      </div>
      <div class="filter-info">
        Showing {{ filteredItems.length }} of {{ getTabCount(activeTab) }} items
      </div>
    </div>

    <!-- Content Table -->
    <div class="content-table-wrapper glass-panel">
      <!-- 1. ELIGIBILITIES TAB -->
      <table v-if="activeTab === 'eligibility'" class="data-table">
        <thead>
          <tr>
            <th>Eligibility / Board Title</th>
            <th>Default Examination Place Hint</th>
            <th>Status</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.id">
            <td><strong>{{ item.eligibility_type }}</strong></td>
            <td>{{ item.exam_place_hint || '—' }}</td>
            <td><span class="badge active-badge">Active</span></td>
            <td class="text-right actions-cell">
              <button @click="openEditModal(item)" class="btn-action edit" title="Edit">✏️</button>
              <button @click="confirmDelete(item)" class="btn-action delete" title="Delete">🗑️</button>
            </td>
          </tr>
          <tr v-if="!filteredItems.length">
            <td colspan="4" class="no-records">No eligibility library items found.</td>
          </tr>
        </tbody>
      </table>

      <!-- 2. WORK EXPERIENCE / POSITIONS TAB -->
      <table v-else-if="activeTab === 'work'" class="data-table">
        <thead>
          <tr>
            <th>Position Title</th>
            <th>Department / Agency / Office</th>
            <th>Salary Grade</th>
            <th>Default Status</th>
            <th>Gov Service</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.id">
            <td><strong>{{ item.position_title }}</strong></td>
            <td>{{ item.department_agency_company }}</td>
            <td><span class="badge-sg">SG {{ item.salary_grade || '—' }}</span></td>
            <td>{{ item.appointment_status || 'Permanent' }}</td>
            <td>{{ item.is_government_service ? 'Yes' : 'No' }}</td>
            <td class="text-right actions-cell">
              <button @click="openEditModal(item)" class="btn-action edit" title="Edit">✏️</button>
              <button @click="confirmDelete(item)" class="btn-action delete" title="Delete">🗑️</button>
            </td>
          </tr>
          <tr v-if="!filteredItems.length">
            <td colspan="6" class="no-records">No work experience library items found.</td>
          </tr>
        </tbody>
      </table>

      <!-- 3. TRAININGS / L&D TAB -->
      <table v-else-if="activeTab === 'training'" class="data-table">
        <thead>
          <tr>
            <th>Training Program / Seminar Title</th>
            <th>Type</th>
            <th>Hours</th>
            <th>Conducted / Sponsored By</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.id">
            <td><strong>{{ item.training_title }}</strong></td>
            <td><span class="badge-type">{{ item.ld_type || 'Technical' }}</span></td>
            <td>{{ item.default_hours }} hrs</td>
            <td>{{ item.conducted_sponsored_by || '—' }}</td>
            <td class="text-right actions-cell">
              <button @click="openEditModal(item)" class="btn-action edit" title="Edit">✏️</button>
              <button @click="confirmDelete(item)" class="btn-action delete" title="Delete">🗑️</button>
            </td>
          </tr>
          <tr v-if="!filteredItems.length">
            <td colspan="5" class="no-records">No training library items found.</td>
          </tr>
        </tbody>
      </table>

      <!-- 4. VOLUNTARY WORKS TAB -->
      <table v-else-if="activeTab === 'voluntary'" class="data-table">
        <thead>
          <tr>
            <th>Organization Name &amp; Address</th>
            <th>Position / Nature of Work</th>
            <th>Default Hours</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.id">
            <td><strong>{{ item.organization_name_address }}</strong></td>
            <td>{{ item.position_nature_of_work || '—' }}</td>
            <td>{{ item.default_hours }} hrs</td>
            <td class="text-right actions-cell">
              <button @click="openEditModal(item)" class="btn-action edit" title="Edit">✏️</button>
              <button @click="confirmDelete(item)" class="btn-action delete" title="Delete">🗑️</button>
            </td>
          </tr>
          <tr v-if="!filteredItems.length">
            <td colspan="4" class="no-records">No voluntary work library items found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- MODAL FOR ADD / EDIT -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-card glass-panel">
        <div class="modal-header">
          <h3>{{ editingId ? 'Edit' : 'Add' }} {{ activeTabLabel }}</h3>
          <button @click="showModal = false" class="btn-close">×</button>
        </div>

        <form @submit.prevent="saveItem" class="modal-form">
          <!-- 1. Eligibility Fields -->
          <template v-if="activeTab === 'eligibility'">
            <div class="form-group">
              <label>Eligibility / Examination Title *</label>
              <input v-model="formData.eligibility_type" required placeholder="e.g. RA 1080 (Teacher's Board), Career Service Professional" />
            </div>
            <div class="form-group">
              <label>Default Examination Place Hint</label>
              <input v-model="formData.exam_place_hint" placeholder="e.g. PRC Regional Office II - Tuguegarao City" />
            </div>
          </template>

          <!-- 2. Work Experience Fields -->
          <template v-else-if="activeTab === 'work'">
            <div class="form-group">
              <label>Position Title *</label>
              <input v-model="formData.position_title" required placeholder="e.g. Master Teacher II, Secondary School Teacher I" />
            </div>
            <div class="form-group">
              <label>Department / Agency / Office *</label>
              <input v-model="formData.department_agency_company" required placeholder="e.g. Cagayan National High School - DepEd" />
            </div>
            <div class="form-row-2">
              <div class="form-group">
                <label>Salary Grade (format: 00-0)</label>
                <input v-model="formData.salary_grade" placeholder="e.g. 18-1" />
              </div>
              <div class="form-group">
                <label>Appointment Status</label>
                <select v-model="formData.appointment_status">
                  <option value="Permanent">Permanent</option>
                  <option value="Temporary">Temporary</option>
                  <option value="Casual">Casual</option>
                  <option value="Contractual">Contractual</option>
                  <option value="Coterminous">Coterminous</option>
                  <option value="Job Order">Job Order</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="cb-label">
                <input type="checkbox" v-model="formData.is_government_service" />
                <span>Government Service (Yes / No)</span>
              </label>
            </div>
          </template>

          <!-- 3. Training Fields -->
          <template v-else-if="activeTab === 'training'">
            <div class="form-group">
              <label>Training / Seminar Program Title *</label>
              <input v-model="formData.training_title" required placeholder="e.g. Regional Training on the MATATAG Curriculum for Teachers" />
            </div>
            <div class="form-row-2">
              <div class="form-group">
                <label>L&amp;D Type</label>
                <select v-model="formData.ld_type">
                  <option value="Technical">Technical</option>
                  <option value="Managerial">Managerial</option>
                  <option value="Supervisory">Supervisory</option>
                  <option value="Foundational">Foundational</option>
                  <option value="Cross-Cutting">Cross-Cutting</option>
                </select>
              </div>
              <div class="form-group">
                <label>Default Number of Hours</label>
                <input type="number" v-model.number="formData.default_hours" min="1" placeholder="e.g. 40" />
              </div>
            </div>
            <div class="form-group">
              <label>Conducted / Sponsored By</label>
              <input v-model="formData.conducted_sponsored_by" placeholder="e.g. Department of Education - Regional Office II" />
            </div>
          </template>

          <!-- 4. Voluntary Work Fields -->
          <template v-else-if="activeTab === 'voluntary'">
            <div class="form-group">
              <label>Name &amp; Address of Organization *</label>
              <input v-model="formData.organization_name_address" required placeholder="e.g. Philippine Red Cross - Cagayan Chapter, Tuguegarao City" />
            </div>
            <div class="form-group">
              <label>Position / Nature of Work</label>
              <input v-model="formData.position_nature_of_work" placeholder="e.g. Volunteer First Aider / Youth Adviser" />
            </div>
            <div class="form-group">
              <label>Default Number of Hours</label>
              <input type="number" v-model.number="formData.default_hours" min="1" placeholder="e.g. 40" />
            </div>
          </template>

          <div class="modal-actions">
            <button type="button" @click="showModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit" :disabled="saving">
              {{ saving ? 'Saving...' : (editingId ? 'Update Record' : 'Add Record') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useLibrariesStore } from '@/stores/libraries'
import notify from '@/utils/notify'

const librariesStore = useLibrariesStore()

const tabs = [
  { id: 'eligibility', label: 'Eligibilities', icon: '🎖️' },
  { id: 'work', label: 'Work Experience / Positions', icon: '💼' },
  { id: 'training', label: 'L&D / Trainings', icon: '📖' },
  { id: 'voluntary', label: 'Voluntary Works', icon: '🤝' },
]

const activeTab = ref('eligibility')
const searchQuery = ref('')
const showModal = ref(false)
const editingId = ref(null)
const saving = ref(false)

const formData = reactive({})

const activeTabLabel = computed(() => {
  const t = tabs.find(x => x.id === activeTab.value)
  return t ? t.label : ''
})

const getTabCount = (tabId) => {
  switch (tabId) {
    case 'eligibility': return librariesStore.eligibilities.length
    case 'work': return librariesStore.workExperiences.length
    case 'training': return librariesStore.trainings.length
    case 'voluntary': return librariesStore.voluntaryWorks.length
    default: return 0
  }
}

const filteredItems = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  let list = []
  if (activeTab.value === 'eligibility') {
    list = librariesStore.eligibilities
    if (!q) return list
    return list.filter(item =>
      (item.eligibility_type || '').toLowerCase().includes(q) ||
      (item.exam_place_hint || '').toLowerCase().includes(q)
    )
  } else if (activeTab.value === 'work') {
    list = librariesStore.workExperiences
    if (!q) return list
    return list.filter(item =>
      (item.position_title || '').toLowerCase().includes(q) ||
      (item.department_agency_company || '').toLowerCase().includes(q)
    )
  } else if (activeTab.value === 'training') {
    list = librariesStore.trainings
    if (!q) return list
    return list.filter(item =>
      (item.training_title || '').toLowerCase().includes(q) ||
      (item.conducted_sponsored_by || '').toLowerCase().includes(q) ||
      (item.ld_type || '').toLowerCase().includes(q)
    )
  } else if (activeTab.value === 'voluntary') {
    list = librariesStore.voluntaryWorks
    if (!q) return list
    return list.filter(item =>
      (item.organization_name_address || '').toLowerCase().includes(q) ||
      (item.position_nature_of_work || '').toLowerCase().includes(q)
    )
  }
  return list
})

const openAddModal = () => {
  editingId.value = null
  Object.keys(formData).forEach(k => delete formData[k])

  if (activeTab.value === 'eligibility') {
    Object.assign(formData, { eligibility_type: '', exam_place_hint: '' })
  } else if (activeTab.value === 'work') {
    Object.assign(formData, {
      position_title: '',
      department_agency_company: 'Cagayan National High School - DepEd',
      salary_grade: '',
      appointment_status: 'Permanent',
      is_government_service: true,
    })
  } else if (activeTab.value === 'training') {
    Object.assign(formData, {
      training_title: '',
      ld_type: 'Technical',
      default_hours: 40,
      conducted_sponsored_by: '',
    })
  } else if (activeTab.value === 'voluntary') {
    Object.assign(formData, {
      organization_name_address: '',
      position_nature_of_work: '',
      default_hours: 40,
    })
  }
  showModal.value = true
}

const openEditModal = (item) => {
  editingId.value = item.id
  Object.keys(formData).forEach(k => delete formData[k])
  Object.assign(formData, item)
  showModal.value = true
}

const saveItem = async () => {
  saving.value = true
  try {
    if (activeTab.value === 'eligibility') {
      if (editingId.value) {
        await librariesStore.updateEligibility(editingId.value, formData)
        notify.success('Eligibility updated successfully!')
      } else {
        await librariesStore.addEligibility(formData)
        notify.success('New Eligibility added to library!')
      }
    } else if (activeTab.value === 'work') {
      if (editingId.value) {
        await librariesStore.updateWorkExperience(editingId.value, formData)
        notify.success('Work Experience position updated successfully!')
      } else {
        await librariesStore.addWorkExperience(formData)
        notify.success('New Position added to library!')
      }
    } else if (activeTab.value === 'training') {
      if (editingId.value) {
        await librariesStore.updateTraining(editingId.value, formData)
        notify.success('Training updated successfully!')
      } else {
        await librariesStore.addTraining(formData)
        notify.success('New Training added to library!')
      }
    } else if (activeTab.value === 'voluntary') {
      if (editingId.value) {
        await librariesStore.updateVoluntary(editingId.value, formData)
        notify.success('Voluntary Work updated successfully!')
      } else {
        await librariesStore.addVoluntary(formData)
        notify.success('New Voluntary Work added to library!')
      }
    }
    showModal.value = false
  } catch (err) {
    console.error(err)
    notify.error('Failed to save library record.')
  } finally {
    saving.value = false
  }
}

const confirmDelete = async (item) => {
  if (!confirm(`Are you sure you want to delete this library item?`)) return
  try {
    if (activeTab.value === 'eligibility') {
      await librariesStore.deleteEligibility(item.id)
    } else if (activeTab.value === 'work') {
      await librariesStore.deleteWorkExperience(item.id)
    } else if (activeTab.value === 'training') {
      await librariesStore.deleteTraining(item.id)
    } else if (activeTab.value === 'voluntary') {
      await librariesStore.deleteVoluntary(item.id)
    }
    notify.success('Library item removed.')
  } catch (err) {
    console.error(err)
    notify.error('Failed to delete library record.')
  }
}

onMounted(() => {
  librariesStore.fetchAllLibraries()
})
</script>

<style scoped>
.libraries-view {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
}

.header-left h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f8fafc;
  margin-bottom: 0.25rem;
}

.subtitle {
  color: #94a3b8;
  font-size: 0.88rem;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-space, linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: #ffffff;
  border: none;
  padding: 0.65rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
}

/* Tabs */
.tabs-container {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  overflow-x: auto;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.2rem;
  border: none;
  background: transparent;
  color: #475569;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.tab-btn.active {
  color: #2563eb;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
}

.tab-badge {
  background: #e2e8f0;
  color: #334155;
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-weight: 700;
}

.tab-btn.active .tab-badge {
  background: #2563eb;
  color: #ffffff;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 1.25rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  max-width: 400px;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  padding: 0.45rem 0.85rem;
  border-radius: 6px;
}

.search-input {
  width: 100%;
  background: transparent;
  border: none;
  color: #0f172a;
  font-size: 0.88rem;
  outline: none;
}

.filter-info {
  font-size: 0.82rem;
  color: #64748b;
  font-weight: 500;
}

/* Table */
.content-table-wrapper {
  border-radius: 12px;
  overflow: hidden;
  padding: 0.5rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.85rem 1rem;
  text-align: left;
}

.data-table th {
  background: #f8fafc;
  color: #475569;
  font-size: 0.76rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #e2e8f0;
}

.data-table td {
  color: #0f172a;
  font-size: 0.88rem;
  border-bottom: 1px solid #f1f5f9;
}

.data-table tbody tr:hover {
  background: #f8fafc;
}

.text-right {
  text-align: right;
}

.badge-sg {
  background: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
}

.badge-type {
  background: #faf5ff;
  color: #7e22ce;
  border: 1px solid #e9d5ff;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
}

.active-badge {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
}

.actions-cell {
  display: flex;
  justify-content: flex-end;
  gap: 0.4rem;
}

.btn-action {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  color: #334155;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
}

.btn-action:hover {
  background: #eff6ff;
  color: #2563eb;
  border-color: #bfdbfe;
}

.no-records {
  text-align: center;
  padding: 3rem 1rem !important;
  color: #64748b;
  font-style: italic;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  width: 100%;
  max-width: 580px;
  border-radius: 12px;
  padding: 1.5rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  font-size: 1.2rem;
  color: #0f172a;
  font-weight: 700;
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #64748b;
  cursor: pointer;
}

.btn-close:hover {
  color: #0f172a;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 0.35rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.55rem 0.75rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  color: #0f172a;
  font-size: 0.88rem;
  outline: none;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.form-group input:focus,
.form-group select:focus {
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.cb-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: #e2e8f0;
  font-size: 0.85rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-cancel {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #e2e8f0;
  padding: 0.55rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-submit {
  background: #0ea5e9;
  border: none;
  color: #ffffff;
  padding: 0.55rem 1.25rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-submit:hover {
  background: #0284c7;
}
</style>
