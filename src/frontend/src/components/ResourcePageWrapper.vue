<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import { appState } from '../store'
import type { ResourceCard } from '../types'

const props = defineProps<{
  resourceType: string
  title: string
  icon: string
}>()

const resources = computed<ResourceCard[]>(() => {
  if (!appState.result) return []
  return appState.result.resources.filter(r => r.resource_type === props.resourceType)
})

const profile = computed(() => appState.result?.student?.profile ?? null)

function renderMd(content: string): string {
  return marked.parse(content) as string
}
</script>

<template>
  <div class="resource-page">
    <div class="page-header">
      <span class="page-icon">{{ icon }}</span>
      <h1 class="page-title">{{ title }}</h1>
    </div>

    <div class="profile-summary glass-card" v-if="profile">
      <span class="summary-item"><strong>{{ appState.studentName }}</strong></span>
      <span class="summary-sep">|</span>
      <span class="summary-item">目标：{{ profile.learning_goal }}</span>
      <span class="summary-sep">|</span>
      <span class="summary-item">基础：{{ profile.prerequisite_level }}</span>
      <span class="summary-sep">|</span>
      <span class="summary-item">风格：{{ profile.learning_style }}</span>
    </div>

    <div v-if="resources.length === 0" class="empty-state glass-card">
      <p class="empty-icon">📭</p>
      <p>还没有生成{{ title }}，请先到首页生成个性化学习方案。</p>
    </div>

    <article
      v-for="res in resources"
      :key="res.title"
      class="resource-card glass-card"
    >
      <h2 class="res-title">{{ res.title }}</h2>
      <div class="md-body" v-html="renderMd(res.content)"></div>
      <div class="res-refs" v-if="res.source_refs.length">
        <span class="refs-label">来源</span>
        <span v-for="ref in res.source_refs" :key="ref" class="ref-tag">{{ ref }}</span>
      </div>
    </article>
  </div>
</template>

<style scoped>
.resource-page {
  max-width: 960px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.page-icon {
  font-size: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, #00d4ff, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.profile-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 12px 18px;
  margin-bottom: 20px;
  font-size: 13px;
  color: var(--text-secondary);
}

.summary-sep {
  color: var(--border-card);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.resource-card {
  margin-bottom: 20px;
}

.res-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 16px;
}

.res-refs {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border-card);
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
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
</style>
