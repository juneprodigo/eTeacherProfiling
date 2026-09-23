import { defineStore } from 'pinia'
import api from '@/api'

export const useAttendanceStore = defineStore('attendance', {
  state: () => ({
    todayStatus: null,
    monthlyDTR: null,
    stats: null,
    leaves: [],
    balances: [],
    facultyList: [],
    isLoading: false,
    isPunching: false,
    error: null,
  }),

  actions: {
    async fetchFacultyList() {
      try {
        const res = await api.get('/attendance/records/faculty_list/')
        this.facultyList = res.data
        return res.data
      } catch (err) {
        console.error('Failed to load faculty list for attendance', err)
        return []
      }
    },

    async fetchTodayStatus(teacherId = null) {
      try {
        const params = teacherId ? { teacher: teacherId } : {}
        const res = await api.get('/attendance/records/today_status/', { params })
        this.todayStatus = res.data
        return res.data
      } catch (err) {
        console.error('Failed to load today attendance status', err)
      }
    },

    async clockPunch(punchType, teacherId = null) {
      this.isPunching = true
      try {
        const payload = { punch_type: punchType }
        if (teacherId) payload.teacher_id = teacherId
        const res = await api.post('/attendance/records/clock_punch/', payload)
        if (this.todayStatus) {
          this.todayStatus.record = res.data.record
        }
        return res.data
      } catch (err) {
        console.error('Punch failed', err)
        throw err
      } finally {
        this.isPunching = false
      }
    },

    async fetchMonthlyDTR(teacherId = null, month = null, year = null) {
      this.isLoading = true
      try {
        const params = {}
        if (teacherId) params.teacher = teacherId
        if (month) params.month = month
        if (year) params.year = year
        const res = await api.get('/attendance/records/monthly_dtr/', { params })
        this.monthlyDTR = res.data
        return res.data
      } catch (err) {
        console.error('Failed to load monthly DTR', err)
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async fetchAttendanceStats() {
      try {
        const res = await api.get('/attendance/records/stats/')
        this.stats = res.data
        return res.data
      } catch (err) {
        console.error('Failed to load attendance stats', err)
      }
    },

    async fetchLeaves(status = null) {
      try {
        const params = status && status !== 'All' ? { status } : {}
        const res = await api.get('/attendance/leaves/', { params })
        this.leaves = res.data.results || res.data
        return this.leaves
      } catch (err) {
        console.error('Failed to load leaves', err)
      }
    },

    async submitLeave(leaveData) {
      try {
        const res = await api.post('/attendance/leaves/', leaveData)
        this.leaves.unshift(res.data)
        return res.data
      } catch (err) {
        console.error('Failed to submit leave', err)
        throw err
      }
    },

    async reviewLeave(leaveId, status, remarks = '') {
      try {
        const res = await api.post(`/attendance/leaves/${leaveId}/review/`, { status, remarks })
        const idx = this.leaves.findIndex(l => l.id === leaveId)
        if (idx !== -1) {
          this.leaves[idx] = res.data.leave
        }
        return res.data
      } catch (err) {
        console.error('Failed to review leave', err)
        throw err
      }
    },

    async fetchBalances() {
      try {
        const res = await api.get('/attendance/balances/')
        this.balances = res.data.results || res.data
        return this.balances
      } catch (err) {
        console.error('Failed to load leave balances', err)
      }
    }
  }
})
