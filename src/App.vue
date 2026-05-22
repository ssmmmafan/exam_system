<template>
  <div id="app">
    <nav class="navbar" v-if="currentPath !== '/login' && !isTeacherPage && !isStudentPage && !isHomePage">
      <div class="navbar-brand">
        <router-link to="/">📚 在线考试系统</router-link>
      </div>
      <div class="navbar-links" v-if="isLoggedIn">
        <span class="user-info">欢迎, {{ currentUser?.username }}</span>
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </div>
    </nav>
    <main class="main-content">
      <router-view></router-view>
    </main>
    <footer class="footer" v-if="currentPath !== '/login' && !isTeacherPage && !isStudentPage && !isHomePage">
      <p>&copy; 2026 在线考试系统 - 软件工程课程大作业</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, provide } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { User } from '@/types'

const router = useRouter()
const route = useRoute()

const currentUser = ref<User | null>(null)
const currentPath = ref<string>('/')
const sidebarCollapsed = ref(false)

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

provide('sidebarCollapsed', sidebarCollapsed)
provide('toggleSidebar', toggleSidebar)

const isLoggedIn = computed(() => {
  return currentUser.value !== null
})

const isTeacherPage = computed(() => {
  return currentPath.value.startsWith('/teacher')
})

const isStudentPage = computed(() => {
  return currentPath.value.startsWith('/student')
})

const isHomePage = computed(() => {
  return currentPath.value === '/'
})

const loadUser = () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      currentUser.value = JSON.parse(userStr)
    } catch (e) {
      currentUser.value = null
    }
  } else {
    currentUser.value = null
  }
}

const handleLogout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  localStorage.removeItem('avatar_url')
  currentUser.value = null
  router.push('/login')
}

watch(() => route.path, (newPath) => {
  currentPath.value = newPath
  loadUser()
})

onMounted(() => {
  loadUser()
  currentPath.value = route.path
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f5f5;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-brand a {
  color: white;
  text-decoration: none;
  font-size: 1.25rem;
  font-weight: bold;
}

.navbar-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.user-info {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.logout-btn {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.main-content {
  flex: 1;
}

.footer {
  background: #1a1a2e;
  color: rgba(255, 255, 255, 0.6);
  padding: 1rem;
  text-align: center;
  font-size: 0.9rem;
}
</style>
