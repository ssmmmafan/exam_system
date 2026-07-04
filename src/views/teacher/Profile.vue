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
              <div v-if="profile.avatar" class="avatar" style="overflow: hidden;">
                <img :src="profile.avatar" style="width:100%;height:100%;object-fit:cover;" />
              </div>
              <div v-else class="avatar" :style="{ background: avatarGradient }">
                {{ userInitial }}
              </div>
              <button @click="triggerAvatarUpload" class="change-avatar-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                  <circle cx="12" cy="13" r="4"/>
                </svg>
              </button>
              <input type="file" ref="fileInput" accept="image/*" style="display:none" @change="uploadAvatar" />
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
              <button @click="showPasswordForm = !showPasswordForm" class="btn btn-secondary">
                {{ showPasswordForm ? '取消' : '修改密码' }}
              </button>
            </div>
            <div v-if="showPasswordForm" class="password-form">
              <div class="form-group">
                <label class="form-label">当前密码</label>
                <input type="password" v-model="passwordForm.old_password" class="form-input" placeholder="请输入当前密码" />
              </div>
              <div class="form-group">
                <label class="form-label">新密码</label>
                <input type="password" v-model="passwordForm.new_password" class="form-input" placeholder="请输入新密码（至少6个字符）" />
              </div>
              <div class="form-group">
                <label class="form-label">确认新密码</label>
                <input type="password" v-model="passwordForm.confirm_password" class="form-input" placeholder="请再次输入新密码" />
              </div>
              <div v-if="passwordError" class="form-error">{{ passwordError }}</div>
              <div class="form-actions">
                <button class="btn btn-primary" :disabled="passwordSubmitting" @click="submitPasswordChange">
                  {{ passwordSubmitting ? '提交中...' : '确认修改' }}
                </button>
              </div>
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
  department: '',
  avatar: ''
})

const showChangeAvatar = ref(false)
const uploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const showPasswordForm = ref(false)
const passwordSubmitting = ref(false)
const passwordError = ref('')
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

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
      if (response.data.profile.avatar) {
        localStorage.setItem('avatar_url', response.data.profile.avatar)
      }
    }
  } catch (error) {
    console.error('Failed to fetch profile:', error)
  }
}

const triggerAvatarUpload = () => {
  fileInput.value?.click()
}

const uploadAvatar = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  
  const file = input.files[0]
  const formData = new FormData()
  formData.append('avatar', file)
  
  uploading.value = true
  try {
    const response = await api.post('teacher/profile/avatar/', formData)
    if (response.data.avatar_url) {
      profile.value.avatar = response.data.avatar_url
      localStorage.setItem('avatar_url', response.data.avatar_url)
    }
    alert('头像更新成功')
  } catch (error) {
    console.error('Failed to upload avatar:', error)
    alert('头像上传失败')
  } finally {
    uploading.value = false
    input.value = ''
  }
}

const submitPasswordChange = async () => {
  passwordError.value = ''
  const { old_password, new_password, confirm_password } = passwordForm.value

  if (!old_password) {
    passwordError.value = '请输入当前密码'
    return
  }
  if (!new_password || new_password.length < 6) {
    passwordError.value = '新密码至少需要6个字符'
    return
  }
  if (new_password !== confirm_password) {
    passwordError.value = '两次输入的密码不一致'
    return
  }

  if (!confirm('确定要修改密码吗？')) return

  passwordSubmitting.value = true
  try {
    await api.post('login/change-password/', { old_password, new_password, confirm_password })
    alert('密码修改成功，请重新登录')
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    localStorage.removeItem('avatar_url')
    window.location.href = '/login'
  } catch (error) {
    console.error('Failed to change password:', error)
    passwordError.value = '密码修改失败，可能是原密码不正确'
  } finally {
    passwordSubmitting.value = false
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

.teacher-top-header .btn svg {
  width: 18px;
  height: 18px;
  margin-right: 8px;
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
  flex-wrap: wrap;
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

.password-form {
  width: 100%;
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

.password-form .form-group {
  margin-bottom: var(--spacing-md);
}

.password-form .form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.password-form .form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 14px;
  background-color: var(--bg-page);
  color: var(--text-primary);
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.password-form .form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 123, 196, 0.1);
}

.form-error {
  color: var(--danger-color);
  font-size: 13px;
  margin-bottom: var(--spacing-md);
  padding: 8px 12px;
  background-color: var(--danger-light);
  border-radius: var(--radius-md);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
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

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color) 0%, #3A6BB4 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
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