import { defineStore } from 'pinia'
import api from '@/api'

export const useLibrariesStore = defineStore('libraries', {
  state: () => ({
    trainings: [],
    voluntaryWorks: [],
    workExperiences: [],
    eligibilities: [],
    isLoading: false,
    error: null,
  }),

  actions: {
    async fetchAllLibraries() {
      this.isLoading = true
      this.error = null
      try {
        const [trRes, volRes, weRes, elRes] = await Promise.all([
          api.get('/libraries/trainings/'),
          api.get('/libraries/voluntary/'),
          api.get('/libraries/work-experiences/'),
          api.get('/libraries/eligibilities/'),
        ])
        this.trainings = trRes.data || []
        this.voluntaryWorks = volRes.data || []
        this.workExperiences = weRes.data || []
        this.eligibilities = elRes.data || []
      } catch (err) {
        console.error('Error fetching libraries:', err)
        this.error = 'Failed to load reference libraries.'
      } finally {
        this.isLoading = false
      }
    },

    async fetchTrainings() {
      try {
        const res = await api.get('/libraries/trainings/')
        this.trainings = res.data || []
      } catch (err) {
        console.error(err)
      }
    },

    async addTraining(payload) {
      const res = await api.post('/libraries/trainings/', payload)
      this.trainings.push(res.data)
      return res.data
    },

    async updateTraining(id, payload) {
      const res = await api.put(`/libraries/trainings/${id}/`, payload)
      const idx = this.trainings.findIndex(t => t.id === id)
      if (idx !== -1) this.trainings[idx] = res.data
      return res.data
    },

    async deleteTraining(id) {
      await api.delete(`/libraries/trainings/${id}/`)
      this.trainings = this.trainings.filter(t => t.id !== id)
    },

    async fetchVoluntary() {
      try {
        const res = await api.get('/libraries/voluntary/')
        this.voluntaryWorks = res.data || []
      } catch (err) {
        console.error(err)
      }
    },

    async addVoluntary(payload) {
      const res = await api.post('/libraries/voluntary/', payload)
      this.voluntaryWorks.push(res.data)
      return res.data
    },

    async updateVoluntary(id, payload) {
      const res = await api.put(`/libraries/voluntary/${id}/`, payload)
      const idx = this.voluntaryWorks.findIndex(v => v.id === id)
      if (idx !== -1) this.voluntaryWorks[idx] = res.data
      return res.data
    },

    async deleteVoluntary(id) {
      await api.delete(`/libraries/voluntary/${id}/`)
      this.voluntaryWorks = this.voluntaryWorks.filter(v => v.id !== id)
    },

    async fetchWorkExperiences() {
      try {
        const res = await api.get('/libraries/work-experiences/')
        this.workExperiences = res.data || []
      } catch (err) {
        console.error(err)
      }
    },

    async addWorkExperience(payload) {
      const res = await api.post('/libraries/work-experiences/', payload)
      this.workExperiences.push(res.data)
      return res.data
    },

    async updateWorkExperience(id, payload) {
      const res = await api.put(`/libraries/work-experiences/${id}/`, payload)
      const idx = this.workExperiences.findIndex(w => w.id === id)
      if (idx !== -1) this.workExperiences[idx] = res.data
      return res.data
    },

    async deleteWorkExperience(id) {
      await api.delete(`/libraries/work-experiences/${id}/`)
      this.workExperiences = this.workExperiences.filter(w => w.id !== id)
    },

    async fetchEligibilities() {
      try {
        const res = await api.get('/libraries/eligibilities/')
        this.eligibilities = res.data || []
      } catch (err) {
        console.error(err)
      }
    },

    async addEligibility(payload) {
      const res = await api.post('/libraries/eligibilities/', payload)
      this.eligibilities.push(res.data)
      return res.data
    },

    async updateEligibility(id, payload) {
      const res = await api.put(`/libraries/eligibilities/${id}/`, payload)
      const idx = this.eligibilities.findIndex(e => e.id === id)
      if (idx !== -1) this.eligibilities[idx] = res.data
      return res.data
    },

    async deleteEligibility(id) {
      await api.delete(`/libraries/eligibilities/${id}/`)
      this.eligibilities = this.eligibilities.filter(e => e.id !== id)
    },
  },
})
