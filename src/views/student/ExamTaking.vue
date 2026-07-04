<template>
  <div class="exam-taking">
    <div class="header">
      <div class="header-left">
        <button class="btn btn-danger btn-sm" @click="confirmExit">退出考试</button>
        <h2>{{ exam.title }}</h2>
      </div>
      <div class="header-right">
        <div class="timer" :class="{ warning: timeLeft < 300, danger: timeLeft < 60 }">
          ⏱️ 剩余时间: {{ formatTime(timeLeft) }}
        </div>
      </div>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
    </div>
    <div v-if="showInstructions" class="instructions-overlay">
      <div class="instructions-card">
        <h2>{{ exam.title }}</h2>
        <div class="instructions-body">
          <div class="instruction-row">
            <span class="instruction-label">考试时长</span>
            <span class="instruction-value">{{ exam.duration }} 分钟</span>
          </div>
          <div class="instruction-row">
            <span class="instruction-label">总分</span>
            <span class="instruction-value">{{ exam.total_score }} 分</span>
          </div>
          <div class="instruction-row">
            <span class="instruction-label">题目数量</span>
            <span class="instruction-value">{{ questions.length }} 题</span>
          </div>
          <div class="instruction-divider"></div>
          <div class="instruction-notice">
            <p><strong>考试须知：</strong></p>
            <ol>
              <li>请确保网络连接稳定，答题过程中请勿刷新页面</li>
              <li>考试倒计时从进入本页面开始计算，请合理安排时间</li>
              <li>倒计时结束后系统将自动提交试卷</li>
              <li>提交试卷后无法修改答案，请确认无误后再提交</li>
              <li>退出考试后系统将继续计时，时间结束后自动提交</li>
            </ol>
          </div>
        </div>
        <button class="btn btn-primary btn-start" @click="startExam">开始答题</button>
      </div>
    </div>
    <div v-else class="content">
      <div class="question-nav">
        <div 
          v-for="(q, index) in questions" 
          :key="q.id" 
          class="nav-item"
          :class="{ active: currentIndex === index, answered: isAnswered(q.id) }"
          @click="goToQuestion(index)"
        >
          {{ index + 1 }}
        </div>
      </div>
      <div class="question-area">
        <div v-if="currentQuestion" class="question-card">
          <div class="question-header">
            <span class="question-number">第 {{ currentIndex + 1 }} 题</span>
            <span class="question-type">{{ getTypeName(currentQuestion.type) }}</span>
            <span class="question-score">{{ currentQuestion.score }} 分</span>
          </div>
          <div class="question-content">{{ currentQuestion.content }}</div>
          <div v-if="currentQuestion.type === 'single'" class="options">
            <div 
              v-for="(option, key) in currentQuestion.options" 
              :key="key"
              class="option-item"
              :class="{ selected: answers[currentQuestion.id] === key }"
              @click="selectAnswer(key)"
            >
              {{ String(key).toUpperCase() }}. {{ option }}
            </div>
          </div>
          <div v-else-if="currentQuestion.type === 'multiple'" class="options">
            <div 
              v-for="(option, key) in currentQuestion.options" 
              :key="key"
              class="option-item multiple"
              :class="{ selected: isMultipleSelected(key) }"
              @click="toggleMultipleAnswer(key)"
            >
              <input type="checkbox" :id="`answer-${currentQuestion.id}-${key}`" :checked="isMultipleSelected(key)" />
              {{ String(key).toUpperCase() }}. {{ option }}
            </div>
          </div>
          <div v-else-if="currentQuestion.type === 'judge'" class="options">
            <div 
              class="option-item"
              :class="{ selected: answers[currentQuestion.id] === 'True' }"
              @click="selectAnswer('True')"
            >
              ✓ 正确
            </div>
            <div 
              class="option-item"
              :class="{ selected: answers[currentQuestion.id] === 'False' }"
              @click="selectAnswer('False')"
            >
              ✗ 错误
            </div>
          </div>
          <div v-else class="essay-area">
            <textarea 
              v-model="answers[currentQuestion.id]"
              class="essay-input"
              placeholder="请输入您的答案..."
              rows="6"
            ></textarea>
          </div>
        </div>
      </div>
      <div class="navigation">
        <button 
          class="btn btn-secondary" 
          :disabled="currentIndex === 0" 
          @click="prevQuestion"
        >上一题</button>
        <button 
          v-if="currentIndex < questions.length - 1" 
          class="btn btn-primary" 
          @click="nextQuestion"
        >下一题</button>
        <button 
          v-else 
          class="btn btn-success" 
          @click="confirmSubmit"
        >提交试卷</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../utils/api'
import { formatTime } from '../../utils/formatters'

import type { ExamTakingSummary, TakingQuestion } from '../../types'

const route = useRoute()
const router = useRouter()
const exam = ref<ExamTakingSummary>({
  id: 0,
  title: '',
  duration: 0,
  total_score: 0,
})
const questions = ref<TakingQuestion[]>([])
const currentIndex = ref(0)
const answers = ref<Record<string, string | string[]>>({})
const timeLeft = ref(0)
const showInstructions = ref(true)
let timerInterval: ReturnType<typeof setInterval> | null = null
let autoSaveInterval: ReturnType<typeof setInterval> | null = null
let serverSyncInterval: ReturnType<typeof setInterval> | null = null

const currentQuestion = computed(() => questions.value[currentIndex.value])
const progressPercent = computed(() => ((currentIndex.value + 1) / questions.value.length) * 100)

const getTypeName = (type) => {
  const types = {
    'single': '单选题',
    'multiple': '多选题',
    'judge': '判断题',
    'essay': '简答题',
    'fill': '填空题',
    'discussion': '论述题'
  }
  return types[type] || type
}

const isAnswered = (questionId) => {
  const answer = answers.value[questionId]
  return answer !== undefined && answer !== '' && (typeof answer !== 'object' || answer.length > 0)
}

const selectAnswer = (key) => {
  answers.value[currentQuestion.value.id] = key
  saveToLocal()  // 只保存到本地，不立即提交后台
}

const isMultipleSelected = (key) => {
  const answer = answers.value[currentQuestion.value.id] || []
  return answer.includes(key)
}

const toggleMultipleAnswer = (key: string) => {
  const current = answers.value[currentQuestion.value.id]
  let answer = Array.isArray(current) ? [...current] : []
  const index = answer.indexOf(key)
  if (index > -1) {
    answer.splice(index, 1)
  } else {
    answer.push(key)
  }
  answers.value[currentQuestion.value.id] = answer
  saveToLocal()
}

const goToQuestion = (index) => {
  currentIndex.value = index
}

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
  }
}

// 本地存储键名（包含考试ID，防止冲突）
const STORAGE_KEY = `exam_${route.params.examId}_answers`

// 保存到本地存储
const saveToLocal = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(answers.value))
}

// 从本地存储恢复答案
const loadFromLocal = () => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved) {
    try {
      const localAnswers = JSON.parse(saved)
      // 合并本地答案（本地优先级更高，防止网络请求覆盖）
      answers.value = { ...answers.value, ...localAnswers }
    } catch (e) {
      console.error('Failed to load from localStorage:', e)
    }
  }
}

// 同步到后台（带错误处理，并校准剩余时间）
const syncToServer = async () => {
  try {
    const response = await api.post(`student/exam/${route.params.examId}/save/`, { answers: answers.value })
    if (response.data.status === 'auto_submitted') {
      localStorage.removeItem(STORAGE_KEY)
      alert('考试时间已到，系统已自动提交')
      router.replace(`/student/result/${response.data.record_id}`)
      return
    }
    if (typeof response.data.time_left === 'number') {
      timeLeft.value = response.data.time_left
    }
  } catch (error) {
    console.error('Sync failed, data kept locally:', error)
  }
}

// 事件触发提交（退出/交卷时）
const submitOnEvent = async (eventType) => {
  saveToLocal()  // 先保存到本地
  try {
    await api.post(`student/exam/${route.params.examId}/save/`, { answers: answers.value })
    localStorage.removeItem(STORAGE_KEY)  // 提交成功后清除本地存储
    console.log(`${eventType} submit successful`)
  } catch (error) {
    console.error(`${eventType} submit failed, data saved locally`)
    // 失败时本地存储仍然保留
  }
}

const confirmExit = () => {
  if (confirm('确定要退出考试吗？退出后系统将继续计时，时间结束后自动提交。')) {
    submitOnEvent('exit')
    if (timerInterval) {
      clearInterval(timerInterval)
    }
    router.push('/student/exams')
  }
}

const startExam = () => {
  showInstructions.value = false
}

const confirmSubmit = () => {
  if (confirm('确定要提交试卷吗？提交后将无法修改答案。')) {
    submitExam()
  }
}

const submitExam = async () => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  
  saveToLocal()  // 先保存到本地
  
  try {
    const response = await api.post(`student/exam/${route.params.examId}/submit/`, { answers: answers.value })
    localStorage.removeItem(STORAGE_KEY)
    alert('提交成功！')
    router.replace(`/student/result/${response.data.record_id}`)
  } catch (error) {
    console.error('Submit failed:', error)
    alert('提交失败，请重试（答案已保存到本地）')
  }
}

onMounted(async () => {
  try {
    const response = await api.get(`student/exam/${route.params.examId}/take/`)
    exam.value = response.data.exam
    questions.value = response.data.questions
    answers.value = response.data.answers || {}
    timeLeft.value = response.data.time_left
    
    // 从本地存储恢复答案（防止页面刷新丢失）
    loadFromLocal()

    if (timeLeft.value <= 0) {
      await submitExam()
      return
    }
    
    timerInterval = setInterval(() => {
      if (timeLeft.value > 0) {
        timeLeft.value--
      } else {
        submitExam()
      }
    }, 1000)
    
    autoSaveInterval = setInterval(() => {
      syncToServer()
    }, 60000)

    serverSyncInterval = setInterval(async () => {
      try {
        const response = await api.get(`student/exam/${route.params.examId}/take/`)
        if (typeof response.data.time_left === 'number') {
          timeLeft.value = response.data.time_left
        }
      } catch (error) {
        if (error.response?.data?.error === '已提交') {
          localStorage.removeItem(STORAGE_KEY)
          router.replace(`/student/result/${error.response.data.record_id}`)
        }
      }
    }, 120000)
  } catch (error) {
    if (error.response?.data?.error === '已提交') {
      router.replace(`/student/result/${error.response.data.record_id}`)
      return
    }
    console.error('Failed to load exam:', error)
  }
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  if (autoSaveInterval) {
    clearInterval(autoSaveInterval)
  }
  if (serverSyncInterval) {
    clearInterval(serverSyncInterval)
  }
  // 页面关闭前保存到本地（最后保障）
  saveToLocal()
})
</script>

<style scoped>
.exam-taking {
  min-height: 100vh;
  background: #f8f9fa;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #0d6efd;
  color: white;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.timer {
  font-size: 1.25rem;
  font-weight: bold;
}

.timer.warning {
  color: #ffc107;
}

.timer.danger {
  color: #dc3545;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.progress-bar {
  height: 4px;
  background: #ddd;
}

.progress-fill {
  height: 100%;
  background: #0d6efd;
  transition: width 0.3s;
}

.instructions-overlay {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 3rem 1rem;
  min-height: calc(100vh - 80px);
  background: #f0f2f5;
}

.instructions-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  max-width: 600px;
  width: 100%;
}

.instructions-card h2 {
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  color: #1a1a2e;
  text-align: center;
}

.instructions-body {
  margin-bottom: 1.5rem;
}

.instruction-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 1rem;
}

.instruction-label {
  color: #666;
}

.instruction-value {
  font-weight: 600;
  color: #1a1a2e;
}

.instruction-divider {
  height: 1px;
  background: #e0e0e0;
  margin: 1rem 0;
}

.instruction-notice {
  background: #f8f9ff;
  border-radius: 8px;
  padding: 1rem 1.25rem;
}

.instruction-notice p {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.instruction-notice ol {
  margin: 0;
  padding-left: 1.25rem;
}

.instruction-notice li {
  margin-bottom: 0.4rem;
  color: #555;
  font-size: 0.9rem;
  line-height: 1.5;
}

.btn-start {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.content {
  display: flex;
  padding: 1rem;
}

.question-nav {
  width: 200px;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  margin-right: 1rem;
}

.nav-item {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eee;
  border-radius: 50%;
  cursor: pointer;
}

.nav-item.active {
  background: #0d6efd;
  color: white;
}

.nav-item.answered {
  background: #28a745;
  color: white;
}

.question-area {
  flex: 1;
}

.question-card {
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.question-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.question-number {
  font-weight: bold;
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
}

.question-content {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.option-item {
  padding: 1rem;
  border: 2px solid #ddd;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.option-item:hover {
  border-color: #0d6efd;
}

.option-item.selected {
  border-color: #0d6efd;
  background: #e7f3ff;
}

.option-item.multiple {
  display: flex;
  align-items: center;
}

.option-item.multiple input {
  margin-right: 0.75rem;
}

.essay-area {
  margin-top: 1rem;
}

.essay-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #ddd;
  border-radius: 0.5rem;
  font-size: 1rem;
  resize: vertical;
}

.navigation {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #0d6efd;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>
