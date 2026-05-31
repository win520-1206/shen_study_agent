<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { getOverviewSummary, getDashboard } from '../composables/useApi'
import type { OverviewSummaryResponse, DashboardResponse } from '../types'

const props = defineProps<{
  refreshKey: number
}>()

const overview = ref<OverviewSummaryResponse | null>(null)
const loading = ref(false)

const students = ref<Array<{
  id: number
  name: string
  major: string
  target_course: string
  learning_goal: string
  prerequisite_level: string
  weak_points: string[]
}>>([])

const expandedId = ref<number | null>(null)
const expandedData = ref<DashboardResponse | null>(null)
const expandLoading = ref(false)

const resourceLabels: Record<string, string> = {
  lesson_note: '讲义',
  quiz: '练习题',
  coding_case: '代码案例',
  mind_map: '思维导图',
  study_path: '学习路径',
}

async function load() {
  loading.value = true
  try {
    overview.value = await getOverviewSummary()
    const resp = await fetch('/api/v1/students')
    const data = await resp.json()
    students.value = data.students || []
  } catch {
    overview.value = null
  } finally {
    loading.value = false
  }
}

async function toggleExpand(studentId: number) {
  if (expandedId.value === studentId) {
    expandedId.value = null
    expandedData.value = null
    return
  }
  expandedId.value = studentId
  expandLoading.value = true
  try {
    expandedData.value = await getDashboard(studentId)
  } catch {
    expandedData.value = null
  } finally {
    expandLoading.value = false
  }
}

onMounted(load)
watch(() => props.refreshKey, load)
</script>

<template>
  <section class="section">
    <h2 class="section-title">教师 / 评委成果看板</h2>

    <div class="overview-grid" v-if="overview">
      <article class="glass-card metric-card">
        <span class="metric-label">学生画像样本</span>
        <strong class="metric-value">{{ overview.student_count }}</strong>
      </article>
      <article class="glass-card metric-card">
        <span class="metric-label">学习会话总数</span>
        <strong class="metric-value">{{ overview.active_session_count }}</strong>
      </article>
      <article class="glass-card metric-card">
        <span class="metric-label">平均评估分数</span>
        <strong class="metric-value">{{ overview.average_score || 0 }}</strong>
      </article>

      <article class="glass-card list-card">
        <h3 class="card-title">最常见薄弱点</h3>
        <div class="rank-list">
          <div v-for="item in overview.most_common_weak_points" :key="item.knowledge_unit" class="rank-row">
            <span>{{ item.knowledge_unit }}</span>
            <span class="chip chip--orange">{{ item.count }}人次</span>
          </div>
        </div>
      </article>

      <article class="glass-card list-card">
        <h3 class="card-title">资源生成分布</h3>
        <div class="rank-list">
          <div v-for="item in overview.resource_type_stats" :key="item.resource_type" class="rank-row">
            <span>{{ resourceLabels[item.resource_type] || item.resource_type }}</span>
            <span class="chip chip--blue">{{ item.count }}</span>
          </div>
        </div>
      </article>

      <article class="glass-card list-card">
        <h3 class="card-title">典型学生案例</h3>
        <div class="student-case" v-for="student in overview.featured_students" :key="student.name + student.goal">
          <div class="student-top">
            <strong>{{ student.name }}</strong>
            <span class="chip chip--purple">{{ student.goal }}</span>
          </div>
          <p>{{ student.major }} · 薄弱点：{{ student.weak_points.join('、') || '待补充' }}</p>
        </div>
      </article>
    </div>

    <div class="glass-card empty-card" v-else>
      <p>{{ loading ? '正在加载成果看板...' : '当前还没有足够的数据生成成果看板。' }}</p>
    </div>

    <!-- 学生列表 -->
    <div class="student-list-section" v-if="students.length">
      <h3 class="subsection-title">全部学生数据</h3>
      <div class="student-list">
        <div
          v-for="s in students"
          :key="s.id"
          class="student-row glass-card"
          :class="{ expanded: expandedId === s.id }"
        >
          <div class="student-header" @click="toggleExpand(s.id)">
            <div class="student-info">
              <strong class="student-name">{{ s.name }}</strong>
              <span class="student-major">{{ s.major }}</span>
              <span class="chip chip--green" v-if="s.learning_goal !== '未建画像'">{{ s.learning_goal }}</span>
              <span class="chip" v-else>{{ s.learning_goal }}</span>
            </div>
            <div class="student-weak">
              <span v-for="w in s.weak_points" :key="w" class="chip chip--orange chip-sm">{{ w }}</span>
            </div>
            <span class="expand-arrow" :class="{ open: expandedId === s.id }">▾</span>
          </div>

          <div class="student-detail" v-if="expandedId === s.id">
            <div v-if="expandLoading" class="detail-loading">加载中...</div>
            <div v-else-if="expandedData" class="detail-content">
              <div class="detail-grid">
                <div class="detail-col">
                  <h4>学生画像</h4>
                  <div v-if="expandedData.student.profile" class="profile-list">
                    <div v-for="(val, key) in expandedData.student.profile" :key="key" class="profile-row">
                      <span class="profile-key">{{ key }}</span>
                      <span class="profile-val">{{ Array.isArray(val) ? val.join('、') : val }}</span>
                    </div>
                  </div>
                </div>
                <div class="detail-col">
                  <h4>最新诊断</h4>
                  <p><strong>阶段：</strong>{{ expandedData.latest_diagnosis.current_stage }}</p>
                  <p><strong>策略：</strong>{{ expandedData.latest_diagnosis.recommended_strategy }}</p>
                  <p><strong>重点：</strong>{{ expandedData.latest_diagnosis.focus_knowledge_unit }}</p>
                </div>
                <div class="detail-col">
                  <h4>最近评估</h4>
                  <div v-if="expandedData.recent_assessments.length">
                    <div v-for="a in expandedData.recent_assessments" :key="a.knowledge_unit + a.score" class="assess-row">
                      <span>{{ a.knowledge_unit }}</span>
                      <span class="assess-score" :class="{ low: a.score < 70 }">{{ a.score }}分</span>
                      <span class="assess-trend">
                        {{ a.trend === '上升' ? '↑' : a.trend === '下降' ? '↓' : '→' }}
                        {{ a.trend }}
                      </span>
                    </div>
                  </div>
                  <p v-else class="no-data">暂无评估记录</p>
                </div>
              </div>
              <div class="detail-resources" v-if="expandedData.resources.length">
                <h4>最新生成资源</h4>
                <div class="res-tags">
                  <span v-for="r in expandedData.resources" :key="r.title" class="chip chip--blue">{{ resourceLabels[r.resource_type] || r.resource_type }}</span>
                </div>
              </div>
            </div>
            <div v-else class="detail-loading">无法加载详情</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  margin-bottom: 28px;
}

.metric-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 700;
  letter-spacing: 0.04em;
}

.metric-value {
  font-size: 34px;
  line-height: 1;
  color: var(--color-primary);
}

.list-card {
  min-height: 220px;
}

.card-title {
  font-size: 15px;
  margin-bottom: 12px;
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rank-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.student-case {
  padding: 10px 0;
  border-bottom: 1px solid var(--border-card);
}

.student-case:last-child {
  border-bottom: none;
}

.student-top {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
}

.student-case p {
  font-size: 13px;
  color: var(--text-secondary);
}

.empty-card {
  text-align: center;
  color: var(--text-muted);
}

.student-list-section {
  margin-top: 28px;
}

.subsection-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.student-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.student-row {
  padding: 0;
  overflow: hidden;
  transition: border-color 0.2s;
}

.student-row.expanded {
  border-color: rgba(0, 212, 255, 0.3);
}

.student-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  cursor: pointer;
  transition: background 0.2s;
}

.student-header:hover {
  background: rgba(255, 255, 255, 0.03);
}

.student-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.student-name {
  font-size: 14px;
  min-width: 60px;
}

.student-major {
  font-size: 12px;
  color: var(--text-muted);
}

.student-weak {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  flex: 1;
}

.chip-sm {
  font-size: 11px;
  padding: 2px 8px;
}

.expand-arrow {
  font-size: 10px;
  color: var(--text-muted);
  transition: transform 0.2s;
  flex-shrink: 0;
}

.expand-arrow.open {
  transform: rotate(180deg);
}

.student-detail {
  border-top: 1px solid var(--border-card);
  padding: 18px;
}

.detail-loading {
  text-align: center;
  color: var(--text-muted);
  padding: 16px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.detail-col h4 {
  font-size: 13px;
  color: var(--color-primary);
  margin-bottom: 10px;
}

.detail-col p {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  line-height: 1.6;
}

.profile-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.profile-row {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.profile-key {
  color: var(--text-muted);
  min-width: 70px;
}

.profile-val {
  color: var(--text-primary);
}

.assess-row {
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 13px;
  margin-bottom: 4px;
}

.assess-score {
  font-weight: 700;
  color: var(--color-success);
}

.assess-score.low {
  color: var(--color-danger);
}

.assess-trend {
  font-size: 12px;
  color: var(--text-muted);
}

.no-data {
  font-size: 13px;
  color: var(--text-muted);
}

.detail-resources h4 {
  font-size: 13px;
  color: var(--color-primary);
  margin-bottom: 8px;
}

.res-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

@media (max-width: 900px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
  .detail-grid {
    grid-template-columns: 1fr;
  }
  .student-header {
    flex-wrap: wrap;
  }
}
</style>
