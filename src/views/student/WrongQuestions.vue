<template>
  <div class="student-page-container">
    <StudentSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['student-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="content-header">
        <h1>错题本</h1>
        <p class="subtitle">记录您的错题，方便复习巩固</p>
      </div>
      <div class="content-wrapper">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>
        <div v-else-if="wrongQuestions.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <h3>暂无错题记录</h3>
          <p>继续保持，下次一定能取得更好的成绩！</p>
        </div>
        <div v-else class="wrong-questions-list">
          <div v-for="(item, index) in wrongQuestions" :key="item.question_key || (item.exam_id + '-' + index)" class="question-card">
            <div class="question-header">
              <span class="question-index">{{ (currentPage - 1) * pageSize + index + 1 }}</span>
              <span :class="['question-type', getTypeClass(item.type)]">{{ getTypeName(item.type) }}</span>
              <span class="exam-name">{{ item.exam_title }}</span>
              <span class="wrong-time">{{ formatDate(item.submit_time) }}</span>
              <button class="delete-btn" @click="confirmDelete(item)" title="删除此题">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                </svg>
              </button>
            </div>
            <div class="question-content">
              <p class="question-text">{{ item.content }}</p>
              <div v-if="item.options && Object.keys(item.options).length > 0" class="options-list">
                <div v-for="(opt, key) in item.options" :key="key" 
                     :class="['option-item', getOptionClass(key, item.answer, item.student_answer, item.type)]">
                  <span class="option-key">{{ key }}.</span>
                  <span class="option-text">{{ opt }}</span>
                  <span v-if="isCorrectAnswer(key, item.answer, item.type)" class="correct-mark">正确答案</span>
                  <span v-if="isWrongAnswer(key, item.student_answer, item.answer, item.type)" class="wrong-mark">您的答案</span>
                </div>
              </div>
            </div>
            <div class="question-footer">
              <div class="answer-comparison">
                <div class="your-answer">
                  <span class="label">您的答案：</span>
                  <span class="value wrong">{{ item.student_answer || '未作答' }}</span>
                </div>
                <div class="correct-answer">
                  <span class="label">正确答案：</span>
                  <span class="value correct">{{ item.answer }}</span>
                </div>
              </div>
              <div v-if="item.analysis" class="analysis">
                <span class="label">题目解析：</span>
                <p>{{ item.analysis }}</p>
              </div>
            </div>
          </div>
        </div>
        <div v-if="totalPages > 1" class="pagination">
          <button class="page-btn" :disabled="currentPage <= 1" @click="changePage(currentPage - 1)">上一页</button>
          <button v-for="p in visiblePages" :key="p" 
                  :class="['page-btn', { active: p === currentPage }]"
                  @click="changePage(p)">{{ p }}</button>
          <button class="page-btn" :disabled="currentPage >= totalPages" @click="changePage(currentPage + 1)">下一页</button>
          <span class="page-info">共 {{ total }} 题，{{ totalPages }} 页</span>
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
const wrongQuestions = ref([])
const currentPage = ref(1)
const total = ref(0)
const totalPages = ref(1)
const pageSize = 10

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

onMounted(async () => {
  await fetchWrongQuestions()
})

const fetchWrongQuestions = async () => {
  try {
    loading.value = true
    const response = await api.get(`student/wrong-questions/?page=${currentPage.value}&page_size=${pageSize}`)
    wrongQuestions.value = response.data.wrong_questions || []
    total.value = response.data.total || 0
    totalPages.value = response.data.total_pages || 1
  } catch (error) {
    console.error('Failed to fetch wrong questions:', error)
    wrongQuestions.value = []
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchWrongQuestions()
}

const getTypeName = (type) => {
  const types = {
    'single': '单选题',
    'multiple': '多选题',
    'judge': '判断题',
    'fill': '填空题',
    'essay': '简答题'
  }
  return types[type] || type
}

const getTypeClass = (type) => {
  const classes = {
    'single': 'type-single',
    'multiple': 'type-multiple',
    'judge': 'type-judge',
    'fill': 'type-fill',
    'essay': 'type-essay'
  }
  return classes[type] || 'type-single'
}

const isCorrectAnswer = (key, correctAnswer, type) => {
  if (type === 'multiple') {
    return String(correctAnswer).split(',').map(s => s.trim()).includes(key)
  }
  return key === correctAnswer
}

const isWrongAnswer = (key, studentAnswer, correctAnswer, type) => {
  if (type === 'multiple') {
    const stuAnswers = String(studentAnswer).split(',').map(s => s.trim())
    const correctAnswers = String(correctAnswer).split(',').map(s => s.trim())
    return stuAnswers.includes(key) && !correctAnswers.includes(key)
  }
  return key === studentAnswer && key !== correctAnswer
}

const getOptionClass = (key, correctAnswer, studentAnswer, type) => {
  if (type === 'multiple') {
    const correctAnswers = String(correctAnswer).split(',').map(s => s.trim())
    const stuAnswers = String(studentAnswer).split(',').map(s => s.trim())
    if (stuAnswers.includes(key) && !correctAnswers.includes(key)) return 'option-wrong'
    if (correctAnswers.includes(key)) return 'option-correct'
    return ''
  }
  if (key === correctAnswer) return 'option-correct'
  if (key === studentAnswer) return 'option-wrong'
  return ''
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const confirmDelete = (item) => {
  if (confirm('确定要从错题本中删除此题吗？')) {
    deleteWrongQuestion(item)
  }
}

const deleteWrongQuestion = async (item) => {
  try {
    await api.post('student/wrong-questions/delete/', { question_key: item.question_key })
    wrongQuestions.value = wrongQuestions.value.filter(q => q.question_key !== item.question_key)
    total.value--
    totalPages.value = Math.max(1, Math.ceil(total.value / pageSize))
    if (wrongQuestions.value.length === 0 && currentPage.value > 1) {
      currentPage.value--
      await fetchWrongQuestions()
    }
  } catch (error) {
    console.error('Failed to delete wrong question:', error)
    alert('删除失败，请重试')
  }
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
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon svg {
  width: 40px;
  height: 40px;
  color: white;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: var(--text-primary);
}

.empty-state p {
  margin: 0;
  color: var(--text-muted);
  font-size: 14px;
}

.wrong-questions-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid var(--border-color);
}

.question-index {
  width: 28px;
  height: 28px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.question-type {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.type-single {
  background: #e3f2fd;
  color: #1565c0;
}

.type-multiple {
  background: #e8f5e9;
  color: #2e7d32;
}

.type-judge {
  background: #fff3e0;
  color: #e65100;
}

.type-fill {
  background: #fce4ec;
  color: #c2185b;
}

.type-essay {
  background: #f3e5f5;
  color: #7b1fa2;
}

.exam-name {
  flex: 1;
  font-size: 13px;
  color: var(--text-secondary);
}

.wrong-time {
  font-size: 12px;
  color: var(--text-muted);
}

.delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #9ca3af;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.delete-btn:hover {
  background: #fef2f2;
  color: #ef4444;
}

.delete-btn svg {
  width: 16px;
  height: 16px;
}

.question-content {
  padding: 20px;
}

.question-text {
  margin: 0 0 16px 0;
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-primary);
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--bg-page);
  border-radius: 8px;
  font-size: 14px;
}

.option-correct {
  background: #e8f5e9;
  border: 1px solid #4caf50;
}

.option-wrong {
  background: #ffebee;
  border: 1px solid #f44336;
}

.option-key {
  font-weight: 600;
  color: var(--text-primary);
}

.option-text {
  flex: 1;
  color: var(--text-primary);
}

.correct-mark {
  font-size: 12px;
  color: #4caf50;
  font-weight: 500;
}

.wrong-mark {
  font-size: 12px;
  color: #f44336;
  font-weight: 500;
}

.question-footer {
  padding: 16px 20px;
  background: #fff8e1;
  border-top: 1px solid var(--border-color);
}

.answer-comparison {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.your-answer,
.correct-answer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  font-size: 13px;
  color: var(--text-secondary);
}

.value {
  font-size: 14px;
  font-weight: 600;
}

.value.wrong {
  color: #f44336;
}

.value.correct {
  color: #4caf50;
}

.analysis {
  padding-top: 12px;
  border-top: 1px dashed var(--border-color);
}

.analysis .label {
  font-size: 13px;
  color: var(--text-secondary);
}

.analysis p {
  margin: 8px 0 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px 0;
}

.page-btn {
  padding: 6px 14px;
  border: 1px solid var(--border-color);
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.page-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  margin-left: 12px;
  font-size: 13px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .student-main-content {
    margin-left: 64px;
  }
  
  .content-wrapper {
    padding: 16px;
  }
  
  .answer-comparison {
    flex-direction: column;
    gap: 8px;
  }
}
</style>