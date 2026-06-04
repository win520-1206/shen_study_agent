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

const knowledgeUnit = computed(() => {
  if (!appState.result) return ''
  const quiz = appState.result.resources.find(r => r.resource_type === 'quiz')
  return quiz?.source_refs?.[0] || ''
})
</script>

<template>
  <ResourcePageWrapper resource-type="quiz" title="\u7ec3\u4e60\u9898" icon="\u2705" />
  <QuizPanel
    v-if="appState.studentId && quizContent"
    :student-id="appState.studentId"
    :quiz-content="quizContent"
    :knowledge-unit="knowledgeUnit"
  />
</template>
