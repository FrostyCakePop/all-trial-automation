import pandas as pd, streamlit as st
from github import Github

def _gh_repo():
    return Github(st.secrets["GH_TOKEN"]).get_repo(st.secrets["REPO"])

def push_csv(df: pd.DataFrame, path: str, msg: str):
    """Write CSV to local disk *and* commit to GitHub main branch."""
    csv_text = df.to_csv(index=False)
    with open(path, "w", encoding="utf-8") as f:
        f.write(csv_text)

    repo = _gh_repo()
    try:                                  # update if it exists
        sha = repo.get_contents(path, ref="main").sha
        repo.update_file(path, msg, csv_text, sha, branch="main")
    except Exception:                     # else create new file
        repo.create_file(path, msg, csv_text, branch="main")

def load_csv(path: str, columns: list[str]) -> pd.DataFrame:
    raw = f"https://raw.githubusercontent.com/{st.secrets['REPO']}/main/{path}"
    try:
        return pd.read_csv(raw)
    except Exception:
        return pd.DataFrame(columns=columns)
