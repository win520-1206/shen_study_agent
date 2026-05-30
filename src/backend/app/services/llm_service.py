"""LLM service layer for LearnMate-AI.

This module provides the abstraction for calling large language models.
The current version includes:
- LLMService: base interface
- MockLLMService: development/testing fallback
- GenericLLMService: OpenAI-compatible generic API client
- XfyunLLMService: 科大讯飞 API integration scaffold

To switch between implementations, set USE_LLM in config.py.
"""
import json
import logging
from typing import Any, Generator

logger = logging.getLogger(__name__)


class LLMService:
    """Base interface for LLM services.

    All LLM implementations should inherit from this class
    and implement the `chat` method.
    """

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    def chat_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        response = self.chat(system_prompt, user_prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
            raise

    def chat_stream(self, system_prompt: str, user_prompt: str) -> Generator[str, None, None]:
        """Streaming version of chat. Default: yield full response at once."""
        yield self.chat(system_prompt, user_prompt)


class MockLLMService(LLMService):
    """Mock LLM service for development and testing.

    Returns realistic-looking responses without calling any real API.
    Use this when you want to test the LLM agent integration flow
    without spending API credits.
    """

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        # 答疑智能体
        if "答疑" in system_prompt or "答疑" in user_prompt:
            return "关于您提问的知识点：这是 Mock 回答。接入真实 API 后将基于知识库内容生成个性化回答。"
        # 诊断智能体
        if "诊断" in system_prompt:
            return json.dumps({
                "current_stage": "基础巩固阶段",
                "priority_modules": ["线性回归", "模型评估"],
                "weak_points": ["线性回归", "特征工程"],
                "recommended_strategy": "建议从基础概念入手，先理解线性回归的数学原理，再通过代码案例加深理解。",
                "risk_alert": "零基础学生容易在公式推导环节卡住，建议先建立直觉认知。",
                "focus_knowledge_unit": "最小二乘法"
            }, ensure_ascii=False)
        # 画像分析 vs 内容生成
        if "画像分析" in system_prompt or ("提取" in user_prompt and "维度" in user_prompt):
            return json.dumps({
                "major_background": "计算机",
                "learning_goal": "项目实战",
                "prerequisite_level": "有编程基础",
                "weak_points": ["特征工程", "线性回归"],
                "learning_style": "喜欢代码实战",
                "weekly_hours": "每周10小时",
                "exercise_preference": "编程题",
                "target_outcome": "完成项目",
            }, ensure_ascii=False)
        return json.dumps({
            "resources": [
                {
                    "resource_type": "lesson_note",
                    "title": "个性化讲解（Mock）",
                    "content": "这是 Mock LLM 生成的讲义内容，接入真实 API 后将替换为个性化生成。",
                    "source_refs": ["mock"],
                },
                {
                    "resource_type": "quiz",
                    "title": "练习题（Mock）",
                    "content": "1. [Mock] 请解释什么是机器学习？\n参考要点：从数据中学习规律",
                    "source_refs": ["mock"],
                },
                {
                    "resource_type": "coding_case",
                    "title": "代码实操（Mock）",
                    "content": "案例标题：Mock 实验\n学习目标：验证 LLM 接入流程\n推荐步骤：运行代码，观察输出",
                    "source_refs": ["mock"],
                },
                {
                    "resource_type": "mind_map",
                    "title": "思维导图（Mock）",
                    "content": "```mermaid\nmindmap\n  root((Mock))\n    接入测试\n```",
                    "source_refs": ["mock"],
                },
                {
                    "resource_type": "study_path",
                    "title": "学习任务清单（Mock）",
                    "content": "1. 确认 Mock 流程正常\n2. 接入真实 API\n3. 验证个性化效果",
                    "source_refs": ["mock"],
                },
            ]
        }, ensure_ascii=False)


class GenericLLMService(LLMService):
    """通用 OpenAI 兼容格式 LLM 服务。

    支持 DeepSeek、通义千问、讯飞星火 OpenAI 模式等任何提供
    Chat Completions API 的服务。只需配置 base_url、api_key、model。
    """

    def __init__(self, base_url: str, api_key: str, model: str = "deepseek-chat"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._mock = MockLLMService()

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        import httpx

        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
        }

        try:
            resp = httpx.post(url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.warning(
                "GenericLLMService 调用失败，fallback 到 Mock: %s", exc
            )
            return self._mock.chat(system_prompt, user_prompt)

    def chat_stream(self, system_prompt: str, user_prompt: str) -> Generator[str, None, None]:
        """Stream response chunks from OpenAI-compatible API."""
        import httpx

        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
            "stream": True,
        }

        try:
            with httpx.Client(timeout=120) as client:
                with client.stream("POST", url, json=payload, headers=headers) as resp:
                    resp.raise_for_status()
                    for line in resp.iter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
        except Exception as exc:
            logger.warning("GenericLLMService stream failed, fallback: %s", exc)
            yield self._mock.chat(system_prompt, user_prompt)


class XfyunLLMService(LLMService):
    """科大讯飞星火大模型 API 服务骨架。

    TODO: 接入真实 API 时，在此处实现以下逻辑：
    1. 构建请求参数（app_id, api_key, messages）
    2. 调用科大讯飞 WebSocket 或 HTTP 接口
    3. 接收流式或非流式响应
    4. 返回模型生成的文本

    参考文档：
    - 星火认知大模型 API 文档
    - https://www.xfyun.cn/doc/spark/Web.html
    """

    def __init__(self, api_key: str = "", app_id: str = "", api_secret: str = ""):
        self.api_key = api_key
        self.app_id = app_id
        self.api_secret = api_secret

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        # TODO: 替换为真实科大讯飞 API 调用
        # 临时使用 Mock 作为 fallback
        mock = MockLLMService()
        return mock.chat(system_prompt, user_prompt)
