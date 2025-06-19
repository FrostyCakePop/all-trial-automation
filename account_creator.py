import streamlit as st, pandas as pd, random, string
from datetime import datetime
from utils_github import load_csv, push_csv

ACCOUNTS_CSV = "accounts.csv"
COLS = ["email","password","platform","location","status",
        "health_score","warming_stage","created_date",
        "daily_emails","safety_score"]

# ---------- UI ----------
st.title("📧 Bulk Account Generator (auto-save)")
df = load_csv(ACCOUNTS_CSV, COLS)
st.metric("Current accounts", len(df))

with st.form("gen"):
    num   = st.slider("How many accounts to create?", 1, 50, 5)
    auto  = st.checkbox("Auto-start warming", True)
    submit= st.form_submit_button("🎯 Generate Accounts")

# ---------- generator ----------
if submit:
    first_names = ["john","jane","lisa","mark","emma","ryan"]
    last_names  = ["smith","lee","brown","davis","miller","wilson"]
    domains     = ["gmail.com","outlook.com","yahoo.com"]
    cities      = ["New York","Los Angeles","Chicago","Houston","Phoenix"]

    new_rows = []
    for _ in range(num):
        fn, ln = random.choice(first_names), random.choice(last_names)
        email  = f"{fn}.{ln}{random.randint(100,999)}@{random.choice(domains)}"
        row = {
            "email": email,
            "password": ''.join(random.choices(string.ascii_letters+string.digits, k=12)),
            "platform": email.split('@')[1].split('.')[0].title(),
            "location": random.choice(cities),
            "status": "active" if auto else "created",
            "health_score": 100,
            "warming_stage": 1,
            "created_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "daily_emails": 0,
            "safety_score": 65
        }
        new_rows.append(row)

    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    push_csv(df, ACCOUNTS_CSV, "auto-update accounts.csv")
    st.success(f"✅  {num} accounts saved permanently!")
    st.balloons()

st.dataframe(df, use_container_width=True)
