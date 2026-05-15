"""Quality Agent: Gemini Flash. Triggers 5-Why for shallow root cause in incidents."""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from agents.base import QualityAgentOutput, build_user_prompt, make_fallback_appender
from utils.llm_factory import default_chain_flash_first, invoke_with_fallback

DIMENSION = "quality"

SYSTEM_DELIVERY = (
    "你是交付物质量审查专家。重点检查需求描述的可测试性："
    "性能/可用性/兼容性等是否量化、功能需求是否可验证、表述是否清晰无歧义。"
    "对'响应要快''稳定可靠'等模糊表述给出 high 严重度问题。"
)

SYSTEM_INCIDENT = (
    "你是障害报告质量审查专家。重点检查根本原因分析的深度："
    "区分直接原因与根本原因，识别表面化描述（如'服务器异常''操作失误''性能不足'）。"
    "如果根本原因明显表面化，请在 five_why 字段填写 5 步 Why 链作为辅助分析（每步是一个推问）。"
    "若原因分析已经足够深入，five_why 留空数组。"
    "five_why 是辅助内容，不构成硬性扣分项。"
)


def run(state: dict) -> dict:
    events: list[str] = []
    doc_type = state["doc_type"]
    system = SYSTEM_INCIDENT if doc_type == "incident" else SYSTEM_DELIVERY
    user_prompt = build_user_prompt(doc_type, state["raw_input"], "质量")
    messages = [SystemMessage(content=system), HumanMessage(content=user_prompt)]

    on_fb = make_fallback_appender(events, DIMENSION)
    out: QualityAgentOutput = invoke_with_fallback(
        default_chain_flash_first(),
        messages,
        structured_schema=QualityAgentOutput,
        on_fallback=on_fb,
    )
    result = {
        "score": out.score,
        "issues": [i.model_dump() for i in out.issues],
        "suggestions": out.suggestions,
    }
    if out.five_why:
        result["five_why"] = out.five_why
    return {"quality_result": result, "fallback_events": events}
