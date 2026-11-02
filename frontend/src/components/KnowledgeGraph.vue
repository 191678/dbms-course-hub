<template>
  <div class="knowledge-graph-container">
    <div class="graph-header">
      <div class="title-section">
        <h3>📊 {{ title }}</h3>
        <span class="node-count">共 {{ filteredNodes.length }} 个关联节点</span>
      </div>
      <div class="toolbar">
        <div class="view-mode-switch">
          <button
            v-for="mode in viewModes"
            :key="mode.value"
            :class="['mode-btn', { active: currentMode === mode.value }]"
            @click="currentMode = mode.value as 'force' | 'mindmap' | 'list'"
          >
            <span class="mode-icon">{{ mode.icon }}</span>
            {{ mode.label }}
          </button>
        </div>
        <div class="relation-filter">
          <select v-model="selectedRelations" multiple @change="handleFilterChange">
            <option value="all">全部关系</option>
            <option v-for="(info, key) in relationTypes" :key="key" :value="key">
              {{ info.name }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading">
      <div class="loading-spinner"></div>
      <p>正在加载知识关联数据...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="loadData">重试</button>
    </div>

    <div v-else class="graph-content">
      <div v-if="currentMode === 'force'" class="force-graph-wrapper" ref="forceGraphRef">
        <svg
          ref="svgRef"
          :viewBox="viewBox"
          class="force-graph-svg"
          @wheel.prevent="handleWheel"
          @mousedown="handleMouseDown"
          @mousemove="handleMouseMove"
          @mouseup="handleMouseUp"
          @mouseleave="handleMouseUp"
        >
          <defs>
            <marker
              v-for="(info, key) in relationTypes"
              :key="'arrow-' + key"
              :id="'arrow-' + key"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
              markerUnits="strokeWidth"
            >
              <path
                d="M0,0 L0,6 L9,3 z"
                :fill="info.color"
              />
            </marker>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#eee" stroke-width="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          <g class="edges">
            <g v-for="edge in filteredEdges" :key="edge.id">
              <path
                :d="getEdgePath(edge)"
                :stroke="edge.color"
                :stroke-dasharray="getLineStyle(edge.lineStyle)"
                stroke-width="2"
                :marker-end="`url(#arrow-${edge.relation_type})`"
                class="edge-path"
                @mouseenter="showEdgeTooltip($event, edge)"
                @mouseleave="hideTooltip"
              />
              <text
                :x="((edge.sourceX ?? 0) + (edge.targetX ?? 0)) / 2"
                :y="((edge.sourceY ?? 0) + (edge.targetY ?? 0)) / 2 - 5"
                text-anchor="middle"
                :fill="edge.color"
                class="edge-label"
                font-size="11"
                font-weight="500"
              >
                {{ edge.icon }}
              </text>
            </g>
          </g>
          <g class="nodes">
            <g
              v-for="node in filteredNodes"
              :key="node.id"
              :transform="`translate(${node.x}, ${node.y})`"
              class="node-group"
              @click="handleNodeClick(node)"
              @mouseenter="showNodeTooltip($event, node)"
              @mouseleave="hideTooltip"
            >
              <circle
                :r="node.is_current ? 28 : 22"
                :fill="node.is_current ? '#667eea' : getCategoryColor(node.category)"
                :stroke="node.is_current ? '#764ba2' : '#ddd'"
                stroke-width="2"
                class="node-circle"
              />
              <circle
                v-if="node.is_current"
                r="34"
                fill="none"
                stroke="#667eea"
                stroke-width="1"
                stroke-dasharray="5,5"
                opacity="0.5"
              />
              <text
                text-anchor="middle"
                dominant-baseline="central"
                fill="white"
                font-size="node.is_current ? 12 : 10"
                font-weight="500"
                class="node-label"
              >
                {{ truncateLabel(node.label) }}
              </text>
            </g>
          </g>
        </svg>
        <div class="zoom-controls">
          <button class="zoom-btn" @click="zoomIn">+</button>
          <span class="zoom-value">{{ Math.round(scale * 100) }}%</span>
          <button class="zoom-btn" @click="zoomOut">−</button>
          <button class="zoom-btn" @click="resetView">⟲</button>
        </div>
      </div>

      <div v-else-if="currentMode === 'mindmap'" class="mindmap-wrapper">
        <div class="mindmap-container">
          <div class="mindmap-center">
            <div class="center-node" :class="{ current: true }" @click="currentKP && handleNodeClick(currentKP)">
              <div class="node-content">
                <span class="node-icon">🎯</span>
                <span class="node-text">{{ currentKP?.label }}</span>
              </div>
              <div v-if="currentKP?.description" class="node-description">
                {{ currentKP.description }}
              </div>
            </div>
            <div v-for="(_edges, relationType) in groupedEdges" :key="relationType" class="relation-group">
              <div class="relation-header">
                <span class="relation-icon" :style="{ color: relationTypes[relationType]?.color }">
                  {{ relationTypes[relationType]?.icon }}
                </span>
                <span class="relation-name">{{ relationTypes[relationType]?.name }}</span>
              </div>
              <div class="relation-nodes">
                <div
                  v-for="node in getNodesByRelation(relationType)"
                  :key="node.id"
                  class="mindmap-node"
                  :class="{ 'is-current': node.is_current }"
                  :style="{ borderLeftColor: relationTypes[relationType]?.color }"
                  @click="handleNodeClick(node)"
                  @mouseenter="showNodeTooltip($event, node)"
                  @mouseleave="hideTooltip"
                >
                  <div class="node-header">
                    <span class="node-label">{{ node.label }}</span>
                    <span class="node-category">{{ node.category }}</span>
                  </div>
                  <div v-if="node.description" class="node-desc">{{ node.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="currentMode === 'list'" class="list-wrapper">
        <div class="relation-list">
          <div
            v-for="(_edges, relationType) in groupedEdges"
            :key="relationType"
            class="list-section"
          >
            <div
              class="list-section-header"
              :style="{ backgroundColor: relationTypes[relationType]?.color + '15', borderColor: relationTypes[relationType]?.color }"
            >
              <span class="section-icon" :style="{ color: relationTypes[relationType]?.color }">
                {{ relationTypes[relationType]?.icon }}
              </span>
              <span class="section-title">{{ relationTypes[relationType]?.name }}</span>
              <span class="section-count">({{ getNodesByRelation(relationType).length }})</span>
            </div>
            <div class="list-items">
              <div
                v-for="node in getNodesByRelation(relationType)"
                :key="node.id"
                class="list-item"
                @click="handleNodeClick(node)"
                @mouseenter="showNodeTooltip($event, node)"
                @mouseleave="hideTooltip"
              >
                <div class="item-indicator" :style="{ backgroundColor: relationTypes[relationType]?.color }"></div>
                <div class="item-content">
                  <div class="item-header">
                    <span class="item-label">{{ node.label }}</span>
                    <span class="item-category">{{ node.category }}</span>
                  </div>
                  <div v-if="node.description" class="item-desc">{{ node.description }}</div>
                </div>
                <div class="item-action">
                  <span class="arrow">→</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tooltipVisible" class="tooltip" :style="tooltipStyle">
      <div class="tooltip-header">{{ tooltipData.label }}</div>
      <div class="tooltip-category">{{ tooltipData.category }}</div>
      <div v-if="tooltipData.description" class="tooltip-desc">{{ tooltipData.description }}</div>
      <div v-if="tooltipData.relationName" class="tooltip-relation">
        <span class="relation-badge" :style="{ backgroundColor: tooltipData.color }">
          {{ tooltipData.relationName }}
        </span>
      </div>
    </div>

    <div class="legend">
      <div v-for="(info, key) in relationTypes" :key="key" class="legend-item">
        <span class="legend-line" :style="{ backgroundColor: info.color, borderStyle: info.lineStyle }"></span>
        <span class="legend-icon">{{ info.icon }}</span>
        <span class="legend-text">{{ info.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { knowledgeGraphApi } from '@/api'

interface Node {
  id: number
  label: string
  category: string
  is_current: boolean
  description: string
  difficulty?: string
  x?: number
  y?: number
}

interface Edge {
  source: number
  target: number
  relation_type: string
  relation_name: string
  color: string
  lineStyle: string
  icon: string
  sourceX?: number
  targetX?: number
  sourceY?: number
  targetY?: number
  id?: string
}

interface RelationTypes {
  [key: string]: {
    name: string
    color: string
    lineStyle: string
    icon: string
  }
}

interface KnowledgeGraphResponse {
  success: boolean
  message?: string
  current_knowledge_point?: {
    id: number
    label: string
    category: string
    description: string
  }
  nodes: Node[]
  edges: Edge[]
  relation_types: RelationTypes
  total_nodes: number
  total_edges: number
}

const props = defineProps<{
  title: string
  knowledgePointId?: number
  knowledgePointContent?: string
}>()

const emit = defineEmits<{
  (e: 'node-click', node: Node): void
}>()

const isLoading = ref(false)
const error = ref('')
const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])
const relationTypes = ref<RelationTypes>({})
const currentKP = ref<Node | null>(null)

const currentMode = ref<'force' | 'mindmap' | 'list'>('force')
const selectedRelations = ref<string[]>(['all'])
const tooltipVisible = ref(false)
const tooltipData = ref<Partial<Node & { relationName?: string; color?: string }>>({})
const tooltipStyle = ref({})

const svgRef = ref<SVGSVGElement | null>(null)
const forceGraphRef = ref<HTMLElement | null>(null)
const scale = ref(1)
const translateX = ref(0)
const translateY = ref(0)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const viewBox = ref('0 0 800 600')

const viewModes = [
  { value: 'force', label: '节点图', icon: '🔗' },
  { value: 'mindmap', label: '思维导图', icon: '🌳' },
  { value: 'list', label: '列表', icon: '📋' },
]

const categoryColors: Record<string, string> = {
  '基础概念': '#667eea',
  '数据模型': '#85ce61',
  '关系数据理论': '#e6a23c',
  'SQL语言': '#f56c6c',
  '数据库设计': '#909399',
  '事务处理': '#5b8ff9',
  '并发控制': '#5ad8a6',
  '数据库恢复': '#f6bd16',
  '数据库安全性': '#6dc8ec',
  '数据库完整性': '#9270ca',
  '索引': '#ff9d4d',
  '查询优化': '#9661bc',
  '未分类': '#909399',
}

const getCategoryColor = (category: string) => {
  return categoryColors[category] || '#909399'
}

const getLineStyle = (style: string) => {
  switch (style) {
    case 'dashed': return '5,5'
    case 'dotted': return '2,2'
    case 'dashdot': return '5,2,2,2'
    default: return 'none'
  }
}

const truncateLabel = (label: string) => {
  return label.length > 6 ? label.slice(0, 5) + '...' : label
}

const filteredEdges = computed(() => {
  if (selectedRelations.value.includes('all')) return edges.value
  return edges.value.filter(e => selectedRelations.value.includes(e.relation_type))
})

const filteredNodes = computed(() => {
  if (selectedRelations.value.includes('all')) return nodes.value
  const relatedNodeIds = new Set<number>()
  filteredEdges.value.forEach(e => {
    relatedNodeIds.add(e.source)
    relatedNodeIds.add(e.target)
  })
  return nodes.value.filter(n => relatedNodeIds.has(n.id))
})

const groupedEdges = computed(() => {
  const groups: Record<string, Edge[]> = {}
  filteredEdges.value.forEach(edge => {
    if (!groups[edge.relation_type]) {
      groups[edge.relation_type] = []
    }
    groups[edge.relation_type].push(edge)
  })
  return groups
})

const getNodesByRelation = (relationType: string) => {
  const edgeList = groupedEdges.value[relationType] || []
  const nodeIds = new Set<number>()
  edgeList.forEach(e => {
    if (e.target !== currentKP.value?.id) nodeIds.add(e.target)
    if (e.source !== currentKP.value?.id) nodeIds.add(e.source)
  })
  return nodes.value.filter(n => nodeIds.has(n.id))
}

const getEdgePath = (edge: Edge) => {
  const sourceX = edge.sourceX ?? 0
  const sourceY = edge.sourceY ?? 0
  const targetX = edge.targetX ?? 0
  const targetY = edge.targetY ?? 0
  const dx = targetX - sourceX
  const dy = targetY - sourceY
  const dist = Math.sqrt(dx * dx + dy * dy) || 1
  const offset = edge.source === currentKP.value?.id ? 28 : 22
  const startX = sourceX + (dx / dist) * offset
  const startY = sourceY + (dy / dist) * offset
  const endOffset = edge.target === currentKP.value?.id ? 28 : 22
  const endX = targetX - (dx / dist) * endOffset
  const endY = targetY - (dy / dist) * endOffset
  return `M ${startX} ${startY} L ${endX} ${endY}`
}

const applyForceLayout = () => {
  const width = 800
  const height = 600
  const centerX = width / 2
  const centerY = height / 2

  nodes.value.forEach(node => {
    if (node.is_current) {
      node.x = centerX
      node.y = centerY
    } else {
      const angle = (Math.random() * Math.PI * 2)
      const distance = 150 + Math.random() * 150
      node.x = centerX + Math.cos(angle) * distance
      node.y = centerY + Math.sin(angle) * distance
    }
  })

  edges.value.forEach(edge => {
    const sourceNode = nodes.value.find(n => n.id === edge.source)
    const targetNode = nodes.value.find(n => n.id === edge.target)
    edge.id = `${edge.source}-${edge.target}`
    edge.sourceX = sourceNode?.x || 0
    edge.sourceY = sourceNode?.y || 0
    edge.targetX = targetNode?.x || 0
    edge.targetY = targetNode?.y || 0
  })

  viewBox.value = `0 0 ${width} ${height}`
}

const loadData = async () => {
  isLoading.value = true
  error.value = ''

  try {
    let response: KnowledgeGraphResponse
    if (props.knowledgePointId) {
      response = await knowledgeGraphApi.getById(props.knowledgePointId)
    } else if (props.knowledgePointContent) {
      response = await knowledgeGraphApi.getByContent(props.knowledgePointContent)
    } else {
      return
    }

    if (response.success) {
      nodes.value = response.nodes
      edges.value = response.edges
      relationTypes.value = response.relation_types
      currentKP.value = response.current_knowledge_point ? {
        ...response.current_knowledge_point,
        is_current: true,
        description: response.current_knowledge_point.description
      } : null

      await nextTick()
      applyForceLayout()
    } else {
      error.value = response.message || '加载失败'
    }
  } catch (err) {
    error.value = '加载知识关联数据时发生错误，请稍后重试'
    console.error('Knowledge graph load error:', err)
  } finally {
    isLoading.value = false
  }
}

const handleFilterChange = () => {
  if (currentMode.value === 'force') {
    applyForceLayout()
  }
}

const handleWheel = (e: WheelEvent) => {
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  scale.value = Math.max(0.3, Math.min(2, scale.value * delta))
}

const zoomIn = () => {
  scale.value = Math.min(2, scale.value * 1.2)
}

const zoomOut = () => {
  scale.value = Math.max(0.3, scale.value / 1.2)
}

const resetView = () => {
  scale.value = 1
  translateX.value = 0
  translateY.value = 0
  applyForceLayout()
}

const handleMouseDown = (e: MouseEvent) => {
  isDragging.value = true
  dragStart.value = { x: e.clientX - translateX.value, y: e.clientY - translateY.value }
}

const handleMouseMove = (e: MouseEvent) => {
  if (!isDragging.value) return
  translateX.value = e.clientX - dragStart.value.x
  translateY.value = e.clientY - dragStart.value.y
}

const handleMouseUp = () => {
  isDragging.value = false
}

const handleNodeClick = (node: Node) => {
  emit('node-click', node)
}

const showNodeTooltip = (e: MouseEvent, node: Node) => {
  tooltipVisible.value = true
  tooltipData.value = {
    label: node.label,
    category: node.category,
    description: node.description
  }
  tooltipStyle.value = {
    left: `${e.clientX + 10}px`,
    top: `${e.clientY + 10}px`
  }
}

const showEdgeTooltip = (e: MouseEvent, edge: Edge) => {
  tooltipVisible.value = true
  tooltipData.value = {
    label: edge.relation_name,
    relationName: edge.relation_name,
    color: edge.color
  }
  tooltipStyle.value = {
    left: `${e.clientX + 10}px`,
    top: `${e.clientY + 10}px`
  }
}

const hideTooltip = () => {
  tooltipVisible.value = false
}

watch(() => [props.knowledgePointId, props.knowledgePointContent], () => {
  loadData()
})

onMounted(() => {
  loadData()
})

onUnmounted(() => {})
</script>

<style scoped>
.knowledge-graph-container {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title-section h3 {
  font-size: 1.2rem;
  color: #1a1a2e;
  margin: 0;
}

.node-count {
  font-size: 0.85rem;
  color: #999;
  background: #f5f7fa;
  padding: 4px 12px;
  border-radius: 12px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 15px;
}

.view-mode-switch {
  display: flex;
  background: #f0f4ff;
  border-radius: 8px;
  padding: 4px;
}

.mode-btn {
  padding: 8px 16px;
  font-size: 0.85rem;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  color: #666;
}

.mode-btn:hover {
  background: rgba(102, 126, 234, 0.1);
}

.mode-btn.active {
  background: #667eea;
  color: #fff;
}

.mode-icon {
  font-size: 1rem;
}

.relation-filter select {
  padding: 8px 12px;
  font-size: 0.85rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  outline: none;
}

.graph-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.loading, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #999;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.retry-btn {
  padding: 10px 24px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 10px;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: #764ba2;
}

.force-graph-wrapper {
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 8px;
  background: #fafafa;
  position: relative;
}

.force-graph-svg {
  width: 100%;
  height: 100%;
  cursor: grab;
}

.force-graph-svg:active {
  cursor: grabbing;
}

.edge-path {
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.edge-path:hover {
  opacity: 0.7;
  stroke-width: 3;
}

.edge-label {
  pointer-events: none;
}

.node-group {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.node-group:hover {
  transform: scale(1.1);
}

.node-circle {
  transition: stroke-width 0.2s ease;
}

.node-group:hover .node-circle {
  stroke-width: 3;
}

.zoom-controls {
  position: absolute;
  bottom: 15px;
  right: 15px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  background: rgba(255, 255, 255, 0.9);
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.zoom-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f0f4ff;
  color: #667eea;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.zoom-btn:hover {
  background: #667eea;
  color: #fff;
}

.zoom-value {
  font-size: 0.75rem;
  color: #666;
  text-align: center;
  padding: 4px 0;
}

.mindmap-wrapper {
  width: 100%;
  height: 100%;
  overflow-y: auto;
}

.mindmap-container {
  padding: 20px;
}

.mindmap-center {
  max-width: 900px;
  margin: 0 auto;
}

.center-node {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 30px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.center-node:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.node-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.node-icon {
  font-size: 1.5rem;
}

.node-text {
  font-size: 1.3rem;
  font-weight: bold;
}

.node-description {
  margin-top: 10px;
  font-size: 0.9rem;
  opacity: 0.9;
  line-height: 1.6;
}

.relation-group {
  margin-bottom: 25px;
}

.relation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
}

.relation-icon {
  font-size: 1.1rem;
}

.relation-nodes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.mindmap-node {
  background: #f8f9fa;
  border-left: 4px solid #ddd;
  padding: 15px;
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mindmap-node:hover {
  background: #fff;
  transform: translateX(5px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.node-label {
  font-weight: 600;
  color: #333;
}

.node-category {
  font-size: 0.75rem;
  color: #999;
  background: #fff;
  padding: 2px 8px;
  border-radius: 4px;
}

.node-desc {
  font-size: 0.85rem;
  color: #666;
  line-height: 1.5;
}

.list-wrapper {
  width: 100%;
  height: 100%;
  overflow-y: auto;
}

.relation-list {
  padding: 10px;
}

.list-section {
  margin-bottom: 20px;
}

.list-section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  border-radius: 8px;
  border-left: 4px solid;
  margin-bottom: 12px;
}

.section-icon {
  font-size: 1.1rem;
}

.section-title {
  font-weight: 600;
  color: #333;
}

.section-count {
  font-size: 0.85rem;
  color: #999;
}

.list-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.list-item {
  display: flex;
  align-items: center;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.list-item:hover {
  background: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.item-indicator {
  width: 4px;
  height: 40px;
  border-radius: 2px;
  margin-right: 12px;
}

.item-content {
  flex: 1;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.item-label {
  font-weight: 500;
  color: #333;
}

.item-category {
  font-size: 0.75rem;
  color: #999;
}

.item-desc {
  font-size: 0.85rem;
  color: #666;
}

.item-action {
  color: #667eea;
  margin-left: 10px;
}

.arrow {
  font-size: 1.2rem;
}

.tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.9);
  color: #fff;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  z-index: 1000;
  max-width: 280px;
  pointer-events: none;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.tooltip-header {
  font-weight: 600;
  margin-bottom: 4px;
}

.tooltip-category {
  font-size: 0.75rem;
  color: #aaa;
  margin-bottom: 6px;
}

.tooltip-desc {
  font-size: 0.8rem;
  color: #ccc;
  line-height: 1.5;
}

.tooltip-relation {
  margin-top: 8px;
}

.relation-badge {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 4px;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: #666;
}

.legend-line {
  width: 20px;
  height: 3px;
  border-radius: 2px;
}

.legend-icon {
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .graph-header {
    flex-direction: column;
    gap: 15px;
  }

  .toolbar {
    flex-wrap: wrap;
    justify-content: center;
  }

  .mindmap-node {
    border-left: none;
    border-top: 4px solid;
    border-radius: 8px 8px 0 0;
  }

  .mindmap-node:hover {
    transform: translateY(-3px);
  }
}
</style>
