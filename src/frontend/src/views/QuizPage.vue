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
</script>

<template>
  <ResourcePageWrapper resource-type="quiz" title="练习题" icon="✅" />
  <QuizPanel
    v-if="appState.studentId && quizContent"
    :student-id="appState.studentId"
    :quiz-content="quizContent"
  />
</template>
