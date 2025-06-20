import streamlit as st
import random
import pandas as pd
from datetime import datetime

# --- Helper data ---
PLATFORMS = ["Gmail", "Outlook", "Yahoo"]
LOCATIONS = ["New York", "Los Angeles", "Chicago", "Dallas", "Miami"]

NEUTRAL_TOPICS = [
    "travel", "sports", "technology", "food", "movies", "books",
    "music", "nature", "science", "local news"
]
ACTIONS = [
    "liked a post about", "commented on", "shared an article about", "joined a discussion on"
]

# --- Session State for accounts and logs ---
if 'accounts' not in st.session_state:
    st.session_state['accounts'] = []
if 'activity_log' not in st.session_state:
    st.session_state['activity_log'] = []

def generate_random_account():
    username = f"user{random.randint(1000,9999)}"
    platform = random.choice(PLATFORMS)
    location = random.choice(LOCATIONS)
    health = random.randint(60, 100)  # Simulated health score
    return {
        "username": username,
        "platform": platform,
        "location": location,
        "health": health
    }

def generate_neutral_activity(account):
    topic = random.choice(NEUTRAL_TOPICS)
    action = random.choice(ACTIONS)
    desc = f"{account['username']} {action} {topic} in {account['location']}"
    return desc

def log_activity(account, activity):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "username": account['username'],
        "platform": account['platform'],
        "location": account['location'],
        "activity": activity
    }
    st.session_state['activity_log'].append(log_entry)

# --- UI ---

st.title("All Trial Automation")

st.header("Create Account")
if st.button("Create Random Account"):
    account = generate_random_account()
    st.session_state['accounts'].append(account)
    st.success(f"Created: {account['username']} on {account['platform']} ({account['location']})")

st.header("Account List")
if st.session_state['accounts']:
    accounts_df = pd.DataFrame(st.session_state['accounts'])
    st.table(accounts_df)
else:
    st.info("No accounts yet. Click above to create one!")

st.header("Simulate Activity")
if st.session_state['accounts']:
    account_names = [a['username'] for a in st.session_state['accounts']]
    selected_user = st.selectbox("Choose account for activity", account_names)
    if st.button("Simulate Neutral Activity"):
        account = next(a for a in st.session_state['accounts'] if a['username'] == selected_user)
        activity = generate_neutral_activity(account)
        log_activity(account, activity)
        st.success(f"Activity: {activity}")

st.header("Activity Log")
if st.session_state['activity_log']:
    log_df = pd.DataFrame(st.session_state['activity_log'])
    st.dataframe(log_df)
    csv = log_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Activity Log CSV", data=csv, file_name="activity_log.csv", mime="text/csv")
else:
    st.info("No activities yet.")
