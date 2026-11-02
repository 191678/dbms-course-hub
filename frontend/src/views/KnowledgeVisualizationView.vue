<template>
  <div class="visualization-container">
    <div class="header">
      <h1>📊 知识点可视化</h1>
      <p class="subtitle">基于王珊《数据库系统概述》教材的智能知识可视化展示</p>
    </div>

    <div class="search-section">
      <div class="search-box">
        <input
          v-model="searchTopic"
          type="text"
          placeholder="输入数据库知识点，如：事务ACID特性、B+树索引、ER图..."
          @keyup.enter="handleSearch"
        />
        <button @click="handleSearch" class="search-btn">
          <span class="icon">🔍</span>
          搜索并可视化
        </button>
      </div>
      <div class="quick-tags">
        <span class="tag-label">快速选择：</span>
        <button
          v-for="tag in quickTags"
          :key="tag"
          class="quick-tag"
          @click="selectTag(tag)"
        >
          {{ tag }}
        </button>
      </div>
    </div>

    <div class="learning-progress-bar">
      <div class="progress-item">
        <span class="progress-icon">⏱️</span>
        <span class="progress-label">本次学习时长：</span>
        <span class="progress-value">{{ formatDuration(accumulatedDuration) }}</span>
      </div>
      <div class="progress-item">
        <span class="progress-icon">👁️</span>
        <span class="progress-label">已访问模块：</span>
        <span class="progress-value">{{ Object.keys(MODULE_TYPES).filter(k => 
          ['knowledge_visualization','knowledge_graph','theory_content','key_points','diagram','search','node_click'].includes(k)
        ).length }} 个</span>
      </div>
      <div class="progress-item">
        <span class="progress-icon">💡</span>
        <span class="progress-label">交互次数：</span>
        <span class="progress-value">{{ interactionCount }}</span>
      </div>
      <div class="progress-hint">学习进度已自动记录</div>
    </div>

    <div v-if="isLoading" class="loading">
      <div class="loading-spinner"></div>
      <p>正在检索教材内容并生成可视化图表...</p>
    </div>

    <div v-else-if="result && result.success" class="result-section">
      <div class="result-header">
        <div class="info-card">
          <div class="info-item">
            <span class="label">章节</span>
            <span class="value">{{ result.chapter ?? '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">知识点</span>
            <span class="value">{{ result.knowledge_point ?? '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">分类</span>
            <span class="value">{{ result.category ?? '-' }}</span>
          </div>
        </div>
      </div>

      <div class="content-wrapper">
        <div class="left-panel">
          <div class="theory-card">
            <h3>📖 理论定义</h3>
            <div class="definition-content">
              <p>{{ result.definition ?? '暂无详细定义' }}</p>
            </div>
          </div>

          <div class="key-points-card">
            <h3>🎯 关键要点</h3>
            <ul v-if="result.key_points && result.key_points.length > 0">
              <li v-for="(point, index) in result.key_points!" :key="index">
                <span class="point-number">{{ (index ?? 0) + 1 }}</span>
                {{ point }}
              </li>
            </ul>
            <p v-else class="no-data">暂无关键要点</p>
          </div>

          <div v-if="result.theory_content" class="detail-card">
            <h3>📚 教材内容</h3>
            <div class="detail-content">
              <p>{{ result.theory_content }}</p>
            </div>
          </div>

          <div v-if="result.diagram && result.diagram.format === 'mermaid'" class="diagram-card">
            <h3>📊 知识图表</h3>
            <div class="mermaid-chart" ref="mermaidContainer"></div>
          </div>

          <div v-if="result.relationship_explanation" class="explanation-card">
            <h3>💡 关联说明</h3>
            <div class="explanation-content">
              <p>{{ result.relationship_explanation }}</p>
            </div>
          </div>
        </div>

        <div class="right-panel">
          <KnowledgeGraph
            :title="result.knowledge_point ?? '知识关联图谱'"
            :knowledge-point-content="result.knowledge_point ?? ''"
            @node-click="handleNodeClick"
          />
        </div>
      </div>
    </div>

    <div v-else-if="!isLoading && searchTopic" class="no-result">
      <div class="no-result-icon">🔍</div>
      <h3>未找到相关知识点</h3>
      <p>请尝试输入其他数据库相关的知识点，如：数据模型、关系代数、事务、数据库恢复等</p>
      <div class="suggestions">
        <span>常见知识点：</span>
        <button
          v-for="suggestion in suggestions"
          :key="suggestion"
          class="suggestion-btn"
          @click="selectTag(suggestion)"
        >
          {{ suggestion }}
        </button>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon">📚</div>
      <h2>智能知识点可视化</h2>
      <p>输入任意数据库相关知识点，系统将自动检索王珊《数据库系统概述》教材内容，生成直观的可视化图表</p>
      <div class="features">
        <div class="feature-card">
          <span class="feature-icon">🎯</span>
          <h4>精准匹配</h4>
          <p>自动匹配教材中的对应理论内容</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">📊</span>
          <h4>图表可视化</h4>
          <p>生成专业的Mermaid图表</p>
        </div>
        <div class="feature-card">
          <span class="feature-icon">🔗</span>
          <h4>知识关联</h4>
          <p>展示知识点间的多维逻辑关系</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onBeforeUnmount, computed } from 'vue'
import { agentApi } from '@/api'
import type { VisualizationResponse } from '@/types'
import KnowledgeGraph from '@/components/KnowledgeGraph.vue'
import { useLearningProgress } from '@/utils/useLearningProgress'
import mermaid from 'mermaid'

const searchTopic = ref('')
const isLoading = ref(false)
const result = ref<VisualizationResponse | null>(null)
const mermaidContainer = ref<HTMLElement | null>(null)

const quickTags = [
  '数据模型',
  '关系代数',
  '数据库设计范式',
  '事务处理',
  '并发控制',
  '数据库恢复',
  'B+树索引',
  'ER图'
]

const suggestions = [
  '数据库系统结构',
  '数据模型',
  '关系代数',
  'SQL语言',
  '数据库安全性',
  '数据库完整性',
  '函数依赖',
  '范式',
  '事务ACID',
  '并发控制',
  '死锁',
  'MVCC',
  'B+树',
  'ER模型'
]

const {
  initTracking,
  cleanupTracking,
  recordModuleAccess,
  recordInteraction,
  accumulatedDuration,
  interactionCount,
  MODULE_TYPES
} = useLearningProgress()

const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const selectTag = (tag: string) => {
  searchTopic.value = tag
  recordInteraction('search', 'quick_tag_click', tag)
  handleSearch()
}

const handleSearch = async () => {
  if (!searchTopic.value.trim()) return

  isLoading.value = true
  result.value = null

  recordModuleAccess('knowledge_visualization', searchTopic.value.trim())
  recordInteraction('search', 'search_submit', searchTopic.value.trim())

  try {
    const response = await agentApi.visualize({ topic: searchTopic.value.trim() })
    result.value = response
    isLoading.value = false

    if (response.success && response.diagram && response.diagram.format === 'mermaid') {
      await nextTick()
      await renderMermaid(response.diagram.content)
      recordModuleAccess('diagram', searchTopic.value.trim())
    }

    if (result.value?.knowledge_point) {
      recordModuleAccess('theory_content', result.value.knowledge_point)
      recordModuleAccess('key_points', result.value.knowledge_point)
    }
  } catch (error) {
    console.error('Visualization error:', error)
    result.value = { success: false }
    isLoading.value = false
  }
}

const handleNodeClick = (node: { label: string }) => {
  searchTopic.value = node.label
  recordInteraction('node_click', 'graph_node_click', node.label)
  recordModuleAccess('knowledge_graph', node.label)
  handleSearch()
}

let mermaidInitialized = false

const ensureMermaidInitialized = () => {
  if (mermaidInitialized) return
  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    flowchart: {
      useMaxWidth: false,
      nodeSpacing: 80,
      rankSpacing: 100
    },
    themeVariables: {
      fontSize: '16px',
      fontFamily: 'Microsoft YaHei, PingFang SC, sans-serif'
    }
  })
  mermaidInitialized = true
}

const renderMermaid = async (script: string) => {
  if (!mermaidContainer.value) {
    await nextTick()
  }
  
  if (!mermaidContainer.value) {
    console.warn('Mermaid container still not available after nextTick')
    return
  }

  try {
    ensureMermaidInitialized()
    mermaidContainer.value.innerHTML = ''
    const chartId = `mermaid-chart-${Math.floor(Math.random() * 1000000)}`
    
    const result = await mermaid.render(chartId, script)
    if (result && typeof result === 'object' && 'svg' in result) {
      mermaidContainer.value.innerHTML = result.svg
    } else {
      mermaidContainer.value.innerHTML = '<div style="color: #f56c6c; padding: 20px;">图表渲染失败：返回格式不正确</div>'
    }
  } catch (error) {
    console.error('Mermaid render error:', error)
    if (mermaidContainer.value) {
      mermaidContainer.value.innerHTML = `<div style="color: #f56c6c; padding: 20px;">图表渲染失败：${error instanceof Error ? error.message : '未知错误'}</div>`
    }
  }
}

onMounted(() => {
  ensureMermaidInitialized()
  initTracking()
})

onBeforeUnmount(() => {
  cleanupTracking()
})
</script>

<style scoped>
.visualization-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 20px;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  font-size: 2.5rem;
  color: #1a1a2e;
  margin-bottom: 10px;
}

.subtitle {
  font-size: 1.1rem;
  color: #666;
}

.search-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}

.search-box {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.search-box input {
  flex: 1;
  padding: 18px 24px;
  font-size: 1.1rem;
  border: none;
  border-radius: 12px;
  outline: none;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.search-btn {
  padding: 18px 32px;
  font-size: 1.1rem;
  font-weight: bold;
  background: #fff;
  color: #667eea;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.icon {
  font-size: 1.3rem;
}

.quick-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.quick-tag {
  padding: 8px 16px;
  font-size: 0.95rem;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-tag:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.loading {
  text-align: center;
  padding: 80px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading p {
  font-size: 1.1rem;
  color: #666;
}

.result-section {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.result-header {
  margin-bottom: 25px;
}

.info-card {
  display: flex;
  gap: 25px;
  background: #fff;
  padding: 20px 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-item .label {
  font-size: 0.9rem;
  color: #888;
  font-weight: 500;
}

.info-item .value {
  font-size: 1rem;
  font-weight: bold;
  color: #333;
  background: #f0f4ff;
  padding: 6px 14px;
  border-radius: 8px;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
}

.left-panel, .right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 600px;
}

.theory-card, .key-points-card, .detail-card, .diagram-card, .explanation-card {
  background: #fff;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.theory-card h3, .key-points-card h3, .detail-card h3, .diagram-card h3, .explanation-card h3 {
  font-size: 1.2rem;
  color: #1a1a2e;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.definition-content p, .detail-content p, .explanation-content p {
  font-size: 1rem;
  line-height: 1.8;
  color: #444;
  text-align: justify;
}

.key-points-card ul {
  list-style: none;
  padding: 0;
}

.key-points-card li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.key-points-card li:last-child {
  border-bottom: none;
}

.point-number {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: bold;
  flex-shrink: 0;
}

.no-data {
  color: #999;
  font-style: italic;
}

.mermaid-chart {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  min-height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}

.mermaid-chart :deep(svg) {
  width: 100% !important;
  height: auto !important;
  max-width: 100% !important;
  max-height: none !important;
  min-height: 350px;
  display: block;
}

.image-chart {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-chart img {
  max-width: 100%;
  max-height: 500px;
  border-radius: 8px;
}

.no-diagram {
  text-align: center;
  padding: 80px 20px;
  color: #999;
}

.no-result {
  text-align: center;
  padding: 60px 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.no-result-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.no-result h3 {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 10px;
}

.no-result p {
  font-size: 1rem;
  color: #666;
  margin-bottom: 25px;
}

.suggestions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.suggestions span {
  color: #666;
  font-weight: 500;
}

.suggestion-btn {
  padding: 8px 16px;
  font-size: 0.9rem;
  background: #f0f4ff;
  color: #667eea;
  border: 1px solid #e0e7ff;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.suggestion-btn:hover {
  background: #667eea;
  color: #fff;
  border-color: #667eea;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 5rem;
  margin-bottom: 25px;
}

.empty-state h2 {
  font-size: 2rem;
  color: #1a1a2e;
  margin-bottom: 15px;
}

.empty-state p {
  font-size: 1.1rem;
  color: #666;
  max-width: 600px;
  margin: 0 auto 40px;
}

.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 25px;
  max-width: 900px;
  margin: 0 auto;
}

.feature-card {
  background: #fff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.feature-card h4 {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 10px;
}

.feature-card p {
  font-size: 0.95rem;
  color: #666;
  line-height: 1.6;
}

.learning-progress-bar {
  display: flex;
  align-items: center;
  gap: 30px;
  background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);
  border-radius: 12px;
  padding: 15px 25px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.1);
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.progress-icon {
  font-size: 1.2rem;
}

.progress-label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

.progress-value {
  font-size: 1rem;
  font-weight: bold;
  color: #667eea;
}

.progress-hint {
  margin-left: auto;
  font-size: 0.85rem;
  color: #999;
  font-style: italic;
}

@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .info-card {
    flex-direction: column;
    gap: 15px;
  }
  
  .search-box {
    flex-direction: column;
  }
  
  .header h1 {
    font-size: 1.8rem;
  }
}
</style>
