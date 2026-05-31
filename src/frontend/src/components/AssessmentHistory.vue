<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { getAssessments } from '../composables/useApi'
import type { AssessmentHistoryResponse } from '../types'

const props = defineProps<{
  studentId: number
}>()

const data = ref<AssessmentHistoryResponse | null>(null)

async function load() {
  if (props.studentId) {
    try { data.value = await getAssessments(props.studentId) } catch { /* no data yet */ }
  }
}

onMounted(load)
watch(() => props.studentId, load)

function trendIcon(t: string) {
  if (t === '上升') return '↑'
  if (t === '下降') return '↓'
  return '→'
}

function trendClass(t: string) {
  if (t === '上升') return 'up'
  if (t === '下降') return 'down'
  return ''
}
</script>

<template>
  <section class="section" v-if="data && data.records.length">
    <h2 class="section-title">学习效果评估</h2>

    <div class="weak-bar" v-if="data.weak_points.length">
      <span class="weak-label">⚠ 持续薄弱知识点：</span>
      <span v-for="wp in data.weak_points" :key="wp.knowledge_unit" class="chip chip--orange">
        {{ wp.knowledge_unit }} (avg {{ wp.avg_score }})
      </span>
    </div>

    <div class="summary-panel glass-card">
      <div class="summary-col">
        <span class="summary-label">阶段成长总结</span>
        <p>{{ data.progress_summary }}</p>
      </div>
      <div class="summary-col" v-if="data.improvement_points.length">
        <span class="summary-label">进步知识点</span>
        <div class="summary-tags">
          <span
            v-for="item in data.improvement_points"
            :key="item.knowledge_unit"
            class="chip chip--green"
          >
            {{ item.knowledge_unit }}
          </span>
        </div>
      </div>
    </div>

    <div class="assess-table glass-card">
      <div class="assess-row assess-header">
        <span>知识点</span>
        <span>分数</span>
        <span>趋势</span>
        <span>反馈</span>
      </div>
      <div v-for="(rec, idx) in data.records" :key="idx" class="assess-row">
        <span class="assess-unit">{{ rec.knowledge_unit }}</span>
        <span class="assess-score" :class="{ low: rec.score < 70 }">{{ rec.score }}</span>
        <span class="assess-trend" :class="trendClass(data.trend[rec.knowledge_unit] || '')">
          {{ trendIcon(data.trend[rec.knowledge_unit] || '首次') }} {{ data.trend[rec.knowledge_unit] || '首次' }}
        </span>
        <span class="assess-fb">{{ rec.feedback }}</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.weak-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.summary-panel {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 16px;
  margin-bottom: 14px;
}

.summary-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-col p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.summary-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
}

.summary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.weak-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-warning);
}

.assess-table {
  overflow-x: auto;
}

.assess-row {
  display: grid;
  grid-template-columns: 140px 70px 80px 1fr;
  gap: 12px;
  padding: 10px 0;
  align-items: center;
  border-bottom: 1px solid var(--border-card);
  font-size: 13px;
}

.assess-row:last-child {
  border-bottom: none;
}

.assess-header {
  font-weight: 700;
  color: var(--text-muted);
  font-size: 12px;
  text-transform: uppercase;
}

.assess-score {
  font-weight: 700;
  color: var(--color-success);
}

.assess-score.low {
  color: var(--color-danger);
}

.assess-trend.up {
  color: var(--color-success);
}

.assess-trend.down {
  color: var(--color-danger);
}

.assess-fb {
  color: var(--text-secondary);
}

.assess-unit {
  font-weight: 600;
  color: var(--text-primary);
}

@media (max-width: 900px) {
  .summary-panel {
    grid-template-columns: 1fr;
  }
}
</style>
