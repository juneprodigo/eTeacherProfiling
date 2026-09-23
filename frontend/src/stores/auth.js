import { defineStore } from 'pinia'
import api from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    isLoading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken && !!state.user,
    isAdmin: (state) => state.user?.role === 'admin',
    isHR: (state) => state.user?.role === 'hr',
    isTeacher: (state) => state.user?.role === 'teacher',
    canManageAll: (state) => state.user?.role === 'admin' || state.user?.role === 'hr',
    fullName: (state) => state.user?.full_name || state.user?.username || 'User',
  },

  actions: {
    async login(username, password) {
      this.isLoading = true
      this.error = null
      try {
        const response = await api.post('/auth/login/', { username, password })
        const { access, refresh, user } = response.data

        this.accessToken = access
        this.refreshToken = refresh
        this.user = user

        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)
        localStorage.setItem('user', JSON.stringify(user))

        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'Invalid username or password'
        return false
      } finally {
        this.isLoading = false
      }
    },

    async fetchMe() {
      try {
        const response = await api.get('/auth/me/')
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
        return response.data
      } catch (err) {
        console.error('Failed to sync profile', err)
      }
    },

    async updateProfile(payload) {
      this.isLoading = true
      try {
        const headers = payload instanceof FormData ? { 'Content-Type': 'multipart/form-data' } : {}
        const response = await api.patch('/auth/me/', payload, { headers })
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
        return response.data
      } catch (err) {
        console.error('Failed to update profile', err)
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async changePassword(oldPassword, newPassword, newPassword2) {
      this.isLoading = true
      try {
        const response = await api.post('/auth/change-password/', {
          old_password: oldPassword,
          new_password: newPassword,
          new_password2: newPassword2,
        })
        return response.data
      } catch (err) {
        console.error('Failed to change password', err)
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async updateUser(userId, payload) {
      try {
        const headers = payload instanceof FormData ? { 'Content-Type': 'multipart/form-data' } : {}
        const response = await api.patch(`/auth/users/${userId}/`, payload, { headers })
        if (this.user?.id === userId) {
          this.user = response.data
          localStorage.setItem('user', JSON.stringify(response.data))
        }
        return response.data
      } catch (err) {
        console.error('Failed to update user', err)
        throw err
      }
    },

    logout() {
      if (this.refreshToken) {
        api.post('/auth/logout/', { refresh: this.refreshToken }).catch(() => {})
      }
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }
})
