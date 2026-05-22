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
          <h1>随机组卷</h1>
        </div>
      </div>
      <div class="content-wrapper">
        <form @submit.prevent="generateExam" class="random-exam-form">
          <div class="form-group">
            <label class="form-label" for="random-exam-title">考试名称</label>
            <input 
              type="text" 
              id="random-exam-title" 
              v-model="randomForm.title" 
              class="form-input" 
              placeholder="请输入考试名称"
              required 
            />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="random-exam-start-time">开始时间</label>
              <input 
                type="datetime-local" 
                id="random-exam-start-time" 
                v-model="randomForm.start_time" 
                class="form-input" 
                required 
              />
            </div>
            <div class="form-group">
              <label class="form-label" for="random-exam-end-time">结束时间</label>
              <input 
                type="datetime-local" 
                id="random-exam-end-time" 
                v-model="randomForm.end_time" 
                class="form-input" 
                required 
              />
            </div>
          </div>
          <div class="form-group">
            <span class="form-label">题目数量设置 (共 {{ totalQuestions }} 题)</span>
            <div class="question-count-grid">
              <div class="count-item">
                <label for="random-single-count">单选题 (可用: {{ questionStats.single }})</label>
                <input type="number" id="random-single-count" v-model.number="randomForm.single_count" class="form-input" min="0" :max="questionStats.single" value="5" />
              </div>
              <div class="count-item">
                <label for="random-multiple-count">多选题 (可用: {{ questionStats.multiple }})</label>
                <input type="number" id="random-multiple-count" v-model.number="randomForm.multiple_count" class="form-input" min="0" :max="questionStats.multiple" value="3" />
              </div>
              <div class="count-item">
                <label for="random-judge-count">判断题 (可用: {{ questionStats.judge }})</label>
                <input type="number" id="random-judge-count" v-model.number="randomForm.judge_count" class="form-input" min="0" :max="questionStats.judge" value="2" />
              </div>
              <div class="count-item">
                <label for="random-fill-count">填空题 (可用: {{ questionStats.fill }})</label>
                <input type="number" id="random-fill-count" v-model.number="randomForm.fill_count" class="form-input" min="0" :max="questionStats.fill" value="2" />
              </div>
              <div class="count-item">
                <label for="random-essay-count">简答题 (可用: {{ questionStats.essay }})</label>
                <input type="number" id="random-essay-count" v-model.number="randomForm.essay_count" class="form-input" min="0" :max="questionStats.essay" value="1" />
              </div>
            </div>
          </div>
          <div class="form-group">
            <span class="form-label">每题分数设置 (总分: {{ totalScore }} 分)</span>
            <div class="question-count-grid">
              <div class="count-item">
                <label for="score-single">单选题</label>
                <input type="number" id="score-single" v-model.number="questionScores.single" class="form-input score-input" min="1" max="100" value="2" />
              </div>
              <div class="count-item">
                <label for="score-multiple">多选题</label>
                <input type="number" id="score-multiple" v-model.number="questionScores.multiple" class="form-input score-input" min="1" max="100" value="4" />
              </div>
              <div class="count-item">
                <label for="score-judge">判断题</label>
                <input type="number" id="score-judge" v-model.number="questionScores.judge" class="form-input score-input" min="1" max="100" value="1" />
              </div>
              <div class="count-item">
                <label for="score-fill">填空题</label>
                <input type="number" id="score-fill" v-model.number="questionScores.fill" class="form-input score-input" min="1" max="100" value="2" />
              </div>
              <div class="count-item">
                <label for="score-essay">简答题</label>
                <input type="number" id="score-essay" v-model.number="questionScores.essay" class="form-input score-input" min="1" max="100" value="10" />
              </div>
            </div>
          </div>
          <div class="form-group">
            <span class="form-label">难度范围</span>
            <div class="difficulty-range">
              <select id="random-min-difficulty" v-model.number="randomForm.min_difficulty" class="form-select">
                <option :value="1">1级 (简单)</option>
                <option :value="2">2级 (较易)</option>
                <option :value="3">3级 (中等)</option>
                <option :value="4">4级 (较难)</option>
                <option :value="5">5级 (困难)</option>
              </select>
              <span class="range-separator">~</span>
              <select id="random-max-difficulty" v-model.number="randomForm.max_difficulty" class="form-select">
                <option :value="1">1级 (简单)</option>
                <option :value="2">2级 (较易)</option>
                <option :value="3">3级 (中等)</option>
                <option :value="4">4级 (较难)</option>
                <option :value="5">5级 (困难)</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-checkbox">
              <input type="checkbox" id="random-random-questions" v-model="randomForm.random_questions" />
              <span>随机题目顺序</span>
            </label>
          </div>
          <div class="form-group">
            <label class="form-checkbox">
              <input type="checkbox" id="random-random-options" v-model="randomForm.random_options" />
              <span>随机选项顺序</span>
            </label>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="goBack">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="!canSubmit">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/>
                <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
              <span>生成试卷</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../utils/api'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const router = useRouter()
const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})

const randomForm = ref({
  title: '',
  start_time: '',
  end_time: '',
  single_count: 5,
  multiple_count: 3,
  judge_count: 2,
  fill_count: 2,
  essay_count: 1,
  min_difficulty: 1,
  max_difficulty: 5,
  random_questions: true,
  random_options: true
})

const questionScores = ref({
  single: 2,
  multiple: 4,
  judge: 1,
  fill: 2,
  essay: 10
})

const questionStats = ref({
  single: 0,
  multiple: 0,
  judge: 0,
  fill: 0,
  essay: 0
})

const totalQuestions = computed(() => {
  return randomForm.value.single_count + 
         randomForm.value.multiple_count + 
         randomForm.value.judge_count + 
         randomForm.value.fill_count + 
         randomForm.value.essay_count
})

const totalScore = computed(() => {
  return randomForm.value.single_count * questionScores.value.single +
         randomForm.value.multiple_count * questionScores.value.multiple +
         randomForm.value.judge_count * questionScores.value.judge +
         randomForm.value.fill_count * questionScores.value.fill +
         randomForm.value.essay_count * questionScores.value.essay
})

const canSubmit = computed(() => {
  return randomForm.value.title && 
         randomForm.value.start_time && 
         randomForm.value.end_time &&
         totalQuestions.value > 0
})

const loadQuestionStats = async () => {
  try {
    const response = await api.get('teacher/questions/stats/', {
      params: {
        min_difficulty: randomForm.value.min_difficulty,
        max_difficulty: randomForm.value.max_difficulty
      }
    })
    if (response.data) {
      questionStats.value = {
        single: response.data.single || 0,
        multiple: response.data.multiple || 0,
        judge: response.data.judge || 0,
        fill: response.data.fill || 0,
        essay: response.data.essay || 0
      }
    }
  } catch (error) {
    console.error('Failed to load question stats:', error)
  }
}

const goBack = () => {
  router.push('/teacher/exams')
}

const generateExam = async () => {
  const errors: string[] = []
  
  if (randomForm.value.single_count > questionStats.value.single) {
    errors.push(`单选题需要 ${randomForm.value.single_count} 题，但题库中只有 ${questionStats.value.single} 题`)
  }
  if (randomForm.value.multiple_count > questionStats.value.multiple) {
    errors.push(`多选题需要 ${randomForm.value.multiple_count} 题，但题库中只有 ${questionStats.value.multiple} 题`)
  }
  if (randomForm.value.judge_count > questionStats.value.judge) {
    errors.push(`判断题需要 ${randomForm.value.judge_count} 题，但题库中只有 ${questionStats.value.judge} 题`)
  }
  if (randomForm.value.fill_count > questionStats.value.fill) {
    errors.push(`填空题需要 ${randomForm.value.fill_count} 题，但题库中只有 ${questionStats.value.fill} 题`)
  }
  if (randomForm.value.essay_count > questionStats.value.essay) {
    errors.push(`简答题需要 ${randomForm.value.essay_count} 题，但题库中只有 ${questionStats.value.essay} 题`)
  }
  
  if (errors.length > 0) {
    alert('题目数量不足，无法生成试卷：\n\n' + errors.join('\n'))
    return
  }
  
  try {
    const data = {
      title: randomForm.value.title,
      start_time: randomForm.value.start_time,
      end_time: randomForm.value.end_time,
      question_spec: {
        single: randomForm.value.single_count,
        multiple: randomForm.value.multiple_count,
        judge: randomForm.value.judge_count,
        fill: randomForm.value.fill_count,
        essay: randomForm.value.essay_count
      },
      question_scores: questionScores.value,
      min_difficulty: randomForm.value.min_difficulty,
      max_difficulty: randomForm.value.max_difficulty,
      random_questions: randomForm.value.random_questions,
      random_options: randomForm.value.random_options
    }
    
    await api.post('teacher/exams/random/', data)
    alert('试卷生成成功！')
    router.push('/teacher/exams')
  } catch (error) {
    console.error('Failed to generate exam:', error)
    alert('生成失败，请重试')
  }
}

onMounted(() => {
  loadQuestionStats()
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

.random-exam-form {
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
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
  
  .question-count-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
