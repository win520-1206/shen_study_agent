# LearnMate-AI

> 基于大模型的个性化学习多智能体系统


---

## 项目简介

LearnMate-AI 让每个学生都有自己的专属学习方案。学生通过结构化表单描述学习情况，7 个智能体自动协作，在几秒内生成一套完整的个性化学习资源——包括讲义、练习题、代码案例、思维导图和学习路径。

**在线体验**：`http://121.199.26.183:8000` | **API 文档**：`http://121.199.26.183:8000/docs`

## 核心能力

- **8 维学生画像**：通过结构化表单精确刻画学习目标、基础水平、薄弱知识点等
- **7 个智能体协作**：画像、诊断、资源规划、内容生成、路径规划、审查、自动批改
- **5 类个性化资源**：讲义、练习题（选择题 + 简答题）、代码案例、思维导图、学习路径
- **知识图谱诊断**：ECharts 可视化课程依赖关系，薄弱点及上游依赖自动高亮
- **交互式答题**：选择题即时判对错，简答题 LLM 自动评分 + 要点反馈
- **苏格拉底式追问**：AI 不仅回答问题，还主动引导学生深入思考
- **学生持续跟踪**：localStorage 持久化，刷新不丢失，支持多学生切换
- **教师看板**：聚合数据展示学生总数、弱项分布、资源统计

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI + SQLAlchemy + SQLite |
| 前端 | Vue 3 + Vite + Element Plus + vue-router + ECharts |
| 大模型 | DeepSeek API（支持 Mock/LLM 一行配置切换） |
| 知识库 | 8 个 ML 模块 + 32 道题 + 10 个代码案例 + 知识依赖图谱 |
| 部署 | 阿里云 ECS + systemd |

## 快速启动

### 云端访问（推荐）

浏览器打开 `http://121.199.26.183:8000` 即可体验全部功能。

### 本地开发

```bash
# 后端
pip install -r requirements.txt
uvicorn src.backend.app.main:app --reload

# 前端（另一个终端）
cd src/frontend
npm install
npm run dev
```

访问 `http://localhost:8000`（后端）或 `http://localhost:5173`（前端开发服务器）。

### 切换大模型

编辑 `src/backend/app/config.py`：

```python
USE_LLM = True
LLM_PROVIDER = "generic"
LLM_BASE_URL = "https://api.deepseek.com"
LLM_API_KEY_V2 = "sk-你的密钥"
LLM_MODEL = "deepseek-chat"
```

## 项目结构

```
shen_study_agent/
├── src/
│   ├── backend/app/           # FastAPI 后端
│   │   ├── routers/           # API 路由（14 个端点）
│   │   ├── services/          # 智能体 + LLM 服务 + 知识库
│   │   └── static/            # 前端构建产物
│   └── frontend/src/          # Vue 3 前端
│       ├── views/             # 6 个页面（首页 + 5 个资源页）
│       ├── components/        # 19 个功能组件
│       ├── router/            # vue-router 路由
│       └── store.ts           # 全局状态 + localStorage
├── data/course_kb/            # 机器学习课程知识库 + 知识图谱
├── docs/                      # 需求、设计、测试、部署、比赛文档
├── evidence/                  # 版本日志、截图、测试记录
├── tests/                     # 自动化测试
└── requirements.txt           # Python 依赖
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/students` | POST | 创建学生 |
| `/api/v1/students` | GET | 学生列表 |
| `/api/v1/chat/profile-build` | POST | 6 智能体学习方案生成 |
| `/api/v1/chat/profile-build/stream` | POST | SSE 流式版本 |
| `/api/v1/chat/qa` | POST | 智能答疑（支持苏格拉底模式） |
| `/api/v1/quiz/grade` | POST | LLM 自动批改练习题 |
| `/api/v1/assessment/submit` | POST | 提交评估成绩 |
| `/api/v1/student/{id}/assessments` | GET | 评估历史 |
| `/api/v1/student/{id}/dashboard` | GET | 学生完整数据 |
| `/api/v1/overview/summary` | GET | 教师看板 |
| `/api/v1/kb/graph` | GET | 知识图谱 |
| `/api/v1/kb/modules` | GET | 课程模块 |
| `/api/v1/kb/questions` | GET | 题库 |
| `/api/v1/kb/coding-cases` | GET | 代码案例 |

## 文档

| 文档 | 路径 |
|------|------|
| 项目简介 | `docs/01_立项与需求/项目简介.md` |
| 系统架构设计 | `docs/02_概要设计/系统架构设计.md` |
| 核心接口设计 | `docs/03_详细设计/核心接口设计.md` |
| 用户主流程 | `docs/03_详细设计/用户主流程.md` |
| 大模型接入方案 | `docs/03_详细设计/大模型接入方案.md` |
| 数据库设计 | `docs/04_数据库设计/数据库设计.md` |
| 用户使用说明书 | `docs/05_测试文档/用户使用说明书.md` |
| 测试计划 | `docs/05_测试文档/测试计划.md` |
| 比赛表达材料 | `docs/06_比赛材料/比赛表达材料.md` |
| 部署运维速查表 | `docs/06_部署运维/运维速查表.md` |
