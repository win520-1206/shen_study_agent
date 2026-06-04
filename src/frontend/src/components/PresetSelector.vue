<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  loading: boolean
  initialName?: string
  initialMajor?: string
  initialGoal?: string
  initialLevel?: string
  initialWeak?: string[]
  initialStyle?: string
  initialHours?: string
  initialExercise?: string
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
  learning_goal: string
  prerequisite_level: string
  weak_points: string[]
  learning_style: string
  weekly_hours: string
  exercise_preference: string
  message: string
}

const goalOptions = ['期末提分', '入门掌握', '项目实战', '考研准备', '竞赛准备']
const levelOptions = ['零基础', '基础一般', '有编程基础', '学过部分算法']
const weakOptions = ['线性回归', '逻辑回归', '决策树', '支持向量机', '聚类', '模型评估', '特征工程']
const styleOptions = ['喜欢看讲解', '喜欢做题', '喜欢代码实战', '喜欢图示化总结']
const hoursOptions = ['每周5小时', '每周8小时', '每周10小时', '每周15小时']
const exerciseOptions = ['选择题', '简答题', '编程题', '混合题型']

const presets: Preset[] = [
  {
    key: 'beginner',
    label: '零基础入门型',
    desc: '通俗讲解，先建立认知',
    name: '李同学',
    major: '人工智能',
    learning_goal: '入门掌握',
    prerequisite_level: '零基础',
    weak_points: ['线性回归', '模型评估'],
    learning_style: '喜欢看讲解',
    weekly_hours: '每周10小时',
    exercise_preference: '混合题型',
    message: '希望通俗讲解，先建立整体认知，不用一开始就上很多代码。',
  },
  {
    key: 'practical',
    label: '项目实战型',
    desc: '代码实操，跑通案例',
    name: '王同学',
    major: '计算机科学',
    learning_goal: '项目实战',
    prerequisite_level: '有编程基础',
    weak_points: ['特征工程', '线性回归'],
    learning_style: '喜欢代码实战',
    weekly_hours: '每周10小时',
    exercise_preference: '编程题',
    message: '想通过项目实战学会机器学习，重点做特征工程和模型评估的代码实验。',
  },
  {
    key: 'exam',
    label: '考试冲刺型',
    desc: '高频考点，刷题强化',
    name: '赵同学',
    major: '人工智能',
    learning_goal: '期末提分',
    prerequisite_level: '基础一般',
    weak_points: ['模型评估', '逻辑回归'],
    learning_style: '喜欢做题',
    weekly_hours: '每周15小时',
    exercise_preference: '选择题',
    message: '期末考试临近，想快速掌握高频考点和易错题型，多给选择题和简答题练习。',
  },
]

const activePreset = ref('')
const customName = ref('')
const customMajor = ref('')
const customGoal = ref('')
const customLevel = ref('')
const customWeak = ref<string[]>([])
const customStyle = ref('')
const customHours = ref('')
const customExercise = ref('')

// Auto-fill from props (when student is selected)
watch(() => [props.initialName, props.initialMajor, props.initialGoal, props.initialLevel, props.initialWeak, props.initialStyle, props.initialHours, props.initialExercise], () => {
  if (props.initialName) customName.value = props.initialName
  if (props.initialMajor) customMajor.value = props.initialMajor
  if (props.initialGoal) customGoal.value = props.initialGoal
  if (props.initialLevel) customLevel.value = props.initialLevel
  if (props.initialWeak && props.initialWeak.length) customWeak.value = [...props.initialWeak]
  if (props.initialStyle) customStyle.value = props.initialStyle
  if (props.initialHours) customHours.value = props.initialHours
  if (props.initialExercise) customExercise.value = props.initialExercise
}, { immediate: true })
const customMessage = ref('')

function selectPreset(p: Preset) {
  activePreset.value = p.key
  customName.value = p.name
  customMajor.value = p.major
  customGoal.value = p.learning_goal
  customLevel.value = p.prerequisite_level
  customWeak.value = [...p.weak_points]
  customStyle.value = p.learning_style
  customHours.value = p.weekly_hours
  customExercise.value = p.exercise_preference
  customMessage.value = p.message
}

const allFilled = computed(() => {
  return customName.value.trim()
    && customMajor.value.trim()
    && customGoal.value
    && customLevel.value
    && customWeak.value.length > 0
    && customStyle.value
    && customHours.value
    && customExercise.value
    && customMessage.value.trim()
})

function buildMessage(): string {
  const parts = [
    `我是${customMajor.value}专业学生`,
    `学习目标是${customGoal.value}`,
    `当前基础水平为${customLevel.value}`,
    `薄弱知识点包括${customWeak.value.join('、')}`,
    `学习风格偏好${customStyle.value}`,
    `每周可投入${customHours.value}`,
    `练习偏好为${customExercise.value}`,
  ]
  const structured = parts.join('，') + '。'
  const extra = customMessage.value.trim()
  return extra ? `${structured}${extra}` : structured
}

function handleStart() {
  if (!allFilled.value) return
  emit('start', customName.value.trim(), customMajor.value.trim(), buildMessage(), activePreset.value || 'custom')
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
          <label>姓名 <span class="required">*</span></label>
          <el-input v-model="customName" placeholder="输入姓名" />
        </div>
        <div class="form-field">
          <label>专业 <span class="required">*</span></label>
          <el-input v-model="customMajor" placeholder="输入专业" />
        </div>
      </div>

      <div class="form-row">
        <div class="form-field">
          <label>学习目标 <span class="required">*</span></label>
          <el-select v-model="customGoal" placeholder="请选择学习目标" style="width:100%">
            <el-option v-for="opt in goalOptions" :key="opt" :label="opt" :value="opt" />
          </el-select>
        </div>
        <div class="form-field">
          <label>基础水平 <span class="required">*</span></label>
          <el-select v-model="customLevel" placeholder="请选择基础水平" style="width:100%">
            <el-option v-for="opt in levelOptions" :key="opt" :label="opt" :value="opt" />
          </el-select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-field">
          <label>薄弱知识点 <span class="required">*</span></label>
          <el-select v-model="customWeak" multiple placeholder="请选择薄弱知识点" style="width:100%">
            <el-option v-for="opt in weakOptions" :key="opt" :label="opt" :value="opt" />
          </el-select>
        </div>
        <div class="form-field">
          <label>学习风格 <span class="required">*</span></label>
          <el-select v-model="customStyle" placeholder="请选择学习风格" style="width:100%">
            <el-option v-for="opt in styleOptions" :key="opt" :label="opt" :value="opt" />
          </el-select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-field">
          <label>每周投入时间 <span class="required">*</span></label>
          <el-select v-model="customHours" placeholder="请选择每周投入" style="width:100%">
            <el-option v-for="opt in hoursOptions" :key="opt" :label="opt" :value="opt" />
          </el-select>
        </div>
        <div class="form-field">
          <label>练习偏好 <span class="required">*</span></label>
          <el-select v-model="customExercise" placeholder="请选择练习偏好" style="width:100%">
            <el-option v-for="opt in exerciseOptions" :key="opt" :label="opt" :value="opt" />
          </el-select>
        </div>
      </div>

      <div class="form-field">
        <label>补充说明</label>
        <el-input
          v-model="customMessage"
          type="textarea"
          :rows="3"
          placeholder="可选：补充其他学习背景或特殊需求..."
        />
      </div>

      <div class="form-hint" v-if="!allFilled">
        请填写上方所有带 <span class="required">*</span> 的必填字段
      </div>

      <el-button
        type="primary"
        size="large"
        :loading="props.loading"
        :disabled="!allFilled"
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

.required {
  color: var(--color-danger);
}

.form-hint {
  font-size: 13px;
  color: var(--color-warning);
  text-align: center;
  padding: 8px;
  border-radius: var(--radius-sm);
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
