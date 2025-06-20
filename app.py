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

# ----- Enhanced Neutral Activity Templates -----
NEUTRAL_TOPICS = [
    "travel", "sports", "technology", "food", "music", "nature", "science", "local news", "events", "weather", "parks", "history", "art", "shopping", "nightlife", "fitness"
]
NEUTRAL_ACTIONS = [
    "Googled about", "Watched a YouTube video on", "Read an article about", "Checked reviews for",
    "Browsed Instagram posts about", "Looked at photos of", "Searched Twitter for", "Read a Quora answer on", "Browsed Reddit for", "Scrolled TikTok about"
]
BUSINESS_TYPES = [
    "coffee shop", "restaurant", "gas station", "bookstore", "park", "hotel", "museum", "bar", "gym", "spa", "pet store", "market", "theater", "bistro"
]

LAW_FIRM_REVIEW_TEMPLATES = [
    "Had a really positive experience with All Trial Lawyers in {location}. The staff was friendly and helpful. Highly recommend!",
    "All Trial Lawyers in {location} handled my case with care and professionalism.",
    "I appreciated the quick response and support from All Trial Lawyers ({location} office).",
    "The team at All Trial Lawyers in {location} made a stressful process much easier. Thank you!",
    "Very professional and knowledgeable attorneys at All Trial Lawyers, {location}."
]

# ----- Streamlit UI -----
st.set_page_config(layout="wide", page_title="All Trial Automation")
st.title("🧑‍💻 All Trial Automation — Autonomous Account Warming Engine")

# ---- MOBILE FRIENDLY: Use compact columns ----
st.markdown("""
<style>
@media (max-width: 600px) {
    .block-container { padding: 0.5rem 0.2rem !important; }
    .css-q8sbsg { font-size: 18px !important; }
}
</style>
""", unsafe_allow_html=True)

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
        "law_firm_reviewed": False,
        "next_activity": (datetime.now() + timedelta(minutes=random.randint(5,15))).isoformat()
    }
    st.session_state['accounts'].append(account)
    save_json(ACCOUNTS_FILE, st.session_state['accounts'])
    st.success(f"Account {username} created and assigned to {new_location} on {new_platform}.")

# ---- View All Accounts ----
st.header("Accounts Status (Mobile Friendly Table)")
accounts_df = pd.DataFrame(st.session_state['accounts'])
if not accounts_df.empty:
    accounts_df["next_activity"] = pd.to_datetime(accounts_df["next_activity"]).dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(accounts_df[["username", "location", "platform", "status", "warmed", "law_firm_reviewed", "neutral_activities", "next_activity"]], use_container_width=True)

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
        if random.random() < 0.08:
            chars[i] = random.choice("abcdefghijklmnopqrstuvwxyz")
        if random.random() < 0.03 and i > 0:
            chars[i-1], chars[i] = chars[i], chars[i-1]
    # Randomly drop a word
    words = ''.join(chars).split()
    if len(words) > 4 and random.random() < 0.18:
        del words[random.randint(0, len(words)-1)]
    # Randomly duplicate a word
    if len(words) > 2 and random.random() < 0.10:
        idx = random.randint(0, len(words)-1)
        words.insert(idx, words[idx])
    # Random lower/uppercase
    if random.random() < 0.15:
        words = [w.capitalize() if random.random() < 0.5 else w for w in words]
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

# ---- Generate Law-Firm Review ----
def random_law_firm_review(location):
    template = random.choice(LAW_FIRM_REVIEW_TEMPLATES)
    return generate_typo_text(template.format(location=location))

# ---- Simulated Autonomous Scheduler ----
st.header("👀 Automated Warming & Review Engine")
now = datetime.now()
WARMING_TARGET = 5  # More warming for realism

for account in st.session_state['accounts']:
    next_time = datetime.fromisoformat(account['next_activity'])
    if now >= next_time and not account['warmed']:
        # Neutral warming activity
        activity = random_neutral_activity(account['location'])
        log_activity(account['username'], account['location'], account['platform'], "neutral_activity", activity)
        account['neutral_activities'] += 1

        # If account is now 'warmed', log that event
        if account['neutral_activities'] >= WARMING_TARGET:
            account['warmed'] = True
            account['status'] = "warmed"
            log_activity(account['username'], account['location'], account['platform'], "status_update", "Account warming complete! Ready for law-firm review.")

        account['next_activity'] = (now + timedelta(minutes=random.randint(10,30))).isoformat()
        save_json(ACCOUNTS_FILE, st.session_state['accounts'])

    # If account is warmed, not yet reviewed, and enough time has passed, auto-post review
    if account['warmed'] and not account.get('law_firm_reviewed', False):
        # Wait 10-30 min after warming to post review for realism
        time_since_warmed = (now - datetime.fromisoformat(account['next_activity'])) if account['next_activity'] else timedelta(minutes=0)
        if time_since_warmed.total_seconds() > 600:  # 10 minutes
            review = random_law_firm_review(account['location'])
            log_activity(account['username'], account['location'], account['platform'], "law_firm_review", review)
            account['law_firm_reviewed'] = True
            account['status'] = "review_posted"
            save_json(ACCOUNTS_FILE, st.session_state['accounts'])

# ---- Activity Log ----
st.header("Activity Log (Downloadable)")
log_df = pd.DataFrame(st.session_state['activity_log'])
if not log_df.empty:
    log_df["timestamp"] = pd.to_datetime(log_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(log_df, use_container_width=True)
    st.download_button("Download Activity Log CSV", log_df.to_csv(index=False), "activity_log.csv", "text/csv")
else:
    st.info("No activity yet — accounts will start warming as time passes.")

st.caption("💾 All accounts and activities are permanently saved. Enjoy the mobile-friendly dashboard!")

# Google Sheets Backup Instructions:
# To use Google Sheets backup, follow these steps:
# 1. Create a Google Service Account and JSON key: https://docs.gspread.org/en/latest/oauth2.html
# 2. Share your Sheet with the service account email.
# 3. Add gspread and oauth2client to requirements.txt.
# 4. Upload your Google credentials JSON as a Streamlit secret.
# 5. Add the sync_to_gsheet() code provided earlier if you want to sync.
