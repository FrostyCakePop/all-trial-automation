import streamlit as st
from utils_github import load_csv

st.set_page_config(page_title="Email Warming System", page_icon="📧", layout="wide")

st.sidebar.title("📧 Email Warming System")
page = st.sidebar.selectbox(
    "Select page",
    ["Dashboard","Account Generator","Activity Viewer"]
)

if page == "Dashboard":
    exec(open("account_warmer.py").read())
elif page == "Account Generator":
    exec(open("account_creator.py").read())
else:  # Activity Viewer
    st.title("🔍 Activity Viewer")
    log_df = load_csv("activity_log.csv", ["timestamp","email","action","details"])
    if log_df.empty:
        st.info("No activity logged yet.")
    else:
        email_filter  = st.selectbox("Email", ["All"]+sorted(log_df.email.unique()))
        action_filter = st.selectbox("Action", ["All"]+sorted(log_df.action.unique()))
        view = log_df
        if email_filter!="All":
            view = view[view.email==email_filter]
        if action_filter!="All":
            view = view[view.action==action_filter]
        st.dataframe(view.sort_values("timestamp",ascending=False), use_container_width=True)
