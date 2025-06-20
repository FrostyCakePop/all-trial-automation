import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# --- Helper: Calculate Health Score ---
def calc_health_score(user_log, days=14):
    # Score: % of last N days with at least 1 activity
    if not user_log:
        return 0
    today = datetime.now().date()
    date_set = set([pd.to_datetime(a['timestamp']).date() for a in user_log])
    last_n = [today - timedelta(days=i) for i in range(days)]
    active_days = sum([d in date_set for d in last_n])
    return int((active_days / days) * 100)

# --- Helper: Draw Calendar Heatmap ---
def plot_calendar_heatmap(user_log, days=30):
    if not user_log:
        st.info("No activity yet for this account.")
        return
    today = datetime.now().date()
    date_set = [pd.to_datetime(a['timestamp']).date() for a in user_log]
    last_n = [today - timedelta(days=i) for i in range(days)]
    values = [date_set.count(d) for d in last_n]
    dates = [d.strftime("%b %d") for d in reversed(last_n)]

    fig, ax = plt.subplots(figsize=(10,1.2))
    cmap = sns.light_palette("seagreen", as_cmap=True)
    data = np.array([values])
    sns.heatmap(data, ax=ax, cmap=cmap, cbar=False, linewidths=1, linecolor='grey', annot=False, xticklabels=dates, yticklabels=[])
    ax.set_xticklabels(dates, rotation=90, fontsize=8)
    ax.set_yticklabels([])
    plt.tight_layout()
    st.pyplot(fig)

# --- Usage example (Put inside your per-account section) ---
# Assume selected_user is the username and user_log is its log
accounts = st.session_state.get('accounts', [])
activity_log = st.session_state.get('activity_log', [])

if accounts:
    usernames = [a['username'] for a in accounts]
    selected_user = st.selectbox("Select account to view activity log", usernames)
    user_log = [a for a in activity_log if a['username'] == selected_user]

    if user_log:
        # Activity Health Score
        score = calc_health_score(user_log)
        badge_color = "green" if score > 80 else "orange" if score > 50 else "red"
        st.markdown(f"<div style='display:inline-block;background:{badge_color};color:white;padding:6px 12px;border-radius:6px;font-weight:bold;'>Activity Health Score: {score}%</div>", unsafe_allow_html=True)

        # Calendar Heatmap
        st.subheader("Activity Calendar (Past 30 Days)")
        plot_calendar_heatmap(user_log, days=30)

        # ... (rest of your activity log code here) ...
