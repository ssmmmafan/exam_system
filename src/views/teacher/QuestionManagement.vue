<template>
  <div class="teacher-page-container">
    <TeacherSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['teacher-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
        <div class="teacher-top-header">
          <h1>题库管理</h1>
          <div class="header-right">
            <button @click="openCreateModal" class="btn btn-primary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 4v16m8-8H4"/>
            </svg>
            <span>创建试题</span>
          </button>
          </div>
        </div>
        <div class="content-wrapper">
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">我的试题</h2>
              <div class="header-actions">
                <select v-model="filterType" class="form-select">
                  <option value="">全部题型</option>
                  <option value="single">单选题</option>
                  <option value="multiple">多选题</option>
                  <option value="judge">判断题</option>
                  <option value="essay">简答题</option>
                  <option value="fill">填空题</option>
                </select>
                <button 
                  v-if="selectedQuestions.length > 0" 
                  @click="deleteSelectedQuestions" 
                  class="btn btn-danger"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M3 6h18"/>
                    <path d="M19 6v14c0 1.1-.9 2-2 2H7c-1.1 0-2-.9-2-2V6"/>
                    <path d="M8 6V4c0-1.1.9-2 2-2h4c1.1 0 2 .9 2 2v2"/>
                  </svg>
                  <span>批量删除 ({{ selectedQuestions.length }})</span>
                </button>
              </div>
            </div>
            <div v-if="loading" class="loading">
              <svg class="loading-spinner" viewBox="0 0 24 24" fill="none">
                <circle class="spinner" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-dasharray="50" stroke-dashoffset="0" transform="rotate(0 12 12)">
                  <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
                </circle>
              </svg>
            </div>
            <div v-else-if="questions.length === 0" class="empty-state">
              <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
                <circle cx="12" cy="12" r="6"/>
                <circle cx="12" cy="12" r="2"/>
              </svg>
              <p>暂无试题</p>
              <button @click="showModal = true" class="btn btn-primary">创建第一道试题</button>
            </div>
            <div v-else class="question-list">
              <div class="question-list-header">
                <label class="checkbox-label">
                  <input 
                    type="checkbox" 
                    :checked="selectedQuestions.length === questions.length"
                    @change="toggleSelectAll"
                    class="form-checkbox"
                  />
                  <span>全选本页</span>
                </label>
              </div>
              <div v-for="question in questions" :key="question.id" class="question-item">
                <input 
                  type="checkbox" 
                  :checked="selectedQuestions.includes(question.id)"
                  @change="toggleSelect(question.id)"
                  class="question-checkbox"
                />
                <div class="question-info">
                  <div class="question-header">
                    <span :class="['tag', getTypeTagClass(question.type)]">{{ getTypeName(question.type) }}</span>
                    <span class="question-id">#{{ question.id }}</span>
                  </div>
                  <div class="question-content">{{ question.content }}</div>
                  <div class="question-meta">
                    <span class="tag tag-primary">分值: {{ question.score }}</span>
                    <span v-if="question.difficulty" class="tag tag-warning">难度: {{ getDifficultyLabel(question.difficulty) }}</span>
                    <span v-if="question.chapter" class="tag tag-info">{{ question.chapter }}</span>
                  </div>
                </div>
                <div class="question-actions">
                  <button @click="viewQuestion(question)" class="btn btn-info">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                      <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                    </svg>
                    <span>查看</span>
                  </button>
                  <button @click="editQuestion(question)" class="btn btn-secondary">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                    <span>编辑</span>
                  </button>
                  <button @click="deleteQuestion(question.id)" class="btn btn-danger">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M3 6h18"/>
                      <path d="M19 6v14c0 1.1-.9 2-2 2H7c-1.1 0-2-.9-2-2V6"/>
                      <path d="M8 6V4c0-1.1.9-2 2-2h4c1.1 0 2 .9 2 2v2"/>
                    </svg>
                    <span>删除</span>
                  </button>
                </div>
              </div>
            </div>
            <div v-if="total > 10" class="pagination-container">
              <div class="pagination">
                <button 
                  @click="prevPage" 
                  :disabled="currentPage === 1" 
                  class="pagination-btn"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="15 18 9 12 15 6"/>
                  </svg>
                  <span>上一页</span>
                </button>
                <div class="pagination-info">
                  <span class="current-page">{{ currentPage }}</span>
                  <span class="page-separator">/</span>
                  <span class="total-pages">{{ totalPages }}</span>
                </div>
                <button 
                  @click="nextPage" 
                  :disabled="currentPage >= totalPages" 
                  class="pagination-btn"
                >
                  <span>下一页</span>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <Teleport to="body">
        <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreviewModal">
          <div class="modal">
            <div class="modal-header">
              <h3>题目详情</h3>
              <button @click="closePreviewModal" class="modal-close">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <div v-if="currentQuestion" class="modal-body">
              <div class="form-group">
                <label class="form-label">题型</label>
                <span :class="['tag', getTypeTagClass(currentQuestion.type)]">{{ getTypeName(currentQuestion.type) }}</span>
              </div>
              <div class="form-group">
                <label class="form-label">题目内容</label>
                <textarea class="form-textarea" rows="3" readonly>{{ currentQuestion.content }}</textarea>
              </div>
              <div v-if="currentQuestion.options && Object.keys(currentQuestion.options).length" class="form-group">
                <label class="form-label">选项</label>
                <div class="options-grid">
                  <div v-for="(opt, key) in currentQuestion.options" :key="key" class="option-input">
                    <span class="option-key">{{ key }}</span>
                    <input type="text" class="form-input" :value="opt" readonly>
                  </div>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">答案</label>
                <input type="text" class="form-input" :value="currentQuestion.answer" readonly>
              </div>
              <div class="form-group">
                <label class="form-label">分值</label>
                <input type="number" class="form-input" :value="currentQuestion.score" readonly>
              </div>
              <div class="form-group">
                <label class="form-label">难度</label>
                <span :class="['tag', 'tag-warning']">{{ getDifficultyLabel(currentQuestion.difficulty) }}</span>
              </div>
              <div v-if="currentQuestion.chapter" class="form-group">
                <label class="form-label">章节</label>
                <input type="text" class="form-input" :value="currentQuestion.chapter" readonly>
              </div>
              <div v-if="currentQuestion.knowledge_point" class="form-group">
                <label class="form-label">知识点</label>
                <input type="text" class="form-input" :value="currentQuestion.knowledge_point" readonly>
              </div>
              <div v-if="currentQuestion.analysis" class="form-group">
                <label class="form-label">解析</label>
                <textarea class="form-textarea" rows="2" readonly>{{ currentQuestion.analysis }}</textarea>
              </div>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingQuestion ? '编辑试题' : '创建试题' }}</h3>
          <button @click="closeModal" class="modal-close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <form @submit.prevent="submitQuestion" class="modal-body">
          <div class="form-group">
            <label class="form-label">题型</label>
            <select v-model="form.type" class="form-select" required>
              <option value="single">单选题</option>
              <option value="multiple">多选题</option>
              <option value="judge">判断题</option>
              <option value="essay">简答题</option>
              <option value="fill">填空题</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">
              题目内容
              <span v-if="form.type === 'fill'" class="help-text">（使用 ____ 标记填空位置）</span>
            </label>
            <textarea v-model="form.content" class="form-textarea" rows="3" required :placeholder="getContentPlaceholder()"></textarea>
            <div v-if="form.type === 'fill' && getFillCount() > 0" class="fill-hint">
              检测到 {{ getFillCount() }} 个填空，已自动生成 {{ getFillCount() }} 个答案输入框
            </div>
          </div>

          <div v-if="form.type === 'single' || form.type === 'multiple'" class="form-group">
            <label class="form-label">选项</label>
            <div class="options-grid">
              <div v-for="(opt, key) in currentOptions" :key="key" class="option-input">
                <span class="option-key">{{ key }}</span>
                <input v-model="currentOptions[key]" type="text" class="form-input" :placeholder="`选项 ${key}`">
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">
              正确答案
              <span :class="['format-hint', form.type]">{{ getAnswerHint() }}</span>
            </label>
            
            <div v-if="form.type === 'fill' && getFillCount() > 0" class="fill-answers">
              <div v-for="(ans, idx) in fillAnswers" :key="idx" class="fill-answer-item">
                <label class="form-label-small">填空 {{ idx + 1 }}</label>
                <input v-model="fillAnswers[idx]" type="text" class="form-input" placeholder="请输入答案">
              </div>
            </div>
            <input v-else-if="form.type === 'judge'" v-model="form.answer" class="form-input" placeholder="输入：对 或 错" required>
            <input v-else-if="form.type === 'single'" v-model="form.answer" class="form-input" placeholder="输入选项字母，如：A" required>
            <input v-else-if="form.type === 'multiple'" v-model="form.answer" class="form-input" placeholder="输入选项字母，如：ABD 或 A,B,D" required>
            <textarea v-else v-model="form.answer" class="form-textarea" rows="3" placeholder="输入正确答案" required></textarea>
          </div>
          
          <div class="form-group">
            <label class="form-label">分值</label>
            <input v-model.number="form.score" type="number" class="form-input" min="1" required>
          </div>
          <div class="form-group">
            <label class="form-label">答案解析</label>
            <textarea v-model="form.analysis" class="form-textarea" rows="2"></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">难度等级</label>
            <select v-model.number="form.difficulty" class="form-select" required>
              <option :value="1">简单</option>
              <option :value="2">较易</option>
              <option :value="3">中等</option>
              <option :value="4">较难</option>
              <option :value="5">困难</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">所属章节</label>
            <input v-model="form.chapter" class="form-input" placeholder="例如：第1章 数据库基础">
          </div>
          <div class="form-group">
            <label class="form-label">知识点</label>
            <input v-model="form.knowledge_point" class="form-input" placeholder="例如：SQL查询、数据表设计">
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn btn-secondary">取消</button>
            <button type="submit" class="btn btn-primary">{{ editingQuestion ? '保存修改' : '创建试题' }}</button>
          </div>
        </form>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, inject } from 'vue'
import api from '../../utils/api'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})
const questions = ref([])
const loading = ref(false)
const showModal = ref(false)
const editingQuestion = ref(null)
const filterType = ref('')
const currentPage = ref(1)
const total = ref(0)
const totalPages = computed(() => Math.ceil(total.value / 10))
const selectedQuestions = ref([])
const showPreviewModal = ref(false)
const currentQuestion = ref(null)

const form = ref({
  type: 'single',
  content: '',
  options: '{"A":"","B":"","C":"","D":""}',
  answer: '',
  score: 5,
  analysis: '',
  difficulty: 3,
  chapter: '',
  knowledge_point: ''
})

const currentOptions = ref({
  A: '',
  B: '',
  C: '',
  D: ''
})

const fillAnswers = ref<string[]>([])

const getFillCount = () => {
  if (form.value.type !== 'fill') return 0
  const matches = form.value.content.match(/____/g)
  return matches ? matches.length : 0
}

watch(() => form.value.content, () => {
  if (form.value.type === 'fill') {
    const count = getFillCount()
    if (count > fillAnswers.value.length) {
      while (fillAnswers.value.length < count) {
        fillAnswers.value.push('')
      }
    } else if (count < fillAnswers.value.length) {
      fillAnswers.value = fillAnswers.value.slice(0, count)
    }
  }
})

watch(() => form.value.type, (newType) => {
  if (newType === 'single' || newType === 'multiple') {
    if (!editingQuestion.value) {
      currentOptions.value = { A: '', B: '', C: '', D: '' }
    }
  }
})

const getContentPlaceholder = () => {
  if (form.value.type === 'fill') {
    return '例如：My name is ______. I am from ______.'
  }
  return ''
}

const getAnswerHint = () => {
  switch (form.value.type) {
    case 'single':
      return '(输入选项字母，如：A)'
    case 'multiple':
      return '(输入选项字母，如：ABD 或 A,B,D)'
    case 'judge':
      return '(输入：对 或 错)'
    case 'fill':
      return '(根据填空数量自动生成输入框)'
    case 'essay':
      return '(输入详细的答案描述)'
    default:
      return ''
  }
}

const getOptionsJSON = () => {
  if (form.value.type === 'single' || form.value.type === 'multiple') {
    const options: Record<string, string> = {}
    for (const [key, value] of Object.entries(currentOptions.value)) {
      if (value.trim()) {
        options[key] = value
      }
    }
    return options
  }
  return form.value.options
}

const openCreateModal = () => {
  console.log('Opening create modal...')
  editingQuestion.value = null
  form.value = {
    type: 'single',
    content: '',
    options: '{"A":"","B":"","C":"","D":""}',
    answer: '',
    score: 5,
    analysis: '',
    difficulty: 3,
    chapter: '',
    knowledge_point: ''
  }
  currentOptions.value = { A: '', B: '', C: '', D: '' }
  fillAnswers.value = []
  showModal.value = true
  console.log('showModal value:', showModal.value)
}

onMounted(async () => {
  await loadQuestions()
})

const loadQuestions = async () => {
  loading.value = true
  try {
    const response = await api.get(`teacher/questions/?page=${currentPage.value}&type=${filterType.value}`)
    questions.value = response.data.questions || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('Failed to load questions:', error)
  } finally {
    loading.value = false
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadQuestions()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadQuestions()
  }
}

watch(filterType, () => {
  currentPage.value = 1
  selectedQuestions.value = []
  loadQuestions()
})

watch(currentPage, () => {
  selectedQuestions.value = []
})

const toggleSelect = (id) => {
  const index = selectedQuestions.value.indexOf(id)
  if (index > -1) {
    selectedQuestions.value.splice(index, 1)
  } else {
    selectedQuestions.value.push(id)
  }
}

const toggleSelectAll = () => {
  if (selectedQuestions.value.length === questions.value.length) {
    selectedQuestions.value = []
  } else {
    selectedQuestions.value = questions.value.map(q => q.id)
  }
}

const viewQuestion = (question) => {
  currentQuestion.value = question
  showPreviewModal.value = true
}

const closePreviewModal = () => {
  showPreviewModal.value = false
  currentQuestion.value = null
}

const deleteSelectedQuestions = async () => {
  if (!confirm(`确定要删除选中的 ${selectedQuestions.value.length} 条题目吗？`)) return
  
  try {
    await api.delete('teacher/questions/batch/', {
      data: { ids: selectedQuestions.value }
    })
    selectedQuestions.value = []
    loadQuestions()
    alert('批量删除成功！')
  } catch (error) {
    console.error('Failed to delete questions:', error)
    alert('批量删除失败')
  }
}

const getTypeName = (type) => {
  const types = {
    'single': '单选',
    'multiple': '多选',
    'judge': '判断',
    'essay': '简答',
    'fill': '填空'
  }
  return types[type] || type
}

const getTypeTagClass = (type) => {
  const classes = {
    'single': 'tag-primary',
    'multiple': 'tag-success',
    'judge': 'tag-info',
    'essay': 'tag-warning',
    'fill': 'tag-danger'
  }
  return classes[type] || 'tag-primary'
}

const getDifficultyLabel = (level) => {
  const labels = {
    1: '简单',
    2: '较易',
    3: '中等',
    4: '较难',
    5: '困难'
  }
  return labels[level] || `等级 ${level}`
}

const editQuestion = (question) => {
  editingQuestion.value = question
  form.value = {
    type: question.type,
    content: question.content,
    options: typeof question.options === 'string' ? question.options : JSON.stringify(question.options || {}),
    answer: question.answer,
    score: question.score,
    analysis: question.analysis || '',
    difficulty: question.difficulty || 3,
    chapter: question.chapter || '',
    knowledge_point: question.knowledge_point || ''
  }
  
  if (question.type === 'single' || question.type === 'multiple') {
    try {
      const opts = typeof question.options === 'string' ? JSON.parse(question.options) : (question.options || {})
      currentOptions.value = {
        A: opts.A || '',
        B: opts.B || '',
        C: opts.C || '',
        D: opts.D || ''
      }
    } catch {
      currentOptions.value = { A: '', B: '', C: '', D: '' }
    }
  }
  
  if (question.type === 'fill' && question.answer) {
    fillAnswers.value = question.answer.split('|||')
  } else {
    fillAnswers.value = []
  }
  
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingQuestion.value = null
  form.value = {
    type: 'single',
    content: '',
    options: '{"A":"","B":"","C":"","D":""}',
    answer: '',
    score: 5,
    analysis: '',
    difficulty: 3,
    chapter: '',
    knowledge_point: ''
  }
}

const submitQuestion = async () => {
  try {
    if (form.value.type === 'fill') {
      if (getFillCount() === 0) {
        alert('请在题目内容中使用 ____ 标记至少一个填空位置')
        return
      }
      
      const emptyAnswers = fillAnswers.value.filter(a => !a.trim())
      if (emptyAnswers.length > 0) {
        alert('请填写所有空格的答案')
        return
      }
      
      form.value.answer = fillAnswers.value.join('|||')
    }
    
    if ((form.value.type === 'single' || form.value.type === 'multiple') && form.value.answer) {
      const answerUpper = form.value.answer.toUpperCase().replace(/,/g, '')
      if (!/^[A-Z]+$/.test(answerUpper)) {
        alert('答案格式错误：单选题和多选题的答案必须是选项字母')
        return
      }
    }
    
    const data = {
      type: form.value.type,
      content: form.value.content,
      options: getOptionsJSON(),
      answer: form.value.answer,
      score: form.value.score,
      analysis: form.value.analysis,
      difficulty: form.value.difficulty,
      chapter: form.value.chapter,
      knowledge_point: form.value.knowledge_point
    }
    
    if (editingQuestion.value) {
      await api.put(`teacher/questions/${editingQuestion.value.id}/`, data)
    } else {
      await api.post('teacher/questions/', data)
    }
    
    await loadQuestions()
    closeModal()
  } catch (error) {
    console.error('Failed to save question:', error)
    alert('保存失败，请重试')
  }
}

const deleteQuestion = async (id) => {
  if (!confirm('确定要删除这道试题吗？')) return
  try {
    await api.delete(`teacher/questions/${id}/`)
    await loadQuestions()
  } catch (error) {
    console.error('Failed to delete question:', error)
    alert('删除失败，请重试')
  }
}

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

.header-right {
  display: flex;
  align-items: center;
}

.header-right .btn svg {
  width: 18px;
  height: 18px;
  margin-right: 8px;
}

.content-wrapper {
  flex: 1;
  padding: var(--spacing-xl);
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.question-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--spacing-lg);
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.question-item:hover {
  box-shadow: var(--shadow-md);
}

.question-info {
  flex: 1;
  min-width: 0;
}

.question-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
}

.question-id {
  font-size: 12px;
  color: var(--text-muted);
}

.question-content {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.5;
  margin-bottom: var(--spacing-sm);
}

.question-meta {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.question-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-shrink: 0;
  margin-left: var(--spacing-md);
}

.question-actions .btn {
  gap: 6px;
}

.question-actions .btn svg {
  width: 16px;
  height: 16px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

.pagination {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn svg {
  width: 16px;
  height: 16px;
}

.pagination-info {
  display: flex;
  align-items: baseline;
  gap: 4px;
  padding: 10px 16px;
}

.current-page {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
}

.page-separator {
  font-size: 16px;
  color: var(--text-muted);
  margin: 0 4px;
}

.total-pages {
  font-size: 14px;
  color: var(--text-secondary);
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  color: var(--primary-color);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: var(--text-muted);
}

.empty-icon {
  width: 56px;
  height: 56px;
  margin-bottom: var(--spacing-md);
}

.empty-state p {
  margin-bottom: var(--spacing-md);
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
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

.modal {
  position: relative;
  z-index: 10000;
  background-color: #ffffff;
  border-radius: var(--radius-xl);
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
  border: 1px solid #e5e7eb;
  display: block;
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

.help-text {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: normal;
  margin-left: 8px;
}

.fill-hint {
  margin-top: 8px;
  padding: 10px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
}

.format-hint {
  font-size: 12px;
  font-weight: normal;
  color: var(--text-muted);
  margin-left: 8px;
}

.format-hint.single,
.format-hint.multiple {
  color: var(--primary-color);
}

.format-hint.judge {
  color: var(--info-color);
}

.format-hint.fill {
  color: var(--warning-color);
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 8px;
}

.option-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-key {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  color: white;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.fill-answers {
  display: grid;
  gap: 12px;
  margin-top: 8px;
}

.fill-answer-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label-small {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

/* Responsive */
@media (max-width: 768px) {
  .teacher-main-content {
    margin-left: 60px;
  }
  
  .content-wrapper {
    padding: var(--spacing-lg);
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .question-item {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .question-actions {
    margin-left: 0;
    justify-content: flex-end;
  }
}
</style>
