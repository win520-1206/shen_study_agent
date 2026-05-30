from fastapi.testclient import TestClient
from src.backend.app.main import app
import json
from pathlib import Path

client = TestClient(app)
out = []

cases = [
    {
        'label': '学生A-零基础讲解型',
        'name': '学生A5',
        'major': '人工智能',
        'message': '我是人工智能专业大一学生，机器学习几乎零基础，现在最怕公式和模型概念看不懂。我想先把监督学习、线性回归和模型评估这些基础概念真正弄明白，希望系统讲得通俗一点，先别太难，也不用一开始就上很多代码。'
    },
    {
        'label': '学生B-项目实战型',
        'name': '学生B5',
        'major': '计算机',
        'message': '我是计算机专业学生，有 Python 基础，也写过一点 sklearn 代码。我现在想通过项目实战系统学习机器学习，重点想掌握线性回归、逻辑回归和特征工程，希望多给我代码案例、实验任务和实践路线。'
    },
    {
        'label': '学生C-考试提分型',
        'name': '学生C5',
        'major': '电子信息',
        'message': '我是电子信息专业学生，这学期要考机器学习课程，现在时间不多，最想解决的是考试重点抓不住、做题总出错。我希望系统能帮我找出高频考点、易错点和重点题型，最好按提分思路来安排学习内容。'
    }
]

for case in cases:
    create_resp = client.post('/api/v1/students', json={
        'name': case['name'],
        'major': case['major'],
        'target_course': '机器学习基础'
    })
    student_id = create_resp.json()['id']
    profile_resp = client.post('/api/v1/chat/profile-build', json={
        'student_id': student_id,
        'message': case['message']
    })
    data = profile_resp.json()
    profile = data['student']['profile']
    diagnosis = data['diagnosis']
    resources = data['resources']
    study_plan = data['study_plan']

    out.append({
        'label': case['label'],
        'profile': {
            'learning_goal': profile['learning_goal'],
            'learning_style': profile['learning_style'],
            'exercise_preference': profile['exercise_preference'],
            'target_outcome': profile['target_outcome'],
            'weak_points': profile['weak_points'],
            'prerequisite_level': profile['prerequisite_level'],
            'weekly_hours': profile['weekly_hours']
        },
        'diagnosis': {
            'current_stage': diagnosis['current_stage'],
            'priority_modules': diagnosis['priority_modules'],
            'focus_knowledge_unit': diagnosis['focus_knowledge_unit'],
            'recommended_strategy': diagnosis['recommended_strategy']
        },
        'resource_summaries': [
            {'type': r['resource_type'], 'title': r['title'], 'excerpt': r['content'][:120]}
            for r in resources
        ],
        'study_plan': [
            {'stage': p['stage'], 'task': p['practice_task']}
            for p in study_plan
        ]
    })

output_path = Path('runtime') / 'week3_day3_comparison.json'
output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(output_path)
