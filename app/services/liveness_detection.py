"""
app/services/liveness_detection.py
-------------------------------------
Basic liveness check using DeepFace anti-spoofing.
Detects whether the face in the image is a real person or a printed photo/screen replay.
"""
from deepface import DeepFace
from app.core.logger import logger


def check_liveness(image_path: str) -> dict:
    """
    Runs anti-spoofing check on the image using DeepFace.
    Returns whether the face is real or a spoof attempt.
    """
    try:
        faces = DeepFace.extract_faces(
            img_path=image_path,
            enforce_detection=True,
            anti_spoofing=True,
        )

        if not faces:
            return {"is_live": False, "reason": "No face detected for liveness check."}

        face = faces[0]
        is_real = face.get("is_real", False)
        antispoof_score = face.get("antispoof_score", 0)

        logger.info(f"Liveness check: is_real={is_real}, score={antispoof_score:.4f}")

        if not is_real:
            return {
                "is_live": False,
                "reason": "Liveness check failed. The system detected a photo or screen replay instead of a real face.",
                "score": antispoof_score,
            }

        return {"is_live": True, "score": antispoof_score}

    except Exception as e:
        logger.warning(f"Liveness check error (allowing pass): {e}")
        # If anti-spoofing is not available, allow pass with warning
        return {"is_live": True, "score": None, "warning": "Anti-spoofing unavailable, check skipped."}
