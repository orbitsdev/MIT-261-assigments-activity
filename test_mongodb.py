from pymongo import MongoClient

# MongoDB connection string - hardcoded for testing
mongo_uri = "mongodb+srv://orbitsdev:%40Password@cluster0.q8v3kcn.mongodb.net/mit261?retryWrites=true&w=majority&appName=Cluster0"

print("Connecting to MongoDB...")
try:
    # Create client
    client = MongoClient(mongo_uri)
    
    # Test connection
    client.admin.command('ping')
    print("MongoDB connection successful!")
    
    # Get database
    db = client.mit261
    
    # List collections
    print("\nAvailable collections:")
    collections = db.list_collection_names()
    for collection in collections:
        print(f"- {collection}")
    
    # Show sample data
    print("\nSample data from students collection:")
    students = list(db.students.find().limit(3))
    for student in students:
        print(student)
    
    print("\nSample data from subjects collection:")
    subjects = list(db.subjects.find().limit(3))
    for subject in subjects:
        print(subject)
        
except Exception as e:
    print(f"Error connecting to MongoDB: {str(e)}")
