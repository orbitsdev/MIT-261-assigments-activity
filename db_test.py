from pymongo import MongoClient
import sys

# Force stdout to flush immediately
sys.stdout.reconfigure(line_buffering=True)

# MongoDB connection string
mongo_uri = "mongodb+srv://orbitsdev:%40Password@cluster0.q8v3kcn.mongodb.net/mit261?retryWrites=true&w=majority&appName=Cluster0"

print("Starting MongoDB connection test...")
sys.stdout.flush()

try:
    # Create client with minimal settings
    print("Creating MongoDB client...")
    sys.stdout.flush()
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    
    # Test connection
    print("Testing connection...")
    sys.stdout.flush()
    client.admin.command('ping')
    print("MongoDB connection successful!")
    sys.stdout.flush()
    
    # Get database
    db = client.mit261
    
    # List collections
    print("\nAvailable collections:")
    sys.stdout.flush()
    collections = db.list_collection_names()
    for collection in collections:
        print(f"- {collection}")
        sys.stdout.flush()
    
    # Show sample data from students collection
    print("\nSample student data:")
    sys.stdout.flush()
    student = db.students.find_one()
    if student:
        print(f"Student: {student}")
    else:
        print("No students found")
    sys.stdout.flush()
    
except Exception as e:
    print(f"Error: {str(e)}")
    sys.stdout.flush()

print("Test completed")
sys.stdout.flush()
