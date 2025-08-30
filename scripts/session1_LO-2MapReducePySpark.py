# session1_LO-2MapReducePySpark.py
# MIT 261 - Parallel and Distributed Systems
# Session 1: LO-2 MapReduce with MongoDB + Pandas (PySpark alternative)
# Author: orbitsdev 🧠

import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
import pandas as pd
from pymongo import MongoClient
import json

# ---------- Load .env ----------
load_dotenv()
user = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASS")
host = os.getenv("MONGO_HOST")

if not user or not password or not host:
    raise SystemExit("❌ Missing MONGO_USER, MONGO_PASS, or MONGO_HOST in .env")

print("✅ Environment loaded")
print(f"👤 MONGO_USER: {user}")
print(f"🔒 MONGO_PASS: {'*' * len(password)}")

# ---------- Build secure Mongo URI ----------
encoded_pass = quote_plus(password)
mongo_uri = f"mongodb+srv://{user}:{encoded_pass}@{host}/?retryWrites=true&w=majority&appName=Cluster0"

# ---------- MongoDB Connection Setup ----------
client = MongoClient(mongo_uri)
db = client["mit261"]
collection = db["students"]

print("🚀 MongoDB connection established")

# ---------- Load Students Collection ----------
# Simulate the MAP phase by fetching data
students = list(collection.find({}))
df = pd.DataFrame(students)

print("📦 Loaded students collection")

# ---------- PART 1: MAP Phase (Preview Student List) ----------
print("\n📋 Student List (from MongoDB via Pandas):")
df_selected = df[["_id", "Name", "Course", "YearLevel"]]
print(df_selected.head(10).to_string(index=False))

# ---------- PART 2: REDUCE Phase (Group by Course) ----------
print("\n📊 Student Count per Course:")
course_counts = df.groupby("Course").size().reset_index(name="count")
print(course_counts.to_string(index=False))

# Optional: Dictionary conversion for JSON/screenshot
result_dict = dict(zip(course_counts["Course"], course_counts["count"]))
print("\n🗂️ Result as dictionary:")
print(json.dumps(result_dict, indent=2))

# ---------- Done ----------
print("\n✅ MapReduce task complete. You may now take screenshots and submit.")

# Close MongoDB connection
client.close()
