"""测试 LLM 模式下编排器是否正常工作。"""
import sys
sys.path.insert(0, ".")

from src.backend.app import config
config.USE_LLM = True

from src.backend.app.services.orchestrator import LearningOrchestrator
from src.backend.app.database import SessionLocal
from src.backend.app import models

db = SessionLocal()
student = db.query(models.Student).first()
if not student:
    student = models.Student(name="LLM测试生", major="计算机", target_course="机器学习基础")
    db.add(student)
    db.commit()
    db.refresh(student)

orch = LearningOrchestrator(db)
result = orch.run_learning_cycle(student, "我是零基础，想通过项目实战学会机器学习，希望多给代码案例")

print("=== 画像 ===")
print(result["student"].profile_json[:300])
print()
print("=== 智能体轨迹 ===")
for t in result["traces"]:
    print(f"  {t['agent_name']}: {t['output_summary']}")
print()
print("=== 资源数量 ===")
print(len(result["resources"]))
print()
print("=== 资源标题列表 ===")
for r in result["resources"]:
    print(f"  - [{r['resource_type']}] {r['title']}")

print()
print("=== LLM 模式测试通过 ===")
db.close()
