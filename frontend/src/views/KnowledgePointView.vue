<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElCard, ElTag, ElButton, ElTable, ElTableColumn, ElImage, ElCollapse, ElCollapseItem } from 'element-plus'
import {
  ArrowLeft, Reading, HelpFilled, Lightning, Trophy, Document, Star,
  MagicStick, Notebook, Operation, Warning, QuestionFilled, Picture
} from '@element-plus/icons-vue'
import { chapterApi, agentApi } from '@/api'
import type { KnowledgePoint, Chapter } from '@/types'
import { useRealtime } from '@/utils/useRealtime'

const route = useRoute()
const router = useRouter()
const chapter = ref<Chapter | null>(null)
const knowledgePoint = ref<KnowledgePoint | null>(null)
const imgLoadError = ref(false)

// 学习内容纯净化配置：这些章节的学习页面隐藏所有题库练习相关内容
const HIDE_QUIZ_CHAPTER_IDS: number[] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
const hideQuiz = ref(false)

const categoryConfig: Record<string, { label: string; icon: any; color: string }> = {
  '基础概念': { label: '基础概念', icon: Reading, color: '#409EFF' },
  '核心理论': { label: '核心理论', icon: HelpFilled, color: '#67c23a' },
  '操作技能': { label: '操作技能', icon: Lightning, color: '#e6a23c' },
  '高级技术': { label: '高级技术', icon: Trophy, color: '#f56c6c' }
}

const getCategoryStyle = (category: string) => {
  return categoryConfig[category] || categoryConfig['基础概念']
}

const getDifficultyTagType = (difficulty: string): 'success' | 'warning' | 'danger' => {
  const tags: Record<string, 'success' | 'warning' | 'danger'> = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return tags[difficulty] || 'warning'
}

const getDifficultyTagText = (difficulty: string): string => {
  const tags: Record<string, string> = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return tags[difficulty] || '中等'
}

const goBack = () => {
  router.push(`/chapter/${route.params.chapterId}`)
}

const askAssistant = async () => {
  if (!knowledgePoint.value) return
  const question = `请解释一下"${knowledgePoint.value.content}"这个知识点`
  try {
    await agentApi.chat({
      student_question: question,
      context: {
        chapter_id: Number(route.params.chapterId),
        knowledge_point_id: knowledgePoint.value.id
      }
    })
    router.push('/agent')
  } catch (error) {
    console.error('Failed to ask assistant:', error)
  }
}

const loading = ref(true)
const loaded = ref(false)

const loadDetail = async () => {
  const chapterId = Number(route.params.chapterId)
  const kpId = Number(route.params.kpId)
  hideQuiz.value = HIDE_QUIZ_CHAPTER_IDS.includes(chapterId)
  loading.value = true
  try {
    chapter.value = await chapterApi.getById(chapterId)
    if (chapter.value && chapter.value.knowledge_points) {
      const findKP = (kps: KnowledgePoint[]): KnowledgePoint | undefined => {
        for (const kp of kps) {
          if (kp.id === kpId) return kp
          if (kp.children) {
            const found = findKP(kp.children)
            if (found) return found
          }
        }
        return undefined
      }
      const foundKP = findKP(chapter.value.knowledge_points)
      knowledgePoint.value = foundKP || null
    }
    loaded.value = true
  } catch (error) {
    console.error('Failed to load knowledge point:', error)
    // 加载失败保留已有内容，避免页面空白
  } finally {
    loading.value = false
  }
}

onMounted(loadDetail)

// 数据变化后 1 秒内自动同步，无需手动刷新
useRealtime(() => { if (!document.hidden) loadDetail() })
</script>

<template>
  <div class="kp-page" v-loading="loading" element-loading-text="正在加载知识点内容…">
    <div class="page-header">
      <ElButton type="text" @click="goBack" class="back-btn">
        <ArrowLeft style="font-size: 16px; margin-right: 4px" />
        返回章节
      </ElButton>

      <h1 class="page-title">{{ knowledgePoint?.content || '知识点详情' }}</h1>

      <div class="meta-bar">
        <span class="chapter-name">{{ chapter?.title }}</span>
        <span v-if="knowledgePoint?.category" class="category-tag" :style="{ color: getCategoryStyle(knowledgePoint.category).color, borderColor: getCategoryStyle(knowledgePoint.category).color }">
          <component :is="getCategoryStyle(knowledgePoint.category).icon" style="font-size: 12px; margin-right: 4px" />
          {{ getCategoryStyle(knowledgePoint.category).label }}
        </span>
        <ElTag :type="getDifficultyTagType(knowledgePoint?.difficulty || 'medium')" size="small" effect="dark">
          {{ getDifficultyTagText(knowledgePoint?.difficulty || 'medium') }}
        </ElTag>
      </div>
    </div>

    <div v-if="knowledgePoint" class="content-container">
      <!-- 原理说明 + 配图 -->
      <ElCard class="section-card intro-section" shadow="never">
        <div class="section-grid">
          <div class="text-area">
            <div class="section-title">
              <Document style="font-size: 20px; color: #409EFF" />
              <span>原理说明</span>
            </div>
            <p v-if="knowledgePoint.detail_content" class="detail-text">{{ knowledgePoint.detail_content }}</p>
            <p v-else class="empty-text">暂无详细内容，点击下方按钮询问智能助教</p>

            <ElButton type="primary" @click="askAssistant" class="ask-btn">
              <MagicStick style="font-size: 14px; margin-right: 6px" />
              询问智能助教
            </ElButton>
          </div>

          <div class="image-area">
            <div v-if="knowledgePoint.image_url && !imgLoadError" class="kp-image-wrapper">
              <ElImage
                :src="knowledgePoint.image_url"
                fit="cover"
                class="kp-image"
                :preview-src-list="knowledgePoint.image_url ? [knowledgePoint.image_url] : []"
                @error="imgLoadError = true"
              >
                <template #error>
                  <div class="image-placeholder">
                    <Picture style="font-size: 36px; color: #c0c4cc" />
                    <span>配图加载失败</span>
                  </div>
                </template>
              </ElImage>
            </div>
            <div v-else class="image-placeholder">
              <Picture style="font-size: 36px; color: #c0c4cc" />
              <span>暂无配图</span>
            </div>
          </div>
        </div>
      </ElCard>

      <!-- 重点内容 -->
      <ElCard v-if="knowledgePoint.key_points && knowledgePoint.key_points.length > 0" class="section-card" shadow="never">
        <div class="section-title">
          <Star style="font-size: 20px; color: #e6a23c" />
          <span>重点内容</span>
        </div>
        <ul class="key-points-list">
          <li v-for="(point, index) in knowledgePoint.key_points" :key="index">
            <span class="point-number">{{ index + 1 }}</span>
            <span class="point-text">{{ point }}</span>
          </li>
        </ul>
      </ElCard>

      <!-- 分步操作指引 -->
      <ElCard v-if="knowledgePoint.learning_steps && knowledgePoint.learning_steps.length > 0" class="section-card" shadow="never">
        <div class="section-title">
          <Operation style="font-size: 20px; color: #67c23a" />
          <span>分步操作指引</span>
        </div>
        <ol class="steps-list">
          <li v-for="(step, index) in knowledgePoint.learning_steps" :key="index">
            <span class="step-number">{{ index + 1 }}</span>
            <span class="step-text">{{ step }}</span>
          </li>
        </ol>
      </ElCard>

      <!-- 实操注意事项 -->
      <ElCard v-if="knowledgePoint.tips && knowledgePoint.tips.length > 0" class="section-card tips-card" shadow="never">
        <div class="section-title">
          <Warning style="font-size: 20px; color: #e6a23c" />
          <span>实操注意事项</span>
        </div>
        <ul class="tips-list">
          <li v-for="(tip, index) in knowledgePoint.tips" :key="index">
            <span class="tip-dot">⚠</span>
            <span class="tip-text">{{ tip }}</span>
          </li>
        </ul>
      </ElCard>

      <!-- 常见问题 -->
      <ElCard v-if="knowledgePoint.faq && knowledgePoint.faq.length > 0" class="section-card" shadow="never">
        <div class="section-title">
          <QuestionFilled style="font-size: 20px; color: #909399" />
          <span>常见问题</span>
        </div>
        <ElCollapse class="faq-collapse">
          <ElCollapseItem
            v-for="(item, index) in knowledgePoint.faq"
            :key="index"
            :title="item.question"
            :name="index"
          >
            <p class="faq-answer">{{ item.answer }}</p>
          </ElCollapseItem>
        </ElCollapse>
      </ElCard>

      <!-- 相关练习题（内容纯净化章节不展示任何题库内容） -->
      <ElCard v-if="!hideQuiz && knowledgePoint.questions && knowledgePoint.questions.length > 0" class="section-card" shadow="never">
        <div class="section-title">
          <Notebook style="font-size: 20px; color: #67c23a" />
          <span>相关练习题</span>
          <span class="question-count">{{ knowledgePoint.questions.length }} 道</span>
        </div>
        <ElTable :data="knowledgePoint.questions" border stripe>
          <ElTableColumn prop="id" label="编号" width="70" align="center" />
          <ElTableColumn prop="type" label="类型" width="90" align="center" />
          <ElTableColumn prop="stem" label="题目" min-width="300" show-overflow-tooltip />
          <ElTableColumn prop="answer" label="答案" width="100" align="center" />
        </ElTable>
      </ElCard>
    </div>

    <div v-else-if="loaded" class="empty-state">
      <Document style="font-size: 48px; color: #c0c4cc; margin-bottom: 16px" />
      <p style="color: #909399">知识点不存在或已删除</p>
      <ElButton type="primary" @click="goBack" style="margin-top: 16px">返回章节</ElButton>
    </div>
  </div>
</template>

<style scoped>
.kp-page {
  padding: 20px;
  max-width: 1100px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.back-btn {
  margin-bottom: 12px;
  padding-left: 0;
}

.page-title {
  font-size: 26px;
  color: #303133;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.meta-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.chapter-name {
  color: #909399;
  font-size: 14px;
}

.category-tag {
  display: inline-flex;
  align-items: center;
  padding: 3px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  border: 1px solid;
}

.content-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-card {
  border-radius: 12px;
  border: 1px solid #ebeef5;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 17px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

/* 原理说明 + 配图 图文并排 */
.intro-section .section-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 24px;
  align-items: start;
}

.text-area {
  min-width: 0;
}

.detail-text {
  font-size: 15px;
  line-height: 1.9;
  color: #303133;
  text-align: justify;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0 0 16px 0;
}

.empty-text {
  color: #909399;
  font-size: 14px;
}

.ask-btn {
  width: 100%;
}

.image-area {
  position: sticky;
  top: 16px;
}

.kp-image-wrapper {
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  background: #f5f7fa;
}

.kp-image {
  width: 100%;
  display: block;
  aspect-ratio: 16 / 9;
}

.image-placeholder {
  aspect-ratio: 16 / 9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 10px;
  color: #c0c4cc;
  font-size: 14px;
  gap: 8px;
}

/* 重点内容 */
.key-points-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px;
}

.key-points-list li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  background: #fdf6ec;
  border-radius: 8px;
  border-left: 3px solid #e6a23c;
}

.point-number {
  background-color: #e6a23c;
  color: #fff;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
  font-weight: 600;
}

.point-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

/* 分步操作指引 */
.steps-list {
  list-style: none;
  padding: 0;
  margin: 0;
  counter-reset: step;
}

.steps-list li {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px dashed #ebeef5;
}

.steps-list li:last-child {
  border-bottom: none;
}

.step-number {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  color: #fff;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
  font-weight: 600;
}

.step-text {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
}

/* 实操注意事项 */
.tips-card {
  background: linear-gradient(to right, #fff8e6, #fffdf5);
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 0;
}

.tip-dot {
  color: #e6a23c;
  font-size: 16px;
  flex-shrink: 0;
  line-height: 1.6;
}

.tip-text {
  font-size: 14px;
  line-height: 1.7;
  color: #856404;
}

/* 常见问题 */
.faq-collapse {
  border: none;
}

.faq-collapse :deep(.el-collapse-item__header) {
  font-weight: 500;
  color: #303133;
  padding-left: 0;
  border-bottom: 1px solid #ebeef5;
}

.faq-collapse :deep(.el-collapse-item__content) {
  padding-left: 4px;
}

.faq-answer {
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
  margin: 0;
}

/* 练习题 */
.question-count {
  font-size: 12px;
  background-color: #67c23a;
  color: #fff;
  padding: 2px 10px;
  border-radius: 10px;
  margin-left: 8px;
  font-weight: normal;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .intro-section .section-grid {
    grid-template-columns: 1fr;
  }

  .image-area {
    position: static;
  }
}

@media (max-width: 768px) {
  .kp-page {
    padding: 12px;
  }

  .page-title {
    font-size: 20px;
  }

  .meta-bar {
    gap: 8px;
  }

  .section-title {
    font-size: 16px;
  }

  .detail-text {
    font-size: 14px;
  }

  .key-points-list {
    grid-template-columns: 1fr;
  }

  .ask-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 18px;
  }

  .category-tag {
    font-size: 12px;
    padding: 2px 8px;
  }
}
</style>
