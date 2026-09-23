<template>
  <div class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar glass-panel">
      <div class="sidebar-brand">
        <div class="logo-box">🎓</div>
        <div class="brand-text">
          <h3>Teacher eProfile</h3>
          <span class="badge-role">{{ authStore.user?.role?.toUpperCase() }}</span>
        </div>
      </div>

      <nav class="nav-menu">
        <router-link to="/" class="nav-item">
          <span class="icon">📊</span>
          <span>Dashboard</span>
        </router-link>

        <router-link v-if="authStore.canManageAll" to="/teachers" class="nav-item">
          <span class="icon">👨‍🏫</span>
          <span>Teachers Directory</span>
        </router-link>

        <router-link to="/activities" class="nav-item">
          <span class="icon">📅</span>
          <span>School Activities</span>
        </router-link>

        <router-link v-if="authStore.canManageAll" to="/analytics" class="nav-item">
          <span class="icon">📈</span>
          <span>Teacher's Analytics</span>
        </router-link>

        <router-link to="/attendance" class="nav-item">
          <span class="icon">⏱️</span>
          <span>Time & Attendance</span>
        </router-link>

        <router-link v-if="authStore.isTeacher" :to="myProfileRoute" class="nav-item">
          <span class="icon">📝</span>
          <span>My CS Form 212</span>
        </router-link>

        <router-link v-if="authStore.isAdmin" to="/users" class="nav-item">
          <span class="icon">🛡️</span>
          <span>User & Roles</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-summary" @click="showProfileModal = true" role="button" tabindex="0" title="Click to edit profile">
          <div class="avatar">
            <img v-if="authStore.user?.profile_photo_url" :src="authStore.user.profile_photo_url" class="avatar-photo" />
            <span v-else>{{ initials }}</span>
          </div>
          <div class="user-details">
            <p class="user-name">{{ authStore.fullName }}</p>
            <p class="user-email">{{ authStore.user?.email }}</p>
          </div>
          <span class="user-edit-hint" title="Edit Profile">✏️</span>
        </div>
        <div class="footer-btn-group">
          <button @click="showProfileModal = true" class="btn-profile-edit" title="Edit Profile Details">
            ⚙️ Edit Profile
          </button>
          <button @click="logout" class="btn-logout" title="Sign Out">
            🚪 Logout
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="main-content">
      <header class="top-header glass-panel">
        <div class="header-title">
          <h2>{{ pageTitle }}</h2>
        </div>
        <div class="header-actions">
          <span class="school-tag">DepEd / Philippine Civil Service</span>
        </div>
      </header>

      <div class="view-content">
        <router-view />
      </div>
    </main>

    <!-- Global User Profile Edit Modal -->
    <UserProfileModal
      :isOpen="showProfileModal"
      @close="showProfileModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import UserProfileModal from '@/components/UserProfileModal.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const showProfileModal = ref(false)

const myProfileRoute = computed(() => {
  return '/profile'
})

const pageTitle = computed(() => {
  return route.meta?.title || 'Teacher eProfile System'
})

const initials = computed(() => {
  const name = authStore.fullName || ''
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'TP'
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar */
.sidebar {
  width: 280px;
  display: flex;
  flex-direction: column;
  border-radius: 0;
  border-left: none;
  border-top: none;
  border-bottom: none;
  padding: 1.5rem 1rem;
  background: rgba(26, 18, 12, 0.96);
  position: sticky;
  top: 0;
  height: 100vh;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 1.5rem;
}

.logo-box {
  font-size: 2rem;
}

.brand-text h3 {
  font-size: 1.15rem;
  color: var(--text-primary);
}

.badge-role {
  display: inline-block;
  font-size: 0.65rem;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  background: var(--accent-gold-subtle);
  color: var(--accent-gold);
  font-weight: 700;
  letter-spacing: 0.5px;
}

.nav-menu {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: var(--bg-surface-elevated);
  color: var(--text-primary);
}

.nav-item.router-link-active {
  background: linear-gradient(135deg, #fecb90, #f8b668);
  color: #26150a;
  font-weight: 700;
  box-shadow: 0 4px 14px rgba(254, 203, 144, 0.35);
}

.sidebar-footer {
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-color);
}

.user-summary {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  padding: 0.4rem 0.5rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.user-summary:hover {
  background: rgba(254, 203, 144, 0.08);
}

.user-edit-hint {
  margin-left: auto;
  font-size: 0.85rem;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.user-summary:hover .user-edit-hint {
  opacity: 1;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-surface-elevated);
  border: 1px solid var(--accent-gold);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--accent-gold);
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details {
  overflow: hidden;
  flex: 1;
}

.user-name {
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.footer-btn-group {
  display: flex;
  gap: 0.5rem;
}

.btn-profile-edit {
  flex: 1;
  background: rgba(254, 203, 144, 0.12);
  color: #fecb90;
  border: 1px solid rgba(254, 203, 144, 0.3);
  padding: 0.45rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-profile-edit:hover {
  background: rgba(254, 203, 144, 0.24);
  border-color: #fecb90;
}

.btn-logout {
  background: rgba(244, 63, 94, 0.15);
  color: #fda4af;
  border: 1px solid rgba(244, 63, 94, 0.3);
  padding: 0.45rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.btn-logout:hover {
  background: var(--accent-rose);
  color: white;
}

/* Main Area */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.top-header {
  margin: 1rem 1.5rem 0;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: var(--radius-md);
}

.school-tag {
  font-size: 0.8rem;
  background: var(--bg-surface-elevated);
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  color: var(--accent-gold);
  border: 1px solid var(--border-color);
}

.view-content {
  padding: 1.5rem;
  flex: 1;
}
</style>
