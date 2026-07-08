"""UI styling and reusable components."""

from __future__ import annotations

import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 1.5rem;
    max-width: 1100px;
}

.hero {
    background: linear-gradient(135deg, rgba(99,102,241,0.25) 0%, rgba(14,165,233,0.15) 50%, rgba(168,85,247,0.2) 100%);
    border: 1px solid rgba(129, 140, 248, 0.35);
    border-radius: 20px;
    padding: 2rem 2.25rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "";
    position: absolute;
    top: -40%;
    right: -10%;
    width: 280px;
    height: 280px;
    background: radial-gradient(circle, rgba(34,211,238,0.25) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(34, 211, 238, 0.15);
    color: #67e8f9;
    border: 1px solid rgba(34, 211, 238, 0.35);
    border-radius: 999px;
    padding: 0.25rem 0.85rem;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}
.hero h1 {
    font-size: 2.35rem;
    font-weight: 800;
    margin: 0 0 0.5rem 0;
    background: linear-gradient(90deg, #f8fafc 0%, #c7d2fe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero p {
    color: #94a3b8;
    font-size: 1.05rem;
    margin: 0;
    max-width: 620px;
    line-height: 1.6;
}

.kpi-card {
    background: linear-gradient(180deg, rgba(30,41,59,0.9) 0%, rgba(15,23,42,0.95) 100%);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 16px;
    padding: 1.1rem 1.25rem;
    height: 100%;
}
.kpi-label {
    color: #94a3b8;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
}
.kpi-value {
    color: #f8fafc;
    font-size: 1.65rem;
    font-weight: 700;
}
.kpi-sub {
    color: #64748b;
    font-size: 0.75rem;
    margin-top: 0.25rem;
}

.section-label {
    color: #94a3b8;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 1.5rem 0 0.75rem 0;
}

.pipeline {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin: 1rem 0;
}
.pipeline-step {
    flex: 1;
    min-width: 120px;
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 12px;
    padding: 0.65rem 0.75rem;
    text-align: center;
    font-size: 0.78rem;
    color: #64748b;
}
.pipeline-step.active {
    border-color: rgba(129, 140, 248, 0.6);
    color: #c7d2fe;
    background: rgba(99, 102, 241, 0.15);
}
.pipeline-step.done {
    border-color: rgba(52, 211, 153, 0.4);
    color: #6ee7b7;
}

.insight-card {
    background: rgba(21, 27, 46, 0.8);
    border: 1px solid rgba(129, 140, 248, 0.2);
    border-radius: 16px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
}

.sidebar-title {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.5rem;
}

.guardrail-pill {
    display: inline-block;
    background: rgba(52, 211, 153, 0.12);
    color: #6ee7b7;
    border: 1px solid rgba(52, 211, 153, 0.25);
    border-radius: 999px;
    padding: 0.2rem 0.65rem;
    font-size: 0.72rem;
    margin: 0.15rem 0.25rem 0.15rem 0;
}

.badge-row { margin: 0.35rem 0 0.15rem 0; }
.badge {
    display: inline-block;
    border-radius: 999px;
    padding: 0.18rem 0.6rem;
    font-size: 0.7rem;
    font-weight: 600;
    margin: 0.1rem 0.3rem 0.1rem 0;
    border: 1px solid transparent;
}
.badge-latency {
    background: rgba(99, 102, 241, 0.14);
    color: #c7d2fe;
    border-color: rgba(129, 140, 248, 0.3);
}
.badge-cache {
    background: rgba(34, 211, 238, 0.12);
    color: #67e8f9;
    border-color: rgba(34, 211, 238, 0.3);
}
.badge-repair {
    background: rgba(251, 191, 36, 0.12);
    color: #fcd34d;
    border-color: rgba(251, 191, 36, 0.3);
}
.badge-ground-high {
    background: rgba(52, 211, 153, 0.14);
    color: #6ee7b7;
    border-color: rgba(52, 211, 153, 0.3);
}
.badge-ground-medium {
    background: rgba(251, 191, 36, 0.14);
    color: #fcd34d;
    border-color: rgba(251, 191, 36, 0.3);
}
.badge-ground-low {
    background: rgba(248, 113, 113, 0.14);
    color: #fca5a5;
    border-color: rgba(248, 113, 113, 0.3);
}

div[data-testid="stChatMessage"] {
    background: rgba(21, 27, 46, 0.5);
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 14px;
    padding: 0.5rem;
    margin-bottom: 0.75rem;
}

div[data-testid="stChatInput"] {
    border-radius: 14px;
}

.stButton > button {
    border-radius: 999px;
    border: 1px solid rgba(129, 140, 248, 0.35);
    background: rgba(99, 102, 241, 0.12);
    color: #c7d2fe;
    font-size: 0.82rem;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    border-color: rgba(129, 140, 248, 0.7);
    background: rgba(99, 102, 241, 0.25);
    color: #eef2ff;
}
</style>
"""


def inject_styles() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-badge">AI-Powered Analytics</div>
            <h1>Ask your data anything.</h1>
            <p>
                Natural language in, SQL out — grounded answers and live charts
                from a multi-table retail database. Built for non-technical teams.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(kpis: dict[str, str]) -> None:
    cols = st.columns(4)
    labels = [
        ("Total Revenue", kpis["revenue"], "Completed orders"),
        ("Orders", kpis["orders"], "Successfully fulfilled"),
        ("Customers", kpis["customers"], "Active accounts"),
        ("Products", kpis["products"], "In catalog"),
    ]
    for col, (label, value, sub) in zip(cols, labels):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-sub">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_pipeline_step(step: int) -> None:
    steps = ["Understand", "Generate SQL", "Run Query", "Visualize"]
    html = '<div class="pipeline">'
    for i, name in enumerate(steps):
        if i < step:
            cls = "pipeline-step done"
        elif i == step:
            cls = "pipeline-step active"
        else:
            cls = "pipeline-step"
        html += f'<div class="{cls}">{i + 1}. {name}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_metric_badges(message: dict) -> None:
    """Render latency / groundedness / cache / repair badges for an answer."""
    badges: list[str] = []

    timings = message.get("timings") or {}
    total_ms = timings.get("total_ms")
    if total_ms:
        secs = total_ms / 1000
        badges.append(f'<span class="badge badge-latency">⚡ {secs:.1f}s</span>')

    label = message.get("groundedness_label")
    score = message.get("groundedness")
    if label and score is not None:
        cls = f"badge-ground-{label.lower()}"
        badges.append(
            f'<span class="badge {cls}">◆ Groundedness: {label} ({score:.0%})</span>'
        )

    if message.get("cached"):
        badges.append('<span class="badge badge-cache">⚡ Cached</span>')

    if message.get("repair_attempts"):
        badges.append(
            f'<span class="badge badge-repair">🔧 Auto-repaired '
            f'({message["repair_attempts"]}x)</span>'
        )

    if badges:
        st.markdown(
            f'<div class="badge-row">{"".join(badges)}</div>',
            unsafe_allow_html=True,
        )


def render_latency_breakdown(timings: dict) -> None:
    if not timings:
        return
    stages = [
        ("Plan (NL→SQL)", timings.get("plan_ms")),
        ("Execute SQL", timings.get("execute_ms")),
        ("Repair", timings.get("repair_ms")),
        ("Summarize", timings.get("summarize_ms")),
        ("Total", timings.get("total_ms")),
    ]
    lines = [f"{name:<16} {ms:>7.0f} ms" for name, ms in stages if ms]
    if lines:
        st.code("\n".join(lines), language=None)


def render_eval_report(report) -> None:
    import pandas as pd

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Pass Rate</div>'
            f'<div class="kpi-value">{report.pass_rate:.0%}</div>'
            f'<div class="kpi-sub">{report.passed}/{report.total} cases</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Avg Latency</div>'
            f'<div class="kpi-value">{report.avg_latency_ms / 1000:.1f}s</div>'
            f'<div class="kpi-sub">end-to-end</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Avg Groundedness</div>'
            f'<div class="kpi-value">{report.avg_groundedness:.0%}</div>'
            f'<div class="kpi-sub">numeric claims supported</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">By category</div>', unsafe_allow_html=True)
    cat_df = pd.DataFrame(
        [
            {"Category": k, "Passed": v[0], "Total": v[1], "Rate": f"{v[0] / v[1]:.0%}"}
            for k, v in sorted(report.by_category().items())
        ]
    )
    st.dataframe(cat_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-label">Per-case results</div>', unsafe_allow_html=True)
    rows = []
    for r in report.results:
        rows.append(
            {
                "Result": "✅ PASS" if r.passed else "❌ FAIL",
                "Category": r.category,
                "Question": r.question,
                "Latency": f"{r.latency_ms / 1000:.1f}s",
                "Grounded": f"{r.groundedness:.0%}" if r.groundedness is not None else "—",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_sidebar() -> None:
    from src.database import get_schema_description

    st.markdown('<div class="sidebar-title">How it works</div>', unsafe_allow_html=True)
    st.markdown(
        """
```mermaid
erDiagram
    categories ||--o{ products : has
    customers ||--o{ orders : places
    orders ||--o{ order_items : contains
    products ||--o{ order_items : "sold in"
```
        """
    )
    st.markdown('<div class="sidebar-title">Security</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <span class="guardrail-pill">Read-only SQL</span>
        <span class="guardrail-pill">Table whitelist</span>
        <span class="guardrail-pill">Injection filter</span>
        <span class="guardrail-pill">Ambiguity checks</span>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Full schema"):
        st.code(get_schema_description(), language=None)
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()
