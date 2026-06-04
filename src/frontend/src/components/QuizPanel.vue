<script setup lang="ts">
import { ref, computed } from 'vue'
import { gradeQuiz } from '../composables/useApi'
import type { QuizGradeResponse } from '../types'

const props = defineProps<{
  studentId: number
  quizContent: string
}>()

interface QuizQuestion {
  index: number
  question: string
  reference: string
}

function parseQuestions(content: string): QuizQuestion[] {
  if (!content) return []
  const questions: QuizQuestion[] = []
  const lines = content.split('\n')
  let current: Partial<QuizQuestion> | null = null

  for (const line of lines) {
    const trimmed = line.trim()
    const qMatch = trimmed.match(/^(\d+)[.、)．]\s*(.+)/)
    if (qMatch) {
      if (current?.question) questions.push(current as QuizQuestion)
      current = { index: parseInt(qMatch[1]), question: qMatch[2], reference: '' }
      continue
    }
    if (current) {
      const refMatch = trimmed.match(/^[参考答案要点|参考答案要点|参考答案|答案要点][:：]?\s*(.*)/i)
      if (refMatch) {
        current.reference = refMatch[1] || ''
      } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ') || trimmed.match(/^\d+[.、)]/)) {
        current.reference += (current.reference ? '\n' : '') + trimmed
      } else if (trimmed && !trimmed.startsWith('```')) {
        if (!current.reference) {
          current.question += ' ' + trimmed
        } else {
          current.reference += '\n' + trimmed
        }
      }
    }
  }
  if (current?.question) questions.push(current as QuizQuestion)
  return questions
}

const questions = computed(() => parseQuestions(props.quizContent))
const answers = ref<Record<number, string>>({})
const results = ref<Record<number, QuizGradeResponse>>({})
const grading = ref<Record<number, boolean>>({})

async function handleGrade(q: QuizQuestion) {
  const ans = answers.value[q.index]?.trim()
  if (!ans) return
  grading.value[q.index] = true
  try {
    const resp = await gradeQuiz(
      props.studentId,
      q.question,
      ans,
      q.reference,
      '',
    )
    results.value[q.index] = resp
  } catch {
    results.value[q.index] = {
      score: 0,
      feedback: '请求失败，请确认后端已启动。',
      key_points_hit: [],
      key_points_missed: [],
      knowledge_unit: '',
      trend: '首次',
    }
  } finally {
    grading.value[q.index] = false
  }
}

const gradedCount = computed(() => Object.keys(results.value).length)
const avgScore = computed(() => {
  const scores = Object.values(results.value).map(r => r.score)
  return scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0
})

function scoreColor(score: number): string {
  if (score >= 80) return 'var(--color-success)'
  if (score >= 60) return 'var(--color-warning)'
  return 'var(--color-danger)'
}
</script>

<template>
  <section class="section" v-if="questions.length">
    <h2 class="section-title">交互答题</h2>

    <div class="quiz-stats glass-card" v-if="gradedCount > 0">
      <span class="stat-item">已答：<strong>{{ gradedCount }}</strong> / {{ questions.length }}</span>
      <span class="stat-item">平均分：<strong :style="{ color: scoreColor(avgScore) }">{{ avgScore }}</strong></span>
    </div>

    <div class="quiz-list">
      <div v-for="q in questions" :key="q.index" class="quiz-item glass-card">
        <div class="quiz-question">
          <span class="quiz-num">{{ q.index }}</span>
          <span class="quiz-text">{{ q.question }}</span>
        </div>

        <div class="quiz-input">
          <el-input
            v-model="answers[q.index]"
            type="textarea"
            :rows="2"
            placeholder="请输入你的答案..."
            :disabled="!!results[q.index]"
          />
        </div>

        <div class="quiz-actions" v-if="!results[q.index]">
          <el-button
            type="primary"
            size="small"
            :loading="grading[q.index]"
            :disabled="!answers[q.index]?.trim() || !studentId"
            @click="handleGrade(q)"
          >
            提交批改
          </el-button>
        </div>

        <div class="quiz-result" v-if="results[q.index]">
          <div class="result-score">
            <div class="score-bar">
              <div class="score-fill" :style="{ width: results[q.index].score + '%', background: scoreColor(results[q.index].score) }"></div>
            </div>
            <span class="score-value" :style="{ color: scoreColor(results[q.index].score) }">{{ results[q.index].score }}分</span>
          </div>
          <p class="result-feedback">{{ results[q.index].feedback }}</p>
          <div class="result-points" v-if="results[q.index].key_points_hit.length || results[q.index].key_points_missed.length">
            <div class="points-hit" v-if="results[q.index].key_points_hit.length">
              <span class="points-label">✅ 命中要点</span>
              <span v-for="p in results[q.index].key_points_hit" :key="p" class="chip chip--green">{{ p }}</span>
            </div>
            <div class="points-missed" v-if="results[q.index].key_points_missed.length">
              <span class="points-label">❌ 遗漏要点</span>
              <span v-for="p in results[q.index].key_points_missed" :key="p" class="chip chip--orange">{{ p }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.quiz-stats {
  display: flex;
  gap: 24px;
  padding: 14px 18px;
  margin-bottom: 16px;
  font-size: 14px;
}

.stat-item {
  color: var(--text-secondary);
}

.stat-item strong {
  font-size: 18px;
}

.quiz-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.quiz-item {
  padding: 18px;
}

.quiz-question {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 12px;
}

.quiz-num {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quiz-text {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.6;
}

.quiz-input {
  margin-bottom: 12px;
}

.quiz-actions {
  display: flex;
  justify-content: flex-end;
}

.quiz-result {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--border-card);
}

.result-score {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.score-bar {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.06);
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.score-value {
  font-size: 20px;
  font-weight: 800;
  min-width: 50px;
  text-align: right;
}

.result-feedback {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 10px;
}

.result-points {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.points-hit, .points-missed {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.points-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  min-width: 70px;
}
</style>
