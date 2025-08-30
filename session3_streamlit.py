import streamlit as st
# Set page configuration as the first Streamlit command
st.set_page_config(page_title="University Interactive Dashboard", layout="wide")

import pandas as pd
import numpy as np
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pymongo import ReadPreference
import bson
from bson.regex import Regex
import os
import sys
import time
import io
import base64
from datetime import datetime

# Add parent directory to path to access config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import Config

# Custom CSS for styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1E3A8A;
    text-align: center;
    margin-bottom: 1rem;
}
.dashboard-container {
    background-color: #EFF6FF;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
}
.sidebar-header {
    font-size: 1.2rem;
    font-weight: bold;
    color: #1E3A8A;
    margin-bottom: 1rem;
}
.stButton>button {
    background-color: #3B82F6;
    color: white;
    border-radius: 5px;
    padding: 0.5rem 1rem;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">🏫 University Interactive Dashboard</div>', unsafe_allow_html=True)

# Singleton pattern for MongoDB client
_mongo_client = None

# MongoDB connection function
def get_mongo_client():
    """
    Creates a MongoDB client with optimized settings for distributed systems.
    Uses singleton pattern to reuse connection across different parts of the application.
    
    Features:
    - Connection pooling with 25 connections
    - Read preference set to SECONDARY_PREFERRED for load distribution
    - Retry logic for better resilience
    - Network compression for large datasets
    - Increased timeout settings
    """
    global _mongo_client
    
    # Return existing client if already initialized
    if _mongo_client is not None:
        return _mongo_client
    
    # Maximum retry attempts
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            # Create client with optimized settings for distributed systems
            # Modify connection URI to include read preference
            mongo_uri = Config.MONGO_URI
            if '?' not in mongo_uri:
                mongo_uri += '?readPreference=secondaryPreferred'
            else:
                mongo_uri += '&readPreference=secondaryPreferred'
                
            client = MongoClient(
                mongo_uri,
                maxPoolSize=25,  # Increased connection pool
                socketTimeoutMS=60000,  # 60 seconds socket timeout
                connectTimeoutMS=30000,  # 30 seconds connect timeout
                serverSelectionTimeoutMS=30000,  # 30 seconds server selection timeout
                retryWrites=True,  # Enable retry for write operations
                retryReads=True,   # Enable retry for read operations
                readConcernLevel="majority",  # Ensure consistency across replica set
                zlibCompressionLevel=9  # Enable network compression
            )
            
            # Verify connection is working
            client.admin.command('ping')
            
            # Store client in global variable for reuse
            _mongo_client = client
            return client
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            if attempt < max_retries - 1:
                st.warning(f"MongoDB connection attempt {attempt + 1} failed. Retrying...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                st.error(f"Failed to connect to MongoDB after {max_retries} attempts: {str(e)}")
                return None
        except Exception as e:
            st.error(f"MongoDB Connection Error: {str(e)}")
            return None

# Helper functions for data retrieval and processing
def get_all_students():
    """Get list of all students for dropdown"""
    client = get_mongo_client()
    if not client:
        return []
    
    students = client.mit261.students
    try:
        return list(students.find({}, {"Name": 1, "_id": 1, "Course": 1, "YearLevel": 1}).sort("Name", 1))
    except Exception as e:
        st.error(f"Error retrieving students: {str(e)}")
        return []

def get_all_semesters():
    """Get list of all semesters for dropdown"""
    client = get_mongo_client()
    if not client:
        return []
    
    semesters = client.mit261.semesters
    try:
        return list(semesters.find({}).sort("SchoolYear", 1))
    except Exception as e:
        st.error(f"Error retrieving semesters: {str(e)}")
        return []

def get_all_subjects():
    """Get list of all subjects for dropdown"""
    client = get_mongo_client()
    if not client:
        return []
    
    subjects = client.mit261.subjects
    try:
        return list(subjects.find({}).sort("_id", 1))
    except Exception as e:
        st.error(f"Error retrieving subjects: {str(e)}")
        return []

def student_exists(fullname):
    """Check if student exists in database"""
    client = get_mongo_client()
    if not client:
        return None
    
    try:
        db = client[Config.MONGO_DB]
        # Case-insensitive search for student name
        student = db.students.find_one({"Name": {"$regex": fullname, "$options": "i"}})
        return student
    except Exception as e:
        st.error(f"Error searching for student: {str(e)}")
        return None

def get_student_by_id(student_id):
    """Get student by ID"""
    client = get_mongo_client()
    if not client:
        return None
    
    students = client.mit261.students
    try:
        # Convert to int if it's a string
        if isinstance(student_id, str) and student_id.isdigit():
            student_id = int(student_id)
        return students.find_one({"_id": student_id})
    except Exception as e:
        st.error(f"Error retrieving student: {str(e)}")
        return None

def get_student_academic_records(student_id=None, semester_id=None, subject_code=None):
    """Get student academic records with optional filters"""
    client = get_mongo_client()
    if not client:
        return []
    
    db = client.mit261
    grades = db.grades
    
    # Build match criteria
    match_criteria = {}
    if student_id is not None:
        # Convert to int if it's a string
        if isinstance(student_id, str) and student_id.isdigit():
            student_id = int(student_id)
        match_criteria["StudentID"] = student_id
    
    if semester_id is not None:
        # Convert to int if it's a string
        if isinstance(semester_id, str) and semester_id.isdigit():
            semester_id = int(semester_id)
        match_criteria["SemesterID"] = semester_id
    
    if subject_code is not None and subject_code != "All Subjects":
        match_criteria["SubjectCodes"] = subject_code
    
    # Early filtering with $match for better performance
    pipeline = [
        {"$match": match_criteria},
        {"$unwind": {"path": "$SubjectCodes", "includeArrayIndex": "idx"}},
        {"$project": {
            "StudentID": 1,
            "SemesterID": 1,
            "SubjectCode": "$SubjectCodes",
            "Grade": {"$arrayElemAt": ["$Grades", "$idx"]},
            "Teacher": {"$arrayElemAt": ["$Teachers", "$idx"]}
        }}
    ]
    
    # Filter by subject code after unwinding if needed
    if subject_code is not None and subject_code != "All Subjects":
        pipeline.append({"$match": {"SubjectCode": subject_code}})
    
    # Continue with lookups and projections
    pipeline.extend([
        {"$lookup": {
            "from": "students",
            "localField": "StudentID",
            "foreignField": "_id",
            "as": "student_info"
        }},
        {"$unwind": "$student_info"},
        {"$lookup": {
            "from": "semesters",
            "localField": "SemesterID",
            "foreignField": "_id",
            "as": "sem_info"
        }},
        {"$unwind": "$sem_info"},
        {"$lookup": {
            "from": "subjects",
            "localField": "SubjectCode",
            "foreignField": "_id",  # Using _id as subject code based on memory
            "as": "subj_info"
        }},
        {"$unwind": {"path": "$subj_info", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "StudentID": 1,
            "StudentName": "$student_info.Name",
            "Course": "$student_info.Course",
            "YearLevel": "$student_info.YearLevel",
            "SchoolYear": "$sem_info.SchoolYear",
            "Semester": "$sem_info.Semester",
            "SemesterID": 1,
            "SubjectCode": 1,
            "SubjectDescription": "$subj_info.Description",
            "Units": "$subj_info.Units",
            "Grade": 1,
            "Teacher": 1
        }},
        {"$sort": {"StudentName": 1, "SchoolYear": 1, "Semester": 1, "SubjectCode": 1}}
    ])

    try:
        return list(grades.aggregate(pipeline, allowDiskUse=True))
    except Exception as e:
        st.error(f"Error retrieving records: {str(e)}")
        return []

def group_by_semester(data):
    """Group records by semester"""
    df = pd.DataFrame(data)
    if df.empty:
        return []

    grouped = df.groupby(["SchoolYear", "Semester"])
    return [((sy, sem), group) for (sy, sem), group in grouped]

def compute_weighted_gpa(group):
    """Compute weighted GPA"""
    group = group.dropna(subset=["Grade", "Units"])
    group["Weighted"] = group["Grade"] * group["Units"]
    total_units = group["Units"].sum()
    total_weighted = group["Weighted"].sum()
    gpa = total_weighted / total_units if total_units else 0
    return round(gpa, 2), total_units

def calculate_kpi_metrics(data):
    """Calculate KPI metrics for dashboard"""
    df = pd.DataFrame(data)
    if df.empty:
        return {
            "total_students": 0,
            "total_subjects": 0,
            "avg_gpa": 0,
            "above_gpa": 0,
            "below_gpa": 0,
            "passing_rate": 0,
            "highest_grade": 0,
            "lowest_grade": 0
        }
    
    # Calculate student-level metrics
    unique_students = df["StudentID"].nunique()
    unique_subjects = df["SubjectCode"].nunique()
    
    # Calculate GPA metrics
    df["Weighted"] = df["Grade"] * df["Units"]
    student_gpas = df.groupby("StudentID").apply(
        lambda x: x["Weighted"].sum() / x["Units"].sum() if x["Units"].sum() > 0 else 0
    )
    
    avg_gpa = student_gpas.mean() if not student_gpas.empty else 0
    threshold_gpa = 75  # Passing grade threshold
    
    above_gpa = (student_gpas >= threshold_gpa).sum()
    below_gpa = (student_gpas < threshold_gpa).sum()
    passing_rate = (above_gpa / unique_students * 100) if unique_students > 0 else 0
    
    # Grade range
    highest_grade = df["Grade"].max() if not df.empty else 0
    lowest_grade = df["Grade"].min() if not df.empty else 0
    
    return {
        "total_students": unique_students,
        "total_subjects": unique_subjects,
        "avg_gpa": round(avg_gpa, 2),
        "above_gpa": above_gpa,
        "below_gpa": below_gpa,
        "passing_rate": round(passing_rate, 2),
        "highest_grade": highest_grade,
        "lowest_grade": lowest_grade
    }

def get_grade_distribution_data(data):
    """Get grade distribution data for Streamlit charts"""
    grades = []
    for record in data:
        for grade in record.get("Grades", []):
            if isinstance(grade, dict) and "$numberInt" in grade:
                grades.append(int(grade["$numberInt"]))
            elif isinstance(grade, int):
                grades.append(grade)
            elif isinstance(grade, str) and grade.isdigit():
                grades.append(int(grade))
    
    if not grades:
        return None
    
    # Create bins for grades
    bins = [0, 50, 60, 70, 75, 80, 90, 100]
    labels = ['0-50', '51-60', '61-70', '71-75', '76-80', '81-90', '91-100']
    
    # Count grades in each bin
    hist, _ = np.histogram(grades, bins=bins)
    
    # Create DataFrame for Streamlit chart
    chart_data = pd.DataFrame({
        'Grade Range': labels,
        'Count': hist
    })
    
    return chart_data

# PDF generation functionality has been removed as it's optional for this activity

# Main app interface
st.sidebar.markdown('<div class="sidebar-header">📊 Dashboard Menu</div>', unsafe_allow_html=True)

# Module selection in sidebar
st.sidebar.markdown("**Select a Module:**")
module_options = ["Home", "Registrar", "Teacher", "Students"]
selected_module = st.sidebar.radio("", module_options, index=3, label_visibility="collapsed")

# Student options submenu (only shown when Students module is selected)
if selected_module == "Students":
    st.sidebar.markdown("**Select Student Option:**")
    student_options_menu = ["Grade Sheet", "Evaluation Sheet"]
    selected_student_option = st.sidebar.radio("", student_options_menu, index=1, label_visibility="collapsed")

# Initialize session state for filters
if 'selected_student' not in st.session_state:
    st.session_state.selected_student = None
if 'selected_semester' not in st.session_state:
    st.session_state.selected_semester = None
if 'selected_subject' not in st.session_state:
    st.session_state.selected_subject = None
if 'data' not in st.session_state:
    st.session_state.data = []

# Load filter options
students = get_all_students()
student_options = [(str(s["_id"]), s["Name"]) for s in students]

semesters = get_all_semesters()
semester_options = [(str(s["_id"]), f"{s['SchoolYear']} - {s['Semester']}") for s in semesters]

subjects = get_all_subjects()
subject_options = [(s["_id"], f"{s['_id']} - {s['Description']}") for s in subjects]

# Main content area - Student Module
if selected_module == "Students" and selected_student_option == "Evaluation Sheet":
    st.markdown("### 🎓 Students Module")
    
    # Create a form for student search
    st.markdown("## 📝 Student Evaluation Sheet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Last Name**")
        last_name = st.text_input("Last Name", placeholder="Carlos", key="last_name", label_visibility="collapsed")
    
    with col2:
        st.markdown("**First Name**")
        first_name = st.text_input("First Name", placeholder="Ester", key="first_name", label_visibility="collapsed")
    
    st.markdown("**Middle Initial (optional)**")
    middle_initial = st.text_input("Middle Initial", placeholder="O", key="middle_initial", label_visibility="collapsed")
    
    # Add search button
    search_button = st.button("🔍 Search Student", key="search_button")
    
    # Process student search
    if search_button:
        # Combine name parts for search
        full_name = f"{last_name}, {first_name}"
        if middle_initial:
            full_name += f" {middle_initial}."
            
        # Find student
        student = student_exists(full_name)
        
        if student:
            st.session_state.selected_student = str(student["_id"])
            
            # Get student data
            data = get_student_academic_records(student_id=student["_id"])
            st.session_state.data = data
        else:
            st.error("❌ Student not found.")
            st.session_state.data = []

# Display data and visualizations
if st.session_state.data:
    data = st.session_state.data
    
    # KPI metrics
    metrics = calculate_kpi_metrics(data)
    
    # KPI cards in columns
    st.subheader("📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", metrics["total_students"])
    with col2:
        st.metric("Average GPA", metrics["avg_gpa"])
    with col3:
        st.metric("Above Passing", metrics["above_gpa"])
    with col4:
        st.metric("Below Passing", metrics["below_gpa"])
    
    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Subjects", metrics["total_subjects"])
    with col2:
        st.metric("Passing Rate", f"{metrics['passing_rate']}%")
    with col3:
        st.metric("Highest Grade", metrics["highest_grade"])
    with col4:
        st.metric("Lowest Grade", metrics["lowest_grade"])
    
    # Visualizations
    # Get grade distribution data
    chart_data = get_grade_distribution_data(data)
    
    if chart_data is not None:
        st.subheader("📊 Grade Distribution")
        st.bar_chart(chart_data.set_index('Grade Range'))
    
    # Data table
    st.subheader("📋 Academic Records")
    
    # If a single student is selected, show their name
    if st.session_state.selected_student and st.session_state.selected_student != "all":
        student = get_student_by_id(st.session_state.selected_student)
        if student:
            st.markdown(f"**Student:** {student['Name']} | **Course:** {student['Course']} | **Year Level:** {student['YearLevel']}")
            
            # PDF generation functionality has been removed as it's optional for this activity
    
    # Group by semester if no specific semester is selected
    if st.session_state.selected_semester == "all" or st.session_state.selected_semester is None:
        grouped = group_by_semester(data)
        
        for (sy, sem), group in grouped:
            gpa, total_units = compute_weighted_gpa(group)
            
            st.markdown(f"### 🗓️ {sy} - {sem} Semester")
            st.markdown(f"**GPA**: `{gpa}` | **Total Units**: `{total_units}`")
            
            # Table display
            st.dataframe(
                group[["StudentName", "Course", "SubjectCode", "SubjectDescription", "Units", "Grade", "Teacher"]],
                use_container_width=True
            )
            
            st.markdown("---")
    else:
        # Show all data in a single table
        df = pd.DataFrame(data)
        st.dataframe(
            df[["StudentName", "Course", "SubjectCode", "SubjectDescription", "Units", "Grade", "Teacher"]],
            use_container_width=True
        )

else:
    st.info("👈 Please select filters and click 'Apply Filters' to view data")

# Footer
st.markdown("---")
st.caption("MIT-261 Student Academic Evaluation | Session 3 - Distributed Data Processing and Visualization with MongoDB and Streamlit")
