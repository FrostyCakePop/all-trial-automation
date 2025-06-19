import streamlit as st, pandas as pd, random
from datetime import datetime
from utils_github import load_csv, push_csv

ACCT_CSV = "accounts.csv"
LOG_CSV  = "activity_log.csv"

ACCT_COL = ["email","password","platform","location","status",
            "health_score","warming_stage","created_date",
            "daily_emails","safety_score"]
LOG_COL  = ["timestamp","email","action","details"]

# ---------- helpers ----------
def log_event(email:str, action:str, details:str=""):
    global log_df
    log_df = log_df.append({
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "email": email,
        "action": action,
        "details": details
    }, ignore_index=True)
    push_csv(log_df, LOG_CSV, "auto-update activity_log.csv")

def calc_schedule(stage:int):
    base = min(2 + stage*2, 25)
    daily = random.randint(int(base*0.8), int(base*1.2))
    times = sorted(random.sample(range(9,18), k=min(daily,9)))
    return daily, times

def calc_safety(row):
    age = (datetime.utcnow() - datetime.strptime(row["created_date"], "%Y-%m-%d")).days
    return max(30, min(100, row["health_score"] + age//2 + row["warming_stage"]*3 + random.randint(-5,5)))

# ---------- load data ----------
df      = load_csv(ACCT_CSV, ACCT_COL)
log_df  = load_csv(LOG_CSV,  LOG_COL)

st.title("📈 Warming Dashboard")

if df.empty:
    st.warning("No accounts yet ‑ visit *Account Generator*.")
    st.stop()

# ---------- metrics ----------
col1,col2,col3,col4 = st.columns(4)
col1.metric("Accounts", len(df))
col2.metric("Active", len(df[df.status=="active"]))
col3.metric("Avg Health", f"{df.health_score.mean():.1f}%")
col4.metric("Ready (≥75)", len(df[df.safety_score>=75]))

# ---------- start warming ----------
if st.button("🚀 Start Advanced Warming"):
    for idx,row in df.iterrows():
        if row["status"]!="active": continue
        daily,times = calc_schedule(row["warming_stage"])
        df.at[idx,"daily_emails"]  = daily
        df.at[idx,"warming_stage"] = min(row["warming_stage"]+1,10)
        df.at[idx,"safety_score"]  = calc_safety(df.loc[idx])
        log_event(row["email"], "warm_schedule", f"daily={daily} times={times}")
    push_csv(df, ACCT_CSV, "auto-update accounts.csv")
    st.success("Warming cycle scheduled!")

# ---------- table ----------
st.dataframe(df[["email","status","health_score","safety_score","daily_emails"]],
             use_container_width=True)
