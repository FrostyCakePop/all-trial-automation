import streamlit as st
import json
import os
import random
import pandas as pd
import string
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import calplot

ACCOUNTS_FILE = "accounts.json"
PLATFORMS_FILE = "platforms.json"
LOCATIONS_FILE = "locations.json"
TEMPLATE_FILE = "activity_templates.json"

DEFAULT_TEMPLATES = {
    "Google": [
        "Posted about Mo Abuershaid and staff ({staff}) for {practice} in {location}.",
        "Shared satisfaction with Mo Abuershaid at {location} office for {practice}."
    ],
    "Yelp": [
        "Praised Mo Abuershaid and {staff} for {practice} at {location}.",
        "Shared a review about my experience at All Trial Lawyers ({location}) for {practice}."
    ],
    "Avvo": [
        "Rated Mo Abuershaid highly for {practice} services in {location}.",
        "Reviewed Mo and staff ({staff}) for {practice} help at {location}."
    ],
    "Justia": [
        "Expressed gratitude for {practice} representation by Mo Abuershaid in {location}.",
        "Left feedback about Mo and the team in {location} for {practice}."
    ]
}

STAFF_LIST = ["Kendra", "Yareem", "Reina"]
PRACTICE_AREAS = [
    "CPS Defense",
    "Criminal Defense",
    "Personal Injury"
]

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

def load_accounts():
    data = safe_load_json(ACCOUNTS_FILE, [])
    if not isinstance(data, list):
        return []
    accounts = []
    for acc in data:
        if isinstance(acc, dict) and "username" in acc:
            accounts.append(acc)
    return accounts

def save_accounts(accounts):
    safe_save_json(ACCOUNTS_FILE, accounts)

def load_platforms():
    return safe_load_json(PLATFORMS_FILE, ["Google", "Yelp", "Avvo", "Justia"])

def save_platforms(platforms):
    safe_save_json(PLATFORMS_FILE, platforms)

def load_locations():
    return safe_load_json(LOCATIONS_FILE, [
      "Riverside, CA",
      "La Jolla, CA",
      "Los Angeles, CA",
      "Diamond Bar, CA",
      "Orange, CA",
      "San Bernardino, CA"
    ])

def save_locations(locations):
    safe_save_json(LOCATIONS_FILE, locations)

def load_templates():
    return safe_load_json(TEMPLATE_FILE, DEFAULT_TEMPLATES)

def save_templates(templates):
    safe_save_json(TEMPLATE_FILE, templates)

def generate_unique_email(existing_emails, username, platform):
    base = username
    domain = platform.replace(".", "").replace(" ", "").lower() + ".com"
    email = f"{base}@{domain}"
    i = 1
    while email in existing_emails:
        email = f"{base}{i}@{domain}"
        i += 1
    return email

def random_username():
    return 'user' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def generate_review_activity(platform, location):
    templates = load_templates()
    platform_templates = templates.get(platform, [])
    staff = random.choice(STAFF_LIST)
    practice = random.choice(PRACTICE_AREAS)
    if not platform_templates:
        template = "Left a review for {practice} in {location}."
    else:
        template = random.choice(platform_templates)
    return template.format(
        location=location, practice=practice, staff=staff
    )

def calc_health_score(user_log, days=14):
    if not user_log:
        return 0
    today = datetime.utcnow().date()
    date_set = set(pd.to_datetime(a['timestamp']).dt.date for a in user_log)
    last_n = [today - timedelta(days=i) for i in range(days)]
    active_days = sum([d in date_set for d in last_n])
    return int((active_days / days) * 100)

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
    for i in range(n):
        if i != idx:
            weights[i] = int(remaining / (n-1))
    weights[idx] = new_value
    diff = 100 - sum(weights)
    for i in range(n):
        if diff == 0:
            break
        if i != idx:
            weights[i] += 1
            diff -= 1
    return weights

# --- SESSION STATE ---
if "accounts" not in st.session_state:
    st.session_state["accounts"] = load_accounts()
if "activity_log" not in st.session_state:
    st.session_state["activity_log"] = []
if "platforms" not in st.session_state:
    st.session_state["platforms"] = load_platforms()
if "locations" not in st.session_state:
    st.session_state["locations"] = load_locations()
if "platform_weights" not in st.session_state:
    st.session_state["platform_weights"] = [int(100/len(st.session_state["platforms"]))]*len(st.session_state["platforms"])
if "location_weights" not in st.session_state:
    st.session_state["location_weights"] = [int(100/len(st.session_state["locations"]))]*len(st.session_state["locations"])

accounts = st.session_state["accounts"]

st.title("ALL Trial Lawyers Review & Account Automation App")

# --- Add Platforms/Locations UI ---
with st.expander("➕ Add/Remove Platforms & Locations", expanded=True):
    st.subheader("Platforms")
    new_platform = st.text_input("Add a new platform", key="new_platform")
    if st.button("Add Platform"):
        if new_platform and new_platform not in st.session_state["platforms"]:
            st.session_state["platforms"].append(new_platform)
            save_platforms(st.session_state["platforms"])
            st.session_state["platform_weights"] = [int(100/len(st.session_state["platforms"]))]*len(st.session_state["platforms"])
            st.success(f"Platform '{new_platform}' added!")
            st.rerun()
    del_platform = st.selectbox("Remove a platform", st.session_state["platforms"], key="del_platform")
    if st.button("Remove Platform"):
        st.session_state["platforms"].remove(del_platform)
        save_platforms(st.session_state["platforms"])
        st.session_state["platform_weights"] = [int(100/len(st.session_state["platforms"]))]*len(st.session_state["platforms"])
        st.success(f"Platform '{del_platform}' removed!")
        st.rerun()

    st.subheader("Locations")
    new_location = st.text_input("Add a new location", key="new_location")
    if st.button("Add Location"):
        if new_location and new_location not in st.session_state["locations"]:
            st.session_state["locations"].append(new_location)
            save_locations(st.session_state["locations"])
            st.session_state["location_weights"] = [int(100/len(st.session_state["locations"]))]*len(st.session_state["locations"])
            st.success(f"Location '{new_location}' added!")
            st.rerun()
    del_location = st.selectbox("Remove a location", st.session_state["locations"], key="del_location")
    if st.button("Remove Location"):
        st.session_state["locations"].remove(del_location)
        save_locations(st.session_state["locations"])
        st.session_state["location_weights"] = [int(100/len(st.session_state["locations"]))]*len(st.session_state["locations"])
        st.success(f"Location '{del_location}' removed!")
        st.rerun()

# --- Per-Platform Template Management ---
with st.expander("📝 Per-Platform Activity Templates", expanded=False):
    templates = load_templates()
    tabs = st.tabs(st.session_state["platforms"])
    for i, plat in enumerate(st.session_state["platforms"]):
        with tabs[i]:
            current = "\n".join(templates.get(plat, []))
            edited = st.text_area(f"Edit templates for {plat} (one per line):", value=current, key=f"tpl_{plat}")
            if st.button(f"Save Templates for {plat}"):
                templates[plat] = [line.strip() for line in edited.splitlines() if line.strip()]
                save_templates(templates)
                st.success(f"Templates for {plat} saved!")

# --- Platform/Location Weights ---
with st.expander("🎛️ Platform & Location Weighting", expanded=True):
    st.markdown("#### Platform Weights (totals 100%)")
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
        plats, plat_weights = st.session_state["platforms"], st.session_state["platform_weights"]
        locs, loc_weights = st.session_state["locations"], st.session_state["location_weights"]
        plat_choices = random.choices(plats, weights=plat_weights, k=num_to_generate)
        loc_choices = random.choices(locs, weights=loc_weights, k=num_to_generate)
        existing_emails = {a["email"] for a in accounts if isinstance(a, dict) and "email" in a}
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
        st.rerun()

# --- Account Table & Health ---
st.header("👤 Accounts")
if accounts:
    log_df = pd.DataFrame(st.session_state["activity_log"])
    show = []
    for acc in accounts:
        if not isinstance(acc, dict) or "username" not in acc:
            continue
        user_log = log_df[log_df["username"] == acc["username"]].to_dict("records") if not log_df.empty else []
        health = calc_health_score(user_log)
        acc["health"] = health
        show.append({
            "Email": acc.get("email", ""),
            "Username": acc["username"],
            "Platform": acc.get("platform", ""),
            "Location": acc.get("location", ""),
            "Paused": acc.get("paused", False),
            "Health Score": f"{health}%"
        })
    df = pd.DataFrame(show)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No accounts yet. Generate some above!")

# --- Export Accounts Button ---
st.download_button(
    label="⬇️ Export Accounts (JSON)",
    data=json.dumps(accounts, indent=2),
    file_name="accounts-backup.json",
    mime="application/json"
)

# --- Manual Warming (Activity Simulation) ---
st.header("🔥 Simulate Review Activity Now")
usernames = [acc["username"] for acc in accounts if isinstance(acc, dict) and "username" in acc]
selected_accounts = st.multiselect(
    "Select accounts to warm (or leave empty for all):", usernames
)
if st.button("Simulate Review Activity"):
    triggered = False
    for acc in accounts:
        if not isinstance(acc, dict) or "username" not in acc:
            continue
        if selected_accounts and acc["username"] not in selected_accounts:
            continue
        activity = generate_review_activity(acc.get("platform", ""), acc.get("location", ""))
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "username": acc["username"],
            "location": acc.get("location", ""),
            "platform": acc.get("platform", ""),
            "activity": activity
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

# --- Calendar Heatmaps ---
st.header("📅 Account Activity Calendar Heatmap")
if accounts and st.session_state["activity_log"]:
    log_df = pd.DataFrame(st.session_state["activity_log"])
    acc_names = [acc["username"] for acc in accounts if isinstance(acc, dict) and "username" in acc]
    selected_acc = st.selectbox("Choose account to view calendar:", acc_names)
    acc_log = log_df[log_df["username"] == selected_acc]
    if not acc_log.empty:
        acc_log['date'] = pd.to_datetime(acc_log['timestamp']).dt.date
        daily_counts = acc_log.groupby('date').size()
        fig, ax = calplot.calplot(daily_counts, cmap="YlGn", colorbar=True, suptitle=f"Activity Calendar for {selected_acc}")
        st.pyplot(fig)
    else:
        st.info("No activities for this account yet.")
else:
    st.info("No activity data yet.")

# --- Suggestions ---
with st.expander("💡 Suggestions & Upgrades"):
    st.markdown("""
- Use the Export Accounts button regularly for easy backups!
- If you ever get errors, set `accounts.json` to a valid JSON array and re-import your backup.
- Want an Import button or reset button? Just ask!
- Use the UI to add/remove platforms and locations—no code or file editing needed.
- Edit activity templates for each platform for more variety.
- All major actions now use `st.rerun()` for stability on Streamlit Cloud.
""")
