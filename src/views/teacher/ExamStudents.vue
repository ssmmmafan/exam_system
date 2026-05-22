<template>
  <div class="teacher-page-container">
    <TeacherSidebar :isCollapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <div :class="['teacher-main-content', { 'sidebar-collapsed': sidebarCollapsed }]">
      <div class="header-row">
        <h2>考试学生列表</h2>
        <router-link :to="`/teacher/exam/${examId}`" class="btn btn-secondary">返回考试详情</router-link>
      </div>
      <div v-if="exam" class="exam-info">
        <h3>{{ exam.title }}</h3>
        <p>{{ exam.description }}</p>
        <p>时间：{{ exam.start_time }} - {{ exam.end_time }}</p>
      </div>
      <div class="student-list">
        <div v-if="students.length === 0" class="empty-state">
          暂无学生参加此考试
        </div>
        <table class="student-table" v-else>
          <thead>
            <tr>
              <th>学生姓名</th>
              <th>状态</th>
              <th>得分</th>
              <th>提交时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in students" :key="student.record_id">
              <td>{{ student.student_name }}</td>
              <td>
                <span :class="getStatusClass(student)">
                  {{ getStatusText(student) }}
                </span>
              </td>
              <td>{{ student.score || '-' }}</td>
              <td>{{ student.submit_time || '-' }}</td>
              <td>
                <button 
                  v-if="student.is_finished && !student.is_graded" 
                  @click="goToGrade(student.record_id)" 
                  class="btn btn-success btn-sm"
                >
                  批改
                </button>
                <button 
                  v-else-if="student.is_graded" 
                  @click="goToGrade(student.record_id)" 
                  class="btn btn-info btn-sm"
                >
                  查看批改
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, inject } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../utils/api'
import TeacherSidebar from '../../components/TeacherSidebar.vue'

const route = useRoute()
const sidebarCollapsed = inject('sidebarCollapsed', ref(false))
const toggleSidebar = inject('toggleSidebar', () => {})
const examId = ref(route.params.examId)
const exam = ref(null)
const students = ref([])

onMounted(async () => {
  try {
    const response = await api.get(`teacher/exam/${examId.value}/students/`)
    exam.value = {
      title: response.data.exam_title,
      description: '',
      start_time: '',
      end_time: ''
    }
    students.value = response.data.students || []
  } catch (error) {
    console.error('Failed to load exam students:', error)
  }
})

const getStatusClass = (student) => {
  if (student.is_graded) return 'status-graded'
  if (student.is_finished) return 'status-finished'
  if (student.is_started) return 'status-started'
  return 'status-pending'
}

const getStatusText = (student) => {
  if (student.is_graded) return '已批改'
  if (student.is_finished) return '已提交'
  if (student.is_started) return '进行中'
  return '未开始'
}

const goToGrade = (recordId) => {
  window.location.href = `/teacher/grade/${recordId}`
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

.main-content {
  flex: 1;
  padding: 2rem;
  background: #f5f5f5;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  text-decoration: none;
  font-size: 0.875rem;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.exam-info {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.student-list {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.student-table {
  width: 100%;
  border-collapse: collapse;
}

.student-table th,
.student-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.student-table th {
  background: #f8f9fa;
  font-weight: bold;
}

.status-pending {
  color: #6c757d;
  background: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.status-started {
  color: #0d6efd;
  background: #e7f3ff;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.status-finished {
  color: #28a745;
  background: #d4edda;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.status-graded {
  color: #17a2b8;
  background: #d1ecf1;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
}
</style>
