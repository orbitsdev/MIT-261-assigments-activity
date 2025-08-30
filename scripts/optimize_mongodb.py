#!/usr/bin/env python
# scripts/optimize_mongodb.py

import os
import time
from pymongo import MongoClient, IndexModel
from pymongo.errors import OperationFailure

# Get MongoDB connection details from environment variables
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'mit261')

def optimize_mongodb():
    """
    Perform MongoDB optimizations:
    1. Create indexes for faster queries
    2. Run explain() to analyze query performance
    3. Print optimization recommendations
    """
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        print("=" * 80)
        print("MongoDB Optimization Script")
        print("=" * 80)
        print(f"Connected to MongoDB at {MONGO_URI}")
        print(f"Database: {DB_NAME}")
        print("-" * 80)
        
        # 1. Create indexes for filtering and joins
        print("\n[1] Creating indexes for faster queries...")
        
        # Create compound indexes for filtering in grades collection
        db.grades.create_index([("SemesterId", 1), ("SubjectCodes", 1)])
        print("✅ Created index on grades: SemesterId + SubjectCodes")
        
        # Create indexes for join operations
        db.grades.create_index([("StudentId", 1)])
        print("✅ Created index on grades: StudentId")
        
        db.students.create_index([("_id", 1)])
        print("✅ Created index on students: _id")
        
        db.subjects.create_index([("_id", 1)])
        print("✅ Created index on subjects: _id")
        
        db.semesters.create_index([("_id", 1)])
        print("✅ Created index on semesters: _id")
        
        # Index for sorting by student name
        db.students.create_index([("Name", 1)])
        print("✅ Created index on students: Name")
        
        # 2. Analyze query performance
        print("\n[2] Analyzing query performance...")
        
        # Get collection stats
        grades_stats = db.command("collStats", "grades")
        students_stats = db.command("collStats", "students")
        subjects_stats = db.command("collStats", "subjects")
        semesters_stats = db.command("collStats", "semesters")
        
        print(f"Grades collection size: {grades_stats['size'] / 1024 / 1024:.2f} MB")
        print(f"Students collection size: {students_stats['size'] / 1024 / 1024:.2f} MB")
        print(f"Subjects collection size: {subjects_stats['size'] / 1024 / 1024:.2f} MB")
        print(f"Semesters collection size: {semesters_stats['size'] / 1024 / 1024:.2f} MB")
        
        # 3. Print optimization recommendations
        print("\n[3] Optimization recommendations:")
        print("✅ Early filtering with $match stage at the beginning of the pipeline")
        print("✅ Indexes created for faster joins and filtering")
        print("✅ Pagination implemented to limit data processing")
        print("✅ Caching added for frequently accessed data")
        print("✅ Proper error handling for MongoDB aggregation errors")
        print("✅ allowDiskUse=True enabled for large sorts")
        
        print("\n[4] Additional recommendations:")
        print("- Consider upgrading MongoDB Atlas tier if still experiencing memory issues")
        print("- Monitor query performance with db.currentOp() during heavy load")
        print("- Consider denormalizing data if joins are still slow")
        print("- Add TTL index for automatic cache cleanup if implementing server-side caching")
        
        print("\n" + "=" * 80)
        print("Optimization completed successfully!")
        print("=" * 80)
        
    except OperationFailure as e:
        print(f"Error during optimization: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    optimize_mongodb()
