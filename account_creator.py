import streamlit as st, pandas as pd, random, string, os, io, requests
from datetime import datetime
from github import Github                         #  <-- NEW import

# ---------- constants ----------
COLUMNS = ["email","password","platform","location","status",
           "health_score","warming_stage","created_date",
           "daily_emails","safety_score"]

# ---------- GitHub helper ----------
def push_csv_to_github(df: pd.DataFrame):
    csv_text = df.to_csv(index=False)
    open("accounts.csv", "w", encoding="utf-8").write(csv_text)  # local copy
    g     = Github(st.secrets["GH_TOKEN"])
    repo  = g.get_repo(st.secrets["REPO"])
    path  = st.secrets["CSV_PATH"]
    try:                                 # update if file already exists
        contents = repo.get_contents(path, ref="main")
        repo.update_file(path, "auto-update accounts.csv", csv_text,
                         contents.sha, branch="main")
    except Exception:                    # or create the file first time
        repo.create_file(path, "create accounts.csv",
                         csv_text, branch="main")

# ---------- load on start ----------
@st.cache_data(show_spinner=False)
def load_accounts():
    raw = f"https://raw.githubusercontent.com/{st.secrets['REPO']}/main/{st.secrets['CSV_PATH']}"
    try:
        return pd.read_csv(raw)
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

df = load_accounts()

# ---------- UI ----------
st.title("📧 Bulk Account Generator (auto-save)")
st.metric("Current accounts", len(df))

with st.form("gen"):
    qty = st.slider("How many accounts?", 1, 50, 5)
    auto = st.checkbox("Auto-start warming", True)
    go   = st.form_submit_button("Generate")

if go:
    data = []
    for _ in range(qty):
        first = random.choice(["john","jane","sam","lisa","mark","emma"])
        last  = random.choice(["smith","lee","wilson","brown"])
        num   = random.randint(100,999)
        domain= random.choice(["gmail.com","outlook.com","yahoo.com"])
        email = f"{first}.{last}{num}@{domain}"
        pwd   = ''.join(random.choices(string.ascii_letters+string.digits, k=12))
        data.append({
            "email": email,
            "password": pwd,
            "platform": domain.split('.')[0].title(),
            "location": random.choice(["NY","CA","TX","FL","IL"]),
            "status": "active" if auto else "created",
            "health_score": 100,
            "warming_stage": 1,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "daily_emails": 0,
            "safety_score": 65
        })
    df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    push_csv_to_github(df)                    # <-- auto-save
    st.success(f"Saved {qty} new accounts permanently!")
    st.balloons()

st.dataframe(df, use_container_width=True)
