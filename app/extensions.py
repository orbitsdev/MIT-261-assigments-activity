from pymongo import MongoClient
from flask import current_app, g

def get_mongo_client() -> MongoClient:
    """
    Create one MongoClient per request context (cached in flask.g).
    DRY and efficient—avoid reconnecting each route.
    Includes optimized connection settings for better reliability.
    """
    if "mongo_client" not in g:
        # Configure MongoDB client with optimized settings for large datasets
        g.mongo_client = MongoClient(
            current_app.config["MONGO_URI"],
            # Connection pool settings - increased for concurrent requests
            maxPoolSize=25,
            minPoolSize=5,
            # Timeout settings (in milliseconds) - increased for large operations
            connectTimeoutMS=10000,  # 10 seconds to connect
            socketTimeoutMS=60000,   # 60 seconds socket timeout for long-running operations
            serverSelectionTimeoutMS=10000,
            # Retry settings for better resilience
            retryWrites=True,
            retryReads=True,
            # Performance settings
            appName="MIT261_ClassList",  # For monitoring in MongoDB Atlas
            compressors="zlib",  # Network compression for large datasets
            maxIdleTimeMS=45000
        )
    return g.mongo_client

def get_db():
    """
    Return the database instance configured in Config.MONGO_DB_NAME.
    """
    client = get_mongo_client()
    return client[current_app.config["MONGO_DB_NAME"]]
