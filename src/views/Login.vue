<template>
  <div class="login-page">
    <div class="login-bg"></div>
    <div class="login-container">
      <div class="login-card">
        <div class="card-header">
          <div class="logo">🎓</div>
          <h1>在线考试系统</h1>
          <p>请登录您的账户</p>
        </div>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="username">用户名</label>
            <div class="input-wrapper">
              <span class="input-icon">👤</span>
              <input
                type="text"
                id="username"
                v-model="username"
                class="form-control"
                placeholder="请输入用户名"
                required
              />
            </div>
          </div>
          
          <div class="form-group">
            <label for="password">密码</label>
            <div class="input-wrapper">
              <span class="input-icon">🔒</span>
              <input
                type="password"
                id="password"
                v-model="password"
                class="form-control"
                placeholder="请输入密码"
                required
              />
            </div>
          </div>
          
          <div class="form-group">
            <label for="role">角色</label>
            <div class="role-selector">
              <button 
                type="button"
                :class="['role-btn', { active: role === 'student' }]"
                @click="role = 'student'"
              >
                <span class="role-icon">👨‍🎓</span>
                <span>学生</span>
              </button>
              <button 
                type="button"
                :class="['role-btn', { active: role === 'teacher' }]"
                @click="role = 'teacher'"
              >
                <span class="role-icon">👨‍🏫</span>
                <span>教师</span>
              </button>
            </div>
          </div>
          
          <button type="submit" class="login-btn" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? '登录中...' : '登 录' }}
          </button>
          
          <p v-if="error" class="error-message">
            <span class="error-icon">❌</span>
            {{ error }}
          </p>
        </form>
        
        <div class="card-footer">
          <p>学生账号：请联系教师获取</p>
          <p>教师账号：使用管理员创建的账号</p>
        </div>
      </div>
      
      <div class="back-home">
        <router-link to="/">← 返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '../utils/api'
import router from '../router'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

const username = ref('')
const password = ref('')
const role = ref('student')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.post('login/', {
      username: username.value,
      password: password.value,
      role: role.value
    })
    if (response.data.success) {
      localStorage.setItem('token', response.data.token)
      userStore.login(response.data.user)
      if (role.value === 'teacher') {
        router.push('/teacher/dashboard')
      } else {
        router.push('/student/dashboard')
      }
    } else {
      error.value = response.data.message || '登录失败'
    }
  } catch (err) {
    if (err.response) {
      const status = err.response.status
      const message = err.response.data?.message
      if (status === 401) {
        error.value = message || '用户名或密码错误'
      } else if (status === 403) {
        error.value = message || '账号被禁止登录'
      } else if (status === 400) {
        error.value = message || '请求参数错误'
      } else {
        error.value = message || `登录失败 (${status})`
      }
    } else if (err.request) {
      error.value = '网络连接失败，请检查网络设置'
    } else {
      error.value = '登录失败，请重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.3) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.3) 0%, transparent 50%);
  animation: bg-pulse 8s ease-in-out infinite;
}

@keyframes bg-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.login-container {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 480px;
  padding: 2rem;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: float 3s ease-in-out infinite;
  display: block;
  line-height: 1;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.card-header h1 {
  margin: 0 0 0.75rem 0;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.3;
  display: block;
}

.card-header p {
  margin: 0;
  opacity: 0.9;
  font-size: 1rem;
  line-height: 1.5;
  display: block;
}

.login-form {
  padding: 2.5rem;
}

.form-group {
  margin-bottom: 1.75rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #333;
  font-size: 0.95rem;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
  z-index: 1;
}

.form-control {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
}

.role-selector {
  display: flex;
  gap: 1rem;
}

.role-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.25rem;
  background: #f8f9fa;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 1rem;
  color: #666;
}

.role-btn:hover {
  background: #e9ecef;
  border-color: #667eea;
}

.role-btn.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-color: #667eea;
  color: #667eea;
  font-weight: 600;
}

.role-icon {
  font-size: 2rem;
}

.login-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #dc3545;
  text-align: center;
  margin: 1.5rem 0 0 0;
  font-size: 0.95rem;
  padding: 1rem;
  background: rgba(220, 53, 69, 0.1);
  border-radius: 10px;
}

.error-icon {
  font-size: 1.2rem;
}

.card-footer {
  padding: 1.5rem 2rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.card-footer p {
  margin: 0.25rem 0;
  font-size: 0.875rem;
  color: #666;
  text-align: center;
}

.back-home {
  margin-top: 2rem;
}

.back-home a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 0.95rem;
  transition: all 0.3s;
}

.back-home a:hover {
  color: white;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

@media (max-width: 768px) {
  .login-container {
    padding: 1rem;
    max-width: 90%;
  }
  
  .login-card {
    border-radius: 16px;
  }
  
  .card-header {
    padding: 2rem 1.5rem;
  }
  
  .logo {
    font-size: 3rem;
  }
  
  .card-header h1 {
    font-size: 1.5rem;
  }
  
  .card-header p {
    font-size: 0.9rem;
  }
  
  .login-form {
    padding: 1.5rem;
  }
  
  .form-group {
    margin-bottom: 1.25rem;
  }
  
  .form-group label {
    font-size: 0.875rem;
  }
  
  .form-control {
    padding: 0.75rem 0.875rem 0.75rem 2.5rem;
    font-size: 0.9rem;
  }
  
  .input-icon {
    font-size: 1rem;
    left: 0.875rem;
  }
  
  .role-btn {
    padding: 1rem;
    font-size: 0.875rem;
  }
  
  .role-icon {
    font-size: 1.5rem;
  }
  
  .login-btn {
    padding: 0.875rem;
    font-size: 1rem;
  }
  
  .card-footer {
    padding: 1rem 1.5rem;
  }
  
  .card-footer p {
    font-size: 0.8rem;
  }
  
  .back-home {
    margin-top: 1.5rem;
  }
  
  .back-home a {
    font-size: 0.875rem;
  }
}

@media (max-width: 480px) {
  .login-container {
    padding: 0.75rem;
    max-width: 95%;
  }
  
  .login-card {
    border-radius: 12px;
  }
  
  .card-header {
    padding: 1.5rem 1rem;
  }
  
  .logo {
    font-size: 2.5rem;
  }
  
  .card-header h1 {
    font-size: 1.25rem;
  }
  
  .card-header p {
    font-size: 0.8rem;
  }
  
  .login-form {
    padding: 1rem;
  }
  
  .role-selector {
    gap: 0.5rem;
  }
  
  .role-btn {
    padding: 0.75rem 0.5rem;
    gap: 0.25rem;
  }
  
  .role-icon {
    font-size: 1.25rem;
  }
  
  .error-message {
    padding: 0.75rem;
    font-size: 0.85rem;
  }
}
</style>
