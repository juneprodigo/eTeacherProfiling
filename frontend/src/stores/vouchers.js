import { defineStore } from 'pinia'
import api from '@/api'

export const useVoucherStore = defineStore('vouchers', {
  state: () => ({
    transactions: [],
    currentVoucher: null,
    libraries: [],
    loading: false,
    error: null,
  }),

  getters: {
    librariesByCategory: (state) => (category) => {
      return state.libraries.filter(l => l.category === category && l.is_active)
    }
  },

  actions: {
    async fetchLibraries() {
      try {
        const response = await api.get('/vouchers/libraries/')
        this.libraries = response.data.results || response.data
      } catch (err) {
        console.error('Failed to fetch voucher libraries:', err)
      }
    },

    async createLibraryItem(data) {
      try {
        const response = await api.post('/vouchers/libraries/', data)
        await this.fetchLibraries()
        return response.data
      } catch (err) {
        throw err
      }
    },

    async updateLibraryItem(id, data) {
      try {
        const response = await api.put(`/vouchers/libraries/${id}/`, data)
        await this.fetchLibraries()
        return response.data
      } catch (err) {
        throw err
      }
    },

    async deleteLibraryItem(id) {
      try {
        await api.delete(`/vouchers/libraries/${id}/`)
        await this.fetchLibraries()
      } catch (err) {
        throw err
      }
    },
    async fetchTransactions() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/vouchers/transactions/')
        this.transactions = response.data.results || response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to fetch vouchers.'
      } finally {
        this.loading = false
      }
    },

    async fetchVoucher(id) {
      this.loading = true
      this.error = null
      try {
        const response = await api.get(`/vouchers/transactions/${id}/`)
        this.currentVoucher = response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to fetch voucher details.'
        throw err
      } finally {
        this.loading = false
      }
    },

    async createVoucher(data) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/vouchers/transactions/', data)
        await this.fetchTransactions()
        return response.data
      } catch (err) {
        this.error = err.response?.data || 'Failed to create voucher.'
        throw err
      } finally {
        this.loading = false
      }
    },

    async updateVoucher(id, data) {
      this.loading = true
      this.error = null
      try {
        const response = await api.put(`/vouchers/transactions/${id}/`, data)
        this.currentVoucher = response.data
        await this.fetchTransactions()
        return response.data
      } catch (err) {
        this.error = err.response?.data || 'Failed to update voucher.'
        throw err
      } finally {
        this.loading = false
      }
    },

    async deleteVoucher(id) {
      this.loading = true
      try {
        await api.delete(`/vouchers/transactions/${id}/`)
        await this.fetchTransactions()
      } catch (err) {
        this.error = err.response?.data || 'Failed to delete voucher.'
        throw err
      } finally {
        this.loading = false
      }
    },

    async downloadExcel(id, transactionCode) {
      try {
        const response = await api.get(`/vouchers/transactions/${id}/export_excel/`, {
          responseType: 'blob'
        })
        const blob = new Blob([response.data], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = `Voucher_${transactionCode || id}.xlsx`
        link.click()
        window.URL.revokeObjectURL(link.href)
      } catch (err) {
        alert('Failed to download Excel file. Please try again.')
      }
    },

    async downloadPdf(id, transactionCode, sheet = '') {
      try {
        const url = sheet
          ? `/vouchers/transactions/${id}/export_pdf/?sheet=${encodeURIComponent(sheet)}`
          : `/vouchers/transactions/${id}/export_pdf/`
        const response = await api.get(url, {
          responseType: 'blob'
        })
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        const suffix = sheet ? `_${sheet}` : ''
        link.download = `Voucher_${transactionCode || id}${suffix}.pdf`
        link.click()
        window.URL.revokeObjectURL(link.href)
      } catch (err) {
        alert('PDF conversion failed or is unavailable. Please try downloading as Excel (.xlsx).')
      }
    },

    async getPdfBlobUrl(id, sheet = '') {
      try {
        const url = sheet
          ? `/vouchers/transactions/${id}/export_pdf/?preview=true&sheet=${encodeURIComponent(sheet)}`
          : `/vouchers/transactions/${id}/export_pdf/?preview=true`
        const response = await api.get(url, {
          responseType: 'blob'
        })
        const blob = new Blob([response.data], { type: 'application/pdf' })
        return window.URL.createObjectURL(blob)
      } catch (err) {
        throw err
      }
    }
  }
})
