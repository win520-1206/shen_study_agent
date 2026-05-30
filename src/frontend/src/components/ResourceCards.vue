<script setup lang="ts">
import { marked } from 'marked'
import type { ResourceCard } from '../types'

const props = defineProps<{
  resources: ResourceCard[]
}>()

const typeConfig: Record<string, { icon: string; colorVar: string; label: string }> = {
  lesson_note: { icon: '📖', colorVar: '--color-lesson', label: '讲义' },
  quiz: { icon: '✅', colorVar: '--color-quiz', label: '练习题' },
  coding_case: { icon: '💻', colorVar: '--color-coding', label: '代码案例' },
  mind_map: { icon: '🧠', colorVar: '--color-mindmap', label: '思维导图' },
  study_path: { icon: '📋', colorVar: '--color-path', label: '学习路径' },
}

function getConfig(type: string) {
  return typeConfig[type] || { icon: '⚙️', colorVar: '--color-primary', label: type }
}

function renderMd(content: string): string {
  return marked.parse(content) as string
}
</script>

<template>
  <section class="section" v-if="props.resources.length">
    <h2 class="section-title">个性化学习资源</h2>
    <div class="res-grid">
      <article
        v-for="res in props.resources"
        :key="res.title"
        class="res-card glass-card fade-in-up"
      >
        <div class="res-top">
          <span
            class="res-type-pill"
            :style="{
              background: `color-mix(in srgb, var(${getConfig(res.resource_type).colorVar}) 15%, transparent)`,
              color: `var(${getConfig(res.resource_type).colorVar})`,
              borderColor: `color-mix(in srgb, var(${getConfig(res.resource_type).colorVar}) 25%, transparent)`,
            }"
          >
            {{ getConfig(res.resource_type).icon }} {{ getConfig(res.resource_type).label }}
          </span>
          <h3 class="res-title">{{ res.title }}</h3>
        </div>
        <div class="md-body" v-html="renderMd(res.content)"></div>
        <div class="res-refs" v-if="res.source_refs.length">
          <span class="refs-label">来源</span>
          <span v-for="ref in res.source_refs" :key="ref" class="ref-tag">{{ ref }}</span>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.res-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
}

.res-card {
  transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
  position: relative;
  overflow: hidden;
}

.res-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--color-primary);
  border-radius: 2px 0 0 2px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.res-card:hover {
  transform: translateY(-4px);
  border-color: rgba(0, 212, 255, 0.25);
  box-shadow: 0 8px 30px rgba(0, 212, 255, 0.08);
}

.res-card:hover::before {
  opacity: 1;
}

.res-top {
  margin-bottom: 12px;
}

.res-type-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 700;
  border: 1px solid;
  margin-bottom: 8px;
}

.res-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
}

.res-refs {
  margin-top: 14px;
  padding-top: 10px;
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

@media (max-width: 700px) {
  .res-grid {
    grid-template-columns: 1fr;
  }
}
</style>
