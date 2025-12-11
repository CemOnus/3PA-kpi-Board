
import streamlit as st
import pandas as pd

from kpi_config import (
    KPI_LIST,
    load_data,
    save_data,
    month_selector,
    get_month_name,
)

st.title("📥 Monthly KPI Data Entry — 3PA 2026")

selected_month, selected_month_name = month_selector("input")

st.subheader(f"Enter Actuals for {selected_month_name} 2026")

df = load_data()

with st.form("kpi_input_form"):
    st.write("Enter actual values for each KPI for the selected month. You can revise these later.")

    new_rows = []
    for kpi in KPI_LIST:
        kpi_name = kpi["name"]
        decimals = kpi["decimals"]

        mask = (df["Month"] == selected_month) & (df["KPI Name"] == kpi_name)
        existing_value = None
        if not df.loc[mask].empty:
            try:
                existing_value = float(df.loc[mask, "Actual"].iloc[0])
            except Exception:
                existing_value = None
        default_value = existing_value if existing_value is not None else 0.0

        label = f"{kpi_name} — {kpi['definition']} ({kpi['proposed_metric']})"
        value = st.number_input(
            label,
            value=float(default_value),
            step=0.01,
            key=f"input_{selected_month}_{kpi_name}",
        )
        new_rows.append({"Month": selected_month, "KPI Name": kpi_name, "Actual": value})

    submitted = st.form_submit_button("Save Actuals for Selected Month")

    if submitted:
        df = df[df["Month"] != selected_month]
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        save_data(df)
        st.success(f"Actuals saved for {selected_month_name} 2026.")

st.markdown("---")

st.subheader("Raw Data Preview (All Months Entered So Far)")
st.dataframe(df.sort_values(["Month", "KPI Name"]), use_container_width=True)
