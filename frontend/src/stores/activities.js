import { defineStore } from 'pinia'
import api from '@/api'

export const useActivitiesStore = defineStore('activities', {
  state: () => ({
    activities: [],
    stats: null,
    currentActivity: null,
    loading: false,
    isSaving: false,
    error: null,
  }),

  actions: {
    async fetchActivities(params = {}) {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/activities/', { params })
        this.activities = res.data.results || res.data
        return this.activities
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to load school activities.'
        console.error('Failed to load activities', err)
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchActivityStats() {
      try {
        const res = await api.get('/activities/stats/')
        this.stats = res.data
        return this.stats
      } catch (err) {
        console.error('Failed to load activity statistics', err)
      }
    },

    async fetchActivityDetail(id) {
      this.loading = true
      try {
        const res = await api.get(`/activities/${id}/`)
        this.currentActivity = res.data
        return this.currentActivity
      } catch (err) {
        console.error('Failed to fetch activity detail', err)
        throw err
      } finally {
        this.loading = false
      }
    },

    async createActivity(payload) {
      this.isSaving = true
      try {
        const res = await api.post('/activities/', payload)
        this.activities.unshift(res.data)
        await this.fetchActivityStats()
        return res.data
      } catch (err) {
        console.error('Failed to create activity', err)
        throw err
      } finally {
        this.isSaving = false
      }
    },

    async updateActivity(id, payload) {
      this.isSaving = true
      try {
        const res = await api.patch(`/activities/${id}/`, payload)
        const idx = this.activities.findIndex(a => a.id === id)
        if (idx !== -1) {
          this.activities[idx] = res.data
        }
        if (this.currentActivity?.id === id) {
          this.currentActivity = res.data
        }
        await this.fetchActivityStats()
        return res.data
      } catch (err) {
        console.error('Failed to update activity', err)
        throw err
      } finally {
        this.isSaving = false
      }
    },

    async deleteActivity(id) {
      try {
        await api.delete(`/activities/${id}/`)
        this.activities = this.activities.filter(a => a.id !== id)
        await this.fetchActivityStats()
      } catch (err) {
        console.error('Failed to delete activity', err)
        throw err
      }
    },

    async addParticipant(activityId, { teacher_id, role, attendance_status }) {
      const res = await api.post(`/activities/${activityId}/participants/`, {
        teacher_id,
        role,
        attendance_status
      })
      if (this.currentActivity?.id === activityId) {
        const existingIdx = this.currentActivity.participants.findIndex(p => p.teacher === teacher_id)
        if (existingIdx !== -1) {
          this.currentActivity.participants[existingIdx] = res.data
        } else {
          this.currentActivity.participants.push(res.data)
        }
      }
      return res.data
    },

    async updateParticipant(activityId, participantId, data) {
      const res = await api.patch(`/activities/${activityId}/participants/${participantId}/`, data)
      if (this.currentActivity?.id === activityId) {
        const idx = this.currentActivity.participants.findIndex(p => p.id === participantId)
        if (idx !== -1) {
          this.currentActivity.participants[idx] = res.data
        }
      }
      return res.data
    },

    async removeParticipant(activityId, participantId) {
      await api.delete(`/activities/${activityId}/participants/${participantId}/`)
      if (this.currentActivity?.id === activityId) {
        this.currentActivity.participants = this.currentActivity.participants.filter(
          p => p.id !== participantId
        )
      }
    },

    async batchUpdateAttendance(activityId, updates) {
      const res = await api.post(`/activities/${activityId}/batch-attendance/`, { updates })
      await this.fetchActivityDetail(activityId)
      await this.fetchActivityStats()
      return res.data
    }
  }
})
