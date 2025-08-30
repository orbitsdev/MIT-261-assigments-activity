#!/usr/bin/env python
# scripts/create_indexes.py

import os
from pymongo import MongoClient
from pymongo.errors import OperationFailure

# Get MongoDB connection details from environment variables
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'mit261')

def create_indexes():
    """Create indexes on MongoDB collections for optimized queries"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        print("Connected to MongoDB. Creating indexes...")
        
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
        
        # Optional: Index for sorting by student name
        db.students.create_index([("Name", 1)])
        print("✅ Created index on students: Name")
        
        print("\nAll indexes created successfully!")
        
    except OperationFailure as e:
        print(f"Error creating indexes: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    create_indexes()
