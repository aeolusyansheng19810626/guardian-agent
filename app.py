"""Guardian Agent — Streamlit entrypoint with custom React UI component."""
from __future__ import annotations

import time
import traceback
from datetime import datetime
from typing import Any

import streamlit as st

from components.guardian_ui import guardian_ui
from config import (
    DIMENSION_LABELS,
    GEMINI_PRO,
    active_dimensions,
    get_weights,
)
from graph.builder import build_graph

st.set_page_config(
    page_title="Guardian Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Strip Streamlit chrome so the React component fills the viewport.
st.markdown(
    """
    <style>
      header[data-testid="stHeader"], footer, [data-testid="stToolbar"],
      [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        display: none !important;
      }
      section[data-testid="stSidebar"] { display: none !important; }
      .main > .block-container,
      [data-testid="stAppViewBlockContainer"] {
        padding: 0 !important;
        max-width: 100% !important;
      }
      .stApp { background: #f8fafc; }
      iframe[title^="components.guardian_ui"] {
        width: 100% !important;
        min-height: 100vh !important;
        border: 0 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


SAMPLE_DELIVERY = (
    "示例：\n系统需求文档，包含功能需求、非功能需求（系统响应要快）、"
    "系统架构图，缺少风险章节。"
)
SAMPLE_INCIDENT = (
    "2024年3月15日 14:00 系统发生障害。\n\n"
    "原因：服务器异常。\n対応：重启服务器。\n防止策：加强监控。"
)


# ---- Session state init ----
def _init_state() -> None:
    defaults: dict[str, Any] = {
        "lang": "zh",
        "theme": "light",
        "palette_color": "#059669",
        "density": "cozy",
        "tab": "incident",
        "ui_state": "idle",  # idle | running | done
        "input_text": "",
        "runtime": {},
        "result": None,
        "history": [],
        "fallback_events": [],
        "selected_history_idx": None,
        "last_event_ts": None,
        "pending_run": None,  # {"text": ..., "tab": ...} when graph should execute
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if "graph" not in st.session_state:
        try:
            st.session_state.graph = build_graph()
            st.session_state.graph_err = None
        except Exception as err:  # noqa: BLE001
            st.session_state.graph = None
            st.session_state.graph_err = str(err)


_init_state()


# ---- Helpers ----
def _empty_runtime(doc_type: str) -> dict:
    rt: dict[str, dict] = {
        "classify": {"status": "pending"},
        "guardian": {"status": "pending"},
        "reporter": {"status": "pending"},
    }
    for d in active_dimensions(doc_type):
        rt[d] = {"status": "pending"}
    return rt


def _build_result(
    final_state: dict,
    doc_type: str,
    submitted_at: str,
    latency_ms: int,
    fallback_events: list[str],
) -> dict:
    weights = get_weights(doc_type)
    raw_breakdown = final_state.get("weighted_breakdown", {}) or {}
    breakdown: dict[str, dict] = {}
    for dim in active_dimensions(doc_type):
        breakdown[dim] = {
            "score": int(raw_breakdown.get(dim, 0)),
            "weight": float(weights.get(dim, 0)),
        }

    issues = []
    for it in final_state.get("consolidated_issues", []) or []:
        dim_label = it.get("dimension", "")
        # Map back from label to key
        dim_key = dim_label
        for k, lbl in DIMENSION_LABELS.items():
            if lbl == dim_label:
                dim_key = k
                break
        issues.append({
            "severity": it.get("severity", "low"),
            "dimension": dim_key,
            "text": it.get("text", ""),
        })

    five_why = (final_state.get("quality_result") or {}).get("five_why")

    return {
        "docType": doc_type,
        "verdict": final_state.get("guardian_verdict", "block"),
        "totalScore": int(final_state.get("total_score", 0)),
        "breakdown": breakdown,
        "issues": issues,
        "suggestions": list(final_state.get("overall_suggestions", []) or []),
        "fiveWhy": list(five_why) if five_why else None,
        "finalReport": final_state.get("final_report", ""),
        "fallback": ", ".join(fallback_events) if fallback_events else None,
        "submittedAt": submitted_at,
        "latencyMs": latency_ms,
        "tokens": 0,
        "primaryModel": "Gemini 2.5 Pro" if "pro" in GEMINI_PRO.lower() else GEMINI_PRO,
    }


def _history_title(text: str, doc_type: str) -> str:
    snippet = text.strip().split("\n")[0][:24]
    if not snippet:
        snippet = "障害报告" if doc_type == "incident" else "交付物"
    return snippet


def _record_history(text: str, doc_type: str, result: dict) -> None:
    next_idx = max((h["idx"] for h in st.session_state.history), default=0) + 1
    st.session_state.history.insert(0, {
        "idx": next_idx,
        "score": result["totalScore"],
        "verdict": result["verdict"],
        "docType": doc_type,
        "ts": datetime.now().strftime("%H:%M"),
        "title": _history_title(text, doc_type),
    })
    st.session_state.selected_history_idx = next_idx


def _run_review(text: str, doc_type: str) -> None:
    if st.session_state.graph is None:
        st.error(f"图构建失败：{st.session_state.graph_err}")
        st.session_state.ui_state = "idle"
        return

    submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    started = time.perf_counter()

    runtime = _empty_runtime(doc_type)
    runtime["classify"] = {"status": "running", "pct": 30}
    st.session_state.runtime = runtime

    initial_state = {
        "raw_input": text,
        "doc_type": doc_type,
        "fallback_events": [],
    }

    final_state: dict = {}
    fallback_events: list[str] = []
    detected_doc_type = doc_type

    try:
        for chunk in st.session_state.graph.stream(
            initial_state, stream_mode="updates"
        ):
            for node_name, partial in chunk.items():
                partial = partial or {}
                if node_name == "classify":
                    runtime["classify"] = {"status": "done", "pct": 100}
                    detected_doc_type = partial.get("doc_type") or doc_type
                    for d in active_dimensions(detected_doc_type):
                        runtime[d] = {"status": "running", "pct": 30}
                elif node_name in ("completeness", "quality", "compliance",
                                   "logic", "prevention"):
                    runtime[node_name] = {"status": "done", "pct": 100}
                elif node_name == "guardian":
                    runtime["guardian"] = {
                        "status": "done",
                        "pct": 100,
                        "totalScore": int(partial.get("total_score", 0)),
                    }
                elif node_name == "reporter":
                    runtime["reporter"] = {"status": "done", "pct": 100}

                for k, v in partial.items():
                    if k == "fallback_events" and v:
                        fallback_events.extend(v)
                        st.session_state.fallback_events.extend(v)
                    else:
                        final_state[k] = v
    except Exception as err:  # noqa: BLE001
        st.error(f"审查失败：{err}")
        st.code(traceback.format_exc())
        st.session_state.ui_state = "idle"
        return

    latency_ms = int((time.perf_counter() - started) * 1000)
    result = _build_result(
        final_state, detected_doc_type, submitted_at, latency_ms, fallback_events
    )
    st.session_state.runtime = runtime
    st.session_state.result = result
    st.session_state.ui_state = "done"
    _record_history(text, detected_doc_type, result)


# ---- Event dispatch ----
def _dispatch(event: dict) -> None:
    et = event.get("type")
    if et == "RUN":
        text = (event.get("text") or "").strip()
        if not text:
            return
        st.session_state.input_text = event["text"]
        st.session_state.tab = event.get("tab", st.session_state.tab)
        st.session_state.ui_state = "running"
        st.session_state.result = None
        st.session_state.runtime = _empty_runtime(st.session_state.tab)
        st.session_state.pending_run = {
            "text": event["text"],
            "tab": st.session_state.tab,
        }
    elif et == "CLEAR_INPUT":
        st.session_state.input_text = ""
    elif et == "SET_INPUT":
        st.session_state.input_text = event.get("text", "")
    elif et == "USE_SAMPLE":
        st.session_state.input_text = (
            SAMPLE_INCIDENT if st.session_state.tab == "incident" else SAMPLE_DELIVERY
        )
    elif et == "SET_TAB":
        new_tab = event.get("tab", st.session_state.tab)
        if new_tab != st.session_state.tab:
            st.session_state.tab = new_tab
            st.session_state.input_text = ""
            st.session_state.ui_state = "idle"
            st.session_state.runtime = {}
            st.session_state.result = None
    elif et == "SET_LANG":
        st.session_state.lang = event.get("lang", "zh")
    elif et == "SET_THEME":
        st.session_state.theme = event.get("theme", "light")
    elif et == "SET_PALETTE":
        st.session_state.palette_color = event.get("color", "#059669")
    elif et == "SET_DENSITY":
        st.session_state.density = event.get("density", "cozy")
    elif et == "SELECT_HISTORY":
        st.session_state.selected_history_idx = event.get("idx")
    elif et == "CLEAR_HISTORY":
        st.session_state.history = []
        st.session_state.selected_history_idx = None
        st.session_state.fallback_events = []


# ---- Main render ----
event = guardian_ui(
    lang=st.session_state.lang,
    theme=st.session_state.theme,
    palette_color=st.session_state.palette_color,
    density=st.session_state.density,
    tab=st.session_state.tab,
    state=st.session_state.ui_state,
    input_text=st.session_state.input_text,
    runtime=st.session_state.runtime,
    result=st.session_state.result,
    history=st.session_state.history,
    fallback_events=st.session_state.fallback_events,
    selected_history_idx=st.session_state.selected_history_idx,
)

# Process event from the iframe (only once per unique _ts).
if isinstance(event, dict):
    ts = event.get("_ts")
    if ts and ts != st.session_state.last_event_ts:
        st.session_state.last_event_ts = ts
        _dispatch(event)
        st.rerun()

# If a run is pending, execute the graph now (the iframe is already showing
# the running state from the most recent render). When done, rerun for the
# done state to be displayed.
if st.session_state.pending_run:
    pending = st.session_state.pending_run
    st.session_state.pending_run = None
    _run_review(pending["text"], pending["tab"])
    st.rerun()
