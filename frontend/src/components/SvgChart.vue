<template>
  <div class="svg-chart" :class="{ compact }">
    <svg :viewBox="`0 0 ${W} ${height}`" preserveAspectRatio="xMidYMid meet" class="chart-svg">
      <!-- ============ 饼图 ============ -->
      <g v-if="type === 'pie'">
        <template v-if="pieTotal > 0">
          <path v-for="(s, i) in pieSlices" :key="i" :d="s.d" :fill="s.color" stroke="#ffffff" stroke-width="1.5" />
          <template v-if="!compact">
            <g v-for="(s, i) in pieLegend" :key="'pl' + i">
              <rect :x="legendX" :y="s.y - 9" width="12" height="12" rx="2" :fill="s.color" />
              <text :x="legendX + 18" :y="s.y" class="chart-label">{{ s.name }} {{ s.percent }}%</text>
            </g>
          </template>
        </template>
        <text v-else :x="W / 2" :y="height / 2" text-anchor="middle" class="chart-empty">暂无数据</text>
      </g>

      <!-- ============ 折线图 ============ -->
      <g v-else-if="type === 'line'">
        <text v-if="!lineValues.length" :x="W / 2" :y="height / 2" text-anchor="middle" class="chart-empty">暂无数据</text>
        <template v-else>
        <line v-for="(g, i) in lineGrid" :key="'lg' + i" :x1="lineLeft" :y1="g.y" :x2="W - 16" :y2="g.y" class="chart-grid" />
        <text v-for="(g, i) in lineGrid" :key="'lt' + i" :x="lineLeft - 6" :y="g.y + 4" text-anchor="end" class="chart-axis">{{ g.label }}</text>
        <polyline :points="linePoints" fill="none" :stroke="colorAt(0)" stroke-width="2.5" stroke-linejoin="round" />
        <template v-if="lineAverage !== null">
          <line :x1="lineLeft" :y1="lineAverageY" :x2="W - 16" :y2="lineAverageY" class="chart-average" stroke-dasharray="6 4" />
          <text :x="W - 16" :y="lineAverageY - 6" text-anchor="end" class="chart-average-label">均值 {{ lineAverage }}</text>
        </template>
        <circle v-for="(p, i) in lineDots" :key="'ld' + i" :cx="p.x" :cy="p.y" r="3.5"
          :fill="isSimulated(i) ? '#ffffff' : colorAt(0)"
          :stroke="isSimulated(i) ? '#E6A23C' : 'none'"
          :stroke-width="isSimulated(i) ? 2 : 0" />
        <g v-for="(a, i) in lineAnomalyDots" :key="'an' + i">
          <circle :cx="a.x" :cy="a.y" r="7" fill="#F56C6C" fill-opacity="0.18" />
          <circle :cx="a.x" :cy="a.y" r="4" fill="#F56C6C" />
          <text :x="a.x" :y="a.y - 11" text-anchor="middle" class="chart-anomaly">{{ a.value }}</text>
        </g>
        <text v-if="!compact" v-for="(l, i) in lineXLables" :key="'lx' + i" :x="l.x" :y="height - 8" text-anchor="middle" class="chart-axis">{{ l.text }}</text>
        </template>
      </g>

      <!-- ============ 柱状图 ============ -->
      <g v-else-if="type === 'bar'">
        <text v-if="!barValues.length" :x="W / 2" :y="height / 2" text-anchor="middle" class="chart-empty">暂无数据</text>
        <template v-else>
        <line v-for="(g, i) in barGrid" :key="'bg' + i" :x1="barLeft" :y1="g.y" :x2="W - 16" :y2="g.y" class="chart-grid" />
        <text v-for="(g, i) in barGrid" :key="'bt' + i" :x="barLeft - 6" :y="g.y + 4" text-anchor="end" class="chart-axis">{{ g.label }}</text>
        <rect v-for="(b, i) in barBars" :key="'bb' + i" :x="b.x" :y="b.y" :width="b.w" :height="b.h"
          :fill="colorAt(i)" :fill-opacity="isSimulated(i) ? 0.35 : 1"
          :stroke="isSimulated(i) ? '#E6A23C' : 'none'" :stroke-width="isSimulated(i) ? 1.2 : 0"
          :stroke-dasharray="isSimulated(i) ? '4 3' : 'none'" rx="3" />
        <text v-if="!compact" v-for="(l, i) in barBarLabels" :key="'bl' + i" :x="l.x" :y="height - 8" text-anchor="middle" class="chart-axis">{{ l.text }}</text>
        </template>
      </g>

      <!-- ============ 雷达图 ============ -->
      <g v-else-if="type === 'radar'">
        <polygon v-for="(g, i) in radarGrids" :key="'rg' + i" :points="g" class="chart-grid" fill="none" />
        <line v-for="(a, i) in radarAxes" :key="'ra' + i" :x1="radarCx" :y1="radarCy" :x2="a.x" :y2="a.y" class="chart-grid" />
        <polygon v-if="radarTotal > 0" :points="radarPolygon" :fill="colorAt(0)" fill-opacity="0.28" :stroke="colorAt(0)" stroke-width="2" />
        <circle v-if="radarTotal > 0" v-for="(p, i) in radarPoints" :key="'rp' + i" :cx="p.x" :cy="p.y" r="3" :fill="colorAt(0)" />
        <text v-if="!compact" v-for="(l, i) in radarLabels" :key="'rl' + i" :x="l.x" :y="l.y" text-anchor="middle" class="chart-axis">{{ l.text }}</text>
      </g>

      <!-- ============ 热力图 ============ -->
      <g v-else-if="type === 'heatmap'">
        <rect v-for="(c, i) in heatCells" :key="'hc' + i" :x="c.x" :y="c.y" :width="c.w" :height="c.h" :fill="c.fill" rx="3" />
        <text v-if="!compact" v-for="(l, i) in heatYLabels" :key="'hy' + i" :x="heatLeft - 6" :y="l.y" text-anchor="end" class="chart-axis">{{ l.text }}</text>
        <text v-for="(l, i) in heatXLabels" :key="'hx' + i" :x="l.x" :y="height - 8" text-anchor="middle" class="chart-axis">{{ l.text }}</text>
      </g>

      <!-- ============ 兜底 ============ -->
      <text v-else :x="W / 2" :y="height / 2" text-anchor="middle" class="chart-empty">暂不支持的图表类型: {{ type }}</text>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const W = 480

const props = withDefaults(defineProps<{
  type: string
  data?: any
  height?: number
  compact?: boolean
}>(), {
  data: () => ({}),
  height: 220,
  compact: false,
})

const PALETTE = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#9B59B6', '#1ABC9C', '#909399', '#5B8FF9']
const colorAt = (i: number): string => PALETTE[i % PALETTE.length]

const colorList = computed<string[]>(() => {
  const c = props.data?.colors
  return Array.isArray(c) && c.length ? c : PALETTE
})
const sliceColor = (i: number): string => colorList.value[i % colorList.value.length]

/* ---------- 饼图 ---------- */
const pieItems = computed<{ name: string; value: number }[]>(() => {
  const d = props.data
  const arr = Array.isArray(d) ? d : (d?.items || [])
  return arr.map((it: any) => ({ name: it.name ?? '', value: Number(it.value) || 0 }))
})
const pieTotal = computed<number>(() => pieItems.value.reduce((s, it) => s + it.value, 0))

const pieGeometry = computed(() => {
  const compact = props.compact
  const cx = compact ? W / 2 : W * 0.32
  const cy = props.height / 2
  const r = Math.min(props.height / 2 - 10, compact ? W * 0.22 : W * 0.30)
  return { cx, cy, r }
})

const pieSlices = computed(() => {
  const { cx, cy, r } = pieGeometry.value
  const total = pieTotal.value
  let start = -Math.PI / 2
  return pieItems.value.map((it, i) => {
    const frac = total > 0 ? it.value / total : 0
    const end = start + frac * Math.PI * 2
    const x1 = cx + r * Math.cos(start)
    const y1 = cy + r * Math.sin(start)
    const x2 = cx + r * Math.cos(end)
    const y2 = cy + r * Math.sin(end)
    const largeArc = frac > 0.5 ? 1 : 0
    const full = frac >= 0.9999
    const d = full
      ? `M ${cx} ${cy - r} A ${r} ${r} 0 1 1 ${cx - 0.01} ${cy - r} Z`
      : `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`
    start = end
    return { d, color: sliceColor(i) }
  })
})

const legendX = W * 0.62
const pieLegend = computed(() => {
  const n = pieItems.value.length
  const total = pieTotal.value || 1
  const step = 22
  const startY = props.height / 2 - ((n - 1) * step) / 2
  return pieItems.value.map((it, i) => ({
    name: it.name,
    percent: Math.round((it.value / total) * 100),
    color: sliceColor(i),
    y: startY + i * step,
  }))
})

/* ---------- 折线 / 柱状 ---------- */
const lineLeft = 48
const barLeft = 48

function axisGrid(plotTop: number, plotH: number, maxV: number) {
  const ticks = 4
  const arr: { y: number; label: string }[] = []
  for (let i = 0; i <= ticks; i++) {
    const y = plotTop + plotH - (plotH * i) / ticks
    arr.push({ y, label: String(Math.round((maxV * i) / ticks)) })
  }
  return arr
}

const lineValues = computed<number[]>(() => (props.data?.values || []).map((v: any) => Number(v) || 0))
const lineLabels = computed<string[]>(() => props.data?.labels || props.data?.dates || [])
const lineMax = computed<number>(() => Math.max(1, ...lineValues.value))

const linePlot = computed(() => {
  const top = 16
  const h = props.height - top - 30
  return { top, h }
})
const lineGrid = computed(() => axisGrid(linePlot.value.top, linePlot.value.h, lineMax.value))
const lineDots = computed(() => {
  const vals = lineValues.value
  const n = vals.length
  if (!n) return []
  const { top, h } = linePlot.value
  const plotW = W - lineLeft - 16
  return vals.map((v, i) => ({
    x: lineLeft + (n > 1 ? (plotW * i) / (n - 1) : plotW / 2),
    y: top + h - (v / lineMax.value) * h,
  }))
})
const linePoints = computed<string>(() => lineDots.value.map((p) => `${p.x},${p.y}`).join(' '))
const lineXLables = computed(() => {
  const dots = lineDots.value
  return lineLabels.value.map((text: string, i: number) => ({ text, x: dots[i]?.x ?? 0 }))
})

// 整体平均值参考线
const lineAverage = computed<number | null>(() => {
  const avg = props.data?.average
  return typeof avg === 'number' && Number.isFinite(avg) ? avg : null
})
const lineAverageY = computed<number>(() => {
  if (lineAverage.value === null) return 0
  const { top, h } = linePlot.value
  return top + h - (lineAverage.value / lineMax.value) * h
})

// 异常波动节点（由后端标记的 index 定位）
const lineAnomalyDots = computed(() => {
  const list = props.data?.anomalies
  if (!Array.isArray(list)) return []
  const dots = lineDots.value
  return list
    .map((item: any) => {
      const dot = dots[item?.index]
      return dot ? { x: dot.x, y: dot.y, value: item?.value ?? '' } : null
    })
    .filter(Boolean) as { x: number; y: number; value: number | string }[]
})

// 模拟填充数据标记（空日期节点，与真实数据视觉区分，不参与统计）
const simulatedFlags = computed<boolean[]>(() => (Array.isArray(props.data?.simulated) ? props.data.simulated : []))
const isSimulated = (i: number): boolean => !!simulatedFlags.value[i]

const barValues = computed<number[]>(() => (props.data?.values || []).map((v: any) => Number(v) || 0))
const barLabels = computed<string[]>(() => props.data?.labels || [])
const barMax = computed<number>(() => Math.max(1, ...barValues.value))
const barGrid = computed(() => axisGrid(16, props.height - 16 - 30, barMax.value))
const barBars = computed(() => {
  const vals = barValues.value
  const n = vals.length
  if (!n) return []
  const top = 16
  const h = props.height - top - 30
  const plotW = W - barLeft - 16
  const slot = plotW / n
  const w = Math.max(6, slot * 0.6)
  return vals.map((v, i) => {
    const bh = (v / barMax.value) * h
    return { x: barLeft + slot * i + (slot - w) / 2, y: top + h - bh, w, h: bh }
  })
})
const barBarLabels = computed(() => {
  const bars = barBars.value
  return barLabels.value.map((text: string, i: number) => ({ text, x: bars[i] ? bars[i].x + bars[i].w / 2 : 0 }))
})

/* ---------- 雷达图 ---------- */
const radarIndicators = computed<{ name: string; max: number }[]>(() =>
  (props.data?.indicators || []).map((it: any) => ({ name: it.name ?? '', max: Number(it.max) || 1 }))
)
const radarValues = computed<number[]>(() => (props.data?.values || []).map((v: any) => Number(v) || 0))
const radarTotal = computed<number>(() => radarValues.value.reduce((s, v) => s + v, 0))
const radarCx = computed<number>(() => W / 2)
const radarCy = computed<number>(() => props.height / 2 + 4)
const radarR = computed<number>(() => Math.min(W, props.height) / 2 - 44)
const radarAngle = (i: number): number => -Math.PI / 2 + (i * Math.PI * 2) / (radarIndicators.value.length || 1)
const radarPointAt = (i: number, ratio: number) => ({
  x: radarCx.value + radarR.value * ratio * Math.cos(radarAngle(i)),
  y: radarCy.value + radarR.value * ratio * Math.sin(radarAngle(i)),
})
const radarAxes = computed(() => radarIndicators.value.map((_, i) => radarPointAt(i, 1)))
const radarGrids = computed(() =>
  [0.25, 0.5, 0.75, 1].map((ratio) =>
    radarIndicators.value.map((_, i) => {
      const p = radarPointAt(i, ratio)
      return `${p.x},${p.y}`
    }).join(' ')
  )
)
const radarPoints = computed(() =>
  radarValues.value.map((v, i) => {
    const max = radarIndicators.value[i]?.max || 1
    return radarPointAt(i, Math.max(0, Math.min(1, v / max)))
  })
)
const radarPolygon = computed<string>(() => radarPoints.value.map((p) => `${p.x},${p.y}`).join(' '))
const radarLabels = computed(() =>
  radarIndicators.value.map((it, i) => {
    const p = radarPointAt(i, 1.18)
    return { text: it.name, x: p.x, y: p.y + 4 }
  })
)

/* ---------- 热力图 ---------- */
const heatLeft = 48
const heatXLabelsRaw = computed<string[]>(() => props.data?.xLabels || [])
const heatYLabelsRaw = computed<string[]>(() => props.data?.yLabels || [])
const heatValues = computed<number[][]>(() => props.data?.values || [])
const heatMax = computed<number>(() => {
  let m = 0
  heatValues.value.forEach((row) => row.forEach((v) => { if (Number(v) > m) m = Number(v) }))
  return m
})
const heatColor = (v: number): string => {
  const max = heatMax.value
  if (max <= 0) return 'rgb(238,243,248)'
  const t = Math.max(0, Math.min(1, v / max))
  return `rgb(${Math.round(238 + (64 - 238) * t)},${Math.round(245 + (120 - 245) * t)},${Math.round(250 + (220 - 250) * t)})`
}
const heatCells = computed(() => {
  const rows = heatYLabelsRaw.value.length
  const cols = heatXLabelsRaw.value.length
  if (!rows || !cols) return []
  const top = 16
  const plotW = W - heatLeft - 16
  const plotH = props.height - top - 30
  const cw = plotW / cols
  const ch = plotH / rows
  const cells: any[] = []
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const v = Number(heatValues.value[r]?.[c] ?? 0)
      cells.push({
        x: heatLeft + c * cw + 2,
        y: top + r * ch + 2,
        w: Math.max(2, cw - 4),
        h: Math.max(2, ch - 4),
        fill: heatColor(v),
      })
    }
  }
  return cells
})
const heatYLabels = computed(() => {
  const rows = heatYLabelsRaw.value.length
  if (!rows) return []
  const top = 16
  const plotH = props.height - top - 30
  const ch = plotH / rows
  return heatYLabelsRaw.value.map((text, r) => ({ text, y: top + r * ch + ch / 2 + 4 }))
})
const heatXLabels = computed(() => {
  const cols = heatXLabelsRaw.value.length
  if (!cols) return []
  const plotW = W - heatLeft - 16
  const cw = plotW / cols
  return heatXLabelsRaw.value.map((text, c) => ({ text, x: heatLeft + c * cw + cw / 2 }))
})
</script>

<style scoped>
.svg-chart {
  width: 100%;
}
.chart-svg {
  width: 100%;
  height: auto;
  display: block;
  overflow: visible;
}
.chart-label {
  font-size: 11px;
  fill: #606266;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
}
.chart-axis {
  font-size: 10px;
  fill: #909399;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
}
.chart-grid {
  stroke: #ebeef5;
  stroke-width: 1;
}
.chart-average {
  stroke: #E6A23C;
  stroke-width: 1.5;
  opacity: 0.85;
}
.chart-average-label {
  font-size: 10px;
  fill: #E6A23C;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
}
.chart-anomaly {
  font-size: 10px;
  fill: #F56C6C;
  font-weight: 600;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
}
.chart-empty {
  font-size: 13px;
  fill: #c0c4cc;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
}
</style>
