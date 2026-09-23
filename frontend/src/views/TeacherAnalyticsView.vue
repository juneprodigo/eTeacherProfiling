<template>
  <div class="analytics-container">
    <!-- Top Bar Navigation & Controls -->
    <div class="analytics-header glass-card">
      <div class="header-titles">
        <div class="breadcrumb">
          <span class="badge-dept">DepEd Faculty Intelligence</span>
          <span class="badge-live">Live Analytics</span>
        </div>
        <h1>Teacher's Analytics &amp; Training Hub</h1>
        <p class="subtitle">Real-time faculty profiling metrics, demographic distributions, and comprehensive CPD/training compliance tracking.</p>
      </div>

      <div class="tab-controls">
        <button
          @click="activeTab = 'demographics'"
          :class="['tab-btn', { active: activeTab === 'demographics' }]"
        >
          <span class="tab-icon">👥</span>
          <span>Demographics &amp; Profiling</span>
        </button>
        <button
          @click="activeTab = 'trainings'"
          :class="['tab-btn', { active: activeTab === 'trainings' }]"
        >
          <span class="tab-icon">🎯</span>
          <span>Training Monitoring Hub</span>
          <span v-if="trainingsData?.kpis?.no_records_count > 0" class="badge-alert">
            {{ trainingsData.kpis.no_records_count }}
          </span>
        </button>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 1: DEMOGRAPHICS & PROFILE ANALYTICS -->
    <!-- ========================================================================= -->
    <div v-if="activeTab === 'demographics'" class="tab-content">
      <!-- Loading / Error states -->
      <div v-if="loadingDemographics" class="loading-state">
        <div class="spinner"></div>
        <p>Analyzing faculty demographic records...</p>
      </div>

      <div v-else-if="demographicsData" class="demographics-grid">
        <!-- Overview KPIs -->
        <div class="kpi-row">
          <div class="kpi-card glass-card">
            <div class="kpi-icon icon-blue">👨‍🏫</div>
            <div class="kpi-meta">
              <span class="kpi-label">Total Faculty</span>
              <h2 class="kpi-value">{{ demographicsData.total_teachers }}</h2>
              <span class="kpi-sub">Active profiles</span>
            </div>
          </div>

          <div class="kpi-card glass-card">
            <div class="kpi-icon icon-emerald">📋</div>
            <div class="kpi-meta">
              <span class="kpi-label">PDS Completeness</span>
              <h2 class="kpi-value">{{ demographicsData.pds_completion_rate }}%</h2>
              <span class="kpi-sub">{{ demographicsData.complete_pds }} of {{ demographicsData.total_teachers }} verified</span>
            </div>
          </div>

          <div class="kpi-card glass-card">
            <div class="kpi-icon icon-gold">🏫</div>
            <div class="kpi-meta">
              <span class="kpi-label">Departments</span>
              <h2 class="kpi-value">{{ demographicsData.departments?.length || 0 }}</h2>
              <span class="kpi-sub">Academic units</span>
            </div>
          </div>

          <div class="kpi-card glass-card">
            <div class="kpi-icon icon-rose">⏳</div>
            <div class="kpi-meta">
              <span class="kpi-label">Pending PDS</span>
              <h2 class="kpi-value">{{ demographicsData.incomplete_pds }}</h2>
              <span class="kpi-sub">Awaiting full submission</span>
            </div>
          </div>
        </div>

        <!-- Row 1: Department Distribution & Sex at Birth -->
        <div class="grid-two-col">
          <!-- Department Distribution -->
          <div class="glass-card card-section">
            <div class="section-head">
              <h3>Faculty by Department</h3>
              <span class="count-tag">{{ demographicsData.departments?.length || 0 }} Departments</span>
            </div>
            <div class="distribution-list">
              <div
                v-for="dept in demographicsData.departments"
                :key="dept.name"
                class="dist-item"
              >
                <div class="dist-meta">
                  <span class="dist-name">{{ dept.name }}</span>
                  <span class="dist-count">{{ dept.count }} faculty ({{ dept.percentage }}%)</span>
                </div>
                <div class="progress-bar-bg">
                  <div
                    class="progress-bar-fill fill-gold"
                    :style="{ width: dept.percentage + '%' }"
                  ></div>
                </div>
              </div>
              <div v-if="!demographicsData.departments?.length" class="empty-text">
                No department records available.
              </div>
            </div>
          </div>

          <!-- Sex & Civil Status -->
          <div class="card-column">
            <!-- Sex at Birth -->
            <div class="glass-card card-section">
              <div class="section-head">
                <h3>Sex at Birth Demographics</h3>
              </div>
              <div class="sex-grid">
                <div
                  v-for="item in demographicsData.sex_distribution"
                  :key="item.label"
                  class="sex-stat-card"
                >
                  <span class="sex-icon">{{ item.label === 'Male' ? '👨' : (item.label === 'Female' ? '👩' : '👤') }}</span>
                  <div class="sex-info">
                    <h4>{{ item.label }}</h4>
                    <span class="sex-count">{{ item.count }} ({{ item.percentage }}%)</span>
                  </div>
                  <div class="mini-bar">
                    <div
                      class="mini-bar-fill"
                      :class="item.label === 'Female' ? 'fill-rose' : 'fill-blue'"
                      :style="{ width: item.percentage + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Civil Status -->
            <div class="glass-card card-section">
              <div class="section-head">
                <h3>Civil Status</h3>
              </div>
              <div class="pill-group">
                <div
                  v-for="civil in demographicsData.civil_distribution"
                  :key="civil.status"
                  class="stat-pill"
                >
                  <span class="pill-name">{{ civil.status }}</span>
                  <span class="pill-badge">{{ civil.count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Row 2: Age Demographics & Educational Attainment -->
        <div class="grid-two-col">
          <!-- Age Brackets -->
          <div class="glass-card card-section">
            <div class="section-head">
              <h3>Age Bracket Distribution</h3>
              <span class="count-tag">Generational Overview</span>
            </div>
            <div class="age-chart-container">
              <div
                v-for="age in demographicsData.age_distribution"
                :key="age.bracket"
                class="age-bar-group"
              >
                <div class="age-label-row">
                  <span class="age-bracket">{{ age.bracket }}</span>
                  <span class="age-stats">{{ age.count }} ({{ age.percentage }}%)</span>
                </div>
                <div class="progress-bar-bg">
                  <div
                    class="progress-bar-fill fill-blue"
                    :style="{ width: age.percentage + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Educational Attainment & Eligibility -->
          <div class="card-column">
            <!-- Educational Attainment -->
            <div class="glass-card card-section">
              <div class="section-head">
                <h3>Highest Educational Attainment</h3>
              </div>
              <div class="distribution-list">
                <div
                  v-for="edu in demographicsData.education_distribution"
                  :key="edu.level"
                  class="dist-item"
                >
                  <div class="dist-meta">
                    <span class="dist-name">🎓 {{ edu.level }}</span>
                    <span class="dist-count">{{ edu.count }} ({{ edu.percentage }}%)</span>
                  </div>
                  <div class="progress-bar-bg">
                    <div
                      class="progress-bar-fill fill-emerald"
                      :style="{ width: edu.percentage + '%' }"
                    ></div>
                  </div>
                </div>
                <div v-if="!demographicsData.education_distribution?.length" class="empty-text">
                  No educational records yet.
                </div>
              </div>
            </div>

            <!-- Civil Service Eligibility -->
            <div class="glass-card card-section">
              <div class="section-head">
                <h3>Civil Service Eligibility Profiles</h3>
              </div>
              <div class="pill-group">
                <div
                  v-for="cse in demographicsData.eligibility_distribution"
                  :key="cse.type"
                  class="stat-pill"
                >
                  <span class="pill-name">📜 {{ cse.type }}</span>
                  <span class="pill-badge">{{ cse.count }}</span>
                </div>
                <div v-if="!demographicsData.eligibility_distribution?.length" class="empty-text">
                  No eligibility records yet.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 2: TRAINING MONITORING HUB -->
    <!-- ========================================================================= -->
    <div v-else-if="activeTab === 'trainings'" class="tab-content">
      <!-- Multi-Criteria Filter Bar (Single Row) -->
      <div class="glass-card filter-toolbar">
        <div class="filter-row">
          <!-- Keyword Search -->
          <div class="filter-field field-search">
            <label>Search Training / Sponsor</label>
            <div class="search-input-wrap">
              <span class="search-icon">🔍</span>
              <input
                v-model="trainingFilters.search"
                @input="debounceFetchTrainings"
                type="text"
                placeholder="Title, Sponsor..."
              />
            </div>
          </div>

          <!-- Department Filter -->
          <div class="filter-field field-dept">
            <label>Department</label>
            <select v-model="trainingFilters.department" @change="fetchTrainings">
              <option value="">All Departments</option>
              <option
                v-for="d in trainingsData?.filter_options?.departments || []"
                :key="d"
                :value="d"
              >
                {{ d }}
              </option>
            </select>
          </div>

          <!-- Teacher Filter -->
          <div class="filter-field field-teacher">
            <label>Specific Faculty</label>
            <select v-model="trainingFilters.teacher_id" @change="fetchTrainings">
              <option value="">All Faculty</option>
              <option
                v-for="t in trainingsData?.filter_options?.teachers || []"
                :key="t.id"
                :value="t.id"
              >
                {{ t.name }}
              </option>
            </select>
          </div>

          <!-- Training Type Filter -->
          <div class="filter-field field-type">
            <label>LD Type</label>
            <select v-model="trainingFilters.ld_type" @change="fetchTrainings">
              <option value="">All Types</option>
              <option
                v-for="ld in trainingsData?.filter_options?.ld_types || []"
                :key="ld"
                :value="ld"
              >
                {{ ld }}
              </option>
            </select>
          </div>

          <!-- Year Filter -->
          <div class="filter-field field-year">
            <label>Year</label>
            <select v-model="trainingFilters.year" @change="fetchTrainings">
              <option value="">All Years</option>
              <option
                v-for="y in trainingsData?.filter_options?.years || []"
                :key="y"
                :value="y"
              >
                {{ y }}
              </option>
            </select>
          </div>

          <!-- Min Hours -->
          <div class="filter-field field-hours">
            <label>Min. Hrs</label>
            <input
              v-model="trainingFilters.min_hours"
              @input="debounceFetchTrainings"
              type="number"
              min="0"
              placeholder="Min"
            />
          </div>

          <!-- Reset Filter Button (Inline on the same row) -->
          <div class="filter-field field-reset">
            <button @click="resetTrainingFilters" class="btn-clear-filters" title="Reset all training filters">
              ↺ Reset
            </button>
          </div>
        </div>
      </div>

      <!-- Loading / Content -->
      <div v-if="loadingTrainings" class="loading-state">
        <div class="spinner"></div>
        <p>Filtering training &amp; seminar records...</p>
      </div>

      <div v-else-if="trainingsData" class="trainings-content">
        <!-- Training KPIs -->
        <div class="kpi-row">
          <div class="kpi-card glass-card">
            <div class="kpi-icon icon-gold">⏱️</div>
            <div class="kpi-meta">
              <span class="kpi-label">Total Training Hours</span>
              <h2 class="kpi-value">{{ trainingsData.kpis.total_training_hours }} hrs</h2>
              <span class="kpi-sub">{{ trainingsData.kpis.total_sessions }} sessions conducted</span>
            </div>
          </div>

          <div class="kpi-card glass-card">
            <div class="kpi-icon icon-blue">📊</div>
            <div class="kpi-meta">
              <span class="kpi-label">Avg. Hours / Faculty</span>
              <h2 class="kpi-value">{{ trainingsData.kpis.avg_hours_per_teacher }} hrs</h2>
              <span class="kpi-sub">Target: {{ trainingsData.kpis.target_hours }} hrs/year</span>
            </div>
          </div>

          <div class="kpi-card glass-card">
            <div class="kpi-icon icon-emerald">✅</div>
            <div class="kpi-meta">
              <span class="kpi-label">Compliance Rate</span>
              <h2 class="kpi-value">{{ trainingsData.kpis.compliance_rate }}%</h2>
              <span class="kpi-sub">{{ trainingsData.kpis.compliant_count }} faculty reached target</span>
            </div>
          </div>

          <div class="kpi-card glass-card">
            <div class="kpi-icon icon-rose">⚠️</div>
            <div class="kpi-meta">
              <span class="kpi-label">Needs Attention</span>
              <h2 class="kpi-value">{{ trainingsData.kpis.no_records_count }}</h2>
              <span class="kpi-sub">0 hours logged</span>
            </div>
          </div>
        </div>

        <!-- Training Type Breakdown Pills -->
        <div class="glass-card card-section">
          <div class="section-head">
            <h3>Training Interventions by Category</h3>
            <span class="count-tag">Distribution by LD Type</span>
          </div>
          <div class="ld-types-grid">
            <div
              v-for="ld in trainingsData.ld_types_breakdown"
              :key="ld.type"
              class="ld-card"
            >
              <div class="ld-head">
                <span class="ld-badge">{{ ld.type }}</span>
                <span class="ld-percent">{{ ld.percentage }}%</span>
              </div>
              <div class="ld-body">
                <div class="ld-metric">
                  <span class="ld-num">{{ ld.total_hours }}</span>
                  <span class="ld-unit">hours</span>
                </div>
                <div class="ld-sessions">{{ ld.session_count }} sessions</div>
              </div>
              <div class="progress-bar-bg">
                <div class="progress-bar-fill fill-gold" :style="{ width: ld.percentage + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Dual View Section: Compliance Table vs Individual Records -->
        <div class="glass-card card-section">
          <div class="section-head-with-actions">
            <div class="sub-tab-group">
              <button
                @click="trainingViewMode = 'compliance'"
                :class="['sub-tab', { active: trainingViewMode === 'compliance' }]"
              >
                🏅 Faculty Compliance &amp; Progress ({{ trainingsData.faculty_compliance?.length || 0 }})
              </button>
              <button
                @click="trainingViewMode = 'logs'"
                :class="['sub-tab', { active: trainingViewMode === 'logs' }]"
              >
                📜 Training Log Records ({{ trainingsData.records?.length || 0 }})
              </button>
            </div>

            <div class="table-actions">
              <label v-if="trainingViewMode === 'compliance'" class="checkbox-inline">
                <input type="checkbox" v-model="filterOnlyNeedsAttention" />
                <span>Show only Needs Attention (0 hrs)</span>
              </label>
              <button @click="exportTrainingCSV" class="btn-export-csv" title="Export current dataset to CSV">
                📥 Export CSV
              </button>
            </div>
          </div>

          <!-- Mode A: Faculty Compliance Table -->
          <div v-if="trainingViewMode === 'compliance'" class="table-wrapper">
            <table class="analytics-table">
              <thead>
                <tr>
                  <th>Teacher / Faculty</th>
                  <th>Department</th>
                  <th>Total Hours</th>
                  <th>Sessions</th>
                  <th>Target Benchmark ({{ trainingsData.kpis.target_hours }} hrs)</th>
                  <th>Last Training</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="f in displayedComplianceFaculty"
                  :key="f.teacher_id"
                >
                  <td>
                    <div class="faculty-name-cell">
                      <strong>{{ f.name }}</strong>
                      <span class="emp-id">{{ f.employee_id ? `#${f.employee_id}` : 'No ID' }}</span>
                    </div>
                  </td>
                  <td>{{ f.department || 'Unassigned' }}</td>
                  <td>
                    <strong class="hours-text">{{ f.total_hours }} hrs</strong>
                  </td>
                  <td>{{ f.session_count }}</td>
                  <td class="progress-cell">
                    <div class="compliance-bar-container">
                      <div class="progress-bar-bg">
                        <div
                          class="progress-bar-fill"
                          :class="f.status === 'Compliant' ? 'fill-emerald' : (f.status === 'In Progress' ? 'fill-gold' : 'fill-rose')"
                          :style="{ width: Math.min(100, Math.round((f.total_hours / trainingsData.kpis.target_hours) * 100)) + '%' }"
                        ></div>
                      </div>
                      <span class="compliance-percent">
                        {{ Math.round((f.total_hours / trainingsData.kpis.target_hours) * 100) }}%
                      </span>
                    </div>
                  </td>
                  <td>{{ f.last_training_date ? formatDate(f.last_training_date) : 'None' }}</td>
                  <td>
                    <span
                      class="status-pill"
                      :class="{
                        'status-compliant': f.status === 'Compliant',
                        'status-in-progress': f.status === 'In Progress',
                        'status-none': f.status === 'No Records'
                      }"
                    >
                      {{ f.status }}
                    </span>
                  </td>
                  <td>
                    <div class="action-buttons">
                      <router-link :to="`/teachers/${f.teacher_id}`" class="btn-table-action" title="View Full PDS">
                        View
                      </router-link>
                      <button @click="openPreview(f.teacher_id, f.name)" class="btn-table-action btn-preview-action" title="Preview CS Form 212">
                        👁️ PDF
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!displayedComplianceFaculty.length">
                  <td colspan="8" class="text-center py-4 text-muted">
                    No faculty records found matching current criteria.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Mode B: Detailed Training Logs Table -->
          <div v-else class="table-wrapper">
            <table class="analytics-table">
              <thead>
                <tr>
                  <th>Training / Seminar Title</th>
                  <th>Faculty Member</th>
                  <th>Department</th>
                  <th>Type</th>
                  <th>Inclusive Dates</th>
                  <th>Hours</th>
                  <th>Conducted / Sponsored By</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="rec in trainingsData.records" :key="rec.id">
                  <td>
                    <strong>{{ rec.training_title }}</strong>
                  </td>
                  <td>
                    <router-link :to="`/teachers/${rec.teacher_id}`" class="link-teacher">
                      {{ rec.teacher_name }}
                    </router-link>
                  </td>
                  <td>{{ rec.department || 'N/A' }}</td>
                  <td>
                    <span class="type-pill">{{ rec.ld_type }}</span>
                  </td>
                  <td>{{ formatDateRange(rec.from_date, rec.to_date) }}</td>
                  <td>
                    <strong class="hours-text">{{ rec.number_of_hours }} hrs</strong>
                  </td>
                  <td class="text-muted">{{ rec.conducted_sponsored_by }}</td>
                </tr>
                <tr v-if="!trainingsData.records?.length">
                  <td colspan="7" class="text-center py-4 text-muted">
                    No training records found matching filter criteria.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- PDF Preview Modal -->
    <PdfPreviewModal
      :show="showPreviewModal"
      :teacherId="previewTeacherId"
      :teacherName="previewTeacherName"
      @close="showPreviewModal = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/api'
import PdfPreviewModal from '@/components/PdfPreviewModal.vue'
import notify from '@/utils/notify'

const activeTab = ref('demographics')
const trainingViewMode = ref('compliance')
const filterOnlyNeedsAttention = ref(false)

// Demographics State
const loadingDemographics = ref(false)
const demographicsData = ref(null)

// Training Hub State
const loadingTrainings = ref(false)
const trainingsData = ref(null)
const trainingFilters = reactive({
  search: '',
  department: '',
  teacher_id: '',
  ld_type: '',
  year: '',
  min_hours: ''
})

// Preview Modal State
const showPreviewModal = ref(false)
const previewTeacherId = ref(null)
const previewTeacherName = ref('')

const openPreview = (id, name) => {
  previewTeacherId.value = id
  previewTeacherName.value = name
  showPreviewModal.value = true
}

// Fetch Demographics
const fetchDemographics = async () => {
  loadingDemographics.value = true
  try {
    const res = await api.get('/analytics/demographics/')
    demographicsData.value = res.data
  } catch (err) {
    console.error('Failed to load demographics:', err)
  } finally {
    loadingDemographics.value = false
  }
}

// Fetch Trainings
let debounceTimer = null
const debounceFetchTrainings = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchTrainings()
  }, 350)
}

const fetchTrainings = async () => {
  loadingTrainings.value = true
  try {
    const params = {}
    if (trainingFilters.search) params.search = trainingFilters.search
    if (trainingFilters.department) params.department = trainingFilters.department
    if (trainingFilters.teacher_id) params.teacher_id = trainingFilters.teacher_id
    if (trainingFilters.ld_type) params.ld_type = trainingFilters.ld_type
    if (trainingFilters.year) params.year = trainingFilters.year
    if (trainingFilters.min_hours) params.min_hours = trainingFilters.min_hours

    const res = await api.get('/analytics/trainings/', { params })
    trainingsData.value = res.data
  } catch (err) {
    console.error('Failed to load training analytics:', err)
  } finally {
    loadingTrainings.value = false
  }
}

const resetTrainingFilters = () => {
  trainingFilters.search = ''
  trainingFilters.department = ''
  trainingFilters.teacher_id = ''
  trainingFilters.ld_type = ''
  trainingFilters.year = ''
  trainingFilters.min_hours = ''
  fetchTrainings()
}

// Filtered Faculty in Compliance View
const displayedComplianceFaculty = computed(() => {
  if (!trainingsData.value?.faculty_compliance) return []
  if (filterOnlyNeedsAttention.value) {
    return trainingsData.value.faculty_compliance.filter(f => f.status === 'No Records')
  }
  return trainingsData.value.faculty_compliance
})

// Format Helpers
const formatDate = (d) => {
  if (!d) return ''
  const parsed = new Date(d)
  return parsed.toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' })
}

const formatDateRange = (from, to) => {
  if (!from && !to) return 'N/A'
  if (from && to && from === to) return formatDate(from)
  if (from && to) return `${formatDate(from)} – ${formatDate(to)}`
  return formatDate(from || to)
}

// CSV Export
const exportTrainingCSV = () => {
  if (trainingViewMode.value === 'compliance') {
    const list = displayedComplianceFaculty.value
    if (!list.length) return notify.warning('No faculty data to export.')
    const headers = ['Teacher Name', 'Employee ID', 'Department', 'Total Hours', 'Sessions', 'Last Training Date', 'Status']
    const rows = list.map(f => [
      `"${f.name}"`,
      `"${f.employee_id}"`,
      `"${f.department}"`,
      f.total_hours,
      f.session_count,
      `"${f.last_training_date || ''}"`,
      `"${f.status}"`
    ])
    downloadCSV([headers, ...rows], 'faculty_training_compliance.csv')
  } else {
    const list = trainingsData.value?.records || []
    if (!list.length) return notify.warning('No training records to export.')
    const headers = ['Teacher Name', 'Department', 'Training Title', 'Type', 'From Date', 'To Date', 'Hours', 'Sponsor']
    const rows = list.map(r => [
      `"${r.teacher_name}"`,
      `"${r.department}"`,
      `"${r.training_title.replace(/"/g, '""')}"`,
      `"${r.ld_type}"`,
      r.from_date || '',
      r.to_date || '',
      r.number_of_hours,
      `"${(r.conducted_sponsored_by || '').replace(/"/g, '""')}"`
    ])
    downloadCSV([headers, ...rows], 'training_seminar_records.csv')
  }
}

const downloadCSV = (rows, filename) => {
  const csvContent = 'data:text/csv;charset=utf-8,' + rows.map(e => e.join(',')).join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
}

onMounted(() => {
  fetchDemographics()
  fetchTrainings()
})
</script>

<style scoped>
.analytics-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Header */
.analytics-header {
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.badge-dept {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  color: var(--accent-gold);
}

.badge-live {
  font-size: 0.7rem;
  font-weight: 700;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: var(--accent-emerald);
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
}

.analytics-header h1 {
  font-size: 1.75rem;
  font-weight: 800;
  margin-bottom: 0.25rem;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
  max-width: 650px;
}

.tab-controls {
  display: flex;
  gap: 0.5rem;
  background: rgba(11, 19, 41, 0.6);
  padding: 0.35rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.tab-btn.active {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
}

.badge-alert {
  background: var(--accent-rose);
  color: white;
  font-size: 0.7rem;
  padding: 0.1rem 0.45rem;
  border-radius: 10px;
  font-weight: 800;
}

/* KPI Cards */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.kpi-card {
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.kpi-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  flex-shrink: 0;
}

.icon-blue { background: rgba(59, 130, 246, 0.15); color: var(--accent-blue); }
.icon-emerald { background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); }
.icon-gold { background: rgba(245, 158, 11, 0.15); color: var(--accent-gold); }
.icon-rose { background: rgba(244, 63, 94, 0.15); color: var(--accent-rose); }

.kpi-meta {
  display: flex;
  flex-direction: column;
}

.kpi-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kpi-value {
  font-size: 1.7rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0.1rem 0;
}

.kpi-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Grid Layouts */
.grid-two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 992px) {
  .grid-two-col {
    grid-template-columns: 1fr;
  }
}

.card-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card-section {
  padding: 1.5rem;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.section-head h3 {
  font-size: 1.05rem;
  font-weight: 700;
}

.count-tag {
  font-size: 0.75rem;
  color: var(--text-secondary);
  background: var(--bg-surface-elevated);
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

/* Progress & Distribution Bars */
.distribution-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.dist-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.dist-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.dist-name {
  font-weight: 600;
  color: var(--text-primary);
}

.dist-count {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.progress-bar-bg {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.fill-gold { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.fill-blue { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.fill-emerald { background: linear-gradient(90deg, #10b981, #34d399); }
.fill-rose { background: linear-gradient(90deg, #f43f5e, #fb7185); }

/* Sex Demographics */
.sex-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}

.sex-stat-card {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  padding: 1rem;
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sex-icon {
  font-size: 1.75rem;
}

.sex-info h4 {
  font-size: 0.95rem;
  margin-bottom: 0.15rem;
}

.sex-count {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.mini-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
}

.mini-bar-fill {
  height: 100%;
}

/* Pills */
.pill-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.stat-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  padding: 0.4rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
}

.pill-badge {
  background: var(--accent-gold-subtle);
  color: var(--accent-gold);
  font-weight: 700;
  font-size: 0.75rem;
  padding: 0.1rem 0.45rem;
  border-radius: 10px;
}

/* Age Chart */
.age-chart-container {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.age-bar-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.age-label-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.age-bracket {
  font-weight: 600;
}

.age-stats {
  color: var(--text-secondary);
}

/* ========================================================================= */
/* Training Hub Styles */
/* ========================================================================= */
.filter-toolbar {
  padding: 0.9rem 1.25rem;
  margin-bottom: 1.5rem;
}

.filter-row {
  display: flex;
  align-items: flex-end;
  gap: 0.65rem;
  width: 100%;
  flex-wrap: nowrap;
  overflow-x: auto;
  scrollbar-width: thin;
  padding-bottom: 0.2rem;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}

.filter-field label {
  display: block;
  font-size: 0.72rem;
  color: var(--accent-gold);
  font-weight: 700;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.field-search {
  flex: 2.2;
  min-width: 180px;
}

.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.65rem;
  font-size: 0.8rem;
  pointer-events: none;
  opacity: 0.6;
}

.search-input-wrap input {
  padding-left: 1.9rem !important;
  width: 100%;
}

.field-dept {
  flex: 1.4;
  min-width: 130px;
}

.field-teacher {
  flex: 1.5;
  min-width: 130px;
}

.field-type {
  flex: 1.2;
  min-width: 110px;
}

.field-year {
  flex: 0.9;
  min-width: 90px;
}

.field-hours {
  flex: 0.8;
  min-width: 75px;
}

.field-reset {
  flex-shrink: 0;
}

.filter-field input,
.filter-field select {
  height: 38px;
  background: rgba(15, 10, 7, 0.7);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 0.84rem;
  padding: 0 0.65rem;
  width: 100%;
  transition: all 0.2s ease;
}

.filter-field input:focus,
.filter-field select:focus {
  outline: none;
  border-color: var(--accent-gold);
  box-shadow: 0 0 10px rgba(254, 203, 144, 0.25);
}

.btn-clear-filters {
  height: 38px;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(254, 203, 144, 0.1);
  color: var(--text-secondary);
  font-size: 0.82rem;
  font-weight: 600;
  padding: 0 0.85rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.btn-clear-filters:hover {
  background: rgba(254, 203, 144, 0.22);
  border-color: var(--accent-gold);
  color: var(--accent-gold);
}

/* LD Types Grid */
.ld-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.ld-card {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  padding: 1rem;
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ld-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ld-badge {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--accent-gold);
}

.ld-percent {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.ld-metric {
  display: flex;
  align-items: baseline;
  gap: 0.35rem;
}

.ld-num {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-primary);
}

.ld-unit {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.ld-sessions {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Sub-Tab Table Switcher */
.section-head-with-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.sub-tab-group {
  display: flex;
  gap: 0.5rem;
}

.sub-tab {
  background: transparent;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.85rem;
  padding: 0.45rem 0.95rem;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
}

.sub-tab:hover {
  color: var(--text-primary);
  background: var(--bg-surface-elevated);
}

.sub-tab.active {
  background: var(--bg-surface-elevated);
  color: var(--accent-gold);
  border-color: var(--accent-gold);
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.checkbox-inline {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.82rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.checkbox-inline input {
  width: auto;
}

.btn-export-csv {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.8rem;
  padding: 0.4rem 0.8rem;
  border-radius: var(--radius-sm);
}

.btn-export-csv:hover {
  background: var(--accent-gold-subtle);
  border-color: var(--accent-gold);
  color: var(--accent-gold);
}

/* Table Styles */
.table-wrapper {
  overflow-x: auto;
}

.analytics-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.analytics-table th {
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  background: rgba(11, 19, 41, 0.4);
  border-bottom: 1px solid var(--border-color);
}

.analytics-table td {
  padding: 0.85rem 1rem;
  font-size: 0.85rem;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}

.analytics-table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.faculty-name-cell {
  display: flex;
  flex-direction: column;
}

.emp-id {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.hours-text {
  color: var(--accent-gold);
}

.compliance-bar-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 150px;
}

.compliance-percent {
  font-size: 0.75rem;
  font-weight: 700;
  min-width: 32px;
}

.status-pill {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.status-compliant {
  background: rgba(16, 185, 129, 0.15);
  color: var(--accent-emerald);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-in-progress {
  background: rgba(245, 158, 11, 0.15);
  color: var(--accent-gold);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.status-none {
  background: rgba(244, 63, 94, 0.15);
  color: var(--accent-rose);
  border: 1px solid rgba(244, 63, 94, 0.3);
}

.type-pill {
  font-size: 0.72rem;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  color: var(--text-primary);
}

.action-buttons {
  display: flex;
  gap: 0.4rem;
}

.btn-table-action {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  display: inline-flex;
  align-items: center;
}

.btn-table-action:hover {
  background: var(--accent-gold-subtle);
  border-color: var(--accent-gold);
  color: var(--accent-gold);
}

.btn-preview-action {
  color: var(--accent-gold);
}

.link-teacher {
  font-weight: 600;
  color: var(--text-primary);
}

.link-teacher:hover {
  color: var(--accent-gold);
}

/* Loading & Empty states */
.loading-state {
  text-align: center;
  padding: 4rem 1rem;
}

.spinner {
  width: 44px;
  height: 44px;
  border: 4px solid rgba(245, 158, 11, 0.15);
  border-top-color: var(--accent-gold);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

.empty-text {
  color: var(--text-muted);
  font-size: 0.85rem;
  font-style: italic;
  padding: 0.5rem 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
