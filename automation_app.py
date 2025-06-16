# automation_app.py
import streamlit as st
import pandas as pd
import random
import time
from faker import Faker
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# Initialize Faker for fake data generation
fake = Faker()

# ======================
# CORE CONFIGURATION
# ======================
STAFF_DISTRIBUTION = {
    "Yareem": 0.45,
    "Kendra": 0.20,
    "Reina": 0.35
}

MO_MENTION_PROBABILITY = 0.85  # 85% chance to mention Mo
CASE_TYPES = ["CPS Defense", "Criminal Defense", "Personal Injury"]

# ======================
# REVIEW GENERATION ENGINE
# ======================
class ReviewGenerator:
    def __init__(self):
        self.templates = [
            "After my {case_type} case in {location}, {attorney} helped me {outcome}. "
            "Special thanks to {staff} for {action}.",
            "I consulted {attorney} about {case_type}. {staff} was crucial in helping with {action}. "
            "Highly recommend!",
        ]
        
        self.actions = {
            "Yareem": ["organizing paperwork", "scheduling appointments", "client intake"],
            "Kendra": ["case updates", "evidence collection", "court reminders"],
            "Reina": ["payment plans", "insurance paperwork", "billing questions"]
        }

    def generate_review(self, location):
        # Randomly decide if Mo is mentioned
        mention_mo = random.random() < MO_MENTION_PROBABILITY
        attorney = "Attorney Mo" if mention_mo else "the legal team"
        
        # Staff mention
        staff = random.choices(
            list(STAFF_DISTRIBUTION.keys()),
            weights=list(STAFF_DISTRIBUTION.values()),
            k=1
        )[0]
        
        return random.choice(self.templates).format(
            case_type=random.choice(CASE_TYPES),
            location=location,
            attorney=attorney,
            staff=staff,
            action=random.choice(self.actions[staff]),
            outcome=random.choice(["resolve the matter", "protect my rights", "secure compensation"])
        )

# ======================
# ACCOUNT MANAGER
# ======================
class AccountManager:
    def __init__(self):
        self.accounts = []
        
    def create_google_account(self):
        driver = uc.Chrome()
        try:
            driver.get("https://accounts.google.com/signup")
            
            # Fill form with fake data
            first_name = fake.first_name()
            last_name = fake.last_name()
            
            driver.find_element(By.NAME, "firstName").send_keys(first_name)
            driver.find_element(By.NAME, "lastName").send_keys(last_name)
            
            # ... continue with account creation steps
            # (you'll need to manually solve CAPTCHA here)
            
            return {
                "email": f"{first_name}{last_name}{random.randint(100,999)}@proton.me",
                "password": fake.password(length=12),
                "platform": "Google"
            }
        finally:
            driver.quit()

# ======================
# STREAMLIT APP INTERFACE
# ======================
def main():
    st.title("ALL Trial Lawyers Review Automation")
    
    # Initialize session state
    if 'accounts' not in st.session_state:
        st.session_state.accounts = []
    
    # Sidebar controls
    with st.sidebar:
        st.header("Configuration")
        num_accounts = st.number_input("Accounts to create", 1, 10, 3)
        
        if st.button("💾 Generate Accounts"):
            manager = AccountManager()
            for _ in range(num_accounts):
                account = manager.create_google_account()
                st.session_state.accounts.append(account)
            st.success(f"Created {num_accounts} new accounts!")
            
    # Main interface
    tab1, tab2 = st.tabs(["📋 Account Manager", "📝 Review Generator"])
    
    with tab1:
        st.dataframe(pd.DataFrame(st.session_state.accounts))
        
    with tab2:
        location = st.selectbox("Select Location", [
            "Riverside", "La Jolla", "LA", "Diamond Bar"
        ])
        
        if st.button("Generate Review"):
            review = ReviewGenerator().generate_review(location)
            st.write(review)
            st.code("This review would be posted to: " + 
                   "https://g.co/kgs/UcVnXi8" if location == "Riverside" else "")

if __name__ == "__main__":
    main()
