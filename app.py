import streamlit as st
import json
import os
import random
import pandas as pd
import string
from datetime import datetime, timedelta

ACCOUNTS_FILE = "accounts.json"
TEMPLATE_FILE = "activity_templates.json"

# ========== HELPERS FOR FILES & DATA ==========

def safe_load_json(filename, default):
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def safe_save_json(filename, data):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.warning(f"Failed to save {filename}: {e}")

# ========== DEFAULTS ==========

DEFAULT_PLATFORMS = [
    "Gmail", "Outlook", "Yahoo", "ProtonMail", "AOL", "Zoho", "iCloud"
]

DEFAULT_LOCATIONS = [
    "Dallas", "Chicago", "San Francisco", "London", "New York", "Miami",
    "Los Angeles", "Seattle", "Houston", "Boston", "Toronto", "Sydney"
]

DEFAULT_TEMPLATES = [
    "Commented on a {topic} post in {location}",
    "Liked a {topic} article in {location}",
    "Shared a news update about {topic} in {location}",
    "Followed a user interested in {topic} in {location}",
    "Replied to a general discussion on {topic} in {location}"
]

# ========== ACCOUNT MANAGEMENT ==========

def load_accounts():
    return safe_load_json(ACCOUNTS_FILE, [])

def save_accounts(accounts):
    safe_save_json(ACCOUNTS_FILE, accounts)

def generate_unique_email(existing_emails, username, platform):
    base = username
    domain = {
        "Gmail": "gmail.com",
        "Outlook": "outlook.com",
        "Yahoo": "yahoo.com",
        "ProtonMail": "protonmail.com",
        "AOL": "aol.com",
        "Zoho": "zoho.com",
        "iCloud": "icloud.com"
    }.get(platform, "mail.com")
    email = f"{base}@{domain}"
    i = 1
    while email in existing_emails:
        email = f"{base}{i}@{domain}"
        i += 1
    return email

def random_username():
    return 'user' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# ========== ACTIVITY TEMPLATES ==========

def load_templates():
    return safe_load_json(TEMPLATE_FILE, DEFAULT_TEMPLATES)

def save_templates(templates):
    safe_save_json(TEMPLATE_FILE, templates)

def generate_neutral_activity(location, topic="general"):
    templates = load_templates()
    if not templates:
        return "No templates available."
    template = random.choice(templates)
    return template.format(topic=topic, location=location)

# ========== HEALTH SCORING ==========

def calc_health_score(user_log, days=14):
    if not user_log:
        return 0
    today = datetime.utcnow().date()
    date_set = set(pd.to_datetime(a['timestamp']).date() for a in user_log)
    last_n = [today - timedelta(days=i) for i in range(days)]
    active_days = sum([d in date_set for d in last_n])
    return int((active_days / days) * 100)

# ========== WEIGHTED SLIDER LOGIC ==========

def auto_balance_weights(weights, idx, new_value):
    n = len(weights)
    if n <= 1:
        return weights
    total_other = sum(weights) - weights[idx]
    remaining = 100 - new_value
    if remaining < 0:
        remaining = 0
    if n - 1 == 0:
        return [new_value] * n
    # Spread remaining evenly among others
    if total_other == 0:
        for i in range(n):
            if i != idx:
                weights[i] = remaining // (n-1)
        weights[idx] = new_value
        return weights
    for i in range(n):
        if i != idx:
            weights[i] = int(remaining / (n-1))
    # fix rounding
    weights[idx] = new_value
    diff = 100 - sum(weights)
    for i in range(n):
        if diff == 0:
            break
        if i != idx:
            weights[i] += 1
            diff -= 1
    return weights

# ========== SESSION STATE ==========

if "accounts" not in st.session_state:
    st.session_state["accounts"] = load_accounts()

if "activity_log" not in st.session_state:
    st.session_state["activity_log"] = []

# Remember platform/location weights in session
if "platforms" not in st.session_state:
    st.session_state["platforms"] = DEFAULT_PLATFORMS.copy()
if "locations" not in st.session_state:
    st.session_state["locations"] = DEFAULT_LOCATIONS.copy()
if "platform_weights" not in st.session_state:
    st.session_state["platform_weights"] = [int(100/len(DEFAULT_PLATFORMS))]*len(DEFAULT_PLATFORMS)
if "location_weights" not in st.session_state:
    st.session_state["location_weights"] = [int(100/len(DEFAULT_LOCATIONS))]*len(DEFAULT_LOCATIONS)

accounts = st.session_state["accounts"]

# ========== UI START ==========

st.title("Automated Account Generator & Warming App")

# --- Platform and Location Weights ---
with st.expander("🎛️ Platform & Location Weighting", expanded=True):
    st.markdown("#### Email Platform Weights (totals 100%)")
    cols = st.columns(len(st.session_state["platforms"]))
    for idx, (col, plat) in enumerate(zip(cols, st.session_state["platforms"])):
        with col:
            val = st.slider(
                plat,
                0, 100,
                st.session_state["platform_weights"][idx],
                key=f"platform_weight_{plat}"
            )
            if val != st.session_state["platform_weights"][idx]:
                st.session_state["platform_weights"] = auto_balance_weights(
                    st.session_state["platform_weights"], idx, val
                )
    st.write("Current Platform Weights:", dict(zip(st.session_state["platforms"], st.session_state["platform_weights"])))

    st.markdown("#### Location Weights (totals 100%)")
    cols2 = st.columns(len(st.session_state["locations"]))
    for idx, (col, loc) in enumerate(zip(cols2, st.session_state["locations"])):
        with col:
            val = st.slider(
                loc,
                0, 100,
                st.session_state["location_weights"][idx],
                key=f"location_weight_{loc}"
            )
            if val != st.session_state["location_weights"][idx]:
                st.session_state["location_weights"] = auto_balance_weights(
                    st.session_state["location_weights"], idx, val
                )
    st.write("Current Location Weights:", dict(zip(st.session_state["locations"], st.session_state["location_weights"])))

# --- Automated Account Generation ---
with st.expander("✨ Generate Accounts Automatically", expanded=True):
    num_to_generate = st.number_input("Number of accounts to generate", min_value=1, max_value=30, value=5)
    if st.button("Generate Accounts"):
        # Weighted random choice for platforms/locations
        plats, plat_weights = st.session_state["platforms"], st.session_state["platform_weights"]
        locs, loc_weights = st.session_state["locations"], st.session_state["location_weights"]
        plat_choices = random.choices(plats, weights=plat_weights, k=num_to_generate)
        loc_choices = random.choices(locs, weights=loc_weights, k=num_to_generate)
        existing_emails = {a["email"] for a in accounts}
        for i in range(num_to_generate):
            username = random_username()
            platform = plat_choices[i]
            location = loc_choices[i]
            email = generate_unique_email(existing_emails, username, platform)
            existing_emails.add(email)
            accounts.append({
                "username": username,
                "email": email,
                "platform": platform,
                "location": location,
                "paused": False,
                "health": 100
            })
        save_accounts(accounts)
        st.success(f"{num_to_generate} accounts generated and added!")
        st.experimental_rerun()

# --- Account Table & Health ---
st.header("👤 Accounts")
if accounts:
    log_df = pd.DataFrame(st.session_state["activity_log"])
    show = []
    for acc in accounts:
        user_log = log_df[log_df["username"] == acc["username"]].to_dict("records") if not log_df.empty else []
        health = calc_health_score(user_log)
        acc["health"] = health
        show.append({
            "Email": acc["email"],
            "Username": acc["username"],
            "Platform": acc["platform"],
            "Location": acc["location"],
            "Paused": acc.get("paused", False),
            "Health Score": f"{health}%"
        })
    df = pd.DataFrame(show)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No accounts yet. Generate some above!")

# --- Manual Warming (Activity Simulation) ---
st.header("🔥 Simulate Activity Now")
usernames = [acc["username"] for acc in accounts]
selected_accounts = st.multiselect(
    "Select accounts to warm (or leave empty for all):", usernames
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
        st.session_state["activity_log"].append(log_entry)
        triggered = True
    if not triggered:
        st.info("No accounts selected or available.")

# --- Activity Log ---
st.header("🗂️ Activity Log")
if st.session_state["activity_log"]:
    log_df = pd.DataFrame(st.session_state["activity_log"])
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

# --- Suggestions ---
with st.expander("💡 Suggestions & Upgrades"):
    st.markdown("""
- **Calendar heatmap:** Visualize daily account activity.
- **Bulk import/export:** Upload/download accounts as CSV.
- **Per-platform templates:** Customize neutral actions by platform.
- **Activity scheduler:** Automate warming by timezone/activity hours.
- **Persistent activity log:** Save all logs to disk or GitHub for backup.
- **Advanced health metrics:** Score on more than just days active.
Want any of these? Just ask!
""")
