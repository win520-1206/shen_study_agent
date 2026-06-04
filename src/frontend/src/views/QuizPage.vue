<script setup lang="ts">
import { computed } from 'vue'
import { appState } from '../store'
import ResourcePageWrapper from '../components/ResourcePageWrapper.vue'
import QuizPanel from '../components/QuizPanel.vue'

const quizContent = computed(() => {
  if (!appState.result) return ''
  const quiz = appState.result.resources.find(r => r.resource_type === 'quiz')
  return quiz?.content || ''
})

// Use diagnosis.focus_knowledge_unit (specific point like "最小二乘法") instead of source_refs[0] (module ID like "ml03_linear_regression")
const knowledgeUnit = computed(() => {
  if (!appState.result) return ''
  return appState.result.diagnosis?.focus_knowledge_unit || ''
})
</script>

<template>
  <ResourcePageWrapper resource-type="quiz" title="练习题" icon="✅" />
  <QuizPanel
    v-if="appState.studentId && quizContent"
    :student-id="appState.studentId"
    :quiz-content="quizContent"
    :knowledge-unit="knowledgeUnit"
  />
</template>
