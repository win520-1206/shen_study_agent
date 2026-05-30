# LearnMate-AI

LearnMate-AI is a training-oriented implementation of the 2026 China Software Cup A3 challenge:
"A large-model-based personalized resource generation and learning multi-agent system."

This repository is organized for two goals at the same time:

1. Build a runnable MVP for the competition.
2. Preserve documents and development evidence from day one for software copyright filing.

## Project Structure

- `src/backend`: FastAPI backend and multi-agent orchestration
- `src/frontend`: Vue 3 frontend scaffold for the demo workflow
- `data/course_kb`: "Machine Learning Fundamentals" course knowledge base
- `docs`: requirements, design, testing, deployment, and copyright materials
- `evidence`: screenshots, version notes, and test records
- `tests`: backend verification

## MVP Scope

- Conversational student profile building with 8 dimensions
- Multi-agent orchestration with 6 explicit agent roles
- Personalized generation of 5 resource types
- Learning path planning and recommendation
- Basic assessment feedback loop
- Trace logging for competition demo and explainability

## Quick Start

### Backend

```bash
pip install -r requirements.txt
uvicorn src.backend.app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the API explorer.

### Frontend

```bash
cd src/frontend
npm install
npm run dev
```

## Learning-Oriented Workflow

1. Read `docs/01_立项与需求/项目简介.md`
2. Review the knowledge base under `data/course_kb`
3. Start the backend and test `/api/v1/chat/profile-build`
4. Use the frontend scaffold to understand the end-to-end demo flow
5. Continue iterating while recording evidence under `evidence`
