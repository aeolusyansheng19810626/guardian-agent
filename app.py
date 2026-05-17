"""Guardian Agent — Streamlit entrypoint with custom React UI component."""
from __future__ import annotations

import threading
import time
import traceback
from datetime import datetime
from typing import Any

import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

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
# NOTE: must use st.html() — recent Streamlit versions sanitize <style> out of
# st.markdown(unsafe_allow_html=True).
st.html(
    """
    <style>
      header[data-testid="stHeader"],
      [data-testid="stToolbar"],
      [data-testid="stDecoration"],
      [data-testid="stStatusWidget"],
      [data-testid="stAppDeployButton"],
      [data-testid="stMainMenu"],
      footer { display: none !important; }

      [data-testid="stSidebar"] { display: none !important; }

      [data-testid="stAppViewContainer"] { padding: 0 !important; }

      [data-testid="stMain"],
      [data-testid="stMainBlockContainer"] {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
      }
      [data-testid="stMainBlockContainer"] > div { gap: 0 !important; }

      [data-testid="stVerticalBlock"] { gap: 0 !important; }

      .stApp,
      [data-testid="stApp"] { background: #f8fafc; }

      /* Streamlit wraps custom-component iframes in this container */
      [data-testid="stIFrame"] {
        height: 100vh !important;
        max-height: 100vh !important;
      }

      iframe[title*="guardian_ui"] {
        width: 100% !important;
        height: 100vh !important;
        border: 0 !important;
        display: block !important;
      }

      html, body { overflow: hidden !important; }
    </style>
    """
)


SAMPLE_DELIVERY = (
    "示例：\n系统需求文档，包含功能需求、非功能需求（系统响应要快）、"
    "系统架构图，缺少风险章节。"
)
SAMPLE_INCIDENT = (
    "2024年3月15日 14:00 系统发生障害。\n\n"
    "原因：服务器异常。\n対応：重启服务器。\n防止策：加强监控。"
)


# ---- Run handle (shared between main thread and graph thread) ----
class RunHandle:
    """Per-run shared state. Mutated by the worker thread, read by the
    main script on every rerun. Treated as snapshot-on-read: we replace
    runtime sub-dicts wholesale rather than in-place mutating them."""

    def __init__(self, text: str, doc_type: str) -> None:
        self.text = text
        self.doc_type = doc_type
        self.detected_doc_type = doc_type
        self.runtime: dict[str, dict] = _empty_runtime(doc_type)
        self.fallback_events: list[str] = []
        self.final_state: dict = {}
        self.submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.started = time.perf_counter()
        self.error: str | None = None
        self.done = False
        self.result: dict | None = None
        self._lock = threading.Lock()

    def update_node(self, key: str, value: dict) -> None:
        with self._lock:
            self.runtime = {**self.runtime, key: value}

    def snapshot_runtime(self) -> dict:
        with self._lock:
            return {k: dict(v) for k, v in self.runtime.items()}

    def drain_fallback(self) -> list[str]:
        with self._lock:
            out, self.fallback_events = self.fallback_events, []
            return out


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
        "run_handle": None,  # RunHandle instance while a graph run is in progress
        "run_error": None,   # str — last run's error, if any
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


# ---- Worker thread ----
def _run_review_thread(handle: RunHandle, graph: Any) -> None:
    """Run graph.stream and update handle.runtime as chunks arrive."""
    handle.update_node("classify", {"status": "running", "pct": 30})

    initial_state = {
        "raw_input": handle.text,
        "doc_type": handle.doc_type,
        "fallback_events": [],
    }

    try:
        for chunk in graph.stream(initial_state, stream_mode="updates"):
            for node_name, partial in chunk.items():
                partial = partial or {}
                if node_name == "classify":
                    handle.update_node("classify", {"status": "done", "pct": 100})
                    detected = partial.get("doc_type") or handle.doc_type
                    handle.detected_doc_type = detected
                    # Mark all active dims as running once classify completes.
                    # Without per-token streaming we can't track individual
                    # agents' progress, but switching them to "running" makes
                    # it visible they've kicked off in parallel.
                    for d in active_dimensions(detected):
                        handle.update_node(d, {"status": "running", "pct": 30})
                elif node_name in (
                    "completeness", "quality", "compliance", "logic", "prevention"
                ):
                    handle.update_node(node_name, {"status": "done", "pct": 100})
                elif node_name == "guardian":
                    handle.update_node("guardian", {
                        "status": "done",
                        "pct": 100,
                        "totalScore": int(partial.get("total_score", 0)),
                    })
                elif node_name == "reporter":
                    handle.update_node("reporter", {"status": "done", "pct": 100})

                for k, v in partial.items():
                    if k == "fallback_events" and v:
                        with handle._lock:
                            handle.fallback_events.extend(v)
                    else:
                        handle.final_state[k] = v
    except Exception as err:  # noqa: BLE001
        handle.error = f"{type(err).__name__}: {err}\n{traceback.format_exc()}"
        handle.done = True
        return

    latency_ms = int((time.perf_counter() - handle.started) * 1000)
    drained = handle.drain_fallback()
    handle.result = _build_result(
        handle.final_state,
        handle.detected_doc_type,
        handle.submitted_at,
        latency_ms,
        drained,
    )
    handle.done = True


# ---- Sync handle → session state on each script run ----
def _sync_run_handle() -> None:
    h: RunHandle | None = st.session_state.run_handle
    if h is None:
        return

    # Reflect current per-node runtime
    st.session_state.runtime = h.snapshot_runtime()

    # Drain any fallback events emitted so far
    fb = h.drain_fallback() if not h.done else []
    if fb:
        st.session_state.fallback_events.extend(fb)

    if h.done:
        if h.error:
            st.session_state.run_error = h.error
            st.session_state.ui_state = "idle"
        else:
            st.session_state.result = h.result
            st.session_state.ui_state = "done"
            _record_history(h.text, h.detected_doc_type, h.result)
        st.session_state.run_handle = None


def _start_run(text: str, doc_type: str) -> None:
    if st.session_state.graph is None:
        st.session_state.run_error = (
            f"图构建失败：{st.session_state.graph_err}"
        )
        return

    handle = RunHandle(text=text, doc_type=doc_type)
    st.session_state.run_handle = handle
    st.session_state.runtime = handle.snapshot_runtime()
    st.session_state.result = None
    st.session_state.run_error = None
    st.session_state.ui_state = "running"

    t = threading.Thread(
        target=_run_review_thread,
        args=(handle, st.session_state.graph),
        daemon=True,
    )
    # Required so the worker can see Streamlit's session context if it ever
    # touches session_state. We don't strictly need it because the worker only
    # mutates the handle, but it suppresses the "missing ScriptRunContext"
    # warning and keeps things future-proof.
    ctx = get_script_run_ctx()
    if ctx is not None:
        add_script_run_ctx(t, ctx)
    t.start()


# ---- Event dispatch ----
def _dispatch(event: dict) -> None:
    et = event.get("type")
    if et == "RUN":
        text = (event.get("text") or "").strip()
        if not text:
            return
        st.session_state.input_text = event["text"]
        st.session_state.tab = event.get("tab", st.session_state.tab)
        _start_run(event["text"], st.session_state.tab)
    elif et == "POLL":
        pass  # no state change — just triggers a rerun so handle gets resynced
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
_init_state()
_sync_run_handle()

if st.session_state.run_error:
    st.error(st.session_state.run_error)

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
