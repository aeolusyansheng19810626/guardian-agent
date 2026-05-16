"""Guardian UI — Streamlit custom component (React).

Two modes:
- Production: serve the vite-built dist (default).
- Dev: set GUARDIAN_UI_DEV=1 + run `npm run dev` in frontend/ at port 5173.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import streamlit.components.v1 as components

_DEV = os.getenv("GUARDIAN_UI_DEV", "").lower() in {"1", "true", "yes"}
_HERE = Path(__file__).parent
_DIST = _HERE / "frontend" / "dist"

if _DEV:
    _component_func = components.declare_component(
        "guardian_ui",
        url="http://localhost:5173",
    )
else:
    _component_func = components.declare_component(
        "guardian_ui",
        path=str(_DIST),
    )


def guardian_ui(
    *,
    lang: str,
    theme: str,
    palette_color: str,
    density: str,
    tab: str,
    state: str,
    input_text: str,
    runtime: dict,
    result: dict | None,
    history: list[dict],
    fallback_events: list[str],
    selected_history_idx: int | None,
    key: str = "guardian_ui",
    default: Any = None,
):
    """Render the Guardian UI and return whatever the user did (an event dict).

    The component returns `None` initially, then a dict shaped like
    {"type": "RUN", "text": "...", "tab": "incident", "_ts": 12345}
    when the user clicks something.
    """
    return _component_func(
        lang=lang,
        theme=theme,
        paletteColor=palette_color,
        density=density,
        tab=tab,
        state=state,
        inputText=input_text,
        runtime=runtime,
        result=result,
        history=history,
        fallbackEvents=fallback_events,
        selectedHistoryIdx=selected_history_idx,
        key=key,
        default=default,
    )


__all__ = ["guardian_ui"]
