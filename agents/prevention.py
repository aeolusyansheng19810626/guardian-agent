"""Prevention (再発防止) Agent: incident only. Gemini Flash."""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from agents.base import AgentOutput, build_user_prompt, make_fallback_appender
from utils.llm_factory import default_chain_flash_first, invoke_with_fallback

DIMENSION = "prevention"
SYSTEM = (
    "你是再発防止策审查专家。每条防止策必须同时具备：(1) 具体可执行的措施 "
    "(2) 明确的担当者/团队 (3) 明确的完成期限。"
    "缺任何一个要素视为 high 严重度。"
    "抽象口号（'加强监控''提升意识''完善流程'）若无三要素同样不合格。"
    "另检查临时対応与恒久対応是否清晰区分、是否做了横展开调查。"
)


def run(state: dict) -> dict:
    events: list[str] = []
    user_prompt = build_user_prompt(state["doc_type"], state["raw_input"], "再発防止")
    messages = [SystemMessage(content=SYSTEM), HumanMessage(content=user_prompt)]

    on_fb = make_fallback_appender(events, DIMENSION)
    out: AgentOutput = invoke_with_fallback(
        default_chain_flash_first(),
        messages,
        structured_schema=AgentOutput,
        on_fallback=on_fb,
    )
    return {
        "prevention_result": {
            "score": out.score,
            "issues": [i.model_dump() for i in out.issues],
            "suggestions": out.suggestions,
        },
        "fallback_events": events,
    }
