import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.orchestrator import LearningOrchestrator


router = APIRouter(prefix="/api/v1", tags=["learnmate"])


@router.post("/students", response_model=schemas.StudentResponse)
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    student = models.Student(
        name=payload.name,
        major=payload.major,
        target_course=payload.target_course,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return schemas.StudentResponse(
        id=student.id,
        name=student.name,
        major=student.major,
        target_course=student.target_course,
        profile=None,
    )


@router.post("/chat/profile-build", response_model=schemas.ProfileBuildResponse)
def build_profile(payload: schemas.ProfileBuildRequest, db: Session = Depends(get_db)):
    student = db.get(models.Student, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    orchestrator = LearningOrchestrator(db)
    result = orchestrator.run_learning_cycle(student, payload.message)
    profile = json.loads(result["student"].profile_json)
    return {
        "student": {
            "id": result["student"].id,
            "name": result["student"].name,
            "major": result["student"].major,
            "target_course": result["student"].target_course,
            "profile": profile,
        },
        "diagnosis": result["diagnosis"],
        "resources": result["resources"],
        "study_plan": result["study_plan"],
        "traces": result["traces"],
    }


@router.post("/chat/qa", response_model=schemas.QAResponse)
def ask_question(payload: schemas.QARequest, db: Session = Depends(get_db)):
    student = db.get(models.Student, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    orchestrator = LearningOrchestrator(db)
    result = orchestrator.answer_question(payload.student_id, payload.question)
    return result


@router.post("/assessment/submit", response_model=schemas.AssessmentResponse)
def submit_assessment(payload: schemas.AssessmentSubmitRequest, db: Session = Depends(get_db)):
    student = db.get(models.Student, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    orchestrator = LearningOrchestrator(db)
    return orchestrator.submit_assessment(payload.student_id, payload.knowledge_unit, payload.score)


@router.get("/student/{student_id}/assessments", response_model=schemas.AssessmentHistoryResponse)
def get_assessment_history(student_id: int, db: Session = Depends(get_db)):
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    orchestrator = LearningOrchestrator(db)
    return orchestrator.get_assessment_history(student_id)


@router.get("/student/{student_id}/dashboard", response_model=schemas.DashboardResponse)
def get_dashboard(student_id: int, db: Session = Depends(get_db)):
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if not student.sessions:
        raise HTTPException(status_code=400, detail="Student has no learning sessions yet")

    latest_session = sorted(student.sessions, key=lambda item: item.created_at)[-1]
    recent_assessments = (
        db.query(models.AssessmentRecord)
        .filter(models.AssessmentRecord.student_id == student_id)
        .order_by(models.AssessmentRecord.created_at.desc())
        .limit(5)
        .all()
    )
    traces = (
        db.query(models.AgentTrace)
        .filter(models.AgentTrace.session_id == latest_session.id)
        .order_by(models.AgentTrace.created_at.asc())
        .all()
    )
    resources = (
        db.query(models.GeneratedResource)
        .filter(models.GeneratedResource.session_id == latest_session.id)
        .order_by(models.GeneratedResource.created_at.asc())
        .all()
    )
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
            }
            for record in recent_assessments
        ],
        "traces": [
            {
                "agent_name": trace.agent_name,
                "input_summary": trace.input_summary,
                "output_summary": trace.output_summary,
            }
            for trace in traces
        ],
        "updated_at": latest_session.created_at,
    }


@router.get("/kb/modules")
def list_modules():
    from ..services.knowledge_base import KnowledgeBaseService

    return {"modules": KnowledgeBaseService().list_modules()}


@router.get("/kb/questions")
def list_questions():
    from ..services.knowledge_base import KnowledgeBaseService

    return {"questions": KnowledgeBaseService().list_questions()}


@router.get("/kb/coding-cases")
def list_coding_cases():
    from ..services.knowledge_base import KnowledgeBaseService

    return {"coding_cases": KnowledgeBaseService().list_coding_cases()}
