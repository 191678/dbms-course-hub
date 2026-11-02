import { ref, onMounted, onBeforeUnmount } from 'vue'
import { learningProgressApi } from '@/api'
import { getUser } from '@/utils/auth'
import type { LearningRecordCreate } from '@/api'

const MODULE_TYPES = {
  knowledge_visualization: '知识可视化',
  knowledge_graph: '知识关联图谱',
  theory_content: '理论内容',
  key_points: '关键要点',
  diagram: '图表展示',
  agent_interaction: 'AI助教交互',
  search: '知识搜索',
  node_click: '节点点击'
}

export function useLearningProgress() {
  const sessionId = ref<string>('')
  const startTime = ref<number>(0)
  const currentModule = ref<string>('')
  const currentKnowledgePoint = ref<string>('')
  const interactionCount = ref<number>(0)
  const accumulatedDuration = ref<number>(0)
  const timerInterval = ref<number | null>(null)
  const currentStudentId = ref<string>('anonymous')

  const moduleDurations = ref<Map<string, number>>(new Map())
  const moduleInteractions = ref<Map<string, number>>(new Map())

  const getStudentId = (): string => {
    const user = getUser()
    if (user) {
      currentStudentId.value = user.student_id
      return user.student_id
    }
    return currentStudentId.value
  }

  const startSession = async (studentId?: string) => {
    const sid = studentId || getStudentId()
    try {
      const response = await learningProgressApi.startSession(sid)
      sessionId.value = response.session_id
      startTime.value = Date.now()
      return response.session_id
    } catch (error) {
      console.error('Failed to start session:', error)
      sessionId.value = `local-${Date.now()}`
      return sessionId.value
    }
  }

  const recordModuleAccess = async (
    moduleType: string,
    knowledgePoint?: string,
    moduleId?: string
  ) => {
    currentModule.value = moduleType
    currentKnowledgePoint.value = knowledgePoint || ''
    interactionCount.value++

    try {
      const studentId = getStudentId()
      const now = new Date()
      const record: LearningRecordCreate = {
        session_id: sessionId.value,
        student_id: studentId,
        module_type: moduleType,
        module_id: moduleId,
        module_name: MODULE_TYPES[moduleType] || moduleType,
        knowledge_point_content: knowledgePoint,
        duration_seconds: accumulatedDuration.value,
        study_duration_minutes: Math.floor(accumulatedDuration.value / 60),
        status: 'viewing',
        interaction_count: interactionCount.value,
        last_study_time: now.toISOString(),
        extra_data: {
          action: 'module_access',
          timestamp: now.toISOString()
        }
      }
      await learningProgressApi.createRecord(record)
    } catch (error) {
      console.error('Failed to record module access:', error)
    }
  }

  const updateDuration = async (additionalSeconds: number) => {
    accumulatedDuration.value += additionalSeconds

    if (currentModule.value) {
      const currentDuration = moduleDurations.value.get(currentModule.value) || 0
      moduleDurations.value.set(currentModule.value, currentDuration + additionalSeconds)
    }
  }

  const recordInteraction = async (
    moduleType: string,
    action: string,
    knowledgePoint?: string
  ) => {
    interactionCount.value++
    const currentCount = moduleInteractions.value.get(moduleType) || 0
    moduleInteractions.value.set(moduleType, currentCount + 1)

    try {
      const studentId = getStudentId()
      const now = new Date()
      const record: LearningRecordCreate = {
        session_id: sessionId.value,
        student_id: studentId,
        module_type: moduleType,
        knowledge_point_content: knowledgePoint || currentKnowledgePoint.value,
        duration_seconds: accumulatedDuration.value,
        study_duration_minutes: Math.floor(accumulatedDuration.value / 60),
        status: 'viewing',
        interaction_count: 1,
        last_study_time: now.toISOString(),
        extra_data: {
          action,
          timestamp: now.toISOString()
        }
      }
      await learningProgressApi.createRecord(record)
    } catch (error) {
      console.error('Failed to record interaction:', error)
    }
  }

  const startTracking = () => {
    if (timerInterval.value) {
      clearInterval(timerInterval.value)
    }

    timerInterval.value = window.setInterval(() => {
      updateDuration(1)
    }, 1000)
  }

  const stopTracking = async () => {
    if (timerInterval.value) {
      clearInterval(timerInterval.value)
      timerInterval.value = null
    }

    if (sessionId.value && accumulatedDuration.value > 0) {
      try {
        const studentId = getStudentId()
        const now = new Date()
        const record: LearningRecordCreate = {
          session_id: sessionId.value,
          student_id: studentId,
          module_type: currentModule.value || 'knowledge_visualization',
          module_name: MODULE_TYPES[currentModule.value] || currentModule.value,
          knowledge_point_content: currentKnowledgePoint.value,
          duration_seconds: accumulatedDuration.value,
          study_duration_minutes: Math.floor(accumulatedDuration.value / 60),
          status: 'viewing',
          interaction_count: interactionCount.value,
          last_study_time: now.toISOString(),
          extra_data: {
            action: 'auto_save',
            timestamp: now.toISOString()
          }
        }
        await learningProgressApi.createRecord(record)
      } catch (error) {
        console.error('Failed to auto-save:', error)
      }
    }
  }

  const endSession = async () => {
    stopTracking()

    if (sessionId.value) {
      try {
        await learningProgressApi.endSession(sessionId.value)
      } catch (error) {
        console.error('Failed to end session:', error)
      }
    }
  }

  const handleVisibilityChange = () => {
    if (document.visibilityState === 'hidden') {
      stopTracking()
    } else {
      if (sessionId.value) {
        startTracking()
      }
    }
  }

  const handlePageHide = () => {
    stopTracking()
    endSession()
  }

  const getProgressSummary = async (studentId?: string) => {
    try {
      const sid = studentId || getStudentId()
      const summary = await learningProgressApi.getSummary({ student_id: sid })
      return summary
    } catch (error) {
      console.error('Failed to get progress summary:', error)
      return null
    }
  }

  const getModuleDuration = (moduleType: string): number => {
    return moduleDurations.value.get(moduleType) || 0
  }

  const getTotalDuration = (): number => {
    return accumulatedDuration.value
  }

  const initTracking = async () => {
    const studentId = getStudentId()
    await startSession(studentId)
    startTracking()

    document.addEventListener('visibilitychange', handleVisibilityChange)
    document.addEventListener('pagehide', handlePageHide)
  }

  const cleanupTracking = () => {
    document.removeEventListener('visibilitychange', handleVisibilityChange)
    document.removeEventListener('pagehide', handlePageHide)
    endSession()
  }

  return {
    sessionId,
    startTime,
    currentModule,
    currentKnowledgePoint,
    interactionCount,
    accumulatedDuration,
    moduleDurations,
    MODULE_TYPES,
    initTracking,
    cleanupTracking,
    recordModuleAccess,
    recordInteraction,
    updateDuration,
    getProgressSummary,
    getModuleDuration,
    getTotalDuration,
    startSession,
    endSession,
    getStudentId
  }
}
