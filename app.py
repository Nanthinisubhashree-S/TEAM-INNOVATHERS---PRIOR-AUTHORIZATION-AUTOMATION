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
        
        div.stButton > button {{
            width: 180px !important;
            background-color: rgba(0, 123, 255, 0.15) !important;
            border: 1px solid rgba(0, 123, 255, 0.4) !important;
            color: black !important;
            text-align: center !important;
            padding: 0.6rem 1rem !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            border-radius: 10px !important;
            margin: 0.3rem auto 0.5rem auto !important;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.1) !important;
            transition: all 0.2s ease-in-out;
            display: block !important;
        }}
        div.stButton > button:hover {{
            background-color: rgba(0, 123, 255, 0.3) !important;
            transform: translateY(-2px);
            cursor: pointer !important;
        }}
        div.stButton > button:focus {{
            outline: none !important;
            box-shadow: 0px 0px 6px rgba(0, 123, 255, 0.6) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

st.sidebar.image("logo.jpg", use_container_width=True)
st.sidebar.title("🔍 Explorer")

pages = {
    "Home": "home",
    "Prior Authorization": "pa",
    "Audit Logs": "audit"
}

for name, key in pages.items():
    if st.sidebar.button(name, key=key):
        st.session_state.page = key

if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    set_bg("medhome.jpg")
    st.title("🏤 PRIOR AUTHORIZATION AUTOMATION")
    st.header("Welcome to *MEDGATE*!")
    st.write("*The Smart Gateway to Faster Care Decisions*")

elif st.session_state.page == "pa":
    set_bg("medhome1.jpg")
    st.title("Prior Authorization")
    integrate5.render_pa_page()

elif st.session_state.page == "audit":
    set_bg("medhome1.jpg")
    auditnew1.render_audit_page()
