export interface User {
  id: number
  username: string
  email: string
  role: 'student' | 'teacher'
  is_superuser?: boolean
}

export interface ApiResponse<T = unknown> {
  data: T
  status?: number
  message?: string
}

export interface TypeCounts {
  single?: number
  multiple?: number
  judge?: number
  fill?: number
  essay?: number
  discussion?: number
}

export type ExamStatus = 'draft' | 'published' | 'ongoing' | 'finished'
export type QuestionType = 'single' | 'multiple' | 'judge' | 'fill' | 'essay' | 'discussion'

export interface Question {
  id: number
  type: QuestionType
  content: string
  options?: Record<string, string> | string[]
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

export interface TeacherExamListItem extends Exam {
  status: ExamStatus
  question_count: number
  type_counts: TypeCounts
  student_count: number
  pending_grading_count: number
}

export interface StudentExamDetail {
  id: number
  title: string
  description?: string
  start_time: string
  end_time: string
  duration: number
  total_score: number
  question_count: number
  type_counts: TypeCounts
  is_published?: boolean
  has_taken: boolean
  score?: number | null
  record_id?: number | null
  needs_grading?: boolean
  record_start_time?: string | null
  record_deadline?: string | null
}

export interface ExamTakingSummary {
  id: number
  title: string
  duration: number
  total_score: number
}

export interface TakingQuestion {
  id: number
  type: QuestionType | string
  content: string
  options: Record<string, string>
  score: number
  order: number
}

export interface ResultExamSummary {
  title: string
  total_score: number
  duration: number
  submit_time?: string | null
}

export interface ResultRecordSummary {
  score: number
  total_score: number
  duration: number
  time_spent: number
  submit_time?: string | null
  is_graded?: boolean
}

export interface ResultQuestionItem {
  id: number
  type: QuestionType | string
  content: string
  options?: Record<string, string>
  user_answer: string | string[]
  correct_answer: string
  score: number
  is_correct: boolean | null
  essay_score?: number | null
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
