from fastapi.testclient import TestClient

from src.backend.app.main import app


client = TestClient(app)


def test_learning_flow():
    create_resp = client.post(
        "/api/v1/students",
        json={"name": "张三", "major": "人工智能", "target_course": "机器学习基础"},
    )
    assert create_resp.status_code == 200
    student_id = create_resp.json()["id"]

    profile_resp = client.post(
        "/api/v1/chat/profile-build",
        json={
            "student_id": student_id,
            "message": "我是人工智能专业学生，机器学习零基础，想通过项目实战学会线性回归和模型评估，希望多给代码案例。",
        },
    )
    assert profile_resp.status_code == 200
    data = profile_resp.json()
    assert len(data["resources"]) >= 5
    assert len(data["traces"]) == 6
    assert "weak_points" in data["student"]["profile"]

    assess_resp = client.post(
        "/api/v1/assessment/submit",
        json={"student_id": student_id, "knowledge_unit": "线性回归", "score": 65},
    )
    assert assess_resp.status_code == 200

    dashboard_resp = client.get(f"/api/v1/student/{student_id}/dashboard")
    assert dashboard_resp.status_code == 200
    dashboard = dashboard_resp.json()
    assert dashboard["student"]["name"] == "张三"
    assert dashboard["resources"][0]["title"]

    kb_questions_resp = client.get("/api/v1/kb/questions")
    assert kb_questions_resp.status_code == 200
    assert len(kb_questions_resp.json()["questions"]) >= 8

    kb_cases_resp = client.get("/api/v1/kb/coding-cases")
    assert kb_cases_resp.status_code == 200
    assert len(kb_cases_resp.json()["coding_cases"]) >= 4
