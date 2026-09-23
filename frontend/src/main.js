import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import notify from '@/utils/notify'

// Gracefully route native alert to SweetAlert2 for consistent UI across the entire application
if (typeof window !== 'undefined') {
  window.alert = (msg) => notify.info(msg)
}

const app = createApp(App)
const pinia = createPinia()

app.config.globalProperties.$notify = notify
app.config.globalProperties.$swal = notify.raw

app.use(pinia)
app.use(router)

app.mount('#app')

