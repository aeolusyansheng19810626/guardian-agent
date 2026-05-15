"""Plotly visualization helpers."""
from __future__ import annotations

import plotly.graph_objects as go

from config import DIMENSION_LABELS


def radar_chart(scores: dict[str, int]) -> go.Figure:
    """scores: {dimension_key: 0-100}"""
    dims = list(scores.keys())
    labels = [DIMENSION_LABELS.get(d, d) for d in dims]
    values = [scores[d] for d in dims]
    # 闭合
    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=labels_closed,
            fill="toself",
            name="得分",
            line=dict(color="#1f77b4"),
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        margin=dict(l=40, r=40, t=30, b=30),
        height=380,
    )
    return fig


def trend_chart(history: list[dict]) -> go.Figure:
    """history: [{'idx': 1, 'score': 78, 'verdict': 'pass'}, ...]"""
    if not history:
        return go.Figure()

    xs = [h["idx"] for h in history]
    ys = [h["score"] for h in history]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines+markers",
            line=dict(color="#2ca02c"),
            marker=dict(size=10),
        )
    )
    fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="通过")
    fig.add_hline(y=60, line_dash="dash", line_color="orange", annotation_text="拦截线")
    fig.update_layout(
        xaxis_title="提交序号",
        yaxis_title="总分",
        yaxis=dict(range=[0, 100]),
        margin=dict(l=30, r=30, t=20, b=30),
        height=240,
    )
    return fig
