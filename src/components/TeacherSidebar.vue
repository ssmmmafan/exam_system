<template>
  <div :class="['teacher-sidebar', { 'collapsed': isCollapsed }]">
    <div class="sidebar-header">
      <div class="logo-container">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M20 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z"/>
          <path d="M14 2H8a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/>
          <path d="M12 6v8"/>
          <path d="M8 10h8"/>
        </svg>
        <span>教师中心</span>
      </div>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/teacher/dashboard" class="nav-item" :class="{ active: currentPath === '/teacher/dashboard' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>首页</span>
      </router-link>
      <router-link to="/teacher/questions" class="nav-item" :class="{ active: currentPath === '/teacher/questions' || currentPath.startsWith('/teacher/questions/') && !currentPath.startsWith('/teacher/questions/import') }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
        </svg>
        <span>题库管理</span>
      </router-link>
      <router-link to="/teacher/questions/import" class="nav-item" :class="{ active: currentPath === '/teacher/questions/import' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        <span>批量导入</span>
      </router-link>
      <router-link to="/teacher/exams" class="nav-item" :class="{ active: currentPath.startsWith('/teacher/exams') || currentPath.startsWith('/teacher/exam/') }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <path d="M14 2v6h6"/>
        </svg>
        <span>考试管理</span>
      </router-link>
      <router-link to="/teacher/students" class="nav-item" :class="{ active: currentPath.startsWith('/teacher/students') }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
        <span>学生管理</span>
      </router-link>
      <router-link to="/teacher/profile" class="nav-item" :class="{ active: currentPath === '/teacher/profile' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span>个人中心</span>
      </router-link>
    </nav>
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar" :style="{ background: avatarGradient }">
          {{ userInitial }}
        </div>
        <div class="user-details">
          <div class="user-name">{{ username }}</div>
          <div class="user-role">教师账号</div>
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
import { computed } from 'vue'
import { useRoute } from 'vue-router'

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

const username = computed(() => userData.value.username || '教师')
const userInitial = computed(() => username.value.charAt(0).toUpperCase())

const avatarGradient = computed(() => {
  const gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
    'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
    'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
  ]
  const index = username.value.charCodeAt(0) % gradients.length
  return gradients[index]
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
.teacher-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: 220px;
  height: 100vh;
  background: linear-gradient(180deg, #2C3E50 0%, #1A252F 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  overflow: hidden;
}

.teacher-sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: padding 0.25s ease;
}

.teacher-sidebar.collapsed .sidebar-header {
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
}

.teacher-sidebar.collapsed .logo-container {
  justify-content: center;
}

.teacher-sidebar.collapsed .logo-container span {
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
  background: rgba(74, 123, 196, 0.8);
  color: #fff;
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

.teacher-sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 12px;
}

.teacher-sidebar.collapsed .nav-item span {
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
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  color: white;
  flex-shrink: 0;
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
  background: rgba(231, 76, 60, 0.2);
  border: none;
  border-radius: 8px;
  color: #e74c3c;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.logout-btn:hover {
  background: rgba(231, 76, 60, 0.3);
  transform: translateX(4px);
}

.logout-btn svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.teacher-sidebar.collapsed .user-info {
  display: none;
}

.teacher-sidebar.collapsed .logout-btn {
  justify-content: center;
  padding: 10px;
}

.teacher-sidebar.collapsed .logout-btn span {
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
  background: linear-gradient(135deg, #4A7BC4 0%, #3A6BB4 100%);
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  box-shadow: 0 4px 12px rgba(74, 123, 196, 0.4);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
}

.sidebar-toggle:hover {
  background: linear-gradient(135deg, #3A6BB4 0%, #2D5A96 100%);
  box-shadow: 0 6px 16px rgba(74, 123, 196, 0.5);
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

.teacher-sidebar.collapsed .sidebar-toggle {
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
  background: linear-gradient(135deg, #2C3E50 0%, #1A252F 100%);
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
  border-color: #4A7BC4;
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
  background: linear-gradient(135deg, #4A7BC4 0%, #3A6BB4 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74, 123, 196, 0.4);
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}
</style>
