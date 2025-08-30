from flask import Blueprint, render_template, request, jsonify
from app.extensions import get_db
from app.services.classlist_service import get_classlist_data, calculate_class_stats
import time

bp = Blueprint("session2_classlist", __name__, url_prefix="/session2")

@bp.route("/")
def index():
    """Session 2 index page"""
    return render_template("session2/index.html", title="Session 2: Interactive Class List")

@bp.route("/classlist")
def classlist_view():
    """Interactive class list with filters and statistics"""
    # Get filter parameters
    subject_filter = request.args.get("subject")
    semester_filter = request.args.get("semester")
    
    # Get pagination parameters
    try:
        page = int(request.args.get("page", 0))
        if page < 0:
            page = 0
    except ValueError:
        page = 0
        
    # Set page size
    page_size = 25

    # Get data from service with pagination
    class_data = get_classlist_data(subject_filter, semester_filter, page, page_size)
    
    # Calculate statistics
    stats = calculate_class_stats(class_data)
    
    # Get all available subjects and semesters for dropdowns
    db = get_db()
    
    # Get subject codes from grades collection directly
    try:
        grades_collection = db.get_collection("grades")
        # Use distinct to get unique subject codes based on actual structure
        subject_codes = grades_collection.distinct("SubjectCodes")
        
        # Format subject codes to match screenshot and use actual subjects collection
        subject_options = []
        
        # If we have subject codes from the database, use them
        if subject_codes:
            # Sort the codes
            subject_codes.sort()
            
            # Look up subject descriptions from subjects collection
            subjects_collection = db.get_collection("subjects")
            
            for code in subject_codes:
                # Try to get description from subjects collection
                subject_doc = subjects_collection.find_one({"_id": code})
                if subject_doc and "Description" in subject_doc:
                    # Use the code as value and code as display (matching screenshot)
                    subject_options.append((code, code))
                else:
                    # If subject not found in subjects collection, just use the code
                    subject_options.append((code, code))
        
        # If still empty, add some default options
        if not subject_options:
            # Check if subjects collection has any documents
            subjects_collection = db.get_collection("subjects")
            all_subjects = list(subjects_collection.find({}).limit(10))
            
            if all_subjects:
                # Use actual subjects from database
                for subject in all_subjects:
                    code = subject.get("_id")
                    subject_options.append((code, code))
            else:
                # Fallback to default codes if no subjects in database
                default_codes = ["CS101", "CS102", "CS103", "CS104", "CS105"]
                for code in default_codes:
                    subject_options.append((code, code))
                print("Using default subject options")
    except Exception as e:
        print(f"Error fetching subjects: {e}")
        # Provide default options matching screenshot
        subject_options = [("CS101", "CS101"), ("CS102", "CS102"), 
                          ("CS103", "CS103"), ("CS104", "CS104"), 
                          ("CS105", "CS105")]
    
    # Get semesters from grades collection directly
    try:
        # Use distinct to get unique semester IDs based on actual structure
        # The field is SemesterID (capital ID) based on your structure
        semester_ids = grades_collection.distinct("SemesterID")
        
        # For semester options, use numeric values like in the screenshots
        semester_options = []
        
        # Convert to integers if possible and sort
        numeric_semesters = []
        for sem_id in semester_ids:
            try:
                # Try to convert to integer if it's a dict with $numberInt
                if isinstance(sem_id, dict) and "$numberInt" in sem_id:
                    numeric_semesters.append(int(sem_id["$numberInt"]))
                else:
                    # Try to convert directly
                    numeric_semesters.append(int(sem_id))
            except (ValueError, TypeError):
                # If not convertible, just use as is
                pass
        
        # Sort numerically
        numeric_semesters.sort()
        
        # Convert back to strings for display
        semester_options = [str(sem) for sem in numeric_semesters]
        
        # If still empty, check semesters collection
        if not semester_options:
            semesters_collection = db.get_collection("semesters")
            all_semesters = list(semesters_collection.find({}).limit(10))
            
            if all_semesters:
                # Use actual semester IDs from database
                for semester in all_semesters:
                    sem_id = semester.get("_id")
                    if isinstance(sem_id, dict) and "$numberInt" in sem_id:
                        semester_options.append(sem_id["$numberInt"])
                    else:
                        semester_options.append(str(sem_id))
                semester_options.sort()
            else:
                # Fallback to default options
                semester_options = ["1", "2", "3", "4"]
                print("Using default semester options")
    except Exception as e:
        print(f"Error fetching semesters: {e}")
        # Provide default numeric options
        semester_options = ["1", "2", "3", "4"]
    
    # Get instructor name and other details for the filtered class - with error handling
    instructor = "N/A"
    subject_name = "All Subjects"
    subject_code = ""
    school_year = ""
    semester_name = ""
    
    if class_data and len(class_data) > 0:
        try:
            instructor = class_data[0].get("Teacher", "N/A")
            subject_name = class_data[0].get("Subject", "All Subjects")
            subject_code = class_data[0].get("SubjectCode", "")
            school_year = class_data[0].get("SchoolYear", "")
            semester_name = class_data[0].get("Semester", "")
        except (IndexError, KeyError) as e:
            print(f"Error extracting class data details: {e}")
    
    # Calculate pagination info
    has_next = len(class_data) == page_size
    has_prev = page > 0
    
    return render_template(
        "session2/classlist.html",
        data=class_data,
        subject_options=subject_options,
        semester_options=semester_options,
        stats=stats,
        instructor=instructor,
        subject=subject_name,
        subject_code=subject_code,
        school_year=school_year,
        semester_name=semester_name,
        current_subject=subject_filter,
        current_semester=semester_filter,
        connected=True,
        # Pagination data
        current_page=page,
        has_next=has_next,
        has_prev=has_prev,
        page_size=page_size
    )

@bp.route("/api/classlist")
def classlist_api():
    """API endpoint for class list data with pagination support"""
    # Get filter parameters
    subject_filter = request.args.get("subject")
    semester_filter = request.args.get("semester")
    
    # Get pagination parameters
    try:
        page = int(request.args.get("page", 0))
        if page < 0:
            page = 0
    except ValueError:
        page = 0
        
    try:
        page_size = int(request.args.get("limit", 25))
        if page_size < 1 or page_size > 100:  # Limit max page size
            page_size = 25
    except ValueError:
        page_size = 25
    
    # Get data from service with pagination
    class_data = get_classlist_data(subject_filter, semester_filter, page, page_size)
    stats = calculate_class_stats(class_data)
    
    # Calculate pagination metadata
    has_next = len(class_data) == page_size
    
    return jsonify({
        "data": class_data,
        "stats": stats,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "has_next": has_next,
            "has_prev": page > 0,
            "total_on_page": len(class_data)
        },
        "filters": {
            "subject": subject_filter,
            "semester": semester_filter
        },
        "execution_time": {
            "timestamp": time.time(),
            "formatted": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    })
