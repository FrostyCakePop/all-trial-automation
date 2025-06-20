import streamlit as st
import json
import os
import random
import pandas as pd
from datetime import datetime

# FILES
TEMPLATE_FILE = "activity_templates.json"

# 1. TEMPLATE MANAGEMENT
def load_templates():
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r") as f:
            return json.load(f)
    else:
        # Default templates
        return [
            "Commented on a {topic} post in {location}",
            "Liked a {topic} article in {location}",
            "Shared a news update about {topic} in {location}",
            "Followed a user interested in {topic} in {location}",
            "Replied to a general discussion on {topic} in {location}"
        ]

def save_templates(templates):
    with open(TEMPLATE_FILE, "w") as f:
        json.dump(templates, f, indent=2)

def reset_templates():
    defaults = [
        "Commented on a {topic} post in {location}",
        "Liked a {topic} article in {location}",
        "Shared a news update about {topic} in {location}",
        "Followed a user interested in {topic} in {location}",
        "Replied to a general discussion on {topic} in {location}"
    ]
    save_templates(defaults)
    return defaults

# 2. ACTIVITY GENERATION
def generate_neutral_activity(location, topic="general"):
    templates = load_templates()
    if not templates:
        return "No templates available."
    template = random.choice(templates)
    return template.format(topic=topic, location=location)

# 3. DEMO ACCOUNTS (Replace with your real account creation logic)
if 'accounts' not in st.session_state:
    st.session_state['accounts'] = [
        {"username": "user1", "location": "Dallas"},
        {"username": "user2", "location": "Chicago"},
        {"username": "user3", "location": "San Francisco"},
        {"username": "user4", "location": "London"}
    ]
if 'activity_log' not in st.session_state:
    st.session_state['activity_log'] = []

accounts = st.session_state['accounts']
topics = ["sports", "travel", "technology", "music", "food"]

# 4. STREAMLIT UI

st.title("Account Warming & Activity Simulation Dashboard")

# --- ACTIVITY TEMPLATE MANAGEMENT ---
with st.expander("📝 Manage Activity Templates", expanded=True):
    templates = load_templates()
    edited_templates = st.text_area(
        "Edit your activity templates (one per line):",
        value="\n".join(templates),
        height=150
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save Templates"):
            new_templates = [line.strip() for line in edited_templates.splitlines() if line.strip()]
            save_templates(new_templates)
            st.success("Templates saved! (Will be used for future activities.)")
    with c2:
        if st.button("Reset to Defaults"):
            defaults = reset_templates()
            st.success("Templates reset to default values.")
            st.experimental_rerun()

# --- ACCOUNT TABLE ---
st.header("👤 Accounts")
accounts_df = pd.DataFrame(accounts)
st.dataframe(accounts_df, use_container_width=True, hide_index=True)

# --- WARMING/ACTIVITY SIMULATION ---
st.header("🔥 Simulate Neutral Activities (Warming)")
selected_accounts = st.multiselect(
    "Select accounts to warm (or leave empty for all):",
    [acc["username"] for acc in accounts]
)
selected_topic = st.selectbox("Select a topic for activity:", topics + ["random"])
if st.button("Simulate Neutral Activity"):
    triggered = False
    for acc in accounts:
        if selected_accounts and acc["username"] not in selected_accounts:
            continue
        topic = selected_topic if selected_topic != "random" else random.choice(topics)
        activity = generate_neutral_activity(acc["location"], topic)
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "username": acc["username"],
            "location": acc["location"],
            "activity": activity,
            "topic": topic
        }
        st.session_state['activity_log'].append(log_entry)
        st.success(f"{acc['username']} - {activity}")
        triggered = True
    if not triggered:
        st.info("No accounts selected or available.")

# --- ACTIVITY LOG ---
st.header("🗂️ Activity Log")
if st.session_state['activity_log']:
    log_df = pd.DataFrame(st.session_state['activity_log'])
    st.dataframe(log_df, use_container_width=True, hide_index=True)
    csv = log_df.to_csv(index=False)
    st.download_button(
        "Download Activity Log (CSV)",
        csv,
        "activity_log.csv",
        "text/csv"
    )
else:
    st.info("No activities logged yet.")

# --- HELP & SUGGESTIONS ---
with st.expander("💡 Suggestions & Upgrades"):
    st.markdown("""
- **New accounts?** Replace the demo accounts in the code with your real accounts or add an account creation UI.
- **Automate warming:** Schedule activities to run periodically using Streamlit's background jobs or an external scheduler.
- **Upgrade activity templates:** Add tags, support multiple languages, or platform-specific actions.
- **Integrate with GitHub:** Save activity logs and templates to GitHub for versioning and backups.
- **Health scoring & calendar heatmap:** Add features to visualize account activity over time.
- **Error handling:** Add checks for file permissions and template validity.
""")
