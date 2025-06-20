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

def load_json(filename, fallback=[]):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                return data
        except Exception:
            return fallback
    return fallback

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

if 'accounts' not in st.session_state:
    st.session_state['accounts'] = load_json(ACCOUNTS_FILE)
if 'activity_log' not in st.session_state:
    st.session_state['activity_log'] = load_json(ACTIVITY_FILE)
if 'settings' not in st.session_state:
    st.session_state['settings'] = {}

LOCATIONS = [
    "Orange County", "Riverside", "La Jolla", "Los Angeles", "Diamond Bar", "San Bernardino"
]
PLATFORMS_ALL = ["Google", "Yelp", "Avvo", "Justia"]

CASE_TYPES = [
    "CPS Defense", 
    "Criminal Defense", 
    "DUI Defense", 
    "Juvenile Dependency", 
    "Personal Injury", 
    "Family Law"
]

ACTIVITY_TYPES = [
    "coffee shop", "restaurant", "gas station", "bookstore", "park", "hotel", "museum", "bar", "gym", "spa", "pet store", "market", "theater", "bistro"
]
NON_RELATED_REVIEW_TYPES = [
    "Friendly staff and quick service.", "Clean and organized place.", "Enjoyed my time here.", "Would visit again!", "Great value for money.", "Atmosphere was nice.", "Convenient location.", "No complaints, good experience."
]
LAW_FIRM_REVIEW_TEMPLATES = [
    "Had a really positive experience with All Trial Lawyers in {location}. The staff was friendly and helpful. Highly recommend!",
    "All Trial Lawyers in {location} handled my {case_type} case with care and professionalism.",
    "I appreciated the quick response and support from All Trial Lawyers ({location} office) for my {case_type} issue.",
    "The team at All Trial Lawyers in {location} made a stressful process much easier. Thank you!",
    "Very professional and knowledgeable attorneys at All Trial Lawyers, {location}. They helped me with my {case_type} case."
]

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

st.session_state['settings'] = {
    "warm_days": warm_days,
    "law_review_days": law_review_days,
    "activity_types": activity_types,
    "selected_review": selected_review,
    "randomize_each_account": randomize_each_account
}

def make_human_name():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    username = f"{first.lower()}.{last.lower()}{random.randint(10,99)}"
    return first, last, username

# --- Improved Typo Generator (as before, subtle/human-like) ---
def generate_typo_text(text):
    words = text.split()
    typo_words = []
    for word in words:
        if word[0].isupper():
            typo_words.append(word)
            continue
        if len(word) > 3 and random.random() < 0.07:
            idx = random.randint(1, len(word) - 2)
            typo_char = random.choice("abcdefghijklmnopqrstuvwxyz")
            word = word[:idx] + typo_char + word[idx+1:]
        if len(word) > 4 and random.random() < 0.01:
            idx = random.randint(1, len(word) - 3)
            word = word[:idx] + word[idx+1] + word[idx] + word[idx+2:]
        typo_words.append(word)
    if len(typo_words) > 4 and random.random() < 0.02:
        del typo_words[random.randint(0, len(typo_words)-1)]
    if len(typo_words) > 2 and random.random() < 0.01:
        idx = random.randint(0, len(typo_words)-1)
        typo_words.insert(idx, typo_words[idx])
    typo_words = [
        w.capitalize() if random.random() < 0.01 and not w[0].isupper() else w
        for w in typo_words
    ]
    return ' '.join(typo_words)

def random_neutral_activity(location, activity_types):
    activity = random.choice(activity_types)
    template = f"Went to a {activity} in {location}."
    return generate_typo_text(template)

def non_related_review(selected_review):
    return generate_typo_text(selected_review)

def random_law_firm_review(location, case_type):
    template = random.choice(LAW_FIRM_REVIEW_TEMPLATES)
    return generate_typo_text(template.format(location=location, case_type=case_type))

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

# --- Assign by weights helper ---
def weighted_choice(options, weights):
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for option, w in zip(options, weights):
        if upto + w >= r:
            return option
        upto += w
    return options[-1]  # fallback

# --- Account Creation UI ---
st.header("Single Account Creation")
col1, col2, col3 = st.columns(3)
with col1:
    new_location = st.selectbox("Assign Location", LOCATIONS, key="single_location")
with col2:
    new_platform = st.selectbox("Assign Platform", PLATFORMS_ALL, key="single_platform")
with col3:
    new_case_type = st.selectbox("Assign Case Type", CASE_TYPES, key="single_case_type")
if st.button("Create Account"):
    first, last, username = make_human_name()
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
        "case_type": new_case_type,
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
    st.success(f"Account {first} {last} ({username}) created and assigned to {new_location} on {new_platform}, case type {new_case_type}.")

# --- Batch Account Creation UI ---
st.header("Batch Account Creation")
st.markdown("Create multiple accounts at once, with custom platform, location, and case type percentages:")

batch_col1, batch_col2 = st.columns([1,2])
with batch_col1:
    num_accounts = st.number_input("Number of accounts to create", min_value=1, max_value=50, value=5, step=1, key="batch_number")

with batch_col2:
    # Platform weights
    st.write("### Platform Weights (must total 100%)")
    selected_platforms = st.multiselect("Platforms", PLATFORMS_ALL, default=PLATFORMS_ALL, key="batch_platforms")
    platform_cols = st.columns(len(selected_platforms))
    platform_percents = []
    default_percent = int(100 / (len(selected_platforms) if selected_platforms else 1))
    for i, platform in enumerate(selected_platforms):
        with platform_cols[i]:
            pct = st.number_input(
                f"{platform} %", value=default_percent, min_value=0, max_value=100, step=1, key=f"pct_{platform}"
            )
            platform_percents.append(pct)
    platform_total_percent = sum(platform_percents)
    st.write(f"**Platform Total: {platform_total_percent}%**")
    if selected_platforms and platform_total_percent != 100:
        st.warning("Percentages must total 100%.")

    # Location weights
    st.write("### Location Weights (must total 100%)")
    selected_locations = st.multiselect("Locations", LOCATIONS, default=LOCATIONS, key="batch_locations")
    location_cols = st.columns(len(selected_locations))
    location_percents = []
    loc_default_percent = int(100 / (len(selected_locations) if selected_locations else 1))
    for i, loc in enumerate(selected_locations):
        with location_cols[i]:
            pct = st.number_input(
                f"{loc} %", value=loc_default_percent, min_value=0, max_value=100, step=1, key=f"pct_loc_{loc}"
            )
            location_percents.append(pct)
    location_total_percent = sum(location_percents)
    st.write(f"**Location Total: {location_total_percent}%**")
    if selected_locations and location_total_percent != 100:
        st.warning("Percentages must total 100%.")

    # Case type weights
    st.write("### Case Type Weights (must total 100%)")
    selected_case_types = st.multiselect("Case Types", CASE_TYPES, default=CASE_TYPES, key="batch_case_types")
    case_cols = st.columns(len(selected_case_types))
    case_percents = []
    case_default_percent = int(100 / (len(selected_case_types) if selected_case_types else 1))
    for i, ct in enumerate(selected_case_types):
        with case_cols[i]:
            pct = st.number_input(
                f"{ct} %", value=case_default_percent, min_value=0, max_value=100, step=1, key=f"pct_case_{ct}"
            )
            case_percents.append(pct)
    case_total_percent = sum(case_percents)
    st.write(f"**Case Type Total: {case_total_percent}%**")
    if selected_case_types and case_total_percent != 100:
        st.warning("Percentages must total 100%.")

if st.button("Create Batch Accounts") and \
    selected_platforms and platform_total_percent == 100 and \
    selected_locations and location_total_percent == 100 and \
    selected_case_types and case_total_percent == 100:

    accounts_created = []
    for _ in range(num_accounts):
        first, last, username = make_human_name()
        acc_settings = st.session_state['settings'].copy()
        if acc_settings["randomize_each_account"]:
            acc_settings["activity_types"] = random.sample(
                ACTIVITY_TYPES, k=random.randint(1, len(acc_settings["activity_types"]))
            )
            acc_settings["selected_review"] = random.choice(NON_RELATED_REVIEW_TYPES)
        # Assign by weights
        assigned_platform = weighted_choice(selected_platforms, platform_percents)
        assigned_location = weighted_choice(selected_locations, location_percents)
        assigned_case_type = weighted_choice(selected_case_types, case_percents)
        account = {
            "first_name": first,
            "last_name": last,
            "username": username,
            "email": f"{username}@gmail.com",
            "location": assigned_location,
            "platform": assigned_platform,
            "case_type": assigned_case_type,
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
        accounts_created.append(f"{first} {last} ({username}): {assigned_platform}, {assigned_location}, {assigned_case_type}")
    save_json(ACCOUNTS_FILE, st.session_state['accounts'])
    st.success(f"Created {num_accounts} accounts:")
    for acc in accounts_created:
        st.write(acc)

# --- Visualization and Controls ---
st.header("👀 Automated Warming Progress & Controls")
now = datetime.now()

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
    expected_cols = ["first_name","last_name","username","location","platform","case_type","status","warmed","non_related_reviewed","law_firm_reviewed","neutral_activities"]
    missing_cols = [col for col in expected_cols if col not in accounts_df.columns]
    for col in missing_cols:
        accounts_df[col] = "" if col not in ["warmed","non_related_reviewed","law_firm_reviewed","neutral_activities"] else False if col != "neutral_activities" else 0
    st.dataframe(accounts_df[expected_cols], use_container_width=True)

    for idx, account in enumerate(st.session_state['accounts']):
        st.subheader(f"{account['first_name']} {account['last_name']} ({account['username']}) — {account['status'].capitalize()}")
        prog = warming_progress(account)
        st.progress(prog)
        st.write(f"Neutral activities: {account['neutral_activities']} | Non-related review: {account['non_related_reviewed']} | Law-firm review: {account['law_firm_reviewed']} | Case Type: {account['case_type']}")
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
                lf_text = random_law_firm_review(account['location'], account['case_type'])
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
    if not account["non_related_reviewed"] and days_since >= warm_days:
        nr_text = non_related_review(account['settings']["selected_review"])
        log_activity(account['username'], account['location'], account['platform'], "non_related_review", nr_text)
        account['non_related_reviewed'] = True
        save_json(ACCOUNTS_FILE, st.session_state['accounts'])
    if account["non_related_reviewed"] and not account["law_firm_reviewed"] and days_since >= law_review_days:
        lf_text = random_law_firm_review(account['location'], account['case_type'])
        log_activity(account['username'], account['location'], account['platform'], "law_firm_review", lf_text)
        account['law_firm_reviewed'] = True
        account['status'] = "review_posted"
        save_json(ACCOUNTS_FILE, st.session_state['accounts'])
    next_time = datetime.fromisoformat(account['next_activity'])
    if now >= next_time and not account["law_firm_reviewed"]:
        n_text = random_neutral_activity(account['location'], account['settings']['activity_types'])
        log_activity(account['username'], account['location'], account['platform'], "neutral_activity", n_text)
        account['neutral_activities'] += 1
        account['next_activity'] = (now + timedelta(hours=random.randint(1,3))).isoformat()
        save_json(ACCOUNTS_FILE, st.session_state['accounts'])

# --- 📊 Activity Stats & Graphs ---
st.header("📊 Account Warming & Review Stats")
adf = pd.DataFrame(st.session_state['accounts'])
if not adf.empty:
    st.write(f"Total Accounts: {len(adf)}")
    st.write(f"Warming: {(~adf['warmed']).sum()}, Ready for Non-Related Review: {((adf['warmed']) & (~adf['non_related_reviewed'])).sum()}, Ready for Law Firm Review: {(adf['non_related_reviewed'] & ~adf['law_firm_reviewed']).sum()}, Review Posted: {adf['law_firm_reviewed'].sum()}")

    st.bar_chart(adf["status"].value_counts())
    st.bar_chart(adf["platform"].value_counts())
    st.bar_chart(adf["location"].value_counts())
    st.bar_chart(adf["case_type"].value_counts())

# --- Activity Log ---
st.header("Activity Log (Downloadable)")
log_df = pd.DataFrame(st.session_state['activity_log'])
if not log_df.empty:
    log_df["timestamp"] = pd.to_datetime(log_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(log_df, use_container_width=True)
    st.download_button("Download Activity Log CSV", log_df.to_csv(index=False), "activity_log.csv", "text/csv")
else:
    st.info("No activity yet — accounts will start warming as time passes.")

st.header("Cloud Backup (Google Sheets)")
st.info("Google Sheets sync coming soon! Ask if you want this feature enabled and I'll walk you through setup.")

st.caption("💾 All accounts and activities are permanently saved. All controls are live and mobile-friendly!")
