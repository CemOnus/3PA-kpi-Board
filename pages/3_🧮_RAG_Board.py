
import streamlit as st
import pandas as pd

from kpi_config import (
    load_data,
    month_selector,
    build_summary_table,
    rag_color,
)

st.title("🧮 RAG Performance Board — 3PA 2026")

selected_month, selected_month_name = month_selector("rag")

df = load_data()
summary_df = build_summary_table(df, selected_month)

st.subheader(f"RAG Board — {selected_month_name} 2026")

status_cols = ["Prior Month RAG", "Current MTD RAG", "YTD RAG"]
styled = summary_df.style.applymap(rag_color, subset=status_cols)

st.dataframe(styled, use_container_width=True)

st.markdown("---")

st.subheader("RAG Distribution (Current MTD)")

rag_counts = (
    summary_df[["KPI Name", "Current MTD RAG"]]
    .groupby("Current MTD RAG")
    .count()
    .rename(columns={"KPI Name": "Count"})
)

st.table(rag_counts)
