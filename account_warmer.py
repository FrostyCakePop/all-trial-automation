import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime, timedelta
import os

# Advanced warming algorithm
def calculate_warming_schedule(account):
    stage = account['warming_stage']
    base_emails = min(2 + (stage * 2), 25)  # Gradual increase
    
    # Randomize daily volume (±20%)
    daily_volume = random.randint(int(base_emails * 0.8), int(base_emails * 1.2))
    
    # Generate realistic send times
    send_times = []
    for _ in range(daily_volume):
        hour = random.choice([9, 10, 11, 14, 15, 16, 17])  # Business hours
        minute = random.randint(0, 59)
        send_times.append(f"{hour:02d}:{minute:02d}")
    
    return {
        "daily_volume": daily_volume,
        "send_times": sorted(send_times),
        "reply_rate": random.randint(15, 35),  # 15-35% reply rate
        "engagement_score": random.randint(70, 95)
    }

def calculate_safety_score(account):
    # Multi-factor safety calculation
    base_score = account['health_score']
    
    # Account age factor
    if 'created_date' in account:
        try:
            created = datetime.strptime(str(account['created_date']), "%Y-%m-%d")
            days_old = (datetime.now() - created).days
            age_bonus = min(days_old * 2, 20)  # Up to 20 points for age
        except:
            age_bonus = 0
    else:
        age_bonus = 0
    
    # Warming stage factor
    stage_bonus = account['warming_stage'] * 3
    
    # Random daily variation (±5)
    daily_variation = random.randint(-5, 5)
    
    final_score = min(100, max(30, base_score + age_bonus + stage_bonus + daily_variation))
    return final_score

# Load accounts
def load_accounts():
    if os.path.exists("accounts.csv"):
        df = pd.read_csv("accounts.csv")
        # Update safety scores
        df['safety_score'] = df.apply(calculate_safety_score, axis=1)
        return df
    else:
        return pd.DataFrame()

# Save accounts
def save_accounts(df):
    df.to_csv("accounts.csv", index=False)

# Main interface
st.set_page_config(page_title="Email Warming Dashboard", page_icon="📧", layout="wide")

# Add PWA support
st.markdown("""
<link rel="manifest" href="manifest.json">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#2196F3">
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js');
}
</script>
""", unsafe_allow_html=True)

# Mobile-responsive CSS
st.markdown("""
<style>
.stButton > button {
    width: 100%;
    height: 3rem;
    font-size: 1.1rem;
    margin: 0.25rem 0;
    border-radius: 0.5rem;
}
@media (max-width: 768px) {
    .css-1d391kg { display: none; }
}
</style>
""", unsafe_allow_html=True)

st.title("📧 Advanced Email Warming Dashboard")

# Load accounts
df = load_accounts()

if len(df) == 0:
    st.warning("⚠️ No accounts found. Please use the Account Generator first.")
    st.stop()

# Dashboard metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Accounts", len(df))

with col2:
    active_accounts = len(df[df['status'] == 'active'])
    st.metric("Active", active_accounts)

with col3:
    avg_health = df['health_score'].mean()
    st.metric("Avg Health", f"{avg_health:.1f}%")

with col4:
    safe_accounts = len(df[df['safety_score'] >= 75])
    st.metric("Review Ready", safe_accounts)

# Emergency controls
st.subheader("🚨 Emergency Controls")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🆘 Emergency Stop All", use_container_width=True):
        df['status'] = 'paused'
        save_accounts(df)
        st.error("All accounts stopped!")
        st.experimental_rerun()

with col2:
    if st.button("▶️ Resume All Warming", use_container_width=True):
        df['status'] = 'active'
        save_accounts(df)
        st.success("All accounts resumed!")
        st.experimental_rerun()

with col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.experimental_rerun()

# Advanced warming controls
st.subheader("⚙️ Warming Management")

if st.button("🚀 Start Advanced Warming Cycle"):
    warming_results = []
    
    for idx, account in df.iterrows():
        if account['status'] == 'active':
            schedule = calculate_warming_schedule(account)
            warming_results.append({
                "email": account['email'],
                "daily_volume": schedule['daily_volume'],
                "send_times": len(schedule['send_times']),
                "reply_rate": schedule['reply_rate']
            })
            
            # Update warming stage
            df.at[idx, 'warming_stage'] = min(account['warming_stage'] + 1, 10)
            df.at[idx, 'daily_emails'] = schedule['daily_volume']
    
    save_accounts(df)
    
    if warming_results:
        st.success(f"🎯 Advanced warming started for {len(warming_results)} accounts!")
        st.dataframe(pd.DataFrame(warming_results))

# Account status display
st.subheader("📊 Account Status")

# Safety score filtering
safety_filter = st.select_slider(
    "Filter by Safety Score",
    options=["All", "High Risk (<60%)", "Medium Risk (60-75%)", "Safe (75-85%)", "Very Safe (>85%)"],
    value="All"
)

# Apply filter
if safety_filter != "All":
    if "High Risk" in safety_filter:
        filtered_df = df[df['safety_score'] < 60]
    elif "Medium Risk" in safety_filter:
        filtered_df = df[(df['safety_score'] >= 60) & (df['safety_score'] < 75)]
    elif "Safe" in safety_filter:
        filtered_df = df[(df['safety_score'] >= 75) & (df['safety_score'] < 85)]
    else:  # Very Safe
        filtered_df = df[df['safety_score'] >= 85]
else:
    filtered_df = df

# Display accounts with color coding
for idx, account in filtered_df.iterrows():
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            # Status emoji
            status_emoji = "🟢" if account['status'] == 'active' else "🔴"
            st.write(f"{status_emoji} **{account['email']}** ({account['platform']})")
            st.write(f"📍 {account['location']}")
        
        with col2:
            st.metric("Health", f"{account['health_score']:.0f}%")
        
        with col3:
            safety_color = "🟢" if account['safety_score'] >= 75 else "🟡" if account['safety_score'] >= 60 else "🔴"
            st.metric("Safety", f"{safety_color} {account['safety_score']:.0f}%")
        
        with col4:
            if account['safety_score'] >= 75:
                st.success("Ready for Reviews")
            elif account['safety_score'] >= 60:
                st.warning("Warming...")
            else:
                st.error("High Risk")
        
        st.divider()

# Account management
st.subheader("🛠️ Account Management")

# Individual account controls
selected_email = st.selectbox("Select Account to Manage", df['email'].tolist())
selected_account = df[df['email'] == selected_email].iloc[0]

col1, col2 = st.columns(2)

with col1:
    new_status = st.selectbox(
        "Change Status", 
        ["active", "paused", "warming", "review_ready"],
        index=["active", "paused", "warming", "review_ready"].index(selected_account['status'])
    )

with col2:
    new_health = st.slider("Adjust Health Score", 0, 100, int(selected_account['health_score']))

if st.button("Update Selected Account"):
    df.loc[df['email'] == selected_email, 'status'] = new_status
    df.loc[df['email'] == selected_email, 'health_score'] = new_health
    save_accounts(df)
    st.success(f"Updated {selected_email}")
    st.experimental_rerun()

# Export functionality
st.subheader("📤 Export Data")
csv_data = df.to_csv(index=False)
st.download_button(
    label="Download Complete Account Data",
    data=csv_data,
    file_name=f"email_accounts_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)
