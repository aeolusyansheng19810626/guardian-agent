"""Common Agent helpers: schema, prompt template, fallback wrapper."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Literal

from pydantic import BaseModel, Field

RULES_DIR = Path(__file__).resolve().parent.parent / "rules"


class Issue(BaseModel):
    severity: Literal["high", "med", "low"] = Field(description="严重程度")
    text: str = Field(description="具体问题描述")


class AgentOutput(BaseModel):
    score: int = Field(ge=0, le=100, description="本维度 0-100 分")
    issues: list[Issue] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class QualityAgentOutput(AgentOutput):
    """质量 Agent 的扩展：障害模式可能填充 5-Why。"""
    five_why: list[str] = Field(
        default_factory=list,
        description="若根本原因表面化，给出 5 步 Why 链；否则留空数组",
    )


def load_rules(name: str) -> str:
    path = RULES_DIR / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def build_user_prompt(doc_type: str, raw_input: str, dimension_focus: str) -> str:
    rule_file = "incident_rules.md" if doc_type == "incident" else "delivery_rules.md"
    rules = load_rules(rule_file)
    type_label = "障害报告" if doc_type == "incident" else "交付物文档"
    return (
        f"你正在审查一份【{type_label}】，本次仅关注【{dimension_focus}】维度。\n"
        f"请严格遵循下列规则进行评估：\n\n{rules}\n\n"
        f"---\n待审查文档：\n{raw_input}\n---\n\n"
        "输出 JSON：score(0-100)、issues(severity+text)、suggestions（具体可执行）。"
        "评分基准：≥80 良好，60-79 有可观察问题，<60 严重问题。"
    )


def make_fallback_appender(state_events: list[str], dim: str) -> Callable[[str, str, Exception], None]:
    def _on(failed: str, nxt: str, err: Exception) -> None:
        state_events.append(f"[{dim}] {failed} → {nxt}: {type(err).__name__}")
    return _on
