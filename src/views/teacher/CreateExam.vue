<template>
  <div class="teacher-page-container">
    <TeacherSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['teacher-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="teacher-top-header">
        <div class="header-left">
          <button @click="goBack" class="back-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <line x1="19" y1="12" x2="5" y2="12"/>
              <polyline points="12 19 5 12 12 5"/>
            </svg>
          </button>
          <h1>创建考试</h1>
        </div>
      </div>
      <div class="content-wrapper">
        <form @submit.prevent="createExam" class="create-exam-form">
          <div class="form-group">
            <label class="form-label" for="exam-title">考试名称</label>
            <input 
              type="text" 
              id="exam-title" 
              v-model="examForm.title" 
              class="form-input" 
              placeholder="请输入考试名称"
              required 
            />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="exam-start-time">开始时间</label>
              <input 
                type="datetime-local" 
                id="exam-start-time" 
                v-model="examForm.start_time" 
                class="form-input" 
                required 
              />
            </div>
            <div class="form-group">
              <label class="form-label" for="exam-end-time">结束时间</label>
              <input 
                type="datetime-local" 
                id="exam-end-time" 
                v-model="examForm.end_time" 
                class="form-input" 
                required 
              />
            </div>
          </div>
          <div v-if="timeError" class="error-message">
            {{ timeError }}
          </div>
          <div class="form-group">
            <label class="form-label">选择题目</label>
            <button type="button" @click="showQuestionSelectModal = true" class="btn btn-secondary">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <path d="M14 2v6h6"/>
              </svg>
              <span>选择题目 (已选 {{ selectedQuestions.length }} 题)</span>
            </button>
          </div>
          <div v-if="selectedQuestions.length > 0" class="selected-questions-preview">
            <div class="preview-header">
              <span>已选题目</span>
              <span class="preview-count">{{ selectedQuestions.length }} 题，共 {{ totalScore }} 分</span>
            </div>
            <div v-for="q in selectedQuestions" :key="q.id" class="selected-question-item">
              <span class="question-type">{{ getQuestionTypeLabel(q.type) }}</span>
              <span class="question-content">{{ truncateText(q.content, 40) }}</span>
              <div class="score-input-wrapper">
                <input 
                  type="number" 
                  class="score-input" 
                  :value="customScores.get(q.id) ?? q.score" 
                  @input="(e) => customScores.set(q.id, Number((e.target as HTMLInputElement).value))"
                  min="1" 
                  max="100"
                  placeholder="分数"
                />
                <span class="score-unit">分</span>
                <span class="default-score">(默认: {{ q.score }})</span>
              </div>
              <button @click="removeSelectedQuestion(q.id)" class="remove-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-checkbox">
              <input type="checkbox" id="exam-random-questions" v-model="examForm.random_questions" />
              <span>随机题目顺序</span>
            </label>
          </div>
          <div class="form-group">
            <label class="form-checkbox">
              <input type="checkbox" id="exam-random-options" v-model="examForm.random_options" />
              <span>随机选项顺序</span>
            </label>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="goBack">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="!canSubmit">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17 21 17 13 7 13 7 21"/>
                <polyline points="7 3 7 8 15 8"/>
              </svg>
              <span>创建考试</span>
            </button>
          </div>
        </form>
      </div>
    </div>
    <Teleport to="body">
      <div v-if="showQuestionSelectModal" class="modal-overlay" @click.self="closeQuestionSelectModal">
        <div class="modal question-select-modal">
          <div class="modal-header">
            <h3>选择题目</h3>
            <button class="modal-close" @click="closeQuestionSelectModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="filter-bar">
              <select v-model="questionFilter.type" class="form-select filter-select">
                <option value="">全部题型</option>
                <option value="single">单选题</option>
                <option value="multiple">多选题</option>
                <option value="judge">判断题</option>
                <option value="fill">填空题</option>
                <option value="essay">简答题</option>
              </select>
              <input 
                type="text" 
                v-model="questionFilter.keyword" 
                class="form-input filter-input" 
                placeholder="搜索题目内容..."
              />
            </div>
            <div class="question-list">
              <div v-for="question in filteredQuestions" :key="question.id" class="question-item">
                <label class="question-checkbox">
                  <input 
                    type="checkbox" 
                    :id="`question-${question.id}`"
                    :checked="isQuestionSelected(question.id)"
                    @change="() => toggleQuestionSelect(question)"
                  />
                </label>
                <div class="question-info">
                  <span class="question-type-tag">{{ getQuestionTypeLabel(question.type) }}</span>
                  <p class="question-text">{{ question.content }}</p>
                </div>
                <div class="question-meta">
                  <span class="meta-item">{{ question.score }}分</span>
                  <span class="meta-item">难度{{ question.difficulty }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeQuestionSelectModal">取消</button>
            <button type="button" class="btn btn-primary" @click="confirmQuestionSelect">确认选择</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, inject } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'
import type { Question } from '../../types'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const router = useRouter()
const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})

const questions = ref<Question[]>([])
const showQuestionSelectModal = ref(false)
const selectedQuestions = ref<Question[]>([])
const questionFilter = ref({
  type: '',
  keyword: ''
})
const customScores = ref<Map<number, number>>(new Map())

const examForm = ref({
  title: '',
  start_time: '',
  end_time: '',
  random_questions: false,
  random_options: false
})

const getQuestionScore = (question: Question) => {
  const custom = customScores.value.get(question.id)
  return custom !== undefined ? custom : question.score
}

const totalScore = computed(() => {
  return selectedQuestions.value.reduce((sum, q) => sum + getQuestionScore(q), 0)
})

const timeError = ref('')

const canSubmit = computed(() => {
  const hasTitle = examForm.value.title
  const hasStartTime = examForm.value.start_time
  const hasEndTime = examForm.value.end_time
  const hasQuestions = selectedQuestions.value.length > 0
  
  if (hasStartTime && hasEndTime) {
    const start = new Date(examForm.value.start_time)
    const end = new Date(examForm.value.end_time)
    if (end <= start) {
      timeError.value = '结束时间必须大于开始时间'
      return false
    }
    timeError.value = ''
  } else {
    timeError.value = ''
  }
  
  return hasTitle && hasStartTime && hasEndTime && hasQuestions
})

const filteredQuestions = computed(() => {
  let result = questions.value
  if (questionFilter.value.type) {
    result = result.filter(q => q.type === questionFilter.value.type)
  }
  if (questionFilter.value.keyword) {
    const keyword = questionFilter.value.keyword.toLowerCase()
    result = result.filter(q => q.content.toLowerCase().includes(keyword))
  }
  return result
})

const getQuestionTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'single': '单选',
    'multiple': '多选',
    'judge': '判断',
    'fill': '填空',
    'essay': '简答'
  }
  return labels[type] || type
}

const truncateText = (text: string, maxLength: number) => {
  if (!text) return ''
  return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
}

const loadQuestions = async () => {
  try {
    console.log('Loading questions...')
    const response = await api.get('teacher/questions/', { params: { per_page: 1000 } })
    console.log('Questions response:', response.data)
    const data = response.data
    questions.value = data && Array.isArray(data.questions) ? data.questions : []
    console.log('Questions loaded:', questions.value.length)
  } catch (error) {
    console.error('Failed to load questions:', error)
    questions.value = []
  }
}

const isQuestionSelected = (questionId: number) => {
  return selectedQuestions.value.some(q => q.id === questionId)
}

const toggleQuestionSelect = (question: Question) => {
  const index = selectedQuestions.value.findIndex(q => q.id === question.id)
  if (index > -1) {
    selectedQuestions.value.splice(index, 1)
  } else {
    selectedQuestions.value.push(question)
  }
}

const removeSelectedQuestion = (questionId: number) => {
  selectedQuestions.value = selectedQuestions.value.filter(q => q.id !== questionId)
}

const closeQuestionSelectModal = () => {
  console.log('Closing modal')
  showQuestionSelectModal.value = false
}

const confirmQuestionSelect = () => {
  console.log('Confirming selection, selected:', selectedQuestions.value.length)
  showQuestionSelectModal.value = false
}

const goBack = () => {
  router.push('/teacher/exams')
}

const createExam = async () => {
  try {
    const questionIds = selectedQuestions.value.map(q => q.id)
    const totalScoreValue = totalScore.value
    
    const questionScores: Record<number, number> = {}
    selectedQuestions.value.forEach(q => {
      const customScore = customScores.value.get(q.id)
      if (customScore !== undefined) {
        questionScores[q.id] = customScore
      }
    })
    
    const data = {
      ...examForm.value,
      question_ids: questionIds,
      question_count: questionIds.length,
      total_score: totalScoreValue,
      question_scores: questionScores
    }
    
    await api.post('teacher/exams/create/', data)
    alert('考试创建成功！')
    router.push('/teacher/exams')
  } catch (error) {
    console.error('Failed to create exam:', error)
    alert('创建失败，请重试')
  }
}

onMounted(() => {
  loadQuestions()
})

// 调试：监控模态框状态变化
watch(showQuestionSelectModal, (newVal, oldVal) => {
  console.log('Modal state changed:', oldVal, '->', newVal)
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
  transition: margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.teacher-main-content.sidebar-collapsed {
  margin-left: 64px;
}

.teacher-main-content {
  flex-direction: column;
  min-height: 100vh;
}

.teacher-top-header {
  background: linear-gradient(135deg, var(--bg-top-header) 0%, #3A5A8C 100%);
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  padding: 8px;
  cursor: pointer;
  color: white;
  transition: all 0.2s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.back-btn svg {
  width: 20px;
  height: 20px;
}

.teacher-top-header h1 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: var(--text-white);
}

.content-wrapper {
  flex: 1;
  padding: var(--spacing-xl);
}

.create-exam-form {
  max-width: 700px;
  margin: 0 auto;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-md);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-label {
  display: block;
  margin-bottom: var(--spacing-sm);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 14px;
  background-color: var(--bg-card);
  color: var(--text-primary);
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 123, 196, 0.1);
}

.form-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 14px;
  background-color: var(--bg-card);
  cursor: pointer;
}

.btn {
  padding: 10px 20px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  pointer-events: auto !important;
  position: relative;
  z-index: 1;
}

.btn svg {
  width: 18px;
  height: 18px;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-primary:disabled {
  background-color: var(--text-muted);
  cursor: not-allowed;
}

.btn-secondary {
  background-color: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background-color: var(--primary-light);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.form-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.form-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.form-checkbox span {
  font-size: 14px;
  color: var(--text-primary);
}

.error-message {
  padding: 10px 14px;
  background-color: rgba(245, 101, 101, 0.1);
  border: 1px solid rgba(245, 101, 101, 0.3);
  border-radius: var(--radius-md);
  color: #f56565;
  font-size: 13px;
  margin-bottom: var(--spacing-lg);
}

.selected-questions-preview {
  background: var(--bg-page);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  font-weight: 500;
  color: var(--text-primary);
}

.preview-count {
  font-size: 13px;
  color: var(--text-secondary);
}

.selected-question-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
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
  flex-shrink: 0;
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
  flex-shrink: 0;
}

.score-input-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.score-input {
  width: 60px;
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 12px;
  text-align: center;
}

.score-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.score-unit {
  font-size: 12px;
  color: var(--text-muted);
}

.default-score {
  font-size: 11px;
  color: var(--text-muted);
  opacity: 0.6;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--danger-color);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
  flex-shrink: 0;
}

.remove-btn:hover {
  background-color: rgba(245, 101, 101, 0.1);
}

.remove-btn svg {
  width: 16px;
  height: 16px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
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
  z-index: 9999 !important;
  pointer-events: auto !important;
}

.modal {
  display: block !important;
  visibility: visible !important;
  position: relative;
  background-color: var(--bg-card);
  border-radius: var(--radius-xl);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
  margin: auto;
  z-index: 10000 !important;
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
  transition: all 0.2s;
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

.question-select-modal {
  max-width: 900px;
}

.filter-bar {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.filter-select {
  width: 150px;
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

@media (max-width: 768px) {
  .teacher-main-content {
    margin-left: 60px;
  }
  
  .content-wrapper {
    padding: var(--spacing-lg);
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
