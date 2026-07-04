<template>
  <div class="result-detail">
    <div class="container">
      <h2>考试成绩</h2>
      <div class="result-header">
        <h3>{{ exam.title }}</h3>
        <div class="score-display">
          <div class="score-circle">
            <span class="score-value">{{ record.score || 0 }}</span>
            <span class="score-label">分</span>
          </div>
          <div class="score-info">
            <div class="info-row">
              <span>总分：{{ record.total_score || 0 }} 分</span>
            </div>
            <div class="info-row">
              <span>答 题 时 间：{{ formatTime(record.time_spent || 0) }}</span>
            </div>
            <div class="info-row">
              <span>提 交 时 间：{{ record.submit_time ? formatDate(record.submit_time) : '暂无' }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="section">
        <h4>答题详情</h4>
        <div v-if="questions.length === 0" class="empty-state">
          暂无答题记录
        </div>
        <div v-else>
          <div v-for="(q, index) in questions" :key="q.id" class="question-item">
            <div class="question-header">
              <span class="question-num">第 {{ index + 1 }} 题</span>
              <span class="question-type">{{ getTypeName(q.type) }}</span>
              <span class="question-score">{{ q.score }} 分</span>
              <span v-if="q.type === 'essay' || q.type === 'discussion'">
                <span v-if="q.essay_score !== null" class="status-score">得分：{{ q.essay_score }}/{{ q.score }}</span>
                <span v-else class="status-pending">待批改</span>
              </span>
              <span v-else-if="q.is_correct === true" class="status-correct">正确</span>
              <span v-else-if="q.is_correct === false" class="status-wrong">错误</span>
              <span v-else class="status-pending">待批改</span>
            </div>
            <div class="question-content">{{ q.content }}</div>
            <div v-if="q.options && Object.keys(q.options).length > 0" class="options-review">
              <div v-for="(option, key) in q.options" :key="key" class="option-review-item">
                <span :class="{
                  correct: q.type === 'multiple' ? String(q.correct_answer).split(',').map(s => s.trim()).includes(String(key)) : q.correct_answer === String(key),
                  selected: q.type === 'multiple' ? (Array.isArray(q.user_answer) ? q.user_answer.includes(String(key)) : String(q.user_answer).split(',').map(s => s.trim()).includes(String(key))) : q.user_answer === String(key)
                }">
                  {{ String(key).toUpperCase() }}. {{ option }}
                </span>
              </div>
            </div>
            <div v-else class="answer-review">
              <div class="answer-item">
                <span class="label">您的答案：</span>
                <span class="value">{{ q.user_answer || '未作答' }}</span>
              </div>
              <div v-if="q.correct_answer && q.is_correct !== null" class="answer-item">
                <span class="label">正确答案：</span>
                <span class="value correct">{{ q.correct_answer }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="actions">
        <router-link to="/student/dashboard" class="btn btn-primary">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../utils/api'
import { formatDate, formatTime } from '../../utils/formatters'

import type { ResultExamSummary, ResultQuestionItem, ResultRecordSummary } from '../../types'

const route = useRoute()
const exam = ref<ResultExamSummary>({
  title: '',
  total_score: 0,
  duration: 0,
})
const record = ref<ResultRecordSummary>({
  score: 0,
  total_score: 0,
  duration: 0,
  time_spent: 0,
})
const questions = ref<ResultQuestionItem[]>([])

const getTypeName = (type: string) => {
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

onMounted(async () => {
  try {
    const response = await api.get(`student/result/${route.params.recordId}/`)
    exam.value = response.data.exam
    record.value = response.data.record
    questions.value = response.data.questions || []
  } catch (error) {
    console.error('Failed to load result:', error)
  }
})
</script>

<style scoped>
.result-detail {
  min-height: 100vh;
  padding: 2rem;
  background: #f8f9fa;
}

.container {
  max-width: 900px;
  margin: 0 auto;
}

.result-header {
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-top: 1rem;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0d6efd 0%, #0a4ed8 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
}

.score-value {
  font-size: 2.5rem;
  font-weight: bold;
}

.score-label {
  font-size: 0.9rem;
}

.score-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-row {
  padding: 0.5rem 0;
}

.section {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.question-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.question-item:last-child {
  border-bottom: none;
}

.question-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.question-num {
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

.user-score {
  color: #28a745;
  font-weight: bold;
}

.status-correct {
  color: #28a745;
  font-weight: bold;
  font-size: 0.85rem;
}

.status-wrong {
  color: #dc3545;
  font-weight: bold;
  font-size: 0.85rem;
}

.status-pending {
  color: #ffc107;
  font-weight: bold;
  font-size: 0.85rem;
}

.status-score {
  color: #7c3aed;
  font-weight: bold;
  font-size: 0.85rem;
}

.question-content {
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.options-review {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.option-review-item span {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  background: #eee;
}

.option-review-item span.correct {
  background: #d4edda;
  color: #155724;
}

.option-review-item span.selected {
  background: #cce5ff;
  color: #004085;
}

.answer-review {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.answer-item {
  display: flex;
}

.answer-item .label {
  font-weight: bold;
  margin-right: 0.5rem;
}

.answer-item .value.correct {
  color: #28a745;
}

.actions {
  margin-top: 1rem;
}

.btn {
  padding: 0.5rem 1.5rem;
  border-radius: 0.25rem;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #0d6efd;
  color: white;
}
</style>
