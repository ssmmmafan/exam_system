<template>
  <div id="app">
    <nav class="navbar" v-if="currentPath !== '/login' && !isTeacherPage && !isStudentPage && !isHomePage">
      <div class="navbar-brand">
        <router-link to="/">📚 在线考试系统</router-link>
      </div>
      <div class="navbar-links" v-if="userStore.isLoggedIn">
        <span class="user-info">欢迎, {{ userStore.user?.username }}</span>
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
import { computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from './stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const currentPath = computed(() => route.path)

const isTeacherPage = computed(() => {
  return currentPath.value.startsWith('/teacher')
})

const isStudentPage = computed(() => {
  return currentPath.value.startsWith('/student')
})

const isHomePage = computed(() => {
  return currentPath.value === '/'
})

const handleLogout = () => {
  userStore.logout()
  localStorage.removeItem('token')
  localStorage.removeItem('avatar_url')
  router.push('/login')
}

watch(() => route.path, (newPath) => {
  // 路由变化时自动触发
})

onMounted(() => {
  // 用户状态已在 main.ts 中初始化
})
</script>

<style>
:root {
  --breakpoint-mobile: 768px;
  --breakpoint-tablet: 1024px;
}

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

/* 移动端适配 */
@media (max-width: 768px) {
  html {
    font-size: 14px;
  }
  
  .navbar {
    padding: 0.75rem 1rem;
  }
  
  .navbar-brand a {
    font-size: 1.1rem;
  }
  
  .navbar-links {
    gap: 0.75rem;
  }
  
  .user-info {
    display: none;
  }
  
  .logout-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
  }
  
  .main-content {
    padding: 0;
  }
  
  .footer {
    padding: 0.75rem;
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  html {
    font-size: 12px;
  }
  
  .navbar {
    padding: 0.5rem 0.75rem;
  }
  
  .navbar-brand a {
    font-size: 1rem;
  }
}
</style>
