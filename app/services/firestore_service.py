"""
app/services/firestore_service.py
-----------------------------------
All Firestore read/write operations for users, face scans, and duplicate records.
"""
from datetime import datetime
from app.db.firebase import db
from app.core.config import COLLECTION_USERS, COLLECTION_FACE_SCANS, COLLECTION_DUPLICATE_FACES
from app.core.logger import logger


def get_user(user_id: str) -> dict | None:
    """Fetch a registered user by user_id."""
    doc = db.collection(COLLECTION_USERS).document(user_id).get()
    if doc.exists:
        return {"user_id": doc.id, **doc.to_dict()}
    return None


def get_all_users() -> list:
    """Fetch all registered users (used for duplicate detection)."""
    docs = db.collection(COLLECTION_USERS).stream()
    return [{"user_id": doc.id, **doc.to_dict()} for doc in docs]


def register_user(user_id: str, face_image_base64: str, name: str = "") -> None:
    """Create or update a user's registration record with their face image (base64)."""
    db.collection(COLLECTION_USERS).document(user_id).set({
        "user_id": user_id,
        "name": name,
        "face_image_base64": face_image_base64,
        "registered_at": datetime.now().isoformat(),
    })
    logger.info(f"User registered: {user_id}")


def save_scan_result(user_id: str, status: str, confidence: float = None, message: str = "") -> None:
    """Save a face scan result to the face_scans collection (image not stored, only outcome)."""
    db.collection(COLLECTION_FACE_SCANS).add({
        "user_id": user_id,
        "status": status,
        "confidence": confidence,
        "message": message,
        "scanned_at": datetime.now().isoformat(),
    })
    logger.info(f"Scan result saved for {user_id}: {status}")


def save_duplicate_record(new_user_id: str, existing_user_id: str) -> None:
    """Log a duplicate face detection event."""
    db.collection(COLLECTION_DUPLICATE_FACES).add({
        "new_user_id": new_user_id,
        "existing_user_id": existing_user_id,
        "detected_at": datetime.now().isoformat(),
    })
    logger.warning(f"Duplicate face logged: {new_user_id} matches {existing_user_id}")