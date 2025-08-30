from flask import Blueprint
from ..extensions import get_db

labs_bp = Blueprint("labs", __name__)

@labs_bp.get("/ping")
def ping():
    """
    Health check + show available collections to confirm connection works.
    """
    db = get_db()
    return {
        "status": "ok",
        "db": db.name,
        "collections": db.list_collection_names()
    }
