import { createApp, ref, provide } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/theme.css'

const app = createApp(App)

const sidebarCollapsed = ref(false)
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

app.provide('sidebarCollapsed', sidebarCollapsed)
app.provide('toggleSidebar', toggleSidebar)

app.use(router)
app.mount('#app')
