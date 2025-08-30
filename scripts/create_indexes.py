#!/usr/bin/env python
# scripts/create_indexes.py

import os
import sys
import time
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import OperationFailure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import config from parent directory
sys.path.append('..')
from config import Config

def create_indexes():
    """Create indexes on MongoDB collections for optimized queries"""
    try:
        # Connect to MongoDB
        client = MongoClient(
            Config.MONGO_URI,
            maxPoolSize=25,  # Increased connection pool
            socketTimeoutMS=60000,  # Longer timeout for index creation
            connectTimeoutMS=30000,
            serverSelectionTimeoutMS=30000,
            retryWrites=True,
            compressors='zlib'
        )
        db = client[Config.MONGO_DBNAME]
        
        logger.info("Connected to MongoDB. Starting index creation...")
        
        # Create indexes for grades collection
        logger.info("Creating indexes for grades collection...")
        start_time = time.time()
        
        # Compound index for filtering by semester and subject
        db.grades.create_index(
            [("SemesterID", ASCENDING), ("SubjectCodes", ASCENDING)],
            background=True,
            name="semester_subject_idx"
        )
        
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
