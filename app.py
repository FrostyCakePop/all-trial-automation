import streamlit as st
import pandas as pd
import random
import json
import os
from datetime import datetime, timedelta

# ------------------ Data Setup ------------------
def load_json(filename, fallback=[]):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception:
            return fallback
    return fallback

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

ACCOUNTS_FILE = "accounts.json"
ACTIVITY_FILE = "activity_log.json"
REVIEW_POOL_FILE = "review_pool.json"

if 'accounts' not in st.session_state:
    st.session_state['accounts'] = load_json(ACCOUNTS_FILE)
if 'activity_log' not in st.session_state:
    st.session_state['activity_log'] = load_json(ACTIVITY_FILE)
if 'review_pool' not in st.session_state:
    st.session_state['review_pool'] = load_json(REVIEW_POOL_FILE, [
        # Default review templates (editable in-app)
        {"type": "law_firm_review", "prompt": "All Trial Lawyers helped me with my {case_type} case. {custom_message}"},
        {"type": "non_related_review", "prompt": "Visited a {place_type} in {location} and had a great experience. {custom_message}"},
        # Add more using in-app UI
    ])
if 'real_reviews' not in st.session_state:
    st.session_state['real_reviews'] = []  # For mimicking structure

def save_review_pool():
    save_json(REVIEW_POOL_FILE, st.session_state['review_pool'])

# --------------- Sidebar Settings ---------------
st.sidebar.header("Warming & Review Engine Settings")
activity_types = ["gas station", "restaurant", "park", "hotel", "museum", "gym", "spa", "market"]
case_types = ["CPS Defense", "Criminal Defense", "DUI Defense", "Juvenile Dependency", "Personal Injury", "Family Law"]

min_searches = st.sidebar.number_input("Min Google Searches per Account", 1, 20, 5)
max_searches = st.sidebar.number_input("Max Google Searches per Account", min_searches, 50, 20)
min_nonrelated = st.sidebar.number_input("Min Non-Related Reviews per Account", 1, 10, 3)
max_nonrelated = st.sidebar.number_input("Max Non-Related Reviews per Account", min_nonrelated, 20, 10)

# ---------------- Review Pool Editor ---------------
st.header("📝 Review Pool Editor")
st.markdown("Add new review templates or prompts for more realistic/flexible reviews. These will be picked randomly for new reviews.")

with st.expander("Add a review prompt to the pool"):
    new_type = st.selectbox("Review Type", options=["law_firm_review", "non_related_review", "custom"])
    new_prompt = st.text_area("Prompt/template (e.g. 'Mo and Kendra were amazing for my DUI case in {location}')")
    if st.button("Add to Review Pool"):
        st.session_state['review_pool'].append({"type": new_type, "prompt": new_prompt})
        save_review_pool()
        st.success("Prompt added!")

if st.session_state['review_pool']:
    st.write("**Current Review Pool:**")
    for i, item in enumerate(st.session_state['review_pool']):
        st.write(f"{i+1}. [{item['type']}] {item['prompt']}")

# ---------- Real Review Mimicry Section -----------
st.header("📋 Real Review Import")
with st.expander("Paste real reviews here to mimic their structure in future reviews"):
    real_review = st.text_area("Paste a real review here")
    if st.button("Add Real Review Example"):
        st.session_state['real_reviews'].append(real_review)
        st.success("Real review added!")
    if st.session_state['real_reviews']:
        st.write("**Real reviews imported:**")
        for r in st.session_state['real_reviews']:
            st.write(r)

# ----------------- Review Scheduler ---------------
st.header("📆 Schedule a Review for Posting")
if 'scheduled_reviews' not in st.session_state:
    st.session_state['scheduled_reviews'] = []

accounts = st.session_state['accounts']
if not accounts:
    st.info("Create an account first to schedule reviews.")
else:
    acc_usernames = [a['username'] for a in accounts]
    account_sel = st.selectbox("Choose Account", acc_usernames)
    acc = next(a for a in accounts if a['username'] == account_sel)
    default_type = "law_firm_review" if acc.get("case_type") else "non_related_review"
    review_type = st.selectbox("Type of Review", ["law_firm_review", "non_related_review"], index=0 if default_type=="law_firm_review" else 1)
    if review_type == "non_related_review":
        place_type = st.selectbox("Place Type", activity_types)
    else:
        place_type = None

    dt_default = datetime.now() + timedelta(days=1)
    post_datetime = st.datetime_input("Date/time to post this review", dt_default)

    # Pre-select a prompt
    pool_choices = [p for p in st.session_state['review_pool'] if p['type'] == review_type]
    prompt_choice = st.selectbox("Choose a review template", [p['prompt'] for p in pool_choices])
    custom_msg = st.text_area("Add a custom message or details to inject", "")

    # Preview
    preview = prompt_choice.format(
        case_type=acc.get("case_type", ""),
        location=acc.get("location", ""),
        place_type=place_type if place_type else "",
        custom_message=custom_msg
    )
    st.info(f"**Preview:** {preview}")

    if st.button("Schedule This Review"):
        st.session_state['scheduled_reviews'].append({
            "account": account_sel,
            "review_type": review_type,
            "place_type": place_type,
            "datetime": post_datetime.isoformat(),
            "prompt": prompt_choice,
            "custom_message": custom_msg,
            "approved": False,
            "edited_text": preview
        })
        st.success("Review scheduled and awaiting approval.")

# --------------- Approve/Edit All Scheduled Reviews ---------------
st.header("✅ Approve/Edit All Pending Reviews")
pending = [r for r in st.session_state['scheduled_reviews'] if not r['approved']]
if not pending:
    st.info("No pending reviews for approval.")
else:
    approve_all = st.button("Approve All Pending Reviews")
    for idx, review in enumerate(pending):
        st.write(f"**{review['account']} | {review['review_type']} | Scheduled for {review['datetime']}**")
        edited = st.text_area(f"Edit review text for {review['account']}", value=review['edited_text'], key=f"edit_review_{idx}")
        col1, col2 = st.columns(2)
        if col1.button(f"Approve this review", key=f"approve_review_{idx}") or approve_all:
            review['approved'] = True
            review['edited_text'] = edited
            st.success(f"Review approved for {review['account']}")
        if col2.button(f"Delete", key=f"del_review_{idx}"):
            st.session_state['scheduled_reviews'].remove(review)
            st.warning("Review removed.")

# --------------- Posting Logic (Auto-Post When Time Comes) ---------------
now = datetime.now()
for review in st.session_state['scheduled_reviews']:
    if review['approved'] and not review.get("posted", False):
        post_time = datetime.fromisoformat(review['datetime'])
        if now >= post_time:
            # Find account info
            a = next((a for a in accounts if a['username'] == review['account']), None)
            if a:
                st.session_state['activity_log'].append({
                    "timestamp": now.isoformat(),
                    "username": a['username'],
                    "location": a.get("location", ""),
                    "platform": a.get("platform", ""),
                    "activity_type": review['review_type'],
                    "details": review['edited_text']
                })
                review['posted'] = True
                save_json(ACTIVITY_FILE, st.session_state['activity_log'])
                st.success(f"Review for {a['username']} posted!")

# --------------- Show Activity Log ---------------
st.header("📊 Activity Log")
log_df = pd.DataFrame(st.session_state['activity_log'])
if not log_df.empty:
    log_df["timestamp"] = pd.to_datetime(log_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(log_df, use_container_width=True)
else:
    st.info("No activity yet.")

# --------------- Suggestions & Upgrades ---------------
st.header("💡 Suggestions & Upgrades")
st.markdown("""
- Add more review prompts above to diversify reviews.
- Import real reviews for better structure copying.
- Export/import the review pool as JSON for backup/sharing.
- Add filters to log for account, review type, etc.
- Add more activity types or case types as your practice grows.
""")
