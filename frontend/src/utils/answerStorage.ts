import type { SavedAnswer, PracticeRecord } from '@/types'

const STORAGE_KEY = 'practice_answers'
const MAX_LENGTH = 2000

/**
 * 答案存储服务 - 使用 localStorage 实现持久化存储
 */

function getAllRecords(): Record<number, PracticeRecord> {
  const data = localStorage.getItem(STORAGE_KEY)
  if (!data) return {}
  try {
    return JSON.parse(data)
  } catch {
    return {}
  }
}

function saveAllRecords(records: Record<number, PracticeRecord>): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records))
}

/**
 * 保存单个答案
 */
export function saveAnswer(knowledgePointId: number, questionId: number, answer: string): void {
  const records = getAllRecords()
  if (!records[knowledgePointId]) {
    records[knowledgePointId] = {
      knowledgePointId,
      answers: [],
      startTime: new Date().toISOString(),
      lastUpdated: new Date().toISOString()
    }
  }

  const record = records[knowledgePointId]
  const existing = record.answers.find(a => a.questionId === questionId)

  if (existing) {
    existing.answer = answer
    existing.savedAt = new Date().toISOString()
  } else {
    record.answers.push({
      questionId,
      answer,
      savedAt: new Date().toISOString(),
      knowledgePointId
    })
  }

  record.lastUpdated = new Date().toISOString()
  saveAllRecords(records)
}

/**
 * 批量保存答案
 */
export function saveAnswers(knowledgePointId: number, answers: SavedAnswer[]): void {
  const records = getAllRecords()
  if (!records[knowledgePointId]) {
    records[knowledgePointId] = {
      knowledgePointId,
      answers: [],
      startTime: new Date().toISOString(),
      lastUpdated: new Date().toISOString()
    }
  }

  const record = records[knowledgePointId]
  answers.forEach(ans => {
    const existing = record.answers.find(a => a.questionId === ans.questionId)
    if (existing) {
      existing.answer = ans.answer
      existing.savedAt = new Date().toISOString()
    } else {
      record.answers.push({ ...ans })
    }
  })

  record.lastUpdated = new Date().toISOString()
  saveAllRecords(records)
}

/**
 * 获取某个知识点的所有已保存答案
 */
export function getSavedAnswers(knowledgePointId: number): SavedAnswer[] {
  const records = getAllRecords()
  return records[knowledgePointId]?.answers || []
}

/**
 * 获取某个知识点某道题的已保存答案
 */
export function getSavedAnswer(knowledgePointId: number, questionId: number): string {
  const answers = getSavedAnswers(knowledgePointId)
  const found = answers.find(a => a.questionId === questionId)
  return found?.answer || ''
}

/**
 * 清除某个知识点的所有答案
 */
export function clearAnswers(knowledgePointId: number): void {
  const records = getAllRecords()
  delete records[knowledgePointId]
  saveAllRecords(records)
}

/**
 * 清除所有答案
 */
export function clearAllAnswers(): void {
  localStorage.removeItem(STORAGE_KEY)
}

/**
 * 获取所有练习记录
 */
export function getAllPracticeRecords(): PracticeRecord[] {
  const records = getAllRecords()
  return Object.values(records).sort((a, b) =>
    new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
  )
}

export { MAX_LENGTH }
