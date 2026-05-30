<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  loading: boolean
}>()

const emit = defineEmits<{
  start: [name: string, major: string, message: string, presetKey: string]
}>()

interface Preset {
  key: string
  label: string
  desc: string
  name: string
  major: string
  message: string
}

const presets: Preset[] = [
  {
    key: 'beginner',
    label: '零基础入门型',
    desc: '通俗讲解，先建立认知',
    name: '李同学',
    major: '人工智能',
    message: '我是人工智能专业学生，机器学习零基础，希望通俗讲解，先建立整体认知，不用一开始就上很多代码。',
  },
  {
    key: 'practical',
    label: '项目实战型',
    desc: '代码实操，跑通案例',
    name: '王同学',
    major: '计算机科学',
    message: '我有 Python 和 sklearn 基础，想通过项目实战学会机器学习，重点做特征工程和模型评估的代码实验。',
  },
  {
    key: 'exam',
    label: '考试冲刺型',
    desc: '高频考点，刷题强化',
    name: '赵同学',
    major: '人工智能',
    message: '期末考试临近，我想快速掌握机器学习高频考点和易错题型，多给选择题和简答题练习。',
  },
]

const activePreset = ref('')
const customName = ref('张三')
const customMajor = ref('人工智能')
const customMessage = ref('')

function selectPreset(p: Preset) {
  activePreset.value = p.key
  customName.value = p.name
  customMajor.value = p.major
  customMessage.value = p.message
}

function handleStart() {
  const name = customName.value.trim()
  const major = customMajor.value.trim()
  const msg = customMessage.value.trim()
  if (!name || !msg) return
  emit('start', name, major, msg, activePreset.value || 'custom')
}
</script>

<template>
  <section class="section">
    <h2 class="section-title">学生类型选择</h2>
    <div class="preset-bar">
      <button
        v-for="p in presets"
        :key="p.key"
        class="preset-btn"
        :class="{ active: activePreset === p.key }"
        :disabled="props.loading"
        @click="selectPreset(p)"
      >
        <span class="preset-label">{{ p.label }}</span>
        <span class="preset-desc">{{ p.desc }}</span>
      </button>
    </div>

    <div class="form-area glass-card">
      <div class="form-row">
        <div class="form-field">
          <label>姓名</label>
          <el-input v-model="customName" placeholder="输入姓名" />
        </div>
        <div class="form-field">
          <label>专业</label>
          <el-input v-model="customMajor" placeholder="输入专业" />
        </div>
      </div>
      <div class="form-field">
        <label>学习诉求</label>
        <el-input
          v-model="customMessage"
          type="textarea"
          :rows="4"
          placeholder="请描述你的学习背景、目标和偏好..."
        />
      </div>
      <el-button
        type="primary"
        size="large"
        :loading="props.loading"
        :disabled="!customMessage.trim()"
        @click="handleStart"
      >
        {{ props.loading ? '智能体协作中...' : '生成个性化学习方案' }}
      </el-button>
    </div>
  </section>
</template>

<style scoped>
.preset-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.preset-btn {
  flex: 1;
  min-width: 160px;
  padding: 14px 18px;
  border-radius: var(--radius-md);
  background: var(--bg-card);
  border: 1.5px solid var(--border-card);
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  backdrop-filter: blur(8px);
}

.preset-btn:hover:not(:disabled) {
  border-color: rgba(0, 212, 255, 0.35);
  background: var(--bg-card-hover);
}

.preset-btn.active {
  border-color: var(--color-primary);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.15), inset 0 0 20px rgba(0, 212, 255, 0.04);
}

.preset-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.preset-label {
  display: block;
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.preset-desc {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
}

.active .preset-label {
  color: var(--color-primary);
}

.form-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-field label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
