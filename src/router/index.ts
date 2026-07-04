import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/Chat.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/student/dashboard',
    name: 'StudentDashboard',
    component: () => import('../views/student/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/exams',
    name: 'StudentExams',
    component: () => import('../views/student/Exams.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/exam/:examId',
    name: 'StudentExamDetail',
    component: () => import('../views/student/ExamDetail.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/exam/:examId/take',
    name: 'StudentExamTaking',
    component: () => import('../views/student/ExamTaking.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/results',
    name: 'StudentResults',
    component: () => import('../views/student/Results.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/result/:recordId',
    name: 'StudentResult',
    component: () => import('../views/student/ResultDetail.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/wrong-questions',
    name: 'StudentWrongQuestions',
    component: () => import('../views/student/WrongQuestions.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/profile',
    name: 'StudentProfile',
    component: () => import('../views/student/Profile.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/teacher/dashboard',
    name: 'TeacherDashboard',
    component: () => import('../views/teacher/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/questions',
    name: 'TeacherQuestions',
    component: () => import('../views/teacher/QuestionManagement.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/questions/import',
    name: 'TeacherImportQuestions',
    component: () => import('../views/teacher/ImportQuestions.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/exams',
    name: 'TeacherExams',
    component: () => import('../views/teacher/ExamManagement.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/students',
    name: 'TeacherStudents',
    component: () => import('../views/teacher/StudentManagement.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/student/:studentId/exams',
    name: 'TeacherStudentExams',
    component: () => import('../views/teacher/StudentExamHistory.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/exam/create',
    name: 'TeacherCreateExam',
    component: () => import('../views/teacher/CreateExam.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/exam/random',
    name: 'TeacherRandomExam',
    component: () => import('../views/teacher/RandomExam.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/exam/:examId',
    name: 'TeacherExamDetail',
    component: () => import('../views/teacher/ExamDetail.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/exam/:examId/students',
    name: 'TeacherExamStudents',
    component: () => import('../views/teacher/ExamStudents.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/grade/:recordId',
    name: 'TeacherGrade',
    component: () => import('../views/teacher/GradeExam.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/result/:recordId',
    name: 'TeacherExamResult',
    component: () => import('../views/teacher/TeacherExamResult.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/profile',
    name: 'TeacherProfile',
    component: () => import('../views/teacher/Profile.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  
  if (to.meta.requiresAuth && !user) {
    return { path: '/login' }
  }
  
  if (to.meta.requiresAuth && user && to.meta.role && user.role !== to.meta.role) {
    if (user.role === 'teacher') {
      return { path: '/teacher/dashboard' }
    } else {
      return { path: '/student/dashboard' }
    }
  }
  
  return true
})

export default router
