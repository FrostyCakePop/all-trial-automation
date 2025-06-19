import streamlit as st, pandas as pd, random
from datetime import datetime
from utils_github import load_csv, push_csv

ACCOUNTS = "accounts.csv"
LOG      = "activity_log.csv"

ACOLS = ["email","password","platform","location","status",
         "health_score","warming_stage","created_date",
         "daily_emails","safety_score"]
LCOLS = ["timestamp","email","action","details"]

df  = load_csv(ACCOUNTS, ACOLS)
log = load_csv(LOG, LCOLS)

def log_event(email, action, details=""):
    global log
    log = log.append(
        {"timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
         "email": email, "action": action, "details": details},
        ignore_index=True
    )
    push_csv(log, LOG, "auto-update activity")

def schedule(stage):
    base = min(2+stage*2, 25)
    vol  = random.randint(int(base*0.8), int(base*1.2))
    hrs  = sorted(random.sample(range(9,18), k=min(vol,9)))
    return vol, hrs

def safety(row):
    age = (datetime.utcnow() - datetime.strptime(row["created_date"], "%Y-%m-%d")).days
    return max(30, min(100, row["health_score"] + age//2 + row["warming_stage"]*3 + random.randint(-5,5)))

st.title("📈 Warming Dashboard")

if df.empty:
    st.warning("Generate accounts first.")
    st.stop()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Total", len(df))
c2.metric("Active", len(df[df.status=="active"]))
c3.metric("Avg health", f"{df.health_score.mean():.1f}%")
c4.metric("Ready", len(df[df.safety_score>=75]))

if st.button("🚀 Start Advanced Warming"):
    for i,row in df.iterrows():
        if row.status!="active": continue
        daily,times = schedule(row.warming_stage)
        df.at[i,"daily_emails"]  = daily
        df.at[i,"warming_stage"] = min(row.warming_stage+1,10)
        df.at[i,"safety_score"]  = safety(df.loc[i])
        log_event(row.email,"warm_schedule",f"daily={daily} hrs={times}")
    push_csv(df, ACCOUNTS, "auto-update accounts.csv")
    st.success("Warming scheduled!")

st.dataframe(df[["email","status","health_score","safety_score","daily_emails"]],
             use_container_width=True)
