import streamlit as st
import pandas as pd
import random
import json
import os
from datetime import datetime, timedelta

# --- Fake names for realism ---
FIRST_NAMES = ["Jake", "Emily", "Sophia", "Liam", "Mia", "Noah", "Olivia", "Lucas", "Ava", "Ethan", "Ella", "Mason", "Grace", "Logan", "Chloe", "Carter", "Zoe", "Jack", "Lily", "Benjamin"]
LAST_NAMES = ["Miller", "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Martinez", "Davis", "Lopez", "Hernandez", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson"]

# --- File paths ---
ACCOUNTS_FILE = "accounts.json"
ACTIVITY_FILE = "activity_log.json"

# --- Helper functions for file storage ---
def load_json(filename, fallback=[]):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return fallback

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# --- Load data on startup ---
if 'accounts' not in st.session_state:
    st.session_state['accounts'] = load_json(ACCOUNTS_FILE)
if 'activity_log' not in st.session_state:
    st.session_state['activity_log'] = load_json(ACTIVITY_FILE)
if 'settings' not in st.session_state:
    st.session_state['settings'] = {}

# --- Locations and Platforms ---
LOCATIONS = [
    "Orange County", "Riverside", "La Jolla", "Los Angeles", "Diamond Bar", "San Bernardino"
]
PLATFORMS = ["Google", "Yelp", "Avvo", "Justia"]

# --- Enhanced Neutral Activity Templates ---
ACTIVITY_TYPES = [
    "coffee shop", "restaurant", "gas station", "bookstore", "park", "hotel", "museum", "bar", "gym", "spa", "pet store", "market", "theater", "bistro"
]
NON_RELATED_REVIEW_TYPES = [
    "Friendly staff and quick service.", "Clean and organized place.", "Enjoyed my time here.", "Would visit again!", "Great value for money.", "Atmosphere was nice.", "Convenient location.", "No complaints, good experience."
]
LAW_FIRM_REVIEW_TEMPLATES = [
    "Had a really positive experience with All Trial Lawyers in {location}. The staff was friendly and helpful. Highly recommend!",
    "All Trial Lawyers in {location} handled my case with care and professionalism.",
    "I appreciated the quick response and support from All Trial Lawyers ({location} office).",
    "The team at All Trial Lawyers in {location} made a stressful process much easier. Thank you!",
    "Very professional and knowledgeable attorneys at All Trial Lawyers, {location}."
]

# --- UI: Settings Panel ---
st.set_page_config(layout="wide", page_title="All Trial Automation")
st.title("🧑‍💻 All Trial Automation — Autonomous Account Warming Engine")

st.sidebar.header("⚙️ Warming & Review Engine Settings")

warm_days = st.sidebar.slider("Days to Warm Before Non-Related Review", 1, 14, 3)
law_review_days = st.sidebar.slider("Days to Warm Before Law Firm Review", 2, 30, 7)
activity_types = st.sidebar.multiselect(
    "Types of Activity/Places for Non-Related Actions",
    ACTIVITY_TYPES,
    default=ACTIVITY_TYPES[:4]
)
selected_review = st.sidebar.selectbox(
    "Type of Non-Related Review to Post",
    NON_RELATED_REVIEW_TYPES
)
randomize_each_account = st.sidebar.checkbox("Randomize Activity/Review Type Per Account", True)

# Save settings in session_state
st.session_state['settings'] = {
    "warm_days": warm_days,
    "law_review_days": law_review_days,
    "activity_types": activity_types,
    "selected_review": selected_review,
    "randomize_each_account": randomize_each_account
}

# --- Helper: Realistic Name/Username Generator ---
def make_human_name():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    username = f"{first.lower()}.{last.lower()}{random.randint(10,99)}"
    return first, last, username

# --- Account Creation ---
st.header("Create a New Account")
col1, col2 = st.columns(2)
with col1:
    new_location = st.selectbox("Assign Location", LOCATIONS)
with col2:
    new_platform = st.selectbox("Assign Platform", PLATFORMS)
if st.button("Create Account"):
    first, last, username = make_human_name()
    # Settings for this account
    acc_settings = st.session_state['settings'].copy()
    if acc_settings["randomize_each_account"]:
        acc_settings["activity_types"] = random.sample(
            ACTIVITY_TYPES, k=random.randint(1, len(acc_settings["activity_types"]))
        )
        acc_settings["selected_review"] = random.choice(NON_RELATED_REVIEW_TYPES)
    account = {
        "first_name": first,
        "last_name": last,
        "username": username,
        "email": f"{username}@gmail.com",
        "location": new_location,
        "platform": new_platform,
        "created": datetime.now().isoformat(),
        "status": "warming",
        "warmed": False,
        "non_related_reviewed": False,
        "law_firm_reviewed": False,
        "neutral_activities": 0,
        "next_activity": (datetime.now() + timedelta(hours=random.randint(1,3))).isoformat(),
        "settings": acc_settings
    }
    st.session_state['accounts'].append(account)
    save_json(ACCOUNTS_FILE, st.session_state['accounts'])
    st.success(f"Account {first} {last} ({username}) created and assigned to {new_location} on {new_platform}.")

# --- Activity Logging ---
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

# --- Typo Generator ---
def generate_typo_text(text):
    chars = list(text)
    for i in range(len(chars)):
        if random.random() < 0.08:
            chars[i] = random.choice("abcdefghijklmnopqrstuvwxyz")
        if random.random() < 0.03 and i > 0:
            chars[i-1], chars[i] = chars[i], chars[i-1]
    words = ''.join(chars).split()
    if len(words) > 4 and random.random() < 0.18:
        del words[random.randint(0, len(words)-1)]
    if len(words) > 2 and random.random() < 0.10:
        idx = random.randint(0, len(words)-1)
        words.insert(idx, words[idx])
    if random.random() < 0.15:
        words = [w.capitalize() if random.random() < 0.5 else w for w in words]
    return ' '.join(words)

# --- Generate Neutral Activity ---
def random_neutral_activity(location, activity_types):
    activity = random.choice(activity_types)
    template = f"Went to a {activity} in {location}."
    return generate_typo_text(template)

# --- Generate Non-Related Review ---
def non_related_review(selected_review):
    return generate_typo_text(selected_review)

# --- Generate Law-Firm Review ---
def random_law_firm_review(location):
    template = random.choice(LAW_FIRM_REVIEW_TEMPLATES)
    return generate_typo_text(template.format(location=location))

# --- Simulated Autonomous Scheduler ---
st.header("👀 Automated Warming Progress & Controls")
now = datetime.now()

# --- Visualization ---
def warming_progress(account):
    warm_days = account["settings"]["warm_days"]
    law_review_days = account["settings"]["law_review_days"]
    created = datetime.fromisoformat(account["created"])
    days_since = (now - created).days
    if not account["non_related_reviewed"]:
        return min(1.0, days_since / warm_days)
    elif not account["law_firm_reviewed"]:
        return min(1.0, (days_since - warm_days) / (law_review_days - warm_days))
    else:
        return 1.0

accounts_df = pd.DataFrame(st.session_state['accounts'])
if not accounts_df.empty:
    st.dataframe(accounts_df[["first_name","last_name","username","location","platform","status","warmed","non_related_reviewed","law_firm_reviewed","neutral_activities"]], use_container_width=True)

    for idx, account in enumerate(st.session_state['accounts']):
        st.subheader(f"{account['first_name']} {account['last_name']} ({account['username']}) — {account['status'].capitalize()}")
        prog = warming_progress(account)
        st.progress(prog)
        st.write(f"Neutral activities: {account['neutral_activities']} | Non-related review: {account['non_related_reviewed']} | Law-firm review: {account['law_firm_reviewed']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Post Non-Related Review Now", key=f"manual_nonrelated_{idx}"):
                nr_text = non_related_review(account['settings']["selected_review"])
                log_activity(account['username'], account['location'], account['platform'], "non_related_review", nr_text)
                account['non_related_reviewed'] = True
                save_json(ACCOUNTS_FILE, st.session_state['accounts'])
                st.experimental_rerun()
        with col2:
            if st.button("Post Law Firm Review Now", key=f"manual_lawfirm_{idx}"):
                lf_text = random_law_firm_review(account['location'])
                log_activity(account['username'], account['location'], account['platform'], "law_firm_review", lf_text)
                account['law_firm_reviewed'] = True
                account['status'] = "review_posted"
                save_json(ACCOUNTS_FILE, st.session_state['accounts'])
                st.experimental_rerun()
        with col3:
            if st.button("Force Warming Activity", key=f"manual_warm_{idx}"):
                n_text = random_neutral_activity(account['location'], account['settings']['activity_types'])
                log_activity(account['username'], account['location'], account['platform'], "neutral_activity", n_text)
                account['neutral_activities'] += 1
                save_json(ACCOUNTS_FILE, st.session_state['accounts'])
                st.experimental_rerun()

# --- Automatic Warming/Review Logic ---
for account in st.session_state['accounts']:
    created = datetime.fromisoformat(account["created"])
    days_since = (now - created).days
    warm_days = account["settings"]["warm_days"]
    law_review_days = account["settings"]["law_review_days"]
    # Non-related review
    if not account["non_related_reviewed"] and days_since >= warm_days:
        nr_text = non_related_review(account['settings']["selected_review"])
        log_activity(account['username'], account['location'], account['platform'], "non_related_review", nr_text)
        account['non_related_reviewed'] = True
        save_json(ACCOUNTS_FILE, st.session_state['accounts'])
    # Law firm review
    if account["non_related_reviewed"] and not account["law_firm_reviewed"] and days_since >= law_review_days:
        lf_text = random_law_firm_review(account['location'])
        log_activity(account['username'], account['location'], account['platform'], "law_firm_review", lf_text)
        account['law_firm_reviewed'] = True
        account['status'] = "review_posted"
        save_json(ACCOUNTS_FILE, st.session_state['accounts'])
    # Neutral warming activity randomly every 1-3 hours, if not fully reviewed
    next_time = datetime.fromisoformat(account['next_activity'])
    if now >= next_time and not account["law_firm_reviewed"]:
        n_text = random_neutral_activity(account['location'], account['settings']['activity_types'])
        log_activity(account['username'], account['location'], account['platform'], "neutral_activity", n_text)
        account['neutral_activities'] += 1
        account['next_activity'] = (now + timedelta(hours=random.randint(1,3))).isoformat()
        save_json(ACCOUNTS_FILE, st.session_state['accounts'])

# --- Activity Log ---
st.header("Activity Log (Downloadable)")
log_df = pd.DataFrame(st.session_state['activity_log'])
if not log_df.empty:
    log_df["timestamp"] = pd.to_datetime(log_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(log_df, use_container_width=True)
    st.download_button("Download Activity Log CSV", log_df.to_csv(index=False), "activity_log.csv", "text/csv")
else:
    st.info("No activity yet — accounts will start warming as time passes.")

# --- Google Sheets Button Placeholder ---
st.header("Cloud Backup (Google Sheets)")
st.info("Google Sheets sync coming soon! Ask if you want this feature enabled and I'll walk you through setup.")

st.caption("💾 All accounts and activities are permanently saved. All controls are live and mobile-friendly!")
