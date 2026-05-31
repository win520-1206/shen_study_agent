import json
from typing import Any

from .agents import AgentResult
from .knowledge_base import KnowledgeBaseService
from .llm_service import LLMService


class LLMProfileAgent:
    """画像智能体 LLM 版：用大模型从自然语言中提取学习画像。"""
    name = "画像智能体(LLM)"

    SYSTEM_PROMPT = (
        "你是一个学习画像分析助手。你的任务是从学生的自然语言描述中准确提取 8 个维度的学习画像信息。\n"
        "重要规则：\n"
        "1. 只返回纯 JSON，不要任何解释文字\n"
        "2. 如果学生的描述中已经明确给出了画像维度（如'学习目标是期末提分'），请直接采用，不要自行推断\n"
        "3. 如果学生说'不想上很多代码'或'不用一开始就写代码'，learning_style 应选'喜欢看讲解'，不能选'喜欢代码实战'\n"
        "4. 如果学生提到'刷题'、'做题'、'提分'、'高频考点'，learning_style 应选'喜欢做题'\n"
        "5. 判断学习风格时，要看学生实际想做什么，而不是提到了什么词"
    )

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, student_major: str, message: str) -> AgentResult:
        user_prompt = (
            f'学生说了以下内容：\n"{message}"\n\n'
            '请提取以下 8 个维度的信息，以 JSON 格式返回：\n'
            '1. major_background：专业背景（直接用 "{student_major}"）\n'
            '2. learning_goal：从 期末提分/入门掌握/项目实战/考研准备/竞赛准备 中选一个\n'
            '3. prerequisite_level：从 零基础/基础一般/有编程基础/学过部分算法 中选一个\n'
            '4. weak_points：从 线性回归/逻辑回归/决策树/支持向量机/聚类/模型评估/特征工程 中选相关项，返回列表\n'
            '5. learning_style：从 喜欢看讲解/喜欢做题/喜欢代码实战/喜欢图示化总结 中选一个\n'
            '6. weekly_hours：从 每周5小时/每周8小时/每周10小时/每周15小时 中选一个\n'
            '7. exercise_preference：从 选择题/简答题/编程题/混合题型 中选一个\n'
            '8. target_outcome：从 通过考试/完成项目/建立体系/准备面试 中选一个\n\n'
            '示例：\n'
            '输入："我是零基础，想通过考试，不想写太多代码"\n'
            '输出：{"prerequisite_level":"零基础","learning_goal":"期末提分","learning_style":"喜欢看讲解",...}\n\n'
            '只返回纯 JSON，不要其他文字。'
        )
        result = self.llm_service.chat_json(self.SYSTEM_PROMPT, user_prompt)
        result["major_background"] = student_major
        if not result.get("weak_points"):
            result["weak_points"] = ["线性回归", "模型评估"]
        return AgentResult(
            name=self.name,
            input_summary=f"专业={student_major}; 用户输入={message[:80]}",
            output_summary=f"(LLM)抽取了{len(result)}维画像",
            payload=result,
        )


class LLMDiagnosisAgent:
    """诊断智能体 LLM 版：用大模型分析薄弱环节并推荐学习策略。"""
    name = "诊断智能体(LLM)"

    SYSTEM_PROMPT = (
        "你是一个机器学习学习诊断专家。根据学生的画像信息，分析其薄弱环节，"
        "推荐学习策略和优先模块。只返回纯 JSON，不要任何解释文字。"
    )

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, profile: dict[str, Any], kb_hits: list[dict[str, Any]]) -> AgentResult:
        priority_modules = [hit["module_name"] for hit in kb_hits[:3]]
        weak_points_str = ", ".join(profile["weak_points"])
        modules_str = ", ".join(priority_modules)

        user_prompt = (
            f"学生画像：\n"
            f"- 基础水平：{profile['prerequisite_level']}\n"
            f"- 学习目标：{profile['learning_goal']}\n"
            f"- 学习风格：{profile['learning_style']}\n"
            f"- 薄弱点：{weak_points_str}\n"
            f"- 可选模块：{modules_str}\n\n"
            f"请返回以下 JSON：\n"
            f'{{\n'
            f'  "current_stage": "基础巩固阶段 或 能力提升阶段",\n'
            f'  "priority_modules": ["推荐的优先学习模块列表"],\n'
            f'  "weak_points": ["薄弱知识点列表"],\n'
            f'  "recommended_strategy": "一段50-100字的具体学习策略建议",\n'
            f'  "risk_alert": "一段30-60字的风险提示",\n'
            f'  "focus_knowledge_unit": "当前最应优先攻克的知识点"\n'
            f'}}\n\n'
            f'只返回纯 JSON。'
        )

        result = self.llm_service.chat_json(self.SYSTEM_PROMPT, user_prompt)
        result.setdefault("priority_modules", priority_modules)
        result.setdefault("weak_points", profile["weak_points"])
        result.setdefault("current_stage", "基础巩固阶段")
        result.setdefault("recommended_strategy", "建议从基础概念入手，循序渐进。")
        result.setdefault("risk_alert", "")
        result.setdefault("focus_knowledge_unit", kb_hits[0]["knowledge_units"][0] if kb_hits else "线性回归")

        return AgentResult(
            name=self.name,
            input_summary=f"画像薄弱点={profile['weak_points']}; 命中模块={len(kb_hits)}",
            output_summary=f"(LLM)推荐优先模块={result['priority_modules'][0] if result.get('priority_modules') else '未知'}",
            payload=result,
        )


class LLMContentGeneratorAgent:
    """内容生成智能体 LLM 版：用大模型根据画像和知识库生成个性化资源。"""
    name = "内容生成智能体(LLM)"

    SYSTEM_PROMPT = (
        "你是一个机器学习课程的个性化学习助手。根据学生画像和知识库内容生成高质量学习资源。\n"
        "重要要求：\n"
        "1. 只返回纯 JSON，不要任何解释文字\n"
        "2. 讲义内容不少于 200 字，必须通俗易懂\n"
        "3. 练习题必须包含参考答案要点\n"
        "4. 代码案例必须包含可运行的步骤说明\n"
        "5. 思维导图使用 Mermaid mindmap 格式\n"
        "6. 内容必须体现学生画像的个性化差异（不同基础、不同目标应有不同内容）"
    )

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, profile: dict[str, Any], diagnosis: dict[str, Any], kb_hits: list[dict[str, Any]], kb_service: KnowledgeBaseService) -> AgentResult:
        module = kb_hits[0]
        kb_content = kb_service.get_module_content(module["module_id"])
        kb_context = kb_content[:2000]

        user_prompt = (
            f"学生画像：\n"
            f"- 专业：{profile['major_background']}\n"
            f"- 基础水平：{profile['prerequisite_level']}\n"
            f"- 学习风格：{profile['learning_style']}\n"
            f"- 学习目标：{profile['learning_goal']}\n"
            f"- 薄弱点：{', '.join(profile['weak_points'])}\n\n"
            f"诊断推荐策略：{diagnosis.get('recommended_strategy', '')}\n\n"
            f"课程知识库中与 \"{module['module_name']}\" 相关的内容：\n"
            f"---\n{kb_context}\n---\n\n"
            '请生成以下 5 类学习资源，以 JSON 格式返回：\n'
            '{"resources": [\n'
            '  {"resource_type": "lesson_note", "title": "...", "content": "200-400字的个性化讲义", "source_refs": [...]},\n'
            '  {"resource_type": "quiz", "title": "...", "content": "3道练习题含参考要点", "source_refs": [...]},\n'
            '  {"resource_type": "coding_case", "title": "...", "content": "代码实操任务说明含步骤", "source_refs": [...]},\n'
            '  {"resource_type": "mind_map", "title": "...", "content": "Mermaid mindmap 格式的思维导图", "source_refs": [...]},\n'
            '  {"resource_type": "study_path", "title": "...", "content": "分步骤的学习任务清单", "source_refs": [...}]}\n'
            ']}\n\n'
            '只返回纯 JSON。'
        )

        result = self.llm_service.chat_json(self.SYSTEM_PROMPT, user_prompt)
        resources = result.get("resources", [])

        for resource in resources:
            resource.setdefault("source_refs", [module["module_id"]])

        if len(resources) < 5:
            resources.append({
                "resource_type": "study_path",
                "title": "本轮学习任务清单",
                "content": "请依次完成讲义、练习题、代码案例和思维导图复盘。",
                "source_refs": [module["module_id"]],
            })

        return AgentResult(
            name=self.name,
            input_summary=f"(LLM)知识点={diagnosis['focus_knowledge_unit']}; 模块={module['module_name']}",
            output_summary=f"(LLM)完成{len(resources)}类资源生成",
            payload={"resources": resources},
        )


class LLMQAAgent:
    """智能答疑智能体：基于知识库回答课程相关问题。"""
    name = "答疑智能体(LLM)"

    SYSTEM_PROMPT = (
        "你是一个机器学习课程的答疑助教。根据课程知识库内容回答学生的问题。\n"
        "规则：\n"
        "1. 回答必须基于提供的知识库内容，不要编造\n"
        "2. 如果知识库中没有相关内容，如实告知\n"
        "3. 用通俗易懂的语言解释，适当举例\n"
        "4. 回答控制在 300 字以内"
    )

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, question: str, student_profile: dict[str, Any] | None, kb_context: str) -> AgentResult:
        level_hint = ""
        if student_profile:
            level_hint = f"\n学生基础：{student_profile.get('prerequisite_level', '未知')}，学习风格：{student_profile.get('learning_style', '未知')}"

        user_prompt = (
            f"课程知识库内容：\n---\n{kb_context[:1500]}\n---\n{level_hint}\n\n"
            f"学生提问：{question}\n\n"
            f"请基于知识库内容回答学生的问题。如果知识库中没有相关内容，请说明。"
        )

        try:
            answer = self.llm_service.chat(self.SYSTEM_PROMPT, user_prompt)
        except Exception:
            answer = f"关于 \"{question}\"：知识库中暂时没有找到直接相关的详细解答，建议先阅读课程讲义中的相关内容。"

        return AgentResult(
            name=self.name,
            input_summary=f"问题={question[:50]}",
            output_summary=f"回答长度={len(answer)}字",
            payload={"answer": answer},
        )
