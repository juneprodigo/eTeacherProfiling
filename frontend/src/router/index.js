import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import AppLayout from '@/components/AppLayout.vue'
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import TeacherListView from '@/views/TeacherListView.vue'
import TeacherDetailView from '@/views/TeacherDetailView.vue'
import UserManagementView from '@/views/UserManagementView.vue'
import TeacherAnalyticsView from '@/views/TeacherAnalyticsView.vue'
import SchoolActivitiesView from '@/views/SchoolActivitiesView.vue'
import AttendanceView from '@/views/AttendanceView.vue'
import ReferenceLibrariesView from '@/views/ReferenceLibrariesView.vue'
import VoucherPreparationView from '@/views/VoucherPreparationView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { public: true }
  },
  {
    path: '/',
    component: AppLayout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: DashboardView,
        meta: { title: 'Executive Overview' }
      },
      {
        path: 'teachers',
        name: 'Teachers',
        component: TeacherListView,
        meta: { title: 'Faculty & Teacher Directory', requiresStaff: true }
      },
      {
        path: 'attendance',
        name: 'Attendance',
        component: AttendanceView,
        meta: { title: 'Time & Attendance Management (CSC Form 48)' }
      },
      {
        path: 'activities',
        name: 'SchoolActivities',
        component: SchoolActivitiesView,
        meta: { title: 'School Activities Monitoring & Management' }
      },
      {
        path: 'analytics',
        name: 'TeacherAnalytics',
        component: TeacherAnalyticsView,
        meta: { title: "Teacher's Analytics & Training Hub", requiresStaff: true }
      },
      {
        path: 'teachers/:id',
        name: 'TeacherDetail',
        component: TeacherDetailView,
        meta: { title: 'Personal Data Sheet (CS Form 212)' }
      },
      {
        path: 'profile',
        name: 'MyProfile',
        component: TeacherDetailView,
        meta: { title: 'My CS Form 212 Profile' }
      },
      {
        path: 'libraries',
        name: 'ReferenceLibraries',
        component: ReferenceLibrariesView,
        meta: { title: 'PDS Reference Libraries', requiresStaff: true }
      },
      {
        path: 'vouchers',
        name: 'VoucherPreparation',
        component: VoucherPreparationView,
        meta: { title: 'Voucher Preparation & Procurement Forms' }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: UserManagementView,
        meta: { title: 'User & Security Role Management', requiresAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Route guard for auth and role verification
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (!to.meta.public && !authStore.isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.meta.public && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'Dashboard' })
  } else if (to.meta.requiresStaff && !authStore.canManageAll) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
