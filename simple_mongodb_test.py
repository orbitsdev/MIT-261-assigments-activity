from pymongo import MongoClient

# MongoDB connection string
mongo_uri = "mongodb+srv://orbitsdev:%40Password@cluster0.q8v3kcn.mongodb.net/mit261?retryWrites=true&w=majority&appName=Cluster0"

# Print statements for debugging
print("Script started")

try:
    # Create client
    print("Creating MongoDB client...")
    client = MongoClient(mongo_uri)
    
    # Test connection
    print("Testing connection...")
    client.admin.command('ping')
    print("MongoDB connection successful!")
    
    # Get database
    db = client.mit261
    
    # List collections
    print("\nAvailable collections:")
    collections = db.list_collection_names()
    for collection in collections:
        print(f"- {collection}")
    
    # Count documents in each collection
    for collection in collections:
        count = db[collection].count_documents({})
        print(f"{collection}: {count} documents")
    
    # Show sample data from students collection
    print("\nSample students:")
    for student in db.students.find().limit(2):
        print(f"Student: {student}")
    
    # Show sample data from subjects collection
    print("\nSample subjects:")
    for subject in db.subjects.find().limit(2):
        print(f"Subject: {subject}")
        
except Exception as e:
    print(f"Error: {str(e)}")

print("Script completed")
