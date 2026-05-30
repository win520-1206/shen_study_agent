# LearnMate-AI 配置文件示例
# 复制此文件为 config.py 并填入真实配置
# 注意：config.py 不要上传到 GitHub！

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
KB_DIR = DATA_DIR / "course_kb"
DB_DIR = BASE_DIR / "runtime"
DB_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{(DB_DIR / 'learnmate.db').as_posix()}"


# ── LLM 接入配置 ──────────────────────────────────────
# 设为 True 启用大模型智能体，设为 False 使用规则式智能体
USE_LLM = False

# LLM 服务提供者: "mock" / "generic" / "xfyun"
LLM_PROVIDER = "mock"

# 科大讯飞 API 配置（真实接入时填写）
XFYUN_APP_ID = ""
XFYUN_API_KEY = ""
XFYUN_API_SECRET = ""

# 通用 LLM API 配置（OpenAI 兼容格式）
# 支持 DeepSeek、通义千问、讯飞星火 OpenAI 模式等任何兼容 API
LLM_BASE_URL = ""   # 例如 "https://api.deepseek.com"
LLM_API_KEY_V2 = "" # 你的 API 密钥（避免与讯飞的 XFYUN_API_KEY 冲突）
LLM_MODEL = ""      # 模型名称，例如 "deepseek-chat"


def get_llm_service():
    """根据配置返回对应的 LLM 服务实例。"""
    from .services.llm_service import GenericLLMService, MockLLMService, XfyunLLMService

    if LLM_PROVIDER == "generic" and LLM_BASE_URL and LLM_API_KEY_V2:
        return GenericLLMService(
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY_V2,
            model=LLM_MODEL,
        )

    if LLM_PROVIDER == "xfyun" and XFYUN_API_KEY:
        return XfyunLLMService(
            api_key=XFYUN_API_KEY,
            app_id=XFYUN_APP_ID,
            api_secret=XFYUN_API_SECRET,
        )
    return MockLLMService()
