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
    <div class="content">
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
              {{ key.toUpperCase() }}. {{ option }}
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
              {{ key.toUpperCase() }}. {{ option }}
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
        <button 
          class="btn btn-warning" 
          @click="confirmSubmit"
        >提前交卷</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../utils/api'
import { formatTime } from '../../utils/formatters'

const route = useRoute()
const exam = ref({})
const questions = ref([])
const currentIndex = ref(0)
const answers = ref({})
const timeLeft = ref(0)
let timerInterval = null

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
  autoSave()
}

const isMultipleSelected = (key) => {
  const answer = answers.value[currentQuestion.value.id] || []
  return answer.includes(key)
}

const toggleMultipleAnswer = (key) => {
  let answer = answers.value[currentQuestion.value.id] || []
  const index = answer.indexOf(key)
  if (index > -1) {
    answer.splice(index, 1)
  } else {
    answer.push(key)
  }
  answers.value[currentQuestion.value.id] = answer
  autoSave()
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

const autoSave = () => {
  api.post(`student/exam/${route.params.examId}/save/`, { answers: answers.value })
}

const confirmExit = () => {
  if (confirm('确定要退出考试吗？退出后系统将继续计时，时间结束后自动提交。')) {
    if (timerInterval) {
      clearInterval(timerInterval)
    }
    window.location.href = '/student/exams/'
  }
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
  try {
    const response = await api.post(`student/exam/${route.params.examId}/submit/`, { answers: answers.value })
    alert('提交成功！')
    window.location.href = `/student/result/${response.data.record_id}`
  } catch (error) {
    console.error('Submit failed:', error)
    alert('提交失败，请重试')
  }
}

onMounted(async () => {
  try {
    const response = await api.get(`student/exam/${route.params.examId}/take/`)
    exam.value = response.data.exam
    questions.value = response.data.questions
    answers.value = response.data.answers || {}
    timeLeft.value = response.data.time_left
    
    timerInterval = setInterval(() => {
      if (timeLeft.value > 0) {
        timeLeft.value--
      } else {
        submitExam()
      }
    }, 1000)
  } catch (error) {
    console.error('Failed to load exam:', error)
  }
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
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
