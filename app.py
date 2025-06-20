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

# ----- Locations for assignment -----
LOCATIONS = [
    "Orange County", "Riverside", "La Jolla", "Los Angeles", "Diamond Bar", "San Bernardino"
]

# ----- Streamlit UI -----
st.title("Autonomous Reputation Engine — Account & Activity Manager")

# ---- Account Creation ----
st.header("Create a New Account")
new_location = st.selectbox("Assign Location", LOCATIONS)
if st.button("Create Account"):
    username = f"user{random.randint(1000,9999)}"
    account = {
        "username": username,
        "email": f"{username}@gmail.com",
        "location": new_location,
        "created": datetime.now().isoformat(),
        "status": "new",
        "warmed": False,
        "next_activity": (datetime.now() + timedelta(hours=random.randint(1,3))).isoformat()
    }
    st.session_state['accounts'].append(account)
    save_json(ACCOUNTS_FILE, st.session_state['accounts'])
    st.success(f"Account {username} created and assigned to {new_location}.")

# ---- View All Accounts ----
st.header("All Accounts")
accounts_df = pd.DataFrame(st.session_state['accounts'])
st.dataframe(accounts_df)

# ---- Activity Logging ----
def log_activity(username, location, activity_type, details):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "username": username,
        "location": location,
        "activity_type": activity_type,
        "details": details
    }
    st.session_state['activity_log'].append(entry)
    save_json(ACTIVITY_FILE, st.session_state['activity_log'])

# ---- Human-like Activity Engine: Scaffolding ----
def generate_typo_text(text):
    # Simple typo/noise generator
    chars = list(text)
    for i in range(len(chars)):
        if random.random() < 0.04:
            chars[i] = random.choice("abcdefghijklmnopqrstuvwxyz")
        if random.random() < 0.02 and i > 0:
            chars[i-1], chars[i] = chars[i], chars[i-1]
    return "".join(chars)

def random_neutral_activity(location):
    templates = [
        f"Googled 'best places to eat in {location}'",
        f"Watched a YouTube video about {location} tourism",
        f"Browsed top-rated restaurants in {location}",
        f"Read reviews for local coffee shops in {location}",
        f"Checked weather in {location} on my phone"
    ]
    act = random.choice(templates)
    return generate_typo_text(act)

def random_review_activity(location):
    samples = [
        f"Had a nice meal at a cafe in {location}. Staff was friendly.",
        f"Stopped by a gas station in {location}; clean and quick.",
        f"Visited a local shop in {location}, good experience.",
        f"Loved the vibe at a bar in {location}. Will return.",
        f"Had coffee at a small spot in {location}."
    ]
    review = random.choice(samples)
    return generate_typo_text(review)

# ---- Simulated Autonomous Scheduler ----
st.header("👀 Live Activity Engine (Demo Mode)")
now = datetime.now()
for account in st.session_state['accounts']:
    next_time = datetime.fromisoformat(account['next_activity'])
    if now >= next_time and not account['warmed']:
        # Simulate a neutral activity
        activity = random_neutral_activity(account['location'])
        log_activity(account['username'], account['location'], "neutral_activity", activity)

        # 1 in 4 chance to post a "review" after warming
        if random.random() < 0.25:
            review = random_review_activity(account['location'])
            log_activity(account['username'], account['location'], "warming_review", review)
            account['warmed'] = True
            account['status'] = "warmed"
        # Schedule next activity
        account['next_activity'] = (now + timedelta(hours=random.uniform(1, 3))).isoformat()
        save_json(ACCOUNTS_FILE, st.session_state['accounts'])

# ---- Activity Log ----
st.header("Activity Log")
log_df = pd.DataFrame(st.session_state['activity_log'])
st.dataframe(log_df)
st.download_button("Download Activity Log CSV", log_df.to_csv(index=False), "activity_log.csv", "text/csv")

st.caption("All accounts and activities are permanently saved. You can edit, upgrade, and change the app without any data loss. Ready for full automation upgrades!")
