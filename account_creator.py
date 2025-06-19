import streamlit as st
import pandas as pd
import random
import string
import os
from datetime import datetime

# Generate random email and password
def generate_credentials():
    first_names = ["john", "jane", "mike", "sarah", "david", "emma", "chris", "lisa", "ryan", "anna"]
    last_names = ["smith", "johnson", "wilson", "brown", "davis", "miller", "taylor", "garcia", "martinez", "anderson"]
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    number = random.randint(10, 999)
    
    platforms = ["gmail.com", "outlook.com", "yahoo.com"]
    platform = random.choice(platforms)
    
    email = f"{first}.{last}{number}@{platform}"
    password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$", k=12))
    
    return email, password, platform.split('.')[0].title()

def generate_location():
    locations = [
        "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ",
        "Philadelphia, PA", "San Antonio, TX", "San Diego, CA", "Dallas, TX", "San Jose, CA",
        "Austin, TX", "Jacksonville, FL", "Fort Worth, TX", "Columbus, OH", "Charlotte, NC",
        "San Francisco, CA", "Indianapolis, IN", "Seattle, WA", "Denver, CO", "Washington, DC"
    ]
    return random.choice(locations)

# Load existing accounts or create empty DataFrame
def load_accounts():
    if os.path.exists("accounts.csv"):
        return pd.read_csv("accounts.csv")
    else:
        return pd.DataFrame(columns=[
            "email", "password", "platform", "location", "status", 
            "health_score", "warming_stage", "created_date", "daily_emails", "safety_score"
        ])

# Save accounts to CSV
def save_accounts(df):
    df.to_csv("accounts.csv", index=False)
    return True

# Main Streamlit interface
st.title("🚀 Automated Email Account Generator")
st.markdown("Generate multiple email accounts with automatic CSV persistence")

# Load existing accounts
df = load_accounts()

# Display current account count
st.metric("Total Accounts", len(df))

# Account generation form
with st.form("bulk_generator"):
    st.subheader("Bulk Account Generation")
    num_accounts = st.slider("Number of accounts to generate", 1, 50, 10)
    auto_start_warming = st.checkbox("Auto-start warming for new accounts", value=True)
    
    if st.form_submit_button("🎯 Generate Accounts"):
        new_accounts = []
        
        progress_bar = st.progress(0)
        for i in range(num_accounts):
            email, password, platform = generate_credentials()
            location = generate_location()
            
            new_account = {
                "email": email,
                "password": password,
                "platform": platform,
                "location": location,
                "status": "active" if auto_start_warming else "created",
                "health_score": 100,
                "warming_stage": 1,
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "daily_emails": 0,
                "safety_score": 65
            }
            new_accounts.append(new_account)
            progress_bar.progress((i + 1) / num_accounts)
        
        # Add new accounts to existing DataFrame
        new_df = pd.DataFrame(new_accounts)
        df = pd.concat([df, new_df], ignore_index=True)
        
        # Save to CSV
        if save_accounts(df):
            st.success(f"✅ Successfully generated {num_accounts} accounts!")
            st.balloons()
        else:
            st.error("❌ Failed to save accounts")

# Display accounts table
if len(df) > 0:
    st.subheader("📋 Generated Accounts")
    st.dataframe(
        df[["email", "platform", "location", "status", "health_score", "safety_score"]],
        use_container_width=True
    )
    
    # Download CSV button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Accounts CSV",
        data=csv,
        file_name="email_accounts.csv",
        mime="text/csv"
    )
