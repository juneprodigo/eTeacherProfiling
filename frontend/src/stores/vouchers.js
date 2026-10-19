import { defineStore } from 'pinia'
import api from '@/api'

export const useVoucherStore = defineStore('vouchers', {
  state: () => ({
    transactions: [],
    currentVoucher: null,
    loading: false,
    error: null,
  }),

  actions: {
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
    }
  }
})
