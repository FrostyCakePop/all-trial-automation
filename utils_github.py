import pandas as pd, streamlit as st
from github import Github

def _repo():
    return Github(st.secrets["GH_TOKEN"]).get_repo(st.secrets["REPO"])

def push_csv(df: pd.DataFrame, path: str, msg: str):
    csv = df.to_csv(index=False)
    open(path, "w", encoding="utf-8").write(csv)
    repo = _repo()
    try:
        sha = repo.get_contents(path, ref="main").sha
        repo.update_file(path, msg, csv, sha, branch="main")
    except Exception:
        repo.create_file(path, msg, csv, branch="main")

def load_csv(path: str, columns: list[str]) -> pd.DataFrame:
    raw = f"https://raw.githubusercontent.com/{st.secrets['REPO']}/main/{path}"
    try:
        return pd.read_csv(raw)
    except Exception:
        return pd.DataFrame(columns=columns)
