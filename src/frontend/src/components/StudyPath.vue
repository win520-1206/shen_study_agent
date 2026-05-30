<script setup lang="ts">
import type { StudyPlan } from '../types'

const props = defineProps<{
  plan: StudyPlan[]
}>()
</script>

<template>
  <section class="section" v-if="props.plan.length">
    <h2 class="section-title">学习路径</h2>
    <div class="steps">
      <div
        v-for="(step, idx) in props.plan"
        :key="step.stage"
        class="step-item fade-in-up"
      >
        <div class="step-left">
          <div class="step-num">{{ idx + 1 }}</div>
          <div class="step-line" v-if="idx < plan.length - 1"></div>
        </div>
        <div class="step-body glass-card">
          <h3 class="step-title">{{ step.stage }}</h3>

          <div class="step-section">
            <span class="step-label">目标</span>
            <ul class="obj-list">
              <li v-for="obj in step.objectives" :key="obj">{{ obj }}</li>
            </ul>
          </div>

          <div class="step-section">
            <span class="step-label">推荐资源</span>
            <div class="res-tags">
              <span v-for="r in step.recommended_resources" :key="r" class="chip chip--blue">{{ r }}</span>
            </div>
          </div>

          <div class="step-section">
            <span class="step-label">实践任务</span>
            <p class="task-text">{{ step.practice_task }}</p>
          </div>

          <div class="step-section" v-if="step.rationale">
            <span class="step-label">为什么先学这一步</span>
            <p class="rationale-text">{{ step.rationale }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.steps {
  display: flex;
  flex-direction: column;
}

.step-item {
  display: flex;
  gap: 16px;
}

.step-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  width: 36px;
}

.step-num {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  color: #fff;
  font-size: 15px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-line {
  width: 2px;
  flex: 1;
  min-height: 20px;
  background: linear-gradient(180deg, var(--color-primary), rgba(124, 58, 237, 0.3));
  margin: 4px 0;
  border-radius: 1px;
}

.step-body {
  flex: 1;
  margin-bottom: 16px;
}

.step-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 14px;
}

.step-section {
  margin-bottom: 12px;
}

.step-section:last-child {
  margin-bottom: 0;
}

.step-label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 6px;
}

.obj-list {
  padding-left: 18px;
  margin: 0;
}

.obj-list li {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.7;
}

.res-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.task-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
  padding: 8px 12px;
  background: rgba(0, 212, 255, 0.04);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--color-primary);
}

.rationale-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
  padding: 8px 12px;
  background: rgba(124, 58, 237, 0.05);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--color-secondary);
}
</style>
