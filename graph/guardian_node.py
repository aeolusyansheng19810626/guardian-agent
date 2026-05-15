"""Guardian verdict node: aggregates sub-agent results via Gemini Pro."""
from __future__ import annotations

import json
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from agents.base import make_fallback_appender
from config import (
    CONDITIONAL_THRESHOLD,
    DIMENSION_LABELS,
    PASS_THRESHOLD,
    active_dimensions,
    get_weights,
)
from utils.llm_factory import default_chain_pro_first, invoke_with_fallback

DIMENSION = "guardian"


class ConsolidatedIssue(BaseModel):
    severity: Literal["high", "med", "low"]
    dimension: str
    text: str


class GuardianOutput(BaseModel):
    consolidated_issues: list[ConsolidatedIssue] = Field(default_factory=list)
    overall_suggestions: list[str] = Field(default_factory=list)
    rationale: str = Field(description="一段话解释裁决依据")


SYSTEM = (
    "你是质量审查 Guardian。输入是各维度子 Agent 的 JSON 结果。"
    "你的任务：(1) 合并去重所有 issues，按严重度排序；"
    "(2) 输出整体改进建议（不超过 6 条，按优先级）；"
    "(3) 用一段话解释整体判断依据，重点指出最关键的 1-2 个问题。"
    "注意：评分与最终裁决由系统按权重自动计算，你不需要重复给分。"
)


def _collect_results(state: dict) -> dict[str, dict]:
    mapping = {
        "completeness": "completeness_result",
        "quality": "quality_result",
        "compliance": "compliance_result",
        "logic": "logic_result",
        "prevention": "prevention_result",
    }
    out = {}
    for dim, key in mapping.items():
        if state.get(key):
            out[dim] = state[key]
    return out


def _weighted_total(results: dict[str, dict], doc_type: str) -> tuple[int, dict[str, int]]:
    weights = get_weights(doc_type)
    breakdown: dict[str, int] = {}
    total = 0.0
    weight_sum = 0.0
    for dim in active_dimensions(doc_type):
        if dim in results:
            score = int(results[dim].get("score", 0))
            breakdown[dim] = score
            w = weights[dim]
            total += score * w
            weight_sum += w
    if weight_sum > 0:
        total = total / weight_sum
    return int(round(total)), breakdown


def _verdict_from_score(score: int, results: dict[str, dict], doc_type: str) -> str:
    # 硬性拦截：任一关键维度有 high 严重度问题 + 该维度 < 60，强制至少 conditional
    has_high = any(
        any(i.get("severity") == "high" for i in r.get("issues", []))
        for r in results.values()
    )
    if score >= PASS_THRESHOLD and not has_high:
        return "pass"
    if score >= CONDITIONAL_THRESHOLD:
        return "conditional"
    return "block"


def run(state: dict) -> dict:
    events: list[str] = []
    results = _collect_results(state)
    total, breakdown = _weighted_total(results, state["doc_type"])
    verdict = _verdict_from_score(total, results, state["doc_type"])

    # LLM 合并 issues / 给整体建议
    summary_for_llm = {
        DIMENSION_LABELS.get(dim, dim): {
            "score": r.get("score"),
            "issues": r.get("issues", []),
            "suggestions": r.get("suggestions", []),
        }
        for dim, r in results.items()
    }
    user = (
        f"文档类型：{'障害报告' if state['doc_type']=='incident' else '交付物'}\n"
        f"加权总分：{total}\n"
        f"各维度得分：{breakdown}\n"
        f"系统裁决：{verdict}（pass≥80, conditional 60-79, block<60，"
        f"或任一维度有 high 问题不可直接 pass）\n\n"
        f"各子 Agent 详细输出：\n{json.dumps(summary_for_llm, ensure_ascii=False, indent=2)}\n\n"
        "请合并 issues、给出整体建议、写一段裁决依据说明。"
    )

    on_fb = make_fallback_appender(events, DIMENSION)
    try:
        out: GuardianOutput = invoke_with_fallback(
            default_chain_pro_first(),
            [SystemMessage(content=SYSTEM), HumanMessage(content=user)],
            structured_schema=GuardianOutput,
            on_fallback=on_fb,
        )
        consolidated = [i.model_dump() for i in out.consolidated_issues]
        suggestions = out.overall_suggestions
    except Exception as err:  # noqa: BLE001
        events.append(f"[guardian] all LLMs failed: {type(err).__name__}")
        # 退化：直接合并 issues
        consolidated = []
        for dim, r in results.items():
            for i in r.get("issues", []):
                consolidated.append({
                    "severity": i.get("severity", "med"),
                    "dimension": DIMENSION_LABELS.get(dim, dim),
                    "text": i.get("text", ""),
                })
        suggestions = []
        for r in results.values():
            suggestions.extend(r.get("suggestions", []))
        suggestions = suggestions[:6]

    sev_order = {"high": 0, "med": 1, "low": 2}
    consolidated.sort(key=lambda x: sev_order.get(x.get("severity", "low"), 9))

    return {
        "guardian_verdict": verdict,
        "total_score": total,
        "weighted_breakdown": breakdown,
        "consolidated_issues": consolidated,
        "overall_suggestions": suggestions,
        "fallback_events": events,
    }
