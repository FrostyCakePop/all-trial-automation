import streamlit as st
import pandas as pd
import random
import json
import os
from datetime import datetime, timedelta

# ----- File paths -----
ACCOUNTS_FILE = "accounts.json"
ACTIVITY_FILE = "activity_log.json"

# ----- Helper functions for file storage -----
def load_json(filename, fallback=[]):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return fallback

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# ----- Load data on startup -----
if 'accounts' not in st.session_state:
    st.session_state['accounts'] = load_json(ACCOUNTS_FILE)
if 'activity_log' not in st.session_state:
    st.session_state['activity_log'] = load_json(ACTIVITY_FILE)

# ----- Locations and Platforms -----
LOCATIONS = [
    "Orange County", "Riverside", "La Jolla", "Los Angeles", "Diamond Bar", "San Bernardino"
]
PLATFORMS = ["Google", "Yelp", "Avvo", "Justia"]

# ----- Neutral Activity Templates -----
NEUTRAL_TOPICS = [
    "travel", "sports", "technology", "food", "music", "nature", "science", "local news", "events", "weather", "parks"
]
NEUTRAL_ACTIONS = [
    "Googled about", "Watched a YouTube video on", "Read an article about", "Checked reviews for",
    "Browsed Instagram posts about", "Looked at photos of", "Searched Twitter for"
]
BUSINESS_TYPES = [
    "coffee shop", "restaurant", "gas station", "bookstore", "park", "hotel", "museum", "bar", "gym"
]

# ----- Streamlit UI -----
st.title("All Trial Automation — Autonomous Account Warming Engine")

# ---- Account Creation ----
st.header("Create a New Account")
col1, col2 = st.columns(2)
with col1:
    new_location = st.selectbox("Assign Location", LOCATIONS)
with col2:
    new_platform = st.selectbox("Assign Platform", PLATFORMS)
if st.button("Create Account"):
    username = f"user{random.randint(1000,9999)}"
    account = {
        "username": username,
        "email": f"{username}@gmail.com",
        "location": new_location,
        "platform": new_platform,
        "created": datetime.now().isoformat(),
        "status": "new",
        "warmed": False,
        "neutral_activities": 0,
        "next_activity": (datetime.now() + timedelta(minutes=random.randint(2,10))).isoformat()
    }
    st.session_state['accounts'].append(account)
    save_json(ACCOUNTS_FILE, st.session_state['accounts'])
    st.success(f"Account {username} created and assigned to {new_location} on {new_platform}.")

# ---- View All Accounts ----
st.header("All Accounts and Status")
accounts_df = pd.DataFrame(st.session_state['accounts'])
if not accounts_df.empty:
    accounts_df["next_activity"] = pd.to_datetime(accounts_df["next_activity"]).dt.strftime("%Y-%m-%d %H:%M")
st.dataframe(accounts_df)

# ---- Activity Logging ----
def log_activity(username, location, platform, activity_type, details):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "username": username,
        "location": location,
        "platform": platform,
        "activity_type": activity_type,
        "details": details
    }
    st.session_state['activity_log'].append(entry)
    save_json(ACTIVITY_FILE, st.session_state['activity_log'])

# ---- Human-like Typo Generator ----
def generate_typo_text(text):
    chars = list(text)
    for i in range(len(chars)):
        if random.random() < 0.05:
            chars[i] = random.choice("abcdefghijklmnopqrstuvwxyz")
        if random.random() < 0.02 and i > 0:
            chars[i-1], chars[i] = chars[i], chars[i-1]
    # Randomly drop a word
    words = ''.join(chars).split()
    if len(words) > 4 and random.random() < 0.10:
        del words[random.randint(0, len(words)-1)]
    return ' '.join(words)

# ---- Generate Neutral Activity ----
def random_neutral_activity(location):
    topic = random.choice(NEUTRAL_TOPICS)
    action = random.choice(NEUTRAL_ACTIONS)
    biz = random.choice(BUSINESS_TYPES)
    city = location
    template = f"{action} {topic} in {city}"
    if random.random() < 0.5:
        template += f" and looked at a {biz} nearby"
    return generate_typo_text(template)

# ---- Simulated Autonomous Scheduler ----
st.header("👀 Live Automated Warming Engine")
now = datetime.now()
WARMING_TARGET = 3  # Number of neutral activities before "warmed"

for account in st.session_state['accounts']:
    next_time = datetime.fromisoformat(account['next_activity'])
    if now >= next_time and not account['warmed']:
        activity = random_neutral_activity(account['location'])
        log_activity(account['username'], account['location'], account['platform'], "neutral_activity", activity)
        account['neutral_activities'] += 1

        # If account is now 'warmed', log that event
        if account['neutral_activities'] >= WARMING_TARGET:
            account['warmed'] = True
            account['status'] = "warmed"
            log_activity(account['username'], account['location'], account['platform'], "status_update", "Account warming complete! Ready for review posting.")
        # Schedule next activity in 2–10 minutes (demo mode, increase to hours for real use)
        account['next_activity'] = (now + timedelta(minutes=random.randint(2,10))).isoformat()
        save_json(ACCOUNTS_FILE, st.session_state['accounts'])

# ---- Activity Log ----
st.header("Activity Log (All Activity)")
log_df = pd.DataFrame(st.session_state['activity_log'])
if not log_df.empty:
    log_df["timestamp"] = pd.to_datetime(log_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
st.dataframe(log_df)
st.download_button("Download Activity Log CSV", log_df.to_csv(index=False), "activity_log.csv", "text/csv")

st.caption("💾 All accounts and activities are permanently saved. You can freely upgrade or edit the app without losing anything. This engine auto-warms accounts with human-like, location-based actions!")
