<template>
  <div class="student-page-container">
    <StudentSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['student-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="content-header">
        <h1>我的考试</h1>
        <p class="subtitle">查看所有考试安排</p>
      </div>
      <div class="content-wrapper">
        <div class="tabs">
          <button v-for="tab in tabs" :key="tab.value"
                  :class="['tab-btn', { active: activeTab === tab.value }]"
                  @click="activeTab = tab.value">
            {{ tab.label }}
            <span class="tab-count">{{ getTabCount(tab.value) }}</span>
          </button>
        </div>
        
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>
        
        <div v-else-if="filteredExams.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <path d="M14 2v6h6"/>
            </svg>
          </div>
          <p>暂无{{ tabs.find(t => t.value === activeTab)?.label || '' }}的考试</p>
        </div>
        
        <div v-else class="exam-grid">
          <div v-for="exam in filteredExams" :key="exam.id" class="exam-card">
            <div class="exam-header">
              <h3>{{ exam.title }}</h3>
              <span :class="['status-badge', getStatusClass(exam)]">{{ getStatusText(exam) }}</span>
            </div>
            <div class="exam-body">
              <div class="exam-info">
                <p><strong>考试时长：</strong>{{ exam.duration }}分钟</p>
                <p><strong>总分：</strong>{{ exam.total_score }}分</p>
                <p><strong>题目数：</strong>{{ exam.question_count }}题</p>
                <p v-if="exam.start_time"><strong>开始时间：</strong>{{ formatDate(exam.start_time) }}</p>
                <p v-if="exam.end_time"><strong>结束时间：</strong>{{ formatDate(exam.end_time) }}</p>
              </div>
              <div class="exam-type-counts">
                <span v-if="exam.type_counts?.single" class="type-tag type-single">单选 {{ exam.type_counts.single }}</span>
                <span v-if="exam.type_counts?.multiple" class="type-tag type-multiple">多选 {{ exam.type_counts.multiple }}</span>
                <span v-if="exam.type_counts?.judge" class="type-tag type-judge">判断 {{ exam.type_counts.judge }}</span>
                <span v-if="exam.type_counts?.fill" class="type-tag type-fill">填空 {{ exam.type_counts.fill }}</span>
                <span v-if="exam.type_counts?.essay" class="type-tag type-essay">简答 {{ exam.type_counts.essay }}</span>
                <span v-if="exam.type_counts?.discussion" class="type-tag type-discussion">论述 {{ exam.type_counts.discussion }}</span>
              </div>
              <div v-if="exam.score !== null" :class="['exam-score', { 'score-pending': exam.needs_grading }]">
                <span class="score-label">得分：</span>
                <span class="score-value">{{ exam.score }}</span>
                <span class="score-divider">/</span>
                <span class="score-total">{{ exam.total_score }}</span>
                <span class="score-unit">分</span>
                <span v-if="exam.needs_grading" class="pending-tag">待批改</span>
              </div>
            </div>
            <div class="exam-footer">
              <router-link v-if="canTakeExam(exam)" :to="`/student/exam/${exam.id}`" class="btn btn-primary">
                查看详情
              </router-link>
              <router-link v-else-if="exam.score !== null" :to="`/student/result/${exam.record_id}`" class="btn btn-primary">
                查看成绩
              </router-link>
              <span v-else class="exam-status-text">{{ getStatusText(exam) }}</span>
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
const activeTab = ref('upcoming')
const allExams = ref([])

onMounted(async () => {
  await fetchExams()
})

const fetchExams = async () => {
  try {
    loading.value = true
    const response = await api.get('student/exams/')
    allExams.value = response.data.exams || []
  } catch (error) {
    console.error('Failed to fetch exams:', error)
    allExams.value = []
  } finally {
    loading.value = false
  }
}

const filteredExams = computed(() => {
  const now = new Date()
  return allExams.value.filter(exam => {
    const startTime = exam.start_time ? new Date(exam.start_time) : null
    const endTime = exam.end_time ? new Date(exam.end_time) : null
    
    if (activeTab.value === 'pending_grading') {
      return exam.needs_grading
    } else if (activeTab.value === 'ongoing') {
      return startTime && endTime && now >= startTime && now <= endTime && !exam.has_taken
    } else if (activeTab.value === 'completed') {
      return exam.has_taken
    } else if (activeTab.value === 'upcoming') {
      return startTime && startTime > now
    } else {
      return endTime && endTime < now && !exam.has_taken
    }
  })
})

const tabs = [
  { value: 'ongoing', label: '进行中' },
  { value: 'pending_grading', label: '待批改' },
  { value: 'completed', label: '已完成' },
  { value: 'upcoming', label: '即将开始' },
  { value: 'missed', label: '已错过' }
]

const getTabCount = (tab) => {
  const now = new Date()
  return allExams.value.filter(exam => {
    const startTime = exam.start_time ? new Date(exam.start_time) : null
    const endTime = exam.end_time ? new Date(exam.end_time) : null
    if (tab === 'pending_grading') return exam.needs_grading
    if (tab === 'ongoing') return startTime && endTime && now >= startTime && now <= endTime && !exam.has_taken
    if (tab === 'completed') return exam.has_taken
    if (tab === 'upcoming') return startTime && startTime > now
    return endTime && endTime < now && !exam.has_taken
  }).length
}

const canTakeExam = (exam) => {
  const now = new Date()
  const startTime = exam.start_time ? new Date(exam.start_time) : null
  const endTime = exam.end_time ? new Date(exam.end_time) : null
  
  if (!startTime || !endTime) return false
  if (exam.has_taken) return false
  
  return now >= startTime && now <= endTime
}

const getStatusClass = (exam) => {
  const now = new Date()
  const startTime = exam.start_time ? new Date(exam.start_time) : null
  const endTime = exam.end_time ? new Date(exam.end_time) : null
  
  if (exam.needs_grading) return 'status-pending'
  if (exam.has_taken) return 'status-completed'
  if (startTime && startTime > now) return 'status-upcoming'
  if (endTime && endTime < now) return 'status-missed'
  return 'status-active'
}

const getStatusText = (exam) => {
  const now = new Date()
  const startTime = exam.start_time ? new Date(exam.start_time) : null
  const endTime = exam.end_time ? new Date(exam.end_time) : null
  
  if (exam.needs_grading) return '待批改'
  if (exam.has_taken) return '已完成'
  if (startTime && startTime > now) return '即将开始'
  if (endTime && endTime < now) return '已错过'
  if (startTime && endTime && now >= startTime && now <= endTime) return '进行中'
  return ''
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
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

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}

.tab-btn {
  padding: 10px 20px;
  border: 1px solid var(--border-color);
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  background: #f1f5f9;
  color: #64748b;
}

.tab-btn.active .tab-count {
  background: rgba(255,255,255,0.25);
  color: white;
}

.tab-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.tab-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
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

.exam-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.exam-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: all 0.2s ease;
}

.exam-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.exam-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.2);
}

.status-completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-upcoming {
  background: #e3f2fd;
  color: #1565c0;
}

.status-missed {
  background: #ffebee;
  color: #c62828;
}

.status-active {
  background: #fff3e0;
  color: #e65100;
}

.exam-body {
  padding: 20px;
}

.exam-type-counts {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.type-tag {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.type-single { background: #e3f2fd; color: #1565c0; }
.type-multiple { background: #e8f5e9; color: #2e7d32; }
.type-judge { background: #fff3e0; color: #e65100; }
.type-fill { background: #fce4ec; color: #c2185b; }
.type-essay { background: #f3e5f5; color: #7b1fa2; }
.type-discussion { background: #fce4ec; color: #d81b60; }

.exam-score {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 12px;
  padding: 10px 14px;
  background: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 8px;
}

.exam-score.score-pending {
  background: #fefce8;
  border-color: #fde047;
}

.score-label {
  font-size: 13px;
  color: #166534;
}

.score-pending .score-label {
  color: #854d0e;
}

.score-value {
  font-size: 20px;
  font-weight: 700;
  color: #16a34a;
}

.score-pending .score-value {
  color: #a16207;
}

.score-divider {
  font-size: 16px;
  color: #86efac;
}

.score-total {
  font-size: 16px;
  font-weight: 600;
  color: #166534;
}

.score-unit {
  font-size: 13px;
  color: #166534;
}

.pending-tag {
  margin-left: auto;
  padding: 2px 8px;
  background: #fef3c7;
  color: #92400e;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.exam-info p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.exam-info p:last-child {
  margin-bottom: 0;
}

.exam-info strong {
  color: var(--text-primary);
}

.exam-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: center;
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

.exam-status-text {
  font-size: 14px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .student-main-content {
    margin-left: 64px;
  }
  
  .content-wrapper {
    padding: 16px;
  }
  
  .tabs {
    flex-wrap: wrap;
  }
  
  .exam-grid {
    grid-template-columns: 1fr;
  }
}
</style>
