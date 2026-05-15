"""Document type classifier: keyword first, LLM fallback."""
from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

from utils.llm_factory import default_chain_flash_first, invoke_with_fallback

DocType = Literal["delivery", "incident"]

_INCIDENT_KEYWORDS = [
    "障害", "障碍", "事故", "故障",
    "発生時刻", "発生时刻", "发生时刻",
    "復旧", "复旧", "恢复时刻",
    "根本原因", "根因",
    "再発防止", "再发防止", "防止策",
    "暫定対応", "暂定对应", "临时对应", "临时対応",
    "恒久対応", "恒久对应",
    "影響範囲", "影响范围",
    "incident", "postmortem", "post-mortem", "rca",
]

_DELIVERY_KEYWORDS = [
    "需求文档", "需求规格", "システム要件",
    "功能需求", "非功能需求", "非機能要件",
    "系统架构", "アーキテクチャ",
    "接口定义", "数据模型",
    "验收标准", "受入基準",
    "设计文档", "設計書",
    "ユースケース", "用户场景",
]


class _ClassifyOut(BaseModel):
    doc_type: Literal["delivery", "incident"] = Field(
        description="delivery=交付物（需求/设计/规格类文档），incident=障害报告"
    )
    confidence: float = Field(ge=0, le=1)
    reason: str


def _keyword_score(text: str, keywords: list[str]) -> int:
    lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in lower)


def classify(text: str) -> DocType:
    inc = _keyword_score(text, _INCIDENT_KEYWORDS)
    dlv = _keyword_score(text, _DELIVERY_KEYWORDS)
    if inc >= 2 and inc > dlv:
        return "incident"
    if dlv >= 2 and dlv > inc:
        return "delivery"
    if inc == 0 and dlv == 0:
        # 无明显关键词，再做一次启发式：日期+原因+対応 → incident
        if re.search(r"\d{4}[-/年]\d{1,2}[-/月]\d{1,2}", text) and (
            "原因" in text or "対応" in text or "对应" in text
        ):
            return "incident"

    # LLM 兜底
    prompt = (
        "判断以下文档属于哪一类：\n"
        "- delivery: 项目交付物（需求文档、设计文档、规格说明、接口定义等）\n"
        "- incident: 障害/事故报告（包含发生时刻、原因分析、再発防止策等）\n\n"
        f"文档内容：\n{text[:4000]}\n\n严格输出 JSON。"
    )
    try:
        result: _ClassifyOut = invoke_with_fallback(
            default_chain_flash_first(),
            prompt,
            structured_schema=_ClassifyOut,
        )
        return result.doc_type
    except Exception:  # noqa: BLE001
        # 终极 fallback：交付物（更安全的默认）
        return "delivery"
