import streamlit as st
import json
import os
import random
import pandas as pd
from datetime import datetime, timedelta
import threading
import time

TEMPLATE_FILE = "activity_templates.json"
ACCOUNTS_FILE = "accounts.json"

# ========== ERROR HANDLING HELPERS ==========

def safe_load_json(filename, default):
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return json.load(f)
    except Exception as e:
        st.warning(f"Failed to load {filename}: {e}")
    return default

def safe_save_json(filename, data):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.warning(f"Failed to save {filename}: {e}")

# ========== TEMPLATE MANAGEMENT ==========

def load_templates():
    return safe_load_json(TEMPLATE_FILE, [
        "Commented on a {topic} post in {location}",
        "Liked a {topic} article in {location}",
        "Shared a news update about {topic} in {location}",
        "Followed a user interested in {topic} in {location}",
        "Replied to a general discussion on {topic} in {location}"
    ])

def save_templates(templates):
    safe_save_json(TEMPLATE_FILE, templates)

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

def generate_neutral_activity(location, topic="general"):
    templates = load_templates()
    if not templates:
        return "No templates available."
    template = random.choice(templates)
    return template.format(topic=topic, location=location)

# ========== ACCOUNT MANAGEMENT ==========

def load_accounts():
    return safe_load_json(ACCOUNTS_FILE, [])

def save_accounts(accounts):
    safe_save_json(ACCOUNTS_FILE, accounts)

# ========== HEALTH SCORING ==========

def calc_health_score(user_log, days=14):
    if not user_log:
        return 0
    today = datetime.utcnow().date()
    date_set = set(pd.to_datetime(a['timestamp']).date() for a in user_log)
    last_n = [today - timedelta(days=i) for i in range(days)]
    active_days = sum([d in date_set for d in last_n])
    return int((active_days / days) * 100)

# ========== AUTOMATION (Background Warming) ==========

def run_automation():
    if st.session_state.get('automating', False):
        accounts = st.session_state['accounts']
        topics = ["sports", "travel", "technology", "music", "food"]
        for idx, acc in enumerate(accounts):
            if acc.get("paused", False):
                continue
            try:
                topic = random.choice(topics)
                activity = generate_neutral_activity(acc["location"], topic)
                log_entry = {
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    "username": acc["username"],
                    "location": acc["location"],
                    "activity": activity,
                    "topic": topic
                }
                st.session_state['activity_log'].append(log_entry)
                # Optional: update last activity time for health scoring
                acc['last_activity'] = log_entry["timestamp"]
            except Exception as e:
                st.warning(f"Automation failed for {acc.get('username', 'unknown')}: {e}")
        save_accounts(accounts)
        time.sleep(st.session_state.get('automation_interval', 90))  # default: every 90 seconds

def automation_loop():
    while st.session_state.get('automating', False):
        run_automation()

# ========== SESSION STATE INIT ==========

if 'accounts' not in st.session_state:
    st.session_state['accounts'] = load_accounts()
if 'activity_log' not in st.session_state:
    st.session_state['activity_log'] = []
if 'automating' not in st.session_state:
    st.session_state['automating'] = False
if 'automation_thread' not in st.session_state:
    st.session_state['automation_thread'] = None
if 'automation_interval' not in st.session_state:
    st.session_state['automation_interval'] = 90  # seconds

accounts = st.session_state['accounts']

# ========== MAIN UI ==========

st.title("Account Warming & Activity Automation Dashboard")

# --- ACTIVITY TEMPLATE MANAGEMENT ---
with st.expander("📝 Manage Activity Templates", expanded=False):
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

# --- ACCOUNT MANAGEMENT UI ---
st.header("👤 Accounts")

add_user, edit_user, del_user = st.columns(3)
with add_user:
    st.subheader("Add Account")
    with st.form("AddAccount"):
        new_username = st.text_input("Username", key="add_username")
        new_location = st.text_input("Location", key="add_location")
        submitted = st.form_submit_button("Add")
        if submitted:
            if not new_username or not new_location:
                st.error("Username and location are required.")
            elif any(acc["username"] == new_username for acc in accounts):
                st.error("Username already exists.")
            else:
                accounts.append({"username": new_username, "location": new_location, "paused": False})
                save_accounts(accounts)
                st.success(f"Account {new_username} added.")
                st.experimental_rerun()
with edit_user:
    st.subheader("Edit Account")
    usernames = [acc["username"] for acc in accounts]
    if usernames:
        selected_edit = st.selectbox("Select account", usernames, key="edit_select")
        acc = next((a for a in accounts if a["username"] == selected_edit), None)
        if acc:
            new_loc = st.text_input("New Location", value=acc["location"], key="edit_location")
            paused = st.checkbox("Paused", value=acc.get("paused", False), key="edit_paused")
            if st.button("Update Account"):
                acc["location"] = new_loc
                acc["paused"] = paused
                save_accounts(accounts)
                st.success("Account updated.")
                st.experimental_rerun()
with del_user:
    st.subheader("Delete Account")
    if usernames:
        selected_del = st.selectbox("Delete which account?", usernames, key="del_select")
        if st.button("Delete Account"):
            accounts[:] = [a for a in accounts if a["username"] != selected_del]
            save_accounts(accounts)
            st.success(f"Account {selected_del} deleted.")
            st.experimental_rerun()

# --- ACCOUNT TABLE + HEALTH ---
st.markdown("### All Accounts and Health")
if accounts:
    log_df = pd.DataFrame(st.session_state['activity_log'])
    show = []
    for acc in accounts:
        user_log = log_df[log_df["username"] == acc["username"]].to_dict("records") if not log_df.empty else []
        health = calc_health_score(user_log)
        badge_color = "#4CAF50" if health > 80 else "#FFC107" if health > 50 else "#f44336"
        show.append({
            "Username": acc["username"],
            "Location": acc["location"],
            "Paused": acc.get("paused", False),
            "Health Score": f"{health}%",
            "Health Color": badge_color
        })
    health_df = pd.DataFrame(show)
    # Style health color
    def color_health(val, color):
        return f"background-color: {color}" if isinstance(val, str) and "%" in val else ""
    st.dataframe(
        health_df[["Username", "Location", "Paused", "Health Score"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No accounts yet.")

# --- AUTOMATION CONTROLS ---
st.header("🤖 True Automation")

st.write(f"Automation interval: {st.session_state['automation_interval']} seconds")
auto_cols = st.columns([1,1,2])
with auto_cols[0]:
    if st.button("Start Automation"):
        if not st.session_state['automating']:
            st.session_state['automating'] = True
            if not st.session_state['automation_thread'] or not st.session_state['automation_thread'].is_alive():
                t = threading.Thread(target=automation_loop, daemon=True)
                st.session_state['automation_thread'] = t
                t.start()
            st.success("Automation started. Accounts will warm in the background.")
with auto_cols[1]:
    if st.button("Stop Automation"):
        st.session_state['automating'] = False
        st.success("Automation stopped.")
with auto_cols[2]:
    interval = st.number_input(
        "Set automation interval (seconds):",
        min_value=20, max_value=600, value=st.session_state['automation_interval'], step=10
    )
    if interval != st.session_state['automation_interval']:
        st.session_state['automation_interval'] = int(interval)
        st.success("Automation interval updated.")

# --- MANUAL ACTIVITY (OPTIONAL) ---
st.header("🔥 Simulate Activity Now")
selected_accounts = st.multiselect(
    "Select accounts to warm (or leave empty for all):",
    [acc["username"] for acc in accounts]
)
topics = ["sports", "travel", "technology", "music", "food"]
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
        acc["last_activity"] = log_entry["timestamp"]
        save_accounts(accounts)
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
- **Health scoring**: Green = healthy, Yellow = moderate, Red = low. Try to keep all accounts green!
- **Background automation**: App will auto-warm accounts on a timer. Adjust the interval as needed.
- **Full UI management**: Add, edit, delete accounts without any code.
- **Error handling**: The app will not crash if a file is missing or data is bad—just a friendly warning.
- **Activity templates**: Expand your neutral actions for even more realism.
- **Upgrade ideas**: Add calendar heatmaps, per-account review, or GitHub/Sheets data storage for backups. Want these? Just ask!
""")
