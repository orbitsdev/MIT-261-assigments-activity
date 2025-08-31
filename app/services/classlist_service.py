# app/services/classlist_service.py

from app.extensions import get_db
from pymongo import ReadPreference
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from statistics import mean, median
from bson import ObjectId
from functools import lru_cache
import time

def get_classlist_data(subject=None, semester=None, school_year=None, teacher=None, page=0, limit=25):
    """
    Aggregates student, subject, grade, and semester data into a class list view.
    Applies optional filters for subject, semester name, and school year.
    
    Uses ReadPreference.SECONDARY_PREFERRED for better performance and distribution of read load.
    Uses ReadConcern.LOCAL for better performance.
    
    Args:
        subject: Subject code filter
        semester: Semester name filter (e.g., 'Summer', 'FirstSem')
        school_year: School year filter (e.g., '2020', '2023')
        teacher: Teacher name filter
        page: Page number for pagination (0-indexed)
        limit: Number of records per page
    """
    # Use the cached version if available
    cache_key = f"{subject}_{semester}_{school_year}_{teacher}_{page}_{limit}"
    cached_result = _get_cached_classlist_data(cache_key)
    if cached_result:
        return cached_result
    
    db = get_db()
    
    # Configure read preferences for distributed system reliability
    grades_collection = db.get_collection(
        "grades",
        read_preference=ReadPreference.SECONDARY_PREFERRED,
        read_concern=ReadConcern("local"),  # Local read concern for better performance
        write_concern=WriteConcern(w=0)  # No write acknowledgment needed for reads
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
        
    # Add teacher filter if provided
    if teacher and teacher != "-- All Teachers --":
        match_conditions["Teachers"] = teacher
    
    # Get semester IDs that match the semester name if provided
    if semester and semester != "-- All Semesters --":
        try:
            # First, try to find semester IDs that match the provided semester name
            semesters_collection = db.get_collection("semesters")
            semester_docs = list(semesters_collection.find({"Semester": semester}))
            
            if semester_docs:
                # If we found matching semesters, use their IDs for filtering
                semester_ids = [doc.get("_id") for doc in semester_docs]
                match_conditions["SemesterID"] = {"$in": semester_ids}
            else:
                # If no matching semester found, try using it directly (fallback)
                match_conditions["SemesterID"] = semester
        except Exception as e:
            print(f"Error finding semester IDs for name {semester}: {e}")
            # Fallback to direct matching
            match_conditions["SemesterID"] = semester
    
    # Add school year filter if provided
    if school_year and school_year != "-- All Years --":
        try:
            # Find semester IDs for the given school year
            semesters_collection = db.get_collection("semesters")
            
            # Try to convert school_year to integer if it's a string
            try:
                year_value = int(school_year)
            except (ValueError, TypeError):
                year_value = school_year
                
            # Find semesters with matching school year
            year_semester_docs = list(semesters_collection.find({"SchoolYear": year_value}))
            
            if year_semester_docs:
                # If we found matching semesters, use their IDs for filtering
                year_semester_ids = [doc.get("_id") for doc in year_semester_docs]
                
                # If we already have a SemesterID filter, we need to find the intersection
                if "SemesterID" in match_conditions:
                    # If it's already a list, find intersection
                    if isinstance(match_conditions["SemesterID"], dict) and "$in" in match_conditions["SemesterID"]:
                        existing_ids = match_conditions["SemesterID"]["$in"]
                        # Find intersection of the two lists
                        intersection_ids = [id for id in existing_ids if id in year_semester_ids]
                        match_conditions["SemesterID"] = {"$in": intersection_ids}
                    else:
                        # If it's a single value, check if it's in the year_semester_ids
                        single_id = match_conditions["SemesterID"]
                        if single_id in year_semester_ids:
                            # Keep the single ID as is
                            pass
                        else:
                            # No intersection, return empty result
                            return []
                else:
                    # No existing semester filter, just add the year filter
                    match_conditions["SemesterID"] = {"$in": year_semester_ids}
            else:
                # If no matching school year found, return empty result
                return []
        except Exception as e:
            print(f"Error finding semester IDs for school year {school_year}: {e}")
    
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
            
            # Sort by FullName (corrected field name)
            {"$sort": {"FullName": 1}}
        ]
        
        # Execute the second phase to get detailed data
        # Use batchSize=25 to match our page size for optimal memory usage
        cursor = grades_collection.aggregate(
            main_pipeline, 
            allowDiskUse=True, 
            batchSize=limit,
            maxTimeMS=30000  # Set a timeout of 30 seconds to prevent long-running queries
        )
        
        # Convert cursor to list with timeout handling
        try:
            results = list(cursor)  # More efficient than appending one by one
        except Exception as e:
            print(f"Error processing cursor: {str(e)}")
            results = []
        
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
CACHE_TTL = 300  # Increased cache time-to-live to 5 minutes for better performance
CACHE_CLEANUP_THRESHOLD = 100  # Only clean up cache when it reaches this size

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
    
    # Clean up cache if it gets too large
    if len(_classlist_cache) > CACHE_CLEANUP_THRESHOLD:
        _clear_expired_cache()

# Clear expired cache entries periodically
def _clear_expired_cache():
    """Remove expired entries from cache"""
    global _classlist_cache, _cache_expiry
    
    current_time = time.time()
    expired_keys = [k for k, v in _cache_expiry.items() if current_time > v]
    
    # Delete in batch for better performance
    for key in expired_keys:
        _classlist_cache.pop(key, None)  # More efficient than checking first
        _cache_expiry.pop(key, None)
    
    # If cache is still too large after removing expired entries,
    # remove oldest entries until we're under the threshold
    if len(_classlist_cache) > CACHE_CLEANUP_THRESHOLD:
        # Sort by expiry time and keep only the newest entries
        sorted_keys = sorted(_cache_expiry.items(), key=lambda x: x[1], reverse=True)
        keys_to_keep = sorted_keys[:CACHE_CLEANUP_THRESHOLD]
        
        # Create new dictionaries with only the keys to keep
        new_cache = {k: _classlist_cache[k] for k, _ in keys_to_keep}
        new_expiry = {k: v for k, v in keys_to_keep}
        
        # Replace the old dictionaries
        _classlist_cache = new_cache
        _cache_expiry = new_expiry
    
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
