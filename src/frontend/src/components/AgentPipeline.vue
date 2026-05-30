<script setup lang="ts">
import { ref } from 'vue'
import type { TraceCard } from '../types'

const props = defineProps<{
  traces: TraceCard[]
}>()

const expanded = ref(false)

const agentIcons: Record<string, string> = {
  '\u753b\u50cf': '\ud83d\udc64',
  '\u8bca\u65ad': '\ud83d\udd0d',
  '\u8d44\u6e90\u89c4\u5212': '\ud83d\udcdc',
  '\u5185\u5bb9\u751f\u6210': '\u270d\ufe0f',
  '\u8def\u5f84\u89c4\u5212': '\ud83d\uddfa\ufe0f',
  '\u5ba1\u67e5': '\u2705',
}

function getShortName(fullName: string): string {
  return fullName
    .replace('\u667a\u80fd\u4f53', '')
    .replace('(LLM)', '')
    .replace('\uff08LLM\uff09', '')
    .trim()
}

function getIcon(name: string): string {
  for (const [key, icon] of Object.entries(agentIcons)) {
    if (name.includes(key)) return icon
  }
  return '\u2699\ufe0f'
}
</script>

<template>
  <section class="section" v-if="props.traces.length">
    <h2 class="section-title">\u591a\u667a\u80fd\u4f53\u534f\u4f5c\u7ba1\u7ebf</h2>
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
        {{ expanded ? '\u6536\u8d77\u8be6\u60c5' : '\u67e5\u770b\u8be6\u60c5' }}
        <span class="expand-arrow" :class="{ open: expanded }">\u25bc</span>
      </button>

      <div class="trace-details" v-if="expanded">
        <div
          v-for="trace in props.traces"
          :key="trace.agent_name + '-detail'"
          class="trace-row"
        >
          <strong>{{ getShortName(trace.agent_name) }}</strong>
          <div class="trace-io">
            <span class="trace-tag">\u8f93\u5165</span> {{ trace.input_summary }}
          </div>
          <div class="trace-io">
            <span class="trace-tag reason">决策</span> {{ trace.decision_reason }}
          </div>
          <div class="trace-io">
            <span class="trace-tag out">\u8f93\u51fa</span> {{ trace.output_summary }}
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
