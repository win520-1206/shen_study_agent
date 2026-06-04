<script setup lang="ts">
import { onMounted } from 'vue'
import { appState, persistStudent } from '../store'
import { createStudent, buildProfile, buildProfileStream, getDashboard } from '../composables/useApi'

import HeroBanner from '../components/HeroBanner.vue'
import PresetSelector from '../components/PresetSelector.vue'
import ProfileCard from '../components/ProfileCard.vue'
import DiagnosisPanel from '../components/DiagnosisPanel.vue'
import AgentPipeline from '../components/AgentPipeline.vue'
import ResourceCards from '../components/ResourceCards.vue'
import StudyPath from '../components/StudyPath.vue'
import QAPanel from '../components/QAPanel.vue'
import AssessmentHistory from '../components/AssessmentHistory.vue'
import RecommendationSummary from '../components/RecommendationSummary.vue'
import OverviewPanel from '../components/OverviewPanel.vue'


// Restore data on page load if studentId exists (from localStorage)
onMounted(async () => {
  if (appState.studentId > 0 && !appState.result) {
    try {
      const dashboard = await getDashboard(appState.studentId)
      appState.result = {
        student: dashboard.student,
        diagnosis: dashboard.latest_diagnosis,
        resources: dashboard.resources,
        study_plan: dashboard.latest_plan,
        traces: dashboard.traces,
        recommendation_summary: dashboard.recommendation_summary,
        credibility: null,
      }
      appState.studentName = dashboard.student.name
      appState.refreshKey += 1
    } catch {
      appState.studentId = 0
      appState.studentName = ''
    }
  }
})

async function handleStart(name: string, major: string, message: string, presetKey?: string) {
  appState.loading = true
  appState.error = ''
  appState.result = null
  try {
    let studentId = appState.studentId
    let studentName = appState.studentName
    if (studentId <= 0) {
      const student = await createStudent(name, major)
      studentId = student.id
      studentName = student.name
      persistStudent(studentId, studentName)
    }
    appState.studentId = studentId
    appState.studentName = studentName

    if (appState.streamMode) {
      appState.result = {
        student: { id: studentId, name: studentName, major: major, target_course: '机器学习基础', profile: null },
        diagnosis: {},
        resources: [],
        study_plan: [],
        traces: [],
        recommendation_summary: '',
        credibility: null,
      }
      await buildProfileStream(studentId, message, {
        onProfile(data) { if (appState.result) { appState.result.student = data.student; persistStudent(studentId, studentName) } },
        onDiagnosis(data) { if (appState.result) appState.result.diagnosis = data },
        onTraces(data) { if (appState.result) appState.result.traces = data },
        onResource(data) { if (appState.result) appState.result.resources.push(data) },
        onPlan(data) { if (appState.result) appState.result.study_plan = data.study_plan },
        onDone() { appState.loading = false },
        onError(msg) { appState.error = msg; appState.loading = false },
      })
    } else {
      appState.result = await buildProfile(studentId, message)
      persistStudent(studentId, studentName)
    }
    appState.refreshKey += 1
  } catch (err: any) {
    appState.error = err?.response?.data?.detail || (err?.code === 'ECONNABORTED' ? '请求超时，6个智能体协作耗时较长，请稍后重试' : err?.message) || '请求失败，请确认后端已启动。'
  } finally {
    appState.loading = false
  }
}
</script>

<template>
  <div class="home-page">
    <HeroBanner />

    <div class="stream-toggle">
      <label class="toggle-label">
        <input type="checkbox" v-model="appState.streamMode" />
        <span class="toggle-text">流式输出模式 {{ appState.streamMode ? '(SSE)' : '(标准)' }}</span>
      </label>
      <label class="toggle-label">
        <input type="checkbox" v-model="appState.demoMode" />
        <span class="toggle-text">演示模式 {{ appState.demoMode ? '(已开启)' : '(已关闭)' }}</span>
      </label>
    </div>

    <PresetSelector
        :loading="appState.loading"
        :initial-name="appState.studentName"
        :initial-major="appState.result?.student?.profile?.major_background"
        :initial-goal="appState.result?.student?.profile?.learning_goal"
        :initial-level="appState.result?.student?.profile?.prerequisite_level"
        :initial-weak="appState.result?.student?.profile?.weak_points"
        :initial-style="appState.result?.student?.profile?.learning_style"
        :initial-hours="appState.result?.student?.profile?.weekly_hours"
        :initial-exercise="appState.result?.student?.profile?.exercise_preference"
        @start="handleStart"
      />

    <div class="error-banner" v-if="appState.error">
      <span>{{ appState.error }}</span>
    </div>

    <div class="loading-banner glass-card" v-if="appState.loading">
      <div class="spinner"></div>
      <span>6 个智能体正在协作生成个性化方案，请稍候...</span>
    </div>

    <template v-if="appState.result">
      <RecommendationSummary
        :summary="appState.result.recommendation_summary"
        :credibility="appState.result.credibility"
        :demo-mode="appState.demoMode"
      />

      <div class="duo-grid section">
        <ProfileCard
          :profile="appState.result.student.profile"
          :name="appState.studentName"
        />
        <DiagnosisPanel :diagnosis="appState.result.diagnosis" />
      </div>

      <AgentPipeline :traces="appState.result.traces" />
      <ResourceCards :resources="appState.result.resources" />
      <StudyPath :plan="appState.result.study_plan" />

      <QAPanel :student-id="appState.studentId" />
      <AssessmentHistory :student-id="appState.studentId" />
    </template>

    <OverviewPanel :refresh-key="appState.refreshKey" />
  </div>
</template>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
}

.duo-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.error-banner {
  padding: 12px 18px;
  border-radius: var(--radius-md);
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: #f87171;
  font-size: 14px;
  margin-bottom: 20px;
}

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

.stream-toggle {
  margin-bottom: 16px;
  display: flex;
  gap: 16px;
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

@media (max-width: 900px) {
  .duo-grid {
    grid-template-columns: 1fr;
  }
}
</style>
