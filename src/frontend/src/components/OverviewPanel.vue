<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { getOverviewSummary } from '../composables/useApi'
import type { OverviewSummaryResponse } from '../types'

const props = defineProps<{
  refreshKey: number
}>()

const overview = ref<OverviewSummaryResponse | null>(null)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    overview.value = await getOverviewSummary()
  } catch {
    overview.value = null
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => props.refreshKey, load)

const resourceLabels: Record<string, string> = {
  lesson_note: '讲义',
  quiz: '练习题',
  coding_case: '代码案例',
  mind_map: '思维导图',
  study_path: '学习路径',
}
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
  </section>
</template>

<style scoped>
.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
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

@media (max-width: 900px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
