
import streamlit as st
import pandas as pd

from kpi_config import (
    load_data,
    month_selector,
    build_summary_table,
    rag_color,
)

st.set_page_config(
    page_title="3PA KPI Executive Dashboard 2026",
    layout="wide",
)

st.title("3PA KPI Executive Dashboard — 2026")

st.sidebar.markdown("### Navigation")
st.sidebar.markdown("Use the pages in the sidebar to access:\n\n- Monthly Data Entry\n- KPI Trend Graphs\n- RAG Performance Board")

selected_month, selected_month_name = month_selector("overview")

df = load_data()
summary_df = build_summary_table(df, selected_month)

st.subheader(f"Executive Overview — {selected_month_name} 2026")

status_cols = ["Prior Month RAG", "Current MTD RAG", "YTD RAG"]
styled = summary_df.style.applymap(rag_color, subset=status_cols)

st.dataframe(styled, use_container_width=True)

st.markdown("---")

st.subheader("At-a-Glance RAG Summary")

rag_counts = (
    summary_df[["KPI Name", "Current MTD RAG"]]
    .groupby("Current MTD RAG")
    .count()
    .rename(columns={"KPI Name": "Count"})
)

st.table(rag_counts)

st.caption(
    "This overview shows prior month, current month-to-date, and year-to-date performance "
    "against monthly targets for all 3PA KPIs."
)
