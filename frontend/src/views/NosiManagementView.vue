<template>
  <div class="nosi-dashboard">
    <!-- Header Banner -->
    <div class="nosi-header glass-panel">
      <div class="header-main">
        <div class="deped-seal">🏛️</div>
        <div>
          <div class="badge-tag">CSC Form 122 • CSC-DBM JC No. 1, s. 2012 • DepEd Orders • CS Form 33</div>
          <h1>Teacher Service Records, NOSI, NOSA & Appointments</h1>
          <p class="subtitle">
            Comprehensive Civil Service Personnel History, 3-Year Step Increment Progression, Salary Standardization Adjustments, and Plantilla Appointments with File Attachments
          </p>
        </div>
      </div>
      <div class="header-actions">
        <button @click="triggerSmartAlertScan" class="btn-refresh-scan" :disabled="isScanning">
          <span :class="{'spin': isScanning}">⚡</span>
          {{ isScanning ? 'Evaluating Roster...' : 'Run Smart Alert Scan' }}
        </button>
        <button
          v-if="activeTab === 'service_records'"
          @click="openNewServiceRecordModal()"
          class="btn-create-nosi"
        >
          <span>+</span> Add Service Record
        </button>
        <button
          v-else-if="authStore.canManageAll && activeTab === 'records'"
          @click="openNewNosiModal"
          class="btn-create-nosi"
        >
          <span>+</span> Prepare New NOSI
        </button>
        <button
          v-else-if="authStore.canManageAll && activeTab === 'nosa'"
          @click="openNewNosaModal"
          class="btn-create-nosi"
        >
          <span>+</span> Record New NOSA
        </button>
        <button
          v-else-if="authStore.canManageAll && activeTab === 'appointments'"
          @click="openNewAppointmentModal"
          class="btn-create-nosi"
        >
          <span>+</span> Record Appointment
        </button>
      </div>
    </div>

    <!-- Teacher Selector & Profile Ribbon (For HR/Admin or Current Teacher) -->
    <div class="teacher-filter-bar glass-panel">
      <div class="filter-left">
        <label class="filter-label">
          <span class="icon">👤</span> <strong>Faculty Scoping:</strong>
        </label>
        <select
          v-if="authStore.canManageAll"
          v-model="selectedTeacherId"
          @change="onTeacherFilterChange"
          class="select-teacher-filter"
        >
          <option value="">All Monitored Faculty (Entire Roster)</option>
          <option v-for="t in teachersList" :key="t.id" :value="t.id">
            {{ t.user?.last_name }}, {{ t.user?.first_name }} — {{ t.position || 'Teacher' }} (ID: {{ t.employee_id || 'N/A' }})
          </option>
        </select>
        <div v-else class="teacher-badge-static">
          <strong>{{ authStore.fullName }}</strong> ({{ authStore.user?.employee_id || 'DepEd Faculty' }})
        </div>
      </div>

      <div class="filter-right" v-if="selectedTeacherSummary">
        <div class="teacher-ribbon-info">
          <span class="ribbon-tag pos">{{ selectedTeacherSummary.position || 'DepEd Teacher' }}</span>
          <span class="ribbon-tag dept">{{ selectedTeacherSummary.department || 'Schools Division Office' }}</span>
          <span class="ribbon-tag id">Emp ID: {{ selectedTeacherSummary.employee_id || 'N/A' }}</span>
          <button
            v-if="activeTab === 'service_records'"
            @click="downloadTeacherServiceRecord(selectedTeacherSummary.id)"
            class="btn-csc-export"
            title="Download Official CSC Form 122 Service Record Excel"
          >
            📥 Export CSC Form 122
          </button>
        </div>
      </div>
    </div>

    <!-- Smart Alerts & Notifications -->
    <div class="alerts-container">
      <div class="alerts-header">
        <div class="alert-title-wrap">
          <span class="bell-icon">🔔</span>
          <h3>Smart Alert Center & System Notifications</h3>
          <span v-if="unreadAlertsCount > 0" class="badge-alert-count">{{ unreadAlertsCount }} Pending</span>
        </div>
        <div class="alert-controls">
          <button v-if="unreadAlertsCount > 0" @click="markAllAlertsRead" class="btn-ghost-sm">Mark All As Read</button>
        </div>
      </div>

      <div v-if="alerts.length === 0" class="alerts-empty">
        <span class="icon">✨</span>
        <p>All teacher service records and step increments are up to date. No overdue increments or missing requirement flags found.</p>
      </div>

      <div v-else class="alerts-grid">
        <div
          v-for="alert in alerts"
          :key="alert.id"
          :class="['alert-card', alert.severity.toLowerCase(), { 'is-read': alert.is_read }]"
        >
          <div class="alert-side-indicator"></div>
          <div class="alert-content">
            <div class="alert-top">
              <span class="alert-badge">{{ formatAlertType(alert.alert_type) }}</span>
              <span class="alert-time">{{ formatDate(alert.created_at) }}</span>
            </div>
            <h4 class="alert-headline">{{ alert.title }}</h4>
            <p class="alert-msg">{{ alert.message }}</p>
            <div class="alert-bottom">
              <span class="alert-target-teacher">👤 {{ alert.teacher_name }}</span>
              <button v-if="!alert.is_read" @click="markAlertRead(alert.id)" class="btn-mark-read">
                Dismiss
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Metrics Row -->
    <div class="metrics-grid">
      <div class="metric-card glass-panel">
        <div class="metric-icon blue">📜</div>
        <div class="metric-data">
          <h3>{{ serviceRecords.length }}</h3>
          <p>Service Record Entries</p>
        </div>
      </div>

      <div class="metric-card glass-panel">
        <div class="metric-icon amber">⏳</div>
        <div class="metric-data">
          <h3>{{ upcomingCount }}</h3>
          <p>Due / Upcoming NOSI</p>
        </div>
      </div>

      <div class="metric-card glass-panel">
        <div class="metric-icon emerald">📋</div>
        <div class="metric-data">
          <h3>{{ records.length }}</h3>
          <p>Issued NOSI Records</p>
        </div>
      </div>

      <div class="metric-card glass-panel">
        <div class="metric-icon purple">⚖️</div>
        <div class="metric-data">
          <h3>{{ nosaRecords.length }}</h3>
          <p>NOSA Adjustments</p>
        </div>
      </div>

      <div class="metric-card glass-panel">
        <div class="metric-icon cyan">📑</div>
        <div class="metric-data">
          <h3>{{ appointmentRecords.length }}</h3>
          <p>Appointments Tracked</p>
        </div>
      </div>
    </div>

    <!-- Main Tabs -->
    <div class="tab-nav">
      <button
        :class="['tab-btn', { active: activeTab === 'service_records' }]"
        @click="activeTab = 'service_records'"
      >
        <span>📜</span> 1. Service Records (CSC Form 122)
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'records' }]"
        @click="activeTab = 'records'"
      >
        <span>📄</span> 2. NOSI (Step Increments)
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'nosa' }]"
        @click="activeTab = 'nosa'"
      >
        <span>⚖️</span> 3. NOSA (Salary Adjustments)
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'appointments' }]"
        @click="activeTab = 'appointments'"
      >
        <span>📑</span> 4. Appointments (CS Form 33)
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'eligibility' }]"
        @click="activeTab = 'eligibility'"
      >
        <span>🎯</span> 5. 3-Year Step Progression Matrix
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'salary_table' }]"
        @click="activeTab = 'salary_table'"
      >
        <span>📊</span> 6. DepEd Salary Scale (Steps 1–8)
      </button>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 1: TEACHER SERVICE RECORDS (CSC FORM NO. 122)                         -->
    <!-- ========================================================================= -->
    <div v-if="activeTab === 'service_records'" class="tab-panel glass-panel">
      <div class="panel-header">
        <div>
          <h3>Civil Service Commission Form No. 122 — Teacher Service Records</h3>
          <p class="panel-desc">
            Official employment history summarized per teacher. Click the drill-down icon (▶) to expand the chronological appointment history, upload supporting scans, or export official CSC Form 122.
          </p>
        </div>
        <div class="panel-filters">
          <!-- Prominent Add Service Record Button right in the toolbar! -->
          <button
            @click="openNewServiceRecordModal()"
            class="btn-create-nosi btn-add-sr-primary"
            title="Encode a new service record entry"
          >
            <span class="plus-icon">+</span> Add Service Record
          </button>
          
          <div class="expand-collapse-btns">
            <button @click="expandAllTeachers" class="btn-toggle-all" title="Expand All Teachers">
              <span>▼</span> Expand All
            </button>
            <button @click="collapseAllTeachers" class="btn-toggle-all" title="Collapse All Teachers">
              <span>▲</span> Collapse All
            </button>
          </div>

          <input
            v-model="serviceRecordSearch"
            type="text"
            placeholder="Search by Teacher, Rank, School, Remarks..."
            class="search-input"
          />
          <button
            v-if="selectedTeacherId || (teachersList.length === 1)"
            @click="downloadTeacherServiceRecord(selectedTeacherId || teachersList[0]?.id)"
            class="btn-csc-download-header"
            title="Export CSC Form 122 Excel"
          >
            📥 Export CSC Form 122
          </button>
        </div>
      </div>

      <div v-if="loadingServiceRecords" class="loading-state">
        Loading Service Records...
      </div>

      <div v-else-if="teacherServiceRecordSummaries.length === 0" class="empty-state">
        <p>No service record summaries found matching your filter. Click <strong>"Add Service Record"</strong> to encode past or current teaching appointments.</p>
        <button @click="openNewServiceRecordModal()" class="btn-action-primary-sm" style="margin-top: 0.75rem;">
          <span>+</span> Add Service Record Now
        </button>
      </div>

      <div v-else class="table-responsive">
        <table class="data-table summary-master-table">
          <thead>
            <tr>
              <th class="th-drilldown" style="width: 44px; text-align: center;">Drill Down</th>
              <th>Teacher Details</th>
              <th>Current Position & Station</th>
              <th>Appointment Status & Salary</th>
              <th>Service Tenure & Period</th>
              <th>Attached Scans</th>
              <th style="text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="t in teacherServiceRecordSummaries" :key="t.teacherId">
              <!-- Master Summary Row -->
              <tr
                :class="['teacher-summary-row', { 'is-expanded': isExpanded(t.teacherId) }]"
                @click="toggleDrillDown(t.teacherId)"
              >
                <td class="drilldown-cell" @click.stop="toggleDrillDown(t.teacherId)">
                  <button
                    class="btn-drilldown-toggle"
                    :class="{ 'expanded': isExpanded(t.teacherId) }"
                    :title="isExpanded(t.teacherId) ? 'Collapse Service Records' : 'Expand Service Records'"
                  >
                    <span class="chevron-icon">{{ isExpanded(t.teacherId) ? '▼' : '▶' }}</span>
                  </button>
                </td>
                <td>
                  <div class="teacher-profile-cell">
                    <div class="teacher-avatar-circle">
                      {{ t.initials }}
                    </div>
                    <div class="teacher-name-box">
                      <strong class="teacher-display-name">{{ t.teacherName }}</strong>
                      <span class="teacher-emp-id">Emp ID: {{ t.employeeId || 'N/A' }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="teacher-curr-pos"><strong>{{ t.currentPosition || 'Teacher' }}</strong></div>
                  <div class="teacher-station">{{ t.department || 'Department of Education' }}</div>
                </td>
                <td>
                  <span class="status-pill appt-status">{{ t.currentStatus || 'Permanent' }}</span>
                  <span v-if="t.currentSG" class="sg-badge">SG {{ t.currentSG }} Step {{ t.currentStep || 1 }}</span>
                  <div class="salary-main" v-if="t.currentMonthlySalary">
                    ₱{{ formatMoney(t.currentMonthlySalary) }}/mo
                  </div>
                </td>
                <td>
                  <div class="span-display">
                    <strong>{{ t.serviceSpan }}</strong>
                  </div>
                  <span class="records-count-badge">{{ t.records.length }} Service {{ t.records.length === 1 ? 'Record' : 'Records' }}</span>
                </td>
                <td>
                  <span v-if="t.documentsCount > 0" class="docs-count-chip">
                    📎 {{ t.documentsCount }} {{ t.documentsCount === 1 ? 'Scan' : 'Scans' }}
                  </span>
                  <span v-else class="no-file-tag">No Scans</span>
                </td>
                <td class="summary-actions-cell" @click.stop>
                  <div class="btn-group-actions" style="justify-content: flex-end;">
                    <button
                      @click="openNewServiceRecordModal(t.teacherId)"
                      class="btn-action-primary-sm"
                      title="Add a new service record entry for this teacher"
                    >
                      <span>+</span> Add Record
                    </button>
                    <button
                      @click="downloadTeacherServiceRecord(t.teacherId)"
                      class="btn-icon"
                      title="Download Official CSC Form 122 (Excel)"
                    >
                      📥 CSC 122
                    </button>
                  </div>
                </td>
              </tr>

              <!-- Drill Down Detail Row (Expanded Records) -->
              <tr v-if="isExpanded(t.teacherId)" class="drilldown-detail-row">
                <td colspan="7" class="drilldown-container-td">
                  <div class="drilldown-subtable-wrapper glass-panel">
                    <div class="drilldown-header">
                      <div class="drilldown-title">
                        <span class="icon">📜</span>
                        <h4>Official Service Record History (CSC Form 122) — {{ t.teacherName }}</h4>
                        <span class="sub-badge">{{ t.records.length }} Entries</span>
                      </div>
                      <div class="drilldown-header-actions">
                        <button
                          @click="openNewServiceRecordModal(t.teacherId)"
                          class="btn-create-sub-entry"
                        >
                          <span>+</span> Add Record for {{ t.teacherName.split(',')[0] }}
                        </button>
                        <button
                          @click="downloadTeacherServiceRecord(t.teacherId)"
                          class="btn-icon"
                          title="Download CSC Form 122"
                        >
                          📥 Export Excel
                        </button>
                      </div>
                    </div>

                    <div v-if="t.records.length === 0" class="empty-subtable">
                      <p>No service records encoded yet for {{ t.teacherName }}. Click <strong>"+ Add Record"</strong> to record their appointment history.</p>
                    </div>

                    <div v-else class="table-responsive">
                      <table class="inner-data-table">
                        <thead>
                          <tr>
                            <th>Inclusive Dates</th>
                            <th>Designation / Rank</th>
                            <th>Status</th>
                            <th>Salary (Monthly / Annual)</th>
                            <th>Station / Branch</th>
                            <th>LWOP</th>
                            <th>Separation</th>
                            <th>Remarks</th>
                            <th>Attached Scan</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="sr in t.records" :key="sr.id">
                            <td>
                              <div class="date-range">
                                <strong>{{ formatDate(sr.from_date) }}</strong>
                                <span class="to-arrow">➔</span>
                                <span :class="['date-end', { 'is-present': sr.to_present }]">
                                  {{ sr.to_present ? 'Present' : formatDate(sr.to_date) }}
                                </span>
                              </div>
                            </td>
                            <td>
                              <div class="pos-title"><strong>{{ sr.designation }}</strong></div>
                            </td>
                            <td>
                              <span class="status-pill appt-status">{{ sr.status_of_appointment }}</span>
                              <span v-if="sr.salary_grade" class="sg-badge">SG {{ sr.salary_grade }} Step {{ sr.step || 1 }}</span>
                            </td>
                            <td>
                              <div class="salary-main">₱{{ formatMoney(sr.monthly_salary) }}/mo</div>
                              <div class="salary-sub">₱{{ formatMoney(sr.annual_salary) }}/yr</div>
                            </td>
                            <td>
                              <div class="station-name">{{ sr.station_office }}</div>
                              <span class="branch-tag">{{ sr.branch }}</span>
                            </td>
                            <td>
                              <span :class="['lwop-pill', { 'has-lwop': sr.lwop_dates && sr.lwop_dates !== 'NONE' }]">
                                {{ sr.lwop_dates || 'NONE' }}
                              </span>
                            </td>
                            <td>
                              <div v-if="sr.separation_date || sr.separation_cause">
                                <div class="sep-cause">{{ sr.separation_cause }}</div>
                                <div class="sep-date">{{ formatDate(sr.separation_date) }}</div>
                              </div>
                              <span v-else class="text-muted-dash">—</span>
                            </td>
                            <td>
                              <div class="remarks-cell" :title="sr.remarks">{{ sr.remarks || '—' }}</div>
                            </td>
                            <td>
                              <div v-if="sr.document_file" class="file-chip">
                                <a :href="sr.document_file" target="_blank" class="btn-doc-link" title="Open Attached Document">
                                  📎 {{ sr.file_name || 'Scanned File' }}
                                </a>
                              </div>
                              <span v-else class="no-file-tag">No upload</span>
                            </td>
                            <td>
                              <div class="btn-group-actions">
                                <button
                                  @click="openEditServiceRecordModal(sr)"
                                  class="btn-icon"
                                  title="Edit Service Record Entry"
                                >
                                  ✏️
                                </button>
                                <button
                                  @click="deleteServiceRecord(sr.id)"
                                  class="btn-icon danger"
                                  title="Delete Entry"
                                >
                                  🗑️
                                </button>
                              </div>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 2: NOSI (NOTICE OF STEP INCREMENT) & REQUIREMENTS CHECKLIST          -->
    <!-- ========================================================================= -->
    <div v-if="activeTab === 'records'" class="tab-panel glass-panel">
      <div class="panel-header">
        <div>
          <h3>DepEd Notice of Step Increment & Requirement Verification</h3>
          <p class="panel-desc">
            Track, process, and verify the 5 Key Processing Requirements needed to claim step increments and salary differentials.
          </p>
        </div>
        <div class="panel-filters">
          <input
            v-model="recordSearch"
            type="text"
            placeholder="Search by NOSI No., Teacher Name..."
            class="search-input"
          />
        </div>
      </div>

      <!-- Key Requirements Guide Box -->
      <div class="requirements-infobox">
        <div class="info-title">
          <span>📌</span> <strong>Key Requirements for Processing DepEd Step Increment & Differential:</strong>
        </div>
        <div class="requirements-pill-row">
          <span class="req-tag">1. Approved NOSI</span>
          <span class="req-tag">2. Annex D / Relevant forms</span>
          <span class="req-tag">3. Payslips / payroll records (before & after inclusion)</span>
          <span class="req-tag">4. Latest Appointment</span>
          <span class="req-tag">5. Updated Service Record</span>
        </div>
      </div>

      <div v-if="loadingRecords" class="loading-state">
        Loading NOSI records...
      </div>

      <div v-else-if="filteredRecords.length === 0" class="empty-state">
        <p>No NOSI records found. Click <strong>"Prepare New NOSI"</strong> to generate one for eligible teachers.</p>
      </div>

      <div v-else class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>NOSI Ref / Date</th>
              <th>Teacher Details</th>
              <th>Step Progression</th>
              <th>Differential</th>
              <th>Requirements Checklist (5 Key Items)</th>
              <th>Direct Upload</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rec in filteredRecords" :key="rec.id">
              <td>
                <div class="resi-number"><strong>{{ rec.nosi_number || `NOSI-${rec.id}` }}</strong></div>
                <div class="resi-sub">{{ formatDate(rec.effective_date) }}</div>
              </td>
              <td>
                <div class="teacher-name">{{ rec.teacher_name }}</div>
                <div class="teacher-sub">{{ rec.teacher_position }} • {{ rec.teacher_department }}</div>
              </td>
              <td>
                <div class="step-transition">
                  <span class="step-badge from">SG {{ rec.previous_salary_grade }} Step {{ rec.previous_step }}</span>
                  <span class="arrow">➔</span>
                  <span class="step-badge to">Step {{ rec.new_step }}</span>
                </div>
                <div class="salary-sub">
                  ₱{{ formatMoney(rec.previous_monthly_salary) }} ➔ ₱{{ formatMoney(rec.new_monthly_salary) }}
                </div>
              </td>
              <td>
                <div class="differential-badge">
                  +₱{{ formatMoney(rec.monthly_differential) }}/mo
                </div>
              </td>
              <td class="req-cell">
                <div class="checklist-progress-bar">
                  <div
                    class="bar-fill"
                    :style="{ width: rec.requirements_completion_rate.percentage + '%' }"
                    :class="{ 'full': rec.requirements_completion_rate.is_fully_compliant }"
                  ></div>
                </div>
                <span class="progress-label">
                  {{ rec.requirements_completion_rate.completed }}/5 Requirements Verified ({{ rec.requirements_completion_rate.percentage }}%)
                </span>
                
                <div class="checklist-checkboxes">
                  <label :class="['chk-item', { checked: rec.has_approved_nosi }]">
                    <input
                      type="checkbox"
                      :checked="rec.has_approved_nosi"
                      :disabled="!authStore.canManageAll"
                      @change="toggleReq(rec, 'has_approved_nosi', $event.target.checked)"
                    />
                    Approved NOSI
                  </label>
                  <label :class="['chk-item', { checked: rec.has_annex_d }]">
                    <input
                      type="checkbox"
                      :checked="rec.has_annex_d"
                      :disabled="!authStore.canManageAll"
                      @change="toggleReq(rec, 'has_annex_d', $event.target.checked)"
                    />
                    Annex D
                  </label>
                  <label :class="['chk-item', { checked: rec.has_payslips }]">
                    <input
                      type="checkbox"
                      :checked="rec.has_payslips"
                      :disabled="!authStore.canManageAll"
                      @change="toggleReq(rec, 'has_payslips', $event.target.checked)"
                    />
                    Payslips
                  </label>
                  <label :class="['chk-item', { checked: rec.has_latest_appointment }]">
                    <input
                      type="checkbox"
                      :checked="rec.has_latest_appointment"
                      :disabled="!authStore.canManageAll"
                      @change="toggleReq(rec, 'has_latest_appointment', $event.target.checked)"
                    />
                    Appointment
                  </label>
                  <label :class="['chk-item', { checked: rec.has_updated_service_record }]">
                    <input
                      type="checkbox"
                      :checked="rec.has_updated_service_record"
                      :disabled="!authStore.canManageAll"
                      @change="toggleReq(rec, 'has_updated_service_record', $event.target.checked)"
                    />
                    Service Record
                  </label>
                </div>
              </td>
              <td>
                <div v-if="rec.document_file" class="file-chip">
                  <a :href="rec.document_file" target="_blank" class="btn-doc-link" title="Open Attached NOSI">
                    📎 {{ rec.file_name || 'Signed NOSI' }}
                  </a>
                </div>
                <span v-else class="no-file-tag">No direct scan</span>
              </td>
              <td>
                <span :class="['status-pill', rec.status.toLowerCase()]">
                  {{ formatStatus(rec.status) }}
                </span>
              </td>
              <td>
                <div class="btn-group-actions">
                  <button
                    @click="downloadNosiDoc(rec)"
                    class="btn-icon"
                    title="Download Official DepEd NOSI Form (Excel)"
                  >
                    📥 Form
                  </button>
                  <button
                    @click="openUploadModal(rec)"
                    class="btn-icon"
                    title="Upload / Manage Supporting Documents"
                  >
                    📎 Docs ({{ rec.documents ? rec.documents.length : 0 }})
                  </button>
                  <button
                    v-if="authStore.canManageAll"
                    @click="openEditModal(rec)"
                    class="btn-icon"
                    title="Edit Record"
                  >
                    ✏️
                  </button>
                  <button
                    v-if="authStore.canManageAll"
                    @click="deleteNosiRecord(rec.id)"
                    class="btn-icon danger"
                    title="Delete NOSI"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 3: NOSA (NOTICE OF SALARY ADJUSTMENT)                                  -->
    <!-- ========================================================================= -->
    <div v-if="activeTab === 'nosa'" class="tab-panel glass-panel">
      <div class="panel-header">
        <div>
          <h3>Notice of Salary Adjustment (NOSA) History & Data Entry</h3>
          <p class="panel-desc">
            Issued upon implementation of Salary Standardization Law (SSL) tranches, National Budget Circulars, and Executive Orders.
          </p>
        </div>
        <div class="panel-filters">
          <input
            v-model="nosaSearch"
            type="text"
            placeholder="Search by NOSA No., Legal Basis, Teacher..."
            class="search-input"
          />
        </div>
      </div>

      <div v-if="loadingNosa" class="loading-state">
        Loading NOSA records...
      </div>

      <div v-else-if="filteredNosaRecords.length === 0" class="empty-state">
        <p>No NOSA records found. Click <strong>"Record New NOSA"</strong> to encode salary adjustments under new SSL tranches.</p>
      </div>

      <div v-else class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>NOSA Ref / Issued</th>
              <th>Teacher Details</th>
              <th>Effective Date & Legal Basis</th>
              <th>Grade & Step</th>
              <th>Salary Adjustment Transition</th>
              <th>Monthly Differential</th>
              <th>Status</th>
              <th>Attached Signed NOSA</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="nosa in filteredNosaRecords" :key="nosa.id">
              <td>
                <div class="resi-number"><strong>{{ nosa.nosa_number || `NOSA-${nosa.id}` }}</strong></div>
                <div class="resi-sub">{{ formatDate(nosa.date_issued) }}</div>
              </td>
              <td>
                <div class="teacher-name">{{ nosa.teacher_name }}</div>
                <div class="teacher-sub">{{ nosa.position_title || nosa.teacher_position }}</div>
              </td>
              <td>
                <div class="nosa-eff-date"><strong>Effective: {{ formatDate(nosa.effective_date) }}</strong></div>
                <div class="legal-basis-text">{{ nosa.legal_basis }}</div>
              </td>
              <td>
                <span class="step-badge to">SG {{ nosa.salary_grade }} Step {{ nosa.step }}</span>
              </td>
              <td>
                <div class="salary-transition-row">
                  <span class="prev-sal">₱{{ formatMoney(nosa.previous_monthly_salary) }}</span>
                  <span class="arrow">➔</span>
                  <strong class="new-sal">₱{{ formatMoney(nosa.adjusted_monthly_salary) }}</strong>
                </div>
              </td>
              <td>
                <div class="differential-badge">
                  +₱{{ formatMoney(nosa.monthly_differential) }}/mo
                </div>
              </td>
              <td>
                <span :class="['status-pill', nosa.status.toLowerCase()]">
                  {{ nosa.status }}
                </span>
              </td>
              <td>
                <div v-if="nosa.document_file" class="file-chip">
                  <a :href="nosa.document_file" target="_blank" class="btn-doc-link" title="Open Signed NOSA">
                    📎 {{ nosa.file_name || 'Signed NOSA' }}
                  </a>
                </div>
                <span v-else class="no-file-tag">No scan</span>
              </td>
              <td>
                <div class="btn-group-actions">
                  <button
                    @click="downloadNosaExcel(nosa.id)"
                    class="btn-icon"
                    title="Download Official NOSA Form (Excel)"
                  >
                    📥 Form
                  </button>
                  <button
                    v-if="authStore.canManageAll"
                    @click="openEditNosaModal(nosa)"
                    class="btn-icon"
                    title="Edit NOSA"
                  >
                    ✏️
                  </button>
                  <button
                    v-if="authStore.canManageAll"
                    @click="deleteNosaRecord(nosa.id)"
                    class="btn-icon danger"
                    title="Delete NOSA"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 4: APPOINTMENTS HISTORY (CS FORM NO. 33 / KSS)                        -->
    <!-- ========================================================================= -->
    <div v-if="activeTab === 'appointments'" class="tab-panel glass-panel">
      <div class="panel-header">
        <div>
          <h3>Civil Service Commission Form No. 33 / KSS Appointments</h3>
          <p class="panel-desc">
            Plantilla item assignments, original/promotional appointments, CSC attestations, and assumption dates.
          </p>
        </div>
        <div class="panel-filters">
          <input
            v-model="appointmentSearch"
            type="text"
            placeholder="Search by Item No., Position, Nature..."
            class="search-input"
          />
        </div>
      </div>

      <div v-if="loadingAppointments" class="loading-state">
        Loading Appointments...
      </div>

      <div v-else-if="filteredAppointmentRecords.length === 0" class="empty-state">
        <p>No appointment records found. Click <strong>"Record Appointment"</strong> to encode CS Form 33 plantilla items.</p>
      </div>

      <div v-else class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>Plantilla Item / Ref</th>
              <th>Teacher Details</th>
              <th>Position & Nature</th>
              <th>Status</th>
              <th>Compensation</th>
              <th>Key Dates (Signed / Assumption)</th>
              <th>CSC Attestation</th>
              <th>Vice / Incumbent</th>
              <th>Attached CS Form 33</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in filteredAppointmentRecords" :key="app.id">
              <td>
                <div class="item-number"><strong>{{ app.plantilla_item_no }}</strong></div>
                <div class="resi-sub">{{ app.appointment_number || `APPT-${app.id}` }}</div>
              </td>
              <td>
                <div class="teacher-name">{{ app.teacher_name }}</div>
                <div class="teacher-sub">Emp ID: {{ app.teacher_employee_id || 'N/A' }}</div>
              </td>
              <td>
                <div class="pos-title"><strong>{{ app.position_title }}</strong></div>
                <span class="nature-pill">{{ app.nature_of_appointment }}</span>
              </td>
              <td>
                <span class="status-pill appt-status">{{ app.status_of_appointment }}</span>
              </td>
              <td>
                <div class="salary-main">₱{{ formatMoney(app.monthly_rate) }}/mo</div>
                <div class="salary-sub">SG {{ app.salary_grade }} Step {{ app.step }}</div>
              </td>
              <td>
                <div class="date-row"><span>Signed:</span> {{ formatDate(app.date_of_signing) }}</div>
                <div class="date-row"><strong>Assumed:</strong> {{ formatDate(app.date_of_assumption) }}</div>
              </td>
              <td>
                <div class="csc-act-text">{{ app.csc_action }}</div>
                <div class="resi-sub">{{ formatDate(app.csc_attestation_date) }}</div>
              </td>
              <td>
                <div v-if="app.vice_personnel">
                  <div class="vice-name">Vice: {{ app.vice_personnel }}</div>
                  <div class="vice-reason">({{ app.vice_reason || 'Transferred/Retired' }})</div>
                </div>
                <span v-else class="text-muted-dash">—</span>
              </td>
              <td>
                <div v-if="app.document_file" class="file-chip">
                  <a :href="app.document_file" target="_blank" class="btn-doc-link" title="Open Appointment File">
                    📎 {{ app.file_name || 'CS Form 33' }}
                  </a>
                </div>
                <span v-else class="no-file-tag">No scan</span>
              </td>
              <td>
                <div class="btn-group-actions">
                  <button
                    v-if="authStore.canManageAll"
                    @click="openEditAppointmentModal(app)"
                    class="btn-icon"
                    title="Edit Appointment"
                  >
                    ✏️
                  </button>
                  <button
                    v-if="authStore.canManageAll"
                    @click="deleteAppointmentRecord(app.id)"
                    class="btn-icon danger"
                    title="Delete Appointment"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 5: 3-YEAR STEP PROGRESSION MATRIX                                     -->
    <!-- ========================================================================= -->
    <div v-if="activeTab === 'eligibility'" class="tab-panel glass-panel">
      <div class="panel-header">
        <div>
          <h3>Teacher 3-Year Continuous Service & Step Forecasting</h3>
          <p class="panel-desc">
            Evaluates tenure and determines entitlement date, upcoming milestones, and projected differential increase.
          </p>
        </div>
      </div>

      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>Teacher</th>
              <th>Position / SG</th>
              <th>Current Step</th>
              <th>Last Step Date</th>
              <th>Next Step Due</th>
              <th>Remaining Days</th>
              <th>Projected Step & Differential</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in eligibilityList" :key="item.teacher_id">
              <td>
                <strong>{{ item.teacher_name }}</strong>
                <div class="teacher-sub">{{ item.department }}</div>
              </td>
              <td>{{ item.position }} (SG {{ item.current_salary_grade }})</td>
              <td>
                <span class="step-badge current">Step {{ item.current_step }}</span>
                <div class="salary-sub">₱{{ formatMoney(item.current_monthly_salary) }}</div>
              </td>
              <td>{{ formatDate(item.last_step_date) }}</td>
              <td>
                <strong>{{ formatDate(item.next_step_date) }}</strong>
              </td>
              <td>
                <span :class="['days-pill', getDaysClass(item.days_until_due)]">
                  {{ formatDaysRemaining(item.days_until_due) }}
                </span>
              </td>
              <td>
                <div><strong>Step {{ item.next_step }}</strong> (₱{{ formatMoney(item.next_monthly_salary) }})</div>
                <div class="differential-sub">+₱{{ formatMoney(item.monthly_differential) }}/mo diff</div>
              </td>
              <td>
                <span v-if="item.is_max_step" class="status-pill info">Max Step (8)</span>
                <span v-else-if="item.is_due" class="status-pill danger">Due for Step Increment</span>
                <span v-else-if="item.is_upcoming_90_days" class="status-pill warning">Approaching (90d)</span>
                <span v-else class="status-pill in_progress">Accumulating Service</span>
              </td>
              <td>
                <button
                  v-if="authStore.canManageAll && !item.is_max_step"
                  @click="prepareNosiFromEligibility(item)"
                  class="btn-action-sm"
                >
                  Prepare NOSI
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- TAB 6: DEPED SALARY STANDARDIZATION SCALE                                 -->
    <!-- ========================================================================= -->
    <div v-if="activeTab === 'salary_table'" class="tab-panel glass-panel">
      <div class="panel-header">
        <div>
          <h3>Department of Education Salary Scale Matrix (Steps 1 to 8)</h3>
          <p class="panel-desc">
            Reference table for Salary Grades 11 through 24 based on the latest Salary Standardization Law tranches.
          </p>
        </div>
      </div>

      <div class="table-responsive">
        <table class="data-table salary-matrix">
          <thead>
            <tr>
              <th>Salary Grade / Position Designation</th>
              <th>Step 1</th>
              <th>Step 2</th>
              <th>Step 3</th>
              <th>Step 4</th>
              <th>Step 5</th>
              <th>Step 6</th>
              <th>Step 7</th>
              <th>Step 8</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in salaryMatrixRows" :key="row.sg">
              <td>
                <strong>SG {{ row.sg }}</strong>
                <span v-if="row.hint" class="sg-hint">({{ row.hint }})</span>
              </td>
              <td v-for="s in [1,2,3,4,5,6,7,8]" :key="s">
                ₱{{ formatMoney(row.steps[s] || 0) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- MODAL 1: SERVICE RECORD ENTRY (ADD / EDIT)                                -->
    <!-- ========================================================================= -->
    <div v-if="showServiceRecordModal" class="modal-overlay" @click.self="showServiceRecordModal = false">
      <div class="modal-card glass-panel modal-lg">
        <div class="modal-header">
          <div>
            <h3>{{ editingServiceRecord?.id ? 'Edit Service Record Entry' : 'Add New Service Record Entry' }}</h3>
            <p class="modal-sub">CSC Form No. 122 — Record of Employment History</p>
          </div>
          <button @click="showServiceRecordModal = false" class="btn-close">×</button>
        </div>

        <form @submit.prevent="saveServiceRecord" class="modal-form">
          <div class="form-row">
            <div class="form-group col-12">
              <label>Teacher Faculty Member *</label>
              <select v-model="serviceRecordForm.teacher" required :disabled="editingServiceRecord?.id || !authStore.canManageAll">
                <option value="" disabled>Select Teacher...</option>
                <option v-for="t in teachersList" :key="t.id" :value="t.id">
                  {{ t.user?.last_name }}, {{ t.user?.first_name }} — {{ t.position || 'Teacher' }} ({{ t.employee_id || 'No ID' }})
                </option>
                <option v-if="!authStore.canManageAll && authStore.user?.teacher_id" :value="authStore.user.teacher_id">
                  {{ authStore.fullName }} (My Record)
                </option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-4">
              <label>From Date *</label>
              <input v-model="serviceRecordForm.from_date" type="date" required />
            </div>
            <div class="form-group col-4">
              <label>To Date (Leave blank if Present)</label>
              <input v-model="serviceRecordForm.to_date" type="date" :disabled="serviceRecordForm.to_present" />
            </div>
            <div class="form-group col-4 chk-col">
              <label class="form-chk-label" style="margin-top: 1.8rem;">
                <input type="checkbox" v-model="serviceRecordForm.to_present" @change="onToPresentToggle" /> Currently in this position (To Present)
              </label>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Designation / Rank *</label>
              <input
                v-model="serviceRecordForm.designation"
                required
                placeholder="e.g. Teacher I, Teacher II, Master Teacher I"
                list="designation-suggestions"
              />
              <datalist id="designation-suggestions">
                <option value="Teacher I" />
                <option value="Teacher II" />
                <option value="Teacher III" />
                <option value="Special Education Teacher I" />
                <option value="Master Teacher I" />
                <option value="Master Teacher II" />
                <option value="Head Teacher I" />
                <option value="Head Teacher III" />
                <option value="School Principal I" />
                <option value="School Principal II" />
              </datalist>
            </div>
            <div class="form-group col-6">
              <label>Status of Appointment *</label>
              <select v-model="serviceRecordForm.status_of_appointment" required>
                <option value="Permanent">Permanent</option>
                <option value="Provisional">Provisional</option>
                <option value="Temporary">Temporary</option>
                <option value="Substitute">Substitute</option>
                <option value="Contractual">Contractual</option>
                <option value="Casual">Casual</option>
                <option value="Coterminous">Coterminous</option>
                <option value="Job Order">Job Order</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-3">
              <label>Salary Grade</label>
              <input v-model.number="serviceRecordForm.salary_grade" type="number" min="1" max="33" />
            </div>
            <div class="form-group col-3">
              <label>Step</label>
              <input v-model.number="serviceRecordForm.step" type="number" min="1" max="8" />
            </div>
            <div class="form-group col-3">
              <label>Monthly Salary (₱)</label>
              <input
                v-model.number="serviceRecordForm.monthly_salary"
                type="number"
                step="0.01"
                @input="onMonthlySalaryInput"
              />
            </div>
            <div class="form-group col-3">
              <label>Annual Salary (₱)</label>
              <input
                v-model.number="serviceRecordForm.annual_salary"
                type="number"
                step="0.01"
                @input="onAnnualSalaryInput"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Station / Place of Assignment</label>
              <input v-model="serviceRecordForm.station_office" placeholder="e.g. Naguilian Elementary School / DepEd Isabela" />
            </div>
            <div class="form-group col-6">
              <label>Branch</label>
              <select v-model="serviceRecordForm.branch">
                <option value="National">National</option>
                <option value="Provincial">Provincial</option>
                <option value="Municipal/City (LGU)">Municipal/City (LGU)</option>
                <option value="Private">Private</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-4">
              <label>Leave Without Pay (LWOP)</label>
              <input v-model="serviceRecordForm.lwop_dates" placeholder="e.g. NONE or 05/01/2023 - 05/15/2023" />
            </div>
            <div class="form-group col-4">
              <label>Separation Date</label>
              <input v-model="serviceRecordForm.separation_date" type="date" />
            </div>
            <div class="form-group col-4">
              <label>Separation Cause</label>
              <input v-model="serviceRecordForm.separation_cause" placeholder="e.g. Promotion, Transfer, Resigned" />
            </div>
          </div>

          <div class="form-group">
            <label>Remarks</label>
            <input v-model="serviceRecordForm.remarks" placeholder="e.g. Original Appointment, Step Increment, SSL Tranche Adjustment" />
          </div>

          <!-- Upload Scanned Service Record File -->
          <div class="form-group upload-field-box">
            <label>Scanned Service Record Document (PDF / Image)</label>
            <div class="file-picker-row">
              <input
                type="file"
                ref="serviceRecordFileInput"
                @change="handleServiceRecordFileSelect"
                accept=".pdf,.png,.jpg,.jpeg"
              />
              <span v-if="editingServiceRecord?.file_name && !selectedServiceRecordFile" class="existing-file-hint">
                Current file: <a :href="editingServiceRecord.document_file" target="_blank">{{ editingServiceRecord.file_name }}</a>
              </span>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" @click="showServiceRecordModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-save" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : 'Save Service Record' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- MODAL 2: NOSI (STEP INCREMENT)                                            -->
    <!-- ========================================================================= -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-card glass-panel modal-lg">
        <div class="modal-header">
          <div>
            <h3>{{ editingRecord ? 'Edit Notice of Step Increment' : 'Prepare New DepEd NOSI' }}</h3>
            <p class="modal-sub">CSC-DBM Joint Circular No. 1, s. 2012</p>
          </div>
          <button @click="showModal = false" class="btn-close">×</button>
        </div>

        <form @submit.prevent="saveNosiRecord" class="modal-form">
          <div class="form-row">
            <div class="form-group col-6">
              <label>Teacher *</label>
              <select v-model="formData.teacher" required :disabled="editingRecord?.id">
                <option value="" disabled>Select Teacher...</option>
                <option v-for="t in teachersList" :key="t.id" :value="t.id">
                  {{ t.user?.last_name }}, {{ t.user?.first_name }} — {{ t.position || 'Teacher' }}
                </option>
              </select>
            </div>
            <div class="form-group col-6">
              <label>NOSI Reference Number</label>
              <input v-model="formData.nosi_number" placeholder="e.g. NOSI-2026-SDO-001" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Date Issued</label>
              <input v-model="formData.date_issued" type="date" />
            </div>
            <div class="form-group col-6">
              <label>Effective Date *</label>
              <input v-model="formData.effective_date" type="date" required />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-3">
              <label>Previous SG</label>
              <input v-model.number="formData.previous_salary_grade" type="number" min="1" max="33" />
            </div>
            <div class="form-group col-3">
              <label>Previous Step</label>
              <input v-model.number="formData.previous_step" type="number" min="1" max="8" />
            </div>
            <div class="form-group col-3">
              <label>New SG</label>
              <input v-model.number="formData.new_salary_grade" type="number" min="1" max="33" />
            </div>
            <div class="form-group col-3">
              <label>New Step</label>
              <input v-model.number="formData.new_step" type="number" min="1" max="8" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Previous Monthly Salary (₱)</label>
              <input v-model.number="formData.previous_monthly_salary" type="number" step="0.01" />
            </div>
            <div class="form-group col-6">
              <label>New Monthly Salary (₱)</label>
              <input v-model.number="formData.new_monthly_salary" type="number" step="0.01" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Division Office</label>
              <input v-model="formData.division_office" placeholder="e.g. Schools Division Office of Isabela" />
            </div>
            <div class="form-group col-6">
              <label>School Name</label>
              <input v-model="formData.school_name" placeholder="e.g. Naguilian Elementary School" />
            </div>
          </div>

          <div class="form-group">
            <label>Schools Division Superintendent</label>
            <input v-model="formData.schools_division_superintendent" placeholder="e.g. MADELYN L. MACALLING, PhD, CESO VI" />
          </div>

          <!-- Requirements Checklist -->
          <div class="checklist-box">
            <h4>Checklist: Key Requirements for Processing</h4>
            <label class="form-chk-label">
              <input type="checkbox" v-model="formData.has_approved_nosi" /> Approved NOSI
            </label>
            <label class="form-chk-label">
              <input type="checkbox" v-model="formData.has_annex_d" /> Annex D / Relevant forms
            </label>
            <label class="form-chk-label">
              <input type="checkbox" v-model="formData.has_payslips" /> Payslips (before and after)
            </label>
            <label class="form-chk-label">
              <input type="checkbox" v-model="formData.has_latest_appointment" /> Latest Appointment
            </label>
            <label class="form-chk-label">
              <input type="checkbox" v-model="formData.has_updated_service_record" /> Updated Service Record
            </label>
          </div>

          <!-- Direct Scanned NOSI File Upload -->
          <div class="form-group upload-field-box">
            <label>Direct Upload: Approved NOSI Scan (PDF / Image)</label>
            <div class="file-picker-row">
              <input
                type="file"
                ref="nosiDirectFileInput"
                @change="handleNosiDirectFileSelect"
                accept=".pdf,.png,.jpg,.jpeg"
              />
              <span v-if="editingRecord?.file_name && !selectedNosiDirectFile" class="existing-file-hint">
                Current file: <a :href="editingRecord.document_file" target="_blank">{{ editingRecord.file_name }}</a>
              </span>
            </div>
          </div>

          <div class="form-group" style="margin-top: 1rem;">
            <label>Status</label>
            <select v-model="formData.status">
              <option value="ELIGIBLE_PENDING">Eligible / For Processing</option>
              <option value="DOCS_INCOMPLETE">Incomplete Requirements</option>
              <option value="DOCS_VERIFIED">Requirements Complete & Verified</option>
              <option value="NOSI_GENERATED">NOSI Prepared & Generated</option>
              <option value="APPROVED">Approved by SDS / Appointing Authority</option>
              <option value="INTEGRATED_PAYROLL">Integrated into Payroll / Differential Paid</option>
            </select>
          </div>

          <div class="form-group">
            <label>Remarks</label>
            <textarea v-model="formData.remarks" rows="2" placeholder="Processing remarks, notes for payroll..."></textarea>
          </div>

          <div class="modal-footer">
            <button type="button" @click="showModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-save" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : 'Save NOSI Record' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- MODAL 3: NOSA (NOTICE OF SALARY ADJUSTMENT)                                -->
    <!-- ========================================================================= -->
    <div v-if="showNosaModal" class="modal-overlay" @click.self="showNosaModal = false">
      <div class="modal-card glass-panel modal-lg">
        <div class="modal-header">
          <div>
            <h3>{{ editingNosa?.id ? 'Edit Notice of Salary Adjustment' : 'Record New NOSA' }}</h3>
            <p class="modal-sub">Salary Standardization Law (SSL) & NBC Salary Adjustments</p>
          </div>
          <button @click="showNosaModal = false" class="btn-close">×</button>
        </div>

        <form @submit.prevent="saveNosaRecord" class="modal-form">
          <div class="form-row">
            <div class="form-group col-6">
              <label>Teacher *</label>
              <select v-model="nosaForm.teacher" required :disabled="editingNosa?.id">
                <option value="" disabled>Select Teacher...</option>
                <option v-for="t in teachersList" :key="t.id" :value="t.id">
                  {{ t.user?.last_name }}, {{ t.user?.first_name }} — {{ t.position || 'Teacher' }}
                </option>
              </select>
            </div>
            <div class="form-group col-6">
              <label>NOSA Reference Number</label>
              <input v-model="nosaForm.nosa_number" placeholder="e.g. NOSA-2024-SDO-045" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Date Issued</label>
              <input v-model="nosaForm.date_issued" type="date" />
            </div>
            <div class="form-group col-6">
              <label>Effective Date *</label>
              <input v-model="nosaForm.effective_date" type="date" required />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Legal Basis / Authority *</label>
              <input v-model="nosaForm.legal_basis" required placeholder="e.g. Executive Order No. 64, s. 2024 / NBC No. 594" />
            </div>
            <div class="form-group col-6">
              <label>Position Title</label>
              <input v-model="nosaForm.position_title" placeholder="e.g. Teacher I, Teacher II" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Salary Grade</label>
              <input v-model.number="nosaForm.salary_grade" type="number" min="1" max="33" />
            </div>
            <div class="form-group col-6">
              <label>Step</label>
              <input v-model.number="nosaForm.step" type="number" min="1" max="8" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Previous Monthly Salary (₱)</label>
              <input v-model.number="nosaForm.previous_monthly_salary" type="number" step="0.01" />
            </div>
            <div class="form-group col-6">
              <label>Adjusted Monthly Salary (₱) *</label>
              <input v-model.number="nosaForm.adjusted_monthly_salary" type="number" step="0.01" required />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Status</label>
              <select v-model="nosaForm.status">
                <option value="DRAFT">Draft</option>
                <option value="ISSUED">Issued</option>
                <option value="APPROVED">Approved by SDS</option>
                <option value="INTEGRATED_PAYROLL">Integrated into Payroll / Differential Paid</option>
              </select>
            </div>
            <div class="form-group col-6">
              <label>Signatory Authority</label>
              <input v-model="nosaForm.signatory_authority" placeholder="e.g. Schools Division Superintendent" />
            </div>
          </div>

          <div class="form-group">
            <label>Remarks</label>
            <input v-model="nosaForm.remarks" placeholder="Implementation remarks, payroll differential tracking..." />
          </div>

          <!-- Scanned NOSA Upload -->
          <div class="form-group upload-field-box">
            <label>Upload Signed NOSA Document (PDF / Image)</label>
            <div class="file-picker-row">
              <input
                type="file"
                ref="nosaFileInput"
                @change="handleNosaFileSelect"
                accept=".pdf,.png,.jpg,.jpeg"
              />
              <span v-if="editingNosa?.file_name && !selectedNosaFile" class="existing-file-hint">
                Current file: <a :href="editingNosa.document_file" target="_blank">{{ editingNosa.file_name }}</a>
              </span>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" @click="showNosaModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-save" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : 'Save NOSA Record' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- MODAL 4: APPOINTMENT RECORD (ADD / EDIT)                                  -->
    <!-- ========================================================================= -->
    <div v-if="showAppointmentModal" class="modal-overlay" @click.self="showAppointmentModal = false">
      <div class="modal-card glass-panel modal-lg">
        <div class="modal-header">
          <div>
            <h3>{{ editingAppointment?.id ? 'Edit Plantilla Appointment' : 'Record Plantilla Appointment' }}</h3>
            <p class="modal-sub">Civil Service Commission Form No. 33 / KSS Pormularyo Blg. 33</p>
          </div>
          <button @click="showAppointmentModal = false" class="btn-close">×</button>
        </div>

        <form @submit.prevent="saveAppointmentRecord" class="modal-form">
          <div class="form-row">
            <div class="form-group col-6">
              <label>Teacher *</label>
              <select v-model="appointmentForm.teacher" required :disabled="editingAppointment?.id">
                <option value="" disabled>Select Teacher...</option>
                <option v-for="t in teachersList" :key="t.id" :value="t.id">
                  {{ t.user?.last_name }}, {{ t.user?.first_name }} — {{ t.position || 'Teacher' }}
                </option>
              </select>
            </div>
            <div class="form-group col-6">
              <label>Appointment Number / Reference</label>
              <input v-model="appointmentForm.appointment_number" placeholder="e.g. APPT-2023-018" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Position Title *</label>
              <input v-model="appointmentForm.position_title" required placeholder="e.g. Teacher I, Teacher II, Master Teacher I" />
            </div>
            <div class="form-group col-6">
              <label>Plantilla Item Number (PSI-POP) *</label>
              <input v-model="appointmentForm.plantilla_item_no" required placeholder="e.g. TCH1-123456-2020" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Nature of Appointment *</label>
              <select v-model="appointmentForm.nature_of_appointment" required>
                <option value="Original">Original</option>
                <option value="Promotion">Promotion</option>
                <option value="Transfer">Transfer</option>
                <option value="Reemployment">Reemployment</option>
                <option value="Reappointment">Reappointment</option>
                <option value="Reclassification">Reclassification</option>
                <option value="Demotion">Demotion</option>
              </select>
            </div>
            <div class="form-group col-6">
              <label>Status of Appointment *</label>
              <select v-model="appointmentForm.status_of_appointment" required>
                <option value="Permanent">Permanent</option>
                <option value="Provisional">Provisional</option>
                <option value="Temporary">Temporary</option>
                <option value="Substitute">Substitute</option>
                <option value="Contractual">Contractual</option>
                <option value="Coterminous">Coterminous</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-3">
              <label>Salary Grade</label>
              <input v-model.number="appointmentForm.salary_grade" type="number" min="1" max="33" />
            </div>
            <div class="form-group col-3">
              <label>Step</label>
              <input v-model.number="appointmentForm.step" type="number" min="1" max="8" />
            </div>
            <div class="form-group col-3">
              <label>Monthly Rate (₱)</label>
              <input v-model.number="appointmentForm.monthly_rate" type="number" step="0.01" />
            </div>
            <div class="form-group col-3">
              <label>Annual Rate (₱)</label>
              <input v-model.number="appointmentForm.annual_rate" type="number" step="0.01" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-4">
              <label>Date of Signing (Appointing Officer)</label>
              <input v-model="appointmentForm.date_of_signing" type="date" />
            </div>
            <div class="form-group col-4">
              <label>Date of Assumption (Duty)</label>
              <input v-model="appointmentForm.date_of_assumption" type="date" />
            </div>
            <div class="form-group col-4">
              <label>CSC Attestation Date</label>
              <input v-model="appointmentForm.csc_attestation_date" type="date" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label>Vice (Former Incumbent)</label>
              <input v-model="appointmentForm.vice_personnel" placeholder="Former incumbent name or 'Newly Created Item'" />
            </div>
            <div class="form-group col-6">
              <label>Reason for Vacancy</label>
              <select v-model="appointmentForm.vice_reason">
                <option value="">Select or N/A</option>
                <option value="Newly Created">Newly Created Item</option>
                <option value="Promoted">Promoted</option>
                <option value="Transferred">Transferred</option>
                <option value="Retired">Retired</option>
                <option value="Resigned">Resigned</option>
                <option value="Deceased">Deceased</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Remarks</label>
            <input v-model="appointmentForm.remarks" placeholder="Page in plantilla, remarks..." />
          </div>

          <!-- Scanned Appointment Upload -->
          <div class="form-group upload-field-box">
            <label>Upload Scanned CS Form 33 / KSS Appointment (PDF / Image)</label>
            <div class="file-picker-row">
              <input
                type="file"
                ref="appointmentFileInput"
                @change="handleAppointmentFileSelect"
                accept=".pdf,.png,.jpg,.jpeg"
              />
              <span v-if="editingAppointment?.file_name && !selectedAppointmentFile" class="existing-file-hint">
                Current file: <a :href="editingAppointment.document_file" target="_blank">{{ editingAppointment.file_name }}</a>
              </span>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" @click="showAppointmentModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-save" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : 'Save Appointment' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- MODAL 5: DOCUMENT UPLOAD & VERIFICATION FOR NOSI (SUPPORTING PACK)        -->
    <!-- ========================================================================= -->
    <div v-if="showDocModal" class="modal-overlay" @click.self="showDocModal = false">
      <div class="modal-card doc-modal glass-panel">
        <div class="modal-header">
          <div>
            <h3>Processing Requirements & Document Attachments</h3>
            <p class="modal-sub">
              NOSI Ref: {{ activeRecordForDocs?.nosi_number }} • {{ activeRecordForDocs?.teacher_name }}
            </p>
          </div>
          <button @click="showDocModal = false" class="btn-close">×</button>
        </div>

        <div class="modal-body">
          <!-- Upload Form -->
          <div class="upload-box">
            <h4>Upload Supporting Claim Document</h4>
            <div class="upload-row">
              <select v-model="uploadDocType" class="select-doc-type">
                <option value="APPROVED_NOSI">Approved NOSI</option>
                <option value="ANNEX_D">Annex D / Relevant Forms</option>
                <option value="PAYSLIP">Payslip / Payroll Records (Before & After)</option>
                <option value="LATEST_APPOINTMENT">Latest Appointment</option>
                <option value="SERVICE_RECORD">Updated Service Record</option>
                <option value="OTHER">Other Supporting Document</option>
              </select>
              <input type="text" v-model="uploadDocTitle" placeholder="Document title or description" class="input-doc-title" />
              <input type="file" ref="fileInput" @change="handleFileSelect" class="input-file" accept=".pdf,.png,.jpg,.jpeg" />
              <button @click="submitFileUpload" class="btn-upload" :disabled="isUploading || !selectedFile">
                {{ isUploading ? 'Uploading...' : 'Upload' }}
              </button>
            </div>
          </div>

          <!-- Existing Attached Documents -->
          <div class="attached-docs-section">
            <h4>Uploaded Document Files ({{ activeRecordForDocs?.documents?.length || 0 }})</h4>
            <div v-if="!activeRecordForDocs?.documents?.length" class="empty-docs">
              No files uploaded yet for this step increment claim.
            </div>
            <div v-else class="doc-list">
              <div v-for="doc in activeRecordForDocs.documents" :key="doc.id" class="doc-item">
                <div class="doc-meta">
                  <span class="doc-badge">{{ doc.doc_type_display }}</span>
                  <strong class="doc-title">{{ doc.title || doc.file_name }}</strong>
                  <span class="doc-date">{{ formatDate(doc.uploaded_at) }}</span>
                </div>
                <div class="doc-actions">
                  <a :href="doc.file" target="_blank" class="btn-download-file">Open File ↗</a>
                  <button
                    v-if="authStore.canManageAll"
                    @click="deleteDocument(doc.id)"
                    class="btn-delete-doc"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const authStore = useAuthStore()

// Navigation & Active Scoping
const activeTab = ref('service_records')
const selectedTeacherId = ref('')

// Core Data Collections
const records = ref([])
const serviceRecords = ref([])
const nosaRecords = ref([])
const appointmentRecords = ref([])
const eligibilityList = ref([])
const alerts = ref([])
const salarySchedules = ref([])
const teachersList = ref([])

// Loading states
const loadingRecords = ref(false)
const loadingServiceRecords = ref(false)
const loadingNosa = ref(false)
const loadingAppointments = ref(false)
const isScanning = ref(false)
const isSaving = ref(false)
const isUploading = ref(false)

// Search filters
const recordSearch = ref('')
const serviceRecordSearch = ref('')
const nosaSearch = ref('')
const appointmentSearch = ref('')

// Modals Visibility
const showModal = ref(false)
const editingRecord = ref(null)
const showServiceRecordModal = ref(false)
const editingServiceRecord = ref(null)
const showNosaModal = ref(false)
const editingNosa = ref(null)
const showAppointmentModal = ref(false)
const editingAppointment = ref(null)
const showDocModal = ref(false)
const activeRecordForDocs = ref(null)

// File Input References & State
const fileInput = ref(null)
const selectedFile = ref(null)
const uploadDocType = ref('APPROVED_NOSI')
const uploadDocTitle = ref('')

const serviceRecordFileInput = ref(null)
const selectedServiceRecordFile = ref(null)

const nosiDirectFileInput = ref(null)
const selectedNosiDirectFile = ref(null)

const nosaFileInput = ref(null)
const selectedNosaFile = ref(null)

const appointmentFileInput = ref(null)
const selectedAppointmentFile = ref(null)

// Form Data: NOSI Record
const formData = ref({
  teacher: '',
  nosi_number: '',
  date_issued: '',
  effective_date: '',
  previous_salary_grade: 11,
  previous_step: 1,
  previous_monthly_salary: 27000,
  new_salary_grade: 11,
  new_step: 2,
  new_monthly_salary: 27284,
  division_office: 'Schools Division Office of Isabela',
  school_name: 'Naguilian Elementary School',
  schools_division_superintendent: 'MADELYN L. MACALLING, PhD, CESO VI',
  has_approved_nosi: false,
  has_annex_d: false,
  has_payslips: false,
  has_latest_appointment: false,
  has_updated_service_record: false,
  status: 'ELIGIBLE_PENDING',
  remarks: ''
})

// Form Data: Service Record Entry
const serviceRecordForm = ref({
  teacher: '',
  from_date: '',
  to_date: '',
  to_present: false,
  designation: 'Teacher I',
  status_of_appointment: 'Permanent',
  salary_grade: 11,
  step: 1,
  monthly_salary: 27000,
  annual_salary: 324000,
  station_office: 'Naguilian Elementary School / DepEd Isabela',
  branch: 'National',
  lwop_dates: 'NONE',
  separation_date: '',
  separation_cause: '',
  remarks: 'Original Appointment'
})

// Form Data: NOSA Record
const nosaForm = ref({
  teacher: '',
  nosa_number: '',
  date_issued: '',
  effective_date: '',
  legal_basis: 'Executive Order No. 64, s. 2024 / NBC No. 594',
  position_title: 'Teacher I',
  salary_grade: 11,
  step: 1,
  previous_monthly_salary: 27000,
  adjusted_monthly_salary: 28000,
  status: 'ISSUED',
  signatory_authority: 'MADELYN L. MACALLING, PhD, CESO VI',
  remarks: ''
})

// Form Data: Appointment Record
const appointmentForm = ref({
  teacher: '',
  appointment_number: '',
  position_title: 'Teacher I',
  plantilla_item_no: 'TCH1-120045-2020',
  nature_of_appointment: 'Original',
  status_of_appointment: 'Permanent',
  salary_grade: 11,
  step: 1,
  monthly_rate: 27000,
  annual_rate: 324000,
  date_of_signing: '',
  date_of_assumption: '',
  csc_attestation_date: '',
  csc_action: 'Approved / Validated',
  vice_personnel: '',
  vice_reason: '',
  remarks: ''
})

// Computed Properties
const selectedTeacherSummary = computed(() => {
  if (!selectedTeacherId.value) return null
  return teachersList.value.find(t => t.id === Number(selectedTeacherId.value)) || null
})

const unreadAlertsCount = computed(() => {
  return alerts.value.filter(a => !a.is_read).length
})

const upcomingCount = computed(() => {
  return eligibilityList.value.filter(e => e.is_due || e.is_upcoming_90_days).length
})

const filteredRecords = computed(() => {
  let list = records.value
  if (selectedTeacherId.value) {
    list = list.filter(r => r.teacher === Number(selectedTeacherId.value))
  }
  if (!recordSearch.value) return list
  const query = recordSearch.value.toLowerCase()
  return list.filter(r => 
    (r.nosi_number && r.nosi_number.toLowerCase().includes(query)) ||
    (r.teacher_name && r.teacher_name.toLowerCase().includes(query)) ||
    (r.teacher_position && r.teacher_position.toLowerCase().includes(query))
  )
})

const filteredServiceRecords = computed(() => {
  let list = serviceRecords.value
  if (selectedTeacherId.value) {
    list = list.filter(r => r.teacher === Number(selectedTeacherId.value))
  }
  if (!serviceRecordSearch.value) return list
  const q = serviceRecordSearch.value.toLowerCase()
  return list.filter(r =>
    (r.designation && r.designation.toLowerCase().includes(q)) ||
    (r.station_office && r.station_office.toLowerCase().includes(q)) ||
    (r.teacher_name && r.teacher_name.toLowerCase().includes(q)) ||
    (r.remarks && r.remarks.toLowerCase().includes(q))
  )
})

// Drill-Down Master-Detail State for Service Records
const expandedTeachers = ref(new Set())

const isExpanded = (teacherId) => {
  return expandedTeachers.value.has(teacherId)
}

const toggleDrillDown = (teacherId) => {
  if (expandedTeachers.value.has(teacherId)) {
    expandedTeachers.value.delete(teacherId)
  } else {
    expandedTeachers.value.add(teacherId)
  }
}

const expandAllTeachers = () => {
  teacherServiceRecordSummaries.value.forEach(t => expandedTeachers.value.add(t.teacherId))
}

const collapseAllTeachers = () => {
  expandedTeachers.value.clear()
}

const teacherServiceRecordSummaries = computed(() => {
  const teacherMap = new Map()

  // 1. Initialize teachers from teachersList
  teachersList.value.forEach(t => {
    const fullName = t.user ? `${t.user.last_name || ''}, ${t.user.first_name || ''}`.trim() : (t.position || `Teacher ${t.id}`)
    const init = ((t.user?.first_name?.[0] || 'T') + (t.user?.last_name?.[0] || '')).toUpperCase()
    teacherMap.set(t.id, {
      teacherId: t.id,
      teacherName: fullName || `Teacher ${t.id}`,
      initials: init,
      employeeId: t.employee_id || '',
      currentPosition: t.position || 'Teacher',
      department: t.department || 'Department of Education',
      records: [],
      documentsCount: 0,
      currentMonthlySalary: 0,
      currentSG: null,
      currentStep: 1,
      currentStatus: 'Permanent',
      serviceSpan: 'No records'
    })
  })

  // 2. Also ensure current logged in teacher is present if not in teachersList
  if (!authStore.canManageAll && authStore.user?.teacher_id) {
    const tid = authStore.user.teacher_id
    if (!teacherMap.has(tid)) {
      const init = ((authStore.user.first_name?.[0] || 'T') + (authStore.user.last_name?.[0] || '')).toUpperCase()
      teacherMap.set(tid, {
        teacherId: tid,
        teacherName: authStore.fullName,
        initials: init,
        employeeId: authStore.user.employee_id || '',
        currentPosition: authStore.user.position || 'Teacher',
        department: authStore.user.department || 'Department of Education',
        records: [],
        documentsCount: 0,
        currentMonthlySalary: 0,
        currentSG: null,
        currentStep: 1,
        currentStatus: 'Permanent',
        serviceSpan: 'No records'
      })
    }
  }

  // 3. Populate from serviceRecords
  serviceRecords.value.forEach(sr => {
    const tid = sr.teacher
    if (!teacherMap.has(tid)) {
      const parts = (sr.teacher_name || `Teacher ${tid}`).replace(',', '').split(' ').filter(Boolean)
      const init = ((parts[0]?.[0] || 'T') + (parts[1]?.[0] || '')).toUpperCase()
      teacherMap.set(tid, {
        teacherId: tid,
        teacherName: sr.teacher_name || `Teacher ${tid}`,
        initials: init,
        employeeId: sr.teacher_employee_id || '',
        currentPosition: sr.teacher_position || sr.designation || 'Teacher',
        department: 'Department of Education',
        records: [],
        documentsCount: 0,
        currentMonthlySalary: 0,
        currentSG: null,
        currentStep: 1,
        currentStatus: 'Permanent',
        serviceSpan: 'No records'
      })
    }
    const tObj = teacherMap.get(tid)
    tObj.records.push(sr)
    if (sr.document_file) {
      tObj.documentsCount++
    }
  })

  // 4. Sort each teacher's records and compute summary metadata
  const summaries = Array.from(teacherMap.values()).map(t => {
    // Sort records chronologically (newest first for display)
    t.records.sort((a, b) => new Date(b.from_date || 0) - new Date(a.from_date || 0))

    if (t.records.length > 0) {
      const activeOrLatest = t.records.find(r => r.to_present) || t.records[0]
      t.currentPosition = activeOrLatest.designation || t.currentPosition
      t.currentStatus = activeOrLatest.status_of_appointment || t.currentStatus
      t.currentMonthlySalary = activeOrLatest.monthly_salary || 0
      t.currentSG = activeOrLatest.salary_grade
      t.currentStep = activeOrLatest.step || 1

      // Compute service span
      const oldest = t.records[t.records.length - 1]
      const newest = t.records[0]
      const fromStr = oldest.from_date ? new Date(oldest.from_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : '?'
      const toStr = newest.to_present ? 'Present' : (newest.to_date ? new Date(newest.to_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : '?')
      t.serviceSpan = `${fromStr} – ${toStr}`
    }

    return t
  })

  // 5. Apply selectedTeacherId filter if user selected a single teacher from dropdown
  let result = summaries
  if (selectedTeacherId.value) {
    result = result.filter(t => t.teacherId === Number(selectedTeacherId.value))
  }

  // 6. Apply serviceRecordSearch query
  if (serviceRecordSearch.value) {
    const q = serviceRecordSearch.value.toLowerCase()
    result = result.filter(t => {
      const matchTeacher = (
        t.teacherName.toLowerCase().includes(q) ||
        t.employeeId.toLowerCase().includes(q) ||
        t.currentPosition.toLowerCase().includes(q) ||
        t.department.toLowerCase().includes(q)
      )
      const matchRecords = t.records.some(r => 
        (r.designation && r.designation.toLowerCase().includes(q)) ||
        (r.station_office && r.station_office.toLowerCase().includes(q)) ||
        (r.remarks && r.remarks.toLowerCase().includes(q))
      )
      return matchTeacher || matchRecords
    })
  }

  return result
})

// Auto-expand all teachers by default when records load so user sees full history immediately
watch(
  () => teacherServiceRecordSummaries.value,
  (list) => {
    if (list.length > 0 && expandedTeachers.value.size === 0) {
      list.forEach(t => expandedTeachers.value.add(t.teacherId))
    }
  },
  { immediate: true }
)


const filteredNosaRecords = computed(() => {
  let list = nosaRecords.value
  if (selectedTeacherId.value) {
    list = list.filter(r => r.teacher === Number(selectedTeacherId.value))
  }
  if (!nosaSearch.value) return list
  const q = nosaSearch.value.toLowerCase()
  return list.filter(r =>
    (r.nosa_number && r.nosa_number.toLowerCase().includes(q)) ||
    (r.teacher_name && r.teacher_name.toLowerCase().includes(q)) ||
    (r.legal_basis && r.legal_basis.toLowerCase().includes(q)) ||
    (r.position_title && r.position_title.toLowerCase().includes(q))
  )
})

const filteredAppointmentRecords = computed(() => {
  let list = appointmentRecords.value
  if (selectedTeacherId.value) {
    list = list.filter(r => r.teacher === Number(selectedTeacherId.value))
  }
  if (!appointmentSearch.value) return list
  const q = appointmentSearch.value.toLowerCase()
  return list.filter(r =>
    (r.plantilla_item_no && r.plantilla_item_no.toLowerCase().includes(q)) ||
    (r.appointment_number && r.appointment_number.toLowerCase().includes(q)) ||
    (r.teacher_name && r.teacher_name.toLowerCase().includes(q)) ||
    (r.position_title && r.position_title.toLowerCase().includes(q)) ||
    (r.nature_of_appointment && r.nature_of_appointment.toLowerCase().includes(q))
  )
})

const salaryMatrixRows = computed(() => {
  const map = {}
  salarySchedules.value.forEach(s => {
    if (!map[s.salary_grade]) {
      let hint = ''
      if (s.salary_grade === 11) hint = 'Teacher I'
      else if (s.salary_grade === 12) hint = 'Teacher II'
      else if (s.salary_grade === 13) hint = 'Teacher III'
      else if (s.salary_grade === 14) hint = 'SPET I'
      else if (s.salary_grade === 18) hint = 'Master Teacher I'
      else if (s.salary_grade === 19) hint = 'Master Teacher II'
      map[s.salary_grade] = { sg: s.salary_grade, hint, steps: {} }
    }
    map[s.salary_grade].steps[s.step] = s.monthly_salary
  })
  return Object.values(map).sort((a, b) => a.sg - b.sg)
})

// Methods & API Calls
const onTeacherFilterChange = () => {
  fetchRecords()
  fetchServiceRecords()
  fetchNosaRecords()
  fetchAppointmentRecords()
}

const fetchRecords = async () => {
  loadingRecords.value = true
  try {
    const params = selectedTeacherId.value ? { teacher_id: selectedTeacherId.value } : {}
    const res = await api.get('/nosi/records/', { params })
    records.value = res.data.results || res.data
  } catch (err) {
    console.error('Failed to load NOSI records:', err)
  } finally {
    loadingRecords.value = false
  }
}

const fetchServiceRecords = async () => {
  loadingServiceRecords.value = true
  try {
    const params = selectedTeacherId.value ? { teacher_id: selectedTeacherId.value } : {}
    const res = await api.get('/nosi/service-records/', { params })
    serviceRecords.value = res.data.results || res.data
  } catch (err) {
    console.error('Failed to load service records:', err)
  } finally {
    loadingServiceRecords.value = false
  }
}

const fetchNosaRecords = async () => {
  loadingNosa.value = true
  try {
    const params = selectedTeacherId.value ? { teacher_id: selectedTeacherId.value } : {}
    const res = await api.get('/nosi/nosa/', { params })
    nosaRecords.value = res.data.results || res.data
  } catch (err) {
    console.error('Failed to load NOSA records:', err)
  } finally {
    loadingNosa.value = false
  }
}

const fetchAppointmentRecords = async () => {
  loadingAppointments.value = true
  try {
    const params = selectedTeacherId.value ? { teacher_id: selectedTeacherId.value } : {}
    const res = await api.get('/nosi/appointments/', { params })
    appointmentRecords.value = res.data.results || res.data
  } catch (err) {
    console.error('Failed to load appointment records:', err)
  } finally {
    loadingAppointments.value = false
  }
}

const fetchEligibility = async () => {
  try {
    const params = selectedTeacherId.value ? { teacher_id: selectedTeacherId.value } : {}
    const res = await api.get('/nosi/eligibility/', { params })
    eligibilityList.value = res.data
  } catch (err) {
    console.error('Failed to load eligibility:', err)
  }
}

const fetchAlerts = async () => {
  try {
    const res = await api.get('/nosi/alerts/')
    alerts.value = res.data.results || res.data
  } catch (err) {
    console.error('Failed to load alerts:', err)
  }
}

const fetchSalarySchedules = async () => {
  try {
    const res = await api.get('/nosi/salary-schedules/')
    salarySchedules.value = res.data.results || res.data
  } catch (err) {
    console.error('Failed to load salary schedules:', err)
  }
}

const fetchTeachers = async () => {
  if (!authStore.canManageAll) return
  try {
    const res = await api.get('/teachers/')
    teachersList.value = res.data.results || res.data
  } catch (err) {
    console.error('Failed to load teachers:', err)
  }
}

const triggerSmartAlertScan = async () => {
  isScanning.value = true
  try {
    await api.post('/nosi/alerts/refresh/')
    await fetchAlerts()
    await fetchEligibility()
  } catch (err) {
    console.error('Failed to run smart alert engine:', err)
  } finally {
    isScanning.value = false
  }
}

const markAlertRead = async (alertId) => {
  try {
    await api.post(`/nosi/alerts/${alertId}/mark_as_read/`)
    const a = alerts.value.find(item => item.id === alertId)
    if (a) a.is_read = true
  } catch (err) {
    console.error('Failed to mark alert as read:', err)
  }
}

const markAllAlertsRead = async () => {
  try {
    await api.post('/nosi/alerts/mark_all_read/')
    alerts.value.forEach(a => a.is_read = true)
  } catch (err) {
    console.error('Failed to mark all alerts as read:', err)
  }
}

const toggleReq = async (record, field, isChecked) => {
  record[field] = isChecked
  try {
    const res = await api.post(`/nosi/records/${record.id}/update_checklist/`, {
      [field]: isChecked
    })
    Object.assign(record, res.data)
  } catch (err) {
    console.error('Failed to update requirement checklist:', err)
  }
}

// Download Handlers
const downloadNosiDoc = (record) => {
  window.open(`/api/nosi/records/${record.id}/download_nosi_excel/`, '_blank')
}

const downloadNosaExcel = (nosaId) => {
  window.open(`/api/nosi/nosa/${nosaId}/download_nosa_excel/`, '_blank')
}

const downloadTeacherServiceRecord = (teacherId) => {
  const tid = teacherId || selectedTeacherId.value
  if (!tid) {
    alert('Please select a teacher to export the official CSC Form 122 Service Record.')
    return
  }
  window.open(`/api/nosi/service-records/download_csc_excel/?teacher_id=${tid}`, '_blank')
}

// Modal Handlers: NOSI
const openNewNosiModal = () => {
  editingRecord.value = null
  selectedNosiDirectFile.value = null
  if (nosiDirectFileInput.value) nosiDirectFileInput.value.value = ''

  formData.value = {
    teacher: selectedTeacherId.value || (teachersList.value[0]?.id || ''),
    nosi_number: `NOSI-${new Date().getFullYear()}-${String(records.value.length + 1).padStart(3, '0')}`,
    date_issued: new Date().toISOString().split('T')[0],
    effective_date: new Date().toISOString().split('T')[0],
    previous_salary_grade: 11,
    previous_step: 1,
    previous_monthly_salary: 27000,
    new_salary_grade: 11,
    new_step: 2,
    new_monthly_salary: 27284,
    division_office: 'Schools Division Office of Isabela',
    school_name: 'Naguilian Elementary School',
    schools_division_superintendent: 'MADELYN L. MACALLING, PhD, CESO VI',
    has_approved_nosi: false,
    has_annex_d: false,
    has_payslips: false,
    has_latest_appointment: false,
    has_updated_service_record: false,
    status: 'ELIGIBLE_PENDING',
    remarks: ''
  }
  showModal.value = true
}

const openEditModal = (rec) => {
  editingRecord.value = rec
  selectedNosiDirectFile.value = null
  formData.value = { ...rec, teacher: rec.teacher }
  showModal.value = true
}

const prepareNosiFromEligibility = (item) => {
  activeTab.value = 'records'
  editingRecord.value = null
  selectedNosiDirectFile.value = null
  formData.value = {
    teacher: item.teacher_id,
    nosi_number: `NOSI-${new Date().getFullYear()}-${String(records.value.length + 1).padStart(3, '0')}`,
    date_issued: new Date().toISOString().split('T')[0],
    effective_date: item.next_step_date,
    previous_salary_grade: item.current_salary_grade,
    previous_step: item.current_step,
    previous_monthly_salary: item.current_monthly_salary,
    new_salary_grade: item.next_salary_grade,
    new_step: item.next_step,
    new_monthly_salary: item.next_monthly_salary,
    division_office: 'Schools Division Office of Isabela',
    school_name: 'Naguilian Elementary School',
    schools_division_superintendent: 'MADELYN L. MACALLING, PhD, CESO VI',
    has_approved_nosi: false,
    has_annex_d: false,
    has_payslips: false,
    has_latest_appointment: false,
    has_updated_service_record: false,
    status: 'ELIGIBLE_PENDING',
    remarks: 'Auto-populated from 3-year continuous service entitlement calculation.'
  }
  showModal.value = true
}

const handleNosiDirectFileSelect = (e) => {
  selectedNosiDirectFile.value = e.target.files[0]
}

const saveNosiRecord = async () => {
  isSaving.value = true
  const data = new FormData()
  Object.keys(formData.value).forEach(key => {
    if (key !== 'documents' && key !== 'requirements_completion_rate' && key !== 'file_name') {
      const val = formData.value[key]
      if (val !== null && val !== undefined) {
        data.append(key, val)
      }
    }
  })
  if (selectedNosiDirectFile.value) {
    data.append('document_file', selectedNosiDirectFile.value)
  }

  try {
    if (editingRecord.value?.id) {
      await api.put(`/nosi/records/${editingRecord.value.id}/`, data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    } else {
      await api.post('/nosi/records/', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    showModal.value = false
    await fetchRecords()
  } catch (err) {
    console.error('Failed to save NOSI record:', err)
    alert('Failed to save NOSI record. Please check required fields.')
  } finally {
    isSaving.value = false
  }
}

const deleteNosiRecord = async (id) => {
  if (!confirm('Are you sure you want to delete this NOSI record?')) return
  try {
    await api.delete(`/nosi/records/${id}/`)
    await fetchRecords()
  } catch (err) {
    console.error('Failed to delete NOSI record:', err)
  }
}

// Modal Handlers: SERVICE RECORDS
const openNewServiceRecordModal = (teacherId) => {
  editingServiceRecord.value = null
  selectedServiceRecordFile.value = null
  if (serviceRecordFileInput.value) serviceRecordFileInput.value.value = ''

  let targetTeacherId = ''
  if (typeof teacherId === 'number' || (typeof teacherId === 'string' && teacherId && !isNaN(Number(teacherId)))) {
    targetTeacherId = Number(teacherId)
  } else if (selectedTeacherId.value) {
    targetTeacherId = Number(selectedTeacherId.value)
  } else if (authStore.canManageAll) {
    targetTeacherId = teachersList.value[0]?.id || ''
  } else {
    targetTeacherId = authStore.user?.teacher_id || ''
  }

  let defaultDesignation = 'Teacher I'
  let defaultStation = 'Naguilian Elementary School / DepEd Isabela'

  if (targetTeacherId) {
    const t = teachersList.value.find(x => x.id === Number(targetTeacherId))
    if (t) {
      if (t.position) defaultDesignation = t.position
      if (t.department) defaultStation = t.department
    }
  } else if (authStore.user?.position) {
    defaultDesignation = authStore.user.position
    if (authStore.user.department) defaultStation = authStore.user.department
  }

  serviceRecordForm.value = {
    teacher: targetTeacherId,
    from_date: new Date().toISOString().split('T')[0],
    to_date: '',
    to_present: true,
    designation: defaultDesignation,
    status_of_appointment: 'Permanent',
    salary_grade: 11,
    step: 1,
    monthly_salary: 27000,
    annual_salary: 324000,
    station_office: defaultStation,
    branch: 'National',
    lwop_dates: 'NONE',
    separation_date: '',
    separation_cause: '',
    remarks: 'Original Appointment'
  }
  showServiceRecordModal.value = true
}

const openEditServiceRecordModal = (sr) => {
  editingServiceRecord.value = sr
  selectedServiceRecordFile.value = null
  serviceRecordForm.value = { ...sr, teacher: sr.teacher }
  showServiceRecordModal.value = true
}

const onToPresentToggle = () => {
  if (serviceRecordForm.value.to_present) {
    serviceRecordForm.value.to_date = ''
  }
}

const onMonthlySalaryInput = () => {
  if (serviceRecordForm.value.monthly_salary) {
    serviceRecordForm.value.annual_salary = Number((serviceRecordForm.value.monthly_salary * 12).toFixed(2))
  }
}

const onAnnualSalaryInput = () => {
  if (serviceRecordForm.value.annual_salary) {
    serviceRecordForm.value.monthly_salary = Number((serviceRecordForm.value.annual_salary / 12).toFixed(2))
  }
}

const handleServiceRecordFileSelect = (e) => {
  selectedServiceRecordFile.value = e.target.files[0]
}

const saveServiceRecord = async () => {
  isSaving.value = true
  const data = new FormData()
  Object.keys(serviceRecordForm.value).forEach(key => {
    if (key !== 'file_name' && key !== 'document_file') {
      const val = serviceRecordForm.value[key]
      if (val !== null && val !== undefined) {
        data.append(key, val)
      }
    }
  })
  if (selectedServiceRecordFile.value) {
    data.append('document_file', selectedServiceRecordFile.value)
  }

  try {
    if (editingServiceRecord.value?.id) {
      await api.put(`/nosi/service-records/${editingServiceRecord.value.id}/`, data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    } else {
      await api.post('/nosi/service-records/', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    showServiceRecordModal.value = false
    await fetchServiceRecords()
  } catch (err) {
    console.error('Failed to save service record entry:', err)
    alert('Failed to save service record entry. Please ensure dates and fields are valid.')
  } finally {
    isSaving.value = false
  }
}

const deleteServiceRecord = async (id) => {
  if (!confirm('Are you sure you want to remove this service record entry?')) return
  try {
    await api.delete(`/nosi/service-records/${id}/`)
    await fetchServiceRecords()
  } catch (err) {
    console.error('Failed to delete service record:', err)
  }
}

// Modal Handlers: NOSA
const openNewNosaModal = () => {
  editingNosa.value = null
  selectedNosaFile.value = null
  if (nosaFileInput.value) nosaFileInput.value.value = ''

  nosaForm.value = {
    teacher: selectedTeacherId.value || (teachersList.value[0]?.id || ''),
    nosa_number: `NOSA-${new Date().getFullYear()}-${String(nosaRecords.value.length + 1).padStart(3, '0')}`,
    date_issued: new Date().toISOString().split('T')[0],
    effective_date: '2024-01-01',
    legal_basis: 'Executive Order No. 64, s. 2024 / NBC No. 594',
    position_title: 'Teacher I',
    salary_grade: 11,
    step: 1,
    previous_monthly_salary: 27000,
    adjusted_monthly_salary: 28000,
    status: 'ISSUED',
    signatory_authority: 'MADELYN L. MACALLING, PhD, CESO VI',
    remarks: 'Annual Salary Standardization Law Tranche Adjustment'
  }
  showNosaModal.value = true
}

const openEditNosaModal = (nosa) => {
  editingNosa.value = nosa
  selectedNosaFile.value = null
  nosaForm.value = { ...nosa, teacher: nosa.teacher }
  showNosaModal.value = true
}

const handleNosaFileSelect = (e) => {
  selectedNosaFile.value = e.target.files[0]
}

const saveNosaRecord = async () => {
  isSaving.value = true
  const data = new FormData()
  Object.keys(nosaForm.value).forEach(key => {
    if (key !== 'file_name' && key !== 'document_file') {
      const val = nosaForm.value[key]
      if (val !== null && val !== undefined) {
        data.append(key, val)
      }
    }
  })
  if (selectedNosaFile.value) {
    data.append('document_file', selectedNosaFile.value)
  }

  try {
    if (editingNosa.value?.id) {
      await api.put(`/nosi/nosa/${editingNosa.value.id}/`, data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    } else {
      await api.post('/nosi/nosa/', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    showNosaModal.value = false
    await fetchNosaRecords()
  } catch (err) {
    console.error('Failed to save NOSA record:', err)
    alert('Failed to save NOSA record.')
  } finally {
    isSaving.value = false
  }
}

const deleteNosaRecord = async (id) => {
  if (!confirm('Are you sure you want to delete this NOSA record?')) return
  try {
    await api.delete(`/nosi/nosa/${id}/`)
    await fetchNosaRecords()
  } catch (err) {
    console.error('Failed to delete NOSA record:', err)
  }
}

// Modal Handlers: APPOINTMENTS
const openNewAppointmentModal = () => {
  editingAppointment.value = null
  selectedAppointmentFile.value = null
  if (appointmentFileInput.value) appointmentFileInput.value.value = ''

  appointmentForm.value = {
    teacher: selectedTeacherId.value || (teachersList.value[0]?.id || ''),
    appointment_number: `APPT-${new Date().getFullYear()}-${String(appointmentRecords.value.length + 1).padStart(3, '0')}`,
    position_title: 'Teacher I',
    plantilla_item_no: `TCH1-${Math.floor(100000 + Math.random() * 900000)}-${new Date().getFullYear()}`,
    nature_of_appointment: 'Original',
    status_of_appointment: 'Permanent',
    salary_grade: 11,
    step: 1,
    monthly_rate: 27000,
    annual_rate: 324000,
    date_of_signing: new Date().toISOString().split('T')[0],
    date_of_assumption: new Date().toISOString().split('T')[0],
    csc_attestation_date: '',
    csc_action: 'Approved / Validated',
    vice_personnel: '',
    vice_reason: '',
    remarks: ''
  }
  showAppointmentModal.value = true
}

const openEditAppointmentModal = (app) => {
  editingAppointment.value = app
  selectedAppointmentFile.value = null
  appointmentForm.value = { ...app, teacher: app.teacher }
  showAppointmentModal.value = true
}

const handleAppointmentFileSelect = (e) => {
  selectedAppointmentFile.value = e.target.files[0]
}

const saveAppointmentRecord = async () => {
  isSaving.value = true
  const data = new FormData()
  Object.keys(appointmentForm.value).forEach(key => {
    if (key !== 'file_name' && key !== 'document_file') {
      const val = appointmentForm.value[key]
      if (val !== null && val !== undefined) {
        data.append(key, val)
      }
    }
  })
  if (selectedAppointmentFile.value) {
    data.append('document_file', selectedAppointmentFile.value)
  }

  try {
    if (editingAppointment.value?.id) {
      await api.put(`/nosi/appointments/${editingAppointment.value.id}/`, data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    } else {
      await api.post('/nosi/appointments/', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    showAppointmentModal.value = false
    await fetchAppointmentRecords()
  } catch (err) {
    console.error('Failed to save appointment record:', err)
    alert('Failed to save appointment record.')
  } finally {
    isSaving.value = false
  }
}

const deleteAppointmentRecord = async (id) => {
  if (!confirm('Are you sure you want to delete this appointment record?')) return
  try {
    await api.delete(`/nosi/appointments/${id}/`)
    await fetchAppointmentRecords()
  } catch (err) {
    console.error('Failed to delete appointment record:', err)
  }
}

// Upload Modal & Logic for NOSI Requirements Documents
const openUploadModal = (rec) => {
  activeRecordForDocs.value = rec
  uploadDocTitle.value = ''
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
  showDocModal.value = true
}

const handleFileSelect = (e) => {
  selectedFile.value = e.target.files[0]
}

const submitFileUpload = async () => {
  if (!selectedFile.value || !activeRecordForDocs.value) return
  isUploading.value = true
  const data = new FormData()
  data.append('record', activeRecordForDocs.value.id)
  data.append('doc_type', uploadDocType.value)
  data.append('title', uploadDocTitle.value || selectedFile.value.name)
  data.append('file', selectedFile.value)

  try {
    await api.post('/nosi/documents/', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    selectedFile.value = null
    uploadDocTitle.value = ''
    if (fileInput.value) fileInput.value.value = ''
    await fetchRecords()
    const updated = records.value.find(r => r.id === activeRecordForDocs.value.id)
    if (updated) activeRecordForDocs.value = updated
  } catch (err) {
    console.error('Failed to upload requirement document:', err)
    alert('Failed to upload document file.')
  } finally {
    isUploading.value = false
  }
}

const deleteDocument = async (docId) => {
  if (!confirm('Are you sure you want to remove this attached file?')) return
  try {
    await api.delete(`/nosi/documents/${docId}/`)
    await fetchRecords()
    const updated = records.value.find(r => r.id === activeRecordForDocs.value.id)
    if (updated) activeRecordForDocs.value = updated
  } catch (err) {
    console.error('Failed to delete document:', err)
  }
}

// Formatting Helpers
const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

const formatMoney = (val) => {
  if (val === null || val === undefined || isNaN(val)) return '0.00'
  return Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDaysRemaining = (days) => {
  if (days === null || days === undefined) return '—'
  if (days < 0) return `${Math.abs(days)}d Overdue`
  if (days === 0) return 'Due Today'
  return `${days}d Remaining`
}

const getDaysClass = (days) => {
  if (days === null || days === undefined) return ''
  if (days < 0) return 'danger'
  if (days <= 90) return 'warning'
  return 'ok'
}

const formatStatus = (status) => {
  const map = {
    ELIGIBLE_PENDING: 'Eligible / For Processing',
    DOCS_INCOMPLETE: 'Incomplete Requirements',
    DOCS_VERIFIED: 'Requirements Verified',
    NOSI_GENERATED: 'NOSI Prepared',
    APPROVED: 'Approved by SDS',
    INTEGRATED_PAYROLL: 'Integrated into Payroll'
  }
  return map[status] || status
}

const formatAlertType = (type) => {
  const map = {
    UPCOMING_INCREMENT: 'Step Increment Approaching',
    OVERDUE_INCREMENT: 'Overdue Claim',
    MISSING_REQUIREMENTS: 'Missing Documents',
    APPROVED_READY: 'Ready for Differential'
  }
  return map[type] || type
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    fetchRecords(),
    fetchServiceRecords(),
    fetchNosaRecords(),
    fetchAppointmentRecords(),
    fetchEligibility(),
    fetchAlerts(),
    fetchSalarySchedules(),
    fetchTeachers()
  ])
})
</script>

<style scoped>
.nosi-dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding-bottom: 3rem;
}

/* Glass Header */
.nosi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.8rem 2rem;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, rgba(30, 58, 138, 0.95), rgba(15, 23, 42, 0.9));
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
}

.header-main {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.deped-seal {
  font-size: 2.8rem;
  background: rgba(255, 255, 255, 0.1);
  width: 68px;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.badge-tag {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  background: rgba(255, 255, 255, 0.15);
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  margin-bottom: 0.35rem;
}

.nosi-header h1 {
  font-size: 1.55rem;
  font-weight: 800;
  margin: 0;
  color: #fff;
}

.subtitle {
  font-size: 0.88rem;
  color: #cbd5e1;
  margin-top: 0.25rem;
  max-width: 820px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-refresh-scan {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.6rem 1.1rem;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  transition: all 0.2s ease;
}

.btn-refresh-scan:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.22);
}

.btn-create-nosi {
  background: #3b82f6;
  color: #fff;
  border: none;
  padding: 0.6rem 1.25rem;
  border-radius: var(--radius-md);
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
  transition: all 0.2s ease;
}

.btn-create-nosi:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

/* Teacher Filter Bar */
.teacher-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.filter-label {
  font-size: 0.88rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-primary);
}

.select-teacher-filter {
  padding: 0.55rem 1rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.88rem;
  min-width: 380px;
}

.teacher-badge-static {
  background: #eff6ff;
  color: #1e40af;
  padding: 0.4rem 0.8rem;
  border-radius: var(--radius-sm);
  font-size: 0.88rem;
  border: 1px solid #bfdbfe;
}

.teacher-ribbon-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.ribbon-tag {
  font-size: 0.78rem;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
}

.ribbon-tag.pos { background: #e0f2fe; color: #0369a1; }
.ribbon-tag.dept { background: #f1f5f9; color: #475569; }
.ribbon-tag.id { background: #fef3c7; color: #92400e; }

.btn-csc-export {
  background: #10b981;
  color: #fff;
  border: none;
  padding: 0.45rem 0.9rem;
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  transition: all 0.2s ease;
}

.btn-csc-export:hover {
  background: #059669;
}

.btn-csc-download-header {
  background: #047857;
  color: #fff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-csc-download-header:hover {
  background: #065f46;
}

/* Alerts Center */
.alerts-container {
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  padding: 1.25rem 1.5rem;
}

.alerts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.alert-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.alert-title-wrap h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
}

.badge-alert-count {
  background: #ef4444;
  color: #fff;
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-weight: 700;
}

.btn-ghost-sm {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.78rem;
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.alerts-empty {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-muted);
  font-size: 0.88rem;
  padding: 0.5rem 0;
}

.alerts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1rem;
}

.alert-card {
  display: flex;
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: all 0.2s ease;
}

.alert-card.is-read {
  opacity: 0.65;
}

.alert-side-indicator {
  width: 5px;
}

.alert-card.danger .alert-side-indicator { background: #ef4444; }
.alert-card.warning .alert-side-indicator { background: #f59e0b; }
.alert-card.info .alert-side-indicator { background: #3b82f6; }
.alert-card.success .alert-side-indicator { background: #10b981; }

.alert-content {
  flex: 1;
  padding: 0.9rem 1.1rem;
}

.alert-top {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  margin-bottom: 0.35rem;
}

.alert-badge {
  font-weight: 700;
  color: #2563eb;
}

.alert-time {
  color: var(--text-muted);
}

.alert-headline {
  font-size: 0.92rem;
  margin: 0 0 0.3rem 0;
  color: var(--text-primary);
}

.alert-msg {
  font-size: 0.82rem;
  color: var(--text-muted);
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
}

.alert-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.76rem;
}

.alert-target-teacher {
  font-weight: 600;
  color: var(--text-primary);
}

.btn-mark-read {
  background: transparent;
  border: none;
  color: #3b82f6;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

/* Quick Metrics Row */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 1.1rem;
  padding: 1.25rem 1.4rem;
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.metric-icon.blue { background: #dbeafe; color: #1d4ed8; }
.metric-icon.amber { background: #fef3c7; color: #b45309; }
.metric-icon.emerald { background: #d1fae5; color: #047857; }
.metric-icon.purple { background: #ede9fe; color: #6d28d9; }
.metric-icon.cyan { background: #cffafe; color: #0e7490; }

.metric-data h3 {
  margin: 0;
  font-size: 1.45rem;
  font-weight: 800;
  color: var(--text-primary);
}

.metric-data p {
  margin: 0.2rem 0 0 0;
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 600;
}

/* Main Tabs Navigation */
.tab-nav {
  display: flex;
  gap: 0.4rem;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0.25rem;
  overflow-x: auto;
}

.tab-btn {
  padding: 0.75rem 1.25rem;
  background: transparent;
  border: none;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-muted);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--text-primary);
  background: rgba(0, 0, 0, 0.03);
}

.tab-btn.active {
  color: #2563eb;
  border-bottom: 3px solid #2563eb;
  background: var(--bg-surface);
}

/* Panels */
.tab-panel {
  padding: 1.75rem 2rem;
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.panel-header h3 {
  font-size: 1.2rem;
  font-weight: 800;
  margin: 0 0 0.3rem 0;
  color: var(--text-primary);
}

.panel-desc {
  font-size: 0.84rem;
  color: var(--text-muted);
  margin: 0;
  max-width: 750px;
}

.panel-filters {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-add-sr-primary {
  background: #2563eb !important;
  color: #fff !important;
  font-weight: 700;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
  padding: 0.6rem 1.2rem !important;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  white-space: nowrap;
}

.btn-add-sr-primary:hover {
  background: #1d4ed8 !important;
  transform: translateY(-1px);
}

.expand-collapse-btns {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.btn-toggle-all {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-toggle-all:hover {
  background: var(--border-color);
  color: var(--text-primary);
}

.search-input {
  padding: 0.55rem 1rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  min-width: 280px;
}

/* Requirements Info Box */
.requirements-infobox {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #3b82f6;
  border-radius: var(--radius-sm);
  padding: 0.85rem 1.1rem;
  margin-bottom: 1.25rem;
}

.info-title {
  font-size: 0.84rem;
  margin-bottom: 0.5rem;
  color: #1e293b;
}

.requirements-pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.req-tag {
  background: #fff;
  border: 1px solid #cbd5e1;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.76rem;
  font-weight: 600;
  color: #475569;
}

/* Data Table */
.table-responsive {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.data-table th {
  background: var(--bg-primary);
  padding: 0.85rem;
  color: var(--text-muted);
  font-weight: 700;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  white-space: nowrap;
}

.data-table td {
  padding: 0.85rem;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
  font-size: 0.86rem;
}

/* Master-Detail Drill Down Styles */
.teacher-summary-row {
  cursor: pointer;
  transition: background 0.15s ease;
}

.teacher-summary-row:hover {
  background: rgba(59, 130, 246, 0.05);
}

.teacher-summary-row.is-expanded {
  background: #f8fafc;
  border-bottom: none;
}

.drilldown-cell {
  text-align: center;
  width: 44px;
}

.btn-drilldown-toggle {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid #cbd5e1;
  background: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-drilldown-toggle:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.btn-drilldown-toggle.expanded {
  background: #3b82f6;
  border-color: #3b82f6;
}

.btn-drilldown-toggle.expanded .chevron-icon {
  color: #fff;
}

.chevron-icon {
  font-size: 0.68rem;
  color: #3b82f6;
  line-height: 1;
}

.teacher-profile-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.teacher-avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: #fff;
  font-weight: 800;
  font-size: 0.82rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.25);
}

.teacher-name-box {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.teacher-display-name {
  font-size: 0.92rem;
  color: var(--text-primary);
}

.teacher-emp-id {
  font-size: 0.74rem;
  color: var(--text-muted);
  font-family: monospace;
}

.teacher-curr-pos {
  font-size: 0.88rem;
  color: var(--text-primary);
}

.teacher-station {
  font-size: 0.76rem;
  color: var(--text-muted);
}

.span-display {
  font-size: 0.85rem;
  color: var(--text-primary);
  margin-bottom: 0.2rem;
}

.records-count-badge {
  font-size: 0.72rem;
  font-weight: 700;
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.12rem 0.5rem;
  border-radius: 9999px;
  display: inline-block;
}

.docs-count-chip {
  font-size: 0.74rem;
  font-weight: 700;
  background: #ecfdf5;
  color: #047857;
  padding: 0.15rem 0.55rem;
  border-radius: 9999px;
  display: inline-block;
}

.btn-action-primary-sm {
  background: #2563eb;
  color: #fff;
  border: none;
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-action-primary-sm:hover {
  background: #1d4ed8;
}

/* Drill Down Details Subtable Container */
.drilldown-detail-row {
  background: #f8fafc;
}

.drilldown-container-td {
  padding: 0.25rem 1rem 1.25rem 1rem !important;
  border-top: none !important;
}

.drilldown-subtable-wrapper {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.drilldown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 1.25rem;
  background: #f1f5f9;
  border-bottom: 1px solid #e2e8f0;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.drilldown-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.drilldown-title h4 {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 800;
  color: #1e293b;
}

.sub-badge {
  font-size: 0.72rem;
  font-weight: 700;
  background: #dbeafe;
  color: #1e40af;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
}

.drilldown-header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-create-sub-entry {
  background: #059669;
  color: #fff;
  border: none;
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  transition: all 0.15s ease;
}

.btn-create-sub-entry:hover {
  background: #047857;
}

.empty-subtable {
  padding: 2rem;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.88rem;
}

.inner-data-table {
  width: 100%;
  border-collapse: collapse;
}

.inner-data-table th {
  background: #f8fafc;
  padding: 0.7rem 0.85rem;
  font-size: 0.74rem;
  color: #475569;
  font-weight: 700;
  border-bottom: 1px solid #e2e8f0;
  text-transform: uppercase;
}

.inner-data-table td {
  padding: 0.75rem 0.85rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.84rem;
  vertical-align: middle;
}


.date-range {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  white-space: nowrap;
}

.to-arrow {
  color: var(--text-muted);
}

.date-end.is-present {
  color: #059669;
  font-weight: 700;
  background: #ecfdf5;
  padding: 0.15rem 0.4rem;
  border-radius: var(--radius-sm);
}

.teacher-name {
  font-weight: 700;
  color: var(--text-primary);
}

.teacher-sub, .resi-sub, .salary-sub {
  font-size: 0.76rem;
  color: var(--text-muted);
}

.pos-title {
  color: var(--text-primary);
  margin-bottom: 0.2rem;
}

.status-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.18rem 0.5rem;
  border-radius: 9999px;
  display: inline-block;
}

.status-pill.appt-status {
  background: #f1f5f9;
  color: #334155;
}

.status-pill.eligible_pending { background: #fef3c7; color: #92400e; }
.status-pill.docs_incomplete { background: #fee2e2; color: #b91c1c; }
.status-pill.docs_verified { background: #e0f2fe; color: #0369a1; }
.status-pill.nosi_generated { background: #ede9fe; color: #6d28d9; }
.status-pill.approved { background: #d1fae5; color: #047857; }
.status-pill.integrated_payroll { background: #ecfdf5; color: #065f46; }
.status-pill.issued { background: #dbeafe; color: #1e40af; }
.status-pill.draft { background: #f1f5f9; color: #475569; }
.status-pill.danger { background: #fee2e2; color: #b91c1c; }
.status-pill.warning { background: #fef3c7; color: #b45309; }
.status-pill.in_progress { background: #eff6ff; color: #2563eb; }
.status-pill.info { background: #f3e8ff; color: #7e22ce; }

.sg-badge {
  font-size: 0.72rem;
  font-weight: 700;
  background: #eff6ff;
  color: #2563eb;
  padding: 0.12rem 0.45rem;
  border-radius: var(--radius-sm);
  margin-left: 0.35rem;
}

.nature-pill {
  font-size: 0.72rem;
  font-weight: 700;
  background: #ecfdf5;
  color: #047857;
  padding: 0.12rem 0.45rem;
  border-radius: var(--radius-sm);
}

.salary-main {
  font-weight: 700;
  color: var(--text-primary);
}

.station-name {
  font-weight: 600;
  color: var(--text-primary);
}

.branch-tag {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.lwop-pill {
  font-size: 0.74rem;
  font-weight: 600;
  color: #64748b;
}

.lwop-pill.has-lwop {
  color: #b91c1c;
  background: #fee2e2;
  padding: 0.15rem 0.4rem;
  border-radius: var(--radius-sm);
}

.sep-cause {
  font-weight: 700;
  font-size: 0.8rem;
  color: #b91c1c;
}

.sep-date {
  font-size: 0.74rem;
  color: var(--text-muted);
}

.text-muted-dash {
  color: var(--text-muted);
}

.remarks-cell {
  max-width: 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.82rem;
  color: var(--text-muted);
}

/* Attached Document Chips */
.file-chip {
  display: inline-block;
}

.btn-doc-link {
  font-size: 0.76rem;
  font-weight: 700;
  color: #2563eb;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 0.25rem 0.55rem;
  border-radius: var(--radius-sm);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.2s ease;
  max-width: 170px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn-doc-link:hover {
  background: #dbeafe;
  border-color: #93c5fd;
}

.no-file-tag {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-style: italic;
}

.btn-group-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-icon {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 0.35rem 0.55rem;
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.15s ease;
}

.btn-icon:hover {
  background: var(--border-color);
}

.btn-icon.danger {
  color: #ef4444;
}

.btn-icon.danger:hover {
  background: #fee2e2;
  border-color: #fca5a5;
}

/* Checklist Progress & Checkboxes in Table */
.req-cell {
  min-width: 270px;
}

.checklist-progress-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.bar-fill {
  height: 100%;
  background: #3b82f6;
  transition: width 0.3s ease;
}

.bar-fill.full {
  background: #10b981;
}

.progress-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
  display: block;
  margin-bottom: 0.35rem;
}

.checklist-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.chk-item {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.7rem;
  padding: 0.12rem 0.35rem;
  background: #f8fafc;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
}

.chk-item.checked {
  background: #ecfdf5;
  color: #065f46;
  border-color: #a7f3d0;
  font-weight: 700;
}

/* Modals */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 1.5rem;
}

.modal-card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  width: 100%;
  max-width: 650px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
}

.modal-card.modal-lg {
  max-width: 820px;
}

.modal-card.doc-modal {
  max-width: 720px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem 1.8rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-primary);
}

.modal-sub {
  margin: 0.25rem 0 0 0;
  font-size: 0.82rem;
  color: var(--text-muted);
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 1.6rem;
  color: var(--text-muted);
  cursor: pointer;
  line-height: 1;
}

.modal-form {
  padding: 1.5rem 1.8rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.col-12 { flex: 0 0 100%; }
.col-6 { flex: 1; }
.col-4 { flex: 1; }
.col-3 { flex: 1; }

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group label {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-primary);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.6rem 0.85rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.88rem;
  width: 100%;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.upload-field-box {
  background: #f8fafc;
  padding: 1rem;
  border-radius: var(--radius-sm);
  border: 1px dashed #cbd5e1;
}

.file-picker-row {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-top: 0.35rem;
}

.existing-file-hint {
  font-size: 0.78rem;
  color: #059669;
  font-weight: 600;
}

.existing-file-hint a {
  color: #2563eb;
  text-decoration: underline;
}

.checklist-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 1rem 1.2rem;
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.checklist-box h4 {
  margin: 0 0 0.4rem 0;
  font-size: 0.88rem;
  font-weight: 700;
  color: #1e293b;
}

.form-chk-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.84rem;
  color: var(--text-primary);
  cursor: pointer;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-color);
  padding: 0.6rem 1.2rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
}

.btn-save {
  background: #2563eb;
  color: #fff;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: var(--radius-sm);
  font-weight: 700;
  cursor: pointer;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Upload & Verification Modal */
.modal-body {
  padding: 1.5rem 1.8rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.upload-box {
  background: #f8fafc;
  padding: 1.25rem;
  border-radius: var(--radius-md);
  border: 1px dashed #cbd5e1;
}

.upload-box h4 {
  margin: 0 0 0.85rem 0;
  font-size: 0.95rem;
}

.upload-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

.select-doc-type {
  padding: 0.55rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  font-size: 0.85rem;
}

.input-doc-title {
  flex: 1;
  padding: 0.55rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  font-size: 0.85rem;
  min-width: 180px;
}

.input-file {
  font-size: 0.82rem;
}

.btn-upload {
  background: #10b981;
  color: #fff;
  border: none;
  padding: 0.55rem 1.2rem;
  border-radius: var(--radius-sm);
  font-weight: 700;
  cursor: pointer;
}

.attached-docs-section h4 {
  margin: 0 0 0.75rem 0;
  font-size: 0.95rem;
}

.doc-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.doc-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.doc-badge {
  font-size: 0.7rem;
  background: #dbeafe;
  color: #1e40af;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-weight: 700;
}

.doc-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.doc-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.btn-download-file {
  font-size: 0.78rem;
  color: #2563eb;
  font-weight: 700;
  text-decoration: none;
}

.btn-delete-doc {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.empty-docs, .empty-state, .loading-state {
  text-align: center;
  padding: 2.5rem 1.5rem;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.spin {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

@media (max-width: 900px) {
  .nosi-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.25rem;
  }
  .teacher-filter-bar {
    flex-direction: column;
    align-items: flex-start;
  }
  .select-teacher-filter {
    min-width: 100%;
  }
  .form-row {
    flex-direction: column;
  }
}
</style>
