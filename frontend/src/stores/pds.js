import { defineStore } from 'pinia'
import api from '@/api'
import notify from '@/utils/notify'

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
        return this.teachers
      } catch (err) {
        this.error = 'Failed to load teachers list'
        return []
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

    async updateEducation(teacherId, id, data) {
      const res = await api.put(`/teachers/${teacherId}/educational-background/${id}/`, data)
      if (this.pdsSummary?.educational_backgrounds) {
        const idx = this.pdsSummary.educational_backgrounds.findIndex(e => e.id === id)
        if (idx !== -1) this.pdsSummary.educational_backgrounds[idx] = res.data
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

    async updateEligibility(teacherId, id, data) {
      const res = await api.put(`/teachers/${teacherId}/civil-service-eligibility/${id}/`, data)
      if (this.pdsSummary?.civil_service_eligibilities) {
        const idx = this.pdsSummary.civil_service_eligibilities.findIndex(e => e.id === id)
        if (idx !== -1) this.pdsSummary.civil_service_eligibilities[idx] = res.data
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

    async updateWorkExperience(teacherId, id, data) {
      const res = await api.put(`/teachers/${teacherId}/work-experience/${id}/`, data)
      if (this.pdsSummary?.work_experiences) {
        const idx = this.pdsSummary.work_experiences.findIndex(w => w.id === id)
        if (idx !== -1) this.pdsSummary.work_experiences[idx] = res.data
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

    async updateLD(teacherId, id, data) {
      const res = await api.put(`/teachers/${teacherId}/learning-development/${id}/`, data)
      if (this.pdsSummary?.learning_developments) {
        const idx = this.pdsSummary.learning_developments.findIndex(l => l.id === id)
        if (idx !== -1) this.pdsSummary.learning_developments[idx] = res.data
      }
      return res.data
    },

    async deleteLD(teacherId, id) {
      await api.delete(`/teachers/${teacherId}/learning-development/${id}/`)
      if (this.pdsSummary?.learning_developments) {
        this.pdsSummary.learning_developments = this.pdsSummary.learning_developments.filter(l => l.id !== id)
      }
    },

    // Sub-items CRUD for Voluntary Work
    async addVoluntaryWork(teacherId, data) {
      const res = await api.post(`/teachers/${teacherId}/voluntary-work/`, data)
      if (this.pdsSummary?.voluntary_works) {
        this.pdsSummary.voluntary_works.unshift(res.data)
      }
      return res.data
    },

    async updateVoluntaryWork(teacherId, id, data) {
      const res = await api.put(`/teachers/${teacherId}/voluntary-work/${id}/`, data)
      if (this.pdsSummary?.voluntary_works) {
        const idx = this.pdsSummary.voluntary_works.findIndex(v => v.id === id)
        if (idx !== -1) this.pdsSummary.voluntary_works[idx] = res.data
      }
      return res.data
    },

    async deleteVoluntaryWork(teacherId, id) {
      await api.delete(`/teachers/${teacherId}/voluntary-work/${id}/`)
      if (this.pdsSummary?.voluntary_works) {
        this.pdsSummary.voluntary_works = this.pdsSummary.voluntary_works.filter(v => v.id !== id)
      }
    },

    // Sub-items CRUD for References
    async addReference(teacherId, data) {
      const res = await api.post(`/teachers/${teacherId}/references/`, data)
      if (this.pdsSummary?.references) {
        this.pdsSummary.references.push(res.data)
      }
      return res.data
    },

    async updateReference(teacherId, id, data) {
      const res = await api.put(`/teachers/${teacherId}/references/${id}/`, data)
      if (this.pdsSummary?.references) {
        const idx = this.pdsSummary.references.findIndex(r => r.id === id)
        if (idx !== -1) this.pdsSummary.references[idx] = res.data
      }
      return res.data
    },

    async deleteReference(teacherId, id) {
      await api.delete(`/teachers/${teacherId}/references/${id}/`)
      if (this.pdsSummary?.references) {
        this.pdsSummary.references = this.pdsSummary.references.filter(r => r.id !== id)
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

    // Upload Teacher Passport Photo (Item 42)
    async uploadPhoto(teacherId, file) {
      const formData = new FormData()
      formData.append('photo', file)
      const res = await api.patch(`/teachers/${teacherId}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      if (this.pdsSummary) {
        this.pdsSummary.photo_url = res.data.photo_url || res.data.photo
      }
      return res.data
    },

    // Remove Teacher Photo
    async removePhoto(teacherId) {
      const res = await api.patch(`/teachers/${teacherId}/`, { photo: null })
      if (this.pdsSummary) {
        this.pdsSummary.photo_url = null
      }
      return res.data
    },

    // Upload / Attach Teacher E-Signature (Item 42)
    async uploadSignature(teacherId, fileOrBlob) {
      const formData = new FormData()
      if (fileOrBlob instanceof Blob && !(fileOrBlob instanceof File)) {
        formData.append('signature_image', fileOrBlob, 'signature.png')
      } else {
        formData.append('signature_image', fileOrBlob)
      }
      const res = await api.patch(`/teachers/${teacherId}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      if (this.pdsSummary) {
        this.pdsSummary.signature_url = res.data.signature_url || res.data.signature_image
      }
      return res.data
    },

    // Remove Teacher E-Signature
    async removeSignature(teacherId) {
      const res = await api.patch(`/teachers/${teacherId}/`, { signature_image: null })
      if (this.pdsSummary) {
        this.pdsSummary.signature_url = null
      }
      return res.data
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
        window.URL.revokeObjectURL(url)
        notify.toast('PDF file downloaded successfully.', 'success')
      } catch (err) {
        let msg = 'Could not export PDF. Please check server logs.'
        if (err.response?.data instanceof Blob) {
          try {
            const text = await err.response.data.text()
            const json = JSON.parse(text)
            if (json.error) msg = `PDF Export Error: ${json.error}`
            else if (json.detail) msg = `PDF Export Error: ${json.detail}`
          } catch (_) {}
        } else if (err.response?.data?.error) {
          msg = `PDF Export Error: ${err.response.data.error}`
        }
        console.error('PDF export failed', err)
        notify.error(msg)
      }
    },

    // Export PDS as Official Excel (.xlsx)
    async exportExcel(teacherId, teacherName = 'Teacher') {
      try {
        const response = await api.get(`/teachers/${teacherId}/export-excel/`, {
          responseType: 'blob'
        })
        const blob = new Blob([response.data], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `CS_Form_212_Revised_2026_${teacherName.replace(/\s+/g, '_')}.xlsx`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        notify.toast('Official Excel (.xlsx) template downloaded.', 'success')
      } catch (err) {
        let msg = 'Could not download Excel file. Please check server logs.'
        if (err.response?.data instanceof Blob) {
          try {
            const text = await err.response.data.text()
            const json = JSON.parse(text)
            if (json.error) msg = `Excel Export Error: ${json.error}`
            else if (json.detail) msg = `Excel Export Error: ${json.detail}`
          } catch (_) {}
        } else if (err.response?.data?.error) {
          msg = `Excel Export Error: ${err.response.data.error}`
        }
        console.error('Excel export failed', err)
        notify.error(msg)
      }
    }
  }
})
