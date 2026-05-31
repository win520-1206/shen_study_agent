from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    name: str
    major: str
    target_course: str = "机器学习基础"


class StudentProfile(BaseModel):
    major_background: str
    learning_goal: str
    prerequisite_level: str
    weak_points: list[str]
    learning_style: str
    weekly_hours: str
    exercise_preference: str
    target_outcome: str


class StudentResponse(BaseModel):
    id: int
    name: str
    major: str
    target_course: str
    profile: StudentProfile | None = None


class ProfileBuildRequest(BaseModel):
    student_id: int
    message: str = Field(..., min_length=5)


class ResourceCard(BaseModel):
    resource_type: str
    title: str
    content: str
    source_refs: list[str]


class TraceCard(BaseModel):
    agent_name: str
    input_summary: str
    output_summary: str
    decision_reason: str = ""
    impact_on_result: str = ""


class StudyPlan(BaseModel):
    stage: str
    objectives: list[str]
    recommended_resources: list[str]
    practice_task: str
    rationale: str = ""


class CredibilityInfo(BaseModel):
    based_on_kb: bool
    reviewed: bool
    source_modules: list[str]
    note: str


class ProfileBuildResponse(BaseModel):
    student: StudentResponse
    diagnosis: dict[str, Any]
    resources: list[ResourceCard]
    study_plan: list[StudyPlan]
    traces: list[TraceCard]
    recommendation_summary: str = ""
    credibility: CredibilityInfo | None = None


class AssessmentSubmitRequest(BaseModel):
    student_id: int
    knowledge_unit: str
    score: int = Field(..., ge=0, le=100)


class AssessmentResponse(BaseModel):
    knowledge_unit: str
    score: int
    feedback: str
    next_recommendation: str
    trend: str = "首次"


class DashboardResponse(BaseModel):
    student: StudentResponse
    latest_diagnosis: dict[str, Any]
    latest_plan: list[StudyPlan]
    resources: list[ResourceCard]
    recent_assessments: list[AssessmentResponse]
    traces: list[TraceCard]
    recommendation_summary: str = ""
    progress_summary: str = ""
    weak_point_rank: list[dict[str, Any]] = []
    improvement_rank: list[dict[str, Any]] = []
    updated_at: datetime


class QARequest(BaseModel):
    student_id: int
    question: str = Field(..., min_length=2)
    socratic: bool = False


class QAResponse(BaseModel):
    answer: str
    source_refs: list[str]
    agent_trace: TraceCard


class AssessmentRecordItem(BaseModel):
    knowledge_unit: str
    score: int
    feedback: str
    created_at: str | None = None


class WeakPoint(BaseModel):
    knowledge_unit: str
    avg_score: float
    attempts: int


class AssessmentHistoryResponse(BaseModel):
    records: list[AssessmentRecordItem]
    weak_points: list[WeakPoint]
    trend: dict[str, str]
    improvement_points: list[WeakPoint] = []
    progress_summary: str = ""


class OverviewSummaryResponse(BaseModel):
    student_count: int
    active_session_count: int
    most_common_weak_points: list[dict[str, Any]]
    resource_type_stats: list[dict[str, Any]]
    average_score: float
    score_band_distribution: list[dict[str, Any]]
    featured_students: list[dict[str, Any]]
