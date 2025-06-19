import streamlit as st, pandas as pd, random, string
from datetime import datetime
from utils_github import load_csv, push_csv

CSV = "accounts.csv"
COLS = ["email","password","platform","location","status",
        "health_score","warming_stage","created_date",
        "daily_emails","safety_score"]

df = load_csv(CSV, COLS)
st.title("📧 Bulk Account Generator")
st.metric("Current accounts", len(df))

with st.form("gen"):
    qty  = st.slider("Accounts to create", 1, 50, 5)
    auto = st.checkbox("Auto-start warming", True)
    ok   = st.form_submit_button("Generate")

if ok:
    first = ["john","jane","sam","lisa","mark","emma"]
    last  = ["smith","lee","brown","davis","miller","wilson"]
    dom   = ["gmail.com","outlook.com","yahoo.com"]
    city  = ["NY","LA","Chicago","Houston","Phoenix"]

    new = []
    for _ in range(qty):
        email = f"{random.choice(first)}.{random.choice(last)}{random.randint(100,999)}@{random.choice(dom)}"
        new.append({
            "email": email,
            "password": ''.join(random.choices(string.ascii_letters+string.digits, k=12)),
            "platform": email.split('@')[1].split('.')[0].title(),
            "location": random.choice(city),
            "status": "active" if auto else "created",
            "health_score": 100,
            "warming_stage": 1,
            "created_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "daily_emails": 0,
            "safety_score": 65
        })

    df = pd.concat([df, pd.DataFrame(new)], ignore_index=True)
    push_csv(df, CSV, "auto-update accounts.csv")
    st.success(f"Saved {qty} accounts permanently!")
    st.balloons()

st.dataframe(df, use_container_width=True)
