<script setup lang="ts">
// HeroBanner - project intro, no props needed
</script>

<template>
  <section class="hero">
    <div class="hero-left">
      <p class="hero-eyebrow">基于大模型的个性化学习</p>
      <h1 class="hero-title">LearnMate-AI</h1>
      <p class="hero-sub">
        面向机器学习基础课程的个性化学习多智能体系统。通过对话构建学生画像，6 个智能体协作生成定制化学习资源与学习路径。
      </p>
    </div>
    <div class="hero-steps glass-card">
      <h3 class="steps-heading">演示流程</h3>
      <ol class="steps-list">
        <li>
          <span class="step-num">1</span>
          <div>
            <strong>选择学生类型</strong>
            <p>一键预设或自定义输入</p>
          </div>
        </li>
        <li>
          <span class="step-num">2</span>
          <div>
            <strong>多智能体协作</strong>
            <p>画像→诊断→规划→生成→路径→审查</p>
          </div>
        </li>
        <li>
          <span class="step-num">3</span>
          <div>
            <strong>查看个性化结果</strong>
            <p>画像、资源、路径一键展示</p>
          </div>
        </li>
      </ol>
    </div>
  </section>
</template>

<style scoped>
.hero {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 24px;
  align-items: center;
  margin-bottom: 32px;
}

.hero-eyebrow {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-primary);
  margin-bottom: 8px;
}

.hero-title {
  font-size: 52px;
  font-weight: 800;
  line-height: 1.1;
  margin: 0 0 12px;
  background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-sub {
  font-size: 16px;
  line-height: 1.7;
  color: var(--text-secondary);
  max-width: 560px;
}

.hero-steps {
  padding: 20px 24px;
}

.steps-heading {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 14px;
}

.steps-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.steps-list li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.step-num {
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

.steps-list strong {
  display: block;
  font-size: 14px;
  color: var(--text-primary);
}

.steps-list p {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
  }
  .hero-title {
    font-size: 38px;
  }
}
</style>
