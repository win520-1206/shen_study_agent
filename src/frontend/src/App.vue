<script setup lang="ts">
import { reactive } from 'vue'
import type { ProfileBuildResponse } from './types'
import { createStudent, buildProfile, buildProfileStream } from './composables/useApi'

import HeroBanner from './components/HeroBanner.vue'
import PresetSelector from './components/PresetSelector.vue'
import ProfileCard from './components/ProfileCard.vue'
import DiagnosisPanel from './components/DiagnosisPanel.vue'
import AgentPipeline from './components/AgentPipeline.vue'
import ResourceCards from './components/ResourceCards.vue'
import StudyPath from './components/StudyPath.vue'
import QAPanel from './components/QAPanel.vue'
import AssessmentHistory from './components/AssessmentHistory.vue'
import AssessmentSubmit from './components/AssessmentSubmit.vue'
import RecommendationSummary from './components/RecommendationSummary.vue'
import OverviewPanel from './components/OverviewPanel.vue'

const state = reactive({
  studentId: 0,
  studentName: '',
  loading: false,
  error: '',
  streamMode: false,
  demoMode: true,
  refreshKey: 0,
  result: null as ProfileBuildResponse | null,
})

async function handleStart(name: string, major: string, message: string) {
  state.loading = true
  state.error = ''
  state.result = null
  state.studentId = 0
  try {
    const student = await createStudent(name, major)
    state.studentId = student.id
    state.studentName = student.name

    if (state.streamMode) {
      // SSE streaming mode
      state.result = {
        student: { id: student.id, name: student.name, major: student.major, target_course: student.target_course, profile: null },
        diagnosis: {},
        resources: [],
        study_plan: [],
        traces: [],
        recommendation_summary: '',
        credibility: null,
      }
      await buildProfileStream(student.id, message, {
        onProfile(data) { if (state.result) state.result.student = data.student },
        onDiagnosis(data) { if (state.result) state.result.diagnosis = data },
        onTraces(data) { if (state.result) state.result.traces = data },
        onResource(data) { if (state.result) state.result.resources.push(data) },
        onPlan(data) { if (state.result) state.result.study_plan = data.study_plan },
        onDone() { state.loading = false },
        onError(msg) { state.error = msg; state.loading = false },
      })
    } else {
      // Normal mode
      state.result = await buildProfile(student.id, message)
    }
    state.refreshKey += 1
  } catch (err: any) {
    state.error = err?.response?.data?.detail || err?.message || '请求失败，请确认后端已启动。'
  } finally {
    state.loading = false
  }
}
</script>

<template>
  <div class="app-shell">
    <!-- Top navigation bar -->
    <nav class="top-nav">
      <span class="nav-logo">LearnMate-AI</span>
      <div class="nav-tags">
        <span class="nav-tag">多智能体系统</span>
        <span class="nav-tag accent">机器学习基础</span>
      </div>
    </nav>

    <main class="main-content">
      <HeroBanner />
      <!-- Stream mode toggle -->
      <div class="stream-toggle">
        <label class="toggle-label">
          <input type="checkbox" v-model="state.streamMode" />
          <span class="toggle-text">流式输出模式 {{ state.streamMode ? '(SSE)' : '(标准)' }}</span>
        </label>
        <label class="toggle-label">
          <input type="checkbox" v-model="state.demoMode" />
          <span class="toggle-text">演示模式 {{ state.demoMode ? '(已开启)' : '(已关闭)' }}</span>
        </label>
      </div>

      <PresetSelector :loading="state.loading" @start="handleStart" />

      <!-- Error message -->
      <div class="error-banner" v-if="state.error">
        <span>{{ state.error }}</span>
      </div>

      <!-- Loading indicator -->
      <div class="loading-banner glass-card" v-if="state.loading">
        <div class="spinner"></div>
        <span>6 个智能体正在协作生成个性化方案，请稍候...</span>
      </div>

      <!-- Results -->
      <template v-if="state.result">
        <RecommendationSummary
          :summary="state.result.recommendation_summary"
          :credibility="state.result.credibility"
          :demo-mode="state.demoMode"
        />

        <!-- Profile + Diagnosis side by side -->
        <div class="duo-grid section">
          <ProfileCard
            :profile="state.result.student.profile"
            :name="state.studentName"
          />
          <DiagnosisPanel :diagnosis="state.result.diagnosis" />
        </div>

        <AgentPipeline :traces="state.result.traces" />
        <ResourceCards :resources="state.result.resources" />
        <StudyPath :plan="state.result.study_plan" />

        <!-- Week 4: QA + Assessment -->
        <QAPanel :student-id="state.studentId" />
        <AssessmentSubmit :student-id="state.studentId" @submitted="() => { state.refreshKey += 1 }" />
        <AssessmentHistory :student-id="state.studentId" />
      </template>

      <OverviewPanel :refresh-key="state.refreshKey" />
    </main>

    <footer class="app-footer">
      <span>LearnMate-AI &copy; 2026 &mdash; 基于大模型的个性化学习多智能体系统</span>
    </footer>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* -- Top nav -- */
.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 28px;
  background: rgba(10, 14, 26, 0.85);
  border-bottom: 1px solid var(--border-card);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-logo {
  font-size: 18px;
  font-weight: 800;
  background: linear-gradient(135deg, #00d4ff, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-tags {
  display: flex;
  gap: 8px;
}

.nav-tag {
  padding: 3px 10px;
  border-radius: var(--radius-pill);
  font-size: 11px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
  border: 1px solid var(--border-card);
}

.nav-tag.accent {
  background: rgba(0, 212, 255, 0.08);
  color: var(--color-primary);
  border-color: rgba(0, 212, 255, 0.2);
}

/* -- Main content -- */
.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px 48px;
}

/* -- Duo grid -- */
.duo-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* -- Error -- */
.error-banner {
  padding: 12px 18px;
  border-radius: var(--radius-md);
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: #f87171;
  font-size: 14px;
  margin-bottom: 20px;
}

/* -- Loading -- */
.loading-banner {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
  font-size: 14px;
  color: var(--color-primary);
}

.spinner {
  width: 22px;
  height: 22px;
  border: 3px solid rgba(0, 212, 255, 0.2);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* -- Stream toggle -- */
.stream-toggle {
  margin-bottom: 16px;
}

.toggle-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
}

.toggle-label input[type="checkbox"] {
  accent-color: var(--color-primary);
  width: 16px;
  height: 16px;
}

.toggle-text {
  font-weight: 600;
}

/* -- Footer -- */
.app-footer {
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: var(--text-muted);
  border-top: 1px solid var(--border-card);
}

@media (max-width: 900px) {
  .duo-grid {
    grid-template-columns: 1fr;
  }

  .nav-tags {
    display: none;
  }
}
</style>
