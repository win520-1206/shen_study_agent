"""测试第四周新增功能：智能答疑 + 评估增强。"""
import sys
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from src.backend.app.main import app

client = TestClient(app)

print("=== 1. 创建学生 ===")
resp = client.post("/api/v1/students", json={"name": "测试生", "major": "人工智能", "target_course": "机器学习基础"})
assert resp.status_code == 200
student_id = resp.json()["id"]
print(f"学生 ID: {student_id}")

print("\n=== 2. 构建画像 ===")
resp = client.post("/api/v1/chat/profile-build", json={"student_id": student_id, "message": "我是零基础，想通过考试提分，希望多做选择题"})
assert resp.status_code == 200
data = resp.json()
print(f"画像: {data['student']['profile']}")
print(f"资源数: {len(data['resources'])}")
print(f"轨迹数: {len(data['traces'])}")
print(f"推荐依据: {data['recommendation_summary']}")
assert data["credibility"]["based_on_kb"] is True

print("\n=== 3. 智能答疑 ===")
resp = client.post("/api/v1/chat/qa", json={"student_id": student_id, "question": "什么是线性回归"})
assert resp.status_code == 200
qa = resp.json()
print(f"回答: {qa['answer'][:200]}")
print(f"来源: {qa['source_refs']}")
print(f"轨迹: {qa['agent_trace']['agent_name']}")

print("\n=== 4. 提交评估 ===")
for score in [55, 65, 80]:
    resp = client.post("/api/v1/assessment/submit", json={"student_id": student_id, "knowledge_unit": "线性回归", "score": score})
    assert resp.status_code == 200
    assess = resp.json()
    print(f"分数={score}, 趋势={assess['trend']}, 反馈={assess['feedback']}")

print("\n=== 5. 评估历史 ===")
resp = client.get(f"/api/v1/student/{student_id}/assessments")
assert resp.status_code == 200
history = resp.json()
print(f"记录数: {len(history['records'])}")
print(f"弱项: {history['weak_points']}")
print(f"进步点: {history['improvement_points']}")
print(f"趋势: {history['trend']}")
print(f"成长总结: {history['progress_summary']}")

print("\n=== 6. 成果看板 ===")
resp = client.get("/api/v1/overview/summary")
assert resp.status_code == 200
overview = resp.json()
print(f"学生数: {overview['student_count']}")
print(f"资源统计: {overview['resource_type_stats']}")

print("\n=== 全部测试通过 ===")
