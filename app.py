#app.py
import streamlit as st
import integrate5
import auditnew1

# ---------------- Set page config once ----------------
st.set_page_config(page_title="PA & Audit Dashboard", layout="wide")

# ---------------- Session state for current page ----------------
if "page" not in st.session_state:
    st.session_state.page = "Main Dashboard"

# ---------------- Main Dashboard ----------------
if st.session_state.page == "Main Dashboard":
    st.title("🏠 PRIOR AUTHORIZATION AND AUTOMATION")
    st.write("Welcome! Choose an action:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚖ Prior Authorization"):
            st.session_state.page = "Prior Authorization"
            st.rerun()

    with col2:
        if st.button("📄 Audit Logs"):
            st.session_state.page = "Audit Logs"
            st.rerun()

# ---------------- Prior Authorization Page ----------------
elif st.session_state.page == "Prior Authorization":
    if st.button("⬅ Back to Main Dashboard"):
        st.session_state.page = "Main Dashboard"
        st.rerun()
    integrate5.render_pa_page()

# ---------------- Audit Logs Page ----------------
elif st.session_state.page == "Audit Logs":
    if st.button("⬅ Back to Main Dashboard"):
        st.session_state.page = "Main Dashboard"
        st.rerun()
    auditnew1.render_audit_page()