<template>
  <div class="users-page">
    <div class="toolbar glass-panel">
      <div class="title-area">
        <h3>User Accounts & Security Roles</h3>
        <p class="subtitle">Manage Administrators, HR Officers, and Faculty Login credentials</p>
      </div>
      <button @click="showModal = true" class="btn-primary">
        + Create Account
      </button>
    </div>

    <!-- Table -->
    <div class="table-card glass-panel">
      <table class="data-table">
        <thead>
          <tr>
            <th>Full Name</th>
            <th>Username</th>
            <th>Email</th>
            <th>Assigned Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td><strong>{{ u.full_name }}</strong></td>
            <td>{{ u.username }}</td>
            <td>{{ u.email }}</td>
            <td>
              <span :class="['role-pill', u.role]">
                {{ u.role_display }}
              </span>
            </td>
            <td>
              <span :class="['status-dot', u.is_active ? 'active' : 'inactive']"></span>
              {{ u.is_active ? 'Active' : 'Disabled' }}
            </td>
            <td class="action-cell">
              <button
                @click="openEditUser(u)"
                class="btn-edit-user"
                title="Edit User Profile"
              >
                ✏️ Edit
              </button>
              <button
                v-if="u.id !== authStore.user?.id"
                @click="toggleUser(u)"
                class="btn-toggle"
              >
                {{ u.is_active ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create User Modal -->
    <div v-if="showModal" class="modal-backdrop">
      <div class="modal-card glass-panel">
        <h3>New User Account</h3>
        <p class="modal-sub">Create access credentials and assign system permissions</p>

        <form @submit.prevent="createUser">
          <div class="field-row">
            <div class="field">
              <label>First Name</label>
              <input v-model="newUser.first_name" required />
            </div>
            <div class="field">
              <label>Last Name</label>
              <input v-model="newUser.last_name" required />
            </div>
          </div>

          <div class="field">
            <label>Username</label>
            <input v-model="newUser.username" required />
          </div>

          <div class="field">
            <label>Email Address</label>
            <input v-model="newUser.email" type="email" required />
          </div>

          <div class="field">
            <label>Role</label>
            <select v-model="newUser.role" required>
              <option value="teacher">Teacher</option>
              <option value="hr">HR Officer</option>
              <option value="admin">Administrator</option>
            </select>
          </div>

          <div class="field-row">
            <div class="field">
              <label>Password</label>
              <input v-model="newUser.password" type="password" required />
            </div>
            <div class="field">
              <label>Confirm Password</label>
              <input v-model="newUser.password2" type="password" required />
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit">Create Account</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit User Profile Modal -->
    <UserProfileModal
      :isOpen="showEditModal"
      :targetUser="userToEdit"
      @close="showEditModal = false"
      @saved="onUserUpdated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import UserProfileModal from '@/components/UserProfileModal.vue'
import api from '@/api'
import notify from '@/utils/notify'

const authStore = useAuthStore()
const users = ref([])
const showModal = ref(false)
const showEditModal = ref(false)
const userToEdit = ref(null)

const openEditUser = async (u) => {
  try {
    const res = await api.get(`/auth/users/${u.id}/`)
    userToEdit.value = res.data
  } catch (err) {
    userToEdit.value = { ...u }
  }
  showEditModal.value = true
}

const onUserUpdated = async () => {
  await loadUsers()
}

const newUser = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  role: 'teacher',
  password: '',
  password2: ''
})

const loadUsers = async () => {
  try {
    const res = await api.get('/auth/users/')
    users.value = res.data.results || res.data
  } catch (err) {
    console.error('Failed to load users', err)
  }
}

const createUser = async () => {
  try {
    await api.post('/auth/users/', newUser)
    showModal.value = false
    Object.assign(newUser, {
      username: '', email: '', first_name: '', last_name: '',
      role: 'teacher', password: '', password2: ''
    })
    notify.success('User account created successfully!')
    await loadUsers()
  } catch (err) {
    notify.error(err.response?.data?.error || JSON.stringify(err.response?.data) || 'Failed to create user')
  }
}

const toggleUser = async (u) => {
  const willDeactivate = u.is_active
  const confirmed = await notify.confirm({
    title: willDeactivate ? 'Deactivate User?' : 'Activate User?',
    text: `Are you sure you want to ${willDeactivate ? 'deactivate' : 'activate'} account for ${u.full_name}?`,
    confirmButtonText: willDeactivate ? 'Yes, Deactivate' : 'Yes, Activate'
  })
  if (!confirmed) return
  try {
    await api.patch(`/auth/users/${u.id}/`, { is_active: !u.is_active })
    u.is_active = !u.is_active
    notify.toast(`User ${u.is_active ? 'activated' : 'deactivated'} successfully.`, 'info')
  } catch (err) {
    notify.error('Failed to update user status.')
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.users-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.toolbar {
  padding: 1.25rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subtitle {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.btn-primary {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  padding: 0.65rem 1.25rem;
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
  color: #475569;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #f8fafc;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
  color: #0f172a;
}

.data-table tr:hover td {
  background: #f8fafc;
}

.role-pill {
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-weight: 700;
}

.role-pill.admin { background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }
.role-pill.hr { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
.role-pill.teacher { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
}
.status-dot.active { background: #059669; }
.status-dot.inactive { background: #dc2626; }

.action-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-edit-user {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
  padding: 0.35rem 0.7rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit-user:hover {
  background: #1d4ed8;
  color: #ffffff;
  border-color: #1d4ed8;
}

.btn-toggle {
  background: var(--bg-surface-elevated);
  color: var(--text-secondary);
  padding: 0.35rem 0.65rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  border: 1px solid var(--border-color);
  cursor: pointer;
}

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

.modal-sub {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 0.4rem;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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
}

.btn-submit {
  background: var(--accent-gold);
  color: var(--text-on-accent, #24120a);
  font-weight: 700;
  padding: 0.5rem 1.25rem;
  border-radius: var(--radius-sm);
}
</style>
