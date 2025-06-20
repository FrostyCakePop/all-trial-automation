import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# --- Streamlit secrets setup ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

# --- Session state setup ---
if 'scraped_reviews' not in st.session_state:
    st.session_state['scraped_reviews'] = []
if 'avoid_list' not in st.session_state:
    st.session_state['avoid_list'] = []
if 'review_pool' not in st.session_state:
    st.session_state['review_pool'] = [
        "All Trial Lawyers handled my {case_type} case. {extra}",
        "Visited {place_type} in {location}; great experience. {extra}"
    ]

# --- Helper: Store scraped reviews ---
def add_scraped_reviews(reviews):
    st.session_state['scraped_reviews'].extend(reviews)
    st.success(f"Added {len(reviews)} reviews to the pool!")

# --- Helper: Scrape reviews from URL ---
def scrape_reviews_from_url(url):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        reviews = []
        for tag in soup.find_all(['p', 'span']):
            txt = tag.get_text().strip()
            if 50 < len(txt) < 500:
                reviews.append(txt)
        reviews = list(set(reviews))
        return reviews[:10]
    except Exception as e:
        return [f"Scraping error: {e}"]

# --- Helper: AI review generation ---
def ai_generate_review(prompt, avoid_list=None):
    avoid_text = ""
    if avoid_list:
        avoid_text = " Avoid these topics/words: " + ", ".join(avoid_list)
    try:
        messages = [
            {"role": "system", "content": "You are a skilled writer of realistic, unique online reviews. Never repeat yourself. Do not mention forbidden topics."},
            {"role": "user", "content": prompt + avoid_text}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.85,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"AI error: {e}"

# --- Helper: Explanations ---
def show_explanation(text):
    st.info(text)

# --- UI: Things to Avoid ---
st.header("🚫 Add Topics/Words to Avoid in Reviews")
with st.expander("What is this?"):
    show_explanation("Type any words or topics you want the AI and manual review writers to avoid (e.g., 'illegal', 'guarantee', 'specific dollar amounts'). This helps keep reviews compliant and natural.")
avoid_input = st.text_input("Add topic/word to avoid")
if st.button("Add to avoid list"):
    st.session_state['avoid_list'].append(avoid_input.strip())
    st.success("Added.")
if st.session_state['avoid_list']:
    st.write("**Current avoid list:**", ", ".join(st.session_state['avoid_list']))

# --- UI: Scrape and Store Reviews ---
st.header("🌎 Scrape Reviews from URLs")
with st.expander("How does this work?"):
    show_explanation("Paste URLs of real law firm or business reviews here (one per line). The app will try to extract review-like text and store it, so you can use it as inspiration for future reviews.")
urls = st.text_area("Paste URLs (one per line)")
if st.button("Scrape Reviews"):
    all_scraped = []
    for url in urls.splitlines():
        url = url.strip()
        if url:
            scraped = scrape_reviews_from_url(url)
            add_scraped_reviews(scraped)
            all_scraped.extend(scraped)
    if all_scraped:
        st.write("**Sample scraped reviews:**")
        for r in all_scraped:
            st.write("- " + r)
    else:
        st.warning("No reviews found at those URLs.")

# --- UI: Review Pool (Editable) ---
st.header("📝 Review Pool (Templates and Real Reviews)")
with st.expander("Why use a review pool?"):
    show_explanation("Your pool should contain both generic templates and real review snippets to help AI generate new, unique reviews. Edit below and click 'Save'.")
review_pool_edit = st.text_area("Edit review pool (one per line)", value="\n".join(st.session_state['review_pool'] + st.session_state['scraped_reviews']))
if st.button("Save Review Pool"):
    st.session_state['review_pool'] = [line for line in review_pool_edit.split("\n") if line.strip()]
    st.success("Review pool updated!")

# --- UI: Generate AI Review with Safety Checks ---
st.header("🤖 AI-Generated Reviews (with Safety Checks)")
with st.expander("Upgrade suggestions"):
    show_explanation("Use the AI button to generate safe, unique reviews based on your pool and forbidden topics. For best results, keep your avoid list up to date and regularly add fresh real reviews.")
prompt = st.selectbox("Choose prompt/template", st.session_state['review_pool'])
extra = st.text_input("Add custom details (optional)", "")
ai_review = ""
if st.button("Generate with AI"):
    ai_prompt = prompt.replace("{extra}", extra)
    ai_review = ai_generate_review(ai_prompt, avoid_list=st.session_state['avoid_list'])
    st.text_area("AI Review", value=ai_review, height=150)

# --- UI: Upgrade Suggestions ---
st.header("🚀 Upgrade Suggestions & Explanations")
st.markdown("""
- **Always keep review pool fresh:** Regularly add new templates and real reviews.
- **Be strict with avoid list:** This helps reduce risk and keeps reviews compliant.
- **Color code safety:** Use green/yellow/red badges in your main dashboard for account/review safety.
- **Explain every feature:** Keep "?" buttons on all sections for team onboarding.
- **Allow export/import:** Back up your review pool and avoid list as JSON.
""")
