import { defineStore } from 'pinia'
import api from '@/api'

export const usePDSStore = defineStore('pds', {
  state: () => ({
    teachers: [],
    currentTeacher: null,
    pdsSummary: null,
    stats: {
      total_teachers: 0,
      total_users: 0,
      active_hr_officers: 0,
      complete_pds: 0,
      incomplete_pds: 0,
    },
    isLoading: false,
    isSaving: false,
    error: null,
  }),

  actions: {
    async fetchDashboardStats() {
      try {
        const res = await api.get('/auth/dashboard/stats/')
        this.stats = res.data
      } catch (err) {
        console.error('Failed to load stats', err)
      }
    },

    async fetchTeachers(params = {}) {
      this.isLoading = true
      try {
        const res = await api.get('/teachers/', { params })
        this.teachers = res.data.results || res.data
      } catch (err) {
        this.error = 'Failed to load teachers list'
      } finally {
        this.isLoading = false
      }
    },

    async fetchMyProfile() {
      this.isLoading = true
      try {
        const res = await api.get('/teachers/my-profile/')
        this.pdsSummary = res.data
        return res.data
      } catch (err) {
        this.error = 'Failed to load my profile'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async fetchPDSSummary(teacherId) {
      this.isLoading = true
      try {
        const res = await api.get(`/teachers/${teacherId}/pds-summary/`)
        this.pdsSummary = res.data
        return res.data
      } catch (err) {
        this.error = 'Failed to load PDS data'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    // Save Section I (Personal Info)
    async savePersonalInfo(teacherId, data) {
      this.isSaving = true
      try {
        const res = await api.put(`/teachers/${teacherId}/personal-info/`, data)
        if (this.pdsSummary) this.pdsSummary.personal_info = res.data
        return res.data
      } finally {
        this.isSaving = false
      }
    },

    // Save Section II (Family Background)
    async saveFamilyBackground(teacherId, data) {
      this.isSaving = true
      try {
        const res = await api.put(`/teachers/${teacherId}/family-background/`, data)
        if (this.pdsSummary) this.pdsSummary.family_background = res.data
        return res.data
      } finally {
        this.isSaving = false
      }
    },

    // Sub-items CRUD for Education
    async addEducation(teacherId, data) {
      const res = await api.post(`/teachers/${teacherId}/educational-background/`, data)
      if (this.pdsSummary?.educational_backgrounds) {
        this.pdsSummary.educational_backgrounds.push(res.data)
      }
      return res.data
    },

    async deleteEducation(teacherId, id) {
      await api.delete(`/teachers/${teacherId}/educational-background/${id}/`)
      if (this.pdsSummary?.educational_backgrounds) {
        this.pdsSummary.educational_backgrounds = this.pdsSummary.educational_backgrounds.filter(e => e.id !== id)
      }
    },

    // Sub-items CRUD for Civil Service Eligibility
    async addEligibility(teacherId, data) {
      const res = await api.post(`/teachers/${teacherId}/civil-service-eligibility/`, data)
      if (this.pdsSummary?.civil_service_eligibilities) {
        this.pdsSummary.civil_service_eligibilities.push(res.data)
      }
      return res.data
    },

    async deleteEligibility(teacherId, id) {
      await api.delete(`/teachers/${teacherId}/civil-service-eligibility/${id}/`)
      if (this.pdsSummary?.civil_service_eligibilities) {
        this.pdsSummary.civil_service_eligibilities = this.pdsSummary.civil_service_eligibilities.filter(e => e.id !== id)
      }
    },

    // Sub-items CRUD for Work Experience
    async addWorkExperience(teacherId, data) {
      const res = await api.post(`/teachers/${teacherId}/work-experience/`, data)
      if (this.pdsSummary?.work_experiences) {
        this.pdsSummary.work_experiences.unshift(res.data)
      }
      return res.data
    },

    async deleteWorkExperience(teacherId, id) {
      await api.delete(`/teachers/${teacherId}/work-experience/${id}/`)
      if (this.pdsSummary?.work_experiences) {
        this.pdsSummary.work_experiences = this.pdsSummary.work_experiences.filter(w => w.id !== id)
      }
    },

    // Sub-items CRUD for Learning & Development
    async addLD(teacherId, data) {
      const res = await api.post(`/teachers/${teacherId}/learning-development/`, data)
      if (this.pdsSummary?.learning_developments) {
        this.pdsSummary.learning_developments.unshift(res.data)
      }
      return res.data
    },

    async deleteLD(teacherId, id) {
      await api.delete(`/teachers/${teacherId}/learning-development/${id}/`)
      if (this.pdsSummary?.learning_developments) {
        this.pdsSummary.learning_developments = this.pdsSummary.learning_developments.filter(l => l.id !== id)
      }
    },

    // Save Section VIII (Other Info)
    async saveOtherInfo(teacherId, data) {
      this.isSaving = true
      try {
        const res = await api.put(`/teachers/${teacherId}/other-information/`, data)
        if (this.pdsSummary) this.pdsSummary.other_information = res.data
        return res.data
      } finally {
        this.isSaving = false
      }
    },

    // Save Government Questions (Items 34-40)
    async saveGovQuestions(teacherId, data) {
      this.isSaving = true
      try {
        const res = await api.put(`/teachers/${teacherId}/government-questions/`, data)
        if (this.pdsSummary) this.pdsSummary.government_questions = res.data
        return res.data
      } finally {
        this.isSaving = false
      }
    },

    // Save Declaration (Item 42)
    async saveDeclaration(teacherId, data) {
      this.isSaving = true
      try {
        const res = await api.put(`/teachers/${teacherId}/declaration/`, data)
        if (this.pdsSummary) this.pdsSummary.pds_declaration = res.data
        return res.data
      } finally {
        this.isSaving = false
      }
    },

    // Export PDS as PDF
    async exportPDF(teacherId, teacherName = 'Teacher') {
      try {
        const response = await api.get(`/teachers/${teacherId}/export-pdf/`, {
          responseType: 'blob'
        })
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `CS_Form_212_${teacherName.replace(/\s+/g, '_')}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (err) {
        console.error('PDF export failed', err)
        alert('Could not export PDF. Please check server logs.')
      }
    }
  }
})
