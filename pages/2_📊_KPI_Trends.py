
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from kpi_config import (
    KPI_LIST,
    load_data,
    get_month_name,
    get_monthly_actual,
    get_kpi_by_name,
)

st.title("📊 KPI Trend Graphs — 3PA 2026")

df = load_data()

if df.empty:
    st.info("No data available yet. Please enter KPI values on the 'Monthly KPI Data Entry' page.")
else:
    kpi_names = [k["name"] for k in KPI_LIST]
    selected_kpi_name = st.selectbox("Select KPI", options=kpi_names)
    kpi = get_kpi_by_name(selected_kpi_name)

    months = list(range(1, 13))
    month_labels = [get_month_name(m)[:3] for m in months]

    actuals = [get_monthly_actual(df, m, selected_kpi_name) for m in months]
    monthly_target = kpi["target"]
    targets = [monthly_target for _ in months]

    st.subheader(f"Monthly Actual vs Target — {selected_kpi_name}")

    fig1, ax1 = plt.subplots()
    ax1.plot(months, actuals, marker="o", label="Actual")
    ax1.plot(months, targets, linestyle="--", label="Target")
    ax1.set_xticks(months)
    ax1.set_xticklabels(month_labels, rotation=45)
    ax1.set_ylabel("Value")
    ax1.set_xlabel("Month (2026)")
    ax1.legend()
    ax1.set_title(f"{selected_kpi_name}: Actual vs Monthly Target")
    st.pyplot(fig1)

    if kpi["agg"] == "sum":
        cumulative_actuals = []
        running_total = 0.0
        for val in actuals:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                running_total += 0
            else:
                running_total += val
            cumulative_actuals.append(running_total)
        cumulative_targets = [monthly_target * m for m in months]

        st.subheader(f"YTD Cumulative Performance — {selected_kpi_name}")

        fig2, ax2 = plt.subplots()
        ax2.plot(months, cumulative_actuals, marker="o", label="YTD Actual")
        ax2.plot(months, cumulative_targets, linestyle="--", label="YTD Target")
        ax2.set_xticks(months)
        ax2.set_xticklabels(month_labels, rotation=45)
        ax2.set_ylabel("Cumulative Value")
        ax2.set_xlabel("Month (2026)")
        ax2.legend()
        ax2.set_title(f"{selected_kpi_name}: YTD Actual vs YTD Target")
        st.pyplot(fig2)
