"""SSE streaming endpoint for profile-build."""
import json
from typing import Generator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.orchestrator import LearningOrchestrator


router = APIRouter(prefix="/api/v1", tags=["learnmate-stream"])


def _sse_event(event: str, data: dict) -> str:
    """Format a dict as an SSE event."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat/profile-build/stream")
def build_profile_stream(payload: schemas.ProfileBuildRequest, db: Session = Depends(get_db)):
    """SSE streaming version of profile-build.

    Streams events in order: profile -> diagnosis -> resources (one by one) -> plan -> done
    """
    student = db.get(models.Student, payload.student_id)
    if not student:
        return StreamingResponse(
            iter([_sse_event("error", {"detail": "Student not found"})]),
            media_type="text/event-stream",
        )

    def event_generator() -> Generator[str, None, None]:
        orchestrator = LearningOrchestrator(db)
        result = orchestrator.run_learning_cycle(student, payload.message)

        # 1. Profile
        profile = json.loads(result["student"].profile_json)
        yield _sse_event("profile", {
            "student": {
                "id": result["student"].id,
                "name": result["student"].name,
                "major": result["student"].major,
                "target_course": result["student"].target_course,
                "profile": profile,
            }
        })

        # 2. Diagnosis
        yield _sse_event("diagnosis", result["diagnosis"])

        # 3. Traces
        yield _sse_event("traces", result["traces"])

        # 4. Resources (one by one for progressive rendering)
        for resource in result["resources"]:
            yield _sse_event("resource", resource)

        # 5. Study plan
        yield _sse_event("plan", {"study_plan": result["study_plan"]})

        # 6. Done
        yield _sse_event("done", {})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
