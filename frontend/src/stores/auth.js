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
      } catch (err) {
        console.error('Failed to sync profile', err)
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
