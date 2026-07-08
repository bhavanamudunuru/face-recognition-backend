"""
app/services/duplicate_detection.py
--------------------------------------
Checks if a new face matches any existing registered user.
Used during registration to prevent duplicate accounts.
"""
from deepface import DeepFace
from app.core.config import FACE_MODEL, FACE_DETECTOR
from app.core.logger import logger
from app.utils.image_utils import download_image


def check_for_duplicate(new_image_path: str, existing_users: list, current_user_id: str) -> dict:
    """
    Compares new face against all registered user faces.
    existing_users: list of dicts with keys user_id and face_image_url
    current_user_id: skip comparing against the same user
    Returns dict with is_duplicate (bool) and duplicate_user_id (str or None).
    """
    for user in existing_users:
        if user.get("user_id") == current_user_id:
            continue

        registered_url = user.get("face_image_url")
        if not registered_url:
            continue

        try:
            registered_path = download_image(registered_url)
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

    return {"is_duplicate": False, "duplicate_user_id": None}
