<script setup lang="ts">
import { ref } from 'vue'
import { marked } from 'marked'
import { askQuestion } from '../composables/useApi'
import type { QAResponse } from '../types'

const props = defineProps<{
  studentId: number
}>()

const question = ref('')
const socraticMode = ref(false)
const loading = ref(false)
const history = ref<Array<{ q: string; a: QAResponse; socratic: boolean }>>([])

async function handleAsk() {
  const q = question.value.trim()
  if (!q || !props.studentId) return
  loading.value = true
  try {
    const resp = await askQuestion(props.studentId, q, socraticMode.value)
    history.value.push({ q, a: resp, socratic: socraticMode.value })
    question.value = ''
  } catch {
    history.value.push({
      q,
      a: {
        answer: '请求失败，请确认后端已启动。',
        source_refs: [],
        agent_trace: { agent_name: '', input_summary: '', output_summary: '', decision_reason: '', impact_on_result: '' },
      },
      socratic: false,
    })
  } finally {
    loading.value = false
  }
}

function renderMd(s: string) { return marked.parse(s) as string }
</script>

<template>
  <section class="section">
    <h2 class="section-title">智能答疑</h2>
    <div class="qa-card glass-card">
      <div class="qa-history" v-if="history.length">
        <div v-for="(item, idx) in history" :key="idx" class="qa-item">
          <div class="qa-q">
            <span class="qa-icon">💬</span>
            <span>{{ item.q }}</span>
            <span class="socratic-badge" v-if="item.socratic">🧠 苏格拉底模式</span>
          </div>
          <div class="qa-a">
            <span class="qa-icon">✅</span>
            <div class="md-body" v-html="renderMd(item.a.answer)"></div>
          </div>
          <div class="qa-refs" v-if="item.a.source_refs.length">
            <span class="refs-label">来源</span>
            <span v-for="ref in item.a.source_refs" :key="ref" class="ref-tag">{{ ref }}</span>
          </div>
        </div>
      </div>
      <div class="qa-empty" v-else>
        <p>对课程内容有疑问？试试问问！</p>
      </div>
      <div class="qa-controls">
        <label class="socratic-toggle">
          <input type="checkbox" v-model="socraticMode" />
          <span class="toggle-track">
            <span class="toggle-thumb"></span>
          </span>
          <span class="toggle-label">🧠 苏格拉底式追问</span>
          <span class="toggle-hint" v-if="socraticMode">AI 会引导你主动思考</span>
        </label>
      </div>
      <div class="qa-input">
        <el-input
          v-model="question"
          placeholder="请输入问题，例如：什么是过拟合？"
          :disabled="loading || !studentId"
          @keyup.enter="handleAsk"
        />
        <el-button type="primary" :loading="loading" :disabled="!question.trim() || !studentId" @click="handleAsk">发送</el-button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.qa-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.qa-history {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.qa-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.qa-q {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.qa-a {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(0, 212, 255, 0.04);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--color-primary);
}

.qa-icon {
  flex-shrink: 0;
  font-size: 16px;
  margin-top: 2px;
}

.socratic-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-pill);
  background: rgba(124, 58, 237, 0.12);
  color: var(--color-secondary);
}

.qa-refs {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-left: 28px;
}

.refs-label {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 600;
}

.ref-tag {
  font-size: 11px;
  color: var(--text-muted);
  padding: 2px 8px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-card);
}

.qa-controls {
  padding: 0 2px;
}

.socratic-toggle {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.socratic-toggle input[type="checkbox"] {
  display: none;
}

.toggle-track {
  width: 40px;
  height: 22px;
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--border-card);
  position: relative;
  transition: all 0.25s;
}

.toggle-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--text-muted);
  position: absolute;
  top: 2px;
  left: 2px;
  transition: all 0.25s;
}

.socratic-toggle input:checked + .toggle-track {
  background: rgba(124, 58, 237, 0.2);
  border-color: rgba(124, 58, 237, 0.4);
}

.socratic-toggle input:checked + .toggle-track .toggle-thumb {
  left: 20px;
  background: var(--color-secondary);
}

.toggle-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.toggle-hint {
  font-size: 11px;
  color: var(--color-secondary);
  font-weight: 500;
}

.qa-empty p {
  color: var(--text-muted);
  font-size: 14px;
  text-align: center;
  padding: 10px 0;
}

.qa-input {
  display: flex;
  gap: 10px;
}

.qa-input .el-input {
  flex: 1;
}
</style>
