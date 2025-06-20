import streamlit as st
import json
import os
import random

TEMPLATE_FILE = "activity_templates.json"

def load_templates():
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r") as f:
            return json.load(f)
    else:
        # Default templates if file doesn't exist
        return [
            "Commented on a {topic} post in {location}",
            "Liked a {topic} article in {location}",
            "Shared a news update about {topic} in {location}",
            "Followed a user interested in {topic} in {location}",
            "Replied to a general discussion on {topic} in {location}"
        ]

def save_templates(templates):
    with open(TEMPLATE_FILE, "w") as f:
        json.dump(templates, f, indent=2)

def generate_neutral_activity(location, topic="general"):
    templates = load_templates()
    if not templates:
        return "No templates available."
    template = random.choice(templates)
    return template.format(topic=topic, location=location)

# --- Streamlit UI ---

st.title("Activity Template Manager & Generator")

st.header("📝 Manage Activity Templates")
templates = load_templates()
edited_templates = st.text_area(
    "Edit your activity templates (one per line):",
    value="\n".join(templates),
    height=150
)

col1, col2 = st.columns(2)
with col1:
    if st.button("Save Templates"):
        new_templates = [line.strip() for line in edited_templates.splitlines() if line.strip()]
        save_templates(new_templates)
        st.success("Templates saved! (This will be reflected in future activities.)")
with col2:
    if st.button("Reset to Defaults"):
        defaults = [
            "Commented on a {topic} post in {location}",
            "Liked a {topic} article in {location}",
            "Shared a news update about {topic} in {location}",
            "Followed a user interested in {topic} in {location}",
            "Replied to a general discussion on {topic} in {location}"
        ]
        save_templates(defaults)
        st.success("Templates reset to default values.")

st.divider()

st.header("🤖 Preview Neutral Activity Generation")

demo_locations = ["Dallas", "Chicago", "San Francisco", "London"]
demo_topics = ["sports", "travel", "technology", "music", "food"]

location = st.selectbox("Pick a location", demo_locations)
topic = st.selectbox("Pick a topic", demo_topics)

if st.button("Generate Example Activity"):
    activity = generate_neutral_activity(location, topic)
    st.info(f"Example activity: {activity}")

st.markdown("""
---
**How this works:**  
- Activity templates are saved in a file called `activity_templates.json`.  
- Edit/add templates above. Use `{topic}` and `{location}` as variables in your templates.  
- The generator picks a random template and fills in the chosen topic/location.
""")

st.markdown("""
---
**Suggestions for upgrades:**  
- Add “Download Templates” and “Upload Templates” buttons for backup/sharing.  
- Tag templates (e.g., comment, like, share) for more advanced simulation.  
- Add a “Test All” button to preview every template at once.  
- Support multi-language or region-specific templates.
""")
