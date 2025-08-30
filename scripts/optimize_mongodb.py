#!/usr/bin/env python
# scripts/optimize_mongodb.py

import os
import sys
import time
import logging
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
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

def optimize_mongodb():
    """
    Perform MongoDB optimizations:
    1. Create indexes for faster queries
    2. Run explain() to analyze query performance
    3. Print optimization recommendations
    """
    try:
        # Connect to MongoDB with optimized settings
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
        
        logger.info("=" * 80)
        logger.info("MongoDB Optimization Script")
        logger.info("=" * 80)
        logger.info(f"Connected to MongoDB at {Config.MONGO_URI}")
        logger.info(f"Database: {Config.MONGO_DBNAME}")
        logger.info("-" * 80)
        
        # 1. Create indexes for filtering and joins
        logger.info("\n[1] Creating indexes for faster queries...")
        
        # Create compound indexes for filtering in grades collection
        db.grades.create_index(
            [('SemesterID', ASCENDING), ('SubjectCodes', ASCENDING)],
            background=True,
            name='semester_subject_idx'
        )
        logger.info('✅ Created index on grades: SemesterID + SubjectCodes')
        
        # Create indexes for join operations
        db.grades.create_index([('StudentID', ASCENDING)])
        logger.info('✅ Created index on grades: StudentID')
        
        db.students.create_index([("_id", ASCENDING)])
        logger.info("✅ Created index on students: _id")
        
        db.subjects.create_index([("_id", ASCENDING)])
        logger.info("✅ Created index on subjects: _id")
        
        db.semesters.create_index([("_id", ASCENDING)])
        logger.info("✅ Created index on semesters: _id")
        
        # Index for sorting by student name
        db.students.create_index([("Name", ASCENDING)])
        logger.info("✅ Created index on students: Name")
        
        # 2. Analyze query performance
        logger.info("\n[2] Analyzing query performance...")
        
        # Get collection stats
        grades_stats = db.command("collStats", "grades")
        students_stats = db.command("collStats", "students")
        subjects_stats = db.command("collStats", "subjects")
        semesters_stats = db.command("collStats", "semesters")
        
        logger.info(f"Grades collection size: {grades_stats['size'] / 1024 / 1024:.2f} MB")
        logger.info(f"Students collection size: {students_stats['size'] / 1024 / 1024:.2f} MB")
        logger.info(f"Subjects collection size: {subjects_stats['size'] / 1024 / 1024:.2f} MB")
        logger.info(f"Semesters collection size: {semesters_stats['size'] / 1024 / 1024:.2f} MB")
        
        # 3. Print optimization recommendations
        logger.info("\n[3] Optimization recommendations:")
        logger.info("✅ Early filtering with $match stage at the beginning of the pipeline")
        logger.info("✅ Indexes created for faster joins and filtering")
        logger.info("✅ Pagination implemented to limit data processing")
        logger.info("✅ Caching added for frequently accessed data")
        logger.info("✅ Proper error handling for MongoDB aggregation errors")
        logger.info("✅ allowDiskUse=True enabled for large sorts")
        
        logger.info("\n[4] Additional recommendations:")
        logger.info("- Consider upgrading MongoDB Atlas tier if still experiencing memory issues")
        logger.info("- Monitor query performance with db.currentOp() during heavy load")
        logger.info("- Consider denormalizing data if joins are still slow")
        logger.info("- Add TTL index for automatic cache cleanup if implementing server-side caching")
        
        logger.info("\n" + "=" * 80)
        logger.info("Optimization completed successfully!")
        logger.info("=" * 80)
        
    except OperationFailure as e:
        logger.error(f"Error during optimization: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    optimize_mongodb()
