"""Guardian Agent - Streamlit entrypoint."""
from __future__ import annotations

import time
import traceback

import streamlit as st

from config import (
    DIMENSION_LABELS,
    active_dimensions,
)
from graph.builder import build_graph
from utils.visualizer import radar_chart, trend_chart

st.set_page_config(
    page_title="Guardian Agent | 质量审查平台",
    page_icon="🛡️",
    layout="wide",
)

# ---- Session state ----
if "history" not in st.session_state:
    st.session_state.history = []  # [{idx, score, verdict, doc_type}]
if "fallback_log" not in st.session_state:
    st.session_state.fallback_log = []
if "graph" not in st.session_state:
    try:
        st.session_state.graph = build_graph()
    except Exception as err:  # noqa: BLE001
        st.session_state.graph = None
        st.session_state.graph_err = str(err)


VERDICT_BADGE = {
    "pass": ("通过", "✅", "#16a34a"),
    "conditional": ("有条件通过", "⚠️", "#d97706"),
    "block": ("拦截", "⛔", "#dc2626"),
}

# ---- Sidebar ----
with st.sidebar:
    st.markdown("## 🛡️ Guardian Agent")
    st.caption("IBM 项目团队内部质量审查（演示）")
    st.divider()
    st.metric("本会话提交次数", len(st.session_state.history))
    if st.session_state.history:
        avg = sum(h["score"] for h in st.session_state.history) / len(st.session_state.history)
        st.metric("平均分", f"{avg:.1f}")
        st.markdown("**分数趋势**")
        st.plotly_chart(trend_chart(st.session_state.history), use_container_width=True)
    st.divider()
    if st.session_state.fallback_log:
        with st.expander(f"降级事件（{len(st.session_state.fallback_log)}）"):
            for ev in st.session_state.fallback_log[-20:]:
                st.text(ev)
    if st.button("清空历史", use_container_width=True):
        st.session_state.history = []
        st.session_state.fallback_log = []
        st.rerun()

st.title("🛡️ Guardian Agent")
st.caption("交付物 / 障害报告 多 Agent 质量审查 — LangGraph + Gemini + Groq")


def _render_progress_panel(container, doc_type: str, status_map: dict):
    """渲染并行 Agent 进度。"""
    container.empty()
    with container.container():
        for dim in active_dimensions(doc_type):
            label = DIMENSION_LABELS.get(dim, dim)
            status = status_map.get(dim, "pending")
            if status == "pending":
                st.progress(0, text=f"⏳ {label}：等待中")
            elif status == "running":
                st.progress(50, text=f"🔄 {label}：分析中…")
            elif isinstance(status, dict):
                score = status.get("score", 0)
                st.progress(int(score), text=f"✓ {label}：{score} 分")


def _render_result(state: dict, doc_type: str):
    verdict_key = state.get("guardian_verdict", "block")
    label, icon, color = VERDICT_BADGE.get(verdict_key, ("未知", "❔", "#666"))
    total = state.get("total_score", 0)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(
            f"""
            <div style="padding:18px;border-radius:12px;background:{color};color:white;text-align:center;">
                <div style="font-size:28px;">{icon} {label}</div>
                <div style="font-size:42px;font-weight:bold;margin-top:6px;">{total} <span style="font-size:18px;font-weight:normal;">/ 100</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        breakdown = state.get("weighted_breakdown", {})
        if breakdown:
            st.plotly_chart(radar_chart(breakdown), use_container_width=True)

    issues = state.get("consolidated_issues", [])
    if issues:
        st.markdown("### 📋 问题清单")
        sev_color = {"high": "🔴", "med": "🟡", "low": "🟢"}
        for i in issues:
            sev = i.get("severity", "low")
            st.markdown(
                f"{sev_color.get(sev, '⚪')} **[{i.get('dimension','')}]** {i.get('text','')}"
            )

    suggestions = state.get("overall_suggestions", [])
    if suggestions:
        st.markdown("### 💡 改进建议")
        for s in suggestions:
            st.markdown(f"- {s}")

    # 5-Why（仅障害且 quality_result 中有 five_why）
    five_why = (state.get("quality_result") or {}).get("five_why")
    if doc_type == "incident" and five_why:
        with st.expander("🔍 5-Why 辅助分析（仅供参考、非硬性扣分）", expanded=True):
            for idx, w in enumerate(five_why, 1):
                st.markdown(f"**Why {idx}.** {w}")

    report = state.get("final_report", "")
    if report:
        with st.expander("📄 完整报告（Markdown）", expanded=False):
            st.markdown(report)


def _run_review(raw_input: str, forced_doc_type: str, progress_slot, result_slot):
    if st.session_state.graph is None:
        result_slot.error(f"图构建失败：{st.session_state.get('graph_err','unknown')}")
        return

    status_map = {dim: "pending" for dim in active_dimensions(forced_doc_type)}
    _render_progress_panel(progress_slot, forced_doc_type, status_map)

    initial_state = {
        "raw_input": raw_input,
        "doc_type": forced_doc_type,
        "fallback_events": [],
    }

    final_state: dict = {}
    try:
        for chunk in st.session_state.graph.stream(initial_state, stream_mode="updates"):
            for node_name, partial in chunk.items():
                # 进度更新
                dim_map = {
                    "completeness": "completeness",
                    "quality": "quality",
                    "compliance": "compliance",
                    "logic": "logic",
                    "prevention": "prevention",
                }
                if node_name in dim_map:
                    dim = dim_map[node_name]
                    res_key = f"{dim}_result"
                    if partial.get(res_key):
                        status_map[dim] = partial[res_key]
                    _render_progress_panel(progress_slot, forced_doc_type, status_map)
                # 累积 state
                for k, v in partial.items():
                    if k == "fallback_events" and v:
                        for ev in v:
                            st.session_state.fallback_log.append(ev)
                            st.toast(f"降级：{ev}", icon="⚠️")
                        final_state.setdefault("fallback_events", []).extend(v)
                    else:
                        final_state[k] = v
    except Exception as err:  # noqa: BLE001
        result_slot.error(f"审查失败：{err}")
        result_slot.code(traceback.format_exc())
        return

    # 最终渲染
    with result_slot.container():
        _render_result(final_state, forced_doc_type)

    # 历史记录
    st.session_state.history.append({
        "idx": len(st.session_state.history) + 1,
        "score": final_state.get("total_score", 0),
        "verdict": final_state.get("guardian_verdict", "block"),
        "doc_type": forced_doc_type,
        "ts": time.time(),
    })


def _tab_layout(doc_type: str, sample: str):
    left, right = st.columns([2, 3], gap="large")
    with left:
        text = st.text_area(
            "粘贴文档内容",
            height=520,
            placeholder=sample,
            key=f"input_{doc_type}",
        )
        col_a, col_b = st.columns(2)
        run_btn = col_a.button(
            "🚀 开始审查",
            key=f"run_{doc_type}",
            type="primary",
            use_container_width=True,
        )
        clear_btn = col_b.button("清空", key=f"clear_{doc_type}", use_container_width=True)
        if clear_btn:
            st.session_state[f"input_{doc_type}"] = ""
            st.rerun()
    with right:
        st.markdown("#### 实时检查进度")
        progress_slot = st.empty()
        # 初始化空进度
        _render_progress_panel(
            progress_slot,
            doc_type,
            {dim: "pending" for dim in active_dimensions(doc_type)},
        )
        st.markdown("---")
        st.markdown("#### 审查结果")
        result_slot = st.empty()
        result_slot.info("提交文档后此处展示裁决与建议。")

    if run_btn:
        if not text or not text.strip():
            st.warning("请先粘贴文档内容")
            return
        with st.spinner("正在执行多 Agent 审查…"):
            _run_review(text, doc_type, progress_slot, result_slot)


SAMPLE_DELIVERY = (
    "示例：\n系统需求文档，包含功能需求、非功能需求（系统响应要快）、"
    "系统架构图，缺少风险章节。"
)
SAMPLE_INCIDENT = (
    "示例：\n2024年3月15日14:00系统发生障害。原因：服务器异常。"
    "対応：重启服务器。防止策：加强监控。"
)

tab_d, tab_i = st.tabs(["📦 交付物审查", "🚨 障害报告审查"])
with tab_d:
    _tab_layout("delivery", SAMPLE_DELIVERY)
with tab_i:
    _tab_layout("incident", SAMPLE_INCIDENT)
