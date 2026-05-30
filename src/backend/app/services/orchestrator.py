import json
from typing import Any

from sqlalchemy.orm import Session

from .. import models
from ..config import USE_LLM, get_llm_service
from .agents import (
    ContentGeneratorAgent,
    DiagnosisAgent,
    PathPlannerAgent,
    ProfileAgent,
    ResourcePlannerAgent,
    ReviewAgent,
)
from .knowledge_base import KnowledgeBaseService
from .llm_agents import (
    LLMContentGeneratorAgent,
    LLMDiagnosisAgent,
    LLMProfileAgent,
    LLMQAAgent,
)


class LearningOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.kb_service = KnowledgeBaseService()

        # 根据配置选择规则式或 LLM 式智能体
        if USE_LLM:
            llm = get_llm_service()
            self.profile_agent = LLMProfileAgent(llm)
            self.diagnosis_agent = LLMDiagnosisAgent(llm)
            self.content_generator_agent = LLMContentGeneratorAgent(llm)
            self._llm_service = llm
        else:
            self.profile_agent = ProfileAgent()
            self.diagnosis_agent = DiagnosisAgent()
            self.content_generator_agent = ContentGeneratorAgent()
            self._llm_service = None

        # 以下智能体暂时保持规则式
        self.resource_planner_agent = ResourcePlannerAgent()
        self.path_planner_agent = PathPlannerAgent()
        self.review_agent = ReviewAgent()

    def run_learning_cycle(self, student: models.Student, message: str) -> dict[str, Any]:
        profile_result = self.profile_agent.run(student.major, message)
        kb_hits = self.kb_service.search(profile_result.payload["weak_points"])
        diagnosis_result = self.diagnosis_agent.run(profile_result.payload, kb_hits)
        resource_plan_result = self.resource_planner_agent.run(profile_result.payload, diagnosis_result.payload)
        content_result = self.content_generator_agent.run(
            profile_result.payload,
            diagnosis_result.payload,
            kb_hits,
            self.kb_service,
        )
        path_result = self.path_planner_agent.run(profile_result.payload, diagnosis_result.payload, content_result.payload["resources"])
        review_result = self.review_agent.run(content_result.payload["resources"], kb_hits)

        student.profile_json = json.dumps(profile_result.payload, ensure_ascii=False)
        session = models.LearningSession(
            student_id=student.id,
            user_input=message,
            diagnosis_json=json.dumps(diagnosis_result.payload, ensure_ascii=False),
            plan_json=json.dumps(path_result.payload["study_plan"], ensure_ascii=False),
        )
        self.db.add(session)
        self.db.flush()

        for resource in content_result.payload["resources"]:
            self.db.add(
                models.GeneratedResource(
                    session_id=session.id,
                    resource_type=resource["resource_type"],
                    title=resource["title"],
                    content=resource["content"],
                    source_refs=json.dumps(resource["source_refs"], ensure_ascii=False),
                )
            )

        for result in [
            profile_result,
            diagnosis_result,
            resource_plan_result,
            content_result,
            path_result,
            review_result,
        ]:
            self.db.add(
                models.AgentTrace(
                    session_id=session.id,
                    agent_name=result.name,
                    input_summary=result.input_summary,
                    output_summary=result.output_summary,
                )
            )

        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        self.db.refresh(session)

        return {
            "student": student,
            "diagnosis": diagnosis_result.payload,
            "resources": content_result.payload["resources"],
            "study_plan": path_result.payload["study_plan"],
            "traces": [
                {
                    "agent_name": result.name,
                    "input_summary": result.input_summary,
                    "output_summary": result.output_summary,
                }
                for result in [
                    profile_result,
                    diagnosis_result,
                    resource_plan_result,
                    content_result,
                    path_result,
                    review_result,
                ]
            ],
        }

    def submit_assessment(self, student_id: int, knowledge_unit: str, score: int) -> dict[str, Any]:
        # 查询历史评估记录
        history = (
            self.db.query(models.AssessmentRecord)
            .filter(
                models.AssessmentRecord.student_id == student_id,
                models.AssessmentRecord.knowledge_unit == knowledge_unit,
            )
            .order_by(models.AssessmentRecord.created_at.desc())
            .limit(5)
            .all()
        )
        scores = [record.score for record in history]

        # 生成反馈
        if score >= 80:
            feedback = "掌握较好，可以进入下一个知识点。"
            recommendation = "推送更高难度练习"
        elif score >= 60:
            feedback = "基本掌握，建议再做一轮巩固练习。"
            recommendation = f"继续练习 {knowledge_unit} 的中等难度题"
        else:
            feedback = "尚未掌握，建议回看讲解文档并重做基础题。"
            recommendation = f"优先复习 {knowledge_unit}，从基础概念开始"

        # 趋势分析
        trend = "持平"
        if len(scores) >= 2:
            if score > scores[0]:
                trend = "上升"
            elif score < scores[0]:
                trend = "下降"

        record = models.AssessmentRecord(
            student_id=student_id,
            knowledge_unit=knowledge_unit,
            score=score,
            feedback=feedback,
        )
        self.db.add(record)
        self.db.commit()
        return {
            "knowledge_unit": knowledge_unit,
            "score": score,
            "feedback": feedback,
            "next_recommendation": recommendation,
            "trend": trend,
        }

    def get_assessment_history(self, student_id: int) -> dict[str, Any]:
        records = (
            self.db.query(models.AssessmentRecord)
            .filter(models.AssessmentRecord.student_id == student_id)
            .order_by(models.AssessmentRecord.created_at.desc())
            .all()
        )
        weak_points = []
        unit_scores: dict[str, list[int]] = {}
        for record in records:
            if record.knowledge_unit not in unit_scores:
                unit_scores[record.knowledge_unit] = []
            unit_scores[record.knowledge_unit].append(record.score)

        for unit, scores in unit_scores.items():
            avg = sum(scores) / len(scores)
            if avg < 70:
                weak_points.append({"knowledge_unit": unit, "avg_score": round(avg, 1), "attempts": len(scores)})

        trend_map: dict[str, str] = {}
        for unit, scores in unit_scores.items():
            if len(scores) >= 2:
                if scores[0] > scores[-1]:
                    trend_map[unit] = "上升"
                elif scores[0] < scores[-1]:
                    trend_map[unit] = "下降"
                else:
                    trend_map[unit] = "持平"
            else:
                trend_map[unit] = "首次"

        return {
            "records": [
                {
                    "knowledge_unit": record.knowledge_unit,
                    "score": record.score,
                    "feedback": record.feedback,
                    "created_at": record.created_at.isoformat() if record.created_at else None,
                }
                for record in records
            ],
            "weak_points": weak_points,
            "trend": trend_map,
        }

    def answer_question(self, student_id: int, question: str) -> dict[str, Any]:
        """智能答疑：基于知识库回答课程相关问题。"""
        # 获取学生画像
        student = self.db.get(models.Student, student_id)
        profile = None
        if student and student.profile_json:
            profile = json.loads(student.profile_json)

        # 知识库检索
        search_terms = [question]
        if profile and profile.get("weak_points"):
            search_terms.extend(profile["weak_points"])
        kb_hits = self.kb_service.search(search_terms)

        # 构建知识库上下文
        kb_context = ""
        if kb_hits:
            module_id = kb_hits[0]["module_id"]
            kb_context = self.kb_service.get_module_content(module_id)[:1500]

        # 调用答疑智能体
        if self._llm_service:
            qa_agent = LLMQAAgent(self._llm_service)
        else:
            qa_agent = LLMQAAgent(get_llm_service())

        result = qa_agent.run(question, profile, kb_context)

        # 记录轨迹
        if student and student.sessions:
            latest_session = sorted(student.sessions, key=lambda s: s.created_at)[-1]
            self.db.add(
                models.AgentTrace(
                    session_id=latest_session.id,
                    agent_name=result.name,
                    input_summary=result.input_summary,
                    output_summary=result.output_summary,
                )
            )
            self.db.commit()

        return {
            "answer": result.payload["answer"],
            "source_refs": [kb_hits[0]["module_id"]] if kb_hits else [],
            "agent_trace": {
                "agent_name": result.name,
                "input_summary": result.input_summary,
                "output_summary": result.output_summary,
            },
        }
