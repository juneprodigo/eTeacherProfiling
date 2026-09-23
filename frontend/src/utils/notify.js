import Swal from 'sweetalert2'

// Base themed mixin for modal alerts matching #fecb90 palette
const themeSwal = Swal.mixin({
  background: '#1d150e',
  color: '#fffdfa',
  backdrop: 'rgba(10, 6, 4, 0.75)',
  confirmButtonColor: '#fecb90',
  cancelButtonColor: '#453326',
  customClass: {
    popup: 'swal2-custom-popup',
    title: 'swal2-custom-title',
    htmlContainer: 'swal2-custom-html',
    confirmButton: 'swal2-custom-confirm',
    cancelButton: 'swal2-custom-cancel',
  },
  buttonsStyling: false,
})

// Top-end Toast notification mixin
const Toast = Swal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
  timer: 3000,
  timerProgressBar: true,
  background: '#1d150e',
  color: '#fffdfa',
  customClass: {
    popup: 'swal2-custom-toast',
    title: 'swal2-custom-toast-title',
  },
  didOpen: (toast) => {
    toast.onmouseenter = Swal.stopTimer
    toast.onmouseleave = Swal.resumeTimer
  }
})

export const notify = {
  // Toast notifications (unobtrusive, auto-dismiss)
  toast(message, icon = 'success') {
    return Toast.fire({
      icon,
      title: message
    })
  },

  // Modal success notification
  success(message, title = 'Success') {
    return themeSwal.fire({
      icon: 'success',
      title,
      text: message,
      confirmButtonText: 'OK'
    })
  },

  // Modal error notification
  error(message, title = 'Error Encountered') {
    return themeSwal.fire({
      icon: 'error',
      title,
      text: typeof message === 'string' ? message : JSON.stringify(message),
      confirmButtonText: 'Understood'
    })
  },

  // Modal warning notification
  warning(message, title = 'Attention') {
    return themeSwal.fire({
      icon: 'warning',
      title,
      text: message,
      confirmButtonText: 'Proceed'
    })
  },

  // Modal info notification
  info(message, title = 'Information') {
    return themeSwal.fire({
      icon: 'info',
      title,
      text: message,
      confirmButtonText: 'OK'
    })
  },

  // Confirmation dialog (returns Promise<boolean>)
  async confirm({
    title = 'Are you sure?',
    text = 'This action cannot be undone.',
    confirmButtonText = 'Yes, Proceed',
    cancelButtonText = 'Cancel',
    icon = 'warning'
  } = {}) {
    const res = await themeSwal.fire({
      title,
      text,
      icon,
      showCancelButton: true,
      confirmButtonText,
      cancelButtonText,
      reverseButtons: true
    })
    return res.isConfirmed
  },

  // Direct access to Swal instance
  raw: Swal,
  themeSwal
}

export default notify
