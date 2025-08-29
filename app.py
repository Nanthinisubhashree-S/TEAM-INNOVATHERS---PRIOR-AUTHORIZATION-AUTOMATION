import streamlit as st
import integrate5
import auditnew1
import base64

st.set_page_config(page_title="PA & Audit Dashboard", layout="wide")

def add_bg_from_local(image_file):
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
            background-color: rgba(255,255,255,0.7);
        }}
        /* 🔹 Force ALL sidebar text to black */
        [data-testid="stSidebar"] * {{
            color: black !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local("medical-equipment-with-copy-space.jpg")

st.sidebar.image("logo1.jpg", use_container_width=True)  # optional logo
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["Main Dashboard", "Prior Authorization", "Audit Logs"]
)

if page == "Home":
    st.title("🏠 PRIOR AUTHORIZATION AUTOMATION")
    st.write("Welcome! Use the navigation bar to access features.")

elif page == "Prior Authorization":
    st.title("⚖ Prior Authorization")
    integrate5.render_pa_page()

elif page == "Audit Logs":
    auditnew1.render_audit_page()
