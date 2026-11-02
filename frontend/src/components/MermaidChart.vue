<template>
  <div class="mermaid-container-wrapper">
    <div ref="chartContainer" class="mermaid-wrapper"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import mermaid from 'mermaid'

const props = defineProps<{
  script: string
}>()

const chartContainer = ref<HTMLElement | null>(null)
let initialized = false

// 使用本地依赖（npm 打包）初始化 Mermaid，避免依赖 jsdelivr CDN 导致"加载失败"
const ensureInit = () => {
  if (initialized) return
  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose',
    fontFamily: 'inherit'
  })
  initialized = true
}

const renderChart = async () => {
  if (!chartContainer.value) {
    return
  }

  if (!props.script) {
    chartContainer.value.innerHTML = '<div style="color: #909399; padding: 20px; font-size: 18px;">暂无图表数据</div>'
    return
  }

  const cleanScript = props.script
    .replace(/^\uFEFF/, '')
    .replace(/\r\n/g, '\n')
    .trim()

  const id = `mermaid-${Date.now()}-${Math.floor(Math.random() * 1000000)}`

  try {
    ensureInit()
    const result = await mermaid.render(id, cleanScript)

    if (result && typeof result === 'object' && 'svg' in result) {
      chartContainer.value.innerHTML = result.svg

      await nextTick()

      const svgEl = chartContainer.value.querySelector('svg')

      if (svgEl) {
        svgEl.style.display = 'block'
        svgEl.style.width = '100%'
        svgEl.style.minWidth = '600px'
        svgEl.style.height = 'auto'
        svgEl.style.minHeight = '500px'
        svgEl.style.maxHeight = 'none'
        svgEl.setAttribute('preserveAspectRatio', 'xMidYMid meet')

        const viewBox = svgEl.getAttribute('viewBox')
        const widthAttr = svgEl.getAttribute('width')
        const heightAttr = svgEl.getAttribute('height')

        if (!viewBox) {
          const computedWidth = parseFloat(widthAttr || '800')
          const computedHeight = parseFloat(heightAttr || '600')
          svgEl.setAttribute('viewBox', `0 0 ${computedWidth} ${computedHeight}`)
        }
      } else {
        chartContainer.value.innerHTML = '<div style="color: #f56c6c; padding: 20px; font-size: 18px;">SVG元素未找到</div>'
      }
    } else {
      chartContainer.value.innerHTML = '<div style="color: #f56c6c; padding: 20px; font-size: 18px;">图表渲染失败</div>'
    }
  } catch (err) {
    console.error('Mermaid render error:', err)
    chartContainer.value.innerHTML = `<div style="color: #f56c6c; padding: 20px; font-size: 18px;">图表渲染失败: ${err instanceof Error ? err.message : 'Unknown error'}</div>`
  }
}

onMounted(() => {
  renderChart()
})

watch(() => props.script, () => {
  renderChart()
})
</script>

<style scoped>
.mermaid-container-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: auto;
}

.mermaid-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}

.mermaid-wrapper :deep(svg) {
  max-width: 100%;
  height: auto;
}
</style>
