export interface User {
  id: number
  username: string
  email: string
  role: 'student' | 'teacher'
  is_superuser?: boolean
}

export interface ApiResponse<T = any> {
  data: T
  status?: number
  message?: string
}

export interface Question {
  id: number
  type: 'single' | 'multiple' | 'judge' | 'fill' | 'essay'
  content: string
  options?: string[]
  answer: string
  score: number
  analysis?: string
  difficulty?: string
  chapter?: string
  knowledge_point?: string
}

export interface Exam {
  id: number
  title: string
  description?: string
  start_time: string
  end_time: string
  duration: number
  total_score: number
  is_published: boolean
  allow_late_submit?: boolean
}

export interface ExamRecord {
  id: number
  exam_id: number
  exam_title: string
  student_id: number
  answers: Record<string, string>
  score: number | null
  is_finished: boolean
  is_graded: boolean
  submit_time?: string
  time_spent: number
}
