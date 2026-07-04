<template>
  <div class="student-page-container">
    <StudentSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['student-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="content-header">
        <h1>学生仪表板</h1>
        <p class="welcome-text">欢迎回来，{{ username }} 同学</p>
      </div>
      <div class="content-wrapper">
        <div class="stats-grid">
          <router-link to="/student/exams" class="stat-card stat-primary">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.upcomingExams }}</div>
              <div class="stat-label">即将开始</div>
            </div>
          </router-link>
          <router-link to="/student/exams" class="stat-card stat-success">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.completedExams }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </router-link>
          <router-link to="/student/exams" class="stat-card stat-warning">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.missedExams }}</div>
              <div class="stat-label">已错过</div>
            </div>
          </router-link>
          <router-link to="/student/wrong-questions" class="stat-card stat-info">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <path d="M14 2v6h6"/>
              </svg>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.wrongQuestions }}</div>
              <div class="stat-label">错题数</div>
            </div>
          </router-link>
        </div>
        <div class="section">
          <h3 class="section-title">即将开始的考试</h3>
          <div v-if="upcomingExams.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <p>暂无即将开始的考试</p>
          </div>
          <div v-else class="exam-list">
            <div v-for="exam in upcomingExams" :key="exam.id" class="exam-item">
              <div class="exam-info">
                <h4>{{ exam.title }}</h4>
                <div class="exam-meta">
                  <span class="meta-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <circle cx="12" cy="12" r="10"/>
                      <polyline points="12 6 12 12 16 14"/>
                    </svg>
                    时长: {{ exam.duration }}分钟
                  </span>
                  <span class="meta-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                      <line x1="16" y1="2" x2="16" y2="6"/>
                      <line x1="8" y1="2" x2="8" y2="6"/>
                      <line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                    {{ formatDate(exam.start_time) }}
                  </span>
                </div>
              </div>
              <div class="exam-actions">
                <router-link :to="`/student/exam/${exam.id}`" class="btn btn-primary">
                  查看详情
                </router-link>
              </div>
            </div>
          </div>
        </div>
        <div class="section">
          <h3 class="section-title">最近考试成绩</h3>
          <div v-if="recentResults.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <path d="M14 2v6h6"/>
              </svg>
            </div>
            <p>暂无考试记录</p>
          </div>
          <div v-else class="result-list">
            <div v-for="result in recentResults" :key="result.id" class="result-item">
              <div class="result-info">
                <h4>{{ result.exam_title }}</h4>
                <p>提交时间：{{ formatDate(result.submit_time) }}</p>
              </div>
              <div class="result-score">
                <span :class="['score-badge', getScoreClass(result.score)]">
                  {{ result.score !== null ? result.score + '分' : '待批改' }}
                </span>
                <router-link :to="`/student/result/${result.id}`" class="btn btn-sm btn-secondary">
                  查看详情
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, inject, onMounted } from 'vue'
import api from '../../utils/api'
import { formatDate } from '../../utils/formatters'
import StudentSidebar from '../../components/StudentSidebar.vue'

const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})

const stats = ref({
  upcomingExams: 0,
  completedExams: 0,
  missedExams: 0,
  wrongQuestions: 0
})

const username = ref('')
const upcomingExams = ref([])
const recentResults = ref([])

onMounted(async () => {
  try {
    const response = await api.get('student/dashboard/')
    stats.value = response.data.stats || stats.value
    upcomingExams.value = response.data.upcoming_exams || []
    recentResults.value = response.data.recent_results || []
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    username.value = user.username || ''
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
})

const getScoreClass = (score) => {
  if (score === null) return 'score-pending'
  if (score >= 90) return 'score-excellent'
  if (score >= 70) return 'score-good'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
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

.welcome-text {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.content-wrapper {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  border-radius: 12px;
  color: white;
  transition: all 0.3s ease;
  text-decoration: none;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.stat-card:active {
  transform: translateY(-2px);
}

.stat-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.stat-warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-info {
  background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon svg {
  width: 24px;
  height: 24px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-md);
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.exam-list,
.result-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.exam-item,
.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--bg-page);
  border-radius: 10px;
  transition: all 0.2s ease;
}

.exam-item:hover,
.result-item:hover {
  background: var(--bg-hover);
  transform: translateX(4px);
}

.exam-info h4,
.result-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.exam-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.meta-item svg {
  width: 14px;
  height: 14px;
}

.exam-info p,
.result-info p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.exam-actions,
.result-score {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.score-excellent {
  background: #d4edda;
  color: #155724;
}

.score-good {
  background: #cce5ff;
  color: #004085;
}

.score-pass {
  background: #fff3cd;
  color: #856404;
}

.score-fail {
  background: #f8d7da;
  color: #721c24;
}

.score-pending {
  background: #e2e3e5;
  color: #383d41;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  display: inline-block;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-secondary {
  background: var(--bg-page);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-hover);
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
  color: var(--text-muted);
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  color: var(--text-muted);
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

@media (max-width: 768px) {
  .student-page-container {
    flex-direction: column;
  }
  
  .student-main-content {
    margin-left: 0;
    width: 100%;
  }
  
  .student-main-content.sidebar-collapsed {
    margin-left: 0;
  }
  
  .content-header {
    padding: 16px;
  }
  
  .content-header h1 {
    font-size: 20px;
  }
  
  .content-wrapper {
    padding: 16px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .stat-card {
    padding: 16px;
    gap: 12px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
  }
  
  .stat-icon svg {
    width: 20px;
    height: 20px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .section {
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .section-title {
    font-size: 16px;
    margin-bottom: 12px;
  }
  
  .exam-item,
  .result-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 16px;
  }
  
  .exam-info h4,
  .result-info h4 {
    font-size: 14px;
    margin-bottom: 4px;
  }
  
  .exam-meta {
    gap: 8px;
  }
  
  .meta-item {
    font-size: 12px;
  }
  
  .exam-info p,
  .result-info p {
    font-size: 12px;
  }
  
  .exam-actions,
  .result-score {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }
  
  .btn {
    text-align: center;
  }
  
  .empty-state {
    padding: 32px 16px;
  }
  
  .empty-icon {
    width: 48px;
    height: 48px;
    margin-bottom: 12px;
  }
  
  .empty-state p {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 12px;
  }
  
  .content-header {
    padding: 12px;
  }
  
  .content-header h1 {
    font-size: 18px;
  }
  
  .content-wrapper {
    padding: 12px;
  }
}
</style>
