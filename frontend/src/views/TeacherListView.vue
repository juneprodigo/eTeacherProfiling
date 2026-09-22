<template>
  <div class="teachers-page">
    <div class="toolbar glass-panel">
      <div class="search-box">
        <span class="icon">🔍</span>
        <input
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          placeholder="Search by teacher name, employee ID, or department..."
        />
      </div>

      <div class="filter-box">
        <select v-model="filterStatus" @change="handleSearch">
          <option value="">All Statuses</option>
          <option value="true">PDS Complete</option>
          <option value="false">PDS Incomplete</option>
        </select>

        <button @click="showCreateModal = true" class="btn-create">
          + New Teacher Profile
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="table-card glass-panel">
      <div v-if="pdsStore.isLoading" class="loading-box">
        Loading directory...
      </div>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Faculty Member</th>
            <th>Employee ID</th>
            <th>Department</th>
            <th>Position</th>
            <th>Status</th>
            <th>PDS Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in pdsStore.teachers" :key="t.id">
            <td class="name-cell">
              <div class="avatar-sm">
                {{ t.full_name.charAt(0) }}
              </div>
              <div class="name-details">
                <strong>{{ t.full_name }}</strong>
                <small>{{ t.user.email }}</small>
              </div>
            </td>
            <td>{{ t.employee_id || '—' }}</td>
            <td>{{ t.department || '—' }}</td>
            <td>{{ t.position || '—' }}</td>
            <td>
              <span :class="['badge-status', t.pds_complete ? 'complete' : 'pending']">
                {{ t.pds_complete ? 'Complete' : 'Incomplete' }}
              </span>
            </td>
            <td class="action-buttons">
              <router-link :to="`/teachers/${t.id}`" class="btn-pds">
                Edit PDS
              </router-link>
              <button @click="exportPDF(t.id, t.full_name)" class="btn-pdf" title="Export CS Form 212">
                📄 PDF
              </button>
            </td>
          </tr>
          <tr v-if="!pdsStore.teachers.length">
            <td colspan="6" class="no-data">No teachers found matching criteria.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Simple Create Profile Modal -->
    <div v-if="showCreateModal" class="modal-backdrop">
      <div class="modal-card glass-panel">
        <h3>Create Teacher Profile</h3>
        <p class="modal-sub">Link a Teacher account to a profile record.</p>

        <form @submit.prevent="createProfile">
          <div class="modal-field">
            <label>Select User Account (Role: Teacher)</label>
            <select v-model="newProfile.user_id" required>
              <option value="" disabled>Choose account</option>
              <option v-for="u in availableUsers" :key="u.id" :value="u.id">
                {{ u.full_name || u.username }} ({{ u.email }})
              </option>
            </select>
          </div>

          <div class="modal-field">
            <label>Employee ID</label>
            <input v-model="newProfile.employee_id" type="text" placeholder="e.g. DEPED-2026-002" />
          </div>

          <div class="modal-field">
            <label>Department</label>
            <input v-model="newProfile.department" type="text" placeholder="e.g. Mathematics Department" />
          </div>

          <div class="modal-field">
            <label>Position</label>
            <input v-model="newProfile.position" type="text" placeholder="e.g. Teacher III" />
          </div>

          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit">Create Profile</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usePDSStore } from '@/stores/pds'
import api from '@/api'

const pdsStore = usePDSStore()
const searchQuery = ref('')
const filterStatus = ref('')
const showCreateModal = ref(false)
const availableUsers = ref([])

const newProfile = ref({
  user_id: '',
  employee_id: '',
  department: '',
  position: ''
})

const handleSearch = () => {
  pdsStore.fetchTeachers({
    search: searchQuery.value,
    pds_complete: filterStatus.value || undefined,
  })
}

const exportPDF = (id, name) => {
  pdsStore.exportPDF(id, name)
}

const loadAvailableUsers = async () => {
  try {
    const res = await api.get('/auth/users/?role=teacher')
    availableUsers.value = res.data.results || res.data
  } catch (err) {
    console.error('Failed to load user accounts', err)
  }
}

const createProfile = async () => {
  try {
    await api.post('/teachers/', newProfile.value)
    showCreateModal.value = false
    newProfile.value = { user_id: '', employee_id: '', department: '', position: '' }
    await pdsStore.fetchTeachers()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to create profile')
  }
}

onMounted(async () => {
  await pdsStore.fetchTeachers()
  await loadAvailableUsers()
})
</script>

<style scoped>
.teachers-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.toolbar {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(11, 19, 41, 0.6);
  border: 1px solid var(--border-color);
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
  flex: 1;
  max-width: 450px;
}

.search-box input {
  border: none;
  background: transparent;
  padding: 0.5rem 0;
}
.search-box input:focus {
  box-shadow: none;
}

.filter-box {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.filter-box select {
  width: auto;
}

.btn-create {
  background: var(--accent-gold);
  color: #0b1329;
  font-weight: 700;
  padding: 0.65rem 1rem;
  border-radius: var(--radius-sm);
}

.table-card {
  padding: 0.5rem;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  font-size: 0.8rem;
  color: var(--text-muted);
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  font-size: 0.875rem;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar-sm {
  width: 36px;
  height: 36px;
  background: var(--bg-surface-elevated);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--accent-gold);
  border: 1px solid var(--border-color);
}

.name-details small {
  display: block;
  color: var(--text-muted);
  font-size: 0.75rem;
}

.badge-status {
  display: inline-block;
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-weight: 600;
}

.badge-status.complete {
  background: rgba(16, 185, 129, 0.15);
  color: #6ee7b7;
}

.badge-status.pending {
  background: rgba(245, 158, 11, 0.15);
  color: #fcd34d;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-pds {
  background: var(--bg-surface-elevated);
  color: var(--text-primary);
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  border: 1px solid var(--border-color);
}

.btn-pds:hover {
  background: var(--accent-gold);
  color: #0b1329;
}

.btn-pdf {
  background: rgba(59, 130, 246, 0.15);
  color: #93c5fd;
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 0.35rem 0.65rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
}

.btn-pdf:hover {
  background: var(--accent-blue);
  color: white;
}

.no-data {
  text-align: center;
  padding: 2rem !important;
  color: var(--text-muted);
}

/* Modal */
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  width: 100%;
  max-width: 480px;
  padding: 2rem;
}

.modal-card h3 {
  margin-bottom: 0.25rem;
}

.modal-sub {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}

.modal-field {
  margin-bottom: 1rem;
}

.modal-field label {
  display: block;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 0.4rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-cancel {
  background: transparent;
  color: var(--text-secondary);
  padding: 0.5rem 1rem;
}

.btn-submit {
  background: var(--accent-gold);
  color: #0b1329;
  font-weight: 700;
  padding: 0.5rem 1.25rem;
  border-radius: var(--radius-sm);
}
</style>
