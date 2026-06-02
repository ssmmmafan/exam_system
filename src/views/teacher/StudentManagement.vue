<template>
  <div class="teacher-page-container">
    <TeacherSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['teacher-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="teacher-top-header">
        <h1>学生管理</h1>
        <button class="btn btn-primary" @click="showImportModal = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          <span>批量导入</span>
        </button>
      </div>
      <div class="content-wrapper">
        <div class="stats-section">
          <div class="stat-card">
            <div class="stat-icon-wrapper stat-icon-primary">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ students.length }}</div>
              <div class="stat-label">总学生数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrapper stat-icon-success">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ activeStudents }}</div>
              <div class="stat-label">活跃学生</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrapper stat-icon-info">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <path d="M14 2v6h6"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ avgExamCount }}</div>
              <div class="stat-label">平均考试次数</div>
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">学生列表</h2>
            <div class="search-box">
              <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="搜索学生姓名或学号..." 
                class="search-input"
              />
            </div>
          </div>
          <div v-if="filteredStudents.length === 0" class="empty-state">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            <p>暂无学生</p>
          </div>
          <div v-else class="table-container">
            <table class="table">
              <thead>
                <tr>
                  <th>学号</th>
                  <th>姓名</th>
                  <th>班级</th>
                  <th>邮箱</th>
                  <th>注册时间</th>
                  <th>考试次数</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in filteredStudents" :key="student.id">
                  <td>{{ student.student_id }}</td>
                  <td>
                    <div class="student-name">
                      <div class="avatar">{{ student.name.charAt(0) }}</div>
                      {{ student.name }}
                    </div>
                  </td>
                  <td>
                    <span class="tag tag-info">{{ student.class_name || '未分配' }}</span>
                  </td>
                  <td>{{ student.email || '-' }}</td>
                  <td>{{ formatDate(student.created_at) }}</td>
                  <td>
                    <span class="tag" :class="student.exam_count > 0 ? 'tag-success' : 'tag-muted'">
                      {{ student.exam_count }} 次
                    </span>
                  </td>
                  <td>
                    <button class="btn btn-secondary" @click="viewStudentExams(student)">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                      <span>查看考试</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const router = useRouter()
const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})
const students = ref([])
const searchQuery = ref('')
const showImportModal = ref(false)

const filteredStudents = computed(() => {
  return students.value.filter(s => 
    s.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    s.student_id.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const activeStudents = computed(() => {
  return students.value.filter(s => s.exam_count > 0).length
})

const avgExamCount = computed(() => {
  if (students.value.length === 0) return 0
  const total = students.value.reduce((sum, s) => sum + s.exam_count, 0)
  return Math.round(total / students.value.length)
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadStudents = async () => {
  try {
    const response = await api.get('teacher/students/')
    students.value = response.data
  } catch (error) {
    console.error('Failed to load students:', error)
  }
}

const viewStudentExams = (student) => {
  router.push(`/teacher/student/${student.id}/exams`)
}

onMounted(() => {
  loadStudents()
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

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  box-shadow: var(--shadow-md);
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.25s ease;
}

.stat-card:hover {
  box-shadow: var(--shadow-lg);
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.stat-icon-wrapper svg {
  width: 24px;
  height: 24px;
}

.stat-icon-primary {
  background-color: var(--primary-light);
  color: var(--primary-color);
}

.stat-icon-success {
  background-color: var(--success-light);
  color: var(--success-color);
}

.stat-icon-info {
  background-color: var(--info-light);
  color: var(--info-color);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
  letter-spacing: -0.03em;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.card {
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid rgba(0, 0, 0, 0.04);
  padding: var(--spacing-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.search-box {
  position: relative;
  width: 280px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 14px;
  background-color: var(--bg-page);
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: var(--bg-card);
  box-shadow: 0 0 0 3px rgba(74, 123, 196, 0.1);
}

.table-container {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-light);
}

.table th {
  background-color: var(--bg-page);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table tr:hover {
  background-color: var(--primary-light);
}

.table tr:last-child td {
  border-bottom: none;
}

.student-name {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
  color: var(--text-primary);
}

.avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-light);
  color: var(--primary-color);
  border-radius: 50%;
  font-weight: 600;
  font-size: 13px;
}

.table .btn svg {
  width: 14px;
  height: 14px;
  margin-right: 4px;
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

.tag-muted {
  background-color: #F3F4F6;
  color: var(--text-secondary);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background-color: var(--bg-card);
  border-radius: var(--radius-xl);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, var(--bg-top-header) 0%, #3A5A8C 100%);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-white);
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-white);
  cursor: pointer;
  padding: 6px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.modal-close svg {
  width: 20px;
  height: 20px;
}

.modal-body {
  padding: var(--spacing-xl);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: var(--spacing-md);
  background-color: var(--bg-page);
  border-radius: var(--radius-md);
}

.detail-label {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.exam-history-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
}

.empty-history {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  color: var(--text-muted);
}

.empty-history .empty-icon {
  width: 40px;
  height: 40px;
  margin-bottom: var(--spacing-sm);
}

.empty-history p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.exam-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.exam-history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background-color: var(--bg-page);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.exam-history-item:hover {
  background-color: var(--primary-light);
}

.exam-info h5 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.exam-info p {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}

.exam-score span {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-secondary);
}

.exam-score span.passed {
  color: var(--success-color);
}

@media (max-width: 768px) {
  .teacher-main-content {
    margin-left: 60px;
  }
  
  .content-wrapper {
    padding: var(--spacing-lg);
  }
  
  .stats-section {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .search-box {
    width: 100%;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .table {
    font-size: 13px;
  }
  
  .table th,
  .table td {
    padding: 10px 12px;
  }
}
</style>
