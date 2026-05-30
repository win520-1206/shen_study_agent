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

    def _build_recommendation_summary(
        self,
        profile: dict[str, Any],
        diagnosis: dict[str, Any],
        weak_history: list[dict[str, Any]],
    ) -> str:
        parts = [
            f"系统识别你当前的学习目标是“{profile['learning_goal']}”，基础水平为“{profile['prerequisite_level']}”。",
            f"本轮优先推荐“{diagnosis['priority_modules'][0]}”，重点攻克“{diagnosis['focus_knowledge_unit']}”。",
        ]
        if weak_history:
            top_weak = weak_history[0]
            parts.append(
                f"结合历史评估，系统发现你在“{top_weak['knowledge_unit']}”上仍较薄弱，因此提高了相关内容的推荐优先级。"
            )
        else:
            parts.append("当前还没有历史测验记录，因此本轮推荐主要依据你的对话画像和知识库命中结果。")
        return "".join(parts)

    def _analyze_history(self, student_id: int) -> dict[str, Any]:
        records = (
            self.db.query(models.AssessmentRecord)
            .filter(models.AssessmentRecord.student_id == student_id)
            .order_by(models.AssessmentRecord.created_at.desc())
            .all()
        )

        unit_scores: dict[str, list[int]] = {}
        for record in records:
            unit_scores.setdefault(record.knowledge_unit, []).append(record.score)

        weak_points = []
        improvement_points = []
        trend_map: dict[str, str] = {}
        for unit, scores in unit_scores.items():
            avg = sum(scores) / len(scores)
            if avg < 70:
                weak_points.append({"knowledge_unit": unit, "avg_score": round(avg, 1), "attempts": len(scores)})
            if len(scores) >= 2 and scores[0] > scores[-1]:
                improvement_points.append({"knowledge_unit": unit, "avg_score": round(avg, 1), "attempts": len(scores)})
            if len(scores) >= 2:
                if scores[0] > scores[-1]:
                    trend_map[unit] = "上升"
                elif scores[0] < scores[-1]:
                    trend_map[unit] = "下降"
                else:
                    trend_map[unit] = "持平"
            else:
                trend_map[unit] = "首次"

        weak_points.sort(key=lambda item: (item["avg_score"], -item["attempts"]))
        improvement_points.sort(key=lambda item: (-item["attempts"], item["avg_score"]))

        if not records:
            progress_summary = "当前还没有评估记录，建议先完成一次针对性练习，系统再根据结果动态调整推荐。"
        elif weak_points:
            progress_summary = f"最近的学习记录显示，你在“{weak_points[0]['knowledge_unit']}”上仍需重点突破，建议优先完成相关讲义和练习。"
        elif improvement_points:
            progress_summary = f"你在“{improvement_points[0]['knowledge_unit']}”上的成绩已有上升趋势，可以逐步把精力转向更高难度任务。"
        else:
            progress_summary = "当前评估结果整体稳定，建议保持现有节奏并继续通过练习巩固。"

        return {
            "records": records,
            "weak_points": weak_points,
            "improvement_points": improvement_points,
            "trend": trend_map,
            "progress_summary": progress_summary,
        }

    def _build_overview_summary(self) -> dict[str, Any]:
        students = self.db.query(models.Student).all()
        sessions = self.db.query(models.LearningSession).all()
        resources = self.db.query(models.GeneratedResource).all()
        assessments = self.db.query(models.AssessmentRecord).all()

        weak_counter: dict[str, int] = {}
        featured_students = []
        for student in students:
            profile = json.loads(student.profile_json) if student.profile_json else {}
            for weak in profile.get("weak_points", []):
                weak_counter[weak] = weak_counter.get(weak, 0) + 1
            if len(featured_students) < 3:
                featured_students.append(
                    {
                        "name": student.name,
                        "major": student.major,
                        "goal": profile.get("learning_goal", "未建画像"),
                        "weak_points": profile.get("weak_points", []),
                    }
                )

        resource_counter: dict[str, int] = {}
        for resource in resources:
            resource_counter[resource.resource_type] = resource_counter.get(resource.resource_type, 0) + 1

        average_score = round(sum(item.score for item in assessments) / len(assessments), 1) if assessments else 0.0
        score_bands = {"90+": 0, "70-89": 0, "0-69": 0}
        for item in assessments:
            if item.score >= 90:
                score_bands["90+"] += 1
            elif item.score >= 70:
                score_bands["70-89"] += 1
            else:
                score_bands["0-69"] += 1

        return {
            "student_count": len(students),
            "active_session_count": len(sessions),
            "most_common_weak_points": [
                {"knowledge_unit": key, "count": value}
                for key, value in sorted(weak_counter.items(), key=lambda item: item[1], reverse=True)[:5]
            ],
            "resource_type_stats": [
                {"resource_type": key, "count": value}
                for key, value in sorted(resource_counter.items(), key=lambda item: item[1], reverse=True)
            ],
            "average_score": average_score,
            "score_band_distribution": [{"label": key, "count": value} for key, value in score_bands.items()],
            "featured_students": featured_students,
        }

    def run_learning_cycle(self, student: models.Student, message: str) -> dict[str, Any]:
        profile_result = self.profile_agent.run(student.major, message)
        history_analysis = self._analyze_history(student.id)
        search_terms = list(profile_result.payload["weak_points"])
        search_terms.extend([item["knowledge_unit"] for item in history_analysis["weak_points"][:2]])
        kb_hits = self.kb_service.search(search_terms)
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
        recommendation_summary = self._build_recommendation_summary(
            profile_result.payload,
            diagnosis_result.payload,
            history_analysis["weak_points"],
        )
        credibility = {
            "based_on_kb": bool(kb_hits),
            "reviewed": review_result.payload["passed"],
            "source_modules": [item["module_id"] for item in kb_hits[:3]],
            "note": "内容由知识库检索结果驱动，并经过审查智能体做基础完整性校验。",
        }

        student.profile_json = json.dumps(profile_result.payload, ensure_ascii=False)
        session = models.LearningSession(
            student_id=student.id,
            user_input=message,
            diagnosis_json=json.dumps(diagnosis_result.payload, ensure_ascii=False),
            plan_json=json.dumps(path_result.payload["study_plan"], ensure_ascii=False),
            recommendation_summary=recommendation_summary,
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
                    decision_reason=result.decision_reason,
                    impact_on_result=result.impact_on_result,
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
            "recommendation_summary": recommendation_summary,
            "credibility": credibility,
            "traces": [
                {
                    "agent_name": result.name,
                    "input_summary": result.input_summary,
                    "output_summary": result.output_summary,
                    "decision_reason": result.decision_reason,
                    "impact_on_result": result.impact_on_result,
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
        analysis = self._analyze_history(student_id)
        records = analysis["records"]

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
            "weak_points": analysis["weak_points"],
            "improvement_points": analysis["improvement_points"],
            "trend": analysis["trend"],
            "progress_summary": analysis["progress_summary"],
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
                    decision_reason=result.decision_reason,
                    impact_on_result=result.impact_on_result,
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
                "decision_reason": result.decision_reason,
                "impact_on_result": result.impact_on_result,
            },
        }

    def get_dashboard(self, student_id: int) -> dict[str, Any]:
        student = self.db.get(models.Student, student_id)
        latest_session = sorted(student.sessions, key=lambda item: item.created_at)[-1]
        recent_assessments = (
            self.db.query(models.AssessmentRecord)
            .filter(models.AssessmentRecord.student_id == student_id)
            .order_by(models.AssessmentRecord.created_at.desc())
            .limit(5)
            .all()
        )
        traces = (
            self.db.query(models.AgentTrace)
            .filter(models.AgentTrace.session_id == latest_session.id)
            .order_by(models.AgentTrace.created_at.asc())
            .all()
        )
        resources = (
            self.db.query(models.GeneratedResource)
            .filter(models.GeneratedResource.session_id == latest_session.id)
            .order_by(models.GeneratedResource.created_at.asc())
            .all()
        )
        analysis = self._analyze_history(student_id)
        return {
            "student": {
                "id": student.id,
                "name": student.name,
                "major": student.major,
                "target_course": student.target_course,
                "profile": json.loads(student.profile_json) if student.profile_json else None,
            },
            "latest_diagnosis": json.loads(latest_session.diagnosis_json),
            "latest_plan": json.loads(latest_session.plan_json),
            "resources": [
                {
                    "resource_type": resource.resource_type,
                    "title": resource.title,
                    "content": resource.content,
                    "source_refs": json.loads(resource.source_refs),
                }
                for resource in resources
            ],
            "recent_assessments": [
                {
                    "knowledge_unit": record.knowledge_unit,
                    "score": record.score,
                    "feedback": record.feedback,
                    "next_recommendation": "保持当前节奏" if record.score >= 80 else f"回到 {record.knowledge_unit}",
                    "trend": analysis["trend"].get(record.knowledge_unit, "首次"),
                }
                for record in recent_assessments
            ],
            "traces": [
                {
                    "agent_name": trace.agent_name,
                    "input_summary": trace.input_summary,
                    "output_summary": trace.output_summary,
                    "decision_reason": getattr(trace, "decision_reason", ""),
                    "impact_on_result": getattr(trace, "impact_on_result", ""),
                }
                for trace in traces
            ],
            "recommendation_summary": latest_session.recommendation_summary or analysis["progress_summary"],
            "progress_summary": analysis["progress_summary"],
            "weak_point_rank": analysis["weak_points"][:5],
            "improvement_rank": analysis["improvement_points"][:5],
            "updated_at": latest_session.created_at,
        }

    def get_overview_summary(self) -> dict[str, Any]:
        return self._build_overview_summary()
