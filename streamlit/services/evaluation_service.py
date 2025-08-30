from streamlit.core.db import get_mongo_client
from bson.regex import Regex
import pandas as pd
import sys
import os

# Add parent directory to path to access config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

def student_exists(fullname):
    client = get_mongo_client()
    if not client:
        return None
    students = client[Config.MONGO_DB_NAME].students
    return students.find_one({"Name": Regex(fullname, "i")})

def get_student_academic_records(fullname):
    client = get_mongo_client()
    if not client:
        return []
    
    db = client[Config.MONGO_DB_NAME]
    students = db.students
    grades = db.grades
    subjects = db.subjects
    semesters = db.semesters

    student = student_exists(fullname)
    if not student:
        return []

    pipeline = [
        {"$match": {"StudentID": student["_id"]}},
        {"$unwind": {"path": "$SubjectCodes", "includeArrayIndex": "idx"}},
        {"$project": {
            "SemesterID": 1,
            "SubjectCode": "$SubjectCodes",
            "Grade": {"$arrayElemAt": ["$Grades", "$idx"]},
            "Teacher": {"$arrayElemAt": ["$Teachers", "$idx"]}
        }},
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
            "foreignField": "_id",
            "as": "subj_info"
        }},
        {"$unwind": {"path": "$subj_info", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "SchoolYear": "$sem_info.SchoolYear",
            "Semester": "$sem_info.Semester",
            "SubjectCode": 1,
            "SubjectDescription": "$subj_info.Description",
            "Units": "$subj_info.Units",
            "Grade": 1,
            "Teacher": 1
        }},
        {"$sort": {"SchoolYear": 1, "Semester": 1, "SubjectCode": 1}}
    ]

    return list(grades.aggregate(pipeline, allowDiskUse=True))

def group_by_semester(data):
    df = pd.DataFrame(data)
    if df.empty:
        return []

    grouped = df.groupby(["SchoolYear", "Semester"])
    return [((sy, sem), group) for (sy, sem), group in grouped]

def compute_weighted_gpa(group):
    group = group.dropna(subset=["Grade", "Units"])
    group["Weighted"] = group["Grade"] * group["Units"]
    total_units = group["Units"].sum()
    total_weighted = group["Weighted"].sum()
    gpa = total_weighted / total_units if total_units else 0
    return round(gpa, 2), total_units
