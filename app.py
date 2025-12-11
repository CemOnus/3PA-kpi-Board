
import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="3PA 2026 KPI Dashboard", layout="wide")

DATA_FILE = "kpi_data_2026.csv"

# ---- KPI CONFIGURATION ----
KPI_LIST = [
    {
        "business_line": "3PA",
        "category": "Customer Success",
        "name": "CSAT",
        "definition": "Client Services Survey Score",
        "proposed_metric": "≥ 4.5 / 5",
        "baseline": 4.75,
        "target": 4.8,
        "direction": "gte",      # higher is better
        "agg": "avg",           # YTD aggregation
        "decimals": 2
    },
    {
        "business_line": "3PA",
        "category": "Customer Success",
        "name": "NPS",
        "definition": "Net Promoter Score",
        "proposed_metric": "≥ 50 NPS",
        "baseline": 87,
        "target": 90,
        "direction": "gte",
        "agg": "avg",
        "decimals": 0
    },
    {
        "business_line": "3PA",
        "category": "Timeliness",
        "name": "Timeliness",
        "definition": '% of audits scheduled as "LOCKED" by 1st of the Month',
        "proposed_metric": "≥ 80%",
        "baseline": 90,
        "target": 90,
        "direction": "gte",
        "agg": "avg",
        "decimals": 1
    },
    {
        "business_line": "3PA",
        "category": "Sales",
        "name": "Sales Performance",
        "definition": "Monthly Sales Quota Met ($)",
        "proposed_metric": "≥ 90% of quota (Target $400k)",
        "baseline": 400000,
        "target": 400000,
        "direction": "gte",
        "agg": "sum",
        "decimals": 0
    },
    {
        "business_line": "3PA",
        "category": "Sales",
        "name": "Marketing Performance",
        "definition": "Sales Accepted Leads (SALs)",
        "proposed_metric": "≥ 40 SALs / month",
        "baseline": 25,
        "target": 40,
        "direction": "gte",
        "agg": "sum",
        "decimals": 0
    },
    {
        "business_line": "3PA",
        "category": "Safety",
        "name": "Safety Incidents",
        "definition": "Reported safety incidents",
        "proposed_metric": "0 incidents",
        "baseline": 0,
        "target": 0,
        "direction": "lte",     # lower is better
        "agg": "sum",
        "decimals": 0
    },
    {
        "business_line": "3PA",
        "category": "Quality",
        "name": "Quality Score",
        "definition": "Auditor Performance Survey Score",
        "proposed_metric": "≥ 4.5 / 5",
        "baseline": 4.8,
        "target": 4.9,
        "direction": "gte",
        "agg": "avg",
        "decimals": 2
    },
]

KPI_DF = pd.DataFrame(KPI_LIST)

# ---- HELPERS ----
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["Month", "KPI Name", "Actual"])
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def get_month_name(month_number: int) -> str:
    return datetime(2026, month_number, 1).strftime("%B")

def evaluate_status(actual, target, direction):
    if pd.isna(actual):
        return "No Data"
    if direction == "gte":
        return "On Track" if actual >= target else "Below Target"
    elif direction == "lte":
        return "On Track" if actual <= target else "Above Target"
    return "N/A"

def format_value(value, decimals):
    if pd.isna(value):
        return ""
    return f"{value:,.{decimals}f}"

# ---- MAIN APP ----
st.title("3PA 2026 KPI Dashboard")

st.caption("Monthly input and automated MTD / YTD tracking for 3PA KPIs (2026 calendar year).")

df = load_data()

# Month selector
month_names = [get_month_name(m) for m in range(1, 13)]
current_year = datetime.now().year
default_month = 1
if current_year == 2026:
    default_month = datetime.now().month

selected_month_name = st.selectbox(
    "Select month for data entry and MTD/YTD view",
    options=month_names,
    index=default_month - 1,
)
selected_month = month_names.index(selected_month_name) + 1

st.markdown("---")

# ---- DATA ENTRY ----
st.subheader(f"Monthly KPI Input — {selected_month_name} 2026")

with st.form("kpi_input_form"):
    input_cols = st.columns(2)
    with input_cols[0]:
        st.write("Enter **actual** values for each KPI for this month.")
    with input_cols[1]:
        st.write("If you don't have data for a KPI yet, you can leave it as 0 and update later.")

    new_rows = []
    for kpi in KPI_LIST:
        kpi_name = kpi["name"]
        mask = (df["Month"] == selected_month) & (df["KPI Name"] == kpi_name)
        existing_value = None
        if not df.loc[mask].empty:
            try:
                existing_value = float(df.loc[mask, "Actual"].iloc[0])
            except Exception:
                existing_value = None

        default_value = existing_value if existing_value is not None else 0.0

        label = f"{kpi_name} — {kpi['definition']}"
        value = st.number_input(
            label,
            value=float(default_value),
            step=0.01,
            key=f"input_{selected_month}_{kpi_name}",
        )
        new_rows.append({"Month": selected_month, "KPI Name": kpi_name, "Actual": value})

    submitted = st.form_submit_button("Save Actuals for Selected Month")

    if submitted:
        # Remove existing records for this month, then append new ones
        df = df[df["Month"] != selected_month]
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        save_data(df)
        st.success(f"Actuals saved for {selected_month_name} 2026.")

st.markdown("---")

# ---- KPI PERFORMANCE CALCULATIONS ----
st.subheader("KPI Performance Overview")

summary_rows = []

for kpi in KPI_LIST:
    kpi_name = kpi["name"]
    direction = kpi["direction"]
    agg = kpi["agg"]
    decimals = kpi["decimals"]
    monthly_target = kpi["target"]

    # MTD
    m_mask = (df["Month"] == selected_month) & (df["KPI Name"] == kpi_name)
    mtd_actual = df.loc[m_mask, "Actual"].mean() if not df.loc[m_mask].empty else float("nan")
    mtd_target = monthly_target

    # YTD (up to selected month)
    ytd_mask = (df["Month"] <= selected_month) & (df["KPI Name"] == kpi_name)
    ytd_data = df.loc[ytd_mask, "Actual"]

    if ytd_data.empty:
        ytd_actual = float("nan")
    else:
        if agg == "avg":
            ytd_actual = ytd_data.mean()
        else:  # "sum"
            ytd_actual = ytd_data.sum()

    # YTD target logic
    if agg == "avg":
        ytd_target = monthly_target
    else:
        ytd_target = monthly_target * selected_month

    summary_rows.append(
        {
            "Business Line": kpi["business_line"],
            "Category": kpi["category"],
            "KPI Name": kpi_name,
            "KPI Definition": kpi["definition"],
            "Proposed Metric": kpi["proposed_metric"],
            "Baseline": format_value(kpi["baseline"], decimals),
            "MTD Actual": format_value(mtd_actual, decimals),
            "MTD Target": format_value(mtd_target, decimals),
            "MTD Status": evaluate_status(mtd_actual, mtd_target, direction),
            "YTD Actual": format_value(ytd_actual, decimals),
            "YTD Target": format_value(ytd_target, decimals),
            "YTD Status": evaluate_status(ytd_actual, ytd_target, direction),
        }
    )

summary_df = pd.DataFrame(summary_rows)

# Simple status coloring
def color_status(val):
    if val == "On Track":
        return "background-color: #d1e7dd; color: #0f5132;"  # greenish
    if val in ("Below Target", "Above Target"):
        return "background-color: #f8d7da; color: #842029;"  # reddish
    return ""

status_cols = ["MTD Status", "YTD Status"]
styled_summary = summary_df.style.applymap(color_status, subset=status_cols)

st.dataframe(styled_summary, use_container_width=True)

st.markdown("---")

# ---- HIGH LEVEL METRIC CARDS ----
st.subheader(f"MTD Snapshot — {selected_month_name} 2026")

cols = st.columns(len(KPI_LIST))
for idx, kpi in enumerate(KPI_LIST):
    kpi_name = kpi["name"]
    m_mask = (df["Month"] == selected_month) & (df["KPI Name"] == kpi_name)
    mtd_actual = df.loc[m_mask, "Actual"].mean() if not df.loc[m_mask].empty else float("nan")
    monthly_target = kpi["target"]
    direction = kpi["direction"]

    delta = ""
    if not pd.isna(mtd_actual):
        if direction == "gte":
            delta_val = mtd_actual - monthly_target
        else:
            delta_val = monthly_target - mtd_actual
        delta = f"{delta_val:.2f}"

    display_value = format_value(mtd_actual, kpi["decimals"]) if not pd.isna(mtd_actual) else "n/a"

    with cols[idx]:
        st.metric(
            label=kpi_name,
            value=display_value,
            delta=delta if delta else None,
            help=kpi["definition"],
        )

st.markdown("---")
st.caption("Data is stored locally in 'kpi_data_2026.csv' in the app directory. Commit this file to GitHub if you want to preserve month-to-month history.")
