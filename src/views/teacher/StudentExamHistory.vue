<template>
  <div class="teacher-page-container">
    <TeacherSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['teacher-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="teacher-top-header">
        <button class="btn btn-back" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="19" y1="12" x2="5" y2="12"/>
            <polyline points="12 19 5 12 12 5"/>
          </svg>
          <span>返回学生列表</span>
        </button>
        <h1>考试记录</h1>
      </div>
      <div class="content-wrapper">
        <div class="student-info-card" v-if="studentName">
          <div class="student-avatar">{{ studentName.charAt(0) }}</div>
          <div class="student-detail">
            <h2>{{ studentName }}</h2>
            <p class="student-id">学号：{{ studentId }}</p>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h2 class="card-title">考试列表</h2>
            <span class="exam-count">共 {{ exams.length }} 次考试</span>
          </div>
          <div v-if="loading" class="loading-state">加载中...</div>
          <div v-else-if="exams.length === 0" class="empty-state">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <path d="M14 2v6h6"/>
            </svg>
            <p>该学生暂无考试记录</p>
          </div>
          <div v-else class="exam-list">
            <div v-for="exam in exams" :key="exam.record_id" class="exam-card" @click="viewExamDetail(exam)">
              <div class="exam-main">
                <h3 class="exam-title">{{ exam.title }}</h3>
                <div class="exam-meta">
                  <span class="meta-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <circle cx="12" cy="12" r="10"/>
                      <polyline points="12 6 12 12 16 14"/>
                    </svg>
                    {{ exam.submit_time }}
                  </span>
                  <span class="meta-item" :class="exam.status === 'graded' ? 'tag-success' : 'tag-warning'">
                    {{ exam.is_graded ? '已批改' : '待批改' }}
                  </span>
                </div>
              </div>
              <div class="exam-score-section">
                  <div class="exam-score">
                    <span class="score-value" :class="{ 'score-pass': exam.score >= exam.total_score * 0.6 }">
                      {{ exam.score }}
                    </span>
                    <span class="score-divider">/</span>
                    <span class="score-total">{{ exam.total_score }}</span>
                  </div>
                  <div class="exam-actions">
                    <button class="btn btn-primary btn-sm" @click.stop="viewExamDetail(exam)">查看详情</button>
                    <button class="btn btn-danger-outline btn-sm" @click.stop="resetExam(exam)">重置考试</button>
                  </div>
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
import { useRoute, useRouter } from 'vue-router'
import api from '../../utils/api'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const route = useRoute()
const router = useRouter()
const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})

const studentName = ref('')
const studentId = ref('')
const exams = ref<any[]>([])
const loading = ref(true)

const goBack = () => {
  router.push('/teacher/students')
}

const viewExamDetail = (exam: any) => {
  router.push(`/teacher/result/${exam.record_id}`)
}

const resetExam = async (exam: any) => {
  if (!confirm(`确定要重置「${exam.title}」的考试记录吗？\n重置后学生可以重新参加考试，已提交的答案和成绩将被清空。`)) {
    return
  }
  try {
    await api.post(`teacher/record/${exam.record_id}/reset/`)
    alert('考试记录已重置，学生可以重新考试')
    exam.score = 0
    exam.status = 'ongoing'
    exam.is_graded = false
    exam.submit_time = null
  } catch (error) {
    alert('重置失败，请重试')
  }
}

onMounted(async () => {
  const studentIdParam = route.params.studentId as string
  try {
    const response = await api.get(`teacher/students/${studentIdParam}/exams/`)
    studentName.value = response.data.student_name
    studentId.value = response.data.student_id
    exams.value = response.data.exams
  } catch (error) {
    console.error('Failed to load student exams:', error)
  } finally {
    loading.value = false
  }
})
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

.teacher-top-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-xl);
  background: linear-gradient(135deg, var(--bg-top-header) 0%, #3A5A8C 100%);
}

.teacher-top-header h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-white);
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.25);
}

.btn-back svg {
  width: 16px;
  height: 16px;
}

.content-wrapper {
  flex: 1;
  padding: var(--spacing-xl);
  overflow-y: auto;
}

.student-info-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  background: white;
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-md);
  margin-bottom: var(--spacing-xl);
}

.student-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.student-detail h2 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.student-id {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.card {
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.card-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.exam-count {
  font-size: 13px;
  color: var(--text-secondary);
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: 14px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-icon {
  width: 56px;
  height: 56px;
  margin-bottom: var(--spacing-md);
}

.empty-state p {
  margin: 0;
  color: var(--text-secondary);
}

.exam-list {
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.exam-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.exam-card:hover {
  border-color: var(--primary-color);
  background-color: var(--primary-light);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.exam-main {
  flex: 1;
  min-width: 0;
}

.exam-title {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.exam-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.meta-item svg {
  width: 14px;
  height: 14px;
}

.tag-success {
  color: var(--success-color);
}

.tag-warning {
  color: var(--warning-color);
}

.exam-score-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  flex-shrink: 0;
}

.exam-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.exam-score {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.score-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-secondary);
}

.score-value.score-pass {
  color: var(--success-color);
}

.score-divider {
  font-size: 16px;
  color: var(--text-muted);
}

.score-total {
  font-size: 16px;
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

.btn-sm {
  padding: 6px 14px;
  font-size: 13px;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color) 0%, #3A6BB4 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.btn-danger-outline {
  background: transparent;
  color: #dc3545;
  border: 1px solid #dc3545;
}

.btn-danger-outline:hover {
  background: #dc3545;
  color: white;
}

@media (max-width: 768px) {
  .teacher-main-content {
    margin-left: 60px;
  }
  
  .content-wrapper {
    padding: var(--spacing-lg);
  }
  
  .exam-card {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .exam-score-section {
    width: 100%;
    justify-content: space-between;
  }

  .exam-actions {
    flex-direction: column;
    gap: 4px;
  }
}
</style>