<template>
  <div class="teacher-dashboard-container">
    <TeacherSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
        <div class="top-header">
          <div class="header-left">
            <h1 class="page-title">教师仪表板</h1>
            <p class="page-subtitle">欢迎回来, {{ username }} 老师</p>
          </div>
          <div class="header-right">
            <div class="user-info">
              <div class="user-avatar">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </div>
              <span class="user-name">{{ username }}</span>
            </div>
          </div>
        </div>
        <div class="content-area">
          <div class="stats-section">
            <router-link to="/teacher/questions" class="stat-card">
              <div class="stat-icon-wrapper">
                <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
                </svg>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.total_questions }}</div>
                <div class="stat-label">我的试题</div>
              </div>
            </router-link>
            <router-link to="/teacher/exams" class="stat-card">
              <div class="stat-icon-wrapper stat-icon-success">
                <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <path d="M14 2v6h6"/>
                </svg>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.total_exams }}</div>
                <div class="stat-label">我的考试</div>
              </div>
            </router-link>
            <router-link to="/teacher/exams" class="stat-card">
              <div class="stat-icon-wrapper stat-icon-warning">
                <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.ongoing_exams }}</div>
                <div class="stat-label">进行中</div>
              </div>
            </router-link>
            <router-link to="/teacher/exams" class="stat-card">
              <div class="stat-icon-wrapper stat-icon-info">
                <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ stats.pending_grading }}</div>
                <div class="stat-label">待批改</div>
              </div>
            </router-link>
          </div>
          <div class="quick-actions">
            <h2 class="section-title">快捷操作</h2>
            <div class="action-grid">
              <router-link to="/teacher/questions" class="action-card">
                <div class="action-icon-wrapper">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M12 5v14M5 12h14"/>
                  </svg>
                </div>
                <span class="action-text">创建试题</span>
              </router-link>
              <router-link to="/teacher/exams" class="action-card">
                <div class="action-icon-wrapper">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <path d="M14 2v6h6M16 13H8"/>
                  </svg>
                </div>
                <span class="action-text">创建试卷</span>
              </router-link>
              <router-link to="/teacher/exams" class="action-card">
                <div class="action-icon-wrapper">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M14 15l-3.75-3.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/>
                  </svg>
                </div>
                <span class="action-text">随机组卷</span>
              </router-link>
              <router-link to="/teacher/students" class="action-card">
                <div class="action-icon-wrapper">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                </div>
                <span class="action-text">我的学生</span>
              </router-link>
            </div>
          </div>
          <div class="content-row">
            <div class="content-card">
              <div class="card-header">
                <h2 class="card-title">进行中的考试</h2>
                <router-link to="/teacher/exams" class="view-all">查看全部</router-link>
              </div>
              <div v-if="ongoingExams.length === 0" class="empty-state">
                <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10"/>
                  <circle cx="12" cy="12" r="6"/>
                  <circle cx="12" cy="12" r="2"/>
                </svg>
                <p>暂无进行中的考试</p>
              </div>
              <div v-else class="exam-list">
                <div v-for="exam in ongoingExams" :key="exam.id" class="exam-item">
                  <div class="exam-info">
                    <h3>{{ exam.title }}</h3>
                    <p class="exam-meta">剩余时间: {{ formatTimeLeft(exam.end_time) }}</p>
                  </div>
                  <div class="exam-actions">
                    <span class="participants">{{ exam.student_count }} 人参加</span>
                    <router-link :to="`/teacher/exam/${exam.id}/students`" class="btn btn-primary">查看学生</router-link>
                  </div>
                </div>
              </div>
            </div>
            <div class="content-card">
              <div class="card-header">
                <h2 class="card-title">待批改试卷</h2>
                <router-link to="/teacher/exams" class="view-all">查看全部</router-link>
              </div>
              <div v-if="pendingExams.length === 0" class="empty-state">
                <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <p>暂无待批改试卷</p>
              </div>
              <div v-else class="pending-list">
                <div v-for="record in pendingExams" :key="record.id" class="pending-item">
                  <div class="pending-info">
                    <h3>{{ record.exam_title }}</h3>
                    <p>{{ record.student_name }}</p>
                  </div>
                  <router-link :to="`/teacher/grade/${record.id}`" class="btn btn-secondary">批改</router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, inject } from 'vue'
import api from '../../utils/api'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const stats = ref({
  total_questions: 0,
  total_exams: 0,
  ongoing_exams: 0,
  pending_grading: 0
})

const username = ref('')
const ongoingExams = ref([])
const pendingExams = ref([])
const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})

onMounted(async () => {
  try {
    const response = await api.get('teacher/dashboard/')
    stats.value = response.data.stats || stats.value
    username.value = response.data.username || ''
    ongoingExams.value = response.data.ongoing_exams || []
    pendingExams.value = response.data.pending_exams || []
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  }
})

const formatTimeLeft = (endTime: string) => {
  if (!endTime) return '未知'
  const end = new Date(endTime).getTime()
  const now = Date.now()
  const diff = end - now
  if (diff <= 0) return '已结束'
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  return `${hours}小时${minutes}分钟`
}
</script>

<style>
/* 全局覆盖样式 */
.teacher-dashboard-container {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 9999 !important;
  margin: 0 !important;
  padding: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  overflow: hidden !important;
}
</style>

<style scoped>
/* 变量定义 */
:root {
  --primary-color: #4A7BC4;
  --primary-light: #E8F0F8;
  --primary-hover: #3A6BB4;
  --success-color: #52C41A;
  --success-light: #E6F7E6;
  --warning-color: #FA8C16;
  --warning-light: #FFF7E6;
  --info-color: #13C2C2;
  --info-light: #E6FFFB;
  --text-primary: #1F2937;
  --text-secondary: #6B7280;
  --text-muted: #9CA3AF;
  --bg-page: #F5F7FA;
  --bg-card: #FFFFFF;
  --bg-sidebar: #1E3A5F;
  --bg-sidebar-hover: #2D4A6F;
  --bg-top-header: #2C4A7C;
  --border-color: #E5E7EB;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.1);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
}

/* 主容器 */
.teacher-dashboard-container {
  display: flex;
  width: 100%;
  height: 100%;
  background-color: var(--bg-page);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  letter-spacing: 0.01em;
  overflow: hidden;
}

/* 主内容区 */
.main-content {
  flex: 1;
  margin-left: 220px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  transition: margin-left 0.3s ease;
}

.main-content.sidebar-collapsed {
  margin-left: 60px;
}

/* 顶部导航 */
.top-header {
  background: linear-gradient(135deg, var(--bg-top-header) 0%, #3A5A8C 100%);
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: #FFFFFF;
  letter-spacing: -0.01em;
}

.page-subtitle {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 14px;
  background-color: rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-md);
  backdrop-filter: blur(4px);
}

.user-avatar {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: #FFFFFF;
}

.user-avatar svg {
  width: 18px;
  height: 18px;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: #FFFFFF;
}

/* 内容区域 */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding-top: 24px;
}

/* 统计卡片 */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 28px;
  padding: 0 32px;
}

.stat-card {
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 22px;
  display: flex;
  align-items: center;
  gap: 18px;
  box-shadow: var(--shadow-md);
  transition: all 0.25s ease;
  border: 1px solid rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
}

.stat-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, var(--primary-color) 0%, rgba(74, 123, 196, 0.5) 100%);
}

.stat-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.stat-icon-wrapper {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-light);
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.stat-icon-wrapper .stat-icon {
  width: 24px;
  height: 24px;
  color: var(--primary-color);
}

.stat-icon-success {
  background-color: var(--success-light) !important;
}

.stat-icon-success .stat-icon {
  color: var(--success-color) !important;
}

.stat-icon-warning {
  background-color: var(--warning-light) !important;
}

.stat-icon-warning .stat-icon {
  color: var(--warning-color) !important;
}

.stat-icon-info {
  background-color: var(--info-light) !important;
}

.stat-icon-info .stat-icon {
  color: var(--info-color) !important;
}

.stat-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.1;
  letter-spacing: -0.05em;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
  line-height: 1.4;
}

/* 快捷操作 */
.quick-actions {
  margin-bottom: 28px;
  padding: 0 32px;
}

.section-title {
  margin: 0 0 18px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 16px;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px;
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--text-primary);
  box-shadow: var(--shadow-md);
  transition: all 0.25s ease;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.action-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-3px);
}

.action-card:hover .action-icon-wrapper {
  background-color: var(--primary-color);
  color: #FFFFFF;
  transform: scale(1.05);
}

.action-icon-wrapper {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-light);
  border-radius: var(--radius-md);
  color: var(--primary-color);
  flex-shrink: 0;
  transition: all 0.25s ease;
}

.action-icon-wrapper svg {
  width: 22px;
  height: 22px;
}

.action-text {
  font-size: 14px;
  font-weight: 500;
  text-align: center;
}

/* 内容卡片行 */
.content-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  padding: 0 32px;
  padding-bottom: 32px;
}

.content-card {
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-md);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.card-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.view-all {
  font-size: 13px;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: var(--radius-md);
  background-color: var(--primary-light);
  transition: all 0.2s ease;
}

.view-all:hover {
  background-color: rgba(74, 123, 196, 0.25);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 24px;
  color: var(--text-muted);
}

.empty-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 14px;
  color: var(--text-muted);
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

/* 列表 */
.exam-list,
.pending-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.exam-item,
.pending-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background-color: #FAFBFC;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  border: 1px solid rgba(0, 0, 0, 0.03);
}

.exam-item:hover,
.pending-item:hover {
  background-color: var(--primary-light);
  border-color: rgba(74, 123, 196, 0.15);
}

.exam-info,
.pending-info {
  flex: 1;
  min-width: 0;
}

.exam-info h3,
.pending-info h3 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.exam-meta {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.pending-info p {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.exam-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.participants {
  font-size: 12px;
  color: var(--primary-color);
  padding: 5px 12px;
  background-color: var(--primary-light);
  border-radius: 16px;
  font-weight: 500;
}

/* 按钮 */
.btn {
  padding: 7px 16px;
  border-radius: var(--radius-md);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background-color: var(--primary-color);
  color: #FFFFFF;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
  box-shadow: 0 2px 8px rgba(74, 123, 196, 0.3);
}

.btn-secondary {
  background-color: var(--warning-light);
  color: var(--warning-color);
}

.btn-secondary:hover {
  background-color: rgba(248, 140, 22, 0.18);
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }

  .logo-text,
  .nav-item span,
  .logout-btn span {
    display: none;
  }

  .sidebar-header {
    padding: 14px;
  }

  .nav-item {
    justify-content: center;
    padding: 10px;
    margin: 4px 6px;
  }

  .top-header {
    padding: 14px 16px;
  }

  .stats-section,
  .quick-actions,
  .content-row {
    padding: 0 16px;
  }

  .stats-section {
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    margin-top: 16px;
  }

  .stat-card {
    padding: 18px;
    gap: 14px;
  }

  .stat-icon-wrapper {
    width: 44px;
    height: 44px;
  }

  .stat-value {
    font-size: 28px;
  }

  .content-row {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .stats-section {
    grid-template-columns: 1fr;
  }

  .action-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .action-card {
    padding: 16px 12px;
  }

  .action-icon-wrapper {
    width: 40px;
    height: 40px;
  }

  .action-icon-wrapper svg {
    width: 20px;
    height: 20px;
  }
}
</style>
