<template>
  <div class="teacher-page-container">
    <TeacherSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['teacher-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="teacher-top-header">
        <h1>个人中心</h1>
      </div>
      <div class="content-wrapper">
        <div class="profile-card">
          <div class="profile-header">
            <div class="avatar-container">
              <div class="avatar" :style="{ background: avatarGradient }">
                {{ userInitial }}
              </div>
              <button @click="showChangeAvatar = true" class="change-avatar-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                  <path d="M16 11.37A4 4 0 0 1 12 17v1a4 4 0 0 0 4-4v-1.63"/>
                </svg>
              </button>
            </div>
            <div class="user-info">
              <h2>{{ profile.username }}</h2>
              <p class="user-role">教师账号</p>
            </div>
          </div>
          
          <div class="profile-body">
            <div class="info-grid">
              <div class="info-item">
                <span class="label">姓名</span>
                <span class="value">{{ profile.username }}</span>
              </div>
              <div class="info-item">
                <span class="label">邮箱</span>
                <span class="value">{{ profile.email || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="label">联系电话</span>
                <span class="value">{{ profile.phone || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="label">所属学院</span>
                <span class="value">{{ profile.department || '未设置' }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="security-section">
          <h3>账号安全</h3>
          <div class="security-card">
            <div class="security-item">
              <div class="security-info">
                <h4>修改密码</h4>
                <p>定期修改密码可以提高账号安全性</p>
              </div>
              <button @click="changePassword" class="btn btn-secondary">
                修改密码
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, inject, onMounted } from 'vue'
import api from '../../utils/api'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})

const profile = ref({
  username: '',
  email: '',
  phone: '',
  department: ''
})

const showChangeAvatar = ref(false)

const userInitial = computed(() => profile.value.username.charAt(0).toUpperCase())

const avatarGradient = computed(() => {
  const gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  ]
  const index = profile.value.username.charCodeAt(0) % gradients.length
  return gradients[index]
})

onMounted(async () => {
  await fetchProfile()
})

const fetchProfile = async () => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      profile.value.username = user.username || ''
    }
    const response = await api.get('teacher/profile/')
    if (response.data.profile) {
      profile.value = { ...profile.value, ...response.data.profile }
    }
  } catch (error) {
    console.error('Failed to fetch profile:', error)
  }
}

const changePassword = async () => {
  const old_password = prompt('请输入当前密码：')
  if (!old_password) return
  
  const new_password = prompt('请输入新密码（至少6个字符）：')
  if (!new_password || new_password.length < 6) {
    alert('新密码至少需要6个字符')
    return
  }
  
  const confirm_password = prompt('请再次输入新密码：')
  if (new_password !== confirm_password) {
    alert('两次输入的密码不一致')
    return
  }
  
  if (!confirm('确认要修改密码吗？')) return

  try {
    await api.post('login/change-password/', { old_password, new_password, confirm_password })
    alert('密码修改成功，请重新登录')
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    window.location.href = '/login'
  } catch (error) {
    console.error('Failed to change password:', error)
    alert('密码修改失败，可能是原密码不正确')
  }
}
</script>

<style scoped>
.teacher-page-container {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg-page);
}

.teacher-main-content {
  flex: 1;
  margin-left: 220px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.teacher-main-content.sidebar-collapsed {
  margin-left: 64px;
}

.content-wrapper {
  flex: 1;
  padding: var(--spacing-xl);
  overflow-y: auto;
}

.profile-card {
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  margin-bottom: var(--spacing-xl);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
  background: linear-gradient(135deg, #2C3E50 0%, #1A252F 100%);
}

.avatar-container {
  position: relative;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  color: white;
}

.change-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 32px;
  height: 32px;
  background: var(--primary-color);
  border: 3px solid white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
}

.change-avatar-btn svg {
  width: 16px;
  height: 16px;
}

.user-info h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 600;
  color: white;
}

.user-role {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.profile-body {
  padding: var(--spacing-xl);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 13px;
  color: var(--text-secondary);
}

.info-item .value {
  font-size: 15px;
  color: var(--text-primary);
  font-weight: 500;
}

.security-section {
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
}

.security-section h3 {
  margin: 0;
  padding: var(--spacing-lg);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
}

.security-info h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.security-info p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.btn {
  padding: 10px 20px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color) 0%, #3A6BB4 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background: var(--bg-page);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-hover);
}

@media (max-width: 768px) {
  .teacher-main-content {
    margin-left: 60px;
  }
  
  .content-wrapper {
    padding: var(--spacing-lg);
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
