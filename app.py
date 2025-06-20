import streamlit as st
from datetime import datetime

# Dummy session state for demo
if "flagged_reviews" not in st.session_state:
    st.session_state["flagged_reviews"] = [
        {"timestamp": datetime.now().isoformat(), "review": "Guaranteed win with this firm!", "risks": ["guarantee", "Suspicious phrase"]},
        {"timestamp": datetime.now().isoformat(), "review": "Great team, but they promised a refund.", "risks": ["refund", "Suspicious phrase"]},
    ]
if "activity_log" not in st.session_state:
    st.session_state["activity_log"] = [
        {"timestamp": datetime.now().isoformat(), "activity": "Created account in Anaheim"},
        {"timestamp": datetime.now().isoformat(), "activity": "Posted neutral comment in Los Angeles"},
    ]
if "accounts" not in st.session_state:
    st.session_state["accounts"] = [
        {"username": "jane.doe", "location": "Anaheim", "status": "warming"},
        {"username": "john.smith", "location": "LA", "status": "ready"},
    ]

def highlight_review(review, risks):
    if risks:
        color = "#ffcccc"  # light red
        border = "2px solid red"
    else:
        color = "#ccffcc"  # light green
        border = "2px solid green"
    return f"<div style='background-color:{color};border:{border};padding:6px;border-radius:6px;margin-bottom:6px'>{review}<br><b>Risks:</b> {', '.join(risks) if risks else 'None'}</div>"

# --- Dashboard Tabs ---
tab1, tab2, tab3 = st.tabs(["Main Dashboard", "Flagged/Risky", "Daily Summary"])

with tab1:
    st.header("📊 Main Dashboard")
    st.write("Account Overview")
    st.table(st.session_state["accounts"])
    st.write("Recent Activity")
    for log in st.session_state["activity_log"]:
        st.write(f"- {log['timestamp']}: {log['activity']}")

with tab2:
    st.header("🚩 Flagged/Risky Reviews & Activities")
    st.write("All reviews/activities flagged for risk. Color-coded by severity.")
    for entry in st.session_state["flagged_reviews"]:
        st.markdown(highlight_review(entry["review"], entry["risks"]), unsafe_allow_html=True)
    st.button("Export Flagged Reviews")

with tab3:
    st.header("📅 Daily Summary")
    today = datetime.now().date()
    total_reviews = len(st.session_state.get("activity_log", []))
    total_flagged = len(st.session_state.get("flagged_reviews", []))
    st.write(f"**Total activities today:** {total_reviews}")
    st.write(f"**Flagged/risky today:** {total_flagged}")
    if total_flagged:
        st.warning("Action required: Review flagged items in the Flagged/Risky tab.")

# --- Suggestions for Non-Coders ---
st.sidebar.header("⭐️ Suggestions & Upgrades")
st.sidebar.markdown("""
- Add bulk actions in the flagged tab (approve, edit, export).
- Show live safety scoring and explanations in all tabs.
- Make tabs collapsible for mobile users.
- Export flagged and safe reviews to CSV for backup.
- Add search/filter to flagged tab for faster triage.
""")
