<template>
  <div class="dashboard-grid">
    <!-- Stat Cards -->
    <div class="stats-row">
      <div class="stat-card glass-panel">
        <div class="stat-icon gold">👨‍🏫</div>
        <div class="stat-info">
          <h3>{{ pdsStore.stats.total_teachers }}</h3>
          <p>Total Teachers</p>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon green">✅</div>
        <div class="stat-info">
          <h3>{{ pdsStore.stats.complete_pds }}</h3>
          <p>Complete PDS</p>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon red">⏳</div>
        <div class="stat-info">
          <h3>{{ pdsStore.stats.incomplete_pds }}</h3>
          <p>Incomplete Profiles</p>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon blue">🛡️</div>
        <div class="stat-info">
          <h3>{{ pdsStore.stats.total_users }}</h3>
          <p>System Accounts</p>
        </div>
      </div>
    </div>

    <!-- Quick Action / Welcome Banner -->
    <div class="welcome-banner glass-panel">
      <div class="banner-text">
        <h2>Civil Service Commission Form No. 212 (Revised 2026)</h2>
        <p>
          Official Philippine Government Personal Data Sheet profiling system for Faculty & Educators.
          Ensure timely updates of Work Experience, Licensures, and Learning & Development records.
        </p>
        <div class="banner-buttons">
          <router-link v-if="authStore.canManageAll" to="/teachers" class="btn-action">
            Browse All Teachers
          </router-link>
          <router-link v-else to="/profile" class="btn-action">
            Update My CS Form 212
          </router-link>
        </div>
      </div>
      <div class="banner-graphic">📜</div>
    </div>

    <!-- Recent Teachers / Quick View -->
    <div v-if="authStore.canManageAll" class="recent-section glass-panel">
      <div class="section-head">
        <h3>Registered Faculty Profiles</h3>
        <router-link to="/teachers" class="view-all">View All →</router-link>
      </div>

      <div v-if="pdsStore.isLoading" class="loading-state">
        Loading faculty records...
      </div>

      <div v-else-if="!pdsStore.teachers.length" class="empty-state">
        No teacher profiles recorded yet.
      </div>

      <div v-else class="teachers-table-wrap">
        <table class="simple-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Employee ID</th>
              <th>Department</th>
              <th>PDS Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in pdsStore.teachers.slice(0, 5)" :key="t.id">
              <td class="name-cell">
                <span class="user-avatar">👤</span>
                <strong>{{ t.full_name }}</strong>
              </td>
              <td>{{ t.employee_id || 'N/A' }}</td>
              <td>{{ t.department || 'Unassigned' }}</td>
              <td>
                <span :class="['badge-status', t.pds_complete ? 'complete' : 'pending']">
                  {{ t.pds_complete ? 'Complete' : 'Pending' }}
                </span>
              </td>
              <td>
                <router-link :to="`/teachers/${t.id}`" class="btn-table">
                  View PDS
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePDSStore } from '@/stores/pds'

const authStore = useAuthStore()
const pdsStore = usePDSStore()

onMounted(async () => {
  await pdsStore.fetchDashboardStats()
  if (authStore.canManageAll) {
    await pdsStore.fetchTeachers()
  }
})
</script>

<style scoped>
.dashboard-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}

.stat-card {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
}

.stat-icon.gold { background: rgba(245, 158, 11, 0.15); }
.stat-icon.green { background: rgba(16, 185, 129, 0.15); }
.stat-icon.red { background: rgba(244, 63, 94, 0.15); }
.stat-icon.blue { background: rgba(59, 130, 246, 0.15); }

.stat-info h3 {
  font-size: 1.75rem;
  line-height: 1.1;
}

.stat-info p {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.welcome-banner {
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #eff6ff, #f8fafc);
  border: 1px solid #bfdbfe;
  border-left: 5px solid var(--accent-gold);
}

.banner-text h2 {
  font-size: 1.4rem;
  margin-bottom: 0.5rem;
  color: #0f172a;
}

.banner-text p {
  color: #475569;
  max-width: 650px;
  font-size: 0.9rem;
  margin-bottom: 1.25rem;
}

.btn-action {
  display: inline-block;
  background: var(--accent-gold);
  color: #ffffff;
  font-weight: 700;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-sm);
}

.btn-action:hover {
  background: #1d4ed8;
  color: #ffffff;
}

.banner-graphic {
  font-size: 5rem;
  opacity: 0.7;
}

.recent-section {
  padding: 1.5rem;
  background: #ffffff;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.view-all {
  font-size: 0.85rem;
  font-weight: 600;
  color: #2563eb;
}

.simple-table {
  width: 100%;
  border-collapse: collapse;
}

.simple-table th {
  text-align: left;
  font-size: 0.8rem;
  color: #475569;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #f8fafc;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
}

.simple-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
  color: #0f172a;
}

.simple-table tr:hover td {
  background: #f8fafc;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #0f172a;
  font-weight: 600;
}

.badge-status {
  display: inline-block;
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-weight: 700;
}

.badge-status.complete {
  background: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}

.badge-status.pending {
  background: #fffbeb;
  color: #b45309;
  border: 1px solid #fde68a;
}

.btn-table {
  font-size: 0.8rem;
  background: #f8fafc;
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-sm);
  color: #1e293b;
  font-weight: 600;
  border: 1px solid var(--border-color);
}

.btn-table:hover {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
}
</style>
