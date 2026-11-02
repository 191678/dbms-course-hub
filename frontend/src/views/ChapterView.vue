<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElCard, ElTag, ElButton, ElBreadcrumb, ElBreadcrumbItem } from 'element-plus'
import { ArrowLeft, HelpFilled } from '@element-plus/icons-vue'
import { chapterApi, knowledgePointApi } from '@/api'
import type { Chapter, KnowledgePoint } from '@/types'
import { useRealtime } from '@/utils/useRealtime'

const route = useRoute()
const router = useRouter()
const chapter = ref<Chapter | null>(null)
const knowledgePoints = ref<KnowledgePoint[]>([])
const loading = ref(true)
const loaded = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    const id = parseInt(route.params.id as string)
    chapter.value = await chapterApi.getById(id)
    knowledgePoints.value = await knowledgePointApi.getAll({ chapter_id: id })
    loaded.value = true
  } catch {
    // 加载失败保留已有数据，避免页面空白
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

// 数据变化后 1 秒内自动同步，无需手动刷新
useRealtime(() => { if (!document.hidden) loadData() })

const getDifficultyTag = (difficulty: string) => {
  const tags: Record<string, { text: string; type: 'success' | 'warning' | 'danger' }> = {
    easy: { text: '简单', type: 'success' },
    medium: { text: '中等', type: 'warning' },
    hard: { text: '困难', type: 'danger' }
  }
  return tags[difficulty] || tags.medium
}

// 取详细介绍的前导内容作为卡片预览（去掉换行、截断）
const getIntroPreview = (kp: KnowledgePoint) => {
  const text = (kp.summary || kp.detail_content || '').replace(/\s*\n+\s*/g, ' ').trim()
  return text.length > 150 ? text.slice(0, 150) + '…' : text
}

const goToKnowledgePoint = (kpId: number) => {
  router.push(`/chapter/${route.params.id}/knowledge-point/${kpId}`)
}
</script>

<template>
  <div style="padding: 20px" v-loading="loading" element-loading-text="正在加载章节内容…">
    <ElBreadcrumb separator="/" style="margin-bottom: 20px">
      <ElBreadcrumbItem :to="{ path: '/' }">首页</ElBreadcrumbItem>
      <ElBreadcrumbItem>{{ chapter?.title }}</ElBreadcrumbItem>
    </ElBreadcrumb>

    <div style="display: flex; align-items: center; margin-bottom: 20px">
      <ElButton @click="router.back()" :icon="ArrowLeft">返回</ElButton>
      <h1 style="font-size: var(--font-title); margin-left: 20px; color: #303133">{{ chapter?.title }}</h1>
    </div>

    <ElCard style="margin-bottom: 20px">
      <p style="color: #606266; font-size: 16px; line-height: 1.8">{{ chapter?.description }}</p>
    </ElCard>

    <h2 style="font-size: var(--font-subtitle); color: #303133; margin-bottom: 16px">知识点列表</h2>
    
    <div class="kp-list">
      <ElCard 
        v-for="kp in knowledgePoints" 
        :key="kp.id" 
        class="kp-item"
      >
        <div class="kp-header">
          <ElTag :type="getDifficultyTag(kp.difficulty).type">
            {{ getDifficultyTag(kp.difficulty).text }}
          </ElTag>
          <span class="kp-id">#{{ kp.id }}</span>
        </div>
        <div class="kp-body">
          <p class="kp-title" @click="goToKnowledgePoint(kp.id)">{{ kp.content }}</p>
          <p v-if="kp.summary" class="kp-summary">{{ kp.summary }}</p>
          <p class="kp-preview">{{ getIntroPreview(kp) }}</p>
        </div>
        <div class="kp-actions">
          <ElButton type="primary" plain size="small" @click="goToKnowledgePoint(kp.id)">
            <HelpFilled style="font-size: var(--icon-size-sm); margin-right: 4px" />
            查看详细介绍
          </ElButton>
        </div>
      </ElCard>
    </div>

    <div v-if="loaded && knowledgePoints.length === 0" style="text-align: center; padding: 40px">
          <HelpFilled style="font-size: var(--icon-size-xxl); color: #c0c4cc; margin-bottom: 12px" />
          <p style="color: #909399">该章节暂无知识点</p>
        </div>
  </div>
</template>

<style scoped>
.kp-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.kp-item {
  transition: all 0.3s ease;
}

.kp-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.kp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.kp-id {
  font-size: 12px;
  color: #909399;
}

.kp-body {
  margin-bottom: 16px;
}

.kp-title {
  color: #303133;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.8;
  margin: 0 0 8px 0;
  cursor: pointer;
}

.kp-title:hover {
  color: #409EFF;
}

.kp-summary {
  color: #606266;
  font-size: 14px;
  line-height: 1.7;
  margin: 0 0 6px 0;
  padding-left: 10px;
  border-left: 3px solid #409EFF;
}

.kp-preview {
  color: #909399;
  font-size: 13px;
  line-height: 1.7;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.kp-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
