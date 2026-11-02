import axios from 'axios'
import type { Chapter, KnowledgePoint, Question, ChatResponse, VisualizationResponse } from '@/types'
import { getToken, logout } from '@/utils/auth'

const baseURL = (() => {
  // 生产环境通过 VITE_API_BASE_URL 环境变量配置后端地址
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  // 开发环境走 Vite 代理
  const hasViteClient = !!document.querySelector('script[src="/@vite/client"]')
  if (hasViteClient) {
    return '/api'
  }
  return 'http://localhost:8000/api'
})()

const instance = axios.create({
  baseURL,
  timeout: 15000
})

instance.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

instance.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error?.response?.status === 401) {
      const url = error.config?.url || ''
      if (!url.includes('/auth/login') && !url.includes('/auth/register')) {
        logout()
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const chapterApi = {
  getAll: (): Promise<Chapter[]> => instance.get('/chapters/'),
  getById: (id: number): Promise<Chapter> => instance.get(`/chapters/${id}/`),
  create: (data: { title: string; description?: string; order_index?: number }): Promise<Chapter> => instance.post('/chapters/', data),
  update: (id: number, data: { title?: string; description?: string; order_index?: number }): Promise<Chapter> => instance.put(`/chapters/${id}/`, data),
  delete: (id: number): Promise<void> => instance.delete(`/chapters/${id}/`)
}

export const knowledgePointApi = {
  getAll: (params?: { chapter_id?: number; difficulty?: string }): Promise<KnowledgePoint[]> => 
    instance.get('/knowledge_points/', { params }),
  getById: (id: number): Promise<KnowledgePoint> => instance.get(`/knowledge_points/${id}/`),
  create: (data: { chapter_id: number; content: string; difficulty?: string; category?: string; detail_content?: string; key_points?: string[]; parent_id?: number; order_index?: number }): Promise<KnowledgePoint> => instance.post('/knowledge_points/', data),
  update: (id: number, data: { content?: string; difficulty?: string; category?: string; detail_content?: string; key_points?: string[]; parent_id?: number; order_index?: number }): Promise<KnowledgePoint> => instance.put(`/knowledge_points/${id}/`, data),
  delete: (id: number): Promise<void> => instance.delete(`/knowledge_points/${id}/`)
}

export const questionApi = {
  getAll: (params?: { knowledge_point_id?: number; type?: string; limit?: number }): Promise<Question[]> =>
    instance.get('/questions/', { params }),
  getById: (id: number): Promise<Question> => instance.get(`/questions/${id}/`),
  create: (data: { knowledge_point_id: number; type: string; difficulty?: string; stem: string; options?: string[]; answer: string; analysis?: string; order_index?: number }): Promise<Question> => instance.post('/questions/', data),
  update: (id: number, data: { type?: string; difficulty?: string; stem?: string; options?: string[]; answer?: string; analysis?: string; order_index?: number }): Promise<Question> => instance.put(`/questions/${id}/`, data),
  delete: (id: number): Promise<void> => instance.delete(`/questions/${id}/`),
  batchCreate: (data: Array<{ knowledge_point_id: number; type: string; difficulty?: string; stem: string; options?: string[]; answer: string; analysis?: string; order_index?: number }>): Promise<void> => instance.post('/questions/batch/', data)
}

export interface SlideItem {
  slide_number?: number
  title?: string
  content?: string
  speech?: string
  duration?: number
}

export interface SlidesAudioResponse {
  success: boolean
  audio_urls: string[]
  total: number
  failed_indexes?: number[]
  error?: string
}

export interface AgentHistoryItem {
  id: number
  question: string
  created_at?: string
}

export interface AgentHistoryResponse {
  student_id: string
  questions: AgentHistoryItem[]
}

export const agentApi = {
  chat: (data: { student_question: string; student_id?: string; context?: { chapter_id?: number; knowledge_point_id?: number } }): Promise<ChatResponse> =>
    instance.post('/agent/chat/', data),
  getHistory: (studentId: string): Promise<AgentHistoryResponse> =>
    instance.get(`/agent/history/${encodeURIComponent(studentId)}/`),
  visualize: (data: { topic: string }): Promise<VisualizationResponse> =>
    instance.post('/agent/visualize/', data),
  generateSlidesAudio: (data: { slides: SlideItem[] }): Promise<SlidesAudioResponse> =>
    instance.post('/agent/generate-slides-audio/', data, { timeout: 120000 })
}

export interface KnowledgeGraphNode {
  id: number
  label: string
  category: string
  is_current: boolean
  description: string
  difficulty?: string
}

export interface KnowledgeGraphEdge {
  source: number
  target: number
  relation_type: string
  relation_name: string
  color: string
  lineStyle: string
  icon: string
}

export interface KnowledgeGraphResponse {
  success: boolean
  current_knowledge_point?: {
    id: number
    label: string
    category: string
    description: string
  }
  nodes: KnowledgeGraphNode[]
  edges: KnowledgeGraphEdge[]
  relation_types: {
    [key: string]: {
      name: string
      color: string
      lineStyle: string
      icon: string
    }
  }
  total_nodes: number
  total_edges: number
}

export const knowledgeGraphApi = {
  getById: (knowledge_point_id: number): Promise<KnowledgeGraphResponse> =>
    instance.get(`/knowledge_graph/relations/${knowledge_point_id}/`),
  getByContent: (content: string): Promise<KnowledgeGraphResponse> =>
    instance.get('/knowledge_graph/relations/by-content/', { params: { content } }),
  getRelationTypes: (): Promise<Record<string, { name: string; color: string; lineStyle: string; icon: string }>> =>
    instance.get('/knowledge_graph/relation-types/'),
  getAllWithRelations: (): Promise<Array<{ id: number; content: string; category: string; parent_id: number; chapter_id: number; relation_count: number }>> =>
    instance.get('/knowledge_graph/knowledge-points/with-relations/')
}

export interface LearningRecord {
  id: number
  record_uuid: string
  session_id: string
  student_id: string
  module_type: string
  module_id?: string
  module_name?: string
  knowledge_point_id?: number
  knowledge_point_content?: string
  duration_seconds: number
  study_duration_minutes: number
  status: string
  completion_percentage: number
  interaction_count: number
  last_recorded_duration: number
  last_study_time?: string
  mastered_count: number
  not_mastered_count: number
  extra_data?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface LearningRecordCreate {
  session_id: string
  student_id?: string
  module_type: string
  module_id?: string
  module_name?: string
  knowledge_point_id?: number
  knowledge_point_content?: string
  duration_seconds?: number
  study_duration_minutes?: number
  status?: string
  completion_percentage?: number
  interaction_count?: number
  last_study_time?: string
  mastered_count?: number
  not_mastered_count?: number
  extra_data?: Record<string, unknown>
}

export interface LearningProgressSummary {
  total_duration_seconds: number
  total_study_minutes: number
  total_records: number
  modules_visited: string[]
  knowledge_points_learned: Array<{
    knowledge_point: string
    total_duration: number
    visit_count: number
    modules: string[]
  }>
  module_statistics: Record<string, {
    module_type: string
    module_name: string
    total_duration: number
    visit_count: number
    interaction_count: number
  }>
  overall_completion_percentage: number
}

export const learningProgressApi = {
  startSession: (student_id?: string): Promise<{ success: boolean; session_id: string; message: string }> =>
    instance.post('/learning-progress/session/start', null, { params: { student_id: student_id || 'anonymous' } }),
  endSession: (session_id: string): Promise<{ success: boolean; total_duration_seconds: number; total_records: number }> =>
    instance.post(`/learning-progress/session/end/${session_id}`),
  createRecord: (data: LearningRecordCreate): Promise<LearningRecord> =>
    instance.post('/learning-progress/records/', data),
  batchCreateRecords: (records: LearningRecordCreate[]): Promise<LearningRecord[]> =>
    instance.post('/learning-progress/records/batch/', { records }),
  getRecords: (params?: { student_id?: string; module_type?: string; knowledge_point_id?: number; session_id?: string; start_date?: string; end_date?: string; limit?: number; offset?: number }): Promise<LearningRecord[]> =>
    instance.get('/learning-progress/records/', { params }),
  getSummary: (params?: { student_id?: string; start_date?: string; end_date?: string }): Promise<LearningProgressSummary> =>
    instance.get('/learning-progress/summary/', { params }),
  updateRecord: (record_id: number, data: Partial<LearningRecordCreate>): Promise<LearningRecord> =>
    instance.put(`/learning-progress/records/${record_id}`, data),
  deleteRecord: (record_id: number): Promise<{ success: boolean }> =>
    instance.delete(`/learning-progress/records/${record_id}`),
  deleteSessionRecords: (session_id: string): Promise<{ success: boolean }> =>
    instance.delete(`/learning-progress/records/session/${session_id}`),
  getModuleTypes: (): Promise<{ module_types: Record<string, string>; status_types: Record<string, string> }> =>
    instance.get('/learning-progress/module-types/')
}

// ==================== 管理端 API ====================

export interface DashboardCharts {
  mastery_pie: Array<{ name: string; value: number }>
  study_trend: { dates: string[]; minutes: number[] }
  chapter_bar: { labels: string[]; values: number[] }
  resource_radar: { indicators: Array<{ name: string; max: number }>; values: number[] }
  activity_heatmap: { xLabels: string[]; yLabels: string[]; values: number[][] }
}

export interface FeatureUsage {
  name: string
  value: number
  percentage: number
}

export interface DashboardStats {
  student_count: number
  admin_count: number
  chapters_count: number
  knowledge_points_count: number
  questions_count: number
  course_contents_count: number
  study_records_count: number
  today_study_minutes: number
  abnormal_records_count: number
  mastered_knowledge_points_count: number
  total_kp_students: number
  module_usage: FeatureUsage[]
  charts?: DashboardCharts
}

export interface StudentUsageItem {
  student_no: string
  name: string
  study_minutes: number
  record_count: number
  active_days: number
  favorite_feature: string
  last_active_at?: string | null
  status: string
}

export interface UsageDailyTrend {
  dates: string[]
  labels: string[]
  active_students: number[]
  study_minutes: number[]
  feature_count?: number[]
  average_study_minutes?: number
  average_active_students?: number
  has_anomaly?: boolean
  simulated_flags?: boolean[]
  has_simulated?: boolean
  simulated_days?: number
  anomalies?: {
    index: number
    date: string
    weekday: string
    value: number
    average: number
    deviation: number
    direction: 'up' | 'down'
    description: string
  }[]
}

export interface UsageMetrics {
  active_students: number
  feature_count: number
  study_minutes: number
  daily_avg_minutes: number
  completion_rate: number
  learning_records: number
  completed_records: number
}

export interface UsageComparisonItem {
  key: string
  label: string
  unit: string
  current: number
  previous: number
  delta: number
  change_percent: number | null
  trend: 'up' | 'down' | 'flat'
}

export interface UsageWeakKnowledgePoint {
  knowledge_point_id: number
  content: string
  chapter_title: string
  difficulty_level: number | string
  student_count: number
  mastered_count: number
  not_mastered_count: number
  mastery_rate: number
  average_study_count: number
  average_study_minutes: number
  attention: string
}

export interface UsageRecent {
  range: {
    days: number
    start_date: string
    end_date: string
    previous_start_date: string
    previous_end_date: string
    label: string
  }
  metrics: UsageMetrics
  daily: UsageDailyTrend
  comparison: {
    current: UsageMetrics
    previous: UsageMetrics
    items: UsageComparisonItem[]
  }
  weak_knowledge_points: UsageWeakKnowledgePoint[]
  basis: {
    learning_records: number
    study_records: number
    chat_records: number
    previous_learning_records: number
    previous_study_records: number
    previous_chat_records: number
    note: string
  }
}

export interface UsageOverview {
  generated_at: string
  range_days: number
  summary: {
    active_students: number
    today_active_students: number
    total_study_minutes: number
    avg_minutes_per_student: number
    interaction_count: number
    feature_count: number
  }
  recent?: UsageRecent
  feature_usage: FeatureUsage[]
  daily_trend: UsageDailyTrend
  hour_distribution: { labels: string[]; values: number[] }
  student_usage: StudentUsageItem[]
}

export interface StudyRecordItem {
  id: number
  student_id: string
  course_name?: string
  chapter_name?: string
  knowledge_point_id?: number
  knowledge_point_content?: string
  study_date: string
  duration_minutes: number
  study_type: string
  is_abnormal: boolean
  abnormal_reason?: string
  notes?: string
  source: string
  created_at?: string
}

export interface KPTag {
  id: number
  name: string
  category: string
  color?: string
  description?: string
  children?: KPTag[]
}

export interface StudentKPItem {
  id: number
  student_id: string
  knowledge_point_id: number
  kp_content?: string
  chapter_id?: number
  mastery_level: string
  difficulty_level: number
  last_study_date?: string
  study_count: number
  total_study_minutes: number
  note?: string
  tags: Array<{ id: number; name: string; color?: string }>
}

export interface CourseContentItem {
  id: number
  content_type: string
  title: string
  content?: string
  content_metadata?: Record<string, unknown>
  status: string
  chapter_id?: number
  chapter_title?: string | null
  knowledge_point_id?: number
  knowledge_point_content?: string | null
  created_by?: number
  published_at?: string
  created_at?: string
  updated_at?: string
}

export interface QuestionUsageStats {
  id: number
  question_id: number
  usage_count: number
  correct_count: number
  average_time_seconds?: number
  difficulty_rating?: number
  last_used_at?: string
}

export interface VizTemplateItem {
  id: number
  name: string
  chart_type: string
  config: Record<string, unknown>
  data_source?: string
  is_public: boolean
  knowledge_point_id?: number
  knowledge_point_content?: string | null
  created_by?: number
  created_at?: string
  updated_at?: string
}

export const adminApi = {
  getDashboard: (): Promise<DashboardStats> =>
    instance.get('/admin/'),

  // RBAC
  listRoles: (): Promise<any[]> =>
    instance.get('/admin/roles/'),
  createRole: (data: { name: string; description?: string }) =>
    instance.post('/admin/roles/', data),
  updateRole: (id: number, data: { name?: string; description?: string }) =>
    instance.put(`/admin/roles/${id}/`, data),
  deleteRole: (id: number) =>
    instance.delete(`/admin/roles/${id}/`),
  assignRolePermissions: (roleId: number, permissionIds: number[]) =>
    instance.post(`/admin/roles/${roleId}/permissions/`, permissionIds),
  listPermissions: (module?: string) =>
    instance.get('/admin/permissions/', { params: { module } }),
  initRbac: () =>
    instance.get('/admin/rbac/init/'),

  // Students
  listStudents: (params?: { page?: number; page_size?: number; search?: string; role?: string }) =>
    instance.get('/admin/students/', { params }),
  createStudent: (data: { student_id: string; username: string; password?: string; name?: string; role?: string }) =>
    instance.post('/admin/students/', data),
  updateStudent: (id: number, data: { name?: string; role?: string; is_active?: boolean; password?: string }) =>
    instance.put(`/admin/students/${id}/`, data),
  deactivateStudent: (id: number) =>
    instance.delete(`/admin/students/${id}/`),
  getStudentStudySummary: (id: number, period: string = 'month') =>
    instance.get(`/admin/students/${id}/study-summary/`, { params: { period } }),

  // Study Records
  listStudyRecords: (params?: { page?: number; page_size?: number; student_id?: string; start_date?: string; end_date?: string; is_abnormal?: boolean; study_type?: string }) =>
    instance.get('/admin/study-records/', { params }),
  createStudyRecord: (data: any) =>
    instance.post('/admin/study-records/', data),
  updateStudyRecord: (id: number, data: any) =>
    instance.put(`/admin/study-records/${id}/`, data),
  deleteStudyRecord: (id: number) =>
    instance.delete(`/admin/study-records/${id}/`),
  batchCreateStudyRecords: (records: any[]) =>
    instance.post('/admin/study-records/batch/', { records }),
  getStudyStatistics: (start_date: string, end_date: string, group_by: string = 'day') =>
    instance.get('/admin/study-records/statistics/', { params: { start_date, end_date, group_by } }),
  detectAnomalies: (min_minutes: number = 5, max_minutes: number = 480) =>
    instance.post('/admin/study-records/detect-anomalies/', null, { params: { min_minutes, max_minutes } }),
  exportStudyRecords: (params?: { start_date?: string; end_date?: string; student_id?: string }) =>
    instance.get('/admin/study-records/export/', { params }),
  listKPTags: (category?: string) =>
    instance.get('/admin/kp-tags/', { params: { category } }),
  createKPTag: (data: { name: string; category?: string; parent_id?: number; color?: string; description?: string }) =>
    instance.post('/admin/kp-tags/', data),
  updateKPTag: (id: number, data: any) =>
    instance.put(`/admin/kp-tags/${id}/`, data),
  deleteKPTag: (id: number) =>
    instance.delete(`/admin/kp-tags/${id}/`),

  // Student KP
  listStudentKPs: (params?: { student_id?: string; mastery_level?: string; chapter_id?: number }) =>
    instance.get('/admin/student-kps/', { params }),
  createStudentKP: (data: any) =>
    instance.post('/admin/student-kps/', data),
  updateStudentKP: (id: number, data: any) =>
    instance.put(`/admin/student-kps/${id}/`, data),
  addKPTag: (kpId: number, tagId: number) =>
    instance.post(`/admin/student-kps/${kpId}/tags/`, { tag_id: tagId }),
  removeKPTag: (kpId: number, tagId: number) =>
    instance.delete(`/admin/student-kps/${kpId}/tags/${tagId}/`),
  getStudentKPStats: (student_id?: string) =>
    instance.get('/admin/student-kps/statistics/', { params: { student_id } }),

  // Course Contents
  listCourseContents: (params?: { page?: number; page_size?: number; status?: string; chapter_id?: number; type?: string; search?: string }) =>
    instance.get('/admin/course-contents/', { params }),
  getCourseContent: (id: number) =>
    instance.get(`/admin/course-contents/${id}/`),
  createCourseContent: (data: any) =>
    instance.post('/admin/course-contents/', data),
  updateCourseContent: (id: number, data: any) =>
    instance.put(`/admin/course-contents/${id}/`, data),
  deleteCourseContent: (id: number) =>
    instance.delete(`/admin/course-contents/${id}/`),
  publishCourseContent: (id: number) =>
    instance.post(`/admin/course-contents/${id}/publish/`),
  archiveCourseContent: (id: number) =>
    instance.post(`/admin/course-contents/${id}/archive/`),
  listContentVersions: (id: number) =>
    instance.get(`/admin/course-contents/${id}/versions/`),
  restoreContentVersion: (id: number, versionId: number) =>
    instance.post(`/admin/course-contents/${id}/versions/${versionId}/restore/`),

  // Questions Admin
  listQuestionsAdmin: (params?: { page?: number; page_size?: number; type?: string; difficulty?: string; chapter_id?: number; knowledge_point_id?: number }) =>
    instance.get('/admin/questions/', { params }),
  createQuestionAdmin: (data: any) =>
    instance.post('/admin/questions/', data),
  updateQuestionAdmin: (id: number, data: any) =>
    instance.put(`/admin/questions/${id}/`, data),
  deleteQuestionAdmin: (id: number) =>
    instance.delete(`/admin/questions/${id}/`),
  batchImportQuestions: (questions: any[], skip_on_error: boolean = false) =>
    instance.post('/admin/questions/batch-import/', { questions, skip_on_error }),
  exportQuestions: (params?: { knowledge_point_id?: number; difficulty?: string; type?: string; format?: string }) =>
    instance.post('/admin/questions/export/', params),
  getQuestionUsage: (id: number) =>
    instance.get(`/admin/questions/${id}/usage/`),
  getQuestionsUsageStats: () =>
    instance.get('/admin/question-usage-stats/'),

  // Visualization Templates
  listVizTemplates: (params?: { page?: number; page_size?: number; chart_type?: string; knowledge_point_id?: number; is_public?: boolean }) =>
    instance.get('/admin/viz-templates/', { params }),
  getVizTemplate: (id: number) =>
    instance.get(`/admin/viz-templates/${id}/`),
  createVizTemplate: (data: any) =>
    instance.post('/admin/viz-templates/', data),
  updateVizTemplate: (id: number, data: any) =>
    instance.put(`/admin/viz-templates/${id}/`, data),
  deleteVizTemplate: (id: number) =>
    instance.delete(`/admin/viz-templates/${id}/`),
  listVizChartTypes: () =>
    instance.get('/admin/viz-types/'),

  // 学生软件使用情况
  getUsageOverview: (days: number = 10): Promise<UsageOverview> =>
    instance.get('/admin/usage/', { params: { days } }),
}

export interface AuthLoginRequest {
  account: string
  password: string
}

export interface AuthRegisterRequest {
  student_id: string
  username: string
  password: string
  name?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: {
    id: number
    student_id: string
    username: string
    name: string
    role: string
  }
}

export interface StudentProfile {
  id: number
  student_id: string
  username: string
  name: string
  role: string
  is_active: boolean
  last_login_at?: string
  created_at: string
}

export interface StudentProgressOverview {
  student_id: string
  total_study_minutes: number
  total_modules_accessed: number
  overall_completion_percentage: number
  module_progress_list: Array<{
    module_uuid: string
    module_name: string
    completion_percentage: number
    last_study_time?: string
    study_duration_minutes: number
    mastered_count: number
    not_mastered_count: number
  }>
  last_learning_time?: string
}

export const authApi = {
  login: (data: AuthLoginRequest): Promise<AuthResponse> =>
    instance.post('/auth/login', data),
  register: (data: AuthRegisterRequest): Promise<StudentProfile> =>
    instance.post('/auth/register', data),
  getProfile: (): Promise<StudentProfile> =>
    instance.get('/auth/profile'),
  logout: (): Promise<{ success: boolean }> =>
    instance.post('/auth/logout'),
  changePassword: (old_password: string, new_password: string): Promise<{ success: boolean }> =>
    instance.put('/auth/change-password', { old_password, new_password }),
  getProgress: (student_id: string): Promise<StudentProgressOverview> =>
    instance.get(`/auth/students/${student_id}/progress`)
}
