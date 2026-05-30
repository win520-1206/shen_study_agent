<script setup lang="ts">
import type { StudentProfile } from '../types'

const props = defineProps<{
  profile: StudentProfile | null
  name: string
}>()

const dimLabels: Record<string, string> = {
  major_background: '专业背景',
  learning_goal: '学习目标',
  prerequisite_level: '基础水平',
  weak_points: '薄弱知识点',
  learning_style: '学习风格',
  weekly_hours: '每周投入',
  exercise_preference: '练习偏好',
  target_outcome: '期望结果',
}

const highlightKeys = ['learning_goal', 'learning_style']
const warnKeys = ['weak_points']
</script>

<template>
  <div class="profile-card glass-card" v-if="props.profile">
    <div class="profile-header">
      <h3 class="section-title">学生画像</h3>
      <span class="badge">{{ props.name }}</span>
    </div>
    <div class="dims">
      <div
        v-for="(label, key) in dimLabels"
        :key="key"
        class="dim-row"
      >
        <span class="dim-label">{{ label }}</span>
        <div class="dim-values">
          <template v-if="Array.isArray((props.profile as any)[key])">
            <span
              v-for="val in (props.profile as any)[key]"
              :key="val"
              class="chip"
              :class="{
                'chip--orange': warnKeys.includes(key),
                'chip--green': highlightKeys.includes(key),
              }"
            >{{ val }}</span>
          </template>
          <span
            v-else
            class="chip"
            :class="{
              'chip--green': highlightKeys.includes(key),
            }"
          >{{ (props.profile as any)[key] }}</span>
        </div>
      </div>
    </div>
  </div>

  <div class="profile-card glass-card empty-state" v-else>
    <p>尚无画像数据，请先输入学习诉求并生成。</p>
  </div>
</template>

<style scoped>
.profile-card {
  position: relative;
  overflow: hidden;
}

.profile-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, var(--color-primary), var(--color-secondary));
  border-radius: 2px 0 0 2px;
}

.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.dims {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dim-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.dim-label {
  flex-shrink: 0;
  width: 80px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  padding-top: 5px;
  text-align: right;
}

.dim-values {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
}

.empty-state p {
  color: var(--text-muted);
  font-size: 14px;
}
</style>
