"""
app/api/routes/register.py
---------------------------
POST /api/register
Registers a user's face for the first time.
Runs quality check, detection, liveness, and duplicate check before saving.
"""
import os
from fastapi import APIRouter, HTTPException
from app.models.face_models import RegisterFaceRequest, FaceResult
from app.utils.image_utils import decode_base64_image, check_image_quality
from app.services.face_detection import detect_face
from app.services.liveness_detection import check_liveness
from app.services.duplicate_detection import check_for_duplicate
from app.services.firestore_service import get_all_users, register_user, save_duplicate_record
from app.core.logger import logger

router = APIRouter(prefix="/api", tags=["Registration"])


@router.post("/register", response_model=FaceResult)
async def register_face(body: RegisterFaceRequest):
    """
    Registers a new user face.
    Steps: decode image -> quality check -> face detection -> liveness -> duplicate check -> save
    """
    image_path = None
    try:
        logger.info(f"Registration started for user: {body.user_id}")

        # Step 1 — Decode base64 image
        image_path = decode_base64_image(body.image_base64)

        # Step 2 — Image quality check
        quality = check_image_quality(image_path)
        if not quality["passed"]:
            return FaceResult(status="poor_quality", message=quality["reason"])

        # Step 3 — Face detection
        detection = detect_face(image_path)
        if not detection["detected"]:
            return FaceResult(status="poor_quality", message=detection["reason"])

        # Step 4 — Liveness check
        liveness = check_liveness(image_path)
        if not liveness["is_live"]:
            return FaceResult(status="liveness_failed", message=liveness["reason"])

        # Step 5 — Duplicate detection
        all_users = get_all_users()
        duplicate = check_for_duplicate(image_path, all_users, body.user_id)
        if duplicate["is_duplicate"]:
            save_duplicate_record(body.user_id, duplicate["duplicate_user_id"])
            return FaceResult(
                status="duplicate",
                message=f"This face is already registered under another account.",
                duplicate_user_id=duplicate["duplicate_user_id"],
            )

        # Step 6 — Save user registration
        register_user(body.user_id, body.image_base64)

        return FaceResult(
            status="registered",
            message="Face registered successfully.",
            confidence=round(detection.get("confidence", 0) * 100, 2),
        )

    except Exception as e:
        logger.error(f"Registration error for {body.user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)