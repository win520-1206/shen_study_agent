<script setup lang="ts">
import type { CredibilityInfo } from '../types'

const props = defineProps<{
  summary: string
  credibility: CredibilityInfo | null
  demoMode: boolean
}>()
</script>

<template>
  <section class="section" v-if="props.summary || props.credibility">
    <h2 class="section-title">本轮推荐依据</h2>
    <div class="summary-grid">
      <article class="glass-card summary-card">
        <div class="summary-top">
          <span class="badge">系统为什么这样推荐</span>
          <span v-if="props.demoMode" class="demo-flag">演示模式</span>
        </div>
        <p class="summary-text">
          {{ props.summary || '系统会结合画像、诊断和历史评估结果生成推荐依据。' }}
        </p>
      </article>

      <article class="glass-card trust-card" v-if="props.credibility">
        <h3 class="trust-title">内容可信度说明</h3>
        <div class="trust-list">
          <div class="trust-item">
            <span class="trust-label">知识库驱动</span>
            <span class="chip" :class="props.credibility.based_on_kb ? 'chip--green' : 'chip--orange'">
              {{ props.credibility.based_on_kb ? '是' : '否' }}
            </span>
          </div>
          <div class="trust-item">
            <span class="trust-label">审查智能体检查</span>
            <span class="chip" :class="props.credibility.reviewed ? 'chip--green' : 'chip--orange'">
              {{ props.credibility.reviewed ? '已完成' : '待检查' }}
            </span>
          </div>
          <div class="trust-item">
            <span class="trust-label">来源模块</span>
            <div class="trust-tags">
              <span
                v-for="module in props.credibility.source_modules"
                :key="module"
                class="chip chip--blue"
              >
                {{ module }}
              </span>
            </div>
          </div>
        </div>
        <p class="trust-note">{{ props.credibility.note }}</p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
}

.summary-card,
.trust-card {
  min-height: 100%;
}

.summary-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.demo-flag {
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  font-size: 11px;
  font-weight: 700;
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.24);
  background: rgba(245, 158, 11, 0.08);
}

.summary-text {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-primary);
}

.trust-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 14px;
}

.trust-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trust-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.trust-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 700;
  letter-spacing: 0.04em;
}

.trust-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.trust-note {
  margin-top: 14px;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.7;
}

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
