import streamlit as st
import integrate5
import auditnew1
import base64

# ---------------- Set page config ----------------
st.set_page_config(page_title="PA & Audit Dashboard", layout="wide")

# ---------------- Function to add local background image ----------------
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

# Apply background
add_bg_from_local("medical-equipment-with-copy-space.jpg")

# ---------------- Sidebar Logo & Navigation ----------------
st.sidebar.image("logo1.jpg", use_container_width=True)  # optional logo
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["Main Dashboard", "Prior Authorization", "Audit Logs"]
)

# ---------------- Main Dashboard ----------------
if page == "Main Dashboard":
    st.title("🏠 PRIOR AUTHORIZATION AND AUTOMATION")
    st.write("Welcome! Use the navigation bar to access features.")

# ---------------- Prior Authorization Page ----------------
elif page == "Prior Authorization":
    st.title("⚖ Prior Authorization")
    integrate5.render_pa_page()

# ---------------- Audit Logs Page ----------------
elif page == "Audit Logs":
    st.title("📄 Audit Logs")
    auditnew1.render_audit_page()