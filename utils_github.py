import pandas as pd, os, io, streamlit as st
from datetime import datetime
from github import Github

def push_csv(df: pd.DataFrame, path: str):
    csv_text = df.to_csv(index=False)
    open(path, "w", encoding="utf-8").write(csv_text)           # local copy
    g     = Github(st.secrets["GH_TOKEN"])
    repo  = g.get_repo(st.secrets["REPO"])
    try:
        contents = repo.get_contents(path, ref="main")
        repo.update_file(path, f"auto-update {path}", csv_text,
                         contents.sha, branch="main")
    except Exception:
        repo.create_file(path, f"create {path}", csv_text, branch="main")

def load_csv(path: str, columns: list[str]) -> pd.DataFrame:
    raw = f"https://raw.githubusercontent.com/{st.secrets['REPO']}/main/{path}"
    try:
        return pd.read_csv(raw)
    except Exception:
        return pd.DataFrame(columns=columns)
