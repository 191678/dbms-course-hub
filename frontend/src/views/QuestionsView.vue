<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElCard, ElSelect, ElOption, ElButton, ElTag, ElBadge, ElDivider } from 'element-plus'
import { VideoPlay, Filter, FolderOpened, Collection, DataAnalysis, Reading } from '@element-plus/icons-vue'
import { chapterApi, knowledgePointApi, questionApi } from '@/api'
import type { Chapter, KnowledgePoint, Question } from '@/types'
import { useRealtime } from '@/utils/useRealtime'

const router = useRouter()
const chapters = ref<Chapter[]>([])
const knowledgePoints = ref<KnowledgePoint[]>([])
const questions = ref<Question[]>([])

const selectedChapter = ref<number | string>('')
const selectedKnowledgePoint = ref<number | string>('')
const selectedType = ref<string>('')

const questionTypes = ['单选', '多选', '判断', 'SQL编程', '填空']

const filteredKnowledgePoints = computed(() => {
  if (selectedChapter.value === '') return knowledgePoints.value
  return knowledgePoints.value.filter(kp => kp.chapter_id === selectedChapter.value)
})

const questionsByKnowledgePoint = computed(() => {
  const grouped: Record<number, { knowledge_point: KnowledgePoint | undefined; questions: Question[] }> = {}
  
  knowledgePoints.value.forEach(kp => {
    grouped[kp.id] = { knowledge_point: kp, questions: [] }
  })
  
  questions.value.forEach(q => {
    if (!grouped[q.knowledge_point_id]) {
      grouped[q.knowledge_point_id] = { knowledge_point: undefined, questions: [] }
    }
    grouped[q.knowledge_point_id].questions.push(q)
  })
  
  return Object.values(grouped).filter(g => g.questions.length > 0)
})

const groupedByChapter = computed(() => {
  const result: { chapter: Chapter; groups: typeof questionsByKnowledgePoint.value }[] = []
  for (const ch of chapters.value) {
    const groups = questionsByKnowledgePoint.value.filter(g => g.knowledge_point?.chapter_id === ch.id)
    if (groups.length > 0) {
      result.push({ chapter: ch, groups })
    }
  }
  return result
})

const totalQuestions = computed(() => questions.value.length)
const totalKnowledgePoints = computed(() => questionsByKnowledgePoint.value.length)
const perfectKPs = computed(() => questionsByKnowledgePoint.value.filter(g => g.questions.length === 10).length)

const loading = ref(true)

onMounted(async () => {
  loading.value = true
  try {
    chapters.value = await chapterApi.getAll()
    knowledgePoints.value = await knowledgePointApi.getAll()
    await loadQuestions()
  } catch {
    // 加载失败保留已有数据，避免页面空白
  } finally {
    loading.value = false
  }
})

// 题库数据变化后自动同步展示，无需手动刷新
useRealtime(() => {
  if (document.hidden) return
  loadQuestions()
})

const handleChapterChange = async () => {
  selectedKnowledgePoint.value = ''
  await loadQuestions()
}

const loadQuestions = async () => {
  const params: Record<string, number | string> = { limit: 2000 }
  if (selectedKnowledgePoint.value !== '') {
    params.knowledge_point_id = selectedKnowledgePoint.value
  }
  if (selectedType.value !== '') {
    params.type = selectedType.value
  }
  try {
    questions.value = await questionApi.getAll(params)
  } catch {
    // 刷新失败保留已有题目，避免页面空白
  }
}

const startPractice = () => {
  const params: Record<string, number | string> = {}
  if (selectedKnowledgePoint.value !== '') {
    params.knowledge_point_id = selectedKnowledgePoint.value
  }
  if (selectedType.value !== '') {
    params.type = selectedType.value
  }
  router.push({ path: '/practice', query: params })
}

const startPracticeByKnowledgePoint = (knowledgePointId: number) => {
  router.push({ path: '/practice', query: { knowledge_point_id: knowledgePointId } })
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

const getDifficultyTag = (difficulty: string) => {
  const types: Record<string, 'info' | 'warning' | 'success' | 'danger'> = {
    'easy': 'success',
    'medium': 'warning',
    'hard': 'danger'
  }
  const labels: Record<string, string> = {
    'easy': '简单',
    'medium': '中等',
    'hard': '困难'
  }
  return { type: types[difficulty] || 'info', label: labels[difficulty] || '未标注' }
}

const getChapterIcon = (chapterId: number) => {
  const icons: Record<number, string> = {
    1: '📖', 2: '🔗', 3: '💾', 4: '📐', 5: '🔄',
    6: '🛡️', 7: '🔒', 8: '📊', 9: '🏗️', 10: '🎯'
  }
  return icons[chapterId] || '📚'
}

const getTypeSummary = (questions: Question[]) => {
  const summary: Record<string, number> = {}
  questions.forEach(q => {
    summary[q.type] = (summary[q.type] || 0) + 1
  })
  return summary
}
</script>

<template>
  <div class="questions-page" v-loading="loading" element-loading-text="正在加载题库…">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">题库练习</h1>
        <p class="page-subtitle">按知识点分类练习，每个知识点包含10道精选题目</p>
      </div>
      <div class="header-stats">
        <div class="stat-card">
          <div class="stat-icon stat-icon--blue">
            <Collection />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ totalKnowledgePoints }}</span>
            <span class="stat-label">知识点</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon stat-icon--green">
            <DataAnalysis />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ totalQuestions }}</span>
            <span class="stat-label">题目总数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon stat-icon--orange">
            <Reading />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ perfectKPs }}/{{ totalKnowledgePoints }}</span>
            <span class="stat-label">达标知识点</span>
          </div>
        </div>
      </div>
    </div>

    <ElCard class="filter-card">
      <div class="filter-section">
        <div class="filter-item">
          <ElSelect 
            v-model="selectedChapter" 
            placeholder="选择章节" 
            style="width: 200px"
            @change="handleChapterChange"
          >
            <ElOption label="全部章节" :value="''" />
            <ElOption 
              v-for="chapter in chapters" 
              :key="chapter.id" 
              :label="chapter.title" 
              :value="chapter.id" 
            />
          </ElSelect>
        </div>

        <div class="filter-item">
          <ElSelect 
            v-model="selectedKnowledgePoint" 
            placeholder="选择知识点" 
            style="width: 280px"
          >
            <ElOption label="全部知识点" :value="''" />
            <ElOption 
              v-for="kp in filteredKnowledgePoints" 
              :key="kp.id" 
              :label="kp.content" 
              :value="kp.id" 
            />
          </ElSelect>
        </div>

        <div class="filter-item">
          <ElSelect 
            v-model="selectedType" 
            placeholder="题目类型" 
            style="width: 150px"
          >
            <ElOption label="全部类型" :value="''" />
            <ElOption 
              v-for="type in questionTypes" 
              :key="type" 
              :label="type" 
              :value="type" 
            />
          </ElSelect>
        </div>

        <div class="filter-actions">
          <ElButton type="primary" @click="loadQuestions">
            <Filter style="font-size: var(--icon-size-sm); margin-right: 4px" />
            筛选
          </ElButton>
          <ElButton type="success" @click="startPractice" :disabled="questions.length === 0">
            <VideoPlay style="font-size: var(--icon-size-sm); margin-right: 4px" />
            开始练习
          </ElButton>
        </div>
      </div>
    </ElCard>

    <div v-if="!loading && questions.length === 0" class="empty-state">
      <Filter class="empty-icon" />
      <p class="empty-text">暂无匹配的题目，请调整筛选条件</p>
    </div>

    <div v-else class="chapter-sections">
      <template v-for="chapterGroup in groupedByChapter" :key="chapterGroup.chapter.id">
        <div class="chapter-section">
          <div class="chapter-header">
            <span class="chapter-icon">{{ getChapterIcon(chapterGroup.chapter.id) }}</span>
            <span class="chapter-title">{{ chapterGroup.chapter.title }}</span>
            <ElTag type="info" size="small" class="chapter-count">
              {{ chapterGroup.groups.length }} 个知识点 · 
              {{ chapterGroup.groups.reduce((sum, g) => sum + g.questions.length, 0) }} 道题
            </ElTag>
          </div>

          <div class="knowledge-points-grid">
            <ElCard 
              v-for="group in chapterGroup.groups" 
              :key="group.knowledge_point?.id" 
              class="kp-card"
              shadow="hover"
            >
              <div class="kp-header">
                <div class="kp-title-row">
                  <FolderOpened class="kp-icon" />
                  <span class="kp-title">{{ group.knowledge_point?.content }}</span>
                </div>
                <div class="kp-tags">
                  <ElTag 
                    :type="getDifficultyTag(group.knowledge_point?.difficulty || 'medium').type" 
                    size="small"
                  >
                    {{ getDifficultyTag(group.knowledge_point?.difficulty || 'medium').label }}
                  </ElTag>
                  <ElBadge 
                    :value="group.questions.length" 
                    :max="99"
                    class="kp-count-badge"
                  />
                  <span class="kp-count-label">题</span>
                </div>
              </div>

              <div class="kp-type-summary">
                <span 
                  v-for="(count, type) in getTypeSummary(group.questions)" 
                  :key="type" 
                  class="type-chip"
                  :class="'type-chip--' + getTagType(type)"
                >
                  {{ type }} ×{{ count }}
                </span>
              </div>

              <ElDivider class="kp-divider" />

              <div class="kp-questions-list">
                <div 
                  v-for="q in group.questions.slice(0, 3)" 
                  :key="q.id" 
                  class="question-item"
                >
                  <ElTag :type="getTagType(q.type)" size="small" class="q-type-tag">
                    {{ q.type }}
                  </ElTag>
                  <span class="q-stem">{{ q.stem }}</span>
                </div>
                <div v-if="group.questions.length > 3" class="question-more">
                  还有 {{ group.questions.length - 3 }} 道题...
                </div>
              </div>

              <div class="kp-actions">
                <ElButton 
                  type="primary" 
                  size="small" 
                  @click="startPracticeByKnowledgePoint(group.knowledge_point?.id || 0)"
                >
                  <VideoPlay style="margin-right: 4px" />
                  练习全部 {{ group.questions.length }} 题
                </ElButton>
              </div>
            </ElCard>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.questions-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  gap: 24px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
  letter-spacing: 1px;
}

.page-subtitle {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.header-stats {
  display: flex;
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  min-width: 140px;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: #fff;
}

.stat-icon--blue { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-icon--green { background: linear-gradient(135deg, #11998e, #38ef7d); }
.stat-icon--orange { background: linear-gradient(135deg, #f093fb, #f5576c); }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
}

.filter-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.filter-section {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}

.filter-item {
  display: flex;
  align-items: center;
}

.filter-actions {
  margin-left: auto;
  display: flex;
  gap: 12px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.empty-text {
  color: #909399;
  font-size: 16px;
  margin: 0;
}

.chapter-sections {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.chapter-section {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

.chapter-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
}

.chapter-icon {
  font-size: 28px;
}

.chapter-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a2e;
}

.chapter-count {
  margin-left: auto;
  font-size: 13px;
}

.knowledge-points-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.kp-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.kp-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.kp-header {
  margin-bottom: 12px;
}

.kp-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.kp-icon {
  color: #409eff;
  font-size: 18px;
  flex-shrink: 0;
}

.kp-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.kp-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.kp-count-badge {
  margin-left: 4px;
}

.kp-count-label {
  font-size: 12px;
  color: #6b7280;
}

.kp-type-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.type-chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.type-chip--info { background: #ecf5ff; color: #409eff; }
.type-chip--warning { background: #fdf6ec; color: #e6a23c; }
.type-chip--success { background: #f0f9eb; color: #67c23a; }
.type-chip--danger { background: #fef0f0; color: #f56c6c; }

.kp-divider {
  margin: 12px 0;
}

.kp-questions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.question-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 10px;
  background: #f8f9fc;
  border-radius: 8px;
  font-size: 13px;
}

.q-type-tag {
  flex-shrink: 0;
  font-size: 11px;
}

.q-stem {
  color: #374151;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.question-more {
  text-align: center;
  font-size: 12px;
  color: #9ca3af;
  padding: 4px;
}

.kp-actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }
  
  .header-stats {
    width: 100%;
  }
  
  .stat-card {
    flex: 1;
    min-width: 0;
  }
  
  .knowledge-points-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-actions {
    margin-left: 0;
  }
}
</style>