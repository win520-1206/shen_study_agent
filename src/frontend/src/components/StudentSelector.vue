<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getStudents } from '../composables/useApi'
import { appState, persistStudent, clearStudent } from '../store'
import type { StudentListItem } from '../types'

const emit = defineEmits<{
  'select': [studentId: number]
  'create-new': []
}>()

const students = ref<StudentListItem[]>([])
const showPanel = ref(false)
const loading = ref(false)

async function loadStudents() {
  loading.value = true
  try {
    students.value = await getStudents()
  } catch {
    students.value = []
  } finally {
    loading.value = false
  }
}

function handleSelect(s: StudentListItem) {
  persistStudent(s.id, s.name)
  showPanel.value = false
  emit('select', s.id)
}

function handleCreateNew() {
  clearStudent()
  showPanel.value = false
  emit('create-new')
}

function togglePanel() {
  showPanel.value = !showPanel.value
  if (showPanel.value) {
    loadStudents()
  }
}

onMounted(() => {
  if (appState.studentId > 0) {
    loadStudents()
  }
})
</script>

<template>
  <div class="student-selector">
    <!-- 有学生时 -->
    <div v-if="appState.studentId > 0" class="current-student" @click="togglePanel">
      <div class="student-avatar">{{ appState.studentName?.charAt(0) || '?' }}</div>
      <div class="student-meta">
        <span class="student-name-text">{{ appState.studentName }}</span>
        <span class="student-hint">已选择</span>
      </div>
      <button class="switch-btn" @click.stop="togglePanel" title="切换学生">
        {{ showPanel ? '✓' : '↔' }}
      </button>
    </div>

    <!-- 无学生时 -->
    <div v-else class="no-student" @click="togglePanel">
      <span class="no-student-icon">👨‍🎓</span>
      <span class="no-student-text">请选择学生</span>
    </div>
  </div>

  <!-- 用 Teleport 渲染到 body，脱离侧边栏层叠上下文 -->
  <Teleport to="body">
    <div v-if="showPanel" class="ss-overlay" @click="showPanel = false"></div>
    <div v-if="showPanel" class="ss-panel">
      <div class="ss-panel-header">
        <span>选择学生</span>
        <button class="ss-refresh" @click="loadStudents" :disabled="loading">
          {{ loading ? '...' : '↻' }}
        </button>
      </div>

      <div class="ss-list" v-if="students.length">
        <div
          v-for="s in students"
          :key="s.id"
          class="ss-item"
          :class="{ active: s.id === appState.studentId }"
          @click="handleSelect(s)"
        >
          <div class="ss-item-avatar">{{ s.name.charAt(0) }}</div>
          <div class="ss-item-info">
            <span class="ss-item-name">{{ s.name }}</span>
            <span class="ss-item-major">{{ s.major }}</span>
          </div>
          <span
            class="ss-item-goal"
            v-if="s.learning_goal && s.learning_goal !== '未建画像'"
          >
            {{ s.learning_goal }}
          </span>
        </div>
      </div>

      <div class="ss-empty" v-else-if="!loading">
        暂无学生记录
      </div>

      <button class="ss-create" @click="handleCreateNew">
        + 新建学生
      </button>
    </div>
  </Teleport>
</template>

<style scoped>
.student-selector {
  padding: 10px 14px;
  position: relative;
}

.current-student {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  background: rgba(0, 212, 255, 0.06);
  border: 1px solid rgba(0, 212, 255, 0.15);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.student-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
  color: #fff;
  font-size: 14px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.student-meta {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.student-name-text {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-hint {
  font-size: 11px;
  color: var(--text-muted);
}

.switch-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid var(--border-card);
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.switch-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: rgba(0, 212, 255, 0.08);
}

.no-student {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  border: 1px dashed var(--border-card);
  cursor: pointer;
  transition: all 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.no-student:hover {
  border-color: var(--color-primary);
  background: rgba(0, 212, 255, 0.04);
}

.no-student-icon {
  font-size: 18px;
}

.no-student-text {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 600;
}

/* Mobile: only show avatar/icon */
@media (max-width: 900px) {
  .student-selector {
    padding: 8px 6px;
  }

  .current-student {
    padding: 8px;
    justify-content: center;
    min-height: 44px;
  }

  .student-meta { display: none; }
  .switch-btn { display: none; }

  .student-avatar {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }

  .no-student {
    justify-content: center;
    padding: 10px;
    min-height: 44px;
  }

  .no-student-text { display: none; }

  .no-student-icon {
    font-size: 24px;
  }
}
</style>

<style>
/* Global styles for Teleported panel (not scoped) */
.ss-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9000;
}

.ss-panel {
  position: fixed;
  z-index: 9001;
  background: rgba(15, 23, 42, 0.98);
  border: 1px solid var(--border-card);
  backdrop-filter: blur(20px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

.ss-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-card);
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.ss-refresh {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 16px;
  padding: 4px 8px;
}

.ss-list {
  overflow-y: auto;
}

.ss-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.ss-item:hover,
.ss-item:active {
  background: rgba(255, 255, 255, 0.05);
}

.ss-item.active {
  background: rgba(0, 212, 255, 0.1);
}

.ss-item-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(124, 58, 237, 0.2);
  color: #7c3aed;
  font-size: 14px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ss-item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.ss-item-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.ss-item-major {
  font-size: 12px;
  color: var(--text-muted);
}

.ss-item-goal {
  font-size: 11px;
  flex-shrink: 0;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
}

.ss-empty {
  padding: 32px 16px;
  text-align: center;
  font-size: 14px;
  color: var(--text-muted);
}

.ss-create {
  display: block;
  width: 100%;
  padding: 14px 16px;
  border: none;
  border-top: 1px solid var(--border-card);
  background: transparent;
  color: #00d4ff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.ss-create:hover,
.ss-create:active {
  background: rgba(0, 212, 255, 0.08);
}

/* Desktop: dropdown below the selector */
@media (min-width: 901px) {
  .ss-panel {
    top: 60px;
    left: 10px;
    width: 200px;
    max-height: 400px;
    border-radius: var(--radius-md);
  }

  .ss-list {
    max-height: 280px;
  }
}

/* Mobile: full-screen panel from sidebar edge */
@media (max-width: 900px) {
  .ss-panel {
    left: 60px;
    top: 0;
    right: 0;
    bottom: 0;
    border-radius: 0;
    display: flex;
    flex-direction: column;
  }

  .ss-list {
    flex: 1;
    max-height: none;
  }
}
</style>
