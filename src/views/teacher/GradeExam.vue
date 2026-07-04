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
        <h2>批改试卷</h2>
        <div class="header-info">
          <span class="student-info">学生：{{ studentName }}</span>
          <span class="exam-total">满分：{{ totalScoreFull }} 分</span>
        </div>
      </div>
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      <div v-else-if="loadError" class="empty-state">
        <p style="color: #dc3545;">{{ loadError }}</p>
        <button class="btn btn-secondary" @click="loadGradeData" style="margin-top: 12px;">重新加载</button>
      </div>
      <template v-else>
      <div v-if="record" class="exam-info">
        <div class="exam-info-row">
          <h3>{{ record.exam_title }}</h3>
          <span v-if="record.reviewed_at" class="reviewed-badge">已批改</span>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">提交时间</span>
            <span class="info-value">{{ record.submit_time || '暂无' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">批改状态</span>
            <span v-if="record.reviewed_at" class="info-value reviewed">已批改 ({{ record.reviewed_at }})</span>
            <span v-else class="info-value pending">待批改</span>
          </div>
          <div class="info-item">
            <span class="info-label">客观题</span>
            <span class="info-value">{{ autoScore }} / {{ maxAutoScore }} 分</span>
          </div>
          <div class="info-item">
            <span class="info-label">主观题</span>
            <span class="info-value">{{ manualScore }} / {{ maxManualScore }} 分</span>
          </div>
        </div>
      </div>
      <div class="questions-list">
        <div v-if="questions.length === 0" class="empty-state">暂无题目</div>
        <div v-for="(question, index) in questions" :key="question.id" class="question-item">
          <div class="question-header">
            <span class="question-number">{{ index + 1 }}</span>
            <span class="question-type">{{ getTypeName(question.type) }}</span>
            <span class="question-score">{{ question.score }} 分</span>
            <span v-if="isAutoGraded(question.type)" :class="getAutoBadgeClass(question)">{{ getAutoBadgeText(question) }}</span>
            <span v-else class="manual-badge">待批改</span>
          </div>
          <div class="question-content">{{ question.content }}</div>
          <div v-if="question.type === 'single' || question.type === 'multiple'" class="question-options">
            <div v-for="(opt, key) in question.options" :key="key" :class="getOptionClass(key, question)">
              <span>{{ key }}. {{ opt }}</span>
            </div>
          </div>
          <div class="answer-section">
            <div class="answer-row">
              <span class="label">正确答案：</span>
              <span class="correct-answer">{{ question.answer }}</span>
            </div>
            <div class="answer-row">
              <span class="label">学生答案：</span>
              <span v-if="question.type === 'essay' || question.type === 'discussion'" class="essay-answer-text">{{ studentAnswers[question.id] || '未作答' }}</span>
              <span v-else :class="isCorrect(question) === true ? 'correct' : (isCorrect(question) === false ? 'incorrect' : '')">
                {{ formatStudentAnswer(studentAnswers[question.id]) || '未作答' }}
              </span>
            </div>
            <div v-if="question.type === 'fill' && question.answer" class="fill-hint">
              <span class="label">提示：</span>
              <span>不区分大小写，填正确答案或同义词均可</span>
            </div>
            <div v-if="question.type === 'essay' || question.type === 'discussion'" class="essay-section">
              <label>给分（0-{{ question.score }}分）</label>
              <div class="essay-score-row">
                <input
                  type="number"
                  v-model.number="essayScores[question.id]"
                  :max="question.score"
                  :min="0"
                  class="score-input"
                  @input="validateScore(question.id, question.score)"
                />
                <span class="score-range">/ {{ question.score }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="submit-section">
        <div class="total-score">
          <div class="total-detail">
            <span class="label">客观题：</span>
            <span class="detail-value">{{ autoScore }} / {{ maxAutoScore }}</span>
            <span class="label-sep">|</span>
            <span class="label">主观题：</span>
            <span class="detail-value">{{ manualScore }} / {{ maxManualScore }}</span>
          </div>
          <div class="total-final">
            <span class="label">总分：</span>
            <span class="total-value">{{ totalScore }} / {{ totalScoreFull }}</span>
          </div>
        </div>
        <div class="submit-actions">
          <button class="btn btn-secondary" @click="goBack">取消</button>
          <button @click="submitGrading" class="btn btn-primary" :disabled="submitting">
            {{ submitting ? '提交中...' : '提交批改' }}
          </button>
        </div>
      </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../utils/api'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const route = useRoute()
const router = useRouter()
const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})
const recordId = ref(route.params.recordId)
const record = ref(null)
const questions = ref([])
const studentAnswers = ref({})
const essayScores = ref({})
const studentName = ref('')
const autoScore = ref(0)
const totalScoreFull = ref(0)
const submitting = ref(false)
const loading = ref(true)
const loadError = ref('')

const loadGradeData = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const response = await api.get(`teacher/grade/${recordId.value}/`)
    record.value = response.data
    questions.value = response.data.questions || []
    studentAnswers.value = response.data.student_answers || {}
    studentName.value = response.data.student_name || ''
    autoScore.value = response.data.auto_score || 0
    totalScoreFull.value = response.data.total_score || 0

    questions.value.forEach(q => {
      if (q.type === 'essay' || q.type === 'discussion') {
        essayScores.value[q.id] = response.data.essay_scores?.[q.id] || 0
      }
    })
  } catch (error: any) {
    console.error('Failed to load grade data:', error)
    loadError.value = error.response?.data?.error || '加载批改数据失败，请重试'
  } finally {
    loading.value = false
  }
}

onMounted(loadGradeData)

const getTypeName = (type: string) => {
  const types: Record<string, string> = {
    single: '单选题',
    multiple: '多选题',
    judge: '判断题',
    essay: '简答题',
    fill: '填空题',
    discussion: '论述题',
  }
  return types[type] || type
}

const isAutoGraded = (type: string) => {
  return ['single', 'multiple', 'judge', 'fill'].includes(type)
}

const maxAutoScore = computed(() => {
  return questions.value
    .filter(q => isAutoGraded(q.type))
    .reduce((sum, q) => sum + (q.score || 0), 0)
})

const maxManualScore = computed(() => {
  return questions.value
    .filter(q => !isAutoGraded(q.type))
    .reduce((sum, q) => sum + (q.score || 0), 0)
})

const getAutoBadgeClass = (question: any) => {
  const result = isCorrect(question)
  if (result === true) return 'auto-badge badge-correct'
  if (result === false) return 'auto-badge badge-wrong'
  return 'auto-badge'
}

const getAutoBadgeText = (question: any) => {
  const result = isCorrect(question)
  if (result === true) return '正确 ✓'
  if (result === false) return '错误 ✗'
  return '自动判分'
}

const getOptionClass = (key: string | number, question: { id: number; answer: string }) => {
  const optionKey = String(key)
  const studentAnswer = studentAnswers.value[question.id] || ''
  const correctKeys = String(question.answer).split(',').map(s => s.trim())
  const selectedKeys = String(studentAnswer).split(',').map(s => s.trim())
  const isCorrectOption = correctKeys.includes(optionKey)
  const isSelected = selectedKeys.includes(optionKey)

  if (isCorrectOption && isSelected) return 'option-item option-correct'
  if (isCorrectOption) return 'option-item option-correct-only'
  if (isSelected) return 'option-item option-wrong'
  return 'option-item'
}

const isCorrect = (question: any) => {
  if (question.type === 'essay' || question.type === 'discussion') return null
  const studentAnswer = String(studentAnswers.value[question.id] || '').trim()
  const correctAnswer = String(question.answer).trim()

  if (question.type === 'multiple') {
    const sSet = new Set(studentAnswer.split(',').map(s => s.trim()))
    const cSet = new Set(correctAnswer.split(',').map(s => s.trim()))
    if (sSet.size !== cSet.size) return false
    for (const s of sSet) if (!cSet.has(s)) return false
    return true
  }
  return studentAnswer.toLowerCase() === correctAnswer.toLowerCase()
}

const formatStudentAnswer = (answer: any) => {
  if (answer === null || answer === undefined) return ''
  if (Array.isArray(answer)) return answer.join(', ')
  return String(answer)
}

const manualScore = computed(() => {
  let total = 0
  Object.values(essayScores.value).forEach(s => {
    total += Number(s) || 0
  })
  return total
})

const validateScore = (questionId: number, maxScore: number) => {
  let val = essayScores.value[questionId]
  if (val === null || val === undefined || isNaN(Number(val))) {
    essayScores.value[questionId] = 0
  } else if (Number(val) > maxScore) {
    essayScores.value[questionId] = maxScore
  } else if (Number(val) < 0) {
    essayScores.value[questionId] = 0
  }
}

const totalScore = computed(() => {
  return (autoScore.value || 0) + manualScore.value
})

const goBack = () => {
  if (record.value?.exam_id) {
    router.push(`/teacher/exam/${record.value.exam_id}`)
  } else {
    router.push('/teacher/exams')
  }
}

const submitGrading = async () => {
  for (const q of questions.value) {
    if (q.type === 'essay' || q.type === 'discussion') {
      const score = Number(essayScores.value[q.id]) || 0
      if (score > q.score) {
        alert(`第${questions.value.indexOf(q) + 1}题分数不能超过${q.score}分`)
        return
      }
    }
  }
  submitting.value = true
  try {
    await api.post(`teacher/grade/${recordId.value}/submit/`, {
      essay_scores: essayScores.value
    })
    alert('批改成功！')
    goBack()
  } catch (error: any) {
    console.error('Failed to submit grading:', error)
    alert(error.response?.data?.error || '批改失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.teacher-page-container {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.teacher-main-content {
  flex: 1;
  margin-left: 220px;
  padding: 2rem;
  transition: margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.teacher-main-content.sidebar-collapsed {
  margin-left: 64px;
}

.header-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.header-row h2 {
  margin: 0;
  flex: 1;
}

.header-info {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.student-info {
  font-size: 1.1rem;
  color: #666;
}

.exam-total {
  font-size: 1rem;
  color: #0d6efd;
  font-weight: bold;
  background: #e7f3ff;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  color: #666;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f5f5f5;
  color: #333;
}

.exam-info {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.5rem;
}

.exam-info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.exam-info-row h3 {
  margin: 0;
  font-size: 1.2rem;
}

.reviewed-badge {
  background: #d4edda;
  color: #155724;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.8rem;
  color: #999;
}

.info-value {
  font-size: 0.95rem;
  color: #333;
}

.info-value.reviewed {
  color: #155724;
  font-weight: 500;
}

.info-value.pending {
  color: #856404;
  font-weight: 500;
}

.score-breakdown {
  display: flex;
  gap: 2rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #eee;
}

.auto-score-label {
  color: #155724;
  font-size: 1rem;
}

.manual-score-label {
  color: #856404;
  font-size: 1rem;
}

.questions-list {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  padding: 1.5rem;
}

.auto-badge {
  padding: 0.15rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  margin-left: auto;
}

.badge-correct {
  background: #d4edda;
  color: #155724;
}

.badge-wrong {
  background: #f8d7da;
  color: #721c24;
}

.manual-badge {
  background: #fff3cd;
  color: #856404;
  padding: 0.15rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  margin-left: auto;
}

.question-item {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.question-item:last-child {
  border-bottom: none;
}

.question-header {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
}

.question-number {
  width: 28px;
  height: 28px;
  background: #0d6efd;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.question-type {
  background: #0d6efd;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.8rem;
}

.question-score {
  color: #666;
  font-size: 0.9rem;
}

.question-content {
  font-size: 1.05rem;
  margin-bottom: 1rem;
  line-height: 1.6;
}

.question-options {
  margin-bottom: 1rem;
}

.option-item {
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.25rem;
  border-radius: 0.25rem;
  background: #f8f9fa;
}

.option-correct {
  background: #d4edda;
  color: #155724;
}

.option-correct-only {
  background: #e7f3ff;
  color: #0c63e4;
}

.option-wrong {
  background: #f8d7da;
  color: #721c24;
}

.answer-section {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.25rem;
}

.answer-row {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.answer-row:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: bold;
  color: #666;
  margin-right: 0.25rem;
}

.correct-answer {
  color: #28a745;
  font-weight: 600;
}

.correct {
  color: #28a745;
  font-weight: 600;
}

.incorrect {
  color: #dc3545;
  font-weight: 600;
}

.essay-answer-text {
  display: block;
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 0.25rem;
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 0.95rem;
  max-height: 200px;
  overflow-y: auto;
}

.fill-hint {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #999;
}

.essay-section {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px dashed #ddd;
}

.essay-section label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #333;
}

.essay-score-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.score-input {
  width: 80px;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  font-size: 1rem;
  text-align: center;
}

.score-input:focus {
  outline: none;
  border-color: #0d6efd;
  box-shadow: 0 0 0 2px rgba(13, 110, 253, 0.15);
}

.score-range {
  color: #999;
  font-size: 0.9rem;
}

.submit-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.total-score {
  font-size: 1.1rem;
}

.total-detail {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.label-sep {
  color: #ddd;
}

.detail-value {
  font-weight: bold;
  color: #333;
}

.total-final {
  font-size: 1.3rem;
}

.total-value {
  font-weight: bold;
  color: #0d6efd;
  font-size: 1.6rem;
}

.submit-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn {
  padding: 0.75rem 2rem;
  border-radius: 0.25rem;
  font-size: 1rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #0d6efd;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0b5ed7;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5c636a;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #999;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e0e0e0;
  border-top-color: #0d6efd;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>