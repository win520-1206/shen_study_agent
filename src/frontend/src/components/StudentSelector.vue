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
        {{ showPanel ? '\u2713' : '\u2194' }}
      </button>
    </div>

    <!-- 无学生时 -->
    <div v-else class="no-student" @click="togglePanel">
      <span class="no-student-icon">\U0001f468\u200d\U0001f393</span>
      <span class="no-student-text">请选择学生</span>
    </div>

    <!-- 移动端遮罩 -->
    <div v-if="showPanel" class="mobile-overlay" @click="showPanel = false"></div>

    <!-- 下拉面板 -->
    <div class="dropdown-panel" v-if="showPanel">
      <div class="dropdown-header">
        <span>选择学生</span>
        <button class="refresh-btn" @click="loadStudents" :disabled="loading">
          {{ loading ? '...' : '\u21bb' }}
        </button>
      </div>

      <div class="student-list" v-if="students.length">
        <div
          v-for="s in students"
          :key="s.id"
          class="student-item"
          :class="{ active: s.id === appState.studentId }"
          @click="handleSelect(s)"
        >
          <div class="item-avatar">{{ s.name.charAt(0) }}</div>
          <div class="item-info">
            <span class="item-name">{{ s.name }}</span>
            <span class="item-major">{{ s.major }}</span>
          </div>
          <span
            class="item-goal"
            v-if="s.learning_goal && s.learning_goal !== '\u672a\u5efa\u753b\u50cf'"
          >
            {{ s.learning_goal }}
          </span>
        </div>
      </div>

      <div class="empty-list" v-else-if="!loading">
        暂无学生记录
      </div>

      <button class="create-btn" @click="handleCreateNew">
        + 新建学生
      </button>
    </div>
  </div>
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

/* Dropdown */
.dropdown-panel {
  position: absolute;
  left: 14px;
  right: 14px;
  top: 100%;
  z-index: 300;
  background: rgba(15, 23, 42, 0.97);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  backdrop-filter: blur(20px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  margin-top: 4px;
}

.dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-card);
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
}

.refresh-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
  padding: 2px 4px;
}

.refresh-btn:hover {
  color: var(--color-primary);
}

.student-list {
  max-height: 240px;
  overflow-y: auto;
}

.student-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.student-item:hover,
.student-item:active {
  background: rgba(255, 255, 255, 0.04);
}

.student-item.active {
  background: rgba(0, 212, 255, 0.08);
}

.item-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(124, 58, 237, 0.2);
  color: var(--color-secondary);
  font-size: 12px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.item-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.item-major {
  font-size: 11px;
  color: var(--text-muted);
}

.item-goal {
  font-size: 11px;
  flex-shrink: 0;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
}

.empty-list {
  padding: 20px;
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}

.create-btn {
  display: block;
  width: 100%;
  padding: 10px;
  border: none;
  border-top: 1px solid var(--border-card);
  background: transparent;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.create-btn:hover,
.create-btn:active {
  background: rgba(0, 212, 255, 0.06);
}

/* Mobile overlay - hidden on desktop */
.mobile-overlay {
  display: none;
}

/* -- Mobile responsive -- */
@media (max-width: 900px) {
  .student-selector {
    padding: 8px 6px;
  }

  .current-student {
    padding: 8px;
    justify-content: center;
    min-height: 44px;
  }

  .student-meta {
    display: none;
  }

  .switch-btn {
    display: none;
  }

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

  .no-student-text {
    display: none;
  }

  .no-student-icon {
    font-size: 24px;
  }

  .mobile-overlay {
    display: block;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 400;
  }

  .dropdown-panel {
    position: fixed;
    left: 60px;
    top: 0;
    right: 0;
    bottom: 0;
    margin: 0;
    border-radius: 0;
    z-index: 500;
    display: flex;
    flex-direction: column;
  }

  .student-list {
    flex: 1;
    max-height: none;
  }

  .dropdown-header {
    padding: 16px 14px;
    font-size: 14px;
  }

  .student-item {
    padding: 14px;
  }

  .item-name {
    font-size: 14px;
  }

  .item-major {
    font-size: 12px;
  }

  .create-btn {
    padding: 14px;
    font-size: 14px;
  }
}
</style>
