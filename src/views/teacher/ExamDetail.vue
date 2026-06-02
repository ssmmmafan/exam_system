<template>
  <div class="teacher-page-container">
    <TeacherSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['teacher-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="teacher-top-header">
        <div class="header-left">
          <button class="back-btn" @click="router.push('/teacher/exams')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M15 18l-6-6 6-6"/>
            </svg>
            <span>返回</span>
          </button>
          <h1>考试详情</h1>
        </div>
        <div class="btn-group">
          <button v-if="exam.status === 'draft'" class="btn btn-primary" @click="publishExam">发布考试</button>
          <button v-if="exam.status === 'published'" class="btn btn-warning" @click="unpublishExam">取消发布</button>
          <button v-if="exam.status === 'draft'" class="btn btn-danger" @click="deleteExam">删除考试</button>
        </div>
      </div>

      <div class="content-wrapper exam-detail-wrapper">
        <div class="detail-section">
          <div class="section-header">
            <h2>考试信息</h2>
            <span :class="['status-tag', `status-${exam.status}`]">{{ statusText }}</span>
          </div>
          
          <div class="detail-grid">
            <div class="detail-item">
              <label>考试名称</label>
              <span>{{ exam.title }}</span>
            </div>
            <div class="detail-item">
              <label>考试描述</label>
              <span>{{ exam.description || '-' }}</span>
            </div>
            <div class="detail-item">
              <label>开始时间</label>
              <span>{{ formatDateTime(exam.start_time) }}</span>
            </div>
            <div class="detail-item">
              <label>结束时间</label>
              <span>{{ formatDateTime(exam.end_time) }}</span>
            </div>
            <div class="detail-item">
              <label>考试时长</label>
              <span>{{ exam.duration }} 分钟</span>
            </div>
            <div class="detail-item">
              <label>总分</label>
              <span>{{ exam.total_score }} 分</span>
            </div>
            <div class="detail-item">
              <label>题目数量</label>
              <span>{{ exam.question_count }} 题</span>
            </div>
            <div class="detail-item">
              <label>参与学生</label>
              <span>{{ exam.student_count || 0 }} 人</span>
            </div>
            <div class="detail-item">
              <label>随机题目顺序</label>
              <span>{{ exam.random_questions ? '是' : '否' }}</span>
            </div>
            <div class="detail-item">
              <label>随机选项顺序</label>
              <span>{{ exam.random_options ? '是' : '否' }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h2>题目列表</h2>
          <div v-if="questions.length === 0" class="empty-state">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <path d="M14 2v6h6"/>
            </svg>
            <p>该考试暂无题目</p>
          </div>
          <div v-else>
            <div class="type-summary">
              <span v-if="typeCounts.single" class="summary-tag type-single">单选题 {{ typeCounts.single }} 题</span>
              <span v-if="typeCounts.multiple" class="summary-tag type-multiple">多选题 {{ typeCounts.multiple }} 题</span>
              <span v-if="typeCounts.judge" class="summary-tag type-judge">判断题 {{ typeCounts.judge }} 题</span>
              <span v-if="typeCounts.fill" class="summary-tag type-fill">填空题 {{ typeCounts.fill }} 题</span>
              <span v-if="typeCounts.essay" class="summary-tag type-essay">简答题 {{ typeCounts.essay }} 题</span>
              <span v-if="typeCounts.discussion" class="summary-tag type-discussion">论述题 {{ typeCounts.discussion }} 题</span>
              <span class="summary-total">共 {{ questions.length }} 题，{{ exam.total_score }} 分</span>
            </div>
            <div class="question-list">
              <div v-for="(question, index) in questions" :key="question.id" class="question-card">
              <div class="question-header">
                <span class="question-number">{{ index + 1 }}</span>
                <span class="question-type">{{ getQuestionTypeLabel(question.type) }}</span>
                <span class="question-score">{{ question.score }}分</span>
              </div>
              <p class="question-content">{{ question.content }}</p>
              <div v-if="question.options" class="question-options">
                <div v-for="(option, key) in question.options" :key="key" class="option-item">
                  <span class="option-key">{{ key }}</span>
                  <span>{{ option }}</span>
                </div>
              </div>
              <div v-if="question.type === 'fill'" class="question-answer">
                <label>正确答案：</label>
                <span>{{ question.answer }}</span>
              </div>
              <div v-if="question.type === 'essay'" class="question-answer">
                <label>参考答案：</label>
                <span>{{ question.answer }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

        <div class="detail-section">
          <h2>学生答题情况</h2>
          <div v-if="examRecords.length === 0" class="empty-state">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            <p>暂无学生答题记录</p>
          </div>
          <div v-else class="records-table">
            <table>
              <thead>
                <tr>
                  <th>学号</th>
                  <th>学生姓名</th>
                  <th>班级</th>
                  <th>答题状态</th>
                  <th>得分</th>
                  <th>提交时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in examRecords" :key="record.id">
                  <td>{{ record.student_id || '-' }}</td>
                  <td>{{ record.student_name }}</td>
                  <td>{{ record.class_name || '-' }}</td>
                  <td>
                    <span :class="['status-badge', `badge-${record.status}`]">
                      {{ getRecordStatusText(record.status) }}
                    </span>
                  </td>
                  <td>{{ record.score !== null ? record.score + ' 分' : '-' }}</td>
                  <td>{{ record.submit_time ? formatDateTime(record.submit_time) : '-' }}</td>
                  <td>
                    <button v-if="record.status === 'finished'" class="btn btn-sm btn-secondary" @click="gradeExam(record.id)">批改</button>
                    <button v-else-if="record.status === 'graded'" class="btn btn-sm btn-primary" @click="viewScore(record.id)">查看得分情况</button>
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
import { useRouter, useRoute } from 'vue-router'
import api from '../../utils/api'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const router = useRouter()
const route = useRoute()
const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})

const exam = ref({
  id: 0,
  title: '',
  description: '',
  start_time: '',
  end_time: '',
  duration: 0,
  total_score: 0,
  question_count: 0,
  student_count: 0,
  random_questions: false,
  random_options: false,
  status: 'draft'
})

interface ExamQuestion {
  id: number
  type: string
  content: string
  options?: Record<string, string>
  answer: string
  score: number
  order: number
}

interface ExamRecordItem {
  id: number
  student_id: string
  student_name: string
  class_name: string
  status: string
  score: number | null
  submit_time: string | null
}

const questions = ref<ExamQuestion[]>([])
const examRecords = ref<ExamRecordItem[]>([])

const statusText = computed(() => {
  const texts: Record<string, string> = {
    'draft': '草稿',
    'published': '已发布',
    'ongoing': '进行中',
    'finished': '已结束'
  }
  return texts[exam.value.status] || exam.value.status
})

const typeCounts = computed(() => {
  const counts: Record<string, number> = {}
  for (const q of questions.value) {
    counts[q.type] = (counts[q.type] || 0) + 1
  }
  return counts
})

const getQuestionTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'single': '单选题',
    'multiple': '多选题',
    'judge': '判断题',
    'fill': '填空题',
    'essay': '简答题'
  }
  return labels[type] || type
}

const getRecordStatusText = (status: string) => {
  const texts: Record<string, string> = {
    'ongoing': '进行中',
    'finished': '待批改',
    'graded': '已批改'
  }
  return texts[status] || status
}

const formatDateTime = (dateStr: string) => {
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

const loadExamDetail = async () => {
  const examId = route.params.examId
  if (!examId) {
    console.error('Exam ID is missing')
    return
  }
  try {
    const response = await api.get(`teacher/exams/${examId}/`)
    exam.value = response.data.exam || exam.value
    questions.value = response.data.questions || []
    examRecords.value = response.data.records || []
  } catch (error: any) {
    console.error('Failed to load exam detail:', error)
    const errorMessage = error.response?.data?.error || '加载考试详情失败'
    alert(errorMessage)
  }
}

const publishExam = async () => {
  try {
    const response = await api.post(`teacher/exams/${exam.value.id}/publish/`)
    exam.value.status = 'published'
    exam.value.is_published = true
    alert('考试发布成功')
  } catch (error: any) {
    console.error('Failed to publish exam:', error)
    const errorMessage = error.response?.data?.error || '发布失败，请重试'
    if (errorMessage.includes('already published')) {
      alert('该考试已经发布')
    } else {
      alert(errorMessage)
    }
  }
}

const unpublishExam = async () => {
  try {
    await api.post(`teacher/exams/${exam.value.id}/unpublish/`)
    exam.value.status = 'draft'
    alert('考试已取消发布')
  } catch (error) {
    console.error('Failed to unpublish exam:', error)
    alert('取消发布失败，请重试')
  }
}

const deleteExam = async () => {
  if (!confirm('确定要删除这个考试吗？')) return
  try {
    await api.delete(`teacher/exams/${exam.value.id}/delete/`)
    router.push('/teacher/exams')
  } catch (error) {
    console.error('Failed to delete exam:', error)
    alert('删除失败，请重试')
  }
}

const gradeExam = (recordId: number) => {
  router.push(`/teacher/grade/${recordId}`)
}

const viewScore = (recordId: number) => {
  router.push(`/teacher/result/${recordId}`)
}

onMounted(() => {
  loadExamDetail()
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
  transition: margin-left 0.3s ease;
}

.teacher-main-content.sidebar-collapsed {
  margin-left: 60px;
}

.exam-detail-wrapper {
  padding: 24px;
}

.detail-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.status-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-draft {
  background: #f5f5f5;
  color: #999;
}

.status-published {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-ongoing {
  background: #fff3e0;
  color: #ef6c00;
}

.status-finished {
  background: #e0e0e0;
  color: #616161;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.detail-item {
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 8px;
}

.detail-item label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.detail-item span {
  font-size: 14px;
  color: var(--text-primary);
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.type-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.summary-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.summary-tag.type-single { background: #e3f2fd; color: #1565c0; }
.summary-tag.type-multiple { background: #e8f5e9; color: #2e7d32; }
.summary-tag.type-judge { background: #fff3e0; color: #e65100; }
.summary-tag.type-fill { background: #fce4ec; color: #c2185b; }
.summary-tag.type-essay { background: #f3e5f5; color: #7b1fa2; }
.summary-tag.type-discussion { background: #fce4ec; color: #d81b60; }

.summary-total {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: auto;
}

.question-card {
  padding: 20px;
  background: #fafafa;
  border-radius: 12px;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.question-number {
  width: 28px;
  height: 28px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.question-type {
  padding: 4px 10px;
  background: rgba(74, 123, 196, 0.1);
  color: var(--primary-color);
  border-radius: 4px;
  font-size: 12px;
}

.question-score {
  font-size: 13px;
  color: var(--text-muted);
  margin-left: auto;
}

.question-content {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
  margin: 0 0 12px 0;
}

.question-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: white;
  border-radius: 6px;
  font-size: 13px;
}

.option-key {
  font-weight: 600;
  color: var(--primary-color);
}

.question-answer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #e0e0e0;
  font-size: 13px;
}

.question-answer label {
  color: var(--text-muted);
}

.question-answer span {
  color: var(--text-primary);
}

.records-table {
  overflow-x: auto;
}

.records-table table {
  width: 100%;
  border-collapse: collapse;
}

.records-table th,
.records-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.records-table th {
  background: #fafafa;
  font-weight: 600;
  font-size: 13px;
  color: var(--text-secondary);
}

.records-table td {
  font-size: 14px;
  color: var(--text-primary);
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-ongoing {
  background: #fff3e0;
  color: #ef6c00;
}

.badge-finished {
  background: #e3f2fd;
  color: #1976d2;
}

.badge-graded {
  background: #e8f5e9;
  color: #2e7d32;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: none;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  margin-right: 16px;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f5f5f5;
}

.header-left {
  display: flex;
  align-items: center;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  width: 40px;
  height: 40px;
  margin-bottom: 12px;
  color: var(--text-muted);
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}
</style>