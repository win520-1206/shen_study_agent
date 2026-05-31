<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { appState } from './store'

const router = useRouter()
const route = useRoute()

const hasResult = computed(() => !!appState.result)

interface NavItem {
  path: string
  name: string
  icon: string
  label: string
  requiresResult: boolean
}

const navItems: NavItem[] = [
  { path: '/', name: 'home', icon: '🏠', label: '首页', requiresResult: false },
  { path: '/resources/lesson', name: 'lesson', icon: '📖', label: '讲义', requiresResult: true },
  { path: '/resources/quiz', name: 'quiz', icon: '✅', label: '练习题', requiresResult: true },
  { path: '/resources/coding', name: 'coding', icon: '💻', label: '代码案例', requiresResult: true },
  { path: '/resources/mindmap', name: 'mindmap', icon: '🧠', label: '思维导图', requiresResult: true },
  { path: '/resources/path', name: 'path', icon: '📋', label: '学习路径', requiresResult: true },
]

function navigateTo(item: NavItem) {
  if (item.requiresResult && !hasResult.value) return
  router.push(item.path)
}

function isActive(item: NavItem): boolean {
  return route.path === item.path
}
</script>

<template>
  <div class="app-layout">
    <!-- 左侧导航栏 -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <span class="logo-text">LearnMate-AI</span>
      </div>
      <nav class="sidebar-nav">
        <button
          v-for="item in navItems"
          :key="item.path"
          class="nav-item"
          :class="{
            active: isActive(item),
            disabled: item.requiresResult && !hasResult,
          }"
          @click="navigateTo(item)"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </button>
      </nav>
      <div class="sidebar-footer">
        <span class="footer-tag">多智能体系统</span>
        <span class="footer-tag">机器学习基础</span>
      </div>
    </aside>

    <!-- 右侧内容区 -->
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* -- Sidebar -- */
.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: rgba(10, 14, 26, 0.95);
  border-right: 1px solid var(--border-card);
  backdrop-filter: blur(16px);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 200;
}

.sidebar-logo {
  padding: 20px 18px 16px;
  border-bottom: 1px solid var(--border-card);
}

.logo-text {
  font-size: 18px;
  font-weight: 800;
  background: linear-gradient(135deg, #00d4ff, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
}

.nav-item:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border-card);
  color: var(--text-primary);
}

.nav-item.active {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.25);
  color: var(--color-primary);
}

.nav-item.disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.nav-icon {
  font-size: 18px;
  flex-shrink: 0;
  width: 24px;
  text-align: center;
}

.nav-label {
  white-space: nowrap;
}

.sidebar-footer {
  padding: 14px 18px;
  border-top: 1px solid var(--border-card);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.footer-tag {
  font-size: 11px;
  color: var(--text-muted);
  padding: 3px 8px;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-card);
  text-align: center;
}

/* -- Main content -- */
.main-content {
  flex: 1;
  margin-left: 220px;
  padding: 28px 32px 48px;
  min-height: 100vh;
}

/* -- Mobile responsive -- */
@media (max-width: 900px) {
  .sidebar {
    width: 60px;
    align-items: center;
  }

  .logo-text {
    font-size: 0;
  }

  .sidebar-logo::after {
    content: 'LM';
    font-size: 14px;
    font-weight: 800;
    background: linear-gradient(135deg, #00d4ff, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .nav-label {
    display: none;
  }

  .nav-item {
    justify-content: center;
    padding: 10px;
  }

  .sidebar-footer {
    display: none;
  }

  .main-content {
    margin-left: 60px;
    padding: 20px 16px 40px;
  }
}
</style>
