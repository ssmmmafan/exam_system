<template>
  <div class="exam-detail">
    <div class="container">
      <h2>{{ exam.title }}</h2>
      <div class="exam-info">
        <div class="info-item">
          <span class="label">考试开始时间：</span>
          <span class="value">{{ formatDate(exam.start_time) }}</span>
        </div>
        <div class="info-item">
          <span class="label">考试结束时间：</span>
          <span class="value">{{ formatDate(exam.end_time) }}</span>
        </div>
        <div v-if="exam.record_start_time" class="info-item highlight">
          <span class="label">你的开始时间：</span>
          <span class="value">{{ formatDate(exam.record_start_time) }}</span>
        </div>
        <div v-if="exam.record_deadline" class="info-item highlight">
          <span class="label">你的截止时间：</span>
          <span class="value">{{ formatDate(exam.record_deadline) }}</span>
        </div>
        <div class="info-item">
          <span class="label">考试时长：</span>
          <span class="value">{{ exam.duration }} 分钟</span>
        </div>
        <div class="info-item">
          <span class="label">题目数量：</span>
          <span class="value">{{ exam.question_count }} 题</span>
        </div>
        <div class="info-item">
          <span class="label">总分：</span>
          <span class="value">{{ exam.total_score }} 分</span>
        </div>
        <div class="info-item">
          <span class="label">题型分布：</span>
          <span class="value">
            <span class="type-tags">
              <span v-if="exam.type_counts?.single" class="type-tag type-single">单选题 {{ exam.type_counts.single }}</span>
              <span v-if="exam.type_counts?.multiple" class="type-tag type-multiple">多选题 {{ exam.type_counts.multiple }}</span>
              <span v-if="exam.type_counts?.judge" class="type-tag type-judge">判断题 {{ exam.type_counts.judge }}</span>
              <span v-if="exam.type_counts?.fill" class="type-tag type-fill">填空题 {{ exam.type_counts.fill }}</span>
              <span v-if="exam.type_counts?.essay" class="type-tag type-essay">简答题 {{ exam.type_counts.essay }}</span>
              <span v-if="exam.type_counts?.discussion" class="type-tag type-discussion">论述题 {{ exam.type_counts.discussion }}</span>
            </span>
          </span>
        </div>
      </div>
      <div v-if="exam.score !== null" class="score-section">
        <div :class="['score-card', { 'score-card-pending': exam.needs_grading }]">
          <div class="score-header">
            考试成绩
            <span v-if="exam.needs_grading" class="pending-badge">部分待批改</span>
          </div>
          <div class="score-body">
            <span class="score-value">{{ exam.score }}</span>
            <span class="score-divider">/</span>
            <span class="score-total">{{ exam.total_score }}</span>
            <span class="score-unit">分</span>
          </div>
          <p v-if="exam.needs_grading" class="pending-hint">含简答/论述题，需老师批改后方可显示最终成绩</p>
          <router-link :to="`/student/result/${exam.record_id}`" class="btn btn-score">查看得分详情</router-link>
        </div>
      </div>
      <div class="actions">
        <router-link v-if="!exam.has_taken && exam.record_id && canStartExam" :to="`/student/exam/${exam.id}/take`" class="btn btn-warning">继续考试</router-link>
        <router-link v-else-if="!exam.has_taken && canStartExam" :to="`/student/exam/${exam.id}/take`" class="btn btn-primary">开始考试</router-link>
        <router-link v-else-if="!exam.has_taken && !canStartExam" to="/student/exams" class="btn btn-primary disabled-link">考试已结束</router-link>
        <router-link v-else :to="`/student/result/${exam.record_id}`" class="btn btn-primary">查看成绩</router-link>
        <router-link to="/student/dashboard" class="btn btn-secondary">返回</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../utils/api'
import { formatDate } from '../../utils/formatters'

const route = useRoute()
const exam = ref({})

const canStartExam = computed(() => {
  if (!exam.value.end_time) return false
  const now = new Date()
  const endTime = new Date(exam.value.end_time)
  return now < endTime
})

onMounted(async () => {
  try {
    const response = await api.get(`student/exam/${route.params.examId}/`)
    exam.value = response.data
  } catch (error) {
    console.error('Failed to load exam detail:', error)
  }
})
</script>

<style scoped>
.exam-detail {
  min-height: 100vh;
  padding: 2rem;
  background: #f8f9fa;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.exam-info {
  margin: 2rem 0;
}

.info-item {
  display: flex;
  padding: 0.75rem 0;
  border-bottom: 1px solid #eee;
  align-items: flex-start;
}

.label {
  font-weight: bold;
  color: #666;
  min-width: 100px;
  flex-shrink: 0;
}

.value {
  color: #333;
  flex: 1;
}

.type-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.type-tag {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.type-single { background: #e3f2fd; color: #1565c0; }
.type-multiple { background: #e8f5e9; color: #2e7d32; }
.type-judge { background: #fff3e0; color: #e65100; }
.type-fill { background: #fce4ec; color: #c2185b; }
.type-essay { background: #f3e5f5; color: #7b1fa2; }
.type-discussion { background: #fce4ec; color: #d81b60; }

.score-section {
  margin: 1.5rem 0;
}

.score-card {
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  border: 1px solid #86efac;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}

.score-card-pending {
  background: linear-gradient(135deg, #fefce8, #fef9c3);
  border-color: #fde047;
}

.score-header {
  font-size: 14px;
  color: #166534;
  font-weight: 500;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.score-card-pending .score-header {
  color: #854d0e;
}

.pending-badge {
  padding: 2px 8px;
  background: #fef3c7;
  color: #92400e;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.pending-hint {
  font-size: 12px;
  color: #a16207;
  margin: 0 0 12px 0;
}

.score-body {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-bottom: 12px;
}

.score-body .score-value {
  font-size: 32px;
  font-weight: 700;
  color: #16a34a;
}

.score-body .score-divider {
  font-size: 20px;
  color: #86efac;
}

.score-body .score-total {
  font-size: 20px;
  font-weight: 600;
  color: #166534;
}

.score-body .score-unit {
  font-size: 14px;
  color: #166534;
}

.actions {
  margin-top: 2rem;
}

.btn {
  margin-right: 1rem;
  padding: 0.5rem 1.5rem;
  border-radius: 0.25rem;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #0d6efd;
  color: white;
}

.disabled-link {
  background: #6c757d;
  color: white;
  cursor: not-allowed;
  opacity: 0.7;
  pointer-events: none;
}

.btn-score {
  background: #16a34a;
  color: white;
  padding: 8px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-score:hover {
  background: #15803d;
  transform: translateY(-1px);
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.info-item.highlight {
  background: #fffbe6;
  border-left: 3px solid #ffc107;
  padding-left: 12px;
}
</style>
