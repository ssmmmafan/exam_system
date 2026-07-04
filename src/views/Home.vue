<template>
  <div class="home-page">
    <div class="navbar">
      <div class="nav-brand">
        <span class="logo-icon">📚</span>
        <span class="brand-text">在线考试系统</span>
      </div>
      <div class="nav-actions">
        <button v-if="!isLoggedIn" @click="goToLogin" class="btn-login">登录</button>
        <div v-else class="user-info">
          <span class="welcome-text">欢迎，{{ userRoleText }}</span>
          <button @click="handleLogout" class="btn-logout">退出</button>
        </div>
      </div>
    </div>
    
    <div class="hero-section">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <div class="logo">🎓</div>
        <h1>在线考试系统</h1>
        <p class="subtitle">专业的在线考试与测评平台</p>
        
        <div class="features">
          <div class="feature-item" v-for="(feature, index) in features" :key="index" :style="{ animationDelay: index * 0.1 + 's' }">
            <span class="feature-icon">{{ feature.icon }}</span>
            <span>{{ feature.text }}</span>
          </div>
        </div>
        
        <div class="cta-section">
          <button v-if="!userStore.isLoggedIn" @click="goToLogin" class="login-btn pulse">
            立即登录
            <span class="btn-arrow">→</span>
          </button>
          <div v-else class="quick-links">
            <router-link to="/chat" class="quick-link chat-link">
              💬 聊天中心
            </router-link>
            <router-link v-if="userStore.userRole === 'student'" to="/student/dashboard" class="quick-link">
              进入学生中心
            </router-link>
            <router-link v-else to="/teacher/dashboard" class="quick-link">
              进入教师中心
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <div class="stats-section">
      <div class="stat-card" v-for="(stat, index) in stats" :key="index">
        <div class="stat-icon">{{ stat.icon }}</div>
        <div class="stat-number">{{ stat.number }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const userRole = computed(() => userStore.userRole)
const userRoleText = computed(() => {
  return userRole.value === 'teacher' ? '教师' : '学生'
})

const features = [
  { icon: '✓', text: '智能组卷' },
  { icon: '✓', text: '在线答题' },
  { icon: '✓', text: '自动批改' },
  { icon: '✓', text: '成绩分析' }
]

const stats = [
  { icon: '👥', number: '1000+', label: '在线学生' },
  { icon: '📝', number: '5000+', label: '题库题目' },
  { icon: '📄', number: '200+', label: '考试场次' },
  { icon: '🏆', number: '98%', label: '用户满意度' }
]

const goToLogin = () => {
  router.push('/login')
}

const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    userStore.logout()
    localStorage.removeItem('token')
    localStorage.removeItem('avatar_url')
    sessionStorage.clear()
    router.push('/login')
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 3rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  font-size: 2rem;
}

.brand-text {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-login {
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-login:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.5);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
}

.btn-logout {
  padding: 0.5rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-logout:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

.hero-section {
  position: relative;
  padding: 6rem 2rem;
  text-align: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse-bg 4s ease-in-out infinite;
}

@keyframes pulse-bg {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.5; }
}

.hero-content {
  position: relative;
  z-index: 1;
}

.logo {
  font-size: 8rem;
  margin-bottom: 2rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

h1 {
  font-size: 4rem;
  font-weight: 800;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, #fff 0%, #667eea 50%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 5px 30px rgba(102, 126, 234, 0.3);
}

.subtitle {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 3rem;
}

.features {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 3rem;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem 1.5rem;
  border-radius: 50px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slide-up 0.5s ease-out forwards;
  opacity: 0;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.feature-icon {
  color: #00ff88;
  font-weight: bold;
  font-size: 1.2rem;
}

.cta-section {
  margin-top: 2rem;
}

.login-btn {
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 3rem;
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
}

.login-btn:hover {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 15px 50px rgba(102, 126, 234, 0.6);
}

.btn-arrow {
  font-size: 1.5rem;
  transition: transform 0.3s;
}

.login-btn:hover .btn-arrow {
  transform: translateX(5px);
}

.pulse {
  animation: pulse-btn 2s ease-in-out infinite;
}

@keyframes pulse-btn {
  0%, 100% { box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4); }
  50% { box-shadow: 0 10px 60px rgba(102, 126, 234, 0.6); }
}

.quick-links {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.quick-link {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
  color: white;
  text-decoration: none;
  border-radius: 30px;
  font-weight: 600;
  transition: all 0.3s;
}

.quick-link:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(58, 123, 213, 0.5);
}

.chat-link {
  background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
}

.chat-link:hover {
  box-shadow: 0 10px 30px rgba(254, 202, 87, 0.5);
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  padding: 4rem 3rem;
  background: rgba(255, 255, 255, 0.03);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-10px);
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
}

.stat-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.stat-number {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.6);
}
</style>
