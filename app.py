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
            background-color: rgba(255,255,255,0.3);
        }}
        /* 🔹 Force ALL sidebar text to black */
        [data-testid="stSidebar"] * {{
            color: black !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local("medhome.jpg")

st.sidebar.image("logo.jpg", use_container_width=True)  # optional logo
st.sidebar.title("🔍 Explorer")
page = st.sidebar.radio(
    "Menu",
    ["Home", "Prior Authorization", "Audit Logs"],
    label_visibility="collapsed"
)

if page == "Home":
    st.title("PRIOR AUTHORIZATION AUTOMATION")
    st.header("Welcome to *MEDGATE*!")
    st.write("The Smart Gateway to Faster Care Decisions")

elif page == "Prior Authorization":
    st.title("Prior Authorization")
    integrate5.render_pa_page()

elif page == "Audit Logs":
    auditnew1.render_audit_page()
