"""Logic consistency Agent: Gemini Flash."""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from agents.base import AgentOutput, build_user_prompt, make_fallback_appender
from utils.llm_factory import default_chain_flash_first, invoke_with_fallback

DIMENSION = "logic"
SYSTEM = (
    "你是逻辑一致性审查专家。检查文档内部是否存在前后矛盾、术语前后是否统一、"
    "需求/设计/验证是否可追溯、章节之间逻辑是否衔接、时序与因果链是否合理。"
    "对障害报告：检查时刻先后顺序、原因与现象的因果是否对得上、"
    "防止策是否真的针对根本原因（而非症状）。"
)


def run(state: dict) -> dict:
    events: list[str] = []
    user_prompt = build_user_prompt(state["doc_type"], state["raw_input"], "逻辑一致性")
    messages = [SystemMessage(content=SYSTEM), HumanMessage(content=user_prompt)]

    on_fb = make_fallback_appender(events, DIMENSION)
    out: AgentOutput = invoke_with_fallback(
        default_chain_flash_first(),
        messages,
        structured_schema=AgentOutput,
        on_fallback=on_fb,
    )
    return {
        "logic_result": {
            "score": out.score,
            "issues": [i.model_dump() for i in out.issues],
            "suggestions": out.suggestions,
        },
        "fallback_events": events,
    }
