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
        <div class="user-summary">
          <div class="avatar">{{ initials }}</div>
          <div class="user-details">
            <p class="user-name">{{ authStore.fullName }}</p>
            <p class="user-email">{{ authStore.user?.email }}</p>
          </div>
        </div>
        <button @click="logout" class="btn-logout" title="Sign Out">
          🚪 Logout
        </button>
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
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

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
  background: rgba(13, 22, 45, 0.95);
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
  background: var(--accent-gold);
  color: #0b1329;
  font-weight: 700;
}

.sidebar-footer {
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-color);
}

.user-summary {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
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
}

.user-details {
  overflow: hidden;
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

.btn-logout {
  width: 100%;
  background: rgba(244, 63, 94, 0.15);
  color: #fda4af;
  border: 1px solid rgba(244, 63, 94, 0.3);
  padding: 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 600;
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
