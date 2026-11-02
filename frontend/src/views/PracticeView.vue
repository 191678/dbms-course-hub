<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElCard, ElButton, ElTag, ElProgress, ElAlert, ElMessage } from 'element-plus'
import { CircleCheck, CircleClose, Refresh, Clock, Document } from '@element-plus/icons-vue'
import { questionApi } from '@/api'
import type { Question } from '@/types'
import { saveAnswer, getSavedAnswers, clearAnswers } from '@/utils/answerStorage'
import { useRealtime } from '@/utils/useRealtime'

const route = useRoute()
const questions = ref<Question[]>([])
const currentIndex = ref(0)
const selectedAnswers = ref<string[]>([])
const timer = ref(0)
const isFinished = ref(false)
const showResult = ref(false)
let timerInterval: ReturnType<typeof setInterval> | null = null

const currentQuestion = computed(() => questions.value[currentIndex.value])
const progress = computed(() => ((currentIndex.value + 1) / questions.value.length) * 100)
const fillMaxLength = 2000

const normalizeAnswer = (answer: string, type: string) => {
  if (type === '判断') {
    const mapping: Record<string, string> = { 'A': '正确', 'B': '错误' }
    return mapping[answer] || answer
  }
  return answer
}

const score = computed(() => {
  if (questions.value.length === 0) return 0
  return Math.round((correctCount.value / questions.value.length) * 100)
})

// 填空题答案长度
const fillAnswerLength = computed(() => {
  const ans = selectedAnswers.value[currentIndex.value] || ''
  return ans.length
})

// 判断是否为文本输入型题目（填空、SQL编程）
const isTextInputType = (type: string) => type === '填空' || type === 'SQL编程'

// 判断答案是否匹配（填空题使用包含匹配）
const isAnswerMatch = (userAnswer: string, correctAnswer: string, type: string) => {
  if (!userAnswer) return false
  const normalizedUser = userAnswer.trim()
  const normalizedCorrect = correctAnswer.trim()
  if (type === '填空') {
    // 填空题：用户答案包含关键词即可
    return normalizedUser.length > 0 && normalizedCorrect.length > 0 &&
           (normalizedUser.includes(normalizedCorrect) || normalizedCorrect.includes(normalizedUser) ||
            normalizedUser.toLowerCase().includes(normalizedCorrect.toLowerCase()))
  }
  if (type === 'SQL编程') {
    // SQL编程：忽略大小写和空白差异
    return normalizedUser.replace(/\s+/g, ' ').toLowerCase() === normalizedCorrect.replace(/\s+/g, ' ').toLowerCase()
  }
  return normalizeAnswer(userAnswer, type) === correctAnswer
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const loading = ref(true)
const loaded = ref(false)

const loadQuestions = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (route.query.knowledge_point_id) {
      params.knowledge_point_id = parseInt(route.query.knowledge_point_id as string)
    }
    if (route.query.type) {
      params.type = route.query.type as string
    }
    questions.value = await questionApi.getAll(params)
    loaded.value = true
  } catch {
    // 加载失败保留已有题目，避免页面空白
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadQuestions()

  // 加载已保存的答案
  if (route.query.knowledge_point_id) {
    const kpId = parseInt(route.query.knowledge_point_id as string)
    const saved = getSavedAnswers(kpId)
    if (saved.length > 0) {
      questions.value.forEach((q, index) => {
        const found = saved.find(a => a.questionId === q.id)
        if (found) {
          selectedAnswers.value[index] = found.answer
        }
      })
      if (saved.length > 0) {
        ElMessage.info(`已恢复 ${saved.length} 道题的已保存答案`)
      }
    }
  }

  timerInterval = setInterval(() => {
    timer.value++
  }, 1000)
})

// 数据变化后自动同步；练习中途（已作答/已交卷）不刷新，避免打断答题
useRealtime(() => {
  if (document.hidden) return
  if (isFinished.value || selectedAnswers.value.some(a => a)) return
  loadQuestions()
})

// 监听答案变化，自动保存
watch(selectedAnswers, (newAnswers) => {
  if (route.query.knowledge_point_id && questions.value.length > 0) {
    const kpId = parseInt(route.query.knowledge_point_id as string)
    const q = questions.value[currentIndex.value]
    if (q && newAnswers[currentIndex.value]) {
      saveAnswer(kpId, q.id, newAnswers[currentIndex.value])
    }
  }
}, { deep: true })

const selectAnswer = (answer: string) => {
  if (showResult.value) return
  
  if (currentQuestion.value.type === '多选') {
    const current = selectedAnswers.value[currentIndex.value] || ''
    const index = current.split('').filter(i => i)
    const idx = index.indexOf(answer)
    if (idx > -1) {
      index.splice(idx, 1)
    } else {
      index.push(answer)
    }
    selectedAnswers.value[currentIndex.value] = index.sort().join('')
  } else {
    selectedAnswers.value[currentIndex.value] = answer
  }
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
  } else {
    finishPractice()
  }
}

const prevQuestion = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

const finishPractice = () => {
  isFinished.value = true
  showResult.value = true
  if (timerInterval) {
    clearInterval(timerInterval)
  }
}

const restartPractice = () => {
  currentIndex.value = 0
  selectedAnswers.value = []
  timer.value = 0
  isFinished.value = false
  showResult.value = false
  timerInterval = setInterval(() => {
    timer.value++
  }, 1000)
}

const isCorrect = computed(() => {
  const userAnswer = selectedAnswers.value[currentIndex.value]
  const correctAnswer = currentQuestion.value?.answer || ''
  const type = currentQuestion.value?.type || ''
  if (!userAnswer) return false
  return isAnswerMatch(userAnswer, correctAnswer, type)
})

// 计算所有题目的正确数（支持填空题）
const correctCount = computed(() => {
  let correct = 0
  questions.value.forEach((q, index) => {
    const userAnswer = selectedAnswers.value[index]
    if (userAnswer && isAnswerMatch(userAnswer, q.answer, q.type)) {
      correct++
    }
  })
  return correct
})

// 清除已保存的答案
const handleClearSaved = () => {
  if (route.query.knowledge_point_id) {
    const kpId = parseInt(route.query.knowledge_point_id as string)
    clearAnswers(kpId)
    selectedAnswers.value = []
    ElMessage.success('已清除所有保存的答案')
  }
}

const isOptionCorrect = (option: string, question: Question) => {
  if (question.type === '判断') {
    const mapping: Record<string, string> = { 'A': '正确', 'B': '错误' }
    return mapping[option] === question.answer
  }
  return question.answer.split('').includes(option)
}

const getTagType = (type: string) => {
  const types: Record<string, 'info' | 'warning' | 'success' | 'danger'> = {
    '单选': 'info',
    '多选': 'warning',
    '判断': 'success',
    'SQL编程': 'danger',
    '填空': 'info'
  }
  return types[type] || 'info'
}

const getOptions = (question: Question) => {
  if (question.type === '判断') {
    return ['A.正确', 'B.错误']
  }
  if (!question.options || !Array.isArray(question.options)) return []
  return question.options.map((opt, idx) => {
    const labels = ['A', 'B', 'C', 'D', 'E', 'F']
    return `${labels[idx]}.${opt}`
  })
}
</script>

<template>
  <div style="padding: 20px" v-loading="loading" element-loading-text="正在加载题目…">
    <div v-if="loaded && !isFinished && questions.length === 0" style="text-align: center; padding: 60px 0">
      <Document style="font-size: 48px; color: #c0c4cc; margin-bottom: 16px" />
      <p style="color: #909399">暂无匹配的题目或加载失败，请返回题库重新选择</p>
    </div>
    <div v-else-if="isFinished" class="result-container">
      <ElCard class="result-card">
        <div class="result-header">
          <CircleCheck v-if="score >= 60" style="font-size: var(--icon-size-xxl); color: #67c23a" />
          <CircleClose v-else style="font-size: var(--icon-size-xxl); color: #f56c6c" />
          <h1>{{ score >= 60 ? '练习完成！' : '继续加油！' }}</h1>
          <p class="score">得分：{{ score }}分</p>
        </div>
        
        <div class="stats">
          <div class="stat-item">
            <span class="stat-label">用时</span>
            <span class="stat-value">{{ formatTime(timer) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">题目总数</span>
            <span class="stat-value">{{ questions.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">正确率</span>
            <span class="stat-value">{{ score }}%</span>
          </div>
        </div>
        
        <div class="result-actions">
          <ElButton type="primary" @click="restartPractice">
            <Refresh style="font-size: var(--icon-size-sm); margin-right: 4px" />
            重新练习
          </ElButton>
          <ElButton @click="handleClearSaved">
            <Refresh style="font-size: var(--icon-size-sm); margin-right: 4px" />
            清除已保存答案
          </ElButton>
        </div>
      </ElCard>
      
      <ElCard style="margin-top: 20px">
        <h3>答案解析</h3>
        <div v-for="(q, index) in questions" :key="q.id" class="answer-review">
          <div class="review-header">
            <span class="question-num">第{{ index + 1 }}题 (ID: {{ q.id }})</span>
            <ElTag :type="getTagType(q.type)">{{ q.type }}</ElTag>
            <CircleCheck v-if="isAnswerMatch(selectedAnswers[index] || '', q.answer, q.type)" style="font-size: var(--icon-size-md); color: #67c23a" />
            <CircleClose v-else style="font-size: var(--icon-size-md); color: #f56c6c" />
          </div>
          <p class="question-stem">{{ q.stem }}</p>
          <div class="answer-info">
            <span>你的答案：{{ selectedAnswers[index] ? (isTextInputType(q.type) ? selectedAnswers[index] : (q.type === '判断' ? (selectedAnswers[index] === 'A' ? '正确' : '错误') : selectedAnswers[index])) : '未作答' }}</span>
            <span>正确答案：{{ q.answer }}</span>
          </div>
          <p class="explanation" v-if="q.analysis">解析：{{ q.analysis }}</p>
        </div>
      </ElCard>
    </div>

    <div v-else>
      <div class="practice-header">
          <div class="timer">
            <Clock style="font-size: var(--icon-size-lg)" />
            <span>{{ formatTime(timer) }}</span>
          </div>
        <ElProgress :percentage="progress" :show-text="false" style="width: 300px" />
        <span class="progress-text">{{ currentIndex + 1 }}/{{ questions.length }}</span>
      </div>

      <ElCard v-if="currentQuestion" class="question-card">
        <div class="question-header">
          <span class="question-num">第{{ currentIndex + 1 }}题 (ID: {{ currentQuestion.id }})</span>
          <ElTag :type="getTagType(currentQuestion.type)">{{ currentQuestion.type }}</ElTag>
          <ElTag v-if="selectedAnswers[currentIndex]" size="small" type="success">
            <Document style="font-size: var(--icon-size-xs); margin-right: 4px" />已保存
          </ElTag>
        </div>
        
        <p class="question-stem">{{ currentQuestion.stem }}</p>
        
        <div v-if="!isTextInputType(currentQuestion.type)" class="options-list">
          <div
            v-for="(opt, idx) in getOptions(currentQuestion)"
            :key="idx"
            class="option-item"
            :class="{
              selected: (selectedAnswers[currentIndex] || '').split('').includes(opt.split('.')[0]),
              correct: showResult && isOptionCorrect(opt.split('.')[0], currentQuestion),
              wrong: showResult && (selectedAnswers[currentIndex] || '').split('').includes(opt.split('.')[0]) && !isOptionCorrect(opt.split('.')[0], currentQuestion)
            }"
            @click="selectAnswer(opt.split('.')[0])"
          >
            <span class="option-label">{{ opt.split('.')[0] }}</span>
            <span class="option-text">{{ opt.split('.').slice(1).join('.') }}</span>
          </div>
        </div>

        <div v-else class="text-input-editor">
          <textarea
            v-model="selectedAnswers[currentIndex]"
            :placeholder="currentQuestion.type === '填空' ? '请输入答案，支持多行文本输入...' : '请输入SQL语句...'"
            class="answer-textarea"
            :maxlength="fillMaxLength"
            rows="6"
          ></textarea>
          <div class="textarea-footer">
            <span class="char-count" :class="{ 'over-limit': fillAnswerLength > fillMaxLength * 0.9 }">
              {{ fillAnswerLength }} / {{ fillMaxLength }} 字符
            </span>
            <ElTag v-if="currentQuestion.type === '填空'" size="small" type="info">
              支持多行文本，可使用换行、退格等编辑功能
            </ElTag>
          </div>
        </div>
        
        <div v-if="showResult" class="result-alert">
          <ElAlert 
            :type="isCorrect ? 'success' : 'error'" 
            :message="isCorrect ? '回答正确！' : `回答错误，正确答案：${currentQuestion.answer}`"
            show-icon
          />
          <p v-if="currentQuestion.analysis" class="explanation">解析：{{ currentQuestion.analysis }}</p>
        </div>
        
        <div class="question-actions">
          <ElButton @click="prevQuestion" :disabled="currentIndex === 0">上一题</ElButton>
          <ElButton v-if="currentIndex < questions.length - 1" type="primary" @click="nextQuestion">下一题</ElButton>
          <ElButton v-else type="success" @click="finishPractice">提交答案</ElButton>
        </div>
      </ElCard>
    </div>
  </div>
</template>

<style scoped>
.practice-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.timer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  color: #606266;
}

.progress-text {
  font-size: 14px;
  color: #909399;
}

.question-card {
  max-width: 800px;
  margin: 0 auto;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.question-num {
  font-size: 14px;
  color: #909399;
}

.question-stem {
  font-size: 16px;
  color: #303133;
  line-height: 1.8;
  margin-bottom: 20px;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.option-item:hover {
  border-color: #409EFF;
}

.option-item.selected {
  background-color: #ecf5ff;
  border-color: #409EFF;
}

.option-item.correct {
  background-color: #f0f9eb;
  border-color: #67c23a;
}

.option-item.wrong {
  background-color: #fef0f0;
  border-color: #f56c6c;
}

.option-label {
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  background-color: #f5f7fa;
  border-radius: 50%;
  font-size: 14px;
  font-weight: bold;
}

.selected .option-label {
  background-color: #409EFF;
  color: white;
}

.correct .option-label {
  background-color: #67c23a;
  color: white;
}

.wrong .option-label {
  background-color: #f56c6c;
  color: white;
}

.option-text {
  flex: 1;
  font-size: 15px;
  color: #303133;
}

.text-input-editor {
  margin-bottom: 16px;
}

.answer-textarea {
  width: 100%;
  min-height: 150px;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.answer-textarea:focus {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.textarea-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.char-count {
  font-size: 12px;
  color: #909399;
}

.char-count.over-limit {
  color: #f56c6c;
  font-weight: bold;
}

.result-alert {
  margin-bottom: 16px;
}

.explanation {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin-top: 12px;
}

.question-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.result-container {
  max-width: 600px;
  margin: 0 auto;
}

.result-card {
  text-align: center;
}

.result-header {
  margin-bottom: 32px;
}

.result-header h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 8px;
}

.score {
  font-size: 48px;
  font-weight: bold;
  color: #409EFF;
}

.stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 32px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.result-actions {
  display: flex;
  justify-content: center;
}

.answer-review {
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
}

.answer-review:last-child {
  border-bottom: none;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.answer-info {
  display: flex;
  gap: 20px;
  margin-bottom: 8px;
  font-size: 14px;
}

.answer-info span:first-child {
  color: #909399;
}

.answer-info span:last-child {
  color: #67c23a;
}
</style>
