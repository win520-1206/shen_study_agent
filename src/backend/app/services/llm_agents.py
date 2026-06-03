import json
from typing import Any

from .agents import AgentResult
from .knowledge_base import KnowledgeBaseService
from .llm_service import LLMService


class LLMProfileAgent:
    name = "\u753b\u50cf\u667a\u80fd\u4f53(LLM)"

    SYSTEM_PROMPT = (
        "\u4f60\u662f\u4e00\u4e2a\u5b66\u4e60\u753b\u50cf\u5206\u6790\u52a9\u624b\u3002"
        "\u4f60\u7684\u4efb\u52a1\u662f\u4ece\u5b66\u751f\u7684\u81ea\u7136\u8bed\u8a00\u63cf\u8ff0\u4e2d\u51c6\u786e\u63d0\u53d6 8 \u4e2a\u7ef4\u5ea6\u7684\u5b66\u4e60\u753b\u50cf\u4fe1\u606f\u3002\n"
        "\u91cd\u8981\u89c4\u5219\uff1a\n"
        "1. \u53ea\u8fd4\u56de\u7eaf JSON\uff0c\u4e0d\u8981\u4efb\u4f55\u89e3\u91ca\u6587\u5b57\n"
        "2. \u5982\u679c\u5b66\u751f\u7684\u63cf\u8ff0\u4e2d\u5df2\u7ecf\u660e\u786e\u7ed9\u51fa\u4e86\u753b\u50cf\u7ef4\u5ea6\uff0c\u8bf7\u76f4\u63a5\u91c7\u7528\n"
        "3. \u5982\u679c\u5b66\u751f\u8bf4\u4e0d\u60f3\u5199\u5f88\u591a\u4ee3\u7801\uff0clearning_style \u5e94\u9009\u559c\u6b22\u770b\u8bb2\u89e3\n"
        "4. \u5982\u679c\u5b66\u751f\u63d0\u5230\u5237\u9898\u3001\u505a\u9898\u3001\u63d0\u5206\uff0clearning_style \u5e94\u9009\u559c\u6b22\u505a\u9898\n"
        "5. \u5224\u65ad\u5b66\u4e60\u98ce\u683c\u65f6\uff0c\u8981\u770b\u5b66\u751f\u5b9e\u9645\u60f3\u505a\u4ec0\u4e48"
    )

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, student_major: str, message: str) -> AgentResult:
        user_prompt = (
            f"\u5b66\u751f\u8bf4\u4e86\u4ee5\u4e0b\u5185\u5bb9\uff1a\n\"{message}\"\n\n"
            "\u8bf7\u63d0\u53d6\u4ee5\u4e0b 8 \u4e2a\u7ef4\u5ea6\u7684\u4fe1\u606f\uff0c\u4ee5 JSON \u683c\u5f0f\u8fd4\u56de\uff1a\n"
            "1. major_background\uff1a\u4e13\u4e1a\u80cc\u666f\n"
            "2. learning_goal\uff1a\u4ece \u671f\u672b\u63d0\u5206/\u5165\u95e8\u638c\u63e1/\u9879\u76ee\u5b9e\u6218/\u8003\u7814\u51c6\u5907/\u7ade\u8d5b\u51c6\u5907 \u4e2d\u9009\u4e00\u4e2a\n"
            "3. prerequisite_level\uff1a\u4ece \u96f6\u57fa\u7840/\u57fa\u7840\u4e00\u822c/\u6709\u7f16\u7a0b\u57fa\u7840/\u5b66\u8fc7\u90e8\u5206\u7b97\u6cd5 \u4e2d\u9009\u4e00\u4e2a\n"
            "4. weak_points\uff1a\u4ece \u7ebf\u6027\u56de\u5f52/\u903b\u8f91\u56de\u5f52/\u51b3\u7b56\u6811/\u652f\u6301\u5411\u91cf\u673a/\u805a\u7c7b/\u6a21\u578b\u8bc4\u4f30/\u7279\u5f81\u5de5\u7a0b \u4e2d\u9009\u76f8\u5173\u9879\uff0c\u8fd4\u56de\u5217\u8868\n"
            "5. learning_style\uff1a\u4ece \u559c\u6b22\u770b\u8bb2\u89e3/\u559c\u6b22\u505a\u9898/\u559c\u6b22\u4ee3\u7801\u5b9e\u6218/\u559c\u6b22\u56fe\u793a\u5316\u603b\u7ed3 \u4e2d\u9009\u4e00\u4e2a\n"
            "6. weekly_hours\uff1a\u4ece \u6bcf\u54685\u5c0f\u65f6/\u6bcf\u54688\u5c0f\u65f6/\u6bcf\u546810\u5c0f\u65f6/\u6bcf\u546815\u5c0f\u65f6 \u4e2d\u9009\u4e00\u4e2a\n"
            "7. exercise_preference\uff1a\u4ece \u9009\u62e9\u9898/\u7b80\u7b54\u9898/\u7f16\u7a0b\u9898/\u6df7\u5408\u9898\u578b \u4e2d\u9009\u4e00\u4e2a\n"
            "8. target_outcome\uff1a\u4ece \u901a\u8fc7\u8003\u8bd5/\u5b8c\u6210\u9879\u76ee/\u5efa\u7acb\u4f53\u7cfb/\u51c6\u5907\u9762\u8bd5 \u4e2d\u9009\u4e00\u4e2a\n\n"
            "\u53ea\u8fd4\u56de\u7eaf JSON\uff0c\u4e0d\u8981\u5176\u4ed6\u6587\u5b57\u3002"
        )
        result = self.llm_service.chat_json(self.SYSTEM_PROMPT, user_prompt)
        result["major_background"] = student_major
        if not result.get("weak_points"):
            result["weak_points"] = ["\u7ebf\u6027\u56de\u5f52", "\u6a21\u578b\u8bc4\u4f30"]
        return AgentResult(
            name=self.name,
            input_summary=f"\u4e13\u4e1a={student_major}; \u7528\u6237\u8f93\u5165={message[:80]}",
            output_summary=f"(LLM)\u62bd\u53d6\u4e86{len(result)}\u7ef4\u753b\u50cf",
            payload=result,
        )


class LLMDiagnosisAgent:
    name = "\u8bca\u65ad\u667a\u80fd\u4f53(LLM)"

    SYSTEM_PROMPT = (
        "\u4f60\u662f\u4e00\u4e2a\u673a\u5668\u5b66\u4e60\u5b66\u4e60\u8bca\u65ad\u4e13\u5bb6\u3002"
        "\u6839\u636e\u5b66\u751f\u7684\u753b\u50cf\u4fe1\u606f\uff0c\u5206\u6790\u5176\u8584\u5f31\u73af\u8282\uff0c"
        "\u63a8\u8350\u5b66\u4e60\u7b56\u7565\u548c\u4f18\u5148\u6a21\u5757\u3002\u53ea\u8fd4\u56de\u7eaf JSON\uff0c\u4e0d\u8981\u4efb\u4f55\u89e3\u91ca\u6587\u5b57\u3002"
    )

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, profile: dict[str, Any], kb_hits: list[dict[str, Any]]) -> AgentResult:
        priority_modules = [hit["module_name"] for hit in kb_hits[:3]]
        weak_points_str = ", ".join(profile["weak_points"])
        modules_str = ", ".join(priority_modules)

        NL = "\n"
        json_block = (
            "{" + NL
            + '  "current_stage": "\u57fa\u7840\u5de9\u56fa\u9636\u6bb5 \u6216 \u80fd\u529b\u63d0\u5347\u9636\u6bb5",' + NL
            + '  "priority_modules": ["\u63a8\u8350\u7684\u4f18\u5148\u5b66\u4e60\u6a21\u5757\u5217\u8868"],' + NL
            + '  "weak_points": ["\u8584\u5f31\u77e5\u8bc6\u70b9\u5217\u8868"],' + NL
            + '  "recommended_strategy": "\u4e00\u6bb550-100\u5b57\u7684\u5177\u4f53\u5b66\u4e60\u7b56\u7565\u5efa\u8bae",' + NL
            + '  "risk_alert": "\u4e00\u6bb530-60\u5b57\u7684\u98ce\u9669\u63d0\u793a",' + NL
            + '  "focus_knowledge_unit": "\u5f53\u524d\u6700\u5e94\u4f18\u5148\u653b\u514b\u7684\u77e5\u8bc6\u70b9"' + NL
            + "}" + NL + NL
            + "\u53ea\u8fd4\u56de\u7eaf JSON\u3002"
        )

        user_prompt = (
            f"\u5b66\u751f\u753b\u50cf\uff1a\n"
            f"- \u57fa\u7840\u6c34\u5e73\uff1a{profile['prerequisite_level']}\n"
            f"- \u5b66\u4e60\u76ee\u6807\uff1a{profile['learning_goal']}\n"
            f"- \u5b66\u4e60\u98ce\u683c\uff1a{profile['learning_style']}\n"
            f"- \u8584\u5f31\u70b9\uff1a{weak_points_str}\n"
            f"- \u53ef\u9009\u6a21\u5757\uff1a{modules_str}\n\n"
            f"\u8bf7\u8fd4\u56de\u4ee5\u4e0b JSON\uff1a\n"
            + json_block
        )

        result = self.llm_service.chat_json(self.SYSTEM_PROMPT, user_prompt)
        result.setdefault("priority_modules", priority_modules)
        result.setdefault("weak_points", profile["weak_points"])
        result.setdefault("current_stage", "\u57fa\u7840\u5de9\u56fa\u9636\u6bb5")
        result.setdefault("recommended_strategy", "\u5efa\u8bae\u4ece\u57fa\u7840\u6982\u5ff5\u5165\u624b\uff0c\u5faa\u5e8f\u6e10\u8fdb\u3002")
        result.setdefault("risk_alert", "")
        result.setdefault("focus_knowledge_unit", kb_hits[0]["knowledge_units"][0] if kb_hits else "\u7ebf\u6027\u56de\u5f52")

        return AgentResult(
            name=self.name,
            input_summary=f"\u753b\u50cf\u8584\u5f31\u70b9={profile['weak_points']}; \u547d\u4e2d\u6a21\u5757={len(kb_hits)}",
            output_summary=f"(LLM)\u63a8\u8350\u4f18\u5148\u6a21\u5757={result['priority_modules'][0] if result.get('priority_modules') else '\u672a\u77e5'}",
            payload=result,
        )


class LLMContentGeneratorAgent:
    name = "\u5185\u5bb9\u751f\u6210\u667a\u80fd\u4f53(LLM)"

    SYSTEM_PROMPT = (
        "\u4f60\u662f\u4e00\u4e2a\u673a\u5668\u5b66\u4e60\u8bfe\u7a0b\u7684\u4e2a\u6027\u5316\u5b66\u4e60\u52a9\u624b\u3002"
        "\u6839\u636e\u5b66\u751f\u753b\u50cf\u548c\u77e5\u8bc6\u5e93\u5185\u5bb9\u751f\u6210\u9ad8\u8d28\u91cf\u5b66\u4e60\u8d44\u6e90\u3002\n"
        "\u91cd\u8981\u8981\u6c42\uff1a\n"
        "1. \u53ea\u8fd4\u56de\u7eaf JSON\uff0c\u4e0d\u8981\u4efb\u4f55\u89e3\u91ca\u6587\u5b57\n"
        "2. \u8bb2\u4e49\u5185\u5bb9\u4e0d\u5c11\u4e8e 200 \u5b57\uff0c\u5fc5\u987b\u901a\u4fd7\u6613\u61c2\n"
        "3. \u7ec3\u4e60\u9898\u5fc5\u987b\u5305\u542b\u53c2\u8003\u7b54\u6848\u8981\u70b9\n"
        "4. \u4ee3\u7801\u6848\u4f8b\u5fc5\u987b\u5305\u542b\u53ef\u8fd0\u884c\u7684\u6b65\u9aa4\u8bf4\u660e\n"
        "5. \u601d\u7ef4\u5bfc\u56fe\u4f7f\u7528 Mermaid mindmap \u683c\u5f0f\n"
        "6. \u5185\u5bb9\u5fc5\u987b\u4f53\u73b0\u5b66\u751f\u753b\u50cf\u7684\u4e2a\u6027\u5316\u5dee\u5f02"
    )

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, profile: dict[str, Any], diagnosis: dict[str, Any], kb_hits: list[dict[str, Any]], kb_service: KnowledgeBaseService) -> AgentResult:
        module = kb_hits[0]
        kb_content = kb_service.get_module_content(module["module_id"])
        kb_context = kb_content[:2000]

        json_part = (
            "\u8bf7\u751f\u6210\u4ee5\u4e0b 5 \u7c7b\u5b66\u4e60\u8d44\u6e90\uff0c\u4ee5 JSON \u683c\u5f0f\u8fd4\u56de\uff1a\n"
            '{"resources": [\n'
            '  {"resource_type": "lesson_note", "title": "...", "content": "200-400\u5b57\u7684\u4e2a\u6027\u5316\u8bb2\u4e49", "source_refs": [...]},\n'
            '  {"resource_type": "quiz", "title": "...", "content": "3\u9053\u7ec3\u4e60\u9898\u542b\u53c2\u8003\u8981\u70b9", "source_refs": [...]},\n'
            '  {"resource_type": "coding_case", "title": "...", "content": "\u4ee3\u7801\u5b9e\u64cd\u4efb\u52a1\u8bf4\u660e\u542b\u6b65\u9aa4", "source_refs": [...]},\n'
            '  {"resource_type": "mind_map", "title": "...", "content": "Mermaid mindmap \u683c\u5f0f\u7684\u601d\u7ef4\u5bfc\u56fe", "source_refs": [...]},\n'
            '  {"resource_type": "study_path", "title": "...", "content": "\u5206\u6b65\u9aa4\u7684\u5b66\u4e60\u4efb\u52a1\u6e05\u5355", "source_refs": [...]}\n'
            ']}\n\n'
            '\u53ea\u8fd4\u56de\u7eaf JSON\u3002'
        )

        user_prompt = (
            f"\u5b66\u751f\u753b\u50cf\uff1a\n"
            f"- \u4e13\u4e1a\uff1a{profile['major_background']}\n"
            f"- \u57fa\u7840\u6c34\u5e73\uff1a{profile['prerequisite_level']}\n"
            f"- \u5b66\u4e60\u98ce\u683c\uff1a{profile['learning_style']}\n"
            f"- \u5b66\u4e60\u76ee\u6807\uff1a{profile['learning_goal']}\n"
            f"- \u8584\u5f31\u70b9\uff1a{', '.join(profile['weak_points'])}\n\n"
            f"\u8bca\u65ad\u63a8\u8350\u7b56\u7565\uff1a{diagnosis.get('recommended_strategy', '')}\n\n"
            f"\u8bfe\u7a0b\u77e5\u8bc6\u5e93\u4e2d\u76f8\u5173\u7684\u5185\u5bb9\uff1a\n"
            f"---\n{kb_context}\n---\n\n"
            + json_part
        )

        result = self.llm_service.chat_json(self.SYSTEM_PROMPT, user_prompt)
        resources = result.get("resources", [])
        for resource in resources:
            resource.setdefault("source_refs", [module["module_id"]])
        if len(resources) < 5:
            resources.append({
                "resource_type": "study_path",
                "title": "\u672c\u8f6e\u5b66\u4e60\u4efb\u52a1\u6e05\u5355",
                "content": "\u8bf7\u4f9d\u6b21\u5b8c\u6210\u8bb2\u4e49\u3001\u7ec3\u4e60\u9898\u3001\u4ee3\u7801\u6848\u4f8b\u548c\u601d\u7ef4\u5bfc\u56fe\u590d\u76d8\u3002",
                "source_refs": [module["module_id"]],
            })
        return AgentResult(
            name=self.name,
            input_summary=f"(LLM)\u77e5\u8bc6\u70b9={diagnosis['focus_knowledge_unit']}; \u6a21\u5757={module['module_name']}",
            output_summary=f"(LLM)\u5b8c\u6210{len(resources)}\u7c7b\u8d44\u6e90\u751f\u6210",
            payload={"resources": resources},
        )


class LLMQAAgent:
    name = "\u7b54\u7591\u667a\u80fd\u4f53(LLM)"

    SYSTEM_PROMPT = (
        "\u4f60\u662f\u4e00\u4e2a\u673a\u5668\u5b66\u4e60\u8bfe\u7a0b\u7684\u7b54\u7591\u52a9\u6559\u3002"
        "\u6839\u636e\u8bfe\u7a0b\u77e5\u8bc6\u5e93\u5185\u5bb9\u56de\u7b54\u5b66\u751f\u7684\u95ee\u9898\u3002\n"
        "\u89c4\u5219\uff1a\n"
        "1. \u56de\u7b54\u5fc5\u987b\u57fa\u4e8e\u63d0\u4f9b\u7684\u77e5\u8bc6\u5e93\u5185\u5bb9\uff0c\u4e0d\u8981\u7f16\u9020\n"
        "2. \u5982\u679c\u77e5\u8bc6\u5e93\u4e2d\u6ca1\u6709\u76f8\u5173\u5185\u5bb9\uff0c\u5982\u5b9e\u544a\u77e5\n"
        "3. \u7528\u901a\u4fd7\u6613\u61c2\u7684\u8bed\u8a00\u89e3\u91ca\uff0c\u9002\u5f53\u4e3e\u4f8b\n"
        "4. \u56de\u7b54\u63a7\u5236\u5728 300 \u5b57\u4ee5\u5185"
    )

    SYSTEM_PROMPT_SOCRATIC = (
        "\u4f60\u662f\u4e00\u4e2a\u673a\u5668\u5b66\u4e60\u8bfe\u7a0b\u7684\u82cf\u683c\u62c9\u5e95\u5f0f\u7b54\u7591\u52a9\u6559\u3002"
        "\u4f60\u4e0d\u4ec5\u56de\u7b54\u95ee\u9898\uff0c\u8fd8\u4f1a\u5f15\u5bfc\u5b66\u751f\u6df1\u5165\u601d\u8003\u3002\n"
        "\u89c4\u5219\uff1a\n"
        "1. \u5148\u57fa\u4e8e\u77e5\u8bc6\u5e93\u5185\u5bb9\u56de\u7b54\u5b66\u751f\u7684\u95ee\u9898\uff0c\u901a\u4fd7\u6613\u61c2\n"
        "2. \u56de\u7b54\u4e3b\u4f53\u63a7\u5236\u5728 200 \u5b57\u4ee5\u5185\n"
        "3. \u5728\u56de\u7b54\u672b\u5c3e\uff0c\u4e3b\u52a8\u629b\u51fa 1 \u4e2a\u5f15\u5bfc\u6027\u95ee\u9898\n"
        "4. \u5f15\u5bfc\u95ee\u9898\u5e94\u8be5\u4e0e\u5f53\u524d\u77e5\u8bc6\u70b9\u76f8\u5173\n"
        "5. \u5982\u679c\u77e5\u8bc6\u5e93\u4e2d\u6ca1\u6709\u76f8\u5173\u5185\u5bb9\uff0c\u5982\u5b9e\u544a\u77e5\n"
        "6. \u5f15\u5bfc\u95ee\u9898\u4ee5\u3010\u601d\u8003\u9898\u3011\u6807\u8bb0"
    )

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, question: str, student_profile: dict[str, Any] | None, kb_context: str, socratic: bool = False) -> AgentResult:
        level_hint = ""
        if student_profile:
            level_hint = (
                f"\n\u5b66\u751f\u57fa\u7840\uff1a{student_profile.get('prerequisite_level', '\u672a\u77e5')}"
                f"\uff0c\u5b66\u4e60\u98ce\u683c\uff1a{student_profile.get('learning_style', '\u672a\u77e5')}"
            )

        system_prompt = self.SYSTEM_PROMPT_SOCRATIC if socratic else self.SYSTEM_PROMPT

        user_prompt = (
            f"\u8bfe\u7a0b\u77e5\u8bc6\u5e93\u5185\u5bb9\uff1a\n---\n{kb_context[:1500]}\n---\n{level_hint}\n\n"
            f"\u5b66\u751f\u63d0\u95ee\uff1a{question}\n\n"
            f"\u8bf7\u57fa\u4e8e\u77e5\u8bc6\u5e93\u5185\u5bb9\u56de\u7b54\u5b66\u751f\u7684\u95ee\u9898\u3002\u5982\u679c\u77e5\u8bc6\u5e93\u4e2d\u6ca1\u6709\u76f8\u5173\u5185\u5bb9\uff0c\u8bf7\u8bf4\u660e\u3002"
        )

        try:
            answer = self.llm_service.chat(system_prompt, user_prompt)
        except Exception:
            answer = f"\u5173\u4e8e \"{question}\"\uff1a\u77e5\u8bc6\u5e93\u4e2d\u6682\u65f6\u6ca1\u6709\u627e\u5230\u76f4\u63a5\u76f8\u5173\u7684\u8be6\u7ec6\u89e3\u7b54\uff0c\u5efa\u8bae\u5148\u9605\u8bfb\u8bfe\u7a0b\u8bb2\u4e49\u4e2d\u7684\u76f8\u5173\u5185\u5bb9\u3002"

        return AgentResult(
            name=self.name,
            input_summary=f"\u95ee\u9898={question[:50]}; socratic={socratic}",
            output_summary=f"\u56de\u7b54\u957f\u5ea6={len(answer)}\u5b57",
            payload={"answer": answer},
        )
