#app.py
import streamlit as st
import integrate5
import auditnew1
import base64

st.set_page_config(page_title="MEDGATE", layout="wide")

def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}
        [data-testid="stSidebar"] {{
            background-color: rgba(255,255,255,0.3);
        }}
        [data-testid="stSidebar"] * {{
            color: black !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

st.sidebar.image("logo.jpg", use_container_width=True)  # optional logo
st.sidebar.title("🔍 Explorer")
page = st.sidebar.radio(
    "Menu",
    ["Home", "Prior Authorization", "Audit Logs"],
    label_visibility="collapsed"
)

if page == "Home":
    set_bg("medhome.jpg")   # Home background
    st.title("🏤 PRIOR AUTHORIZATION AUTOMATION")
    st.header("Welcome to *MEDGATE*!")
    st.write("*The Smart Gateway to Faster Care Decisions*")

elif page == "Prior Authorization":
    set_bg("medhome1.jpg")
    st.title("Prior Authorization")
    integrate5.render_pa_page()

elif page == "Audit Logs":
    set_bg("medhome1.jpg")
    auditnew1.render_audit_page()
