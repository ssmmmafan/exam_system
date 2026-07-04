<template>
  <div class="teacher-page-container">
    <TeacherSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['teacher-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="teacher-top-header">
        <h1>考试管理</h1>
        <div class="btn-group">
          <button class="btn btn-primary" @click="router.push('/teacher/exam/create')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 4v16m8-8H4"/>
            </svg>
            <span>创建考试</span>
          </button>
          <button class="btn btn-secondary" @click="router.push('/teacher/exam/random')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/>
              <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
            </svg>
            <span>随机组卷</span>
          </button>
        </div>
      </div>
      <div class="content-wrapper">
        <div class="tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.value"
            class="tab-btn"
            :class="{ active: activeTab === tab.value }"
            @click="activeTab = tab.value"
          >
            {{ tab.label }}
            <span class="tab-count">{{ getTabCount(tab.value) }}</span>
          </button>
        </div>
        <div class="exam-grid">
          <div v-if="filteredExams.length === 0" class="empty-state">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <path d="M14 2v6h6M16 13H8M16 17H8"/>
            </svg>
            <p>暂无{{ getActiveTabLabel() }}考试</p>
          </div>
          <div v-else>
            <div v-for="exam in filteredExams" :key="exam.id" class="exam-card">
              <div class="exam-header">
                <h3>{{ exam.title }}</h3>
                <span :class="['tag', getExamStatusClass(exam.status)]">{{ getExamStatusLabel(exam.status) }}</span>
              </div>
              <div class="exam-info">
                <div class="info-row">
                  <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                  </svg>
                  <span>{{ formatDate(exam.start_time) }} - {{ formatDate(exam.end_time) }}</span>
                </div>
                <div class="info-row">
                  <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <path d="M14 2v6h6"/>
                  </svg>
                  <span>{{ exam.question_count }} 题 | {{ exam.total_score }} 分</span>
                </div>
                <div class="info-row type-counts">
                  <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M4 6h16M4 12h16M4 18h16"/>
                  </svg>
                  <div class="type-tags">
                    <span v-if="exam.type_counts?.single" class="type-tag type-single">单选 {{ exam.type_counts.single }}</span>
                    <span v-if="exam.type_counts?.multiple" class="type-tag type-multiple">多选 {{ exam.type_counts.multiple }}</span>
                    <span v-if="exam.type_counts?.judge" class="type-tag type-judge">判断 {{ exam.type_counts.judge }}</span>
                    <span v-if="exam.type_counts?.fill" class="type-tag type-fill">填空 {{ exam.type_counts.fill }}</span>
                    <span v-if="exam.type_counts?.essay" class="type-tag type-essay">简答 {{ exam.type_counts.essay }}</span>
                    <span v-if="exam.type_counts?.discussion" class="type-tag type-discussion">论述 {{ exam.type_counts.discussion }}</span>
                  </div>
                </div>
                <div class="info-row">
                  <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                  <span>{{ exam.student_count }} 名学生</span>
                  <span v-if="exam.pending_grading_count > 0" class="pending-badge">待批改 {{ exam.pending_grading_count }} 人</span>
                </div>
              </div>
              <div class="exam-actions">
                <button v-if="exam.status === 'draft'" class="btn btn-primary" @click="publishExam(exam.id)">发布</button>
                <button v-if="exam.status === 'published'" class="btn btn-warning" @click="unpublishExam(exam.id)">取消发布</button>
                <button v-if="exam.status === 'ongoing'" class="btn btn-danger" @click="unpublishExam(exam.id)">强制结束</button>
                <button class="btn btn-secondary" @click="viewExam(exam.id)">查看详情</button>
                <button v-if="exam.status === 'draft'" class="btn btn-danger" @click="deleteExam(exam.id)">删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'
import type { TeacherExamListItem } from '../../types'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const router = useRouter()
const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})

const exams = ref<TeacherExamListItem[]>([])
const activeTab = ref('all')

const tabs = [
  { value: 'all', label: '全部' },
  { value: 'draft', label: '草稿' },
  { value: 'published', label: '已发布' },
  { value: 'ongoing', label: '进行中' },
  { value: 'finished', label: '已结束' },
  { value: 'pending_grading', label: '待批改' }
]

const filteredExams = computed(() => {
  if (!Array.isArray(exams.value)) return []
  if (activeTab.value === 'all') return exams.value
  if (activeTab.value === 'pending_grading') return exams.value
  return exams.value.filter(e => e.status === activeTab.value)
})

const getTabCount = (tab: string) => {
  if (!Array.isArray(exams.value)) return 0
  if (tab === 'all') return exams.value.length
  if (tab === 'pending_grading') return exams.value.filter(e => e.pending_grading_count > 0).length
  return exams.value.filter(e => e.status === tab).length
}

const getActiveTabLabel = () => {
  const tab = tabs.find(t => t.value === activeTab.value)
  return tab ? tab.label : ''
}

const getExamStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    'draft': '草稿',
    'published': '待开始',
    'ongoing': '进行中',
    'finished': '已结束'
  }
  return labels[status] || status
}

const getExamStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    'draft': 'tag-muted',
    'published': 'tag-info',
    'ongoing': 'tag-warning',
    'finished': 'tag-muted'
  }
  return classes[status] || 'tag-muted'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadExams = async () => {
  try {
    const params = activeTab.value === 'pending_grading' ? '?status=pending_grading' : ''
    const response = await api.get(`teacher/exams/${params}`)
    const data = response.data
    exams.value = data && Array.isArray(data.exams) ? data.exams : []
  } catch (error) {
    console.error('Failed to load exams:', error)
    exams.value = []
  }
}

const publishExam = async (id: number) => {
  try {
    await api.post(`teacher/exams/${id}/publish/`)
    loadExams()
  } catch (error) {
    console.error('Failed to publish exam:', error)
    alert('发布失败，请检查是否已发布')
  }
}

const unpublishExam = async (id: number) => {
  const exam = exams.value.find(e => e.id === id)
  if (!exam) return
  
  let confirmMessage = ''
  if (exam.status === 'ongoing') {
    confirmMessage = '确定要强制结束这个进行中的考试吗？所有正在考试的学生将被强制交卷！'
  } else {
    confirmMessage = '确定要取消发布这个考试吗？'
  }
  
  if (!confirm(confirmMessage)) return
  
  try {
    await api.post(`teacher/exams/${id}/unpublish/`)
    loadExams()
  } catch (error) {
    console.error('Failed to unpublish exam:', error)
    alert('操作失败')
  }
}

const deleteExam = async (id: number) => {
  const exam = exams.value.find(e => e.id === id)
  if (!exam) return
  const questionCount = exam.question_count || '未知'
  if (!confirm(`确定要删除草稿「${exam.title}」吗？\n包含 ${questionCount} 道题目，删除后不可恢复！`)) return
  try {
    await api.delete(`teacher/exams/${id}/delete/`)
    exams.value = Array.isArray(exams.value) ? exams.value.filter(e => e.id !== id) : []
  } catch (error: any) {
    const msg = error?.response?.data?.error || '删除失败'
    alert(msg)
  }
}

const viewExam = (id: number) => {
  router.push(`/teacher/exam/${id}`)
}

onMounted(() => {
  loadExams()
})

watch(activeTab, () => {
  loadExams()
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

.btn-group {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-group .btn {
  gap: 8px;
}

.btn-group .btn svg {
  width: 18px;
  height: 18px;
}

.content-wrapper {
  flex: 1;
  padding: var(--spacing-xl);
  overflow-y: auto;
}

.tabs {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-sm);
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background-color: var(--primary-light);
  color: var(--primary-color);
}

.tab-btn.active {
  background-color: var(--primary-color);
  color: var(--text-white);
}

.tab-count {
  padding: 2px 8px;
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  font-size: 12px;
}

.tab-btn.active .tab-count {
  background-color: rgba(255, 255, 255, 0.2);
}

.exam-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg);
}

.exam-card {
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid rgba(0, 0, 0, 0.04);
  padding: var(--spacing-xl);
  transition: all 0.2s ease;
}

.exam-card:hover {
  box-shadow: var(--shadow-lg);
}

.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.exam-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.exam-info {
  margin-bottom: var(--spacing-lg);
}

.info-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.info-icon {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.info-row span {
  font-size: 13px;
  color: var(--text-secondary);
}

.type-counts {
  flex-wrap: wrap;
  gap: 6px;
}

.type-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
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

.pending-badge {
  padding: 2px 8px;
  background: #fff3cd;
  color: #856404;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.exam-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.exam-actions .btn {
  padding: 6px 12px;
  font-size: 12px;
}

.empty-state {
  grid-column: 1 / -1;
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

/* Modal styles */
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
  max-width: 500px;
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

.form-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

.selected-questions-preview {
  margin-top: 12px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 8px;
}

.selected-question-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  margin-bottom: 4px;
  background-color: var(--bg-page);
  border-radius: var(--radius-sm);
}

.selected-question-item:last-child {
  margin-bottom: 0;
}

.question-type {
  padding: 4px 8px;
  background-color: var(--primary-color);
  color: white;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.question-content {
  flex: 1;
  font-size: 13px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.question-score {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--danger-color);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.remove-btn:hover {
  background-color: rgba(245, 101, 101, 0.1);
}

.remove-btn svg {
  width: 16px;
  height: 16px;
}

.question-select-modal {
  max-width: 800px;
}

.filter-bar {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.filter-select {
  width: 140px;
}

.filter-input {
  flex: 1;
}

.question-list {
  max-height: 400px;
  overflow-y: auto;
}

.question-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.2s;
}

.question-item:hover {
  background-color: rgba(74, 123, 196, 0.05);
}

.question-checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.question-info {
  flex: 1;
}

.question-type-tag {
  display: inline-block;
  padding: 3px 8px;
  background-color: var(--bg-page);
  color: var(--text-secondary);
  border-radius: 4px;
  font-size: 11px;
  margin-right: 8px;
}

.question-text {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.4;
}

.question-meta {
  display: flex;
  gap: 12px;
}

.meta-item {
  font-size: 12px;
  color: var(--text-muted);
}

.question-count-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.count-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.count-item label {
  font-size: 13px;
  color: var(--text-secondary);
}

.difficulty-range {
  display: flex;
  align-items: center;
  gap: 12px;
}

.range-separator {
  color: var(--text-muted);
  font-weight: 500;
}

@media (max-width: 768px) {
  .teacher-main-content {
    margin-left: 60px;
  }
  
  .content-wrapper {
    padding: var(--spacing-lg);
  }
  
  .tabs {
    flex-wrap: wrap;
  }
  
  .exam-grid {
    grid-template-columns: 1fr;
  }
  
  .question-count-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
