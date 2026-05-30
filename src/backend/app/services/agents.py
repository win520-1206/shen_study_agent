from dataclasses import dataclass
from typing import Any


PROFILE_DIMENSIONS = {
    "major_background": ["人工智能", "计算机", "电子信息", "数学", "自动化"],
    "learning_goal": ["期末提分", "入门掌握", "项目实战", "考研准备", "竞赛准备"],
    "prerequisite_level": ["零基础", "基础一般", "有编程基础", "学过部分算法"],
    "weak_points": ["线性回归", "逻辑回归", "决策树", "支持向量机", "聚类", "模型评估", "特征工程"],
    "learning_style": ["喜欢看讲解", "喜欢做题", "喜欢代码实战", "喜欢图示化总结"],
    "weekly_hours": ["每周5小时", "每周8小时", "每周10小时", "每周15小时"],
    "exercise_preference": ["选择题", "简答题", "编程题", "混合题型"],
    "target_outcome": ["通过考试", "完成项目", "建立体系", "准备面试"],
}


@dataclass
class AgentResult:
    name: str
    input_summary: str
    output_summary: str
    payload: dict[str, Any]
    decision_reason: str = ""
    impact_on_result: str = ""


class ProfileAgent:
    name = "画像智能体"

    def run(self, student_major: str, message: str) -> AgentResult:
        normalized_message = message.lower()
        weak_points = [item for item in PROFILE_DIMENSIONS["weak_points"] if item in message]
        if not weak_points:
            if any(k in message for k in ["考", "提分", "考点", "题型"]):
                weak_points = ["模型评估", "逻辑回归"]
            elif any(k in message for k in ["项目", "实战", "sklearn", "实验"]):
                weak_points = ["特征工程", "线性回归"]
            else:
                weak_points = ["线性回归", "模型评估"]

        # 优先级：考试刷题 > 代码实战 > 图示总结 > 看讲解
        # 考试场景关键词优先判断，避免被"项目/实战"误触
        exam_keywords = ["刷题", "做题", "重点题型", "提分", "易错点", "高频考点", "题型", "考点"]
        code_keywords = ["代码", "实战", "sklearn", "实验", "项目", "代码案例"]
        visual_keywords = ["图示", "可视化", "思维导图", "总结", "框架"]

        if any(k in message for k in exam_keywords) and not any(k in message for k in code_keywords):
            learning_style = "喜欢做题"
        elif any(k in message for k in code_keywords):
            learning_style = "喜欢代码实战"
        elif any(k in message for k in visual_keywords):
            learning_style = "喜欢图示化总结"
        else:
            learning_style = "喜欢看讲解"

        # 优先判断考试场景
        if any(k in message for k in ["考试", "提分", "高频考点", "易错点", "重点题型", "题型", "考点", "考过"]):
            goal = "期末提分"
        elif any(k in message for k in ["项目", "实战", "实验", "sklearn"]):
            goal = "项目实战"
        elif any(k in message for k in ["竞赛", "比赛"]):
            goal = "竞赛准备"
        elif any(k in message for k in ["面试"]):
            goal = "准备面试"
        else:
            goal = "入门掌握"

        if any(k in message for k in ["零基础", "几乎零基础", "完全不会"]):
            prerequisite = "零基础"
        elif any(k in normalized_message for k in ["python", "sklearn"]) or "编程基础" in message:
            prerequisite = "有编程基础"
        elif any(k in message for k in ["学过", "接触过", "部分算法"]):
            prerequisite = "学过部分算法"
        else:
            prerequisite = "基础一般"

        if any(k in message for k in ["时间不多", "赶时间"]):
            weekly_hours = "每周5小时"
        elif any(k in message for k in ["每天", "高强度", "冲刺"]):
            weekly_hours = "每周15小时"
        elif any(k in message for k in ["周末", "课余"]):
            weekly_hours = "每周8小时"
        else:
            weekly_hours = "每周10小时"

        if any(k in message for k in ["编程", "代码", "实验", "项目"]):
            exercise_preference = "编程题"
        elif any(k in message for k in ["刷题", "重点题型", "选择题", "易错点", "高频考点", "题型", "做题"]):
            exercise_preference = "选择题"
        elif any(k in message for k in ["简答", "概念", "解释"]):
            exercise_preference = "简答题"
        else:
            exercise_preference = "混合题型"

        if goal == "项目实战":
            target_outcome = "完成项目"
        elif goal == "期末提分":
            target_outcome = "通过考试"
        elif goal == "竞赛准备":
            target_outcome = "建立体系"
        elif goal == "准备面试":
            target_outcome = "准备面试"
        else:
            target_outcome = "建立体系"

        profile = {
            "major_background": student_major,
            "learning_goal": goal,
            "prerequisite_level": prerequisite,
            "weak_points": weak_points,
            "learning_style": learning_style,
            "weekly_hours": weekly_hours,
            "exercise_preference": exercise_preference,
            "target_outcome": target_outcome,
        }
        return AgentResult(
            name=self.name,
            input_summary=f"专业={student_major}; 用户输入={message[:80]}",
            output_summary=f"抽取了8维画像，薄弱点={','.join(weak_points)}",
            payload=profile,
            decision_reason="根据学生自述中的目标、基础、偏好和关键词提取学习画像，并优先识别薄弱知识点。",
            impact_on_result=f"决定后续诊断重点、资源风格以及学习路径起点，当前重点为{','.join(weak_points)}。",
        )


class DiagnosisAgent:
    name = "诊断智能体"

    def run(self, profile: dict[str, Any], kb_hits: list[dict[str, Any]]) -> AgentResult:
        first_hit = kb_hits[0]
        if profile["learning_goal"] == "项目实战":
            strategy = "先跑通案例再回补原理，优先完成可执行实验与代码复盘"
            risk_alert = "容易只顾跑代码而忽视评价指标和特征工程细节"
            focus_unit = "特征构造" if "特征工程" in profile["weak_points"] else first_hit["knowledge_units"][0]
        elif profile["learning_goal"] == "期末提分":
            strategy = "先抓高频考点和易错点，再做针对性练习与错题复盘"
            risk_alert = "时间有限时，容易只背结论而不理解指标适用场景"
            focus_unit = "准确率与召回率" if "模型评估" in profile["weak_points"] else first_hit["knowledge_units"][0]
        elif profile["prerequisite_level"] == "零基础":
            strategy = "先讲概念再做简单练习，先建立全局框架再进入代码实验"
            risk_alert = "概念、公式和术语可能形成连续理解障碍"
            focus_unit = first_hit["knowledge_units"][0]
        else:
            strategy = "先概念后代码，先单模型后综合评估"
            risk_alert = "数学基础与评估指标理解可能成为阻塞点"
            focus_unit = first_hit["knowledge_units"][0]

        priority_modules = [hit["module_name"] for hit in kb_hits[:3]]
        if profile["learning_goal"] == "期末提分" and "模型评估与过拟合控制" not in priority_modules:
            priority_modules = ["模型评估与过拟合控制"] + priority_modules[:2]
        if profile["learning_goal"] == "项目实战" and "数据预处理与特征工程" not in priority_modules:
            priority_modules = ["数据预处理与特征工程"] + priority_modules[:2]

        diagnosis = {
            "current_stage": "基础巩固阶段" if profile["prerequisite_level"] == "零基础" else "能力提升阶段",
            "priority_modules": priority_modules,
            "weak_points": profile["weak_points"],
            "recommended_strategy": strategy,
            "risk_alert": risk_alert,
            "focus_knowledge_unit": focus_unit,
        }
        return AgentResult(
            name=self.name,
            input_summary=f"画像薄弱点={profile['weak_points']}; 命中模块={len(kb_hits)}",
            output_summary=f"推荐优先模块={diagnosis['priority_modules'][0]}",
            payload=diagnosis,
            decision_reason="结合学生目标、基础水平和知识库命中结果，判断当前最该优先攻克的模块与风险点。",
            impact_on_result=f"决定资源生成聚焦在{diagnosis['focus_knowledge_unit']}，并把{diagnosis['priority_modules'][0]}设为优先模块。",
        )


class ResourcePlannerAgent:
    name = "资源规划智能体"

    def run(self, profile: dict[str, Any], diagnosis: dict[str, Any]) -> AgentResult:
        if profile["learning_goal"] == "期末提分":
            tone = "考点速览"
            difficulty = "基础版" if profile["prerequisite_level"] == "零基础" else "进阶版"
        elif profile["learning_style"] == "喜欢代码实战":
            tone = "任务驱动"
            difficulty = "进阶版"
        elif profile["prerequisite_level"] == "零基础":
            tone = "分步教学"
            difficulty = "基础版"
        else:
            tone = "分步教学"
            difficulty = "进阶版"

        plan = {
            "resource_types": ["lesson_note", "quiz", "coding_case", "mind_map", "study_path"],
            "difficulty": difficulty,
            "tone": tone,
            "focus": diagnosis["focus_knowledge_unit"],
        }
        return AgentResult(
            name=self.name,
            input_summary=f"学习风格={profile['learning_style']}; 当前阶段={diagnosis['current_stage']}",
            output_summary="规划了5类个性化资源",
            payload=plan,
            decision_reason="根据学习目标、学习风格和当前阶段，确定资源类型、表达语气与难度层级。",
            impact_on_result=f"最终资源将以{tone}风格呈现，整体难度为{difficulty}。",
        )


class ContentGeneratorAgent:
    name = "内容生成智能体"

    def run(self, profile: dict[str, Any], diagnosis: dict[str, Any], kb_hits: list[dict[str, Any]], kb_service) -> AgentResult:
        module = kb_hits[0]
        content = kb_service.get_module_content(module["module_id"])
        questions = kb_service.get_questions_by_module(module["module_id"])
        coding_cases = kb_service.get_coding_cases_by_module(module["module_id"])
        lesson_sections = [section.strip() for section in content.split("##") if section.strip()]

        goal = profile["learning_goal"]
        style = profile["learning_style"]
        prereq = profile["prerequisite_level"]

        # 根据学生画像选择不同的讲义切片和引导语
        if goal == "期末提分":
            lesson_sections_to_use = lesson_sections[:2]
            lesson_intro = "考试重点速览：以下内容覆盖高频考点和常见易错点，请优先掌握。"
        elif goal == "项目实战":
            lesson_sections_to_use = lesson_sections[:4]
            lesson_intro = "实操导向讲义：建议边读边动手，遇到不理解的概念先记录，后续通过代码案例加深理解。"
        elif prereq == "零基础":
            lesson_sections_to_use = lesson_sections[:2]
            lesson_intro = "通俗入门讲义：先建立整体认知，不必纠结每一个公式，重点理解核心思想。"
        else:
            lesson_sections_to_use = lesson_sections[:3]
            lesson_intro = "系统学习讲义：建议先通读一遍了解结构，再重点攻克薄弱环节。"
        lesson_excerpt = "\n\n".join(f"## {section}" for section in lesson_sections_to_use)

        # 题目选择策略
        if goal == "期末提分" and len(questions) >= 4:
            selected_questions = questions[:4]
            quiz_intro = "考试强化练习：以下题目覆盖常见考点和易错点，建议限时完成并核对参考要点。"
        elif style == "喜欢代码实战":
            selected_questions = questions[:2]
            quiz_intro = "精简练习：快速检验核心概念理解，更多精力留给代码实操。"
        else:
            selected_questions = questions[:3]
            quiz_intro = "综合练习：建议先独立作答，再对照参考要点查漏补缺。"

        # 代码案例选择策略
        selected_case = coding_cases[0] if coding_cases else None
        if goal == "项目实战" and len(coding_cases) >= 2:
            selected_case = coding_cases[1] if coding_cases[1]["difficulty"] == "进阶" else coding_cases[0]
            case_intro = "项目实战案例：建议完整跑通后尝试修改参数，观察结果变化并记录实验心得。"
        elif goal == "期末提分":
            case_intro = "考试关联案例：重点理解每一步在做什么，考试中可能以简答或分析题形式出现。"
        elif prereq == "零基础":
            case_intro = "入门引导案例：先跑通看看结果，不必一次理解所有代码，重点感受整体流程。"
        else:
            case_intro = "标准实操案例：按步骤完成实验，重点关注指标含义和参数影响。"

        # 学习任务清单策略
        if goal == "期末提分":
            task_content = (
                "1. 快速阅读讲义中的核心概念和高频考点标记。\n"
                "2. 限时完成练习题，重点记录自己没答到的参考要点。\n"
                "3. 对照代码案例理解实验步骤，思考可能的简答题问法。\n"
                "4. 用思维导图整理本模块考点清单，标注自己的易错点。"
            )
        elif goal == "项目实战":
            task_content = (
                "1. 阅读讲义时重点关注可操作的步骤和原理。\n"
                "2. 快速完成概念题检验理解后，立刻进入代码案例。\n"
                "3. 完整跑通代码案例，尝试修改 1-2 个参数观察变化。\n"
                "4. 用思维导图总结实验流程和关键发现，记录可改进点。"
            )
        elif prereq == "零基础":
            task_content = (
                "1. 先通读讲义，圈出不理解的术语，不用急着记公式。\n"
                "2. 完成基础概念题，重点理解每个知识点的含义。\n"
                "3. 对照代码案例逐步操作，先跑通再说，不求一次理解。\n"
                "4. 用思维导图复盘本模块，用自己的话总结核心思想。"
            )
        else:
            task_content = (
                "1. 先阅读个性化讲义，圈出自己最不懂的 2 个概念。\n"
                "2. 完成练习题，尤其关注参考要点中自己没答到的部分。\n"
                "3. 按代码案例步骤完成一次最小实验，并记录实验现象。\n"
                "4. 最后用思维导图复盘本模块结构，写出自己的错题与易混点总结。"
            )

        # 根据学习风格给资源标题加标签
        style_tag = {"喜欢看讲解": "[讲解型]", "喜欢做题": "[刷题型]", "喜欢代码实战": "[实操型]", "喜欢图示化总结": "[总结型]"}.get(style, "")

        resources = [
            {
                "resource_type": "lesson_note",
                "title": f"{module['module_name']}个性化讲解 {style_tag}",
                "content": (
                    f"{lesson_intro}\n\n"
                    f"学生画像：{prereq} / {goal} / {style}\n"
                    f"当前重点攻克：{', '.join(profile['weak_points'])}\n\n"
                    f"{lesson_excerpt}"
                ),
                "source_refs": [module["module_id"], f"{module['module_id']}.md"],
            },
            {
                "resource_type": "quiz",
                "title": f"{module['module_name']}练习题 {style_tag}",
                "content": "\n\n".join(
                    [quiz_intro]
                    + [
                        f"{index + 1}. [{question['difficulty']}/{question['type']}] {question['question']}\n参考要点：{'、'.join(question['expected_points'])}"
                        for index, question in enumerate(selected_questions)
                    ]
                ),
                "source_refs": [module["module_id"], "question_bank.json"],
            },
            {
                "resource_type": "coding_case",
                "title": f"{module['module_name']}代码实操 {style_tag}",
                "content": (
                    f"{case_intro}\n\n"
                    f"案例标题：{selected_case['title']}\n"
                    f"学习目标：{selected_case['goal']}\n"
                    f"难度：{selected_case['difficulty']}\n"
                    f"场景：{selected_case['scenario']}\n\n"
                    "推荐步骤：\n"
                    + "\n".join([f"- {step}" for step in selected_case["steps"]])
                    + f"\n\n预期收获：{selected_case['expected_output']}"
                    if selected_case
                    else "当前模块暂未配置代码案例，请先完成讲义和练习题学习。"
                ),
                "source_refs": [module["module_id"], "coding_cases.json"],
            },
            {
                "resource_type": "mind_map",
                "title": f"{module['module_name']}思维导图 {style_tag}",
                "content": (
                    "```mermaid\n"
                    "mindmap\n"
                    f"  root(({module['module_name']}学习路径))\n"
                    f"    {module['module_name']}\n"
                    "      核心概念\n"
                    f"      {diagnosis['focus_knowledge_unit']}\n"
                    f"      当前目标：{goal}\n"
                    f"      学习风格：{style}\n"
                    "      常见误区\n"
                    "      实践建议\n"
                    "```"
                ),
                "source_refs": [module["module_id"], f"{module['module_id']}.md"],
            },
            {
                "resource_type": "study_path",
                "title": f"本轮学习任务清单 {style_tag}",
                "content": task_content,
                "source_refs": [module["module_id"], "question_bank.json", "coding_cases.json"],
            },
        ]
        return AgentResult(
            name=self.name,
            input_summary=f"重点知识点={diagnosis['focus_knowledge_unit']}; 命中模块={module['module_name']}",
            output_summary=f"完成5类资源生成，风格={style}，目标={goal}，整合了{len(selected_questions)}道题与{1 if selected_case else 0}个代码案例",
            payload={"resources": resources},
            decision_reason="围绕优先模块、学生目标和基础水平，从知识库中挑选讲义切片、题目与案例进行个性化重组。",
            impact_on_result=f"生成的讲义、练习、代码案例和任务清单会明显体现{goal}与{style}差异。",
        )


class PathPlannerAgent:
    name = "路径规划智能体"

    def run(self, profile: dict[str, Any], diagnosis: dict[str, Any], resources: list[dict[str, Any]]) -> AgentResult:
        goal = profile["learning_goal"]
        prereq = profile["prerequisite_level"]

        if goal == "期末提分":
            plan = [
                {
                    "stage": "阶段1：抓考点",
                    "objectives": ["识别高频考点", "标注薄弱知识点"],
                    "recommended_resources": [resources[0]["title"], resources[3]["title"]],
                    "practice_task": "完成 4 道强化题，重点记录自己没答到的参考要点",
                    "rationale": "先建立考点清单和知识框架，避免一上来盲目刷题。",
                },
                {
                    "stage": "阶段2：刷题纠错",
                    "objectives": ["巩固易错题型", "掌握评价指标含义"],
                    "recommended_resources": [resources[1]["title"]],
                    "practice_task": "限时完成练习题并整理错题本",
                    "rationale": "在明确重点后进行针对性练习，更容易快速提分。",
                },
                {
                    "stage": "阶段3：案例串联",
                    "objectives": ["理解实验步骤", "应对简答分析题"],
                    "recommended_resources": [resources[2]["title"]],
                    "practice_task": "对照代码案例，口述每一步在做什么以及为什么",
                    "rationale": "用案例把概念和题目串起来，帮助应对综合题与分析题。",
                },
            ]
        elif goal == "项目实战":
            plan = [
                {
                    "stage": "阶段1：通读原理",
                    "objectives": ["了解核心概念", "明确可操作步骤"],
                    "recommended_resources": [resources[0]["title"], resources[3]["title"]],
                    "practice_task": "阅读讲义并标注 3 个最想动手验证的点",
                    "rationale": "先理解整体原理，再进入实操，能减少只会跑代码不会解释的问题。",
                },
                {
                    "stage": "阶段2：跑通案例",
                    "objectives": ["完整执行实验", "理解关键代码逻辑"],
                    "recommended_resources": [resources[2]["title"]],
                    "practice_task": "完整跑通代码案例并记录运行结果",
                    "rationale": "先获得可运行结果，建立正反馈和项目把控感。",
                },
                {
                    "stage": "阶段3：改参实验",
                    "objectives": ["修改参数观察变化", "形成实验报告"],
                    "recommended_resources": [resources[1]["title"]],
                    "practice_task": "修改 1-2 个参数并对比结果差异，写出实验心得",
                    "rationale": "通过改参和复盘，把会运行升级为会分析和会优化。",
                },
            ]
        elif prereq == "零基础":
            plan = [
                {
                    "stage": "阶段1：建立认知",
                    "objectives": ["理解核心概念", "消除术语障碍"],
                    "recommended_resources": [resources[0]["title"], resources[3]["title"]],
                    "practice_task": "用自己的话解释 3 个核心概念",
                    "rationale": "零基础先建立概念框架，比直接做代码更容易进入状态。",
                },
                {
                    "stage": "阶段2：基础练习",
                    "objectives": ["检验理解程度", "积累做题经验"],
                    "recommended_resources": [resources[1]["title"]],
                    "practice_task": "完成概念题，重点理解每个选项背后的道理",
                    "rationale": "通过低门槛练习确认概念是否真正理解。",
                },
                {
                    "stage": "阶段3：初步实操",
                    "objectives": ["跑通基础案例", "感受机器学习流程"],
                    "recommended_resources": [resources[2]["title"]],
                    "practice_task": "跟着代码案例逐步操作，先跑通再说",
                    "rationale": "在已有基础认知后接触代码，更容易把流程与概念对应起来。",
                },
            ]
        else:
            plan = [
                {
                    "stage": "阶段1：打基础",
                    "objectives": ["理解核心概念", "识别常见误区"],
                    "recommended_resources": [resources[0]["title"], resources[3]["title"]],
                    "practice_task": "完成3道概念题并写出自己的理解",
                    "rationale": "先建立统一概念基础，后续练习和代码更容易对上知识点。",
                },
                {
                    "stage": "阶段2：做练习",
                    "objectives": ["会选模型", "会看评估结果"],
                    "recommended_resources": [resources[1]["title"]],
                    "practice_task": "完成练习题并记录错题原因",
                    "rationale": "通过练习定位误区，避免只学不练。",
                },
                {
                    "stage": "阶段3：做代码",
                    "objectives": ["跑通案例", "解释关键代码"],
                    "recommended_resources": [resources[2]["title"]],
                    "practice_task": "修改代码中的参数并观察结果变化",
                    "rationale": "最后通过实操把抽象概念转化为可解释的实验体验。",
                },
            ]

        return AgentResult(
            name=self.name,
            input_summary=f"学习目标={goal}; 当前阶段={diagnosis['current_stage']}",
            output_summary=f"生成{len(plan)}阶段学习路径，目标类型={goal}",
            payload={"study_plan": plan},
            decision_reason="结合学生目标与先修基础，把资源组织成由浅入深、由认知到实践的阶段式路径。",
            impact_on_result=f"最终学习顺序被设计为先解决{diagnosis['focus_knowledge_unit']}，再逐步扩展到完整模块能力。",
        )


class ReviewAgent:
    name = "审查智能体"

    def run(self, resources: list[dict[str, Any]], kb_hits: list[dict[str, Any]]) -> AgentResult:
        issues = []
        if len(resources) < 5:
            issues.append("资源类型不足")
        if not all(resource["source_refs"] for resource in resources):
            issues.append("存在未标注来源的资源")
        output = "通过基础校验" if not issues else f"发现问题：{','.join(issues)}"
        return AgentResult(
            name=self.name,
            input_summary=f"资源数量={len(resources)}; 参考模块={len(kb_hits)}",
            output_summary=output,
            payload={"passed": not issues, "issues": issues},
            decision_reason="检查资源数量、来源标注和基础完整性，确认输出不是无依据的裸生成。",
            impact_on_result="为最终展示补上可信度说明，降低内容缺失和无来源输出的风险。",
        )
