import streamlit as st
import pandas as pd
import os
import sys

# Add parent directory to path to access app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.evaluation_service import (
    student_exists,
    get_student_academic_records,
    group_by_semester,
    compute_weighted_gpa
)

st.set_page_config(page_title="Student Academic Evaluation", layout="wide")
st.title("📊 Student Academic Evaluation Dashboard")

# --- Input form
with st.form(key="student_search"):
    fullname = st.text_input("Enter full name (e.g. Juan Dela Cruz)", max_chars=50)
    submit = st.form_submit_button("🔍 Search")

if submit:
    if not fullname.strip():
        st.warning("⚠️ Please enter a valid full name.")
    elif not student_exists(fullname):
        st.error("❌ Student not found.")
    else:
        data = get_student_academic_records(fullname)

        if not data:
            st.info("ℹ️ No academic records found.")
        else:
            grouped = group_by_semester(data)

            for (sy, sem), group in grouped:
                gpa, total_units = compute_weighted_gpa(group)

                st.subheader(f"🗓️ {sy} - {sem} Semester")
                st.markdown(f"**GPA**: `{gpa}` &nbsp;&nbsp;&nbsp; **Total Units**: `{total_units}`")

                # Table display
                st.dataframe(group[["SubjectCode", "SubjectDescription", "Units", "Grade", "Teacher"]])

                st.markdown("---")
