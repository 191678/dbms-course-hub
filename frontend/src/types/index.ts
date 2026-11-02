export interface Chapter {
  id: number
  title: string
  description: string
  order_index: number
  knowledge_points?: KnowledgePoint[]
}

export interface KnowledgePoint {
  id: number
  chapter_id: number
  parent_id?: number
  content: string
  summary?: string
  difficulty: string
  category?: string
  detail_content?: string
  key_points?: string[]
  image_prompt?: string
  video_script?: string
  learning_steps?: string[]
  tips?: string[]
  faq?: Array<{ question: string; answer: string }>
  image_url?: string
  order_index?: number
  children?: KnowledgePoint[]
  questions?: Question[]
}

export interface Question {
  id: number
  knowledge_point_id: number
  type: '单选' | '多选' | '判断' | 'SQL编程' | '填空'
  difficulty: 'easy' | 'medium' | 'hard'
  stem: string
  options?: string[]
  answer: string
  analysis?: string
  order_index?: number
}

export interface SavedAnswer {
  questionId: number
  answer: string
  savedAt: string
  knowledgePointId?: number
}

export interface PracticeRecord {
  knowledgePointId: number
  answers: SavedAnswer[]
  startTime: string
  lastUpdated: string
}

export interface ChatRequest {
  student_question: string
  context?: {
    chapter_id?: number
    knowledge_point_id?: number
  }
}

export interface ChatResponse {
  answer: string
  tool_used?: string
  context?: {
    chapter_id?: number
    knowledge_point_id?: number
  }
  media_data?: {
    media_type: string
    format: string
    content?: string
    title?: string
    steps?: Array<{ frame: number; speech: string; highlight_element: string }>
    duration?: string
  }
  questions?: Array<{ id: number; type: string; stem: string; options?: string[]; answer: string; analysis: string }>
}

export interface VisualizationDiagram {
  media_type: string
  format: string
  content: string
  title: string
}

export interface VisualizationResponse {
  success: boolean
  knowledge_point?: string
  chapter?: string
  category?: string
  definition?: string
  key_points?: string[]
  theory_content?: string
  diagram?: VisualizationDiagram
  relationship_explanation?: string
}
