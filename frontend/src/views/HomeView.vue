<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElCard, ElTag, ElButton, ElEmpty } from 'element-plus'
import { ArrowRight, Star, Reading, HelpFilled, Lightning, Trophy } from '@element-plus/icons-vue'
import { chapterApi } from '@/api'
import type { Chapter } from '@/types'
import { useRealtime } from '@/utils/useRealtime'

const router = useRouter()
const chapters = ref<Chapter[]>([])
const loading = ref(true)
const loaded = ref(false)
const expandedChapters = ref<number[]>([])
const selectedCategory = ref<string>('')

const categoryConfig: Record<string, { label: string; icon: any; color: string }> = {
  '基础概念': { label: '基础概念', icon: Reading, color: '#409EFF' },
  '核心理论': { label: '核心理论', icon: HelpFilled, color: '#67c23a' },
  '操作技能': { label: '操作技能', icon: Lightning, color: '#e6a23c' },
  '高级技术': { label: '高级技术', icon: Trophy, color: '#f56c6c' }
}

const allCategories = ['基础概念', '核心理论', '操作技能', '高级技术']

const getCategoryStyle = (category: string) => {
  return categoryConfig[category] || categoryConfig['基础概念']
}

const getDifficultyTag = (difficulty: string) => {
  const tags: Record<string, { text: string; type: 'success' | 'warning' | 'danger' }> = {
    easy: { text: '简单', type: 'success' },
    medium: { text: '中等', type: 'warning' },
    hard: { text: '困难', type: 'danger' }
  }
  return tags[difficulty] || tags.medium
}

const getKPStats = (chapter: Chapter) => {
  const kps = chapter.knowledge_points || []
  const count = kps.length
  const totalQuestions = kps.reduce((sum, kp) => sum + (kp.questions?.length || 0), 0)
  return { count, totalQuestions }
}

const handleChapterExpand = (chapterId: number) => {
  const index = expandedChapters.value.indexOf(chapterId)
  if (index > -1) {
    expandedChapters.value.splice(index, 1)
  } else {
    expandedChapters.value.push(chapterId)
  }
}

const goToChapter = (chapterId: number) => {
  router.push(`/chapter/${chapterId}`)
}

const goToKnowledgePoint = (chapterId: number, kpId: number) => {
  router.push(`/chapter/${chapterId}/knowledge-point/${kpId}`)
}

const loadChapters = async () => {
  loading.value = true
  try {
    chapters.value = await chapterApi.getAll()
    loaded.value = true
  } catch {
    // 加载失败保留已有数据，避免页面空白
  } finally {
    loading.value = false
  }
}

onMounted(loadChapters)

// 数据变化后 1 秒内自动同步，无需手动刷新
useRealtime(() => { if (!document.hidden) loadChapters() })
</script>

<template>
  <div style="padding: 20px" v-loading="loading" element-loading-text="正在加载课程内容…">
    <div style="margin-bottom: 24px">
      <h1 style="font-size: var(--font-title); color: #303133; margin-bottom: 8px">数据库系统课程学习平台</h1>
      <p style="color: #909399">系统化学习数据库系统知识，配合智能助教答疑解惑</p>
    </div>

    <div class="category-filter" style="margin-bottom: 24px">
      <ElTag 
        :type="selectedCategory === '' ? 'primary' : 'info'" 
        @click="selectedCategory = ''"
        class="category-tag"
      >
        全部
      </ElTag>
      <ElTag
        v-for="category in allCategories"
        :key="category"
        :type="selectedCategory === category ? 'primary' : 'info'"
        :style="{ borderColor: getCategoryStyle(category).color, color: getCategoryStyle(category).color }"
        @click="selectedCategory = category"
        class="category-tag"
      >
        <component :is="getCategoryStyle(category).icon" style="font-size: var(--icon-size-md); margin-right: 6px" />
        {{ getCategoryStyle(category).label }}
      </ElTag>
    </div>

    <ElEmpty v-if="loaded && !chapters.length" description="课程内容加载失败或暂无数据，请稍后重试" />
    <div v-for="chapter in chapters" :key="chapter.id" class="chapter-section">
      <ElCard 
        class="chapter-card"
        :body-style="{ padding: '0' }"
      >
        <div class="chapter-header" @click="handleChapterExpand(chapter.id)">
          <div class="chapter-info">
            <div class="chapter-title">
              <span class="chapter-number">{{ chapter.order_index }}</span>
              <span>{{ chapter.title }}</span>
            </div>
            <p class="chapter-description">{{ chapter.description }}</p>
            <div class="chapter-stats">
              <span class="stat-item">
                <Reading style="font-size: var(--icon-size-sm); margin-right: 6px" />
                {{ getKPStats(chapter).count }} 个知识点
              </span>
              <span class="stat-item">
                <Star style="font-size: var(--icon-size-sm); margin-right: 6px" />
                {{ getKPStats(chapter).totalQuestions }} 道练习题
              </span>
            </div>
          </div>
          <div class="chapter-actions">
            <ElButton type="primary" size="small" @click.stop="goToChapter(chapter.id)">
              <span>进入学习</span>
              <ArrowRight style="font-size: var(--icon-size-sm); margin-left: 6px" />
            </ElButton>
            <span 
              class="expand-icon"
              :class="{ expanded: expandedChapters.includes(chapter.id) }"
            >
              ▼
            </span>
          </div>
        </div>

        <div v-if="expandedChapters.includes(chapter.id)" class="chapter-content">
          <div v-if="chapter.knowledge_points && chapter.knowledge_points.length > 0" class="knowledge-points-container">
            <div v-for="category in allCategories" :key="category">
              <div 
                v-if="chapter.knowledge_points.some(kp => kp.category === category)" 
                class="category-section"
              >
                <div class="category-header">
                  <component 
                    :is="getCategoryStyle(category).icon" 
                    :style="{ color: getCategoryStyle(category).color, fontSize: 'var(--icon-size-lg)' }"
                  />
                  <span :style="{ color: getCategoryStyle(category).color }">
                    {{ getCategoryStyle(category).label }}
                  </span>
                  <span class="category-count">
                    {{ chapter.knowledge_points.filter(kp => kp.category === category).length }}
                  </span>
                </div>
                
                <div class="kp-list">
                  <div 
                    v-for="kp in chapter.knowledge_points.filter(kp => kp.category === category)" 
                    :key="kp.id"
                    class="kp-item"
                    @click="goToKnowledgePoint(chapter.id, kp.id)"
                  >
                    <div class="kp-main">
                      <span class="kp-content">{{ kp.content }}</span>
                      <ElTag :type="getDifficultyTag(kp.difficulty).type" size="small">
                        {{ getDifficultyTag(kp.difficulty).text }}
                      </ElTag>
                    </div>
                    <div v-if="kp.summary" class="kp-summary">
                      {{ kp.summary }}
                    </div>
                    <div class="kp-footer">
                      <span class="question-count">{{ kp.questions?.length || 0 }} 道练习题</span>
                      <span class="arrow-icon">→</span>
                    </div>
                    
                    <div v-if="kp.children && kp.children.length > 0" class="kp-children">
                      <div 
                        v-for="child in kp.children" 
                        :key="child.id"
                        class="kp-child"
                        @click.stop="goToKnowledgePoint(chapter.id, child.id)"
                      >
                        <span class="child-dot">•</span>
                        <span class="child-content">{{ child.content }}</span>
                        <ElTag :type="getDifficultyTag(child.difficulty).type" size="small" class="child-tag">
                          {{ getDifficultyTag(child.difficulty).text }}
                        </ElTag>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else style="padding: 20px; text-align: center; color: #909399">
            暂无知识点数据
          </div>
        </div>
      </ElCard>
    </div>

    <div v-if="chapters.length === 0" style="text-align: center; padding: 60px">
          <Star style="font-size: var(--icon-size-xxl); color: #c0c4cc; margin-bottom: 16px" />
          <p style="color: #909399">暂无章节数据，请先添加课程章节</p>
        </div>
  </div>
</template>

<style scoped>
.chapter-section {
  margin-bottom: 16px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chapter-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.chapter-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  cursor: pointer;
}

.chapter-header:hover {
  background-color: #fafafa;
}

.chapter-info {
  flex: 1;
}

.chapter-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.chapter-number {
  background-color: #409EFF;
  color: #fff;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  margin-right: 12px;
  font-weight: normal;
}

.chapter-description {
  font-size: 14px;
  color: #909399;
  line-height: 1.6;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.chapter-stats {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #606266;
}

.stat-item {
  display: flex;
  align-items: center;
}

.chapter-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.expand-icon {
  font-size: 12px;
  color: #c0c4cc;
  transition: transform 0.3s ease;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.chapter-content {
  border-top: 1px solid #ebeef5;
  padding: 20px;
}

.category-section {
  margin-bottom: 20px;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.category-count {
  font-size: 12px;
  background-color: #ebeef5;
  color: #606266;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: normal;
}

.kp-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.kp-item {
  background-color: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.kp-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}

.kp-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.kp-content {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.kp-summary {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 8px;
  padding-left: 4px;
  border-left: 3px solid #ebeef5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.kp-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-count {
  font-size: 12px;
  color: #909399;
}

.arrow-icon {
  font-size: 14px;
  color: #c0c4cc;
}

.kp-children {
  margin-top: 12px;
  padding-left: 16px;
  border-left: 2px solid #ebeef5;
}

.kp-child {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.kp-child:hover {
  background-color: #f5f7fa;
  padding-left: 8px;
  margin-left: -8px;
  border-radius: 4px;
}

.child-dot {
  color: #c0c4cc;
}

.child-content {
  font-size: 13px;
  color: #606266;
  flex: 1;
}

.child-tag {
  font-size: 10px;
}

.category-filter {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.category-tag {
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-tag:hover {
  transform: translateY(-2px);
}
</style>
