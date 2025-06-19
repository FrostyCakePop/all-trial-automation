import streamlit as st
from utils_github import load_csv

st.set_page_config("Email System","📧",layout="wide")

page = st.sidebar.selectbox("Page",
    ["Dashboard","Account Generator","Activity Viewer"])

if page=="Dashboard":
    exec(open("account_warmer.py").read())
elif page=="Account Generator":
    exec(open("account_creator.py").read())
else:
    st.title("🔍 Activity Viewer")
    df = load_csv("activity_log.csv",
                  ["timestamp","email","action","details"])
    if df.empty:
        st.info("No activity yet.")
    else:
        email = st.selectbox("Email",["All"]+sorted(df.email.unique()))
        act   = st.selectbox("Action",["All"]+sorted(df.action.unique()))
        view = df
        if email!="All": view = view[view.email==email]
        if act!="All":   view = view[view.action==act]
        st.dataframe(view.sort_values("timestamp",ascending=False),
                     use_container_width=True)
