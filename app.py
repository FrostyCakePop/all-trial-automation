import streamlit as st
import random

# --- Helper data ---
PLATFORMS = ["Gmail", "Outlook", "Yahoo"]
LOCATIONS = ["New York", "Los Angeles", "Chicago", "Dallas", "Miami"]

# --- Session State for accounts ---
if 'accounts' not in st.session_state:
    st.session_state['accounts'] = []

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

st.title("All Trial Automation")

st.header("Create Account")
if st.button("Create Random Account"):
    account = generate_random_account()
    st.session_state['accounts'].append(account)
    st.success(f"Created: {account['username']} on {account['platform']} ({account['location']})")

st.header("Account List")
if st.session_state['accounts']:
    st.table(st.session_state['accounts'])
else:
    st.info("No accounts yet. Click above to create one!")
