"""Compliance / format Agent: Gemini Flash."""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from agents.base import AgentOutput, build_user_prompt, make_fallback_appender
from utils.llm_factory import default_chain_flash_first, invoke_with_fallback

DIMENSION = "compliance"
SYSTEM = (
    "你是文档格式合规审查专家。检查标题层级是否清晰不跳级、表格使用合理、"
    "图示有图号说明、术语首次出现有定义、缩写有对照、章节编号一致、列表格式统一。"
    "障害报告检查时序日志是否按时间顺序、时刻格式统一。"
)


def run(state: dict) -> dict:
    events: list[str] = []
    user_prompt = build_user_prompt(state["doc_type"], state["raw_input"], "格式合规")
    messages = [SystemMessage(content=SYSTEM), HumanMessage(content=user_prompt)]

    on_fb = make_fallback_appender(events, DIMENSION)
    out: AgentOutput = invoke_with_fallback(
        default_chain_flash_first(),
        messages,
        structured_schema=AgentOutput,
        on_fallback=on_fb,
    )
    return {
        "compliance_result": {
            "score": out.score,
            "issues": [i.model_dump() for i in out.issues],
            "suggestions": out.suggestions,
        },
        "fallback_events": events,
    }
