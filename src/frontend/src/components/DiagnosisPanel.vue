<script setup lang="ts">
import KnowledgeGraph from './KnowledgeGraph.vue'

const props = defineProps<{
  diagnosis: Record<string, any> | null
}>()
</script>

<template>
  <div class="diag-card glass-card" v-if="props.diagnosis">
    <h3 class="section-title">诊断结果</h3>

    <div class="diag-grid">
      <div class="diag-item">
        <span class="diag-label">当前阶段</span>
        <span class="badge">{{ props.diagnosis.current_stage }}</span>
      </div>

      <div class="diag-item">
        <span class="diag-label">优先模块</span>
        <div class="module-tags">
          <span
            v-for="mod in props.diagnosis.priority_modules"
            :key="mod"
            class="chip chip--blue"
          >{{ mod }}</span>
        </div>
      </div>

      <div class="diag-item">
        <span class="diag-label">推荐策略</span>
        <p class="diag-text">{{ props.diagnosis.recommended_strategy }}</p>
      </div>

      <div class="diag-item">
        <span class="diag-label">重点知识点</span>
        <span class="chip chip--green">{{ props.diagnosis.focus_knowledge_unit }}</span>
      </div>

      <div class="diag-item" v-if="props.diagnosis.risk_alert">
        <span class="diag-label">风险提示</span>
        <div class="risk-box">
          <span class="risk-icon">⚠️</span>
          <span>{{ props.diagnosis.risk_alert }}</span>
        </div>
      </div>
    </div>

    <KnowledgeGraph :weak-points="props.diagnosis.weak_points || []" />
  </div>

  <div class="diag-card glass-card empty-state" v-else>
    <p>尚无诊断数据</p>
  </div>
</template>

<style scoped>
.diag-card {
  position: relative;
  overflow: hidden;
}

.diag-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, var(--color-success), var(--color-primary));
  border-radius: 2px 0 0 2px;
}

.diag-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.diag-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.diag-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.diag-text {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.7;
}

.module-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.risk-box {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.2);
  font-size: 13px;
  color: var(--color-warning);
  line-height: 1.6;
}

.risk-icon {
  flex-shrink: 0;
  font-size: 16px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80px;
}

.empty-state p {
  color: var(--text-muted);
  font-size: 14px;
}
</style>
