<template>
  <div class="attendance-container">
    <!-- Header Section -->
    <div class="page-header glass-panel">
      <div class="header-left">
        <div class="title-with-badge">
          <h1>⏱️ Time &amp; Attendance Management</h1>
          <span class="badge-csc">CSC Form 48 &amp; Form 6</span>
        </div>
        <p class="subtitle">Daily Time Record (DTR) monitoring, digital biometric clock, and Civil Service leave credit administration</p>
      </div>

      <div class="header-right">
        <!-- Faculty Selector for HR/Admin -->
        <div v-if="isAdminOrHR" class="teacher-select-box">
          <label>View Faculty / Staff:</label>
          <select v-model="selectedTeacherId" @change="handleTeacherChange">
            <option v-for="t in teachersList" :key="t.id" :value="t.id">
              {{ t.full_name }} — {{ t.role_display || t.position || 'Staff' }} ({{ t.employee_id || 'ID' }})
            </option>
          </select>
        </div>

        <button @click="downloadDTRExcel" class="btn-action btn-excel" :disabled="isDownloadingExcel" title="Download Official CS Form 48 as Excel (.xlsx)">
          <span v-if="isDownloadingExcel">⏳ Exporting...</span>
          <span v-else>📊 Download Excel</span>
        </button>

        <button @click="downloadDTRPdf" class="btn-action btn-pdf" :disabled="isDownloadingPdf" title="Download Official CS Form 48 as PDF (.pdf)">
          <span v-if="isDownloadingPdf">⏳ Generating...</span>
          <span v-else>📄 Download PDF</span>
        </button>

        <button @click="printDTR" class="btn-action btn-print" title="Print CSC Form 48">
          🖨️ Print Form 48
        </button>
      </div>
    </div>

    <!-- Live Punch Card & Shift Schedule Banner -->
    <div class="punch-and-schedule-grid">
      <!-- Live Clock & Punch Station -->
      <div class="clock-card glass-panel">
        <div class="clock-header">
          <span class="clock-icon">🕒</span>
          <div>
            <span class="clock-label">Philippine Standard Time (PST)</span>
            <div class="current-date-text">{{ currentDateFormatted }}</div>
          </div>
        </div>

        <div class="digital-clock-display">
          {{ currentTimeFormatted }}
        </div>

        <div class="punch-buttons-grid">
          <!-- AM IN -->
          <div class="punch-slot">
            <button
              @click="handlePunch('am_in')"
              :disabled="attendanceStore.isPunching || hasPunched('am_time_in')"
              :class="['btn-punch', { punched: hasPunched('am_time_in') }]"
            >
              <div class="punch-slot-title">AM Arrival (In)</div>
              <div class="punch-time-val">
                {{ getPunchTime('am_time_in') || '08:00 AM' }}
              </div>
              <span v-if="hasPunched('am_time_in')" class="punched-badge">✓ Recorded</span>
              <span v-else class="punch-action-label">Click to Punch</span>
            </button>
          </div>

          <!-- AM OUT -->
          <div class="punch-slot">
            <button
              @click="handlePunch('am_out')"
              :disabled="attendanceStore.isPunching || hasPunched('am_time_out')"
              :class="['btn-punch', { punched: hasPunched('am_time_out') }]"
            >
              <div class="punch-slot-title">AM Departure (Out)</div>
              <div class="punch-time-val">
                {{ getPunchTime('am_time_out') || '12:00 PM' }}
              </div>
              <span v-if="hasPunched('am_time_out')" class="punched-badge">✓ Recorded</span>
              <span v-else class="punch-action-label">Click to Punch</span>
            </button>
          </div>

          <!-- PM IN -->
          <div class="punch-slot">
            <button
              @click="handlePunch('pm_in')"
              :disabled="attendanceStore.isPunching || hasPunched('pm_time_in')"
              :class="['btn-punch', { punched: hasPunched('pm_time_in') }]"
            >
              <div class="punch-slot-title">PM Arrival (In)</div>
              <div class="punch-time-val">
                {{ getPunchTime('pm_time_in') || '01:00 PM' }}
              </div>
              <span v-if="hasPunched('pm_time_in')" class="punched-badge">✓ Recorded</span>
              <span v-else class="punch-action-label">Click to Punch</span>
            </button>
          </div>

          <!-- PM OUT -->
          <div class="punch-slot">
            <button
              @click="handlePunch('pm_out')"
              :disabled="attendanceStore.isPunching || hasPunched('pm_time_out')"
              :class="['btn-punch', { punched: hasPunched('pm_time_out') }]"
            >
              <div class="punch-slot-title">PM Departure (Out)</div>
              <div class="punch-time-val">
                {{ getPunchTime('pm_time_out') || '05:00 PM' }}
              </div>
              <span v-if="hasPunched('pm_time_out')" class="punched-badge">✓ Recorded</span>
              <span v-else class="punch-action-label">Click to Punch</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Shift Info & Status Box -->
      <div class="shift-info-card glass-panel">
        <div class="shift-card-header">
          <h3>Faculty Shift Schedule</h3>
          <span class="badge-status-tag">Active Schedule</span>
        </div>

        <div class="shift-details-list">
          <div class="shift-row">
            <span class="shift-label">Official AM Working Hours:</span>
            <strong class="shift-val">08:00 AM – 12:00 PM</strong>
          </div>
          <div class="shift-row">
            <span class="shift-label">Official PM Working Hours:</span>
            <strong class="shift-val">01:00 PM – 05:00 PM</strong>
          </div>
          <div class="shift-row">
            <span class="shift-label">Tardiness Grace Period:</span>
            <span class="grace-badge">15 Minutes Allowed</span>
          </div>
          <div class="shift-row">
            <span class="shift-label">Today's Rendered Hours:</span>
            <strong class="hours-val">{{ todayRecord?.total_hours_rendered || '0.00' }} hrs</strong>
          </div>
        </div>

        <!-- Quick Status Alert -->
        <div class="today-status-banner" :class="todayRecord?.status?.toLowerCase()?.replace(/\s+/g, '-')">
          <span class="status-icon">📋</span>
          <div>
            <strong>Status Today: {{ todayRecord?.status || 'Not Yet Logged' }}</strong>
            <p v-if="todayRecord?.tardy_minutes > 0" class="sub-alert">
              Tardy: {{ todayRecord.tardy_minutes }} minutes
            </p>
            <p v-else class="sub-alert">Official attendance is verified.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Analytics KPI Cards -->
    <div class="stats-grid">
      <div class="kpi-card glass-panel">
        <div class="kpi-icon-wrap present">👨‍🏫</div>
        <div class="kpi-content">
          <div class="kpi-title">Campus Present Today</div>
          <div class="kpi-val">{{ attendanceStore.stats?.today_present ?? 0 }}</div>
          <div class="kpi-sub">Out of {{ attendanceStore.stats?.total_teachers ?? 0 }} total faculty</div>
        </div>
      </div>

      <div class="kpi-card glass-panel">
        <div class="kpi-icon-wrap rate">📈</div>
        <div class="kpi-content">
          <div class="kpi-title">Today's Attendance Rate</div>
          <div class="kpi-val">{{ attendanceStore.stats?.today_attendance_rate ?? 100 }}%</div>
          <div class="kpi-sub">On-duty institutional rating</div>
        </div>
      </div>

      <div class="kpi-card glass-panel">
        <div class="kpi-icon-wrap tardy">⚠️</div>
        <div class="kpi-content">
          <div class="kpi-title">Tardy Minutes Today</div>
          <div class="kpi-val">{{ attendanceStore.stats?.total_tardy_minutes_today ?? 0 }} min</div>
          <div class="kpi-sub">{{ attendanceStore.stats?.today_tardy ?? 0 }} faculty late arrivals</div>
        </div>
      </div>

      <div class="kpi-card glass-panel">
        <div class="kpi-icon-wrap leave">🏖️</div>
        <div class="kpi-content">
          <div class="kpi-title">Pending Leave Requests</div>
          <div class="kpi-val">{{ attendanceStore.stats?.pending_leaves_count ?? 0 }}</div>
          <div class="kpi-sub">Awaiting HR endorsement</div>
        </div>
      </div>
    </div>

    <!-- Main Navigation Tabs: DTR (Form 48) vs Leave Applications (Form 6) -->
    <div class="module-tab-bar glass-panel">
      <button
        @click="activeTab = 'dtr'"
        :class="['tab-btn', { active: activeTab === 'dtr' }]"
      >
        📄 Civil Service Form No. 48 (Daily Time Record)
      </button>
      <button
        @click="activeTab = 'leave'"
        :class="['tab-btn', { active: activeTab === 'leave' }]"
      >
        🏖️ Leave Management &amp; Credits (CSC Form 6)
      </button>
    </div>

    <!-- TAB 1: CSC FORM NO. 48 (DAILY TIME RECORD) -->
    <div v-if="activeTab === 'dtr'" class="dtr-view-wrapper glass-panel">
      <!-- DTR Month Selector & Controls -->
      <div class="dtr-controls-bar">
        <div class="month-selector-group">
          <button @click="changeMonth(-1)" class="btn-month-nav" title="Previous Month">◀</button>
          <div class="current-month-display">
            <strong>{{ attendanceStore.monthlyDTR?.month_name || currentMonthName }} {{ currentYear }}</strong>
            <small>Daily Time Record</small>
          </div>
          <button @click="changeMonth(1)" class="btn-month-nav" title="Next Month">▶</button>
          <div class="dtr-export-buttons">
            <button @click="downloadDTRExcel" class="btn-export-small btn-excel" :disabled="isDownloadingExcel" title="Download Excel">
              📊 Excel
            </button>
            <button @click="downloadDTRPdf" class="btn-export-small btn-pdf" :disabled="isDownloadingPdf" title="Download PDF">
              📄 PDF
            </button>
          </div>
        </div>

        <!-- Monthly Totals Summary Strip -->
        <div v-if="attendanceStore.monthlyDTR?.summary" class="monthly-summary-badges">
          <div class="sum-pill present">
            <span>Days Present:</span>
            <strong>{{ attendanceStore.monthlyDTR.summary.days_present }}</strong>
          </div>
          <div class="sum-pill tardy">
            <span>Total Tardy:</span>
            <strong>{{ attendanceStore.monthlyDTR.summary.tardy_formatted }}</strong>
          </div>
          <div class="sum-pill undertime">
            <span>Undertime:</span>
            <strong>{{ attendanceStore.monthlyDTR.summary.undertime_formatted }}</strong>
          </div>
          <div class="sum-pill hours">
            <span>Rendered Hours:</span>
            <strong>{{ attendanceStore.monthlyDTR.summary.total_hours_rendered }} hrs</strong>
          </div>
        </div>
      </div>

      <!-- Printable CSC Form 48 Header (renders for screen & print) -->
      <div class="printable-form48-header">
        <div class="form48-gov-title">CIVIL SERVICE FORM NO. 48</div>
        <h2>DAILY TIME RECORD</h2>
        <div class="form48-name-line">
          <strong>{{ attendanceStore.monthlyDTR?.teacher?.name || 'FACULTY MEMBER' }}</strong>
          <span class="caption">(Name in Full)</span>
        </div>
        <div class="form48-meta-line">
          <span>For the month of <u>{{ attendanceStore.monthlyDTR?.month_name }} {{ currentYear }}</u></span>
          <span>Official hours: <u>8:00 AM - 12:00 PM / 1:00 PM - 5:00 PM</u></span>
        </div>
      </div>

      <!-- 31-Day Table -->
      <div class="table-responsive">
        <table class="dtr-csc-table">
          <thead>
            <tr>
              <th rowspan="2" class="col-day">Day</th>
              <th colspan="2" class="col-group">A.M.</th>
              <th colspan="2" class="col-group">P.M.</th>
              <th colspan="2" class="col-group">UNDERTIME</th>
              <th rowspan="2" class="col-status">Status</th>
              <th rowspan="2" class="col-remarks">Remarks</th>
            </tr>
            <tr>
              <th class="col-sub">Arrival</th>
              <th class="col-sub">Departure</th>
              <th class="col-sub">Arrival</th>
              <th class="col-sub">Departure</th>
              <th class="col-sub">Hours</th>
              <th class="col-sub">Minutes</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="d in attendanceStore.monthlyDTR?.days"
              :key="d.day"
              :class="{
                'weekend-row': d.is_weekend,
                'leave-row': d.status === 'On Leave',
                'tardy-row': d.tardy_minutes > 0
              }"
            >
              <td class="cell-day">
                <strong>{{ d.day }}</strong>
                <span class="day-abbr">{{ d.day_name }}</span>
              </td>
              <td class="cell-time">{{ d.am_time_in || '—' }}</td>
              <td class="cell-time">{{ d.am_time_out || '—' }}</td>
              <td class="cell-time">{{ d.pm_time_in || '—' }}</td>
              <td class="cell-time">{{ d.pm_time_out || '—' }}</td>
              <td class="cell-num">{{ d.undertime_minutes ? Math.floor(d.undertime_minutes / 60) : '—' }}</td>
              <td class="cell-num">{{ d.tardy_minutes || d.undertime_minutes ? (d.tardy_minutes + (d.undertime_minutes % 60)) : '—' }}</td>
              <td class="cell-status">
                <span :class="['dtr-status-pill', getStatusClass(d.status)]">
                  {{ d.status || (d.is_weekend ? 'Weekend' : '—') }}
                </span>
              </td>
              <td class="cell-remarks">{{ d.remarks || '—' }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="total-row">
              <td><strong>TOTAL</strong></td>
              <td colspan="4" class="text-center">Total Hours Rendered: <strong>{{ attendanceStore.monthlyDTR?.summary?.total_hours_rendered }} hrs</strong></td>
              <td><strong>{{ Math.floor((attendanceStore.monthlyDTR?.summary?.total_undertime_minutes || 0) / 60) }}</strong></td>
              <td><strong>{{ (attendanceStore.monthlyDTR?.summary?.total_tardy_minutes || 0) + ((attendanceStore.monthlyDTR?.summary?.total_undertime_minutes || 0) % 60) }}</strong></td>
              <td colspan="2"></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- Printable Certification Footer -->
      <div class="printable-form48-footer">
        <p class="cert-text">
          I certify on my honor that the above is a true and correct report of the hours of work performed, record of which was made daily at the time of arrival and departure from office.
        </p>
        <div class="sig-lines-row">
          <div class="sig-block">
            <div class="line"></div>
            <span>Signature of Teacher / Employee</span>
          </div>
          <div class="sig-block">
            <div class="line"></div>
            <span>In Charge / School Head</span>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: LEAVE MANAGEMENT & CREDITS (CSC FORM NO. 6) -->
    <div v-else-if="activeTab === 'leave'" class="leave-module-wrapper">
      <!-- Leave Credits Overview Cards -->
      <div class="leave-credits-grid">
        <div class="credit-card glass-panel vacation">
          <div class="credit-header">
            <span class="credit-icon">🏖️</span>
            <div>
              <h4>Vacation Leave (VL)</h4>
              <small>Sec. 51, Rule XVI, CSC MC 41</small>
            </div>
          </div>
          <div class="credit-balance-row">
            <div class="balance-num">{{ currentTeacherBalance?.vacation_leave ?? '15.00' }}</div>
            <span class="days-label">Days Left</span>
          </div>
          <div class="credit-bar">
            <div
              class="credit-fill"
              :style="{ width: `${Math.min(100, ((currentTeacherBalance?.vacation_leave || 15) / 15) * 100)}%` }"
            ></div>
          </div>
        </div>

        <div class="credit-card glass-panel sick">
          <div class="credit-header">
            <span class="credit-icon">🩺</span>
            <div>
              <h4>Sick Leave (SL)</h4>
              <small>Sec. 43, Rule XVI, CSC MC 41</small>
            </div>
          </div>
          <div class="credit-balance-row">
            <div class="balance-num">{{ currentTeacherBalance?.sick_leave ?? '15.00' }}</div>
            <span class="days-label">Days Left</span>
          </div>
          <div class="credit-bar">
            <div
              class="credit-fill sick"
              :style="{ width: `${Math.min(100, ((currentTeacherBalance?.sick_leave || 15) / 15) * 100)}%` }"
            ></div>
          </div>
        </div>

        <div class="credit-card glass-panel spl">
          <div class="credit-header">
            <span class="credit-icon">⭐</span>
            <div>
              <h4>Special Privilege Leave (SPL)</h4>
              <small>3 Days Non-Cumulative Annual</small>
            </div>
          </div>
          <div class="credit-balance-row">
            <div class="balance-num">{{ currentTeacherBalance?.special_privilege_leave ?? '3.00' }}</div>
            <span class="days-label">Days Left</span>
          </div>
          <div class="credit-bar">
            <div
              class="credit-fill spl"
              :style="{ width: `${Math.min(100, ((currentTeacherBalance?.special_privilege_leave || 3) / 3) * 100)}%` }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Leave Actions Bar -->
      <div class="leave-toolbar glass-panel">
        <div class="toolbar-left">
          <h3>Applications for Leave (CS Form No. 6)</h3>
        </div>
        <button @click="openApplyModal" class="btn-primary-peach">
          ➕ Apply for Leave
        </button>
      </div>

      <!-- Leave Applications Table -->
      <div class="leave-table-container glass-panel">
        <table class="leave-table">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Leave Type</th>
              <th>Inclusive Dates</th>
              <th>Days</th>
              <th>Reason</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in attendanceStore.leaves" :key="l.id">
              <td>
                <strong>{{ l.teacher_name }}</strong>
                <small>{{ l.employee_id }} • {{ l.department }}</small>
              </td>
              <td><span class="leave-type-pill">{{ l.leave_type }}</span></td>
              <td>{{ l.start_date }} to {{ l.end_date }}</td>
              <td><strong>{{ l.days_applied }} days</strong></td>
              <td class="reason-cell" :title="l.reason">{{ l.reason }}</td>
              <td>
                <span :class="['status-badge', l.status.toLowerCase()]">
                  {{ l.status }}
                </span>
              </td>
              <td>
                <div v-if="l.status === 'Pending' && isAdminOrHR" class="action-btn-group">
                  <button @click="openReviewModal(l, 'Approved')" class="btn-approve" title="Approve Leave">✓</button>
                  <button @click="openReviewModal(l, 'Disapproved')" class="btn-reject" title="Disapprove Leave">✕</button>
                </div>
                <span v-else class="text-muted-sm">{{ l.reviewed_by_name ? `by ${l.reviewed_by_name}` : '—' }}</span>
              </td>
            </tr>
            <tr v-if="!attendanceStore.leaves.length">
              <td colspan="7" class="no-data">No leave applications filed yet.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Apply for Leave Modal -->
    <div v-if="showApplyModal" class="modal-backdrop" @click.self="showApplyModal = false">
      <div class="modal-card glass-panel">
        <div class="modal-header">
          <h3>CS Form No. 6 — Application for Leave</h3>
          <button @click="showApplyModal = false" class="btn-close">✕</button>
        </div>
        <form @submit.prevent="submitLeaveApplication">
          <div class="modal-body">
            <div class="field">
              <label>Type of Leave *</label>
              <select v-model="leaveForm.leave_type" required>
                <option value="Vacation Leave">Vacation Leave (Sec. 51, Rule XVI)</option>
                <option value="Mandatory / Forced Leave">Mandatory / Forced Leave (Sec. 25, Rule XVI)</option>
                <option value="Sick Leave">Sick Leave (Sec. 43, Rule XVI)</option>
                <option value="Special Privilege Leave (SPL)">Special Privilege Leave (Rule XVI, Sec. 21)</option>
                <option value="Solo Parent Leave">Solo Parent Leave (RA 8972 / RA 11861)</option>
                <option value="Maternity Leave">Maternity Leave (RA 11210)</option>
                <option value="Paternity Leave">Paternity Leave (RA 8187)</option>
                <option value="Study Leave">Study Leave (Sec. 68, Rule XVI)</option>
                <option value="Others">Others</option>
              </select>
            </div>

            <div class="form-grid-2">
              <div class="field">
                <label>Start Date *</label>
                <input v-model="leaveForm.start_date" type="date" required @change="calculateDays" />
              </div>
              <div class="field">
                <label>End Date *</label>
                <input v-model="leaveForm.end_date" type="date" required @change="calculateDays" />
              </div>
            </div>

            <div class="field">
              <label>Number of Working Days Applied *</label>
              <input v-model="leaveForm.days_applied" type="number" step="0.5" min="0.5" required />
            </div>

            <div class="field">
              <label>Details / Justification of Leave *</label>
              <textarea v-model="leaveForm.reason" rows="3" required placeholder="Specify details of leave application..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="showApplyModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-primary-peach" :disabled="isSubmittingLeave">
              Submit Application
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Review Leave Modal (Approve / Disapprove) -->
    <div v-if="showReviewModal" class="modal-backdrop" @click.self="showReviewModal = false">
      <div class="modal-card glass-panel">
        <div class="modal-header">
          <h3>{{ reviewAction }} Leave Application</h3>
          <button @click="showReviewModal = false" class="btn-close">✕</button>
        </div>
        <form @submit.prevent="confirmReview">
          <div class="modal-body">
            <p class="review-meta-text">
              Applicant: <strong>{{ activeLeaveToReview?.teacher_name }}</strong><br />
              Leave Type: <strong>{{ activeLeaveToReview?.leave_type }}</strong> ({{ activeLeaveToReview?.days_applied }} days)
            </p>
            <div class="field mt-3">
              <label>Administrative Remarks / Endorsement:</label>
              <textarea v-model="reviewRemarks" rows="3" placeholder="Enter remarks or conditions for approval/disapproval..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="showReviewModal = false" class="btn-cancel">Cancel</button>
            <button
              type="submit"
              :class="reviewAction === 'Approved' ? 'btn-approve-confirm' : 'btn-reject-confirm'"
            >
              Confirm {{ reviewAction }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useAttendanceStore } from '@/stores/attendance'
import { usePDSStore } from '@/stores/pds'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import notify from '@/utils/notify'

const attendanceStore = useAttendanceStore()
const pdsStore = usePDSStore()
const authStore = useAuthStore()

const activeTab = ref('dtr')
const teachersList = ref([])
const selectedTeacherId = ref(null)

// Current Date & Clock State
const now = new Date()
const currentMonth = ref(now.getMonth() + 1)
const currentYear = ref(now.getFullYear())
const clockTimer = ref(null)
const currentTime = ref(new Date())

// Modals
const showApplyModal = ref(false)
const isSubmittingLeave = ref(false)
const leaveForm = ref({
  leave_type: 'Vacation Leave',
  start_date: '',
  end_date: '',
  days_applied: 1,
  reason: ''
})

const showReviewModal = ref(false)
const activeLeaveToReview = ref(null)
const reviewAction = ref('Approved')
const reviewRemarks = ref('')

const isAdminOrHR = computed(() => {
  return authStore.user?.is_staff || ['admin', 'hr'].includes(authStore.user?.role)
})

const todayRecord = computed(() => attendanceStore.todayStatus?.record)

const currentTeacherBalance = computed(() => {
  if (!attendanceStore.balances.length) return null
  return attendanceStore.balances.find(b => b.teacher === selectedTeacherId.value) || attendanceStore.balances[0]
})

const currentTimeFormatted = computed(() => {
  return currentTime.value.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  })
})

const currentDateFormatted = computed(() => {
  return currentTime.value.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  })
})

const currentMonthName = computed(() => {
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
  return months[currentMonth.value - 1]
})

onMounted(async () => {
  // Start clock timer
  clockTimer.value = setInterval(() => {
    currentTime.value = new Date()
  }, 1000)

  // Load all registered users / faculty for selector
  let list = []
  try {
    if (attendanceStore && typeof attendanceStore.fetchFacultyList === 'function') {
      list = await attendanceStore.fetchFacultyList()
    } else {
      const res = await api.get('/attendance/records/faculty_list/')
      list = res.data
    }
  } catch (err) {
    console.warn('Attendance faculty list fetch fallback:', err)
  }

  if (!list || !list.length) {
    list = (await pdsStore.fetchTeachers()) || []
  }
  teachersList.value = list

  // Initialize selected teacher: prioritize current logged in user's profile
  if (authStore.user?.teacher_profile) {
    selectedTeacherId.value = authStore.user.teacher_profile.id
  } else if (teachersList.value.length > 0) {
    const myEntry = teachersList.value.find(t => t.user_id === authStore.user?.id || t.username === authStore.user?.username)
    selectedTeacherId.value = myEntry ? myEntry.id : teachersList.value[0].id
  }

  await loadAllData()
})

onBeforeUnmount(() => {
  if (clockTimer.value) clearInterval(clockTimer.value)
})

const loadAllData = async () => {
  await Promise.all([
    attendanceStore.fetchTodayStatus(selectedTeacherId.value),
    attendanceStore.fetchMonthlyDTR(selectedTeacherId.value, currentMonth.value, currentYear.value),
    attendanceStore.fetchAttendanceStats(),
    attendanceStore.fetchLeaves(),
    attendanceStore.fetchBalances()
  ])
}

const handleTeacherChange = async () => {
  await loadAllData()
}

const changeMonth = async (direction) => {
  let m = currentMonth.value + direction
  let y = currentYear.value
  if (m > 12) {
    m = 1
    y += 1
  } else if (m < 1) {
    m = 12
    y -= 1
  }
  currentMonth.value = m
  currentYear.value = y
  await attendanceStore.fetchMonthlyDTR(selectedTeacherId.value, m, y)
}

const handlePunch = async (punchType) => {
  try {
    const res = await attendanceStore.clockPunch(punchType, selectedTeacherId.value)
    notify.toast(res.message, 'success')
    await loadAllData()
  } catch (e) {
    notify.error('Punch failed. Please check network/server status.')
  }
}

const hasPunched = (punchField) => {
  return !!todayRecord.value?.[punchField]
}

const getPunchTime = (punchField) => {
  const val = todayRecord.value?.[punchField]
  if (!val) return null
  const [h, m] = val.split(':')
  const hour = parseInt(h, 10)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const displayH = hour % 12 || 12
  return `${String(displayH).padStart(2, '0')}:${m} ${ampm}`
}

const getStatusClass = (statusStr) => {
  if (!statusStr) return ''
  const s = statusStr.toLowerCase()
  if (s.includes('present')) return 'present'
  if (s.includes('late')) return 'late'
  if (s.includes('leave')) return 'leave'
  if (s.includes('weekend')) return 'weekend'
  if (s.includes('absent')) return 'absent'
  return 'default'
}

const isDownloadingExcel = ref(false)
const isDownloadingPdf = ref(false)

const printDTR = () => {
  window.print()
}

const downloadDTRExcel = async () => {
  if (!selectedTeacherId.value) return
  isDownloadingExcel.value = true
  try {
    const res = await api.get('/attendance/records/export_excel/', {
      params: {
        teacher: selectedTeacherId.value,
        month: currentMonth.value,
        year: currentYear.value,
      },
      responseType: 'blob',
    })
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const teacherName = (attendanceStore.monthlyDTR?.teacher?.name || 'Faculty').replace(/\s+/g, '_')
    link.setAttribute('download', `DTR_${teacherName}_${currentMonthName.value}_${currentYear.value}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    notify.success('CS Form 48 Excel downloaded successfully!')
  } catch (err) {
    console.error('Failed to download DTR Excel:', err)
    notify.error('Failed to download DTR Excel.')
  } finally {
    isDownloadingExcel.value = false
  }
}

const downloadDTRPdf = async () => {
  if (!selectedTeacherId.value) return
  isDownloadingPdf.value = true
  try {
    const res = await api.get('/attendance/records/export_pdf/', {
      params: {
        teacher: selectedTeacherId.value,
        month: currentMonth.value,
        year: currentYear.value,
      },
      responseType: 'blob',
    })
    const blob = new Blob([res.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const teacherName = (attendanceStore.monthlyDTR?.teacher?.name || 'Faculty').replace(/\s+/g, '_')
    link.setAttribute('download', `DTR_${teacherName}_${currentMonthName.value}_${currentYear.value}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    notify.success('CS Form 48 PDF downloaded successfully!')
  } catch (err) {
    console.error('Failed to download DTR PDF:', err)
    notify.error('Failed to download DTR PDF.')
  } finally {
    isDownloadingPdf.value = false
  }
}

// Leave application logic
const openApplyModal = () => {
  leaveForm.value = {
    leave_type: 'Vacation Leave',
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    days_applied: 1,
    reason: ''
  }
  showApplyModal.value = true
}

const calculateDays = () => {
  if (leaveForm.value.start_date && leaveForm.value.end_date) {
    const start = new Date(leaveForm.value.start_date)
    const end = new Date(leaveForm.value.end_date)
    const diffTime = end - start
    if (diffTime >= 0) {
      const days = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1
      leaveForm.value.days_applied = days
    }
  }
}

const submitLeaveApplication = async () => {
  isSubmittingLeave.value = true
  try {
    const payload = {
      ...leaveForm.value,
      teacher: selectedTeacherId.value
    }
    await attendanceStore.submitLeave(payload)
    showApplyModal.value = false
    notify.success('Application for leave submitted successfully for review.')
    await loadAllData()
  } catch (err) {
    notify.error('Failed to submit leave. Please review form entries.')
  } finally {
    isSubmittingLeave.value = false
  }
}

const openReviewModal = (leave, actionType) => {
  activeLeaveToReview.value = leave
  reviewAction.value = actionType
  reviewRemarks.value = actionType === 'Approved' ? 'Endorsed per CSC guidelines.' : 'Requires proper certificate/documentation.'
  showReviewModal.value = true
}

const confirmReview = async () => {
  if (!activeLeaveToReview.value) return
  try {
    await attendanceStore.reviewLeave(
      activeLeaveToReview.value.id,
      reviewAction.value,
      reviewRemarks.value
    )
    showReviewModal.value = false
    notify.success(`Leave application marked ${reviewAction.value.toLowerCase()}.`)
    await loadAllData()
  } catch (e) {
    notify.error('Failed to update leave review.')
  }
}
</script>

<style scoped>
.attendance-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Page Header */
.page-header {
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.badge-csc {
  background: var(--accent-gold-subtle);
  color: var(--accent-gold);
  border: 1px solid rgba(254, 203, 144, 0.3);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-top: 0.25rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.teacher-select-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.teacher-select-box label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.teacher-select-box select {
  width: auto;
  min-width: 220px;
  padding: 0.45rem 0.75rem;
}

.btn-print {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--accent-gold);
  font-weight: 600;
  padding: 0.6rem 1.1rem;
  border-radius: var(--radius-sm);
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-print:hover {
  background: var(--accent-gold-subtle);
  border-color: var(--accent-gold);
}

.btn-excel {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #34d399;
  font-weight: 600;
  padding: 0.6rem 1.1rem;
  border-radius: var(--radius-sm);
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-excel:hover:not(:disabled) {
  background: rgba(16, 185, 129, 0.25);
  border-color: #34d399;
  transform: translateY(-1px);
}

.btn-pdf {
  background: rgba(244, 63, 94, 0.15);
  border: 1px solid rgba(244, 63, 94, 0.4);
  color: #fda4af;
  font-weight: 600;
  padding: 0.6rem 1.1rem;
  border-radius: var(--radius-sm);
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-pdf:hover:not(:disabled) {
  background: rgba(244, 63, 94, 0.25);
  border-color: #f43f5e;
  transform: translateY(-1px);
}

.btn-excel:disabled, .btn-pdf:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dtr-export-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: 0.5rem;
}

.btn-export-small {
  padding: 0.35rem 0.75rem !important;
  font-size: 0.8rem !important;
  border-radius: 6px !important;
}

/* Punch & Schedule Grid */
.punch-and-schedule-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 1024px) {
  .punch-and-schedule-grid {
    grid-template-columns: 1fr;
  }
}

.clock-card {
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.clock-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.clock-icon {
  font-size: 1.5rem;
}

.clock-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.current-date-text {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.digital-clock-display {
  font-family: 'Plus Jakarta Sans', monospace;
  font-size: 3.25rem;
  font-weight: 800;
  color: var(--accent-gold);
  text-shadow: 0 0 20px rgba(254, 203, 144, 0.35);
  margin: 1rem 0;
  letter-spacing: 2px;
}

.punch-buttons-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

@media (max-width: 768px) {
  .punch-buttons-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.btn-punch {
  background: rgba(36, 26, 18, 0.9);
  border: 1px solid var(--border-color);
  padding: 1rem 0.75rem;
  border-radius: var(--radius-md);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  transition: all 0.25s ease;
}

.btn-punch:hover:not(:disabled) {
  border-color: var(--accent-gold);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(254, 203, 144, 0.2);
}

.btn-punch.punched {
  border-color: rgba(16, 185, 129, 0.5);
  background: rgba(16, 185, 129, 0.08);
  cursor: default;
}

.punch-slot-title {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
}

.punch-time-val {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.punch-action-label {
  font-size: 0.75rem;
  color: var(--accent-gold);
  font-weight: 600;
}

.punched-badge {
  font-size: 0.75rem;
  color: #34d399;
  font-weight: 700;
}

/* Shift Info Card */
.shift-info-card {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.shift-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.shift-card-header h3 {
  font-size: 1.1rem;
}

.badge-status-tag {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
}

.shift-details-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.shift-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  padding-bottom: 0.4rem;
}

.shift-label {
  color: var(--text-secondary);
}

.grace-badge {
  background: var(--accent-gold-subtle);
  color: var(--accent-gold);
  padding: 0.1rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.hours-val {
  color: var(--accent-gold);
}

.today-status-banner {
  margin-top: 1rem;
  padding: 0.85rem 1rem;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(254, 203, 144, 0.1);
  border: 1px solid rgba(254, 203, 144, 0.25);
}

.today-status-banner.late {
  background: rgba(244, 63, 94, 0.12);
  border-color: rgba(244, 63, 94, 0.3);
}

.sub-alert {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Stats KPI Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

@media (max-width: 992px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.kpi-card {
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.kpi-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.kpi-icon-wrap.present { background: rgba(16, 185, 129, 0.15); }
.kpi-icon-wrap.rate { background: var(--accent-gold-subtle); }
.kpi-icon-wrap.tardy { background: rgba(249, 115, 22, 0.15); }
.kpi-icon-wrap.leave { background: rgba(59, 130, 246, 0.15); }

.kpi-title {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 500;
}

.kpi-val {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.2;
}

.kpi-sub {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

/* Module Tab Bar */
.module-tab-bar {
  display: flex;
  padding: 0.4rem;
  gap: 0.5rem;
}

.tab-btn {
  flex: 1;
  padding: 0.85rem 1.25rem;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: var(--bg-surface-elevated);
  color: var(--text-primary);
}

.tab-btn.active {
  background: linear-gradient(135deg, #fecb90, #f8b668);
  color: #26150a;
  font-weight: 700;
}

/* DTR View Wrapper */
.dtr-view-wrapper {
  padding: 1.5rem;
}

.dtr-controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}

.month-selector-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-month-nav {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-month-nav:hover {
  border-color: var(--accent-gold);
  color: var(--accent-gold);
}

.current-month-display {
  text-align: center;
}

.current-month-display strong {
  display: block;
  font-size: 1.2rem;
  color: var(--accent-gold);
}

.current-month-display small {
  color: var(--text-muted);
}

.monthly-summary-badges {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.sum-pill {
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  font-size: 0.8rem;
  display: flex;
  gap: 0.4rem;
  align-items: center;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
}

.sum-pill.present strong { color: #34d399; }
.sum-pill.tardy strong { color: #fb923c; }
.sum-pill.undertime strong { color: #f43f5e; }
.sum-pill.hours strong { color: var(--accent-gold); }

/* Printable Header & Footer */
.printable-form48-header {
  text-align: center;
  margin-bottom: 1.25rem;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0.75rem;
}

.form48-gov-title {
  font-size: 0.8rem;
  letter-spacing: 1px;
  color: var(--text-muted);
  font-weight: 700;
}

.printable-form48-header h2 {
  font-size: 1.35rem;
  color: var(--accent-gold);
  letter-spacing: 1.5px;
  margin: 0.25rem 0;
}

.form48-name-line {
  margin: 0.5rem 0;
}

.form48-name-line strong {
  font-size: 1.15rem;
  text-decoration: underline;
}

.form48-name-line .caption {
  font-size: 0.75rem;
  color: var(--text-muted);
  display: block;
}

.form48-meta-line {
  display: flex;
  justify-content: space-around;
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.4rem;
}

/* DTR Table */
.dtr-csc-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.dtr-csc-table th, .dtr-csc-table td {
  border: 1px solid var(--border-color);
  padding: 0.45rem 0.6rem;
  text-align: center;
}

.dtr-csc-table thead th {
  background: var(--bg-surface-elevated);
  color: var(--accent-gold);
  font-weight: 700;
}

.col-day { width: 75px; }
.cell-day strong { display: block; font-size: 0.95rem; }
.day-abbr { font-size: 0.7rem; color: var(--text-muted); }

.weekend-row {
  background: rgba(255, 255, 255, 0.02);
  color: var(--text-muted);
}

.leave-row {
  background: rgba(59, 130, 246, 0.08);
}

.tardy-row {
  background: rgba(249, 115, 22, 0.06);
}

.total-row {
  background: var(--bg-surface-elevated);
  font-weight: 700;
}

.dtr-status-pill {
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 700;
}

.dtr-status-pill.present { background: rgba(16, 185, 129, 0.2); color: #34d399; }
.dtr-status-pill.late { background: rgba(249, 115, 22, 0.2); color: #fb923c; }
.dtr-status-pill.leave { background: rgba(59, 130, 246, 0.2); color: #93c5fd; }
.dtr-status-pill.weekend { background: rgba(255, 255, 255, 0.05); color: var(--text-muted); }
.dtr-status-pill.absent { background: rgba(244, 63, 94, 0.2); color: #fda4af; }

.printable-form48-footer {
  margin-top: 1.5rem;
  padding-top: 1rem;
}

.cert-text {
  font-size: 0.8rem;
  font-style: italic;
  text-align: justify;
  color: var(--text-secondary);
}

.sig-lines-row {
  display: flex;
  justify-content: space-between;
  margin-top: 2.5rem;
  padding: 0 3rem;
}

.sig-block {
  text-align: center;
  width: 250px;
}

.sig-block .line {
  border-bottom: 1px solid var(--text-primary);
  margin-bottom: 0.4rem;
}

.sig-block span {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Leave Management Tab */
.leave-credits-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  .leave-credits-grid {
    grid-template-columns: 1fr;
  }
}

.credit-card {
  padding: 1.25rem;
}

.credit-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.credit-icon {
  font-size: 1.8rem;
}

.credit-header h4 {
  font-size: 1rem;
  margin-bottom: 0.15rem;
}

.credit-header small {
  color: var(--text-muted);
}

.credit-balance-row {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin: 1rem 0 0.5rem;
}

.balance-num {
  font-size: 2.25rem;
  font-weight: 800;
  color: var(--accent-gold);
}

.days-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.credit-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  overflow: hidden;
}

.credit-fill {
  height: 100%;
  background: var(--accent-gold);
  border-radius: 4px;
}

.credit-fill.sick { background: #10b981; }
.credit-fill.spl { background: #3b82f6; }

.leave-toolbar {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.btn-primary-peach {
  background: linear-gradient(135deg, #fecb90, #f8b668);
  color: #26150a;
  font-weight: 700;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-sm);
  box-shadow: 0 4px 14px rgba(254, 203, 144, 0.3);
}

.btn-primary-peach:hover:not(:disabled) {
  transform: translateY(-1px);
}

.leave-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.leave-table th, .leave-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
}

.leave-table th {
  background: var(--bg-surface-elevated);
  color: var(--accent-gold);
}

.leave-type-pill {
  background: var(--accent-gold-subtle);
  color: var(--accent-gold);
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.reason-cell {
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-badge {
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-badge.pending { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.status-badge.approved { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.status-badge.disapproved { background: rgba(244, 63, 94, 0.15); color: #fda4af; }

.action-btn-group {
  display: flex;
  gap: 0.4rem;
}

.btn-approve {
  background: #10b981;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 4px;
}

.btn-reject {
  background: #f43f5e;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 4px;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-card {
  width: 90%;
  max-width: 520px;
  padding: 1.5rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.btn-close {
  background: transparent;
  color: var(--text-muted);
  font-size: 1.1rem;
}

.form-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.35rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.btn-cancel {
  background: var(--bg-surface-elevated);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.65rem 1.2rem;
  border-radius: var(--radius-sm);
}

.btn-approve-confirm {
  background: #10b981;
  color: white;
  font-weight: 700;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-sm);
}

.btn-reject-confirm {
  background: #f43f5e;
  color: white;
  font-weight: 700;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-sm);
}

/* Print Rules */
@media print {
  body {
    background: white !important;
    color: black !important;
  }
  .page-header, .punch-and-schedule-grid, .stats-grid, .module-tab-bar, .dtr-controls-bar, .sidebar {
    display: none !important;
  }
  .dtr-view-wrapper {
    background: white !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
  }
  .dtr-csc-table th, .dtr-csc-table td {
    border-color: black !important;
    color: black !important;
  }
}
</style>
