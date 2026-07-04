<template>
  <div class="teacher-page-container">
    <TeacherSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['teacher-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="header-row">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
          返回
        </button>
        <h2>学生成绩详情</h2>
      </div>

      <div v-if="loading" class="loading-state">
        <p>加载中...</p>
      </div>

      <div v-else-if="error" class="empty-state">
        <p>{{ error }}</p>
      </div>

      <template v-else>
        <div class="result-summary">
          <div class="summary-header">
            <h3>{{ exam.title }}</h3>
            <span class="student-name">{{ studentName }}</span>
          </div>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">得分</span>
              <span class="info-value score-value">{{ record.score }}</span>
              <span class="info-unit">/ {{ record.total_score }} 分</span>
            </div>
            <div class="info-item">
              <span class="info-label">客观题</span>
              <span class="info-value auto-score-value">{{ record.auto_score || 0 }}</span>
              <span class="info-unit">分</span>
            </div>
            <div class="info-item">
              <span class="info-label">主观题</span>
              <span class="info-value manual-score-value">{{ (record.score || 0) - (record.auto_score || 0) }}</span>
              <span class="info-unit">分</span>
            </div>
            <div class="info-item">
              <span class="info-label">答题用时</span>
              <span class="info-value">{{ formatTime(record.time_spent) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">交卷时间</span>
              <span class="info-value small">{{ record.submit_time ? formatDate(record.submit_time) : '暂无' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">批改状态</span>
              <span :class="['status-badge', record.is_graded ? 'badge-graded' : 'badge-pending']">
                {{ record.is_graded ? '已批改' : '待批改' }}
              </span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h3>答题详情</h3>
          <div v-if="questions.length === 0" class="empty-state">
            <p>暂无答题数据</p>
          </div>
          <div v-else class="questions-list">
            <div v-for="(q, index) in questions" :key="q.id" class="question-card">
              <div class="question-header">
                <span class="question-number">{{ index + 1 }}</span>
                <span :class="['question-type', `type-${q.type}`]">{{ getTypeLabel(q.type) }}</span>
                <span class="question-score">{{ q.score }} 分</span>
                <span v-if="q.is_correct === true" class="badge-correct">正确 ✓</span>
                <span v-else-if="q.is_correct === false" class="badge-wrong">错误 ✗</span>
                <span v-else class="badge-pending">待批改</span>
              </div>
              <p class="question-content">{{ q.content }}</p>

              <div v-if="q.options && Object.keys(q.options).length > 0" class="options-list">
                <div v-for="(text, key) in q.options" :key="key"
                     :class="['option-item', getOptionClass(String(key), q)]">
                  <span class="option-key">{{ key }}</span>
                  <span class="option-text">{{ text }}</span>
                  <span v-if="isCorrectAnswer(String(key), q)" class="option-mark correct-mark">✓ 正确答案</span>
                  <span v-if="isWrongAnswer(String(key), q)" class="option-mark wrong-mark">✗ 学生选择</span>
                </div>
              </div>

              <div class="answer-info">
                <div class="answer-row">
                  <span class="answer-label">学生答案：</span>
                  <span class="answer-value">{{ q.user_answer || '未作答' }}</span>
                </div>
                <div v-if="q.correct_answer && q.is_correct !== null" class="answer-row">
                  <span class="answer-label">正确答案：</span>
                  <span class="answer-value correct-text">{{ q.correct_answer }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../utils/api'
import { formatDate, formatTime } from '../../utils/formatters'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const router = useRouter()
const route = useRoute()
const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})

const loading = ref(true)
const error = ref('')
const studentName = ref('')
const exam = ref<any>({})
const record = ref<any>({})
const questions = ref<any[]>([])
const examId = ref<number | null>(null)

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'single': '单选题',
    'multiple': '多选题',
    'judge': '判断题',
    'fill': '填空题',
    'essay': '简答题',
    'discussion': '论述题'
  }
  return labels[type] || type
}

const isCorrectAnswer = (key: string, q: any) => {
  if (q.type === 'multiple') {
    return String(q.correct_answer).split(',').map((s: string) => s.trim()).includes(key)
  }
  return key === q.correct_answer
}

const isWrongAnswer = (key: string, q: any) => {
  if (q.is_correct !== false) return false
  if (q.type === 'multiple') {
    const stuAnswers = String(q.user_answer).split(',').map((s: string) => s.trim())
    const correctAnswers = String(q.correct_answer).split(',').map((s: string) => s.trim())
    return stuAnswers.includes(key) && !correctAnswers.includes(key)
  }
  return key === q.user_answer && key !== q.correct_answer
}

const getOptionClass = (key: string, q: any) => {
  const classes: string[] = []
  if (isCorrectAnswer(key, q)) classes.push('option-correct')
  if (isWrongAnswer(key, q)) classes.push('option-wrong')
  return classes
}

const goBack = () => {
  if (examId.value) {
    router.push(`/teacher/exam/${examId.value}`)
  } else {
    router.push('/teacher/exams')
  }
}

const loadResult = async () => {
  const recordId = route.params.recordId
  if (!recordId) {
    error.value = '缺少记录ID'
    loading.value = false
    return
  }
  try {
    const response = await api.get(`teacher/result/${recordId}/`)
    const data = response.data
    studentName.value = data.student_name || ''
    exam.value = data.exam || {}
    record.value = data.record || {}
    questions.value = data.questions || []
    examId.value = data.exam_id || null
  } catch (err: any) {
    console.error('Failed to load result:', err)
    error.value = err.response?.data?.error || '加载成绩详情失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadResult()
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
  padding: 24px;
}

.teacher-main-content.sidebar-collapsed {
  margin-left: 60px;
}

.header-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header-row h2 {
  font-size: 22px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
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
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f5f5f5;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
  font-size: 16px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  color: var(--text-secondary);
}

.result-summary {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.summary-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.student-name {
  font-size: 14px;
  color: #64748b;
  padding: 4px 12px;
  background: #f1f5f9;
  border-radius: 6px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.info-label {
  font-size: 12px;
  color: #94a3b8;
}

.info-value {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
}

.info-value.small {
  font-size: 14px;
  font-weight: 500;
}

.score-value {
  color: #2563eb;
}

.auto-score-value {
  color: #16a34a;
}

.manual-score-value {
  color: #d97706;
}

.info-unit {
  font-size: 12px;
  color: #94a3b8;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
}

.badge-graded {
  background: #dcfce7;
  color: #166534;
}

.badge-pending {
  background: #fef3c7;
  color: #92400e;
}

.detail-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.detail-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-card {
  padding: 20px;
  background: #fafafa;
  border-radius: 12px;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.question-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #eef2ff;
  color: #4f46e5;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.question-type {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.type-single { background: #e3f2fd; color: #1565c0; }
.type-multiple { background: #e8f5e9; color: #2e7d32; }
.type-judge { background: #fff3e0; color: #e65100; }
.type-fill { background: #fce4ec; color: #c2185b; }
.type-essay { background: #f3e5f5; color: #7b1fa2; }
.type-discussion { background: #fce4ec; color: #d81b60; }

.question-score {
  font-size: 12px;
  color: #94a3b8;
  margin-left: auto;
}

.badge-correct {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  background: #dcfce7;
  color: #166534;
}

.badge-wrong {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  background: #fee2e2;
  color: #dc2626;
}

.question-content {
  font-size: 15px;
  color: #334155;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s;
}

.option-item.option-correct {
  background: #f0fdf4;
  border-color: #86efac;
}

.option-item.option-wrong {
  background: #fef2f2;
  border-color: #fca5a5;
}

.option-key {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e2e8f0;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  flex-shrink: 0;
}

.option-text {
  font-size: 14px;
  color: #334155;
  flex: 1;
}

.option-mark {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}

.correct-mark {
  background: #dcfce7;
  color: #166534;
}

.wrong-mark {
  background: #fee2e2;
  color: #dc2626;
}

.answer-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.answer-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.answer-label {
  color: #94a3b8;
  flex-shrink: 0;
}

.answer-value {
  color: #334155;
  font-weight: 500;
}

.correct-text {
  color: #166534;
}
</style>