# scripts/session1_student_subject_list.py
# Session 1: Student List & Subject List (MongoDB Atlas + PyMongo + Pandas)
# DRY + clear comments + secure env handling.

import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd

# ---------- Config ----------
DB_NAME = "mit261"

# ---------- Load env (.env) ----------
load_dotenv()
user = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASS")
host = os.getenv("MONGO_HOST")

if not user or not password or not host:
    raise SystemExit("❌ Missing MONGO_USER, MONGO_PASS, or MONGO_HOST in .env")

# Masked output (don’t print the real password)
print("✅ Environment loaded")
print(f"👤 MONGO_USER: {user}")
print(f"🔒 MONGO_PASS: {'*' * len(password)}")

# ---------- Build safe URI (URL-encode password) ----------
uri = f"mongodb+srv://{user}:{quote_plus(password)}@{host}/{DB_NAME}?retryWrites=true&w=majority&appName=Cluster0"

# ---------- Connect & get DB ----------
client = MongoClient(uri)
db = client[DB_NAME]

# ---------- Helper: fetch -> DataFrame ----------
def fetch_df(coll_name: str, projection: dict, limit=10) -> pd.DataFrame:
    """Fetch documents from `coll_name` with given projection and return a DataFrame."""
    coll = db[coll_name]
    count = coll.count_documents({})
    print(f"\n🧾 Documents in `{coll_name}`: {count}")

    if count == 0:
        return pd.DataFrame()

    docs = list(coll.find({}, projection).limit(limit))
    df = pd.DataFrame(docs)
    return df

# ---------- Students ----------
students_projection = {"_id": 1, "Name": 1, "Course": 1, "YearLevel": 1}
df_students = fetch_df("students", students_projection, limit=10)

if df_students.empty:
    print("⚠️ No student records found.")
else:
    print("\n📋 Student List:")
    # Pretty print to console; also save for submission
    print(df_students.head(10).to_string(index=False))
    df_students.to_csv("students_list.csv", index=False)

# ---------- Subjects ----------
subjects_projection = {"_id": 1, "Description": 1, "Units": 1, "Teacher": 1}
df_subjects = fetch_df("subjects", subjects_projection, limit=10)

if df_subjects.empty:
    print("⚠️ No subject records found.")
else:
    print("\n📋 Subject List:")
    print(df_subjects.to_string(index=False))
    df_subjects.to_csv("subjects_list.csv", index=False)

# ---------- Done ----------
print("\n✅ Saved: students_list.csv, subjects_list.csv")
