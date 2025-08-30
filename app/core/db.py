# app/core/db.py
import os
import sys
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Add parent directory to path to access config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

# Singleton pattern for MongoDB client
_mongo_client = None

def get_mongo_client():
    """
    Creates a MongoDB client with optimized settings for distributed systems.
    Uses singleton pattern to reuse connection across different parts of the application.
    
    Features:
    - Connection pooling with 25 connections
    - Retry logic for better resilience
    - Network compression for large datasets
    - Increased timeout settings
    
    Returns:
        MongoClient: Configured MongoDB client
    """
    global _mongo_client
    
    # Return existing client if already initialized
    if _mongo_client is not None:
        return _mongo_client
        
    # Maximum retry attempts
    max_retries = 3
    retry_delay = 1  # seconds
    
    # Modify connection URI to include read preference
    mongo_uri = Config.MONGO_URI
    # Use primary read preference which is the default and most compatible
    if '?' not in mongo_uri:
        mongo_uri += '?readPreference=primary'
    else:
        mongo_uri += '&readPreference=primary'
    
    for attempt in range(max_retries):
        try:
            # Create client with optimized settings
            client = MongoClient(
                mongo_uri,
                maxPoolSize=25,  # Increased connection pool
                socketTimeoutMS=60000,  # 60 seconds socket timeout
                connectTimeoutMS=30000,  # 30 seconds connect timeout
                serverSelectionTimeoutMS=30000,  # 30 seconds server selection timeout
                retryWrites=True,  # Enable retry for write operations
                retryReads=True,   # Enable retry for read operations
                zlibCompressionLevel=9  # Enable network compression
            )
            
            # Verify connection is working
            client.admin.command('ping')
            
            # Store client in global variable for reuse
            _mongo_client = client
            return client
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            if attempt < max_retries - 1:
                print(f"MongoDB connection attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Failed to connect to MongoDB after {max_retries} attempts: {str(e)}")
                raise
