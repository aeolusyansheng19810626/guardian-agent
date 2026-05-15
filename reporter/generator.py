"""Final report generator: Markdown via Gemini Pro."""
from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from agents.base import make_fallback_appender
from config import DIMENSION_LABELS
from utils.llm_factory import default_chain_pro_first, invoke_with_fallback

DIMENSION = "reporter"

VERDICT_LABEL = {
    "pass": "✅ 通过",
    "conditional": "⚠️ 有条件通过",
    "block": "⛔ 拦截",
}

SYSTEM = (
    "你是资深质量评审报告撰写者。基于提供的审查结果，生成结构清晰、措辞专业的"
    "Markdown 报告，面向 IBM 项目团队 Reader。报告需包含："
    "（1）裁决摘要（一句话总评）"
    "（2）各维度逐项分析（标题 + 得分 + 关键发现）"
    "（3）问题清单（按严重度）"
    "（4）改进建议（按优先级）"
    "（5）若有 5-Why 辅助分析则附在末尾，并明确标注'仅供参考、非硬性扣分'。"
    "语言：与原文档语言一致（中文为主）。不要重复输出 JSON。"
)


def _build_payload(state: dict) -> dict:
    results = {}
    five_why = None
    for dim_key, key in [
        ("completeness", "completeness_result"),
        ("quality", "quality_result"),
        ("compliance", "compliance_result"),
        ("logic", "logic_result"),
        ("prevention", "prevention_result"),
    ]:
        r = state.get(key)
        if r:
            label = DIMENSION_LABELS.get(dim_key, dim_key)
            results[label] = {
                "score": r.get("score"),
                "issues": r.get("issues", []),
                "suggestions": r.get("suggestions", []),
            }
            if dim_key == "quality" and r.get("five_why"):
                five_why = r["five_why"]
    return {
        "doc_type": "障害报告" if state["doc_type"] == "incident" else "交付物",
        "verdict": VERDICT_LABEL.get(state["guardian_verdict"], state["guardian_verdict"]),
        "total_score": state["total_score"],
        "breakdown": {
            DIMENSION_LABELS.get(k, k): v
            for k, v in state.get("weighted_breakdown", {}).items()
        },
        "results": results,
        "consolidated_issues": state.get("consolidated_issues", []),
        "overall_suggestions": state.get("overall_suggestions", []),
        "five_why": five_why,
    }


def run(state: dict) -> dict:
    events: list[str] = []
    payload = _build_payload(state)
    user = (
        "请基于以下 JSON 生成 Markdown 审查报告：\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )
    on_fb = make_fallback_appender(events, DIMENSION)
    try:
        msg = invoke_with_fallback(
            default_chain_pro_first(),
            [SystemMessage(content=SYSTEM), HumanMessage(content=user)],
            on_fallback=on_fb,
        )
        report = msg.content if hasattr(msg, "content") else str(msg)
    except Exception as err:  # noqa: BLE001
        events.append(f"[reporter] all LLMs failed: {type(err).__name__}")
        report = _fallback_markdown(payload)

    return {"final_report": report, "fallback_events": events}


def _fallback_markdown(p: dict) -> str:
    lines = [
        f"# 审查报告（{p['doc_type']}）",
        "",
        f"**裁决**：{p['verdict']}　**总分**：{p['total_score']} / 100",
        "",
        "## 维度得分",
    ]
    for k, v in p["breakdown"].items():
        lines.append(f"- {k}: {v}")
    lines.append("\n## 问题清单")
    for i in p["consolidated_issues"]:
        lines.append(f"- **[{i['severity']}] [{i['dimension']}]** {i['text']}")
    lines.append("\n## 改进建议")
    for s in p["overall_suggestions"]:
        lines.append(f"- {s}")
    if p.get("five_why"):
        lines.append("\n## 5-Why 辅助分析（仅供参考）")
        for idx, w in enumerate(p["five_why"], 1):
            lines.append(f"{idx}. {w}")
    return "\n".join(lines)
