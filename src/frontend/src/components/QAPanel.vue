<script setup lang="ts">
import { ref } from 'vue'
import { marked } from 'marked'
import { askQuestion } from '../composables/useApi'
import type { QAResponse } from '../types'

const props = defineProps<{
  studentId: number
}>()

const question = ref('')
const suggestedQuestions = ['什么是线性回归？', '逻辑回归和线性回归有什么区别？', '什么是过拟合？', '决策树的优缺点是什么？']
const loading = ref(false)
const history = ref<Array<{ q: string; a: QAResponse }>>([])

async function handleAsk() {
  const q = question.value.trim()
  if (!q || !props.studentId) return
  loading.value = true
  try {
    const resp = await askQuestion(props.studentId, q)
    history.value.push({ q, a: resp })
    question.value = ''
  } catch {
    history.value.push({ q, a: { answer: '请求失败，请确认后端已启动。', source_refs: [], agent_trace: { agent_name: '', input_summary: '', output_summary: '' } } })
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
            <span class="qa-icon">❓</span>
            <span>{{ item.q }}</span>
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
      <div class="qa-input">
        <el-input
          v-model="question"
          placeholder="请输入问题，例如：什么是线性回归？"
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
  align-items: flex-start;
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

.suggested {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.suggested-label {
  font-size: 12px;
  color: var(--text-muted);
}

.suggested-btn {
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  background: rgba(0, 212, 255, 0.08);
  border: 1px solid rgba(0, 212, 255, 0.15);
  color: var(--color-primary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.suggested-btn:hover {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.3);
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
