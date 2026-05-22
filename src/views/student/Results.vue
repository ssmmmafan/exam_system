<template>
  <div class="student-page-container">
    <StudentSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['student-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="content-header">
        <h1>考试成绩</h1>
        <p class="subtitle">查看所有考试历史记录</p>
      </div>
      <div class="content-wrapper">
        <div class="stats-row">
          <div class="stat-item">
            <div class="stat-value">{{ stats.totalExams }}</div>
            <div class="stat-label">参加考试</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.averageScore }}</div>
            <div class="stat-label">平均分</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.highestScore }}</div>
            <div class="stat-label">最高分</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.lowestScore }}</div>
            <div class="stat-label">最低分</div>
          </div>
        </div>
        
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>
        
        <div v-else-if="results.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <path d="M14 2v6h6"/>
            </svg>
          </div>
          <p>暂无考试记录</p>
        </div>
        
        <div v-else class="results-table-container">
          <table class="results-table">
            <thead>
              <tr>
                <th>考试名称</th>
                <th>提交时间</th>
                <th>得分</th>
                <th>正确率</th>
                <th>用时</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="result in results" :key="result.id">
                <td>{{ result.exam_title }}</td>
                <td>{{ formatDate(result.submit_time) }}</td>
                <td>
                  <span :class="['score-badge', getScoreClass(result.score)]">
                    {{ result.score !== null ? result.score + '分' : '待批改' }}
                  </span>
                </td>
                <td>{{ result.accuracy !== null ? result.accuracy + '%' : '-' }}</td>
                <td>{{ formatTime(result.time_spent) }}</td>
                <td>
                  <router-link :to="`/student/result/${result.id}`" class="btn-link">
                    查看详情
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
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
const results = ref([])

const stats = computed(() => {
  const scores = results.value.filter(r => r.score !== null).map(r => r.score)
  return {
    totalExams: results.value.length,
    averageScore: scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0,
    highestScore: scores.length > 0 ? Math.max(...scores) : 0,
    lowestScore: scores.length > 0 ? Math.min(...scores) : 0
  }
})

onMounted(async () => {
  await fetchResults()
})

const fetchResults = async () => {
  try {
    loading.value = true
    const response = await api.get('student/results/')
    results.value = response.data.results || []
  } catch (error) {
    console.error('Failed to fetch results:', error)
    results.value = []
  } finally {
    loading.value = false
  }
}

const getScoreClass = (score) => {
  if (score === null) return 'score-pending'
  if (score >= 90) return 'score-excellent'
  if (score >= 70) return 'score-good'
  if (score >= 60) return 'score-pass'
  return 'score-fail'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const formatTime = (seconds) => {
  if (!seconds) return '-'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (hours > 0) {
    return `${hours}小时${minutes}分`
  }
  if (minutes > 0) {
    return `${minutes}分${secs}秒`
  }
  return `${secs}秒`
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

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  background: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: var(--shadow-md);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: var(--bg-page);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon svg {
  width: 40px;
  height: 40px;
  color: var(--text-muted);
}

.empty-state p {
  margin: 0;
  color: var(--text-muted);
  font-size: 14px;
}

.results-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th {
  background: var(--bg-page);
  padding: 14px 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
}

.results-table td {
  padding: 14px 16px;
  font-size: 14px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
}

.results-table tr:last-child td {
  border-bottom: none;
}

.results-table tr:hover {
  background: var(--bg-hover);
}

.score-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
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

.btn-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 14px;
}

.btn-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .student-main-content {
    margin-left: 64px;
  }
  
  .content-wrapper {
    padding: 16px;
  }
  
  .stats-row {
    grid-template-columns: 1fr 1fr;
  }
  
  .results-table-container {
    overflow-x: auto;
  }
  
  .results-table {
    min-width: 600px;
  }
}
</style>
