#auditnew1.py
import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "prior_auth.db"

def render_audit_page():
    # Function to fetch audit logs
    def get_audit_logs():
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY timestamp DESC", conn)
        return df

    st.title("📄 Audit Log Viewer")

    # Fetch audit data
    df = get_audit_logs()

    if df.empty:
        st.warning("No audit logs found!")
        return

    # Filters
    st.sidebar.header("Filters")
    patient_filter = st.sidebar.text_input("Filter by Patient ID")
    provider_filter = st.sidebar.text_input("Filter by Provider NPI")
    final_decision_filter = st.sidebar.selectbox(
        "Filter by Final Decision", 
        ["All"] + df['final_decision'].dropna().unique().tolist()
    )

    # Apply filters
    if patient_filter:
        df = df[df['patient_id'].str.contains(patient_filter, case=False, na=False)]
    if provider_filter:
        df = df[df['provider_npi'].str.contains(provider_filter, case=False, na=False)]
    if final_decision_filter != "All":
        df = df[df['final_decision'] == final_decision_filter]

    st.write(f"Total Records: {len(df)}")
    st.dataframe(df)

    # Option to download CSV
    st.download_button(
        label="Download Audit Logs as CSV",
        data=df.to_csv(index=False),
        file_name="audit_logs.csv",
        mime="text/csv"
    )