"""LangGraph AgentState definition."""
from __future__ import annotations

import operator
from typing import Annotated, Any, Literal, TypedDict

DocType = Literal["delivery", "incident"]
Verdict = Literal["pass", "conditional", "block"]


class AgentResult(TypedDict, total=False):
    score: int
    issues: list[dict]
    suggestions: list[str]
    five_why: list[str]
    model_used: str


class AgentState(TypedDict, total=False):
    raw_input: str
    doc_type: DocType

    completeness_result: AgentResult
    quality_result: AgentResult
    compliance_result: AgentResult
    logic_result: AgentResult
    prevention_result: AgentResult

    guardian_verdict: Verdict
    total_score: int
    weighted_breakdown: dict[str, int]
    consolidated_issues: list[dict]
    overall_suggestions: list[str]

    final_report: str

    # 用 add reducer 让多个并行节点都能 append
    fallback_events: Annotated[list[str], operator.add]
