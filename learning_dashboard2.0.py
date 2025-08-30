import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

DATA_FILE = "learning_data.json"

# Def functions
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"courses": {}, "streak": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def update_streak(streak):
    today = datetime.today().strftime("%Y-%m-%d")
    streak[today] = 1
    return streak

# Layout of the app
st.set_page_config(page_title="Learning Dashboard", layout="centered")
st.title("Learning Dashboard v2.0")
st.info("Use the sidebar to manage courses and view streaks.")

# Load data
data = load_data()
if "data" not in st.session_state:
    st.session_state.data = data
if "selected_course" not in st.session_state:
    st.session_state.selected_course = None

#The sidebar to add or pick a course
st.sidebar.header("Courses")
with st.sidebar.form("add_course"):
    course_title = st.text_input("Course Title")
    lessons_input = st.text_area("Lessons (one per line)", height=150)
    submit = st.form_submit_button("Add Course")
    if submit and course_title and lessons_input:
        lessons = lessons_input.strip().split("\n")
        st.session_state.data["courses"][course_title] = [
            {"lesson": lesson, "completed": False, "needs_revision": False, "what_learned": ""}
            for lesson in lessons
        ]
        st.session_state.selected_course = course_title
        save_data(st.session_state.data)
        st.rerun()

if st.session_state.data["courses"]:
    st.sidebar.header("Select Course")
    st.session_state.selected_course = st.sidebar.selectbox(
        "Your Courses", list(st.session_state.data["courses"].keys()),
        index=0 if not st.session_state.selected_course else list(st.session_state.data["courses"].keys()).index(st.session_state.selected_course)
    )
    if st.sidebar.button("Archive Course"):
        del st.session_state.data["courses"][st.session_state.selected_course]
        st.session_state.selected_course = None
        save_data(st.session_state.data)
        st.rerun()
    if "show_delete_confirm" not in st.session_state:
        st.session_state.show_delete_confirm = False

    if st.sidebar.button(" Delete Course (Permanent)"):
        st.session_state.show_delete_confirm = True

    if st.session_state.show_delete_confirm:
        st.sidebar.warning("This will permanently delete the selected course and all its lessons.")
        c1, c2 = st.sidebar.columns(2)   # define two side-by-side buttons
        if c1.button("Cancel", key="cancel_delete_course"):
            st.session_state.show_delete_confirm = False
        if c2.button("Yes, delete", key="confirm_delete_course"):
            del st.session_state.data["courses"][st.session_state.selected_course]
            st.session_state.selected_course = None
            st.session_state.show_delete_confirm = False
            save_data(st.session_state.data)
            st.rerun()

# Main View-Course Lessons
if st.session_state.selected_course:
    lessons = st.session_state.data["courses"][st.session_state.selected_course]
    st.header(f"{st.session_state.selected_course}")

    updated = False
    for i, lesson in enumerate(lessons):
        lesson["lesson"] = st.text_input(f"Lesson {i+1} Name", value=lesson["lesson"], key=f"lesson_{i}")
        lesson["completed"] = st.checkbox("Completed", value=lesson["completed"], key=f"comp_{i}")
        lesson["needs_revision"] = st.checkbox("Needs Revision", value=lesson["needs_revision"], key=f"rev_{i}")
        lesson["what_learned"] = st.text_area("What I Learned", value=lesson["what_learned"], key=f"note_{i}")
        updated = True

    if updated:
        save_data(st.session_state.data)

    st.subheader("Summary of Completed Lessons")
    for lesson in lessons:
        if lesson["completed"] and lesson["what_learned"]:
            st.markdown(f"**{lesson['lesson']}**\n\n{lesson['what_learned']}")

    #Progress
    st.subheader("Progress Overview")
    total = len(lessons)
    completed = sum(1 for l in lessons if l["completed"])
    needs_revision = sum(1 for l in lessons if l["needs_revision"])
    progress_score = (completed + 0.5 * needs_revision) / total if total else 0

    st.progress(progress_score)
    st.markdown(f"**{completed}/{total} lessons completed** (+{needs_revision} needing revision)")

    fig, ax = plt.subplots()
    ax.pie([
        completed,
        needs_revision,
        total - completed - needs_revision
    ], labels=["Completed", "Needs Revision", "Remaining"], autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # Export stuff
    st.subheader("Export Progress")
    df = pd.DataFrame(lessons)
    df.insert(0, "Course", st.session_state.selected_course)
    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, "learning_progress.csv", "text/csv")

else:
    st.info("Start by adding and selecting a course from the sidebar.")
