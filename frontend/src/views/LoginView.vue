<template>
  <div class="login-wrapper">
    <div class="login-card glass-panel">
      <div class="brand-header">
        <div class="seal-icon">🎓</div>
        <h2>Teacher eProfile</h2>
        <p class="subtitle">DepEd & Civil Service Form No. 212 (Rev. 2026)</p>
      </div>

      <div v-if="authStore.error" class="alert-error">
        {{ authStore.error }}
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>Username</label>
          <input
            v-model="username"
            type="text"
            placeholder="Enter username"
            required
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input
            v-model="password"
            type="password"
            placeholder="Enter password"
            required
            autocomplete="current-password"
          />
        </div>

        <button type="submit" class="btn-primary" :disabled="authStore.isLoading">
          <span v-if="authStore.isLoading">Signing in...</span>
          <span v-else>Access Portal</span>
        </button>
      </form>

      <div class="quick-credentials">
        <p class="quick-title">Quick Demo Logins:</p>
        <div class="creds-tags">
          <span @click="fill('admin', 'Admin@123456')">Admin</span>
          <span @click="fill('hr_officer', 'Hr@123456')">HR Officer</span>
          <span @click="fill('teacher1', 'Teacher@123456')">Teacher</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')

const handleLogin = async () => {
  const success = await authStore.login(username.value, password.value)
  if (success) {
    router.push('/')
  }
}

const fill = (u, p) => {
  username.value = u
  password.value = p
}
</script>

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 1.5rem;
}

.login-card {
  width: 100%;
  max-width: 440px;
  padding: 2.5rem;
}

.brand-header {
  text-align: center;
  margin-bottom: 2rem;
}

.seal-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
  filter: drop-shadow(0 0 16px rgba(245, 158, 11, 0.4));
}

.brand-header h2 {
  font-size: 1.75rem;
  background: linear-gradient(135deg, #f8fafc, #f59e0b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.25rem;
}

.subtitle {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.alert-error {
  background: rgba(244, 63, 94, 0.15);
  border: 1px solid var(--accent-rose);
  color: #fda4af;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  margin-bottom: 1.25rem;
  font-size: 0.85rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  font-size: 0.825rem;
  font-weight: 500;
  margin-bottom: 0.4rem;
  color: var(--text-secondary);
}

.btn-primary {
  width: 100%;
  background: linear-gradient(135deg, var(--accent-gold), var(--accent-gold-hover));
  color: var(--text-on-accent, #26150a);
  font-weight: 700;
  font-size: 0.95rem;
  padding: 0.75rem;
  border-radius: var(--radius-sm);
  margin-top: 0.75rem;
  box-shadow: 0 4px 14px rgba(254, 203, 144, 0.35);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(254, 203, 144, 0.5);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.quick-credentials {
  margin-top: 1.75rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-color);
  text-align: center;
}

.quick-title {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.creds-tags {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.creds-tags span {
  font-size: 0.75rem;
  background: var(--bg-surface-elevated);
  padding: 0.35rem 0.65rem;
  border-radius: 20px;
  cursor: pointer;
  color: var(--accent-gold);
  border: 1px solid rgba(245, 158, 11, 0.2);
  transition: all 0.2s ease;
}

.creds-tags span:hover {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
}
</style>
