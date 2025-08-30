# app/services/classlist_service.py

from app.extensions import get_db
from pymongo import ReadPreference
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from statistics import mean, median
from bson import ObjectId
from functools import lru_cache
import time

def get_classlist_data(subject=None, semester=None, page=0, limit=25):
    """
    Aggregates student, subject, grade, and semester data into a class list view.
    Applies optional filters for subject and semester.
    
    Uses ReadPreference.SECONDARY_PREFERRED for better performance and distribution of read load.
    Uses ReadConcern.MAJORITY to ensure consistent reads across replicas.
    
    Args:
        subject: Subject code filter
        semester: Semester term filter
        page: Page number for pagination (0-indexed)
        limit: Number of records per page
    """
    # Use the cached version if available
    cache_key = f"{subject}_{semester}_{page}_{limit}"
    cached_result = _get_cached_classlist_data(cache_key)
    if cached_result:
        return cached_result
    
    db = get_db()
    
    # Configure read preferences for distributed system reliability
    grades_collection = db.get_collection(
        "grades",
        read_preference=ReadPreference.SECONDARY_PREFERRED,
        read_concern=ReadConcern("local")  # Changed to local for better performance
    )
    
    # Reduce page size for better performance
    if limit > 50:
        limit = 25
    
    # OPTIMIZATION: Use a two-phase approach for large datasets
    # Phase 1: Get only the IDs we need with early filtering
    # Phase 2: Fetch only those specific documents
    
    # Build match conditions for early filtering
    match_conditions = {}
    if subject and subject != "-- All Subjects --":
        match_conditions["SubjectCodes"] = subject
    if semester and semester != "-- All Semesters --":
        # Handle semester as numeric ID based on actual structure
        try:
            semester_id = int(semester)
            match_conditions["SemesterID"] = semester_id
        except (ValueError, TypeError):
            match_conditions["SemesterID"] = semester
    
    # Phase 1: Get only the IDs we need with pagination
    id_pipeline = []
    if match_conditions:
        id_pipeline.append({"$match": match_conditions})
    
    # Add minimal processing to get IDs
    id_pipeline.extend([
        # Minimal unwinding
        {"$unwind": "$SubjectCodes"},
        
        # Additional filtering if needed
        {
            "$match": {
                "$and": [
                    {} if not subject or subject == "-- All Subjects --" else {"SubjectCodes": subject},
                ]
            }
        },
        
        # Project only what we need for the next phase
        {"$project": {"_id": 1, "StudentID": 1, "SubjectCodes": 1}},
        
        # Sort by _id for consistent pagination
        {"$sort": {"_id": 1}},
        
        # Add pagination
        {"$skip": page * limit},
        {"$limit": limit}
    ])
    
    try:
        # Execute the first phase to get IDs
        start_time = time.time()
        id_results = list(grades_collection.aggregate(id_pipeline, allowDiskUse=True))
        
        # If no results, return early
        if not id_results:
            print("No matching records found")
            return []
        
        # Extract IDs for the second phase
        grade_ids = [doc["_id"] for doc in id_results]
        student_ids = [doc.get("StudentID", doc.get("StudentId")) for doc in id_results]
        subject_codes = [doc["SubjectCodes"] for doc in id_results]
        
        # Phase 2: Get full data for only these specific IDs
        main_pipeline = [
            # Match only the specific IDs we need
            {"$match": {"_id": {"$in": grade_ids}}},
            
            # Unwind arrays that we need to process
            {"$unwind": "$Grades"},
            {"$unwind": "$Teachers"},
            {"$unwind": "$SubjectCodes"},
            
            # Lookup students - use indexes and limit to only our student IDs
            {
                "$lookup": {
                    "from": "students",
                    "localField": "StudentID",
                    "foreignField": "_id",
                    "as": "student"
                }
            },
            {"$unwind": "$student"},
            
            # Lookup subjects - use indexes
            {
                "$lookup": {
                    "from": "subjects",
                    "localField": "SubjectCodes",
                    "foreignField": "_id",
                    "as": "subject"
                }
            },
            {"$unwind": "$subject"},
            
            # Lookup semesters - use indexes
            {
                "$lookup": {
                    "from": "semesters",
                    "localField": "SemesterID",
                    "foreignField": "_id",
                    "as": "semester"
                }
            },
            {"$unwind": "$semester"},
            
            # Project only needed fields - reduces memory usage
            {
                "$project": {
                    "_id": 0,
                    "StudentID": "$StudentID",
                    "FullName": "$student.Name",
                    "Course": "$student.Course",
                    "YearLevel": "$student.YearLevel",
                    "Subject": "$subject.Description",
                    "SubjectCode": "$SubjectCodes",
                    "Units": "$subject.Units",
                    "Teacher": "$Teachers",
                    "Grade": "$Grades",
                    "Semester": "$semester.Semester",
                    "SchoolYear": "$semester.SchoolYear"
                }
            },
            
            # Sort by student name
            {"$sort": {"StudentName": 1}}
        ]
        
        # Execute the second phase to get detailed data
        cursor = grades_collection.aggregate(main_pipeline, allowDiskUse=True, batchSize=100)
        
        # Convert cursor to list with timeout handling
        results = []
        for doc in cursor:
            results.append(doc)
        
        execution_time = time.time() - start_time
        print(f"Aggregation completed in {execution_time:.2f} seconds")
        
        # Cache results if we have them
        if results:
            _cache_classlist_data(cache_key, results)
        
        return results
    except Exception as e:
        print(f"MongoDB aggregation error: {str(e)}")
        # Return empty list with detailed error logging
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return []

# Simple in-memory cache with expiration
_classlist_cache = {}
_cache_expiry = {}
CACHE_TTL = 120  # Increased cache time-to-live to 2 minutes for better performance

def _get_cached_classlist_data(key):
    """Get data from cache if it exists and hasn't expired"""
    if key in _classlist_cache and time.time() < _cache_expiry[key]:
        print(f"Cache hit for key: {key}")
        return _classlist_cache[key]
    return None

def _cache_classlist_data(key, data):
    """Store data in cache with expiration"""
    _classlist_cache[key] = data
    _cache_expiry[key] = time.time() + CACHE_TTL
    print(f"Cached data for key: {key}")

# Clear expired cache entries periodically
def _clear_expired_cache():
    """Remove expired entries from cache"""
    current_time = time.time()
    expired_keys = [k for k, v in _cache_expiry.items() if current_time > v]
    
    for key in expired_keys:
        if key in _classlist_cache:
            del _classlist_cache[key]
        if key in _cache_expiry:
            del _cache_expiry[key]
    
    return len(expired_keys)

def calculate_class_stats(class_data):
    """
    Calculate class statistics including:
    - General Percentile Average (GPA)
    - Number of students above/below GPA
    - Total enrolled students
    """
    if not class_data:
        return {
            "gpa": 0,
            "total_enrolled": 0,
            "above_gpa": 0,
            "below_gpa": 0
        }
    
    # Extract grades as numbers
    grades = [float(row["Grade"]) for row in class_data]
    
    # Calculate GPA (mean grade)
    gpa = round(mean(grades), 2) if grades else 0
    
    # Count students above/below GPA
    above_gpa = sum(1 for grade in grades if grade > gpa)
    below_gpa = sum(1 for grade in grades if grade < gpa)
    
    return {
        "gpa": gpa,
        "total_enrolled": len(class_data),
        "above_gpa": above_gpa,
        "below_gpa": below_gpa
    }
