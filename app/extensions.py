from pymongo import MongoClient
from flask import current_app, g

def get_mongo_client() -> MongoClient:
    """
    Create one MongoClient per request context (cached in flask.g).
    DRY and efficient—avoid reconnecting each route.
    """
    if "mongo_client" not in g:
        g.mongo_client = MongoClient(current_app.config["MONGO_URI"])
    return g.mongo_client

def get_db():
    """
    Return the database instance configured in Config.MONGO_DB_NAME.
    """
    client = get_mongo_client()
    return client[current_app.config["MONGO_DB_NAME"]]
