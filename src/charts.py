"""Chart rendering from agent results."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CHART_COLORS = ["#818cf8", "#22d3ee", "#a78bfa", "#34d399", "#fbbf24", "#f472b6"]
LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,23,42,0.4)",
    font=dict(family="Inter, sans-serif", color="#e2e8f0", size=13),
    title=dict(font=dict(size=16, color="#f1f5f9")),
    margin=dict(l=24, r=24, t=48, b=24),
    colorway=CHART_COLORS,
    xaxis=dict(gridcolor="rgba(148,163,184,0.12)", zeroline=False),
    yaxis=dict(gridcolor="rgba(148,163,184,0.12)", zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def build_chart(
    columns: list[str],
    rows: list[tuple],
    chart_type: str | None,
    chart_config: dict[str, Any] | None,
):
    if not rows or not columns or chart_type in (None, "none"):
        return None

    df = pd.DataFrame(rows, columns=columns)
    config = chart_config or {}
    title = config.get("title", "Results")
    x_col = config.get("x_column")
    y_col = config.get("y_column")

    if x_col and x_col not in df.columns:
        x_col = None
    if y_col and y_col not in df.columns:
        y_col = None

    if not x_col and len(df.columns) >= 1:
        x_col = df.columns[0]
    if not y_col and len(df.columns) >= 2:
        y_col = df.columns[1]

    try:
        if chart_type == "bar" and x_col and y_col:
            fig = px.bar(
                df, x=x_col, y=y_col, title=title, color_discrete_sequence=CHART_COLORS
            )
            fig.update_traces(marker_line_width=0, opacity=0.92)
        elif chart_type == "line" and x_col and y_col:
            fig = px.line(
                df, x=x_col, y=y_col, title=title, markers=True,
                color_discrete_sequence=["#22d3ee"],
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
        elif chart_type == "pie" and x_col and y_col:
            fig = px.pie(
                df, names=x_col, values=y_col, title=title, color_discrete_sequence=CHART_COLORS
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
        elif chart_type == "table":
            fig = go.Figure(
                data=[
                    go.Table(
                        header=dict(
                            values=[f"  {c}  " for c in df.columns],
                            fill_color="#4338ca",
                            font=dict(color="white", size=12),
                            align="left",
                        ),
                        cells=dict(
                            values=[df[c] for c in df.columns],
                            fill_color=[["#1e293b", "#0f172a"] * len(df)],
                            font=dict(color="#e2e8f0", size=11),
                            align="left",
                            height=28,
                        ),
                    )
                ]
            )
            fig.update_layout(title=title)
        else:
            return None

        fig.update_layout(**LAYOUT)
        fig.update_layout(height=380)
        return fig
    except Exception:
        return None
