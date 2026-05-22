<template>
  <div class="teacher-page-container">
    <TeacherSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['teacher-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="teacher-top-header">
        <h1>批量导入试题</h1>
        <router-link to="/teacher/questions" class="btn btn-secondary">返回题库</router-link>
      </div>
      <div class="content-wrapper">
        <div class="card">
          <h3 class="card-title">导入格式说明</h3>
          <div class="format-info">
            <p><strong>CSV格式（共9列）：</strong></p>
            <div class="field-list">
              <div class="field-item">
                <span class="field-name">type</span>
                <span class="field-desc">题型 (single/multiple/judge/essay/fill/discussion)</span>
              </div>
              <div class="field-item">
                <span class="field-name">content</span>
                <span class="field-desc">题目内容</span>
              </div>
              <div class="field-item">
                <span class="field-name">options</span>
                <span class="field-desc">选项（JSON格式），如 {"A":"选项A","B":"选项B"}</span>
              </div>
              <div class="field-item">
                <span class="field-name">answer</span>
                <span class="field-desc">正确答案 (单选多选填A/B/C/D，判断填True/False)</span>
              </div>
              <div class="field-item">
                <span class="field-name">score</span>
                <span class="field-desc">分值（数字）</span>
              </div>
              <div class="field-item">
                <span class="field-name">analysis</span>
                <span class="field-desc">答案解析（可选）</span>
              </div>
              <div class="field-item">
                <span class="field-name">difficulty</span>
                <span class="field-desc">难度 1-5（可选）</span>
              </div>
              <div class="field-item">
                <span class="field-name">chapter</span>
                <span class="field-desc">章节（可选）</span>
              </div>
              <div class="field-item">
                <span class="field-name">knowledge_point</span>
                <span class="field-desc">知识点（可选）</span>
              </div>
            </div>
            <h4>示例：</h4>
            <pre>single,在Python中定义函数用哪个关键字?,{"A":"function","B":"def","C":"func","D":"define"},B,2,在Python中使用def定义函数,1,Python基础,函数定义
judge,Python是编译型语言?,{"A":"True","B":"False"},False,2,Python是解释型语言,1,Python基础,语言特性
essay,请简述面向对象三大特性?,{},封装继承多态,10,封装隐藏细节继承复用代码多态同一接口不同实现,2,面向对象,核心概念</pre>
          </div>
        </div>
        <div class="card">
          <h3 class="card-title">选择文件</h3>
          <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
            <input 
              type="file" 
              ref="fileInput"
              @change="handleFileSelect" 
              accept=".csv,.txt"
              class="file-input"
            />
            <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <p class="upload-text">点击或拖拽文件到此处</p>
            <p class="upload-hint">支持 .csv 和 .txt 格式</p>
          </div>
        </div>
        <div v-if="importPreview.length > 0" class="card">
          <h3 class="card-title">数据预览 (共 {{ importPreview.length }} 条)</h3>
          <div class="preview-table-container">
            <table class="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>题型</th>
                  <th>题目内容</th>
                  <th>答案</th>
                  <th>分值</th>
                  <th>解析</th>
                  <th>难度</th>
                  <th>章节</th>
                  <th>知识点</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(question, index) in paginatedPreview" :key="index">
                  <td>{{ (currentPage - 1) * itemsPerPage + index + 1 }}</td>
                  <td><span :class="['tag', getTypeTagClass(question.type)]">{{ getTypeName(question.type) }}</span></td>
                  <td class="content-cell">{{ truncate(question.content, 40) }}</td>
                  <td>{{ question.answer }}</td>
                  <td>{{ question.score }}</td>
                  <td>{{ truncate(question.analysis, 20) || '-' }}</td>
                  <td>{{ question.difficulty || '-' }}</td>
                  <td>{{ question.chapter || '-' }}</td>
                  <td>{{ truncate(question.knowledge_point, 15) || '-' }}</td>
                  <td>
                    <button @click="previewQuestion(question)" class="btn btn-sm btn-secondary">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                        <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                      </svg>
                      <span>预览</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="totalPages > 1" class="pagination">
            <button 
              @click="prevPage" 
              :disabled="currentPage === 1" 
              class="pagination-btn"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>
            <span class="pagination-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
            <button 
              @click="nextPage" 
              :disabled="currentPage >= totalPages" 
              class="pagination-btn"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
          </div>
          <div class="action-section">
            <button @click="clearPreview" class="btn btn-secondary">清空预览</button>
            <button @click="importQuestions" :disabled="loading" class="btn btn-primary">
              <svg v-if="loading" class="spinner" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-dasharray="50" stroke-dashoffset="0">
                  <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
                </circle>
              </svg>
              {{ loading ? '导入中...' : `导入 ${importPreview.length} 条试题` }}
            </button>
          </div>
        </div>
        <div v-if="importError" class="error-section">
          <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          <span class="error-message">{{ importError }}</span>
        </div>
        <div v-if="importErrors.length > 0" class="card error-list">
          <h3 class="card-title">导入失败详情</h3>
          <div class="error-items">
            <div v-for="(error, index) in importErrors" :key="index" class="error-item">
              <svg class="error-dot" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="4"/>
              </svg>
              <span>{{ error }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreviewModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>题目预览</h3>
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
              <p class="question-content">{{ currentQuestion.content }}</p>
            </div>
            <div v-if="currentQuestion.options" class="form-group">
              <label class="form-label">选项</label>
              <div class="options-list">
                <div v-for="(opt, key) in parseOptions(currentQuestion.options)" :key="key" class="option-item">
                  <span class="option-key">{{ key }}</span>
                  <span class="option-value">{{ opt }}</span>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">答案</label>
              <p>{{ currentQuestion.answer }}</p>
            </div>
            <div class="form-group">
              <label class="form-label">分值</label>
              <p>{{ currentQuestion.score }} 分</p>
            </div>
            <div class="form-group">
              <label class="form-label">难度</label>
              <p>{{ getDifficultyLabel(currentQuestion.difficulty) }}</p>
            </div>
            <div v-if="currentQuestion.chapter" class="form-group">
              <label class="form-label">章节</label>
              <p>{{ currentQuestion.chapter }}</p>
            </div>
            <div v-if="currentQuestion.knowledge_point" class="form-group">
              <label class="form-label">知识点</label>
              <p>{{ currentQuestion.knowledge_point }}</p>
            </div>
            <div v-if="currentQuestion.analysis" class="form-group">
              <label class="form-label">解析</label>
              <p>{{ currentQuestion.analysis }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, inject, computed } from 'vue'
import api from '../../utils/api'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})

const fileInput = ref(null)
const importPreview = ref([])
const importError = ref('')
const importErrors = ref([])
const loading = ref(false)
const currentPage = ref(1)
const itemsPerPage = 15
const showPreviewModal = ref(false)
const currentQuestion = ref(null)

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleDrop = (e) => {
  const files = e.dataTransfer.files
  if (files.length > 0) {
    handleFile(files[0])
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    handleFile(file)
  }
}

const handleFile = (file) => {
  importError.value = ''
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const content = e.target.result
      const lines = content.split('\n').filter(line => line.trim())
      const questionsData = []
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]
        if (i === 0 && line.startsWith('type,content')) {
          continue
        }
        
        const parts = parseCSVLine(line)
        if (parts.length >= 5) {
          const type = parts[0]?.trim() || ''
          const content = parts[1]?.trim() || ''
          const options = parts[2]?.trim() || ''
          const answer = parts[3]?.trim() || ''
          const score = parseInt(parts[4]?.trim()) || 5
          const analysis = parts[5]?.trim() || ''
          const difficulty = parseInt(parts[6]?.trim()) || 1
          const chapter = parts[7]?.trim() || ''
          const knowledge_point = parts[8]?.trim() || ''
          
          questionsData.push({
            type,
            content,
            options,
            answer,
            score,
            analysis,
            difficulty,
            chapter,
            knowledge_point
          })
        }
      }
      
      importPreview.value = questionsData
    } catch (error) {
      importError.value = '文件解析错误，请检查文件格式：' + error.message
      importPreview.value = []
    }
  }
  reader.readAsText(file)
}

const parseCSVLine = (line) => {
  const result = []
  let current = ''
  let inQuotes = false
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i]
    
    if (char === '"' && line[i+1] === '"') {
      current += '"'
      i++
    } else if (char === '"') {
      inQuotes = !inQuotes
    } else if (char === ',' && !inQuotes) {
      result.push(current)
      current = ''
    } else {
      current += char
    }
  }
  result.push(current)
  
  return result
}

const getTypeName = (type) => {
  const types = {
    'single': '单选',
    'multiple': '多选',
    'judge': '判断',
    'essay': '简答',
    'fill': '填空',
    'discussion': '论述'
  }
  return types[type] || type
}

const getTypeTagClass = (type) => {
  const classes = {
    'single': 'tag-primary',
    'multiple': 'tag-success',
    'judge': 'tag-info',
    'essay': 'tag-warning',
    'fill': 'tag-danger',
    'discussion': 'tag-info'
  }
  return classes[type] || 'tag-primary'
}

const parseOptions = (options) => {
  if (!options) return {}
  // 简单的处理：按||分割选项
  const optArray = options.split('||').filter(opt => opt.trim())
  const result = {}
  optArray.forEach((opt, idx) => {
    result[String.fromCharCode(65 + idx)] = opt.trim()
  })
  return result
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

const truncate = (text, length) => {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

const totalPages = computed(() => Math.ceil(importPreview.value.length / itemsPerPage))

const paginatedPreview = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return importPreview.value.slice(start, end)
})

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const previewQuestion = (question) => {
  currentQuestion.value = question
  showPreviewModal.value = true
}

const closePreviewModal = () => {
  showPreviewModal.value = false
  currentQuestion.value = null
}

const clearPreview = () => {
  importPreview.value = []
  importError.value = ''
  importErrors.value = []
  currentPage.value = 1
  fileInput.value.value = ''
}

const importQuestions = async () => {
  if (importPreview.value.length === 0) return
  
  loading.value = true
  try {
    const response = await api.post('teacher/questions/import/', {
      questions: importPreview.value
    })
    
    if (response.data.status === 'success') {
      alert(`✅ 成功导入 ${response.data.imported_count} 条试题！`)
      importPreview.value = []
      importError.value = ''
      importErrors.value = []
    } else {
      const message = `⚠️ 部分导入成功：${response.data.imported_count} 条成功，${response.data.failed_count} 条失败。`
      alert(message)
      importErrors.value = response.data.errors || []
    }
  } catch (error) {
    importError.value = '导入失败，请重试：' + (error.response?.data?.message || error.message)
  } finally {
    loading.value = false
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

.content-wrapper {
  flex: 1;
  padding: var(--spacing-xl);
  overflow-y: auto;
}

.card {
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid rgba(0, 0, 0, 0.04);
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-lg);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-lg);
}

.format-info {
  font-size: 14px;
  color: var(--text-secondary);
}

.format-info strong {
  color: var(--primary-color);
}

.format-info pre {
  background-color: var(--bg-page);
  padding: var(--spacing-lg);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  margin: var(--spacing-lg) 0;
  overflow-x: auto;
  font-size: 13px;
  font-family: monospace;
}

.field-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-md);
  margin: var(--spacing-lg) 0;
}

.field-item {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.field-name {
  font-weight: 600;
  color: var(--primary-color);
  min-width: 120px;
  font-family: monospace;
}

.field-desc {
  color: var(--text-secondary);
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-lg);
  padding: 60px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: var(--bg-page);
}

.upload-area:hover {
  border-color: var(--primary-color);
  background-color: var(--primary-light);
}

.file-input {
  display: none;
}

.upload-icon {
  width: 48px;
  height: 48px;
  color: var(--primary-color);
  margin-bottom: var(--spacing-md);
}

.upload-text {
  font-size: 16px;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.upload-hint {
  color: var(--text-muted);
  margin: 0;
  font-size: 13px;
}

.preview-table-container {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  margin-top: var(--spacing-lg);
}

.content-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-section {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
}

.action-section .btn {
  gap: 8px;
}

.spinner {
  width: 18px;
  height: 18px;
  color: currentColor;
}

.error-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background-color: var(--danger-light);
  border-radius: var(--radius-md);
  border: 1px solid rgba(245, 101, 101, 0.2);
}

.error-icon {
  width: 24px;
  height: 24px;
  color: var(--danger-color);
}

.error-message {
  color: var(--danger-color);
  font-size: 14px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--text-secondary);
  transition: color 0.2s;
}

.modal-close:hover {
  color: var(--text-primary);
}

.modal-close svg {
  width: 20px;
  height: 20px;
}

.modal-body {
  padding: var(--spacing-lg);
}

.modal-body .form-group {
  margin-bottom: var(--spacing-lg);
}

.modal-body .form-label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.question-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-item {
  display: flex;
  gap: 12px;
}

.option-key {
  font-weight: 600;
  color: var(--primary-color);
  min-width: 20px;
}

.option-value {
  color: var(--text-primary);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

.pagination-btn {
  background: none;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: var(--bg-hover);
  border-color: var(--primary-color);
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
  font-size: 14px;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .teacher-main-content {
    margin-left: 60px;
  }
  
  .content-wrapper {
    padding: var(--spacing-lg);
  }
  
  .field-list {
    grid-template-columns: 1fr;
  }
}
</style>
