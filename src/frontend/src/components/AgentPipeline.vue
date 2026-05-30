<script setup lang="ts">
import { ref } from 'vue'
import type { TraceCard } from '../types'

const props = defineProps<{
  traces: TraceCard[]
}>()

const expanded = ref(false)

const agentIcons: Record<string, string> = {
  '画像': '👤',
  '诊断': '🔍',
  '资源规划': '📄',
  '内容生成': '✍️',
  '路径规划': '🗺️',
  '审查': '✅',
}

function getShortName(fullName: string): string {
  return fullName
    .replace('智能体', '')
    .replace('(LLM)', '')
    .replace('（LLM）', '')
    .trim()
}

function getIcon(name: string): string {
  for (const [key, icon] of Object.entries(agentIcons)) {
    if (name.includes(key)) return icon
  }
  return '⚙️'
}
</script>

<template>
  <section class="section" v-if="props.traces.length">
    <h2 class="section-title">多智能体协作管线</h2>
    <div class="pipeline glass-card">
      <div class="pipe-track">
        <template v-for="(trace, idx) in props.traces" :key="trace.agent_name">
          <div class="pipe-node">
            <div class="node-circle">
              <span class="node-icon">{{ getIcon(trace.agent_name) }}</span>
            </div>
            <span class="node-name">{{ getShortName(trace.agent_name) }}</span>
            <span class="node-summary">{{ trace.output_summary.slice(0, 30) }}</span>
            <span class="node-impact">{{ trace.impact_on_result.slice(0, 18) }}</span>
          </div>
          <div class="pipe-arrow" v-if="idx < traces.length - 1">
            <svg width="32" height="12" viewBox="0 0 32 12">
              <line x1="0" y1="6" x2="24" y2="6" stroke="rgba(0,212,255,0.4)" stroke-width="2" />
              <polygon points="24,2 32,6 24,10" fill="rgba(0,212,255,0.5)" />
            </svg>
          </div>
        </template>
      </div>

      <button class="expand-btn" @click="expanded = !expanded">
        {{ expanded ? '收起详情' : '查看详情' }}
        <span class="expand-arrow" :class="{ open: expanded }">▼</span>
      </button>

      <div class="trace-details" v-if="expanded">
        <div
          v-for="trace in props.traces"
          :key="trace.agent_name + '-detail'"
          class="trace-row"
        >
          <strong>{{ getShortName(trace.agent_name) }}</strong>
          <div class="trace-io">
            <span class="trace-tag">输入</span> {{ trace.input_summary }}
          </div>
          <div class="trace-io">
            <span class="trace-tag reason">决策</span> {{ trace.decision_reason }}
          </div>
          <div class="trace-io">
            <span class="trace-tag out">输出</span> {{ trace.output_summary }}
          </div>
          <div class="trace-io">
            <span class="trace-tag impact">影响</span> {{ trace.impact_on_result }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.pipeline {
  overflow-x: auto;
}

.pipe-track {
  display: flex;
  align-items: flex-start;
  gap: 0;
  padding: 8px 0 16px;
  min-width: max-content;
}

.pipe-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 90px;
  gap: 6px;
}

.node-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(0, 212, 255, 0.08);
  border: 2px solid rgba(0, 212, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2.5s infinite;
}

.pipe-node:nth-child(odd) .node-circle {
  animation-delay: 0.4s;
}

.node-icon {
  font-size: 20px;
}

.node-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
  white-space: nowrap;
}

.node-summary {
  font-size: 11px;
  color: var(--text-muted);
  text-align: center;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-impact {
  font-size: 10px;
  color: var(--color-primary);
  text-align: center;
  max-width: 110px;
  line-height: 1.4;
}

.pipe-arrow {
  display: flex;
  align-items: center;
  padding-top: 14px;
}

.expand-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding: 6px 14px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-card);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.expand-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.expand-arrow {
  font-size: 10px;
  transition: transform 0.2s;
}

.expand-arrow.open {
  transform: rotate(180deg);
}

.trace-details {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-top: 1px solid var(--border-card);
  padding-top: 16px;
}

.trace-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.trace-row strong {
  font-size: 13px;
  color: var(--color-primary);
}

.trace-io {
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  align-items: flex-start;
  gap: 6px;
}

.trace-tag {
  flex-shrink: 0;
  padding: 1px 8px;
  border-radius: var(--radius-pill);
  font-size: 11px;
  font-weight: 600;
  background: rgba(16, 185, 129, 0.12);
  color: var(--color-success);
}

.trace-tag.out {
  background: rgba(124, 58, 237, 0.12);
  color: var(--color-secondary);
}

.trace-tag.reason {
  background: rgba(59, 130, 246, 0.12);
  color: var(--color-lesson);
}

.trace-tag.impact {
  background: rgba(0, 212, 255, 0.12);
  color: var(--color-primary);
}

@media (max-width: 900px) {
  .pipe-track {
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
  }

  .pipe-arrow {
    display: none;
  }
}
</style>
