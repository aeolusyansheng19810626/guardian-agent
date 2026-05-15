"""LangGraph builder: classify → parallel agents → guardian → reporter."""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents import compliance, completeness, logic, prevention, quality
from graph import guardian_node
from graph.state import AgentState
from reporter import generator as reporter_gen
from utils.classifier import classify


def _classify_node(state: AgentState) -> dict:
    return {"doc_type": classify(state["raw_input"])}


def _route_after_classify(state: AgentState) -> list[str]:
    base = ["completeness", "quality", "compliance", "logic"]
    if state["doc_type"] == "incident":
        base.append("prevention")
    return base


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("classify", _classify_node)
    g.add_node("completeness", completeness.run)
    g.add_node("quality", quality.run)
    g.add_node("compliance", compliance.run)
    g.add_node("logic", logic.run)
    g.add_node("prevention", prevention.run)
    g.add_node("guardian", guardian_node.run)
    g.add_node("reporter", reporter_gen.run)

    g.add_edge(START, "classify")
    g.add_conditional_edges(
        "classify",
        _route_after_classify,
        {
            "completeness": "completeness",
            "quality": "quality",
            "compliance": "compliance",
            "logic": "logic",
            "prevention": "prevention",
        },
    )

    # 并行节点全部汇入 guardian
    for n in ["completeness", "quality", "compliance", "logic", "prevention"]:
        g.add_edge(n, "guardian")

    g.add_edge("guardian", "reporter")
    g.add_edge("reporter", END)

    return g.compile()
