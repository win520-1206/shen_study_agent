<script setup lang="ts">
import { marked } from 'marked'
import type { ResourceCard } from '../types'

const props = defineProps<{
  resources: ResourceCard[]
}>()

const typeConfig: Record<string, { icon: string; colorVar: string; label: string }> = {
  lesson_note: { icon: '\ud83d\udcd6', colorVar: '--color-lesson', label: '\u8bb2\u4e49' },
  quiz: { icon: '\u2705', colorVar: '--color-quiz', label: '\u7ec3\u4e60\u9898' },
  coding_case: { icon: '\ud83d\udcbb', colorVar: '--color-coding', label: '\u4ee3\u7801\u6848\u4f8b' },
  mind_map: { icon: '\ud83e\udde0', colorVar: '--color-mindmap', label: '\u601d\u7ef4\u5bfc\u56fe' },
  study_path: { icon: '\ud83d\udccb', colorVar: '--color-path', label: '\u5b66\u4e60\u8def\u5f84' },
}

function getConfig(type: string) {
  return typeConfig[type] || { icon: '\u2699\ufe0f', colorVar: '--color-primary', label: type }
}

function renderMd(content: string): string {
  return marked.parse(content) as string
}
</script>

<template>
  <section class="section" v-if="props.resources.length">
    <h2 class="section-title">\u4e2a\u6027\u5316\u5b66\u4e60\u8d44\u6e90</h2>
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
          <span class="refs-label">\u6765\u6e90</span>
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
