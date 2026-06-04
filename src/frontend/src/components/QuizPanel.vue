<script setup lang="ts">
import { ref, computed } from 'vue'
import { gradeQuiz } from '../composables/useApi'
import type { QuizGradeResponse } from '../types'

const props = defineProps<{
  studentId: number
  quizContent: string
  knowledgeUnit?: string
}>()

interface QuizQuestion {
  index: number
  question: string
  reference: string
  type: 'choice' | 'essay'
  options: string[]
  correctAnswer: string
}

function parseQuestions(content: string): QuizQuestion[] {
  if (!content) return []
  const questions: QuizQuestion[] = []
  const lines = content.split('\n')
  let current: Partial<QuizQuestion> | null = null

  for (const line of lines) {
    const trimmed = line.trim()
    // Match question number: "1." "1、" "1。" etc.
    const qMatch = trimmed.match(/^(\d+)[.\u3001\uff0e]\s*(.+)/)
    if (qMatch) {
      if (current?.question) {
        finalizeQuestion(current)
        questions.push(current as QuizQuestion)
      }
      current = {
        index: parseInt(qMatch[1]),
        question: qMatch[2],
        reference: '',
        type: 'essay',
        options: [],
        correctAnswer: '',
      }
      continue
    }
    if (current) {
      // Detect choice options: "A. xxx" "B. xxx" etc.
      const optMatch = trimmed.match(/^([A-D])[.\uff0e]\s*(.+)/)
      if (optMatch) {
        current.options.push(trimmed)
        continue
      }
      // Detect reference answer line
      const refMatch = trimmed.match(/^[\u53c2\u8003\u7b54\u6848\u8981\u70b9|\u53c2\u8003\u7b54\u6848|\u7b54\u6848\u8981\u70b9|\u53c2\u8003\u8981\u70b9][:\uff1a]?\s*(.*)/i)
      if (refMatch) {
        current.reference = refMatch[1] || ''
      } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
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
  if (current?.question) {
    finalizeQuestion(current)
    questions.push(current as QuizQuestion)
  }
  return questions
}

function finalizeQuestion(q: Partial<QuizQuestion>) {
  if (q.options && q.options.length >= 2) {
    q.type = 'choice'
  }
  // Extract correct answer from reference: "正确答案是A" "答案：B" "答案是C"
  if (q.reference) {
    const ansMatch = q.reference.match(/[\u6b63\u786e]?\u7b54\u6848[\u662f\uff1a:]*\s*([A-D])/i)
      || q.reference.match(/([A-D])\s*(?:\u662f\u6b63\u786e|\u6b63\u786e)/i)
    if (ansMatch) {
      q.correctAnswer = ansMatch[1].toUpperCase()
    }
  }
}

const questions = computed(() => parseQuestions(props.quizContent))
const answers = ref<Record<number, string>>({})
const choiceResults = ref<Record<number, { correct: boolean; selected: string }>>({})
const results = ref<Record<number, QuizGradeResponse>>({})
const grading = ref<Record<number, boolean>>({})
const submitting = ref<Record<number, boolean>>({})

async function handleChoiceSelect(q: QuizQuestion, selected: string) {
  answers.value[q.index] = selected
  const isCorrect = selected === q.correctAnswer
  choiceResults.value[q.index] = { correct: isCorrect, selected }

  // Auto-submit assessment
  if (props.studentId && props.knowledgeUnit) {
    submitting.value[q.index] = true
    try {
      const score = isCorrect ? 100 : 0
      await fetch('/api/v1/assessment/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: props.studentId,
          knowledge_unit: props.knowledgeUnit,
          score,
        }),
      })
    } catch { /* silent */ }
    finally { submitting.value[q.index] = false }
  }
}

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
      props.knowledgeUnit || '',
    )
    results.value[q.index] = resp
  } catch {
    results.value[q.index] = {
      score: 0,
      feedback: '\u8bf7\u6c42\u5931\u8d25\uff0c\u8bf7\u786e\u8ba4\u540e\u7aef\u5df2\u542f\u52a8\u3002',
      key_points_hit: [],
      key_points_missed: [],
      knowledge_unit: '',
      trend: '\u9996\u6b21',
    }
  } finally {
    grading.value[q.index] = false
  }
}

const gradedCount = computed(() => {
  const choiceCount = Object.keys(choiceResults.value).length
  const essayCount = Object.keys(results.value).length
  return choiceCount + essayCount
})

const avgScore = computed(() => {
  const scores: number[] = []
  for (const [idx, cr] of Object.entries(choiceResults.value)) {
    scores.push(cr.correct ? 100 : 0)
  }
  for (const r of Object.values(results.value)) {
    scores.push(r.score)
  }
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
    <h2 class="section-title">\u4ea4\u4e92\u7b54\u9898</h2>

    <div class="quiz-stats glass-card" v-if="gradedCount > 0">
      <span class="stat-item">\u5df2\u7b54\uff1a<strong>{{ gradedCount }}</strong> / {{ questions.length }}</span>
      <span class="stat-item">\u5e73\u5747\u5206\uff1a<strong :style="{ color: scoreColor(avgScore) }">{{ avgScore }}</strong></span>
    </div>

    <div class="quiz-list">
      <div v-for="q in questions" :key="q.index" class="quiz-item glass-card">
        <div class="quiz-question">
          <span class="quiz-num">{{ q.index }}</span>
          <span class="quiz-text">{{ q.question }}</span>
          <span class="quiz-type-badge" :class="q.type === 'choice' ? 'badge-choice' : 'badge-essay'">
            {{ q.type === 'choice' ? '\u9009\u62e9\u9898' : '\u7b80\u7b54\u9898' }}
          </span>
        </div>

        <!-- 选择题 -->
        <template v-if="q.type === 'choice'">
          <div class="choice-options">
            <label
              v-for="opt in q.options"
              :key="opt"
              class="choice-option"
              :class="{
                selected: answers[q.index] === opt.charAt(0),
                correct: choiceResults[q.index] && opt.charAt(0) === q.correctAnswer,
                wrong: choiceResults[q.index]?.correct === false && answers[q.index] === opt.charAt(0),
                disabled: !!choiceResults[q.index],
              }"
            >
              <input
                type="radio"
                :name="'q-' + q.index"
                :value="opt.charAt(0)"
                :disabled="!!choiceResults[q.index]"
                @change="handleChoiceSelect(q, opt.charAt(0))"
                :checked="answers[q.index] === opt.charAt(0)"
              />
              <span class="opt-text">{{ opt }}</span>
              <span v-if="choiceResults[q.index] && opt.charAt(0) === q.correctAnswer" class="opt-icon">\u2705</span>
              <span v-if="choiceResults[q.index]?.correct === false && answers[q.index] === opt.charAt(0)" class="opt-icon">\u274c</span>
            </label>
          </div>
          <div class="choice-result" v-if="choiceResults[q.index]">
            <span :class="choiceResults[q.index].correct ? 'result-correct' : 'result-wrong'">
              {{ choiceResults[q.index].correct ? '\u7b54\u5bf9\u4e86\uff01' : '\u7b54\u9519\u4e86\uff0c\u6b63\u786e\u7b54\u6848\u662f ' + q.correctAnswer }}
            </span>
            <span class="auto-submit-hint" v-if="submitting[q.index]">\u6b63\u5728\u8bb0\u5f55\u6210\u7ee9...</span>
          </div>
        </template>

        <!-- 简答题 -->
        <template v-else>
          <div class="quiz-input">
            <el-input
              v-model="answers[q.index]"
              type="textarea"
              :rows="2"
              placeholder="\u8bf7\u8f93\u5165\u4f60\u7684\u7b54\u6848..."
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
              \u63d0\u4ea4\u6279\u6539
            </el-button>
          </div>
          <div class="quiz-result" v-if="results[q.index]">
            <div class="result-score">
              <div class="score-bar">
                <div class="score-fill" :style="{ width: results[q.index].score + '%', background: scoreColor(results[q.index].score) }"></div>
              </div>
              <span class="score-value" :style="{ color: scoreColor(results[q.index].score) }">{{ results[q.index].score }}\u5206</span>
            </div>
            <p class="result-feedback">{{ results[q.index].feedback }}</p>
            <div class="result-points" v-if="results[q.index].key_points_hit.length || results[q.index].key_points_missed.length">
              <div class="points-hit" v-if="results[q.index].key_points_hit.length">
                <span class="points-label">\u2705 \u547d\u4e2d\u8981\u70b9</span>
                <span v-for="p in results[q.index].key_points_hit" :key="p" class="chip chip--green">{{ p }}</span>
              </div>
              <div class="points-missed" v-if="results[q.index].key_points_missed.length">
                <span class="points-label">\u274c \u9057\u6f0f\u8981\u70b9</span>
                <span v-for="p in results[q.index].key_points_missed" :key="p" class="chip chip--orange">{{ p }}</span>
              </div>
            </div>
          </div>
        </template>
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
  flex: 1;
}

.quiz-type-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-pill);
  flex-shrink: 0;
}

.badge-choice {
  background: rgba(124, 58, 237, 0.12);
  color: var(--color-secondary);
}

.badge-essay {
  background: rgba(0, 212, 255, 0.1);
  color: var(--color-primary);
}

/* Choice options */
.choice-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.choice-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  border: 1.5px solid var(--border-card);
  cursor: pointer;
  transition: all 0.2s;
}

.choice-option:hover:not(.disabled) {
  border-color: rgba(0, 212, 255, 0.3);
  background: rgba(0, 212, 255, 0.04);
}

.choice-option.selected {
  border-color: var(--color-primary);
  background: rgba(0, 212, 255, 0.06);
}

.choice-option.correct {
  border-color: var(--color-success);
  background: rgba(16, 185, 129, 0.1);
}

.choice-option.wrong {
  border-color: var(--color-danger);
  background: rgba(239, 68, 68, 0.1);
}

.choice-option.disabled {
  cursor: default;
}

.choice-option input[type="radio"] {
  accent-color: var(--color-primary);
  width: 16px;
  height: 16px;
}

.opt-text {
  font-size: 14px;
  color: var(--text-primary);
  flex: 1;
}

.opt-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.choice-result {
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-correct {
  color: var(--color-success);
}

.result-wrong {
  color: var(--color-danger);
}

.auto-submit-hint {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 400;
}

/* Essay */
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
