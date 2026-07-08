"""
app/services/face_verification.py
-----------------------------------
Face verification service using DeepFace FaceNet512 model.
Compares a scanned face against the registered face for a user.
"""
from deepface import DeepFace
from app.core.config import FACE_MODEL, FACE_DETECTOR, FACE_MATCH_THRESHOLD
from app.core.logger import logger


def verify_face(registered_image_path: str, scanned_image_path: str) -> dict:
    """
    Compares two face images and returns match status with confidence.
    registered_image_path: the stored face image of the user
    scanned_image_path: the newly captured face image
    """
    try:
        result = DeepFace.verify(
            img1_path=registered_image_path,
            img2_path=scanned_image_path,
            model_name=FACE_MODEL,
            detector_backend=FACE_DETECTOR,
            enforce_detection=True,
        )

        verified = result.get("verified", False)
        distance = result.get("distance", 1.0)
        threshold = result.get("threshold", FACE_MATCH_THRESHOLD)

        # Convert distance to confidence percentage (closer to 0 = better match)
        confidence = round(max(0, (1 - distance / threshold)) * 100, 2)

        logger.info(f"Verification result: verified={verified}, distance={distance:.4f}, confidence={confidence}%")
        return {
            "verified": verified,
            "confidence": confidence,
            "distance": distance,
        }

    except Exception as e:
        logger.error(f"Face verification failed: {e}")
        return {
            "verified": False,
            "confidence": 0.0,
            "error": str(e),
        }
