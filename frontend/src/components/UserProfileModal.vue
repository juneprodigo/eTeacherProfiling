<template>
  <div v-if="isOpen" class="modal-backdrop" @click.self="closeModal">
    <div class="modal-card glass-panel" :class="{ 'admin-mode': isTargetOtherUser }">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-left">
          <div class="avatar-large">
            <img v-if="photoPreview || form.profile_photo_url" :src="photoPreview || form.profile_photo_url" alt="Profile" />
            <span v-else>{{ initials }}</span>
          </div>
          <div>
            <h3>{{ isTargetOtherUser ? `Edit User: ${form.username}` : 'My User Profile' }}</h3>
            <p class="subtitle">{{ isTargetOtherUser ? 'Manage employee access & system information' : 'Update your personal account credentials & employee details' }}</p>
          </div>
        </div>
        <button class="btn-close" @click="closeModal" title="Close">✕</button>
      </div>

      <!-- Navigation Tabs (Only if editing self, or if password change not needed for admin) -->
      <div v-if="!isTargetOtherUser" class="modal-tabs">
        <button
          :class="['tab-btn', { active: activeTab === 'general' }]"
          @click="activeTab = 'general'"
        >
          👤 Account &amp; Employee Info
        </button>
        <button
          :class="['tab-btn', { active: activeTab === 'security' }]"
          @click="activeTab = 'security'"
        >
          🔒 Security &amp; Password
        </button>
      </div>

      <!-- Tab 1: General Info -->
      <div v-show="activeTab === 'general' || isTargetOtherUser" class="tab-content">
        <form @submit.prevent="saveProfile">
          <!-- Profile Photo Upload -->
          <div class="photo-upload-section">
            <div class="photo-box">
              <img v-if="photoPreview || form.profile_photo_url" :src="photoPreview || form.profile_photo_url" class="photo-img" />
              <div v-else class="photo-placeholder">{{ initials }}</div>
            </div>
            <div class="photo-controls">
              <label class="btn-upload">
                📷 Change Photo
                <input type="file" accept="image/*" @change="handlePhotoChange" hidden />
              </label>
              <small class="hint">Recommended: Square format, PNG or JPG (Max 2MB)</small>
            </div>
          </div>

          <div class="form-grid">
            <!-- First Name -->
            <div class="field">
              <label>First Name <span class="required">*</span></label>
              <input v-model="form.first_name" type="text" required placeholder="e.g. Juan" />
            </div>

            <!-- Last Name -->
            <div class="field">
              <label>Last Name <span class="required">*</span></label>
              <input v-model="form.last_name" type="text" required placeholder="e.g. Dela Cruz" />
            </div>

            <!-- Email -->
            <div class="field">
              <label>Email Address <span class="required">*</span></label>
              <input v-model="form.email" type="email" required placeholder="user@deped.gov.ph" />
            </div>

            <!-- Username -->
            <div class="field">
              <label>Username</label>
              <input :value="form.username" type="text" disabled class="input-disabled" />
              <small class="hint">Username cannot be altered</small>
            </div>

            <!-- Role Selection (Editable only by Admin when managing another user) -->
            <div class="field">
              <label>Security Role</label>
              <select
                v-if="isTargetOtherUser && authStore.isAdmin"
                v-model="form.role"
                class="role-select"
              >
                <option value="teacher">Teacher / Faculty</option>
                <option value="hr">HR Officer</option>
                <option value="admin">Administrator</option>
              </select>
              <div v-else class="role-badge-display">
                <span :class="['role-pill', form.role]">
                  {{ form.role_display || (form.role ? form.role.toUpperCase() : 'USER') }}
                </span>
              </div>
            </div>

            <!-- Employee ID -->
            <div class="field">
              <label>Employee ID</label>
              <input v-model="form.employee_id" type="text" placeholder="e.g. DEPED-2026-001" />
            </div>

            <!-- Department -->
            <div class="field">
              <label>Department / Office</label>
              <input v-model="form.department" type="text" placeholder="e.g. Science Department" />
            </div>

            <!-- Position -->
            <div class="field">
              <label>Designation / Position</label>
              <input v-model="form.position" type="text" placeholder="e.g. Master Teacher I" />
            </div>

            <!-- Active Status (Only for Admin editing other user) -->
            <div v-if="isTargetOtherUser && authStore.isAdmin" class="field field-full">
              <label class="checkbox-label">
                <input v-model="form.is_active" type="checkbox" />
                <span>Active Account (Can login and record attendance)</span>
              </label>
            </div>
          </div>

          <div v-if="successMsg" class="alert-success">✓ {{ successMsg }}</div>
          <div v-if="errorMsg" class="alert-error">✕ {{ errorMsg }}</div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-cancel">Cancel</button>
            <button type="submit" :disabled="isSaving" class="btn-submit">
              <span v-if="isSaving">Saving Changes...</span>
              <span v-else>💾 Save Information</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Tab 2: Security & Password (Self Only) -->
      <div v-show="activeTab === 'security' && !isTargetOtherUser" class="tab-content">
        <form @submit.prevent="updatePassword">
          <div class="security-intro">
            <p>Ensure your account remains safe by using a strong password with at least 8 characters, combining uppercase, lowercase, numbers, and symbols.</p>
          </div>

          <div class="form-grid single-col">
            <div class="field">
              <label>Current Password <span class="required">*</span></label>
              <input v-model="pwForm.old_password" type="password" required placeholder="Enter current password" />
            </div>

            <div class="field">
              <label>New Password <span class="required">*</span></label>
              <input v-model="pwForm.new_password" type="password" required minlength="8" placeholder="Enter new strong password" />
            </div>

            <div class="field">
              <label>Confirm New Password <span class="required">*</span></label>
              <input v-model="pwForm.new_password2" type="password" required minlength="8" placeholder="Repeat new password" />
            </div>
          </div>

          <div v-if="pwSuccessMsg" class="alert-success">✓ {{ pwSuccessMsg }}</div>
          <div v-if="pwErrorMsg" class="alert-error">✕ {{ pwErrorMsg }}</div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-cancel">Cancel</button>
            <button type="submit" :disabled="isSavingPw" class="btn-submit">
              <span v-if="isSavingPw">Updating Password...</span>
              <span v-else>🔑 Change Password</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  // If targetUser is provided, we are editing that specific user (Admin mode)
  targetUser: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'saved'])

const authStore = useAuthStore()

const activeTab = ref('general')
const isSaving = ref(false)
const isSavingPw = ref(false)
const successMsg = ref('')
const errorMsg = ref('')
const pwSuccessMsg = ref('')
const pwErrorMsg = ref('')

const photoFile = ref(null)
const photoPreview = ref(null)

const isTargetOtherUser = computed(() => {
  return props.targetUser && props.targetUser.id !== authStore.user?.id
})

const form = ref({
  id: null,
  first_name: '',
  last_name: '',
  email: '',
  username: '',
  role: 'teacher',
  role_display: '',
  profile_photo_url: null,
  employee_id: '',
  department: '',
  position: '',
  is_active: true
})

const pwForm = ref({
  old_password: '',
  new_password: '',
  new_password2: ''
})

const initials = computed(() => {
  const f = form.value.first_name || ''
  const l = form.value.last_name || ''
  if (!f && !l) return 'U'
  return `${f.charAt(0)}${l.charAt(0)}`.toUpperCase()
})

const populateForm = () => {
  const src = props.targetUser || authStore.user || {}
  form.value = {
    id: src.id || null,
    first_name: src.first_name || '',
    last_name: src.last_name || '',
    email: src.email || '',
    username: src.username || '',
    role: src.role || 'teacher',
    role_display: src.role_display || (src.role === 'admin' ? 'Administrator' : src.role === 'hr' ? 'HR Officer' : 'Teacher'),
    profile_photo_url: src.profile_photo_url || src.profile_photo || null,
    employee_id: src.employee_id || '',
    department: src.department || '',
    position: src.position || '',
    is_active: src.is_active !== undefined ? src.is_active : true
  }
  photoFile.value = null
  photoPreview.value = null
  successMsg.value = ''
  errorMsg.value = ''
  pwSuccessMsg.value = ''
  pwErrorMsg.value = ''
  activeTab.value = 'general'
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    populateForm()
  }
})

watch(() => props.targetUser, () => {
  if (props.isOpen) {
    populateForm()
  }
})

const handlePhotoChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    errorMsg.value = 'Photo file size exceeds 2MB limit.'
    return
  }
  photoFile.value = file
  photoPreview.value = URL.createObjectURL(file)
}

const saveProfile = async () => {
  isSaving.value = true
  successMsg.value = ''
  errorMsg.value = ''

  try {
    let payload
    if (photoFile.value) {
      payload = new FormData()
      payload.append('first_name', form.value.first_name)
      payload.append('last_name', form.value.last_name)
      payload.append('email', form.value.email)
      payload.append('employee_id', form.value.employee_id)
      payload.append('department', form.value.department)
      payload.append('position', form.value.position)
      if (isTargetOtherUser.value && authStore.isAdmin) {
        payload.append('role', form.value.role)
        payload.append('is_active', form.value.is_active)
      }
      payload.append('profile_photo', photoFile.value)
    } else {
      payload = {
        first_name: form.value.first_name,
        last_name: form.value.last_name,
        email: form.value.email,
        employee_id: form.value.employee_id,
        department: form.value.department,
        position: form.value.position,
      }
      if (isTargetOtherUser.value && authStore.isAdmin) {
        payload.role = form.value.role
        payload.is_active = form.value.is_active
      }
    }

    let updatedUser
    if (isTargetOtherUser.value) {
      updatedUser = await authStore.updateUser(form.value.id, payload)
    } else {
      updatedUser = await authStore.updateProfile(payload)
    }

    successMsg.value = 'Profile information saved successfully!'
    emit('saved', updatedUser)

    setTimeout(() => {
      if (successMsg.value) {
        closeModal()
      }
    }, 1200)
  } catch (err) {
    const data = err.response?.data
    if (data && typeof data === 'object') {
      const msgs = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
      errorMsg.value = msgs.join(' | ')
    } else {
      errorMsg.value = 'Failed to update profile. Please try again.'
    }
  } finally {
    isSaving.value = false
  }
}

const updatePassword = async () => {
  isSavingPw.value = true
  pwSuccessMsg.value = ''
  pwErrorMsg.value = ''

  if (pwForm.value.new_password !== pwForm.value.new_password2) {
    pwErrorMsg.value = 'New passwords do not match.'
    isSavingPw.value = false
    return
  }

  try {
    await authStore.changePassword(
      pwForm.value.old_password,
      pwForm.value.new_password,
      pwForm.value.new_password2
    )
    pwSuccessMsg.value = 'Password changed successfully!'
    pwForm.value = { old_password: '', new_password: '', new_password2: '' }
    setTimeout(() => {
      closeModal()
    }, 1200)
  } catch (err) {
    const data = err.response?.data
    if (data?.error) {
      pwErrorMsg.value = data.error
    } else if (data?.new_password) {
      pwErrorMsg.value = Array.isArray(data.new_password) ? data.new_password.join(' ') : data.new_password
    } else {
      pwErrorMsg.value = 'Password update failed. Please verify your current password.'
    }
  } finally {
    isSavingPw.value = false
  }
}

const closeModal = () => {
  emit('close')
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 6, 4, 0.78);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1.5rem;
  animation: fadeIn 0.2s ease-out;
}

.modal-card {
  width: 100%;
  max-width: 680px;
  background: rgba(26, 18, 12, 0.94);
  border: 1px solid rgba(254, 203, 144, 0.35);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 35px rgba(254, 203, 144, 0.12);
  border-radius: 14px;
  padding: 2rem;
  color: #fff;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(254, 203, 144, 0.15);
  padding-bottom: 1.25rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}

.avatar-large {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fecb90, #f8b668);
  color: #26150a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  font-weight: 700;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(254, 203, 144, 0.3);
}

.avatar-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-header h3 {
  font-size: 1.35rem;
  color: #fecb90;
  margin: 0 0 0.25rem 0;
  font-weight: 600;
}

.modal-header .subtitle {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.65);
  margin: 0;
}

.btn-close {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 1.4rem;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
  transition: color 0.2s;
}

.btn-close:hover {
  color: #fecb90;
}

/* Tabs */
.modal-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(254, 203, 144, 0.15);
  padding-bottom: 0.5rem;
}

.tab-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #fecb90;
  background: rgba(254, 203, 144, 0.08);
}

.tab-btn.active {
  color: #26150a;
  background: #fecb90;
  font-weight: 600;
}

/* Photo Section */
.photo-upload-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(254, 203, 144, 0.04);
  border: 1px dashed rgba(254, 203, 144, 0.25);
  border-radius: 10px;
}

.photo-box {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  overflow: hidden;
  background: rgba(254, 203, 144, 0.15);
  border: 2px solid rgba(254, 203, 144, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  font-size: 1.6rem;
  font-weight: 700;
  color: #fecb90;
}

.btn-upload {
  display: inline-block;
  background: rgba(254, 203, 144, 0.15);
  border: 1px solid rgba(254, 203, 144, 0.35);
  color: #fecb90;
  padding: 0.45rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-upload:hover {
  background: rgba(254, 203, 144, 0.28);
  border-color: #fecb90;
}

.hint {
  display: block;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 0.3rem;
}

/* Forms */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-grid.single-col {
  grid-template-columns: 1fr;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-full {
  grid-column: 1 / -1;
}

.field label {
  font-size: 0.82rem;
  color: #fecb90;
  font-weight: 500;
}

.required {
  color: #ff6b6b;
}

.field input,
.field select {
  background: rgba(15, 10, 7, 0.7);
  border: 1px solid rgba(254, 203, 144, 0.25);
  border-radius: 6px;
  padding: 0.6rem 0.8rem;
  color: #fff;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.field input:focus,
.field select:focus {
  outline: none;
  border-color: #fecb90;
  box-shadow: 0 0 10px rgba(254, 203, 144, 0.25);
}

.input-disabled {
  background: rgba(255, 255, 255, 0.05) !important;
  color: rgba(255, 255, 255, 0.45) !important;
  cursor: not-allowed;
}

.role-pill {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
}

.role-pill.admin {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.role-pill.hr {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.role-pill.teacher {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  cursor: pointer;
  margin-top: 0.5rem;
  font-size: 0.88rem;
}

.checkbox-label input {
  accent-color: #fecb90;
  width: 16px;
  height: 16px;
}

.security-intro {
  background: rgba(254, 203, 144, 0.05);
  border-left: 3px solid #fecb90;
  padding: 0.8rem 1rem;
  border-radius: 4px;
  margin-bottom: 1.25rem;
}

.security-intro p {
  margin: 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

/* Alerts */
.alert-success {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.4);
  color: #4ade80;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-top: 1rem;
  font-size: 0.85rem;
}

.alert-error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #f87171;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-top: 1rem;
  font-size: 0.85rem;
}

/* Actions */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;
  margin-top: 1.75rem;
  padding-top: 1.25rem;
  border-top: 1px solid rgba(254, 203, 144, 0.15);
}

.btn-cancel {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.7);
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.btn-submit {
  background: linear-gradient(135deg, #fecb90, #f8b668);
  border: none;
  color: #26150a;
  padding: 0.6rem 1.4rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(254, 203, 144, 0.3);
}

.btn-submit:hover:not(:disabled) {
  opacity: 0.92;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(254, 203, 144, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}
</style>
