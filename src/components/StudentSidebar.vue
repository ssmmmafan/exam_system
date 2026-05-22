<template>
  <div :class="['student-sidebar', { 'collapsed': isCollapsed }]">
    <div class="sidebar-header">
      <div class="logo-container">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M12 14l9-5-9-5-9 5 9 5z"/>
          <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/>
          <path d="M12 14l9-5-9-5-9 5 9 5z"/>
        </svg>
        <span>学生中心</span>
      </div>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/student/dashboard" class="nav-item" :class="{ active: currentPath === '/student/dashboard' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>首页</span>
      </router-link>
      <router-link to="/student/exams" class="nav-item" :class="{ active: currentPath.startsWith('/student/exams') }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <path d="M14 2v6h6"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
        <span>我的考试</span>
      </router-link>
      <router-link to="/student/results" class="nav-item" :class="{ active: currentPath.startsWith('/student/results') }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        <span>考试成绩</span>
      </router-link>
      <router-link to="/student/wrong-questions" class="nav-item" :class="{ active: currentPath === '/student/wrong-questions' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        <span>错题本</span>
      </router-link>
      <router-link to="/student/profile" class="nav-item" :class="{ active: currentPath === '/student/profile' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span>个人中心</span>
      </router-link>
    </nav>
    <div class="sidebar-footer">
      <div class="user-info" v-if="!isCollapsed">
        <div v-if="avatarUrl" class="user-avatar-img-wrapper">
          <img :src="avatarUrl" class="user-avatar-img" alt="avatar" />
        </div>
        <div v-else class="user-avatar">{{ userInitial }}</div>
        <div class="user-details">
          <div class="user-name">{{ username }}</div>
          <div class="user-role">学生账号</div>
        </div>
      </div>
      <button @click="handleLogout" class="logout-btn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        <span>退出登录</span>
      </button>
    </div>
    <button @click="$emit('toggle')" class="sidebar-toggle">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline v-if="isCollapsed" points="9 18 15 12 9 6"/>
        <polyline v-else points="15 6 9 12 15 18"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../utils/api'

defineProps<{
  isCollapsed: boolean
}>()

defineEmits<{
  (e: 'toggle'): void
}>()

const route = useRoute()
const currentPath = computed(() => route.path)

const userData = computed(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      return JSON.parse(userStr)
    } catch {
      return { username: '' }
    }
  }
  return { username: '' }
})

const username = computed(() => userData.value.username || '学生')
const userInitial = computed(() => username.value.charAt(0).toUpperCase())
const avatarUrl = computed(() => localStorage.getItem('avatar_url') || '')

onMounted(async () => {
  try {
    const response = await api.get('student/profile/')
    if (response.data.profile?.avatar) {
      localStorage.setItem('avatar_url', response.data.profile.avatar)
    }
  } catch {
    // ignore
  }
})

const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    localStorage.removeItem('avatar_url')
    window.location.href = '/login'
  }
}

</script>

<style scoped>
.student-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: 220px;
  height: 100vh;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  overflow: hidden;
}

.student-sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: padding 0.25s ease;
}

.student-sidebar.collapsed .sidebar-header {
  padding: 16px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.25s ease;
}

.logo-container svg {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  color: #00d2ff;
}

.logo-container span {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 1;
  transition: opacity 0.2s ease, width 0.25s ease;
  width: auto;
  color: #00d2ff;
}

.student-sidebar.collapsed .logo-container {
  justify-content: center;
}

.student-sidebar.collapsed .logo-container span {
  opacity: 0;
  width: 0;
  display: none;
}

.sidebar-nav {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 8px;
  text-decoration: none;
  color: rgba(255, 255, 255, 0.85);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  transform: translateX(4px);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(0, 210, 255, 0.3) 0%, rgba(58, 123, 213, 0.3) 100%);
  color: #00d2ff;
  border-left: 3px solid #00d2ff;
}

.nav-item svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  flex-grow: 0;
}

.nav-item span {
  opacity: 1;
  transition: opacity 0.2s ease;
}

.student-sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 12px;
}

.student-sidebar.collapsed .nav-item span {
  opacity: 0;
  display: none;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.user-avatar-img-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.user-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.user-details {
  overflow: hidden;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 14px;
  background: rgba(220, 53, 69, 0.2);
  border: none;
  border-radius: 8px;
  color: #ff6b6b;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.logout-btn:hover {
  background: rgba(220, 53, 69, 0.3);
  transform: translateX(4px);
}

.logout-btn svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.student-sidebar.collapsed .logout-btn {
  justify-content: center;
  padding: 12px;
}

.student-sidebar.collapsed .logout-btn span {
  opacity: 0;
  display: none;
}

.sidebar-toggle {
  position: absolute;
  right: -16px;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 210, 255, 0.4);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
}

.sidebar-toggle:hover {
  background: linear-gradient(135deg, #00b8d9 0%, #2e6eb5 100%);
  box-shadow: 0 6px 16px rgba(0, 210, 255, 0.5);
  transform: translateY(-50%) scale(1.1);
}

.sidebar-toggle:active {
  transform: translateY(-50%) scale(0.95);
}

.sidebar-toggle svg {
  width: 16px;
  height: 16px;
  transition: transform 0.25s ease;
}

.student-sidebar.collapsed .sidebar-toggle {
  right: -16px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 400px;
  max-width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 12px 12px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.modal-close {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 6px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-close svg {
  width: 20px;
  height: 20px;
}

.modal-body {
  padding: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
}

.form-input {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #00d2ff;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 210, 255, 0.4);
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}
</style>
