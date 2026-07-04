<template>
  <div class="student-page-container">
    <StudentSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['student-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="content-header">
        <h1>个人中心</h1>
        <p class="subtitle">管理您的个人信息</p>
      </div>
      <div class="content-wrapper">
        <div class="profile-card">
          <div class="profile-header">
            <div class="avatar-container">
              <div v-if="profile.avatar" class="avatar-img-wrapper">
                <img :src="profile.avatar" class="avatar-img" alt="头像" />
              </div>
              <div v-else class="avatar" :style="{ background: avatarGradient }">
                {{ userInitial }}
              </div>
              <div v-if="uploading" class="avatar-uploading-overlay">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spinner">
                  <circle cx="12" cy="12" r="10" stroke-dasharray="31.4 31.4" stroke-linecap="round"/>
                </svg>
              </div>
              <input ref="fileInput" type="file" accept="image/*" class="file-input-hidden" @change="uploadAvatar" />
              <button @click="triggerAvatarUpload" class="change-avatar-btn" :disabled="uploading">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                  <circle cx="12" cy="13" r="4"/>
                </svg>
              </button>
            </div>
            <div class="user-info">
              <h2>{{ profile.username }}</h2>
              <p class="user-role">学生账号</p>
            </div>
          </div>
          
          <div class="profile-body">
            <div v-if="!editing" class="info-grid">
              <div class="info-item">
                <span class="label">学号</span>
                <span class="value">{{ profile.student_id || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="label">姓名</span>
                <span class="value">{{ profile.username }}</span>
              </div>
              <div class="info-item">
                <span class="label">班级</span>
                <span class="value">{{ profile.class_name || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="label">专业</span>
                <span class="value">{{ profile.major || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="label">入学年份</span>
                <span class="value">{{ profile.enrollment_year || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="label">联系电话</span>
                <span class="value">{{ profile.phone || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="label">负责教师</span>
                <span class="value">{{ profile.teacher_name || '未分配' }}</span>
              </div>
            </div>
            
            <div v-else class="edit-form">
              <div class="form-group">
                <label>学号</label>
                <input type="text" v-model="formData.student_id" />
              </div>
              <div class="form-group">
                <label>班级</label>
                <input type="text" v-model="formData.class_name" />
              </div>
              <div class="form-group">
                <label>专业</label>
                <input type="text" v-model="formData.major" />
              </div>
              <div class="form-group">
                <label>入学年份</label>
                <input type="number" v-model="formData.enrollment_year" />
              </div>
              <div class="form-group">
                <label>联系电话</label>
                <input type="text" v-model="formData.phone" />
              </div>
            </div>
          </div>
          
          <div class="profile-footer">
            <button v-if="!editing" @click="startEditing" class="btn btn-primary">
              编辑信息
            </button>
            <div v-else class="btn-group">
              <button @click="cancelEditing" class="btn btn-secondary">取消</button>
              <button @click="saveProfile" class="btn btn-primary">保存</button>
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
import StudentSidebar from '../../components/StudentSidebar.vue'

const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})

const loading = ref(true)
const editing = ref(false)
const uploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const profile = ref({
  username: '',
  student_id: '',
  class_name: '',
  major: '',
  enrollment_year: '',
  phone: '',
  teacher_name: '',
  avatar: ''
})

const formData = ref({
  student_id: '',
  class_name: '',
  major: '',
  enrollment_year: '',
  phone: ''
})

const showPasswordForm = ref(false)
const passwordSubmitting = ref(false)
const passwordError = ref('')
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const userInitial = computed(() => {
  return profile.value.username.charAt(0).toUpperCase()
})

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
    loading.value = true
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      profile.value.username = user.username || ''
    }
    const response = await api.get('student/profile/')
    if (response.data.profile) {
      profile.value = { ...profile.value, ...response.data.profile }
      if (response.data.profile.avatar) {
        localStorage.setItem('avatar_url', response.data.profile.avatar)
      }
    }
  } catch (error) {
    console.error('Failed to fetch profile:', error)
  } finally {
    loading.value = false
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
    const response = await api.post('student/profile/avatar/', formData)
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

const startEditing = () => {
  formData.value = {
    student_id: profile.value.student_id,
    class_name: profile.value.class_name,
    major: profile.value.major,
    enrollment_year: profile.value.enrollment_year,
    phone: profile.value.phone
  }
  editing.value = true
}

const cancelEditing = () => {
  editing.value = false
}

const saveProfile = async () => {
  try {
    await api.put('student/profile/', formData.value)
    profile.value = { ...profile.value, ...formData.value }
    editing.value = false
    alert('保存成功')
  } catch (error) {
    console.error('Failed to save profile:', error)
    alert('保存失败')
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
.student-page-container {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg-page);
}

.student-main-content {
  flex: 1;
  margin-left: 220px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.student-main-content.sidebar-collapsed {
  margin-left: 64px;
}

.content-header {
  padding: 24px 32px;
  background: white;
  border-bottom: 1px solid var(--border-color);
}

.content-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.content-wrapper {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}

.profile-card,
.security-section {
  background: white;
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  margin-bottom: 24px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(135deg, #2C3E50 0%, #1A252F 100%);
}

.avatar-container {
  position: relative;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  color: white;
}

.avatar-img-wrapper {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.file-input-hidden {
  display: none;
}

.avatar-uploading-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-uploading-overlay svg {
  width: 28px;
  height: 28px;
  color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.change-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 28px;
  height: 28px;
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
  width: 14px;
  height: 14px;
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
  padding: 24px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
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

.edit-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  color: var(--text-secondary);
}

.form-group input {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.profile-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
}

.btn-group {
  display: flex;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-hover);
}

.security-section h3 {
  margin: 0;
  padding: 20px 24px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
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
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.password-form .form-group {
  margin-bottom: 16px;
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
  border-radius: 8px;
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
  margin-bottom: 16px;
  padding: 8px 12px;
  background-color: var(--danger-light);
  border-radius: 8px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .student-main-content {
    margin-left: 64px;
  }
  
  .content-wrapper {
    padding: 16px;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .info-grid,
  .edit-form {
    grid-template-columns: 1fr;
  }
  
  .security-item {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>
