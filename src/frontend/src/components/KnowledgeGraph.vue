<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import * as echarts from 'echarts'
import VChart from 'vue-echarts'
import { getKnowledgeGraph } from '../composables/useApi'
import type { KnowledgeGraphData } from '../types'

const props = defineProps<{
  weakPoints?: string[]
}>()

const graphData = ref<KnowledgeGraphData | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    graphData.value = await getKnowledgeGraph()
  } catch {
    graphData.value = null
  } finally {
    loading.value = false
  }
})

function resolveWeakIds(weakPoints: string[]): Set<string> {
  const ids = new Set<string>()
  if (!graphData.value || !weakPoints) return ids
  const map = graphData.value.module_map
  for (const wp of weakPoints) {
    if (map[wp]) ids.add(map[wp])
  }
  return ids
}

function findUpstream(targetId: string, edges: KnowledgeGraphData['edges']): Set<string> {
  const upstream = new Set<string>()
  const queue = [targetId]
  while (queue.length) {
    const current = queue.shift()!
    for (const edge of edges) {
      if (edge.to === current && !upstream.has(edge.from)) {
        upstream.add(edge.from)
        queue.push(edge.from)
      }
    }
  }
  return upstream
}

const chartOption = computed(() => {
  if (!graphData.value) return {}
  const { nodes, edges } = graphData.value
  const weakIds = resolveWeakIds(props.weakPoints || [])

  // Collect upstream of weak points
  const upstreamIds = new Set<string>()
  for (const wid of weakIds) {
    for (const uid of findUpstream(wid, edges)) {
      upstreamIds.add(uid)
    }
  }

  // Build ECharts graph data
  const levelY = [0, 150, 300, 450]
  const levelCounts: Record<number, number> = {}
  const nodePositions: Record<string, { x: number; y: number }> = {}

  for (const n of nodes) {
    const count = levelCounts[n.level] || 0
    levelCounts[n.level] = count + 1
  }

  const levelIndex: Record<number, number> = {}
  for (const n of nodes) {
    const idx = levelIndex[n.level] || 0
    levelIndex[n.level] = idx + 1
    const total = levelCounts[n.level]
    const spacing = 200
    const startX = -((total - 1) * spacing) / 2
    nodePositions[n.id] = { x: startX + idx * spacing, y: levelY[n.level - 1] || 0 }
  }

  const graphNodes = nodes.map((n) => {
    const isWeak = weakIds.has(n.id)
    const isUpstream = upstreamIds.has(n.id)
    let color = '#334155'
    let borderColor = 'rgba(0, 212, 255, 0.3)'
    let borderWidth = 2
    let size = 40
    let fontColor = '#e2e8f0'

    if (isWeak) {
      color = 'rgba(239, 68, 68, 0.2)'
      borderColor = '#f87171'
      borderWidth = 3
      size = 50
      fontColor = '#f87171'
    } else if (isUpstream) {
      color = 'rgba(245, 158, 11, 0.15)'
      borderColor = '#f59e0b'
      borderWidth = 2
      size = 44
      fontColor = '#f59e0b'
    }

    return {
      id: n.id,
      name: n.label,
      x: nodePositions[n.id].x,
      y: nodePositions[n.id].y,
      symbolSize: size,
      itemStyle: { color, borderColor, borderWidth },
      label: { color: fontColor, fontSize: 12, fontWeight: 'bold' },
      tooltip: { formatter: `<b>${n.label}</b><br/>${n.description}<br/>知识点：${n.knowledge_units.join('、')}` },
    }
  })

  const graphEdges = edges.map((e) => ({
    source: e.from,
    target: e.to,
    label: { show: true, formatter: e.label, fontSize: 10, color: '#64748b' },
    lineStyle: {
      color: weakIds.has(e.to) ? 'rgba(248, 113, 113, 0.5)' : 'rgba(0, 212, 255, 0.25)',
      width: weakIds.has(e.to) ? 2.5 : 1.5,
      curveness: 0.1,
    },
  }))

  return {
    tooltip: { trigger: 'item' },
    series: [
      {
        type: 'graph',
        layout: 'none',
        roam: true,
        data: graphNodes,
        links: graphEdges,
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: 8,
        emphasis: {
          focus: 'adjacency',
          lineStyle: { width: 4 },
        },
      },
    ],
  }
})

const hasWeakPoints = computed(() => (props.weakPoints || []).length > 0)
</script>

<template>
  <section class="section" v-if="!loading && graphData">
    <h2 class="section-title">知识图谱 — 学科依赖关系</h2>
    <div class="kg-card glass-card">
      <div class="kg-legend">
        <span class="legend-item"><span class="dot dot-normal"></span>正常模块</span>
        <span class="legend-item" v-if="hasWeakPoints"><span class="dot dot-weak"></span>薄弱模块</span>
        <span class="legend-item" v-if="hasWeakPoints"><span class="dot dot-upstream"></span>前置依赖</span>
      </div>
      <div class="kg-hint" v-if="hasWeakPoints">
        <span class="hint-icon">💡</span>
        <span>系统发现你在 <strong>{{ weakPoints?.join('、') }}</strong> 上较薄弱，建议先巩固图中标记的前置依赖模块。</span>
      </div>
      <div class="kg-chart-wrap">
        <VChart :option="chartOption" autoresize style="height: 420px; width: 100%;" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.kg-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.kg-legend {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: var(--text-secondary);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot-normal {
  background: #334155;
  border: 1.5px solid rgba(0, 212, 255, 0.3);
}

.dot-weak {
  background: rgba(239, 68, 68, 0.3);
  border: 1.5px solid #f87171;
}

.dot-upstream {
  background: rgba(245, 158, 11, 0.2);
  border: 1.5px solid #f59e0b;
}

.kg-hint {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  background: rgba(245, 158, 11, 0.06);
  border: 1px solid rgba(245, 158, 11, 0.2);
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.hint-icon {
  flex-shrink: 0;
}

.kg-chart-wrap {
  border-radius: var(--radius-md);
  overflow: hidden;
  background: rgba(15, 23, 42, 0.5);
}
</style>
