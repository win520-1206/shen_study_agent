<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  studentId: number
}>()

const emit = defineEmits<{
  submitted: [result: any]
}>()

const knowledgeUnit = ref('')
const score = ref(75)
const loading = ref(false)
const result = ref<any>(null)

const presetUnits = [
  '线性回归',
  '逻辑回归',
  '决策树',
  '支持向量机',
  '聚类',
  '模型评估',
  '特征工程',
]

async function handleSubmit() {
  if (!knowledgeUnit.value.trim() || !props.studentId) return
  loading.value = true
  try {
    const resp = await fetch(`/api/v1/assessment/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: props.studentId,
        knowledge_unit: knowledgeUnit.value,
        score: score.value,
      }),
    })
    result.value = await resp.json()
    emit('submitted', result.value)
  } catch {
    result.value = { feedback: '提交失败，请确认后端已启动。' }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="section">
    <h2 class="section-title">提交练习成绩</h2>
    <div class="assess-card glass-card">
      <div class="unit-presets">
        <span class="preset-label">知识点：</span>
        <button
          v-for="unit in presetUnits"
          :key="unit"
          class="unit-btn"
          :class="{ active: knowledgeUnit === unit }"
          @click="knowledgeUnit = unit"
        >
          {{ unit }}
        </button>
      </div>
      
      <div class="assess-form">
        <div class="form-field">
          <label>或手动输入知识点</label>
          <el-input v-model="knowledgeUnit" placeholder="例如：线性回归" />
        </div>
        
        <div class="form-field">
          <label>分数：{{ score }}</label>
          <el-slider v-model="score" :min="0" :max="100" :step="5" />
        </div>
        
        <el-button 
          type="primary" 
          :loading="loading" 
          :disabled="!knowledgeUnit.trim() || !studentId"
          @click="handleSubmit"
        >
          提交成绩
        </el-button>
      </div>

      <div v-if="result" class="assess-result">
        <div class="result-item">
          <span class="result-label">反馈：</span>
          <span>{{ result.feedback }}</span>
        </div>
        <div class="result-item">
          <span class="result-label">建议：</span>
          <span>{{ result.next_recommendation }}</span>
        </div>
        <div class="result-item" v-if="result.trend">
          <span class="result-label">趋势：</span>
          <span :class="{
            up: result.trend === '上升',
            down: result.trend === '下降',
          }">
            {{ result.trend === '上升' ? '↑' : result.trend === '下降' ? '↓' : '→' }} {{ result.trend }}
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.assess-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.unit-presets {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.unit-btn {
  padding: 4px 12px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-card);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.unit-btn:hover {
  border-color: rgba(0, 212, 255, 0.3);
  color: var(--color-primary);
}

.unit-btn.active {
  background: rgba(0, 212, 255, 0.15);
  border-color: var(--color-primary);
  color: var(--color-primary);
  font-weight: 600;
}

.assess-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-field label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.assess-result {
  padding: 14px;
  background: rgba(0, 212, 255, 0.04);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--color-primary);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-item {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.result-label {
  font-weight: 600;
  color: var(--text-muted);
  flex-shrink: 0;
}

.up {
  color: var(--color-success);
  font-weight: 600;
}

.down {
  color: var(--color-danger);
  font-weight: 600;
}
</style>
