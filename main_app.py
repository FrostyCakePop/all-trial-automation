import streamlit as st
import subprocess
import sys

# Page configuration
st.set_page_config(
    page_title="Email Warming System",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PWA support
st.markdown("""
<link rel="manifest" href="manifest.json">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#2196F3">
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js');
}
</script>
""", unsafe_allow_html=True)

# Navigation sidebar
st.sidebar.title("📧 Email Warming System")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["Dashboard", "Account Generator", "Review Manager"]
)

# Page routing
if page == "Dashboard":
    # Import and run account_warmer content
    exec(open("account_warmer.py").read())
elif page == "Account Generator":
    # Import and run account_creator content
    exec(open("account_creator.py").read())
else:
    st.title("🌟 Review Manager")
    st.info("Review management features coming soon!")
    st.markdown("### Planned Features:")
    st.write("- Automated review generation")
    st.write("- Lawyer database management") 
    st.write("- Safety score monitoring for posting")
