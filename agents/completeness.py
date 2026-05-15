"""Completeness Agent: Groq llama-3.3-70b first."""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from agents.base import AgentOutput, build_user_prompt, make_fallback_appender
from utils.llm_factory import default_chain_groq_first, invoke_with_fallback

DIMENSION = "completeness"
SYSTEM = (
    "你是文档完整性检查专家。重点检查必填章节是否齐备、关键要素是否缺失。"
    "对障害报告关注：发生时刻/恢复时刻/影响范围/影响用户数/根本原因/防止策。"
    "对交付物关注：功能需求/非功能需求/架构/接口/数据模型/风险章节/验收标准。"
)


def run(state: dict) -> dict:
    events: list[str] = []
    user_prompt = build_user_prompt(state["doc_type"], state["raw_input"], "完整性")
    messages = [SystemMessage(content=SYSTEM), HumanMessage(content=user_prompt)]

    on_fb = make_fallback_appender(events, DIMENSION)
    out: AgentOutput = invoke_with_fallback(
        default_chain_groq_first(),
        messages,
        structured_schema=AgentOutput,
        on_fallback=on_fb,
    )
    return {
        "completeness_result": {
            "score": out.score,
            "issues": [i.model_dump() for i in out.issues],
            "suggestions": out.suggestions,
        },
        "fallback_events": events,
    }
