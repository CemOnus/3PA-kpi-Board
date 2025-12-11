
import os
from datetime import datetime
from typing import Tuple, List

import pandas as pd
import streamlit as st

DATA_FILE = "kpi_data_2026.csv"

KPI_LIST = [
    {
        "business_line": "3PA",
        "category": "Customer Success",
        "name": "CSAT",
        "definition": "Client Services Survey Score",
        "proposed_metric": "≥ 4.5 / 5",
        "baseline": 4.75,
        "target": 4.8,
        "direction": "gte",
        "agg": "avg",
        "decimals": 2,
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
        "decimals": 0,
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
        "decimals": 1,
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
        "decimals": 0,
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
        "decimals": 0,
    },
    {
        "business_line": "3PA",
        "category": "Safety",
        "name": "Safety Incidents",
        "definition": "Reported safety incidents",
        "proposed_metric": "0 incidents",
        "baseline": 0,
        "target": 0,
        "direction": "lte",
        "agg": "sum",
        "decimals": 0,
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
        "decimals": 2,
    },
]

KPI_DF = pd.DataFrame(KPI_LIST)


def load_data() -> pd.DataFrame:
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["Month", "KPI Name", "Actual"])
    return df


def save_data(df: pd.DataFrame) -> None:
    df.to_csv(DATA_FILE, index=False)


def get_month_name(month_number: int) -> str:
    return datetime(2026, month_number, 1).strftime("%B")


def get_prior_month(month_number: int) -> int:
    return 12 if month_number == 1 else month_number - 1


def month_selector(key_prefix: str = "rep") -> Tuple[int, str]:
    month_names = [get_month_name(m) for m in range(1, 13)]
    current_year = datetime.now().year
    default_index = 0
    if current_year == 2026:
        default_index = datetime.now().month - 1
        default_index = max(0, min(default_index, 11))
    selected_name = st.sidebar.selectbox(
        "Reporting month (2026)",
        options=month_names,
        index=default_index,
        key=f"{key_prefix}_month",
    )
    month_number = month_names.index(selected_name) + 1
    return month_number, selected_name


def get_monthly_actual(df: pd.DataFrame, month: int, kpi_name: str) -> float:
    mask = (df["Month"] == month) & (df["KPI Name"] == kpi_name)
    if df.loc[mask].empty:
        return float("nan")
    return df.loc[mask, "Actual"].mean()


def aggregate_ytd(df: pd.DataFrame, upto_month: int, kpi: dict) -> float:
    mask = (df["Month"] <= upto_month) & (df["KPI Name"] == kpi["name"])
    data = df.loc[mask, "Actual"]
    if data.empty:
        return float("nan")
    if kpi["agg"] == "avg":
        return data.mean()
    return data.sum()


def evaluate_rag(actual: float, target: float, direction: str) -> str:
    import math

    if actual is None or (isinstance(actual, float) and math.isnan(actual)):
        return "No Data"

    if target is None:
        return "No Data"

    if direction == "gte":
        if actual >= target:
            return "Green"
        elif actual >= 0.95 * target:
            return "Amber"
        else:
            return "Red"
    elif direction == "lte":
        # Special handling when the target is zero (e.g., safety incidents)
        if target == 0:
            if actual == 0:
                return "Green"
            elif actual == 1:
                return "Amber"
            else:
                return "Red"
        else:
            if actual <= target:
                return "Green"
            elif actual <= 1.05 * target:
                return "Amber"
            else:
                return "Red"
    return "No Data"


def rag_color(val: str) -> str:
    if val == "Green":
        return "background-color: #d1e7dd; color: #0f5132;"
    if val == "Amber":
        return "background-color: #fff3cd; color: #664d03;"
    if val == "Red":
        return "background-color: #f8d7da; color: #842029;"
    return ""


def format_value(value, decimals: int):
    import math

    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return f"{value:,.{decimals}f}"


def build_summary_table(df: pd.DataFrame, selected_month: int) -> pd.DataFrame:
    prior_month = get_prior_month(selected_month)
    rows = []

    for kpi in KPI_LIST:
        name = kpi["name"]
        direction = kpi["direction"]
        agg = kpi["agg"]
        decimals = kpi["decimals"]
        monthly_target = kpi["target"]

        prior_actual = get_monthly_actual(df, prior_month, name)
        current_actual = get_monthly_actual(df, selected_month, name)
        ytd_actual = aggregate_ytd(df, selected_month, kpi)

        prior_target = monthly_target
        current_target = monthly_target

        if agg == "avg":
            ytd_target = monthly_target
        else:
            ytd_target = monthly_target * selected_month

        prior_rag = evaluate_rag(prior_actual, prior_target, direction)
        current_rag = evaluate_rag(current_actual, current_target, direction)
        ytd_rag = evaluate_rag(ytd_actual, ytd_target, direction)

        rows.append(
            {
                "Business Line": kpi["business_line"],
                "Category": kpi["category"],
                "KPI Name": name,
                "KPI Definition": kpi["definition"],
                "Baseline": format_value(kpi["baseline"], decimals),
                "Proposed Metric": kpi["proposed_metric"],
                "Prior Month Actual": format_value(prior_actual, decimals),
                "Prior Month Target": format_value(prior_target, decimals),
                "Prior Month RAG": prior_rag,
                "Current MTD Actual": format_value(current_actual, decimals),
                "Current MTD Target": format_value(current_target, decimals),
                "Current MTD RAG": current_rag,
                "YTD Actual": format_value(ytd_actual, decimals),
                "YTD Target": format_value(ytd_target, decimals),
                "YTD RAG": ytd_rag,
            }
        )

    return pd.DataFrame(rows)


def get_kpi_by_name(name: str) -> dict:
    for kpi in KPI_LIST:
        if kpi["name"] == name:
            return kpi
    raise ValueError(f"KPI not found: {name}")
