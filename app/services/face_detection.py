"""
app/services/face_detection.py
--------------------------------
Face detection service using DeepFace with RetinaFace detector.
Extracts face region from image and validates pose.
"""
from deepface import DeepFace
from app.core.config import FACE_DETECTOR
from app.core.logger import logger


def detect_face(image_path: str) -> dict:
    """
    Detects faces in the image using DeepFace + RetinaFace.
    Returns detection result with face region info.
    """
    try:
        faces = DeepFace.extract_faces(
            img_path=image_path,
            detector_backend=FACE_DETECTOR,
            enforce_detection=True,
            align=True,
        )
        if not faces:
            return {"detected": False, "reason": "No face found by DeepFace detector."}

        face = faces[0]
        confidence = face.get("confidence", 0)
        if confidence < 0.8:
            return {"detected": False, "reason": f"Face detection confidence too low ({confidence:.2f}). Please look directly at the camera."}

        logger.info(f"Face detected with confidence: {confidence:.2f}")
        return {"detected": True, "confidence": confidence, "face_region": face.get("facial_area")}

    except Exception as e:
        logger.error(f"Face detection failed: {e}")
        return {"detected": False, "reason": "Face detection failed. Please ensure your face is clearly visible."}
