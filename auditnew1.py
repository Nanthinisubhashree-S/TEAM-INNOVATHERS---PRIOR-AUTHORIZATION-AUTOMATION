#auditnew1.py
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from io import BytesIO

DB_PATH = "prior_auth.db"

@st.cache_data(ttl=60)
def get_audit_logs():
    """Fetch all audit logs from DB"""
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY timestamp DESC", conn)
    return df

def compute_delta(current, previous, total_logs=None):
    """Return delta percentage.
       If no previous data, fall back to current/total_logs %.
    """
    if previous == 0:
        if total_logs and total_logs > 0:
            return f"{(current / total_logs * 100):.1f}%"
        return "0.0%"
    try:
        pct = (current - previous) / previous * 100.0
        sign = "+" if pct >= 0 else ""
        return f"{sign}{pct:.1f}%"
    except Exception:
        return "N/A"

def render_audit_page():
    st.title("📊 Smart Audit Explorer")

    df = get_audit_logs()
    if df.empty:
        st.warning("No audit logs found!")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    if "final_decision" not in df:
        df["final_decision"] = ""
    df["final_decision"] = (
        df["final_decision"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
        .replace({
            "APPROVE": "APPROVED",
            "DENY": "DENIED",
            "APPROVED.": "APPROVED",
            "DENIED.": "DENIED",
        })
    )

    st.sidebar.header("Filters")
    patient_filter = st.sidebar.text_input("Patient ID")
    provider_filter = st.sidebar.text_input("Provider NPI")
    treatment_filter = st.sidebar.text_input("Treatment Name")

    decision_options = sorted([x for x in df["final_decision"].unique().tolist() if x])
    final_decision_filter = st.sidebar.selectbox(
        "Final Decision",
        ["All"] + decision_options
    )

    non_null_ts = df["timestamp"].dropna()
    if non_null_ts.empty:
        start_default = end_default = date.today()
    else:
        start_default = non_null_ts.min().date()
        end_default = non_null_ts.max().date()

    date_range = st.sidebar.date_input(
        "Date",
        [start_default, end_default]
    )

    base_filtered = df.copy()

    if patient_filter:
        base_filtered = base_filtered[
            base_filtered["patient_id"].astype(str).str.contains(patient_filter, case=False, na=False)
        ]
    if provider_filter:
        base_filtered = base_filtered[
            base_filtered["provider_npi"].astype(str).str.contains(provider_filter, case=False, na=False)
        ]
    if treatment_filter:
        base_filtered = base_filtered[
            base_filtered["treatment_name"].astype(str).str.contains(treatment_filter, case=False, na=False)
        ]
    if final_decision_filter != "All":
        base_filtered = base_filtered[base_filtered["final_decision"] == final_decision_filter]

    df_filtered = base_filtered.copy()
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_filtered[
            (df_filtered["timestamp"].dt.date >= start_date) &
            (df_filtered["timestamp"].dt.date <= end_date)
        ]

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = start_default, end_default

    period_days = (end_date - start_date).days + 1
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days - 1)
    df_prev_period = base_filtered[
        (base_filtered["timestamp"].dt.date >= prev_start) &
        (base_filtered["timestamp"].dt.date <= prev_end)
    ]

    st.subheader("📌 Summary")

    total_logs = int(len(df_filtered))
    approved_count = int(df_filtered["final_decision"].value_counts().get("APPROVED", 0))
    denied_count = int(df_filtered["final_decision"].value_counts().get("DENIED", 0))
    pending_count = int(df_filtered["final_decision"].value_counts().get("PENDING", 0))

    prev_total = int(len(df_prev_period))
    prev_approved = int(df_prev_period["final_decision"].value_counts().get("APPROVED", 0))
    prev_denied = int(df_prev_period["final_decision"].value_counts().get("DENIED", 0))
    prev_pending = int(df_prev_period["final_decision"].value_counts().get("PENDING", 0))

    total_delta = compute_delta(total_logs, prev_total, total_logs)
    approved_delta = compute_delta(approved_count, prev_approved, total_logs)
    denied_delta = compute_delta(denied_count, prev_denied, total_logs)
    pending_delta = compute_delta(pending_count, prev_pending, total_logs)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Logs", total_logs, total_delta)
    col2.metric("Approved", approved_count, approved_delta)
    col3.metric("Denied", denied_count, denied_delta, delta_color="inverse")

    st.subheader("📈 Visual Insights")

    if not df_filtered.empty:
        # Pie chart
        decision_counts = (
            df_filtered["final_decision"]
            .value_counts()
            .reset_index()
        )
        decision_counts.columns = ["decision", "count"]
        decision_counts["percentage"] = (
            decision_counts["count"] / decision_counts["count"].sum() * 100
        ).round(1)

        fig_pie = px.pie(
            decision_counts,
            names="decision",
            values="count",
            title="Decision Status",
            hole=0.4
        )
        fig_pie.update_traces(
            textinfo="label+percent",
            hovertemplate="%{label}: %{value} (%{percent})"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        trend = df_filtered.groupby(df_filtered["timestamp"].dt.date).size().reset_index(name="count")
        trend.columns = ["timestamp", "count"]
        fig_line = px.line(trend, x="timestamp", y="count", title="Logs Trend", markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

        if "provider_npi" in df_filtered:
            top_providers = df_filtered["provider_npi"].astype(str).value_counts().head(5).reset_index()
            top_providers.columns = ["provider_npi", "count"]
            fig_prov = px.bar(
                top_providers, x="provider_npi", y="count", title="Top 5 Providers", color="provider_npi"
            )
            st.plotly_chart(fig_prov, use_container_width=True)
    else:
        st.info("No records match the current filters.")

    st.subheader("📋 Audit Logs Table")
    st.write(f"Showing {len(df_filtered)} records (period: {start_date} → {end_date})")

    cols_to_show = ["timestamp", "patient_id", "provider_npi", "icd10_code", "treatment_name",
                    "rule_status", "proof_status", "final_decision"]
    available_cols = [c for c in cols_to_show if c in df_filtered.columns]
    df_table = df_filtered.copy()
    if "timestamp" in df_table.columns:
        df_table["timestamp"] = df_table["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(df_table[available_cols], use_container_width=True)

    csv_data = df_filtered.to_csv(index=False)
    st.download_button(
        label="⬇ Full Audit Logs",
        data=csv_data,
        file_name="audit_logs.csv",
        mime="text/csv"
    )

    excel_buffer = BytesIO()
    try:
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            summary_df = pd.DataFrame({
                "Metric": ["Total Logs", "Approved", "Denied", "Pending"],
                "Value": [total_logs, approved_count, denied_count, pending_count],
                "Delta": [total_delta, approved_delta, denied_delta, pending_delta]
            })
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            df_filtered.to_excel(writer, sheet_name="Audit Logs", index=False)

        st.download_button(
            label="⬇ Log Summary",
            data=excel_buffer.getvalue(),
            file_name="audit_logs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.warning("Excel export not available: install openpyxl (pip install openpyxl) to enable Excel download.")
