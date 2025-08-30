# session1_LO-1ParallelvsDistributed.py
# MIT 261 - Parallel and Distributed Systems
# Session 1: LO-1 Parallel vs Distributed Computing using MongoDB + Pandas
# Author: orbitsdev 🧠

import os
import time
import json
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from urllib.parse import quote_plus
from multiprocessing import Pool, cpu_count

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

# ---------- Connect to MongoDB ----------
encoded_pass = quote_plus(password)
mongo_uri = f"mongodb+srv://{user}:{encoded_pass}@{host}/?retryWrites=true&w=majority"

# Add timeout to prevent hanging
client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
try:
    # Verify connection works
    client.server_info()
    db = client["mit261"]
    print("🚀 Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")
    raise SystemExit("Failed to connect to MongoDB")

# ---------- Load students and grades ----------
try:
    # Add limits to prevent loading too much data
    students = list(db["students"].find({}, {"_id": 1, "Name": 1, "Course": 1, "YearLevel": 1}).limit(1000))
    print(f"📥 Students loaded: {len(students)}")
    
    grades = list(db["grades"].find({}, {"StudentID": 1, "Grades": 1, "SubjectCodes": 1, "Teachers": 1, "SemesterID": 1}).limit(1000))
    print(f"📥 Grades loaded: {len(grades)}")
    
    if not students or not grades:
        print("⚠️ Warning: No data found in one or both collections")
        
except Exception as e:
    print(f"❌ Error loading data: {e}")
    client.close()
    raise SystemExit("Database error occurred")

# Print statements already handled in try block

# ---------- Convert to DataFrames ----------
df_students = pd.DataFrame(students).rename(columns={"_id": "StudentID"})
df_grades = pd.DataFrame(grades)

# Merge: grades + students
df = pd.merge(df_grades, df_students, on="StudentID", how="left")

# ---------- Explode Arrays ----------
df_exploded = df.explode(["Grades", "SubjectCodes", "Teachers"]).reset_index(drop=True)
df_exploded.rename(columns={"Grades": "Grade", "SubjectCodes": "SubjectCode"}, inplace=True)

print("📋 Sample of exploded data:")
print(df_exploded[["StudentID", "Grade", "SubjectCode", "Teachers"]].head(10))

# ---------- Parallel Computing ----------
def compute_parallel_avg(df_chunk):
    return df_chunk.groupby("StudentID")["Grade"].mean()

def run_parallel(df):
    print("\n⚙️ Running parallel average computation...")
    start = time.perf_counter()
    
    # Use fewer cores to avoid potential issues
    num_cores = min(4, cpu_count())
    print(f"Using {num_cores} CPU cores")
    
    # Handle Windows multiprocessing properly
    if __name__ == "__main__":
        chunks = np.array_split(df, num_cores)
        
        try:
            with Pool(processes=num_cores) as pool:
                results = pool.map(compute_parallel_avg, chunks)
            
            # Simplify - avoid double groupby
            result = pd.concat(results)
            end = time.perf_counter()
            print(f"⏱️ Parallel time: {end - start:.2f}s")
            return result
        except Exception as e:
            print(f"Error in parallel processing: {e}")
            # Fallback to single-process
            result = compute_parallel_avg(df)
            end = time.perf_counter()
            print(f"⏱️ Single-process time: {end - start:.2f}s")
            return result
    else:
        # Fallback if not in main module
        result = compute_parallel_avg(df)
        end = time.perf_counter()
        print(f"⏱️ Single-process time: {end - start:.2f}s")
        return result

# ---------- Distributed Computing (Simulated) ----------
def simulate_node(node_id, df):
    print(f"🧠 Node {node_id} processing {len(df)} rows...")
    time.sleep(0.5)  # simulate network delay
    return df.groupby("StudentID")["Grade"].mean()

def run_distributed(df, nodes=4):
    print("\n🌐 Simulating distributed computing...")
    start = time.perf_counter()
    chunks = np.array_split(df, nodes)
    results = []

    for i, chunk in enumerate(chunks, start=1):
        result = simulate_node(i, chunk)
        results.append(result)

    result = pd.concat(results).groupby("StudentID").mean()
    end = time.perf_counter()
    print(f"⏱️ Distributed time: {end - start:.2f}s")
    return result

# Add guard for multiprocessing
if __name__ == "__main__":
    # ---------- Execute both computations ----------
    # Use a smaller sample for processing to avoid hanging
    sample_df = df_exploded.sample(min(1000, len(df_exploded)))
    print(f"\nProcessing sample of {len(sample_df)} rows")
    
    parallel_avg = run_parallel(sample_df)
    distributed_avg = run_distributed(sample_df)
    
    # ---------- Compare results (should match) ----------
    print("\n📊 Sample average grades (Parallel):")
    print(parallel_avg.head())
    
    print("\n📊 Sample average grades (Distributed):")
    print(distributed_avg.head())
    
    # ---------- Done ----------
    print("\n✅ Lab complete! You may now take screenshots and submit.")
    
    # Close MongoDB
    client.close()

# MongoDB client is already closed inside the if block
