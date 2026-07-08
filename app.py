"""Conversational Data Analyst — Streamlit UI."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.agent import ask, cache_stats
from src.charts import build_chart
from src.dashboard import SAMPLE_QUESTIONS, get_kpis
from src.seed_data import seed_database
from src.ui import (
    inject_styles,
    render_eval_report,
    render_hero,
    render_kpi_row,
    render_latency_breakdown,
    render_metric_badges,
    render_pipeline_step,
    render_sidebar,
)

st.set_page_config(
    page_title="InsightAgent | Conversational Data Analyst",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

seed_database()
inject_styles()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None
if "eval_report" not in st.session_state:
    st.session_state.eval_report = None
if "msg_counter" not in st.session_state:
    st.session_state.msg_counter = 0

with st.sidebar:
    st.markdown("### ✦ InsightAgent")
    st.caption("Conversational analytics for retail data")
    render_sidebar()

render_hero()

try:
    render_kpi_row(get_kpis())
except Exception:
    pass

chat_tab, eval_tab = st.tabs(["  Chat  ", "  Evaluation  "])


def render_answer_extras(msg: dict) -> None:
    mid = msg.get("id", id(msg))
    render_metric_badges(msg)
    if msg.get("sql"):
        st.markdown("**Generated SQL**")
        st.code(msg["sql"], language="sql")
    if msg.get("chart"):
        st.plotly_chart(msg["chart"], use_container_width=True, key=f"chart_{mid}")
    if msg.get("table") is not None:
        st.dataframe(
            msg["table"], use_container_width=True, hide_index=True, key=f"table_{mid}"
        )
    if msg.get("csv"):
        st.download_button(
            "⬇ Download results (CSV)",
            data=msg["csv"],
            file_name="query_results.csv",
            mime="text/csv",
            key=f"dl_{mid}",
        )
    if msg.get("timings"):
        with st.expander("Latency breakdown"):
            render_latency_breakdown(msg["timings"])


def render_message(message: dict) -> None:
    avatar = ":material/person:" if message["role"] == "user" else ":material/smart_toy:"
    with st.chat_message(message["role"], avatar=avatar):
        if message["role"] == "assistant":
            st.markdown(
                f'<div class="insight-card">{message["content"]}</div>',
                unsafe_allow_html=True,
            )
            render_answer_extras(message)
        else:
            st.markdown(message["content"])


def build_assistant_message(prompt: str) -> dict:
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
        if m["role"] in ("user", "assistant")
    ][:-1]

    with st.status("Analyzing your question...", expanded=True) as status:
        render_pipeline_step(0)
        status.write("Understanding question and schema context...")
        render_pipeline_step(1)
        status.write("Generating read-only SQL query...")
        result = ask(prompt, history)
        render_pipeline_step(2)
        status.write("Executing query against SQLite...")
        render_pipeline_step(3)
        status.write("Verifying groundedness and building visualization...")

        chart_fig = None
        df = None
        csv_data = None
        if result.rows and result.columns:
            df = pd.DataFrame(result.rows, columns=result.columns)
            csv_data = df.to_csv(index=False).encode("utf-8")
            chart_fig = build_chart(
                result.columns, result.rows, result.chart_type, result.chart_config
            )

        if result.blocked:
            status.update(label="Request handled safely", state="complete")
        elif result.clarification:
            status.update(label="Clarification needed", state="complete")
        else:
            status.update(label="Analysis complete", state="complete")

    st.session_state.msg_counter += 1
    msg_id = st.session_state.msg_counter
    return {
        "id": msg_id,
        "role": "assistant",
        "content": result.answer,
        "sql": result.sql,
        "chart": chart_fig,
        "table": (
            df if chart_fig is None and df is not None and len(result.rows) > 1 else None
        ),
        "csv": csv_data,
        "timings": result.timings,
        "groundedness": result.groundedness,
        "groundedness_label": result.groundedness_label,
        "cached": result.cached,
        "repair_attempts": result.repair_attempts,
    }


with chat_tab:
    st.markdown('<div class="section-label">Suggested questions</div>', unsafe_allow_html=True)
    pill_cols = st.columns(3)
    for i, question in enumerate(SAMPLE_QUESTIONS):
        with pill_cols[i % 3]:
            if st.button(question, key=f"sample_{i}", use_container_width=True):
                st.session_state.pending_prompt = question
                st.rerun()

    st.markdown('<div class="section-label">Conversation</div>', unsafe_allow_html=True)

    for message in st.session_state.messages:
        render_message(message)

    if st.session_state.pending_prompt:
        st.session_state.messages.append(
            {"role": "user", "content": st.session_state.pending_prompt}
        )
        st.session_state.pending_prompt = None
        st.rerun()

    needs_response = (
        st.session_state.messages and st.session_state.messages[-1]["role"] == "user"
    )
    if needs_response:
        last_prompt = st.session_state.messages[-1]["content"]
        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            try:
                assistant_msg = build_assistant_message(last_prompt)
            except RuntimeError as exc:
                st.error(str(exc))
                st.stop()
            st.markdown(
                f'<div class="insight-card">{assistant_msg["content"]}</div>',
                unsafe_allow_html=True,
            )
            render_answer_extras(assistant_msg)
        st.session_state.messages.append(assistant_msg)
        st.rerun()

    if prompt := st.chat_input("Ask anything about revenue, orders, customers, or products..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    stats = cache_stats()
    if stats["hits"] + stats["misses"] > 0:
        st.caption(
            f"Cache: {stats['hits']} hits / {stats['misses']} misses "
            f"({stats['hit_rate']:.0%} hit rate)"
        )


with eval_tab:
    st.markdown('<div class="section-label">Automated evaluation</div>', unsafe_allow_html=True)
    st.caption(
        "Runs a golden dataset of questions and scores SQL correctness, "
        "groundedness, ambiguity handling, guardrails, and latency. "
        "Ground truth is computed live from the database."
    )
    col_run, col_note = st.columns([1, 3])
    with col_run:
        run_eval = st.button("▶ Run evaluation", use_container_width=True)
    with col_note:
        st.caption(
            "Uses ~12 API calls. On the free tier, pace requests if you hit a rate limit."
        )

    if run_eval:
        from src.evaluation import run_evaluation

        progress = st.progress(0.0, text="Starting evaluation...")

        def _on_progress(i, total, result):
            progress.progress(
                i / total,
                text=f"{i}/{total} — {result.question[:48]}",
            )

        try:
            report = run_evaluation(on_progress=_on_progress, delay_seconds=0.0)
            st.session_state.eval_report = report
            progress.empty()
        except Exception as exc:
            progress.empty()
            st.error(f"Evaluation failed: {exc}")

    if st.session_state.eval_report is not None:
        render_eval_report(st.session_state.eval_report)
    else:
        st.info("Click **Run evaluation** to score the agent against the golden dataset.")
