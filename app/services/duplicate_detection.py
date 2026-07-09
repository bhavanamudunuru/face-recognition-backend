"""
app/services/duplicate_detection.py
--------------------------------------
Checks if a new face matches any existing registered user.
Used during registration to prevent duplicate accounts.
"""
import os
from deepface import DeepFace
from app.core.config import FACE_MODEL, FACE_DETECTOR
from app.core.logger import logger
from app.utils.image_utils import decode_base64_image


def check_for_duplicate(new_image_path: str, existing_users: list, current_user_id: str) -> dict:
    """
    Compares new face against all registered user faces.
    existing_users: list of dicts with keys user_id and face_image_base64
    current_user_id: skip comparing against the same user
    Returns dict with is_duplicate (bool) and duplicate_user_id (str or None).
    """
    for user in existing_users:
        if user.get("user_id") == current_user_id:
            continue
        registered_base64 = user.get("face_image_base64")
        if not registered_base64:
            continue
        registered_path = None
        try:
            registered_path = decode_base64_image(registered_base64)
            result = DeepFace.verify(
                img1_path=new_image_path,
                img2_path=registered_path,
                model_name=FACE_MODEL,
                detector_backend=FACE_DETECTOR,
                enforce_detection=False,
            )
            if result.get("verified"):
                logger.warning(f"Duplicate face found: matches user {user['user_id']}")
                return {
                    "is_duplicate": True,
                    "duplicate_user_id": user["user_id"],
                }
        except Exception as e:
            logger.warning(f"Skipping duplicate check for user {user.get('user_id')}: {e}")
            continue
        finally:
            if registered_path and os.path.exists(registered_path):
                os.remove(registered_path)
    return {"is_duplicate": False, "duplicate_user_id": None}