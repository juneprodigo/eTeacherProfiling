<template>
  <div class="activities-view-container">
    <!-- Header Page Banner -->
    <div class="activities-header glass-panel">
      <div class="header-left">
        <div class="icon-badge">📅</div>
        <div>
          <h2>School Activities Monitoring &amp; Management</h2>
          <p class="sub-text">
            Track institutional seminars, faculty development, curriculum reviews, assemblies, and faculty attendance.
          </p>
        </div>
      </div>
      <div class="header-actions">
        <button @click="openCreateModal" class="btn-create-activity">
          + Schedule New Activity
        </button>
      </div>
    </div>

    <!-- Analytics KPI Overview Cards -->
    <div class="kpi-grid">
      <div class="kpi-card glass-panel">
        <div class="kpi-icon">📋</div>
        <div class="kpi-info">
          <span class="kpi-val">{{ stats?.total_activities || 0 }}</span>
          <span class="kpi-lbl">Total Activities</span>
        </div>
      </div>

      <div class="kpi-card glass-panel kpi-upcoming">
        <div class="kpi-icon">⏳</div>
        <div class="kpi-info">
          <span class="kpi-val">{{ stats?.upcoming || 0 }}</span>
          <span class="kpi-lbl">Upcoming Scheduled</span>
        </div>
      </div>

      <div class="kpi-card glass-panel kpi-progress">
        <div class="kpi-icon">⚡</div>
        <div class="kpi-info">
          <span class="kpi-val">{{ stats?.in_progress || 0 }}</span>
          <span class="kpi-lbl">In Progress Today</span>
        </div>
      </div>

      <div class="kpi-card glass-panel kpi-completed">
        <div class="kpi-icon">✅</div>
        <div class="kpi-info">
          <span class="kpi-val">{{ stats?.completed || 0 }}</span>
          <span class="kpi-lbl">Completed</span>
        </div>
      </div>

      <div class="kpi-card glass-panel kpi-attendance">
        <div class="kpi-icon">🎯</div>
        <div class="kpi-info">
          <span class="kpi-val">{{ stats?.attendance_rate || 0 }}%</span>
          <span class="kpi-lbl">Faculty Attendance Rate</span>
        </div>
      </div>
    </div>

    <!-- Filter & Search Toolbar -->
    <div class="filter-toolbar glass-panel">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          @input="debounceSearch"
          placeholder="Search activity title, venue, or funding source..."
        />
        <button v-if="searchQuery" @click="searchQuery = ''; applyFilters()" class="btn-clear-search">✕</button>
      </div>

      <div class="filter-group">
        <select v-model="filterType" @change="applyFilters" class="select-filter">
          <option value="">All Categories</option>
          <option v-for="t in activityTypes" :key="t" :value="t">{{ t }}</option>
        </select>

        <select v-model="filterModality" @change="applyFilters" class="select-filter">
          <option value="">All Modalities</option>
          <option value="In-Person">In-Person</option>
          <option value="Online / Virtual">Online / Virtual</option>
          <option value="Hybrid">Hybrid</option>
        </select>
      </div>

      <div class="status-pills">
        <button
          v-for="s in statusOptions"
          :key="s.value"
          :class="['status-pill', { active: filterStatus === s.value }]"
          @click="filterStatus = s.value; applyFilters()"
        >
          {{ s.label }}
        </button>
      </div>
    </div>

    <!-- Activities Cards Grid -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading school activities...</p>
    </div>

    <div v-else-if="activities.length === 0" class="empty-state glass-panel">
      <div class="empty-icon">📂</div>
      <h3>No Activities Found</h3>
      <p>There are no activities matching your current search or filter criteria.</p>
      <button @click="openCreateModal" class="btn-create-empty">+ Schedule First Activity</button>
    </div>

    <div v-else class="activities-grid">
      <div
        v-for="act in activities"
        :key="act.id"
        class="activity-card glass-panel"
      >
        <div class="card-top">
          <span :class="['badge-status', getStatusClass(act.status)]">
            {{ act.status }}
          </span>
          <span class="badge-modality">{{ act.modality }}</span>
        </div>

        <h3 class="activity-title">{{ act.title }}</h3>
        <span class="badge-category">{{ act.activity_type }}</span>

        <p v-if="act.description" class="activity-desc">
          {{ act.description }}
        </p>

        <div class="activity-meta-list">
          <div class="meta-item">
            <span class="meta-icon">📍</span>
            <span>{{ act.venue }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-icon">🗓️</span>
            <span>{{ formatDateTime(act.start_date) }} – {{ formatDateTime(act.end_date) }}</span>
          </div>
          <div class="meta-item" v-if="act.coordinator_name">
            <span class="meta-icon">👤</span>
            <span>Coordinator: <strong>{{ act.coordinator_name }}</strong></span>
          </div>
          <div class="meta-item" v-if="act.budget && act.budget > 0">
            <span class="meta-icon">💰</span>
            <span>Budget: ₱{{ Number(act.budget).toLocaleString() }} ({{ act.funding_source || 'MOOE' }})</span>
          </div>
        </div>

        <!-- Participants Counter -->
        <div class="attendance-summary-bar">
          <div class="summary-count">
            <span>👥 Faculty Participants:</span>
            <strong>{{ act.participant_count || 0 }} enrolled</strong>
          </div>
          <span v-if="act.status === 'Completed'" class="attended-count-pill">
            ✓ {{ act.attended_count || 0 }} Attended
          </span>
        </div>

        <!-- Card Actions -->
        <div class="card-actions">
          <button @click="openAttendanceModal(act)" class="btn-action-attendance">
            👥 Attendance &amp; Faculty
          </button>
          <div class="btn-group-right">
            <button @click="openEditModal(act)" class="btn-action-edit" title="Edit Activity">
              ✏️
            </button>
            <button @click="confirmDelete(act)" class="btn-action-del" title="Delete Activity">
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================================================================== -->
    <!-- CREATE / EDIT ACTIVITY MODAL -->
    <!-- ===================================================================== -->
    <div v-if="showActivityModal" class="modal-backdrop" @click.self="showActivityModal = false">
      <div class="modal-card glass-panel modal-lg">
        <div class="modal-header">
          <h3>{{ editingActivityId ? 'Edit School Activity' : 'Schedule New School Activity' }}</h3>
          <button @click="showActivityModal = false" class="btn-close-modal">✕</button>
        </div>

        <form @submit.prevent="submitActivity">
          <div class="field">
            <label>Activity Title *</label>
            <input v-model="activityForm.title" required placeholder="e.g. Division Training Workshop on Digital Learning" />
          </div>

          <div class="form-grid-2">
            <div class="field">
              <label>Activity Category / Type *</label>
              <select v-model="activityForm.activity_type" required>
                <option v-for="t in activityTypes" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
            <div class="field">
              <label>Modality *</label>
              <select v-model="activityForm.modality" required>
                <option value="In-Person">In-Person</option>
                <option value="Online / Virtual">Online / Virtual</option>
                <option value="Hybrid">Hybrid</option>
              </select>
            </div>
          </div>

          <div class="form-grid-2">
            <div class="field">
              <label>Venue / Location *</label>
              <input v-model="activityForm.venue" required placeholder="e.g. School Auditorium / Google Meet" />
            </div>
            <div class="field">
              <label>Activity Status *</label>
              <select v-model="activityForm.status" required>
                <option value="Upcoming">Upcoming</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Postponed">Postponed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>
          </div>

          <div class="form-grid-2">
            <div class="field">
              <label>Start Date &amp; Time *</label>
              <input v-model="activityForm.start_date" type="datetime-local" required />
            </div>
            <div class="field">
              <label>End Date &amp; Time *</label>
              <input v-model="activityForm.end_date" type="datetime-local" required />
            </div>
          </div>

          <div class="form-grid-3">
            <div class="field">
              <label>Assigned Coordinator</label>
              <select v-model="activityForm.coordinator">
                <option :value="null">None (Unassigned)</option>
                <option v-for="t in teachersList" :key="t.id" :value="t.id">
                  {{ t.full_name }} ({{ t.department || 'Faculty' }})
                </option>
              </select>
            </div>
            <div class="field">
              <label>Budget (₱)</label>
              <input v-model="activityForm.budget" type="number" step="0.01" min="0" placeholder="0.00" />
            </div>
            <div class="field">
              <label>Funding Source</label>
              <input v-model="activityForm.funding_source" placeholder="e.g. School MOOE, SEF, HRD Fund" />
            </div>
          </div>

          <div class="field">
            <label>Description &amp; Objectives</label>
            <textarea
              v-model="activityForm.description"
              rows="3"
              placeholder="Outline the goals, target faculty competency, and planned agenda..."
            ></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showActivityModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit" :disabled="activitiesStore.isSaving">
              {{ activitiesStore.isSaving ? 'Saving Activity...' : (editingActivityId ? 'Update Activity' : 'Create Activity') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ===================================================================== -->
    <!-- ATTENDANCE & PARTICIPANTS MODAL -->
    <!-- ===================================================================== -->
    <div v-if="showAttendanceModal" class="modal-backdrop" @click.self="showAttendanceModal = false">
      <div class="modal-card glass-panel modal-xl">
        <div class="modal-header">
          <div>
            <h3>👥 Faculty Attendance &amp; Participant Roster</h3>
            <p class="modal-sub">
              <strong>{{ currentActivity?.title }}</strong> • {{ currentActivity?.venue }}
            </p>
          </div>
          <button @click="showAttendanceModal = false" class="btn-close-modal">✕</button>
        </div>

        <!-- Add Participant Row -->
        <div class="add-participant-panel glass-panel">
          <div class="field-inline">
            <label>Enroll Faculty Member:</label>
            <select v-model="selectedTeacherId">
              <option value="">Select Faculty to Enroll...</option>
              <option
                v-for="t in availableTeachers"
                :key="t.id"
                :value="t.id"
              >
                {{ t.full_name }} ({{ t.department || 'Faculty' }})
              </option>
            </select>
          </div>
          <div class="field-inline">
            <label>Role:</label>
            <select v-model="selectedRole">
              <option value="Participant">Participant</option>
              <option value="Resource Speaker / Trainer">Resource Speaker / Trainer</option>
              <option value="Facilitator / Committee">Facilitator / Committee</option>
              <option value="Organizer / Coordinator">Organizer / Coordinator</option>
            </select>
          </div>
          <button
            type="button"
            @click="enrollTeacher"
            class="btn-enroll"
            :disabled="!selectedTeacherId"
          >
            + Enroll Teacher
          </button>
        </div>

        <!-- Participants Table -->
        <div class="participants-table-wrapper">
          <table class="participants-table">
            <thead>
              <tr>
                <th>Faculty Name</th>
                <th>Department &amp; Position</th>
                <th>Role in Activity</th>
                <th style="width: 220px;">Attendance Status</th>
                <th style="width: 110px; text-align: center;">Certificate</th>
                <th style="width: 80px; text-align: center;">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="part in currentActivity?.participants" :key="part.id">
                <td>
                  <strong>{{ part.teacher_name }}</strong>
                </td>
                <td class="text-sub">
                  {{ part.teacher_position || 'Faculty' }} • {{ part.teacher_department || 'Academic' }}
                </td>
                <td>
                  <span class="role-badge">{{ part.role }}</span>
                </td>
                <td>
                  <div class="attendance-btn-group">
                    <button
                      type="button"
                      :class="['btn-att', { active: part.attendance_status === 'Attended' }]"
                      @click="setAttendance(part, 'Attended')"
                    >
                      Attended
                    </button>
                    <button
                      type="button"
                      :class="['btn-exc', { active: part.attendance_status === 'Excused' }]"
                      @click="setAttendance(part, 'Excused')"
                    >
                      Excused
                    </button>
                    <button
                      type="button"
                      :class="['btn-abs', { active: part.attendance_status === 'Absent' }]"
                      @click="setAttendance(part, 'Absent')"
                    >
                      Absent
                    </button>
                  </div>
                </td>
                <td style="text-align: center;">
                  <input
                    type="checkbox"
                    :checked="part.certificate_issued"
                    @change="toggleCertificate(part, $event.target.checked)"
                    title="Mark certificate issued"
                  />
                </td>
                <td style="text-align: center;">
                  <button
                    type="button"
                    @click="removeParticipant(part.id)"
                    class="btn-del-part"
                    title="Remove from activity"
                  >
                    ✕
                  </button>
                </td>
              </tr>
              <tr v-if="!currentActivity?.participants?.length">
                <td colspan="6" class="no-participants">
                  No faculty participants enrolled yet. Use the selector above to enroll teachers.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="modal-actions">
          <button
            type="button"
            @click="markAllAttended"
            class="btn-mark-all"
            v-if="currentActivity?.participants?.length"
          >
            ✓ Mark All Enrolled as Attended
          </button>
          <button type="button" @click="showAttendanceModal = false" class="btn-submit">
            Done
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { useActivitiesStore } from '@/stores/activities'
import { usePDSStore } from '@/stores/pds'
import notify from '@/utils/notify'

const activitiesStore = useActivitiesStore()
const pdsStore = usePDSStore()

const loading = ref(true)
const activities = computed(() => activitiesStore.activities)
const stats = computed(() => activitiesStore.stats)
const currentActivity = computed(() => activitiesStore.currentActivity)

// Filter & Search
const searchQuery = ref('')
const filterType = ref('')
const filterModality = ref('')
const filterStatus = ref('All')

let searchTimer = null

const statusOptions = [
  { label: 'All Activities', value: 'All' },
  { label: 'Upcoming', value: 'Upcoming' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Postponed', value: 'Postponed' },
]

const activityTypes = [
  'Faculty Development / Training',
  'Faculty & Staff Meeting',
  'Institutional Seminar / Workshop',
  'School Assembly / Convocation',
  'Curriculum & Syllabi Review',
  'Accreditation & Compliance',
  'Community Extension & Outreach',
  'Co-Curricular / Student Activity',
  'Others',
]

// Modal & Forms
const showActivityModal = ref(false)
const editingActivityId = ref(null)
const activityForm = reactive({
  title: '',
  activity_type: 'Faculty Development / Training',
  modality: 'In-Person',
  venue: '',
  status: 'Upcoming',
  start_date: '',
  end_date: '',
  coordinator: null,
  budget: 0.00,
  funding_source: 'School MOOE',
  description: '',
})

// Attendance Modal
const showAttendanceModal = ref(false)
const selectedTeacherId = ref('')
const selectedRole = ref('Participant')
const teachersList = ref([])

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      activitiesStore.fetchActivities(),
      activitiesStore.fetchActivityStats(),
      loadTeachersList()
    ])
  } catch (err) {
    console.error('Activities initialization error:', err)
  } finally {
    loading.value = false
  }
})

const loadTeachersList = async () => {
  try {
    const res = await pdsStore.fetchTeachers()
    teachersList.value = res || pdsStore.teachers || []
  } catch (e) {
    console.error('Failed to load teachers for coordinator picker', e)
    teachersList.value = pdsStore.teachers || []
  }
}

const availableTeachers = computed(() => {
  if (!currentActivity.value?.participants) return teachersList.value
  const enrolledIds = new Set(currentActivity.value.participants.map(p => p.teacher))
  return teachersList.value.filter(t => !enrolledIds.has(t.id))
})

const applyFilters = () => {
  const params = {}
  if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
  if (filterType.value) params.activity_type = filterType.value
  if (filterModality.value) params.modality = filterModality.value
  if (filterStatus.value && filterStatus.value !== 'All') params.status = filterStatus.value

  activitiesStore.fetchActivities(params)
}

const debounceSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    applyFilters()
  }, 350)
}

// Format Helper
const formatDateTime = (dtStr) => {
  if (!dtStr) return 'TBD'
  const d = new Date(dtStr)
  return d.toLocaleDateString('en-PH', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusClass = (status) => {
  switch (status) {
    case 'Upcoming': return 'status-upcoming'
    case 'In Progress': return 'status-progress'
    case 'Completed': return 'status-completed'
    case 'Postponed': return 'status-postponed'
    case 'Cancelled': return 'status-cancelled'
    default: return ''
  }
}

// Create & Edit Handlers
const openCreateModal = () => {
  editingActivityId.value = null
  Object.assign(activityForm, {
    title: '',
    activity_type: 'Faculty Development / Training',
    modality: 'In-Person',
    venue: 'Main Campus Facility',
    status: 'Upcoming',
    start_date: '',
    end_date: '',
    coordinator: null,
    budget: 0.00,
    funding_source: 'School MOOE',
    description: '',
  })
  showActivityModal.value = true
}

const openEditModal = (act) => {
  editingActivityId.value = act.id
  Object.assign(activityForm, {
    title: act.title,
    activity_type: act.activity_type,
    modality: act.modality,
    venue: act.venue,
    status: act.status,
    start_date: act.start_date ? act.start_date.substring(0, 16) : '',
    end_date: act.end_date ? act.end_date.substring(0, 16) : '',
    coordinator: act.coordinator,
    budget: act.budget,
    funding_source: act.funding_source,
    description: act.description || '',
  })
  showActivityModal.value = true
}

const submitActivity = async () => {
  try {
    if (editingActivityId.value) {
      await activitiesStore.updateActivity(editingActivityId.value, activityForm)
      notify.success('Activity updated successfully!')
    } else {
      await activitiesStore.createActivity(activityForm)
      notify.success('New activity scheduled successfully!')
    }
    showActivityModal.value = false
    applyFilters()
  } catch (err) {
    notify.error('Failed to save activity. Please check input dates and values.')
  }
}

const confirmDelete = async (act) => {
  const confirmed = await notify.confirm({
    title: 'Delete Activity?',
    text: `Are you sure you want to delete the activity "${act.title}"?`,
    confirmButtonText: 'Yes, Delete Activity'
  })
  if (confirmed) {
    try {
      await activitiesStore.deleteActivity(act.id)
      notify.success('Activity deleted.')
    } catch (err) {
      notify.error('Failed to delete activity.')
    }
  }
}

// Attendance Handlers
const openAttendanceModal = async (act) => {
  await activitiesStore.fetchActivityDetail(act.id)
  selectedTeacherId.value = ''
  selectedRole.value = 'Participant'
  showAttendanceModal.value = true
}

const enrollTeacher = async () => {
  if (!selectedTeacherId.value) return
  try {
    await activitiesStore.addParticipant(currentActivity.value.id, {
      teacher_id: selectedTeacherId.value,
      role: selectedRole.value,
      attendance_status: 'Registered'
    })
    selectedTeacherId.value = ''
    notify.toast('Teacher enrolled in activity.', 'success')
  } catch (err) {
    notify.error('Failed to enroll teacher.')
  }
}

const setAttendance = async (part, status) => {
  try {
    await activitiesStore.updateParticipant(currentActivity.value.id, part.id, {
      attendance_status: status
    })
  } catch (err) {
    console.error('Failed to update attendance', err)
  }
}

const toggleCertificate = async (part, val) => {
  try {
    await activitiesStore.updateParticipant(currentActivity.value.id, part.id, {
      certificate_issued: val
    })
  } catch (err) {
    console.error('Failed to update certificate status', err)
  }
}

const removeParticipant = async (partId) => {
  const confirmed = await notify.confirm({
    title: 'Remove Participant?',
    text: 'Remove this teacher from the activity roster?',
    confirmButtonText: 'Yes, Remove'
  })
  if (confirmed) {
    await activitiesStore.removeParticipant(currentActivity.value.id, partId)
    notify.toast('Participant removed', 'info')
  }
}

const markAllAttended = async () => {
  if (!currentActivity.value?.participants?.length) return
  const updates = currentActivity.value.participants.map(p => ({
    id: p.id,
    attendance_status: 'Attended'
  }))
  await activitiesStore.batchUpdateAttendance(currentActivity.value.id, updates)
  notify.success('All participants marked as Attended.')
}
</script>

<style scoped>
.activities-view-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Header */
.activities-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-radius: var(--radius-md);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.icon-badge {
  font-size: 2.2rem;
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.3);
  padding: 0.75rem;
  border-radius: var(--radius-md);
}

.activities-header h2 {
  font-size: 1.45rem;
  color: #fff;
  margin-bottom: 0.25rem;
}

.sub-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.btn-create-activity {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-create-activity:hover {
  background: var(--accent-gold-hover);
  transform: translateY(-1px);
}

/* KPI Overview Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
}

.kpi-card {
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.kpi-icon {
  font-size: 2rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 0.6rem;
  border-radius: var(--radius-sm);
}

.kpi-info {
  display: flex;
  flex-direction: column;
}

.kpi-val {
  font-size: 1.7rem;
  font-weight: 800;
  color: var(--accent-gold);
  line-height: 1.1;
}

.kpi-lbl {
  font-size: 0.78rem;
  color: var(--text-secondary);
  margin-top: 0.2rem;
  font-weight: 600;
}

.kpi-upcoming .kpi-val { color: #38bdf8; }
.kpi-progress .kpi-val { color: #f59e0b; }
.kpi-completed .kpi-val { color: #34d399; }
.kpi-attendance .kpi-val { color: #a855f7; }

/* Filter & Search Toolbar */
.filter-toolbar {
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-box {
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 0 0.85rem;
}

.search-icon {
  font-size: 1rem;
  margin-right: 0.5rem;
  color: var(--text-muted);
}

.search-box input {
  border: none;
  background: transparent;
  padding: 0.75rem 0;
  width: 100%;
}

.btn-clear-search {
  background: transparent;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.filter-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.select-filter {
  flex: 1;
  min-width: 180px;
}

.status-pills {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.status-pill {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.4rem 0.85rem;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
  transition: all 0.2s;
}

.status-pill.active {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  border-color: var(--accent-gold);
  font-weight: 700;
}

/* Activities Grid */
.activities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem;
}

.activity-card {
  padding: 1.5rem;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 1px solid var(--border-color);
  transition: transform 0.2s, box-shadow 0.2s;
}

.activity-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.badge-status {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.65rem;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-upcoming { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
.status-progress { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.4); }
.status-completed { background: rgba(52, 211, 153, 0.2); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.4); }
.status-postponed { background: rgba(249, 115, 22, 0.2); color: #f97316; border: 1px solid rgba(249, 115, 22, 0.4); }
.status-cancelled { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); }

.badge-modality {
  font-size: 0.72rem;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.activity-title {
  font-size: 1.05rem;
  color: #fff;
  font-weight: 700;
  line-height: 1.35;
  margin-bottom: 0.4rem;
}

.badge-category {
  display: inline-block;
  font-size: 0.72rem;
  color: var(--accent-gold);
  background: rgba(245, 158, 11, 0.1);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.75rem;
}

.activity-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.activity-meta-list {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font-size: 0.78rem;
  color: var(--text-secondary);
  background: rgba(0, 0, 0, 0.2);
  padding: 0.85rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.meta-icon {
  font-size: 0.9rem;
}

.attendance-summary-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.85rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 6px;
  font-size: 0.78rem;
  margin-bottom: 1.25rem;
}

.summary-count {
  display: flex;
  gap: 0.4rem;
  color: var(--text-secondary);
}

.summary-count strong {
  color: var(--accent-gold);
}

.attended-count-pill {
  font-size: 0.72rem;
  color: #34d399;
  font-weight: 700;
}

.card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 1rem;
}

.btn-action-attendance {
  background: var(--accent-gold-subtle);
  color: var(--accent-gold);
  border: 1px solid rgba(245, 158, 11, 0.4);
  padding: 0.45rem 0.85rem;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 700;
  transition: all 0.2s;
}

.btn-action-attendance:hover {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
}

.btn-group-right {
  display: flex;
  gap: 0.4rem;
}

.btn-action-edit, .btn-action-del {
  background: rgba(255, 255, 255, 0.06);
  padding: 0.45rem 0.65rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

.btn-action-edit:hover { background: rgba(255, 255, 255, 0.15); }
.btn-action-del:hover { background: rgba(239, 68, 68, 0.3); }

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(4, 9, 23, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  padding: 1.5rem;
}

.modal-card {
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  background: #111a33;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-md);
  padding: 2rem;
}

.modal-lg { max-width: 750px; }
.modal-xl { max-width: 960px; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 0.75rem;
}

.modal-header h3 {
  color: var(--accent-gold);
  font-size: 1.25rem;
}

.modal-sub {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.btn-close-modal {
  background: transparent;
  color: var(--text-muted);
  font-size: 1.2rem;
}

.btn-close-modal:hover { color: #fff; }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

/* Attendance Modal Specific */
.add-participant-panel {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  padding: 1rem;
  border-radius: var(--radius-sm);
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.field-inline {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
  min-width: 220px;
}

.field-inline label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 600;
}

.btn-enroll {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  white-space: nowrap;
}

.btn-enroll:disabled { opacity: 0.4; cursor: not-allowed; }

.participants-table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.participants-table {
  width: 100%;
  border-collapse: collapse;
}

.participants-table th, .participants-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 0.82rem;
  text-align: left;
}

.participants-table th {
  background: rgba(0, 0, 0, 0.3);
  font-weight: 700;
  color: var(--text-secondary);
}

.role-badge {
  background: rgba(245, 158, 11, 0.15);
  color: var(--accent-gold);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 600;
}

.attendance-btn-group {
  display: flex;
  gap: 0.25rem;
}

.btn-att, .btn-exc, .btn-abs {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.15s;
}

.btn-att.active { background: #059669; color: #fff; border-color: #059669; }
.btn-exc.active { background: #d97706; color: #fff; border-color: #d97706; }
.btn-abs.active { background: #dc2626; color: #fff; border-color: #dc2626; }

.btn-del-part {
  background: transparent;
  color: #ef4444;
  font-size: 0.9rem;
  padding: 0.2rem 0.5rem;
}

.btn-mark-all {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.4);
  font-weight: 700;
  padding: 0.6rem 1.25rem;
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  margin-right: auto;
}

.btn-mark-all:hover {
  background: #34d399;
  color: var(--text-on-accent, #24120a);
}

.no-participants {
  text-align: center;
  color: var(--text-muted);
  padding: 2.5rem 1rem !important;
}

/* Empty & Loading */
.empty-state {
  text-align: center;
  padding: 4rem 1.5rem;
  border-radius: var(--radius-md);
}

.empty-icon { font-size: 3rem; margin-bottom: 0.75rem; }
.btn-create-empty {
  margin-top: 1rem;
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  padding: 0.65rem 1.5rem;
  border-radius: var(--radius-sm);
}

.loading-state {
  text-align: center;
  padding: 5rem 1rem;
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

@keyframes spin { to { transform: rotate(360deg); } }

/* Form Grids */
.form-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.form-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }

@media (max-width: 768px) {
  .form-grid-2, .form-grid-3 { grid-template-columns: 1fr; }
  .activities-header { flex-direction: column; align-items: flex-start; gap: 1rem; }
}

.field label {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.35rem;
}

.btn-cancel {
  background: var(--bg-surface-elevated);
  color: var(--text-secondary);
  padding: 0.55rem 1.25rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

.btn-submit {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  padding: 0.55rem 1.25rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}
</style>
